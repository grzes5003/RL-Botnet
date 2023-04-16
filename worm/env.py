import collections
import dataclasses
import threading
import time

import numpy as np
import psutil

from action import ActionBot, Actions


class Env:
    @dataclasses.dataclass
    class ObservationSpace:
        low = [0, 0, 0, 0, -10000, 0]
        high = [100, 100, 10, 10, 10000, 1500000]

    def __init__(self):
        self._n = 6
        self.action_space = ActionBot()
        self.observation = None
        self.lock = threading.Lock()
        self.fetcher_handle = self.observer()
        self.fetcher_handle.start()

        self.action_cooldown_dict = {action: 0 for action in Actions}

    @staticmethod
    def cpu_usage():
        return psutil.cpu_percent()

    @staticmethod
    def ram_usage():
        return psutil.virtual_memory().percent

    @staticmethod
    def net_packets():
        return psutil.net_io_counters().packets_recv, \
            psutil.net_io_counters().packets_sent

    @staticmethod
    def net_bytes():
        return psutil.net_io_counters().bytes_recv, \
            psutil.net_io_counters().bytes_sent

    @staticmethod
    def get_env():
        return np.array([*Env.net_bytes(), *Env.net_packets(), Env.ram_usage(), Env.cpu_usage()])

    def diff_observation(self, other):
        """substracts two tuples of observations"""
        return tuple(map(lambda x, y: x - y, self.observation, other))

    def observer(self):
        def fetcher():
            records = collections.deque(2 * [None], 2)

            while True:
                records.appendleft(self.get_env())
                if records[1] is None:
                    continue
                with self.lock:
                    self.observation = records[0] - records[1]
                time.sleep(.5)

        return threading.Thread(target=fetcher, daemon=True)

    def get_obs_diff(self):
        return self.observation - self.get_env()

    def sample(self):
        return self.action_space.sample()

    def action(self, action):
        return self.action_space.action(action)

    def step(self, action: int):
        result = self.action_space.action(action)
        time.sleep(.5)

        reward = Actions(action).action_reward() - self.action_cooldown(action)
        if result == -1:
            reward *= 0.5
        elif result == -2:
            reward = 0
        observation = self._get_obs()
        info = self._get_info()

        return observation, reward, False, False, info

    def action_cooldown(self, action: int):
        cooldown = 100
        action_key = Actions(action)

        current_time = time.time()
        p_100 = Actions(action).action_reward()
        cooldown_val = max(cooldown - current_time + self.action_cooldown_dict[action_key], 0)
        self.action_cooldown_dict[action_key] = current_time

        return p_100 * (cooldown_val / 100)

    def reset(self):
        self.action_space.reset()
        time.sleep(.5)
        observation = self._get_obs()

        return observation

    def _get_obs(self):
        with self.lock:
            return self.observation

    def _get_info(self):
        return {}

    def observation_space(self):
        return self.ObservationSpace

    @property
    def n(self):
        return self._n


if __name__ == '__main__':
    env = Env()
    threading.Event().wait()
