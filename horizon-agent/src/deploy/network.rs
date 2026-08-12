use std::collections::{HashMap, HashSet};
use std::sync::{LazyLock, Mutex};

use bollard::Docker;
use bollard::models::{ContainerSummary, NetworkDisconnectRequest};
use bollard::query_parameters::{ListContainersOptionsBuilder, ListNetworksOptionsBuilder};

use crate::deploy::control::Control;
use crate::deploy::executor::{self, MANAGED_LABEL};
use crate::deploy::job::{NetworkDesired, NetworkDesiredState, NetworkSyncResult};

const WORKLOAD_ID_LABEL: &str = "horizon.workload_id";

const STATUS_SYNCED: &str = "SYNCED";
const STATUS_FAILED: &str = "FAILED";

static PENDING_RESULTS: LazyLock<Mutex<Vec<NetworkSyncResult>>> =
    LazyLock::new(|| Mutex::new(Vec::new()));

struct LocalContainer {
    docker_id: String,
    network_mode: Option<String>,
}

pub async fn reconcile(control: &Control, docker: &Docker) {
    let desired = match control.sync_networks(&take_results()).await {
        Ok(desired) => desired,
        Err(err) => {
            tracing::warn!("network sync failed: {err}");
            return;
        }
    };

    let local = local_containers(docker).await;
    let horizon_ids: HashSet<String> = local.values().map(|c| c.docker_id.clone()).collect();

    let mut results = Vec::new();
    for network in &desired.networks {
        let targets: Vec<(&LocalContainer, &str)> = network
            .members
            .iter()
            .filter_map(|member| {
                local
                    .get(&member.workload_id)
                    .map(|container| (container, member.alias.as_str()))
            })
            .filter(|(container, _)| !is_host_or_none(container))
            .collect();
        if let Some(result) = apply(docker, network, &targets, &horizon_ids).await {
            results.push(result);
        }
    }

    results.extend(prune_unlisted(docker, &desired, &horizon_ids).await);

    stash_results(results);
}

async fn apply(
    docker: &Docker,
    network: &NetworkDesired,
    targets: &[(&LocalContainer, &str)],
    horizon_ids: &HashSet<String>,
) -> Option<NetworkSyncResult> {
    if !targets.is_empty()
        && let Err(err) =
            executor::ensure_network(docker, &network.name, &network.driver, &network.options).await
    {
        return Some(failed(&network.name, format!("ensure failed: {err}")));
    }

    let attached = match attached_ids(docker, &network.name).await {
        Ok(attached) => attached,
        Err(_) if targets.is_empty() => return None,
        Err(err) => return Some(failed(&network.name, format!("inspect failed: {err}"))),
    };

    for (container, alias) in targets {
        if attached.contains(&container.docker_id) {
            continue;
        }
        if let Err(err) = executor::connect_network(
            docker,
            &container.docker_id,
            &network.name,
            vec![(*alias).to_string()],
        )
        .await
        {
            return Some(failed(&network.name, format!("connect failed: {err}")));
        }
    }

    let wanted: HashSet<&str> = targets
        .iter()
        .map(|(container, _)| container.docker_id.as_str())
        .collect();
    for docker_id in &attached {
        if wanted.contains(docker_id.as_str()) || !horizon_ids.contains(docker_id) {
            continue;
        }
        if let Err(err) = disconnect(docker, &network.name, docker_id).await {
            return Some(failed(&network.name, format!("disconnect failed: {err}")));
        }
    }

    Some(synced(&network.name))
}

async fn prune_unlisted(
    docker: &Docker,
    desired: &NetworkDesiredState,
    horizon_ids: &HashSet<String>,
) -> Vec<NetworkSyncResult> {
    let filters = HashMap::from([("label", vec![format!("{MANAGED_LABEL}=true")])]);
    let options = ListNetworksOptionsBuilder::new().filters(&filters).build();

    let managed = match docker.list_networks(Some(options)).await {
        Ok(managed) => managed,
        Err(err) => {
            tracing::warn!("could not list managed networks: {err}");
            return Vec::new();
        }
    };

    let listed: HashSet<&str> = desired
        .networks
        .iter()
        .map(|network| network.name.as_str())
        .collect();

    let mut results = Vec::new();
    for network in managed {
        let Some(name) = network.name else {
            continue;
        };
        if listed.contains(name.as_str()) {
            continue;
        }
        results.push(detach_all(docker, &name, horizon_ids).await);
    }
    results
}

async fn detach_all(
    docker: &Docker,
    name: &str,
    horizon_ids: &HashSet<String>,
) -> NetworkSyncResult {
    let attached = match attached_ids(docker, name).await {
        Ok(attached) => attached,
        Err(err) => return failed(name, format!("inspect failed: {err}")),
    };

    for docker_id in &attached {
        if !horizon_ids.contains(docker_id) {
            continue;
        }
        if let Err(err) = disconnect(docker, name, docker_id).await {
            return failed(name, format!("disconnect failed: {err}"));
        }
    }
    synced(name)
}

async fn local_containers(docker: &Docker) -> HashMap<i64, LocalContainer> {
    let filters = HashMap::from([("label", vec![WORKLOAD_ID_LABEL])]);
    let options = ListContainersOptionsBuilder::new()
        .all(false)
        .filters(&filters)
        .build();

    let summaries = match docker.list_containers(Some(options)).await {
        Ok(summaries) => summaries,
        Err(err) => {
            tracing::warn!("could not list horizon containers: {err}");
            return HashMap::new();
        }
    };

    summaries
        .into_iter()
        .filter_map(|summary| {
            let ContainerSummary {
                id,
                labels,
                host_config,
                ..
            } = summary;
            let labels = labels?;
            let workload_id = labels.get(WORKLOAD_ID_LABEL)?.parse::<i64>().ok()?;
            Some((
                workload_id,
                LocalContainer {
                    docker_id: id?,
                    network_mode: host_config.and_then(|config| config.network_mode),
                },
            ))
        })
        .collect()
}

async fn attached_ids(docker: &Docker, name: &str) -> Result<HashSet<String>, String> {
    let inspect = docker
        .inspect_network(name, None)
        .await
        .map_err(|err| err.to_string())?;
    Ok(inspect.containers.unwrap_or_default().into_keys().collect())
}

async fn disconnect(docker: &Docker, name: &str, container_id: &str) -> Result<(), String> {
    docker
        .disconnect_network(
            name,
            NetworkDisconnectRequest {
                container: container_id.to_string(),
                force: Some(false),
            },
        )
        .await
        .map_err(|err| err.to_string())
}

fn is_host_or_none(container: &LocalContainer) -> bool {
    matches!(
        container.network_mode.as_deref(),
        Some("host") | Some("none")
    )
}

fn synced(name: &str) -> NetworkSyncResult {
    NetworkSyncResult {
        network_name: name.to_string(),
        status: STATUS_SYNCED,
        error_message: None,
    }
}

fn failed(name: &str, error_message: String) -> NetworkSyncResult {
    tracing::warn!("network {name} reconcile failed: {error_message}");
    NetworkSyncResult {
        network_name: name.to_string(),
        status: STATUS_FAILED,
        error_message: Some(error_message),
    }
}

fn take_results() -> Vec<NetworkSyncResult> {
    let mut pending = PENDING_RESULTS.lock().expect("pending results poisoned");
    std::mem::take(&mut *pending)
}

fn stash_results(results: Vec<NetworkSyncResult>) {
    *PENDING_RESULTS.lock().expect("pending results poisoned") = results;
}
