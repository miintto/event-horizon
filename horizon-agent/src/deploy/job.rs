use std::collections::HashMap;

use serde::Deserialize;

#[derive(Debug, Clone, Deserialize)]
pub struct EnvVar {
    pub name: String,
    pub value: String,
}

#[derive(Debug, Clone, Deserialize)]
pub struct PortBinding {
    pub container_port: u16,
    #[serde(default)]
    pub host_port: Option<u16>,
    #[serde(default = "default_protocol")]
    pub protocol: String,
}

fn default_protocol() -> String {
    "tcp".to_string()
}

#[derive(Debug, Clone, Deserialize)]
pub struct MountSpec {
    #[serde(rename = "type")]
    pub kind: String,
    pub source: String,
    pub target: String,
    #[serde(default)]
    pub read_only: bool,
}

#[derive(Debug, Clone, Deserialize)]
pub struct RestartPolicySpec {
    pub name: String,
    #[serde(default)]
    pub max_retry: i64,
}

#[derive(Debug, Clone, Deserialize)]
pub struct HealthcheckSpec {
    pub test: Vec<String>,
    #[serde(default)]
    pub interval_secs: Option<i64>,
    #[serde(default)]
    pub timeout_secs: Option<i64>,
    #[serde(default)]
    pub retries: Option<i64>,
}

#[derive(Debug, Clone, Deserialize)]
pub struct NetworkSpec {
    #[serde(default)]
    pub mode: Option<String>,
}

#[derive(Debug, Clone, Deserialize)]
pub struct LogSpec {
    pub driver: String,
    #[serde(default)]
    pub options: HashMap<String, String>,
}

#[derive(Debug, Clone, Default, Deserialize)]
pub struct ContainerSpec {
    #[serde(default)]
    pub command: Option<Vec<String>>,
    #[serde(default)]
    pub entrypoint: Option<Vec<String>>,
    #[serde(default)]
    pub env: Vec<EnvVar>,
    #[serde(default)]
    pub ports: Vec<PortBinding>,
    #[serde(default)]
    pub mounts: Vec<MountSpec>,
    #[serde(default)]
    pub restart_policy: Option<RestartPolicySpec>,
    #[serde(default)]
    pub healthcheck: Option<HealthcheckSpec>,
    #[serde(default)]
    pub labels: HashMap<String, String>,
    #[serde(default)]
    pub network: Option<NetworkSpec>,
    #[serde(default)]
    pub log: Option<LogSpec>,
}

#[derive(Debug, Clone, Deserialize)]
pub struct DeploymentJob {
    pub deployment_id: i64,
    pub container_name: String,
    pub image: String,
    #[serde(default)]
    pub spec: ContainerSpec,
    #[serde(default)]
    pub cpu_limit: Option<String>,
    #[serde(default)]
    pub memory_limit: Option<i64>,
    #[serde(default)]
    pub labels: HashMap<String, String>,
    #[serde(default)]
    pub previous_docker_ids: Vec<String>,
}
