mod collect;
mod config;
mod deploy;
mod identity;
mod runner;

use std::sync::Arc;

use anyhow::{Context, Result};
use bollard::Docker;
use sysinfo::System;
use tracing_subscriber::EnvFilter;

use crate::collect::buffer::RingBuffer;
use crate::collect::container::ContainerCollector;
use crate::collect::host::HostCollector;
use crate::collect::shipper::Shipper;
use crate::config::Config;
use crate::deploy::control::Control;

fn config_path() -> String {
    std::env::args()
        .nth(1)
        .or_else(|| std::env::var("HORIZON_AGENT_CONFIG").ok())
        .unwrap_or_else(|| "config.toml".to_string())
}

#[tokio::main]
async fn main() -> Result<()> {
    tracing_subscriber::fmt()
        .with_env_filter(
            EnvFilter::try_from_default_env().unwrap_or_else(|_| EnvFilter::new("info")),
        )
        .init();

    let config = Config::load(&config_path())?;
    let agent_uuid = identity::load_or_create_agent_uuid(&config.agent_id_path)?;
    let hostname = System::host_name().unwrap_or_else(|| "unknown".to_string());

    let buffer = RingBuffer::new(config.max_buffer_size);
    let container_buffer = RingBuffer::new(config.max_container_buffer_size);
    let collector = HostCollector::new(&config.disk_path);
    let container_collector = if config.collect_containers {
        ContainerCollector::connect()
    } else {
        ContainerCollector::disabled()
    };
    let shipper = Shipper::new(&config, agent_uuid, hostname)?;

    let deploy = if config.deploy_enabled {
        let docker = Docker::connect_with_local_defaults()
            .context("Failed to connect to Docker for deployments")?;
        let control = Arc::new(Control::new(&config, agent_uuid)?);
        tracing::info!(
            "deployments enabled (polling every {}s)",
            config.deploy_poll_interval_secs
        );
        Some((control, docker))
    } else {
        tracing::info!("deployments disabled (set `deploy_enabled = true` to opt in)");
        None
    };

    runner::run(
        &config,
        collector,
        container_collector,
        buffer,
        container_buffer,
        shipper,
        deploy,
        shutdown_signal(),
    )
    .await;
    Ok(())
}

async fn shutdown_signal() {
    #[cfg(unix)]
    {
        use tokio::signal::unix::{SignalKind, signal};
        let mut sigterm = match signal(SignalKind::terminate()) {
            Ok(s) => s,
            Err(err) => {
                tracing::error!("failed to install SIGTERM handler: {err}");
                return;
            }
        };
        tokio::select! {
            _ = tokio::signal::ctrl_c() => {}
            _ = sigterm.recv() => {}
        }
    }

    #[cfg(not(unix))]
    {
        let _ = tokio::signal::ctrl_c().await;
    }
}
