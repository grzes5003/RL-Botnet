use std::cmp::{max, min};
use ndarray::{ArrayD, ArrayView, Dim, Ix, IxDyn, SliceInfo, SliceInfoElem};
use crate::env::envirement::Env;

struct Agent<'a> {
    env: Env<'a>,

    buckets: Vec<usize>,
    num_episodes: u32,

    min_lr: f32,
    min_epsilon: f32,
    discount: f32,
    decay: f32,
    learning_rate: f32,

    epsilon: f32,

    done: bool,

    q_table: ArrayD<f32>,
}

impl<'a> Agent<'a> {
    fn new() -> Self {
        let env = Env::new();
        let buckets = vec![10usize; 6];
        let num_episodes = 1000;
        let min_lr = 0.1;
        let min_epsilon = 0.1;
        let discount = 0.99;
        let decay = 25.0;
        let epsilon = 1.0;
        let done = false;

        let learning_rate = 1.0;
        let q_table = ArrayD::zeros(IxDyn(buckets.as_slice()));

        Agent {
            env,
            buckets,
            num_episodes,
            min_lr,
            min_epsilon,
            discount,
            decay,
            learning_rate,
            epsilon,
            done,
            q_table,
        }
    }

    fn discretize_state(&self, state: &Vec<f32>) -> Vec<usize> {
        let mut discrete_state = Vec::new();
        for i in 0..state.len() {
            let mut s = state[i];
            s = if s < self.env.observation_space.high[i] as f32 { s } else { self.env.observation_space.high[i] as f32 };
            s = if s > self.env.observation_space.low[i] as f32 { s } else { self.env.observation_space.low[i] as f32 };

            let scaling = (s + self.env.observation_space.low[i] as f32) / (self.env.observation_space.high[i] - self.env.observation_space.low[i]) as f32;
            let mut new_state = ((self.buckets[i] as f32 - 1.0) * scaling).round() as usize;
            new_state = min(self.buckets[i] - 1, max(0, new_state));
            discrete_state.push(new_state);
        }
        discrete_state
    }

    fn choose_action(&self, d_state: &Vec<usize>) -> usize {
        let mut action;
        if rand::random::<f32>() > self.epsilon {
            action = Self::argmax(self.get_slice(d_state));
        } else {
            action = self.env.sample();
        }
        action
    }

    fn update_q(&mut self, d_state: &Vec<usize>, action: usize, reward: f32, d_new_state: &Vec<usize>) {
        let idx = Self::concat_idx(d_state, action);
        self.q_table[idx.as_slice()] += self.learning_rate *
            (reward + self.discount * Self::max(self.get_slice(d_new_state)) - self.q_table[idx.as_slice()]);
    }

    pub fn train(&mut self) {
        println!("Training agent...");
        for e in 0..self.num_episodes {
            let mut reward_sum = 0.0;
            let state = self.env.reset();
            let mut d_state = self.discretize_state(&state);

            while !self.done {
                let action = self.choose_action(&d_state);
                let (new_state, reward, done) = self.env.step(action);
                let d_new_state = self.discretize_state(&new_state);
                self.update_q(&d_state, action, reward, &d_new_state);
                d_state = d_new_state;
                reward_sum += reward;
                println!("Episode: {}, Reward: {}", e, reward_sum);
            }
        }
        println!("Training complete!")
    }

    fn get_slice(&self, slice_idx: &Vec<usize>) -> ArrayView<f32, Dim<[Ix; 1]>>{
        let slice_info_elems = slice_idx.iter()
            .map(|x| SliceInfoElem::from(*x))
            .collect::<Vec<SliceInfoElem>>();
        unsafe {
            let slice_info: SliceInfo<Vec<SliceInfoElem>, IxDyn, Dim<[Ix; 1]>> = SliceInfo::new(slice_info_elems).unwrap();
            self.q_table.slice(slice_info)
        }
    }

    fn set_qtable_val(&mut self, idxs: Vec<usize>, val: f32) {
        self.q_table[idxs.as_slice()] = val;
    }

    fn concat_idx(idxs: &Vec<usize>, idx: usize) -> Vec<usize> {
        let mut new_idxs = idxs.clone();
        new_idxs.push(idx);
        new_idxs
    }

    fn argmax(slice: ArrayView<f32, Dim<[Ix; 1]>>) -> usize {
        slice.iter()
            .enumerate()
            .min_by(|(_, a), (_, b)| a.total_cmp(b))
            .map(|(idx, _)| idx)
            .unwrap()
    }

    fn max(slice: ArrayView<f32, Dim<[Ix; 1]>>) -> f32 {
        slice.iter()
            .max_by(|a, b| a.total_cmp(b))
            .unwrap()
            .clone()
    }

    fn set_buckets(&mut self, buckets: Vec<usize>) {
        self.buckets = buckets;
    }

}


#[cfg(test)]
mod agent_tests {
    use super::*;

    #[test]
    fn test_discretize_state() {
        let agent = Agent::new();
        let state = vec![50.0, 50.0, 5.0, 5.0, 0.0, 750000.0];
        let discrete_state = agent.discretize_state(&state);
        assert_eq!(discrete_state, vec![5; 6]);

        let state = vec![0.0, 0.0, 0.0, 0.0, -10000.0, 0.0];
        let discrete_state = agent.discretize_state(&state);
        assert_eq!(discrete_state, vec![0; 6]);
    }
}
