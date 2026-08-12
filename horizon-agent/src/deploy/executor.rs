use std::collections::HashMap;
use std::time::{Duration, Instant};

use bollard::Docker;
use bollard::models::{
    ContainerCreateBody, EndpointSettings, HealthConfig, HealthStatusEnum, HostConfig,
    HostConfigLogConfig, Mount, MountType, NetworkConnectRequest, NetworkCreateRequest,
    NetworkingConfig, PortBinding as DockerPortBinding, RestartPolicy, RestartPolicyNameEnum,
};
use bollard::query_parameters::{
    CreateContainerOptionsBuilder, CreateImageOptionsBuilder, LogsOptionsBuilder,
    RemoveContainerOptionsBuilder, StopContainerOptionsBuilder,
};
use futures_util::StreamExt;

use crate::config::Config;
use crate::deploy::job::{ContainerSpec, DeploymentJob};

const NANOS_PER_SEC: i64 = 1_000_000_000;
const HEALTH_POLL_INTERVAL: Duration = Duration::from_secs(1);

pub const MANAGED_LABEL: &str = "horizon.managed";

const FAILURE_LOG_TAIL: &str = "20";
const FAILURE_LOG_MAX_CHARS: usize = 360;

#[derive(Debug, Clone, Copy)]
pub struct Timeouts {
    pub health_secs: u64,
    pub settle_secs: u64,
    pub stop_secs: i32,
}

impl From<&Config> for Timeouts {
    fn from(config: &Config) -> Self {
        Self {
            health_secs: config.health_timeout_secs,
            settle_secs: config.health_settle_secs,
            stop_secs: config.stop_timeout_secs,
        }
    }
}

pub enum Outcome {
    Succeeded {
        docker_id: String,
        removed: Vec<String>,
    },
    Failed {
        error_message: String,
    },
}

impl Outcome {
    pub fn status(&self) -> &'static str {
        match self {
            Outcome::Succeeded { .. } => "succeeded",
            Outcome::Failed { .. } => "failed",
        }
    }
}

fn failed(error_message: impl Into<String>) -> Outcome {
    Outcome::Failed {
        error_message: error_message.into(),
    }
}

pub async fn deploy(docker: &Docker, job: &DeploymentJob, timeouts: Timeouts) -> Outcome {
    if let Err(err) = pull_image(docker, &job.image).await {
        if docker.inspect_image(&job.image).await.is_err() {
            return failed(format!("pull failed: {err}"));
        }
        tracing::warn!("pull failed, using local image {}: {err}", job.image);
    }

    // 1. ensure networks
    for network in &job.networks {
        if let Err(err) =
            ensure_network(docker, &network.name, &network.driver, &network.options).await
        {
            return failed(format!("network {} failed: {err}", network.name));
        }
    }

    // 2. create container
    let create_options = CreateContainerOptionsBuilder::new()
        .name(&job.container_name)
        .build();
    let new_id = match docker
        .create_container(Some(create_options), build_config(job))
        .await
    {
        Ok(response) => response.id,
        Err(err) => return failed(format!("create failed: {err}")),
    };

    // 3. connect network
    for network in job.networks.iter().skip(1) {
        if let Err(err) =
            connect_network(docker, &new_id, &network.name, network.aliases.clone()).await
        {
            let reason = format!("network {} connect failed: {err}", network.name);
            rollback(docker, &new_id, &[]).await;
            return failed(reason);
        }
    }

    // 4. stop old container
    let stop_options = StopContainerOptionsBuilder::new()
        .t(timeouts.stop_secs)
        .build();
    for old in &job.previous_docker_ids {
        if let Err(err) = docker.stop_container(old, Some(stop_options.clone())).await {
            tracing::warn!("stop {old} failed: {err}");
        }
    }

    // 5. start new
    if let Err(err) = docker.start_container(&new_id, None).await {
        let reason = with_logs(docker, &new_id, format!("start failed: {err}")).await;
        rollback(docker, &new_id, &job.previous_docker_ids).await;
        return failed(reason);
    }

    // 6. healthcheck
    if let Err(error_message) = await_healthy(docker, &new_id, timeouts).await {
        let reason = with_logs(docker, &new_id, error_message).await;
        rollback(docker, &new_id, &job.previous_docker_ids).await;
        return failed(reason);
    }

    // 7. success
    let mut removed = Vec::new();
    for old in &job.previous_docker_ids {
        match remove(docker, old).await {
            Ok(()) => removed.push(old.clone()),
            Err(err) => tracing::warn!("remove {old} failed: {err}"),
        }
    }

    Outcome::Succeeded {
        docker_id: new_id,
        removed,
    }
}

pub async fn ensure_network(
    docker: &Docker,
    name: &str,
    driver: &str,
    options: &HashMap<String, String>,
) -> Result<(), String> {
    if docker.inspect_network(name, None).await.is_ok() {
        return Ok(());
    }

    match docker
        .create_network(NetworkCreateRequest {
            name: name.to_string(),
            driver: Some(driver.to_string()),
            options: Some(options.clone()),
            labels: Some(HashMap::from([(
                MANAGED_LABEL.to_string(),
                "true".to_string(),
            )])),
            ..Default::default()
        })
        .await
    {
        Ok(_) => Ok(()),
        Err(err) if docker.inspect_network(name, None).await.is_ok() => {
            tracing::debug!("network {name} already created: {err}");
            Ok(())
        }
        Err(err) => Err(err.to_string()),
    }
}

pub async fn connect_network(
    docker: &Docker,
    container_id: &str,
    name: &str,
    aliases: Vec<String>,
) -> Result<(), String> {
    docker
        .connect_network(
            name,
            NetworkConnectRequest {
                container: container_id.to_string(),
                endpoint_config: Some(endpoint_settings(aliases)),
            },
        )
        .await
        .map_err(|err| err.to_string())
}

fn endpoint_settings(aliases: Vec<String>) -> EndpointSettings {
    EndpointSettings {
        aliases: Some(aliases),
        ..Default::default()
    }
}

async fn rollback(docker: &Docker, new_id: &str, previous: &[String]) {
    if let Err(err) = remove(docker, new_id).await {
        tracing::warn!("rollback: remove {new_id} failed: {err}");
    }
    for old in previous {
        if let Err(err) = docker.start_container(old, None).await {
            tracing::error!("rollback: start {old} failed: {err}");
        }
    }
}

async fn with_logs(docker: &Docker, id: &str, reason: String) -> String {
    let options = LogsOptionsBuilder::new()
        .stdout(true)
        .stderr(true)
        .tail(FAILURE_LOG_TAIL)
        .build();

    let mut stream = docker.logs(id, Some(options));
    let mut lines = Vec::new();
    while let Some(item) = stream.next().await {
        match item {
            Ok(output) => lines.push(output.to_string()),
            Err(err) => {
                tracing::warn!("could not read logs of {id}: {err}");
                break;
            }
        }
    }

    let tail = lines.join("").trim().to_string();
    if tail.is_empty() {
        return reason;
    }

    let tail = match tail.char_indices().nth_back(FAILURE_LOG_MAX_CHARS - 1) {
        Some((at, _)) => format!("…{}", &tail[at..]),
        None => tail,
    };
    format!("{reason}: {tail}")
}

async fn remove(docker: &Docker, id: &str) -> Result<(), bollard::errors::Error> {
    let options = RemoveContainerOptionsBuilder::new().force(true).build();
    docker.remove_container(id, Some(options)).await
}

async fn pull_image(docker: &Docker, image: &str) -> Result<(), String> {
    let (name, tag) = split_image(image);
    let mut builder = CreateImageOptionsBuilder::new().from_image(&name);
    if let Some(tag) = &tag {
        builder = builder.tag(tag);
    }

    let mut stream = docker.create_image(Some(builder.build()), None, None);
    while let Some(item) = stream.next().await {
        item.map_err(|err| err.to_string())?;
    }
    Ok(())
}

fn split_image(image: &str) -> (String, Option<String>) {
    if image.contains('@') {
        return (image.to_string(), None);
    }
    let start = image.rfind('/').map(|i| i + 1).unwrap_or(0);
    match image[start..].rfind(':') {
        Some(offset) => {
            let at = start + offset;
            (image[..at].to_string(), Some(image[at + 1..].to_string()))
        }
        None => (image.to_string(), Some("latest".to_string())),
    }
}

async fn await_healthy(docker: &Docker, id: &str, timeouts: Timeouts) -> Result<(), String> {
    let deadline = Instant::now() + Duration::from_secs(timeouts.health_secs);
    let settled_at = Instant::now() + Duration::from_secs(timeouts.settle_secs);

    loop {
        let state = docker
            .inspect_container(id, None)
            .await
            .map_err(|err| format!("inspect failed: {err}"))?
            .state
            .ok_or_else(|| "container state unavailable".to_string())?;

        if state.running != Some(true) {
            let code = state.exit_code.unwrap_or_default();
            return Err(format!("container is not running (exit code {code})"));
        }

        match state.health.and_then(|health| health.status) {
            Some(HealthStatusEnum::HEALTHY) => return Ok(()),
            Some(HealthStatusEnum::UNHEALTHY) => {
                return Err("healthcheck reported unhealthy".into());
            }
            Some(HealthStatusEnum::STARTING) => {}
            _ => {
                if Instant::now() >= settled_at && state.restarting != Some(true) {
                    return Ok(());
                }
            }
        }

        if Instant::now() >= deadline {
            return Err(format!(
                "healthcheck timed out after {}s",
                timeouts.health_secs
            ));
        }
        tokio::time::sleep(HEALTH_POLL_INTERVAL).await;
    }
}

fn build_config(job: &DeploymentJob) -> ContainerCreateBody {
    let spec = &job.spec;
    let mut labels = spec.labels.clone();
    labels.extend(job.labels.clone());

    ContainerCreateBody {
        image: Some(job.image.clone()),
        cmd: spec.command.clone(),
        entrypoint: spec.entrypoint.clone(),
        env: Some(
            spec.env
                .iter()
                .map(|e| format!("{}={}", e.name, e.value))
                .collect(),
        ),
        exposed_ports: Some(spec.ports.iter().map(port_key).collect()),
        healthcheck: spec.healthcheck.as_ref().map(|hc| HealthConfig {
            test: Some(hc.test.clone()),
            interval: hc.interval_secs.map(|s| s * NANOS_PER_SEC),
            timeout: hc.timeout_secs.map(|s| s * NANOS_PER_SEC),
            retries: hc.retries,
            ..Default::default()
        }),
        labels: Some(labels),
        host_config: Some(build_host_config(job, spec)),
        networking_config: job.networks.first().map(|network| NetworkingConfig {
            endpoints_config: Some(HashMap::from([(
                network.name.clone(),
                endpoint_settings(network.aliases.clone()),
            )])),
        }),
        ..Default::default()
    }
}

fn build_host_config(job: &DeploymentJob, spec: &ContainerSpec) -> HostConfig {
    HostConfig {
        memory: job.memory_limit,
        nano_cpus: job
            .cpu_limit
            .as_deref()
            .and_then(|raw| raw.parse::<f64>().ok())
            .map(|cores| (cores * NANOS_PER_SEC as f64) as i64),
        port_bindings: Some(port_bindings(spec)),
        mounts: Some(spec.mounts.iter().map(to_mount).collect()),
        restart_policy: spec.restart_policy.as_ref().map(|rp| RestartPolicy {
            name: Some(restart_policy_name(&rp.name)),
            maximum_retry_count: Some(rp.max_retry),
        }),
        network_mode: if job.networks.is_empty() {
            spec.network_mode.clone()
        } else {
            None
        },
        log_config: spec.log.as_ref().map(|log| HostConfigLogConfig {
            typ: Some(log.driver.clone()),
            config: Some(log.options.clone()),
        }),
        ..Default::default()
    }
}

fn port_key(port: &crate::deploy::job::PortBinding) -> String {
    format!("{}/{}", port.container_port, port.protocol)
}

fn port_bindings(spec: &ContainerSpec) -> HashMap<String, Option<Vec<DockerPortBinding>>> {
    spec.ports
        .iter()
        .map(|port| {
            let binding = port.host_port.map(|host_port| {
                vec![DockerPortBinding {
                    host_ip: None,
                    host_port: Some(host_port.to_string()),
                }]
            });
            (port_key(port), binding)
        })
        .collect()
}

fn to_mount(mount: &crate::deploy::job::MountSpec) -> Mount {
    Mount {
        target: Some(mount.target.clone()),
        source: Some(mount.source.clone()),
        typ: Some(match mount.kind.as_str() {
            "bind" => MountType::BIND,
            "tmpfs" => MountType::TMPFS,
            "npipe" => MountType::NPIPE,
            _ => MountType::VOLUME,
        }),
        read_only: Some(mount.read_only),
        ..Default::default()
    }
}

fn restart_policy_name(name: &str) -> RestartPolicyNameEnum {
    match name {
        "always" => RestartPolicyNameEnum::ALWAYS,
        "unless-stopped" => RestartPolicyNameEnum::UNLESS_STOPPED,
        "on-failure" => RestartPolicyNameEnum::ON_FAILURE,
        _ => RestartPolicyNameEnum::NO,
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn splits_image_tag() {
        assert_eq!(
            split_image("redis:7-alpine"),
            ("redis".into(), Some("7-alpine".into()))
        );
        assert_eq!(
            split_image("redis"),
            ("redis".into(), Some("latest".into()))
        );
        assert_eq!(
            split_image("registry:5000/team/app:v1"),
            ("registry:5000/team/app".into(), Some("v1".into()))
        );
        assert_eq!(
            split_image("registry:5000/team/app"),
            ("registry:5000/team/app".into(), Some("latest".into()))
        );
    }
}
