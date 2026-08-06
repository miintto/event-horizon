use std::sync::Arc;
use std::time::Duration;

use bollard::Docker;
use tokio::task::JoinHandle;
use tokio::time::{MissedTickBehavior, interval};

use crate::collect::buffer::RingBuffer;
use crate::collect::container::{self, ContainerCollector, ContainerObservation};
use crate::collect::host::{HostCollector, HostMetricDatapoint};
use crate::collect::shipper::{SendOutcome, Shipper};
use crate::config::Config;
use crate::deploy::control::Control;
use crate::deploy::executor::{self, Outcome, Timeouts};

#[allow(clippy::too_many_arguments)]
pub async fn run(
    config: &Config,
    mut collector: HostCollector,
    container_collector: ContainerCollector,
    mut buffer: RingBuffer<HostMetricDatapoint>,
    mut container_buffer: RingBuffer<ContainerObservation>,
    shipper: Shipper,
    deploy: Option<(Arc<Control>, Docker)>,
    shutdown: impl std::future::Future<Output = ()>,
) {
    let mut collect_tick = interval(Duration::from_secs(config.collect_interval_secs));
    collect_tick.set_missed_tick_behavior(MissedTickBehavior::Skip);

    let mut send_tick = interval(Duration::from_secs(config.send_interval_secs));
    send_tick.set_missed_tick_behavior(MissedTickBehavior::Skip);
    send_tick.reset();

    let mut deploy_tick = interval(Duration::from_secs(config.deploy_poll_interval_secs));
    deploy_tick.set_missed_tick_behavior(MissedTickBehavior::Skip);
    let mut deploy_task: Option<JoinHandle<()>> = None;
    let timeouts = Timeouts::from(config);

    tracing::info!("agent started");
    tokio::pin!(shutdown);

    loop {
        tokio::select! {
            _ = collect_tick.tick() => {
                buffer.add(collector.collect());
                for observation in container_collector.collect().await {
                    container_buffer.add(observation);
                }
            }
            _ = send_tick.tick() => {
                flush(&mut buffer, &mut container_buffer, &shipper).await;
            }
            _ = deploy_tick.tick(), if deploy.is_some() => {
                if deploy_task.as_ref().is_none_or(|task| task.is_finished()) {
                    let (control, docker) = deploy.clone().expect("guarded by deploy.is_some()");
                    deploy_task = Some(tokio::spawn(deploy_once(control, docker, timeouts)));
                }
            }
            _ = &mut shutdown => {
                break;
            }
        }
    }

    flush(&mut buffer, &mut container_buffer, &shipper).await;
    tracing::info!("agent stopped");
}

async fn deploy_once(control: Arc<Control>, docker: Docker, timeouts: Timeouts) {
    let job = match control.claim().await {
        Ok(Some(job)) => job,
        Ok(None) => return,
        Err(err) => {
            tracing::warn!("deployment claim failed: {err}");
            return;
        }
    };

    tracing::info!(
        "deploying {} (deployment {})",
        job.container_name,
        job.deployment_id
    );
    let outcome = executor::deploy(&docker, &job, timeouts).await;

    let (docker_id, removed, error_message) = match &outcome {
        Outcome::Succeeded { docker_id, removed } => {
            tracing::info!("deployment {} succeeded", job.deployment_id);
            (Some(docker_id.as_str()), removed.as_slice(), None)
        }
        Outcome::Failed { error_message } => {
            tracing::error!("deployment {} failed: {error_message}", job.deployment_id);
            (None, [].as_slice(), Some(error_message.as_str()))
        }
    };

    if let Err(err) = control
        .report(
            job.deployment_id,
            outcome.status(),
            docker_id,
            removed,
            error_message,
        )
        .await
    {
        tracing::error!("deployment {} report failed: {err}", job.deployment_id);
    }
}

async fn flush(
    buffer: &mut RingBuffer<HostMetricDatapoint>,
    container_buffer: &mut RingBuffer<ContainerObservation>,
    shipper: &Shipper,
) {
    let datapoints = buffer.snapshot();
    let observations = container_buffer.snapshot();
    if datapoints.is_empty() && observations.is_empty() {
        return;
    }

    let containers = container::group(observations.clone());

    match shipper.send(&datapoints, &containers).await {
        SendOutcome::Delivered => {
            buffer.remove_front(datapoints.len());
            container_buffer.remove_front(observations.len());
            tracing::info!(
                "Sent {} datapoints, {} containers",
                datapoints.len(),
                containers.len()
            );
        }
        SendOutcome::Rejected => {
            buffer.remove_front(datapoints.len());
            container_buffer.remove_front(observations.len());
            tracing::warn!(
                "Dropped rejected batch ({} datapoints, {} containers)",
                datapoints.len(),
                containers.len()
            );
        }
        SendOutcome::Retry => {
            tracing::warn!(
                "Send failed, {} datapoints / {} container observations buffered",
                buffer.len(),
                container_buffer.len()
            );
        }
    }
}
