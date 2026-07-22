mod buffer;
mod collector;
mod config;
mod identity;
mod runner;
mod shipper;

use anyhow::Result;
use sysinfo::System;
use tracing_subscriber::EnvFilter;

use crate::buffer::MetricBuffer;
use crate::collector::Collector;
use crate::config::Config;
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

    let buffer = MetricBuffer::new(config.max_buffer_size);
    let collector = Collector::new(&config.disk_path);
    let shipper = Shipper::new(&config, agent_uuid, hostname)?;

    runner::run(&config, collector, buffer, shipper, shutdown_signal()).await;
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
