use std::cmp::max;
use std::collections::HashMap;
use std::thread::sleep;
use std::time::UNIX_EPOCH;
use crate::env::action::Actions;

type ObsType = i32;

pub struct ObservationSpace<'a> {
    pub low: &'a[ObsType],
    pub high: &'a[ObsType],
}

impl<'a> ObservationSpace<'a> {
    const fn low() -> &'a[ObsType] {
        &[0, 0, 0, 0, -10000, 0]
    }

    const fn high() -> &'a[ObsType] {
        &[100, 100, 10, 10, 10000, 1500000]
    }

    pub const fn new() -> Self {
        Self {
            low: Self::low(),
            high: Self::high(),
        }
    }
}

pub struct Env<'a> {
    pub observation_space: ObservationSpace<'a>,
    pub action_space: usize,

    cooldown_map: HashMap<Actions, u64>
}

impl<'a> Env<'a> {

    pub const fn get_action_space() -> (&'a[ObsType], &'a[ObsType]) {
        (ObservationSpace::low(), ObservationSpace::high())
    }

    pub fn new() -> Self {
        let mut cooldown_map = HashMap::new();
        Actions::iter().for_each(|a| {
            cooldown_map.insert(a, 0);
        });
        Self {
            observation_space: ObservationSpace::new(),
            action_space: 5,
            cooldown_map
        }
    }

    pub fn sample(&self) -> usize {
        rand::random::<usize>() % self.action_space
    }

    pub fn reset(&mut self) -> Vec<f32> {
        unimplemented!("reset")
    }

    pub fn step(&mut self, action: usize) -> (Vec<f32>, f32, bool) {
        let result = Actions::from(action);
        sleep(std::time::Duration::from_millis(500));

        let mut reward = result.get_reward() - self.action_cooldown(action);
        if result
    }

    fn action_cooldown(&mut self, action_key: usize) -> i32 {
        let cooldown = 100;
        let action = Actions::from(action_key);

        let time = std::time::SystemTime::now().duration_since(UNIX_EPOCH)
            .expect("tf")
            .as_secs();
        let p_100 = action.get_reward();
        let cooldown_val = max(cooldown - time + self.cooldown_map.get(&action).unwrap(), 0);
        *self.cooldown_map.get_mut(&action).unwrap() = time;

        p_100 * cooldown_val as i32 / 100
    }
}