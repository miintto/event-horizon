use chrono::{DateTime, Utc};
use serde::Serialize;
use sysinfo::{Disks, Networks, System};

#[derive(Debug, Clone, Serialize)]
pub struct HostMetricDatapoint {
    pub collected_at: DateTime<Utc>,
    pub cpu_usage: f32,
    pub memory_used: u64,
    pub memory_total: u64,
    pub disk_used: u64,
    pub disk_total: u64,
    pub net_rx: u64,
    pub net_tx: u64,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub load_avg_1: Option<f64>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub load_avg_5: Option<f64>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub load_avg_15: Option<f64>,
}

pub struct HostCollector {
    system: System,
    disks: Disks,
    networks: Networks,
    disk_path: String,
}

impl HostCollector {
    pub fn new(disk_path: &str) -> Self {
        let mut system = System::new();
        system.refresh_cpu_usage();

        Self {
            system,
            disks: Disks::new_with_refreshed_list(),
            networks: Networks::new_with_refreshed_list(),
            disk_path: disk_path.to_string(),
        }
    }

    pub fn collect(&mut self) -> HostMetricDatapoint {
        self.system.refresh_cpu_usage();
        self.system.refresh_memory();
        self.disks.refresh(true);
        self.networks.refresh(true);

        let (disk_total, disk_used) = self.disk_usage();
        let (net_rx, net_tx) = self.network_totals();
        let load = Self::load_average();

        HostMetricDatapoint {
            collected_at: Utc::now(),
            cpu_usage: self.system.global_cpu_usage(),
            memory_used: self.system.used_memory(),
            memory_total: self.system.total_memory(),
            disk_used,
            disk_total,
            net_rx,
            net_tx,
            load_avg_1: load.0,
            load_avg_5: load.1,
            load_avg_15: load.2,
        }
    }

    fn disk_usage(&self) -> (u64, u64) {
        let best = self
            .disks
            .list()
            .iter()
            .filter(|disk| {
                std::path::Path::new(&self.disk_path).starts_with(disk.mount_point())
            })
            .max_by_key(|disk| disk.mount_point().as_os_str().len());

        match best {
            Some(disk) => {
                let total = disk.total_space();
                let used = total.saturating_sub(disk.available_space());
                (total, used)
            }
            None => (0, 0),
        }
    }

    fn network_totals(&self) -> (u64, u64) {
        let mut rx = 0u64;
        let mut tx = 0u64;
        for data in self.networks.list().values() {
            rx = rx.saturating_add(data.total_received());
            tx = tx.saturating_add(data.total_transmitted());
        }
        (rx, tx)
    }

    #[cfg(unix)]
    fn load_average() -> (Option<f64>, Option<f64>, Option<f64>) {
        let load = System::load_average();
        (Some(load.one), Some(load.five), Some(load.fifteen))
    }

    #[cfg(not(unix))]
    fn load_average() -> (Option<f64>, Option<f64>, Option<f64>) {
        (None, None, None)
    }
}
