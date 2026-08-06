use std::collections::VecDeque;

pub struct RingBuffer<T> {
    items: VecDeque<T>,
    max_size: usize,
}

impl<T: Clone> RingBuffer<T> {
    pub fn new(max_size: usize) -> Self {
        Self {
            items: VecDeque::with_capacity(max_size),
            max_size,
        }
    }

    pub fn add(&mut self, item: T) {
        if self.items.len() >= self.max_size {
            self.items.pop_front();
        }
        self.items.push_back(item);
    }

    pub fn snapshot(&self) -> Vec<T> {
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
