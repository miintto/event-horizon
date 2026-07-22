use std::time::Duration;

use tokio::time::{interval, MissedTickBehavior};

use crate::buffer::MetricBuffer;
use crate::collector::Collector;
use crate::config::Config;
use crate::shipper::{SendOutcome, Shipper};

pub async fn run(
    config: &Config,
    mut collector: Collector,
    mut buffer: MetricBuffer,
    shipper: Shipper,
    shutdown: impl std::future::Future<Output = ()>,
) {
    let mut collect_tick = interval(Duration::from_secs(config.collect_interval_secs));
    collect_tick.set_missed_tick_behavior(MissedTickBehavior::Skip);

    let mut send_tick = interval(Duration::from_secs(config.send_interval_secs));
    send_tick.set_missed_tick_behavior(MissedTickBehavior::Skip);
    send_tick.reset();

    tracing::info!("agent started");
    tokio::pin!(shutdown);

    loop {
        tokio::select! {
            _ = collect_tick.tick() => {
                buffer.add(collector.collect());
            }
            _ = send_tick.tick() => {
                flush(&mut buffer, &shipper).await;
            }
            _ = &mut shutdown => {
                break;
            }
        }
    }

    flush(&mut buffer, &shipper).await;
    tracing::info!("agent stopped");
}

async fn flush(buffer: &mut MetricBuffer, shipper: &Shipper) {
    let samples = buffer.snapshot();
    if samples.is_empty() {
        return;
    }

    match shipper.send(&samples).await {
        SendOutcome::Delivered => {
            buffer.remove_front(samples.len());
            tracing::info!("Sent {} datapoints", samples.len());
        }
        SendOutcome::Rejected => {
            buffer.remove_front(samples.len());
            tracing::warn!("Dropped {} rejected datapoints", samples.len());
        }
        SendOutcome::Retry => {
            tracing::warn!("Send failed, {} datapoints buffered", buffer.len());
        }
    }
}
