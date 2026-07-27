use std::path::PathBuf;

use anyhow::{bail, Context, Result};
use serde::Deserialize;

/// Configuration
#[derive(Debug, Clone, Deserialize)]
pub struct Config {
    /// Base URL of the horizon-api server.
    pub server_url: String,

    /// Server auth key. Currently not sent; parsed for future authentication.
    #[serde(default)]
    #[allow(dead_code)]
    pub api_key: Option<String>,

    /// Interval between metric collections, in seconds.
    #[serde(default = "default_collect_interval")]
    pub collect_interval_secs: u64,

    /// Interval between batch uploads to the server, in seconds.
    #[serde(default = "default_send_interval")]
    pub send_interval_secs: u64,

    /// File path where the persistent agent UUID is stored.
    #[serde(default = "default_agent_id_path")]
    pub agent_id_path: PathBuf,

    /// Mount point to measure disk usage for.
    #[serde(default = "default_disk_path")]
    pub disk_path: String,

    /// HTTP request timeout, in seconds.
    #[serde(default = "default_http_timeout")]
    pub http_timeout_secs: u64,

    /// Maximum number of host datapoints held in the send buffer.
    #[serde(default = "default_max_buffer_size")]
    pub max_buffer_size: usize,

    /// Whether to collect Docker container metrics.
    #[serde(default = "default_collect_containers")]
    pub collect_containers: bool,

    /// Maximum number of container observations held in the send buffer.
    #[serde(default = "default_max_container_buffer_size")]
    pub max_container_buffer_size: usize,
}

fn default_collect_interval() -> u64 {
    10
}

fn default_send_interval() -> u64 {
    60
}

fn default_agent_id_path() -> PathBuf {
    PathBuf::from("/var/lib/horizon-agent/agent_id")
}

fn default_disk_path() -> String {
    "/".to_string()
}

fn default_http_timeout() -> u64 {
    10
}

fn default_max_buffer_size() -> usize {
    2880
}

fn default_collect_containers() -> bool {
    true
}

fn default_max_container_buffer_size() -> usize {
    28800
}

impl Config {
    /// Load configuration
    pub fn load(path: &str) -> Result<Self> {
        let raw = std::fs::read_to_string(path)
            .with_context(|| format!("Failed to read config file: {path}"))?;
        let config: Config =
            toml::from_str(&raw).with_context(|| format!("Failed to parse config file: {path}"))?;
        config.validate()?;
        Ok(config)
    }

    fn validate(&self) -> Result<()> {
        if self.server_url.trim().is_empty() {
            bail!("server_url must not be empty");
        }
        if self.collect_interval_secs == 0 {
            bail!("collect_interval_secs must be greater than 0");
        }
        if self.send_interval_secs == 0 {
            bail!("send_interval_secs must be greater than 0");
        }
        if self.http_timeout_secs == 0 {
            bail!("http_timeout_secs must be greater than 0");
        }
        if self.max_buffer_size == 0 {
            bail!("max_buffer_size must be greater than or equal to 1");
        }
        if self.max_container_buffer_size == 0 {
            bail!("max_container_buffer_size must be greater than or equal to 1");
        }
        Ok(())
    }
}
