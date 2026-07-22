use std::collections::VecDeque;

use crate::collector::MetricDatapoint;

pub struct MetricBuffer {
    items: VecDeque<MetricDatapoint>,
    max_size: usize,
}

impl MetricBuffer {
    pub fn new(max_size: usize) -> Self {
        Self {
            items: VecDeque::with_capacity(max_size),
            max_size,
        }
    }

    pub fn add(&mut self, datapoint: MetricDatapoint) {
        if self.items.len() >= self.max_size {
            self.items.pop_front();
        }
        self.items.push_back(datapoint);
    }

    pub fn snapshot(&self) -> Vec<MetricDatapoint> {
        self.items.iter().cloned().collect()
    }

    pub fn remove_front(&mut self, count: usize) {
        for _ in 0..count.min(self.items.len()) {
            self.items.pop_front();
        }
    }

    pub fn len(&self) -> usize {
        self.items.len()
    }
}
