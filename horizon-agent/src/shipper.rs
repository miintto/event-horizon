use std::time::Duration;

use anyhow::{Context, Result};
use reqwest::Client;
use serde::Serialize;
use uuid::Uuid;

use crate::collector::MetricDatapoint;
use crate::config::Config;

#[derive(Serialize)]
struct MetricBatch<'a> {
    agent_uuid: Uuid,
    hostname: &'a str,
    datapoints: &'a [MetricDatapoint],
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum SendOutcome {
    Delivered,
    Rejected,
    Retry,
}

pub struct Shipper {
    client: Client,
    url: String,
    agent_uuid: Uuid,
    hostname: String,
}

impl Shipper {
    pub fn new(config: &Config, agent_uuid: Uuid, hostname: String) -> Result<Self> {
        let client = Client::builder()
            .timeout(Duration::from_secs(config.http_timeout_secs))
            .build()
            .context("Failed to build HTTP client")?;

        let url = format!(
            "{}/api/metrics/hosts",
            config.server_url.trim_end_matches('/')
        );

        Ok(Self {
            client,
            url,
            agent_uuid,
            hostname,
        })
    }

    pub async fn send(&self, samples: &[MetricDatapoint]) -> SendOutcome {
        let payload = MetricBatch {
            agent_uuid: self.agent_uuid,
            hostname: &self.hostname,
            datapoints: samples,
        };

        let response = match self.client.post(&self.url).json(&payload).send().await {
            Ok(response) => response,
            Err(err) => {
                tracing::warn!("Metric send failed: {err}");
                return SendOutcome::Retry;
            }
        };

        let status = response.status();
        if status.is_success() {
            return SendOutcome::Delivered;
        }

        if status.is_client_error() {
            let body = response.text().await.unwrap_or_default();
            tracing::error!("Metric batch rejected ({status}), dropping: {body}");
            return SendOutcome::Rejected;
        }

        tracing::warn!("Metric send failed: status {status}");
        SendOutcome::Retry
    }
}
