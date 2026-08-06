use std::time::Duration;

use anyhow::{Context, Result};
use reqwest::{Client, StatusCode};
use serde::Serialize;
use uuid::Uuid;

use crate::config::Config;
use crate::deploy::job::DeploymentJob;

#[derive(Serialize)]
struct ClaimRequest {
    agent_uuid: Uuid,
}

#[derive(Serialize)]
struct ResultRequest<'a> {
    agent_uuid: Uuid,
    status: &'a str,
    #[serde(skip_serializing_if = "Option::is_none")]
    docker_id: Option<&'a str>,
    removed_docker_ids: &'a [String],
    #[serde(skip_serializing_if = "Option::is_none")]
    error_message: Option<&'a str>,
}

pub struct Control {
    client: Client,
    base_url: String,
    api_key: Option<String>,
    agent_uuid: Uuid,
}

impl Control {
    pub fn new(config: &Config, agent_uuid: Uuid) -> Result<Self> {
        let client = Client::builder()
            .timeout(Duration::from_secs(config.http_timeout_secs))
            .build()
            .context("Failed to build control HTTP client")?;

        Ok(Self {
            client,
            base_url: config.server_url.trim_end_matches('/').to_string(),
            api_key: config.api_key.clone(),
            agent_uuid,
        })
    }

    pub async fn claim(&self) -> Result<Option<DeploymentJob>> {
        let url = format!("{}/api/agents/deployments/claim", self.base_url);
        let payload = ClaimRequest {
            agent_uuid: self.agent_uuid,
        };

        let response = self.post(&url, &payload).await?;
        let status = response.status();
        if status == StatusCode::NO_CONTENT {
            return Ok(None);
        }
        if !status.is_success() {
            let body = response.text().await.unwrap_or_default();
            anyhow::bail!("claim failed ({status}): {body}");
        }

        let job = response
            .json::<DeploymentJob>()
            .await
            .context("Failed to decode deployment job")?;
        Ok(Some(job))
    }

    pub async fn report(
        &self,
        deployment_id: i64,
        status: &str,
        docker_id: Option<&str>,
        removed_docker_ids: &[String],
        error_message: Option<&str>,
    ) -> Result<()> {
        let url = format!(
            "{}/api/agents/deployments/{deployment_id}/result",
            self.base_url
        );
        let payload = ResultRequest {
            agent_uuid: self.agent_uuid,
            status,
            docker_id,
            removed_docker_ids,
            error_message,
        };

        let response = self.post(&url, &payload).await?;
        let status_code = response.status();
        if !status_code.is_success() {
            let body = response.text().await.unwrap_or_default();
            anyhow::bail!("report failed ({status_code}): {body}");
        }
        Ok(())
    }

    async fn post<T: Serialize>(&self, url: &str, payload: &T) -> Result<reqwest::Response> {
        let mut request = self.client.post(url).json(payload);
        if let Some(api_key) = &self.api_key {
            request = request.bearer_auth(api_key);
        }
        request.send().await.context("control request failed")
    }
}
