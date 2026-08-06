use std::collections::HashMap;

use bollard::Docker;
use bollard::models::{ContainerStatsResponse, ContainerSummary};
use bollard::query_parameters::{ListContainersOptionsBuilder, StatsOptionsBuilder};
use chrono::{DateTime, Utc};
use futures_util::{StreamExt, stream};
use serde::Serialize;

const COMPOSE_PROJECT_LABEL: &str = "com.docker.compose.project";
const COMPOSE_SERVICE_LABEL: &str = "com.docker.compose.service";

const STATS_CONCURRENCY: usize = 16;

#[derive(Debug, Clone, Serialize)]
pub struct ContainerMetricDatapoint {
    pub collected_at: DateTime<Utc>,
    pub cpu_usage: f64,
    pub cpu_throttled_time: u64,
    pub memory_used: u64,
    pub block_read: u64,
    pub block_write: u64,
    pub pids: u64,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub memory_limit: Option<u64>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub net_rx: Option<u64>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub net_tx: Option<u64>,
}

#[derive(Debug, Clone)]
pub struct ContainerObservation {
    pub docker_id: String,
    pub name: String,
    pub image: String,
    pub state: String,
    pub compose_project: Option<String>,
    pub compose_service: Option<String>,
    pub datapoint: ContainerMetricDatapoint,
}

#[derive(Debug, Serialize)]
pub struct ContainerCollectItem {
    pub docker_id: String,
    pub name: String,
    pub image: String,
    pub state: String,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub compose_project: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub compose_service: Option<String>,
    pub datapoints: Vec<ContainerMetricDatapoint>,
}

pub fn group(observations: Vec<ContainerObservation>) -> Vec<ContainerCollectItem> {
    let mut order: Vec<String> = Vec::new();
    let mut items: HashMap<String, ContainerCollectItem> = HashMap::new();

    for obs in observations {
        let item = items.entry(obs.docker_id.clone()).or_insert_with(|| {
            order.push(obs.docker_id.clone());
            ContainerCollectItem {
                docker_id: obs.docker_id.clone(),
                name: String::new(),
                image: String::new(),
                state: String::new(),
                compose_project: None,
                compose_service: None,
                datapoints: Vec::new(),
            }
        });
        item.name = obs.name;
        item.image = obs.image;
        item.state = obs.state;
        item.compose_project = obs.compose_project;
        item.compose_service = obs.compose_service;
        item.datapoints.push(obs.datapoint);
    }

    order
        .into_iter()
        .filter_map(|id| items.remove(&id))
        .collect()
}

pub struct ContainerCollector {
    docker: Option<Docker>,
}

impl ContainerCollector {
    pub fn disabled() -> Self {
        Self { docker: None }
    }

    pub fn connect() -> Self {
        match Docker::connect_with_local_defaults() {
            Ok(docker) => {
                tracing::info!("connected to Docker daemon");
                Self {
                    docker: Some(docker),
                }
            }
            Err(err) => {
                tracing::warn!("Docker unavailable, container metrics disabled: {err}");
                Self { docker: None }
            }
        }
    }

    pub async fn collect(&self) -> Vec<ContainerObservation> {
        let Some(docker) = &self.docker else {
            return Vec::new();
        };
        match Self::collect_inner(docker).await {
            Ok(observations) => observations,
            Err(err) => {
                tracing::warn!("container metric collection failed: {err}");
                Vec::new()
            }
        }
    }

    async fn collect_inner(docker: &Docker) -> anyhow::Result<Vec<ContainerObservation>> {
        let options = ListContainersOptionsBuilder::default().all(false).build();
        let containers = docker.list_containers(Some(options)).await?;
        let collected_at = Utc::now();

        let observations = stream::iter(containers)
            .map(|summary| async move { Self::observe(docker, collected_at, summary).await })
            .buffer_unordered(STATS_CONCURRENCY)
            .filter_map(|observation| async move { observation })
            .collect::<Vec<_>>()
            .await;

        Ok(observations)
    }

    async fn observe(
        docker: &Docker,
        collected_at: DateTime<Utc>,
        summary: ContainerSummary,
    ) -> Option<ContainerObservation> {
        let docker_id = summary.id?;
        let stats = Self::fetch_stats(docker, &docker_id).await?;

        let labels = summary.labels.unwrap_or_default();
        Some(ContainerObservation {
            docker_id,
            name: summary
                .names
                .and_then(|names| names.into_iter().next())
                .map(|name| name.trim_start_matches('/').to_string())
                .unwrap_or_default(),
            image: summary.image.unwrap_or_default(),
            state: summary
                .state
                .map(|state| state.to_string())
                .unwrap_or_default(),
            compose_project: labels.get(COMPOSE_PROJECT_LABEL).cloned(),
            compose_service: labels.get(COMPOSE_SERVICE_LABEL).cloned(),
            datapoint: datapoint_from_stats(collected_at, &stats),
        })
    }

    async fn fetch_stats(docker: &Docker, docker_id: &str) -> Option<ContainerStatsResponse> {
        let options = StatsOptionsBuilder::default()
            .stream(false)
            .one_shot(false)
            .build();
        match docker.stats(docker_id, Some(options)).next().await {
            Some(Ok(stats)) => Some(stats),
            Some(Err(err)) => {
                tracing::debug!("stats failed for {docker_id}: {err}");
                None
            }
            None => None,
        }
    }
}

fn datapoint_from_stats(
    collected_at: DateTime<Utc>,
    stats: &ContainerStatsResponse,
) -> ContainerMetricDatapoint {
    let (block_read, block_write) = block_io(stats);
    let (net_rx, net_tx) = network_io(stats);

    ContainerMetricDatapoint {
        collected_at,
        cpu_usage: cpu_cores(stats),
        cpu_throttled_time: stats
            .cpu_stats
            .as_ref()
            .and_then(|cpu| cpu.throttling_data.as_ref())
            .and_then(|throttling| throttling.throttled_time)
            .unwrap_or(0),
        memory_used: memory_used(stats),
        memory_limit: stats.memory_stats.as_ref().and_then(|mem| mem.limit),
        block_read,
        block_write,
        pids: stats
            .pids_stats
            .as_ref()
            .and_then(|pids| pids.current)
            .unwrap_or(0),
        net_rx,
        net_tx,
    }
}

fn cpu_cores(stats: &ContainerStatsResponse) -> f64 {
    let cpu = stats.cpu_stats.as_ref();
    let precpu = stats.precpu_stats.as_ref();

    let total = cpu
        .and_then(|c| c.cpu_usage.as_ref())
        .and_then(|u| u.total_usage)
        .unwrap_or(0);
    let pre_total = precpu
        .and_then(|c| c.cpu_usage.as_ref())
        .and_then(|u| u.total_usage)
        .unwrap_or(0);
    let cpu_delta = total as f64 - pre_total as f64;

    let system = cpu.and_then(|c| c.system_cpu_usage).unwrap_or(0);
    let pre_system = precpu.and_then(|c| c.system_cpu_usage).unwrap_or(0);
    let system_delta = system as f64 - pre_system as f64;

    if cpu_delta <= 0.0 || system_delta <= 0.0 {
        return 0.0;
    }

    let online_cpus = cpu
        .and_then(|c| c.online_cpus)
        .map(|n| n as u64)
        .or_else(|| {
            cpu.and_then(|c| c.cpu_usage.as_ref())
                .and_then(|u| u.percpu_usage.as_ref())
                .map(|percpu| percpu.len() as u64)
        })
        .unwrap_or(1) as f64;

    (cpu_delta / system_delta) * online_cpus
}

fn memory_used(stats: &ContainerStatsResponse) -> u64 {
    let Some(mem) = stats.memory_stats.as_ref() else {
        return 0;
    };
    let usage = mem.usage.unwrap_or(0);
    let inactive = mem
        .stats
        .as_ref()
        .and_then(|s| {
            s.get("inactive_file")
                .or_else(|| s.get("total_inactive_file"))
        })
        .copied()
        .unwrap_or(0);
    usage.saturating_sub(inactive)
}

fn block_io(stats: &ContainerStatsResponse) -> (u64, u64) {
    let mut read = 0u64;
    let mut write = 0u64;
    if let Some(entries) = stats
        .blkio_stats
        .as_ref()
        .and_then(|blkio| blkio.io_service_bytes_recursive.as_ref())
    {
        for entry in entries {
            let value = entry.value.unwrap_or(0);
            match entry.op.as_deref().map(str::to_ascii_lowercase).as_deref() {
                Some("read") => read = read.saturating_add(value),
                Some("write") => write = write.saturating_add(value),
                _ => {}
            }
        }
    }
    (read, write)
}

fn network_io(stats: &ContainerStatsResponse) -> (Option<u64>, Option<u64>) {
    match stats.networks.as_ref() {
        Some(networks) if !networks.is_empty() => {
            let mut rx = 0u64;
            let mut tx = 0u64;
            for data in networks.values() {
                rx = rx.saturating_add(data.rx_bytes.unwrap_or(0));
                tx = tx.saturating_add(data.tx_bytes.unwrap_or(0));
            }
            (Some(rx), Some(tx))
        }
        _ => (None, None),
    }
}
