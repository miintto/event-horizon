mod buffer;
mod config;
mod host_collector;
mod container_collector;
mod identity;
mod runner;
mod shipper;

use anyhow::Result;
use sysinfo::System;
use tracing_subscriber::EnvFilter;

use crate::buffer::RingBuffer;
use crate::host_collector::HostCollector;
use crate::config::Config;
use crate::container_collector::ContainerCollector;
use crate::shipper::Shipper;

fn config_path() -> String {
    std::env::args()
        .nth(1)
        .or_else(|| std::env::var("HORIZON_AGENT_CONFIG").ok())
        .unwrap_or_else(|| "config.toml".to_string())
}

#[tokio::main]
async fn main() -> Result<()> {
    tracing_subscriber::fmt()
        .with_env_filter(EnvFilter::try_from_default_env().unwrap_or_else(|_| EnvFilter::new("info")))
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

    runner::run(
        &config,
        collector,
        container_collector,
        buffer,
        container_buffer,
        shipper,
        shutdown_signal(),
    )
    .await;
    Ok(())
}

async fn shutdown_signal() {
    #[cfg(unix)]
    {
        use tokio::signal::unix::{signal, SignalKind};
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
