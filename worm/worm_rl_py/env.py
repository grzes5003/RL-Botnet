import collections
import dataclasses
import threading
import time
from copy import deepcopy

import numpy as np
import psutil

from action import ActionBot, Actions


class Env:
    @dataclasses.dataclass
    class ObservationSpace:
        low = [0, 0, 0, 0, -10000, 0, 0, 0, 0, 0, 0]
        high = [100, 100, 10, 10, 10000, 1500000, 2, 2, 2, 2, 2]

    def __init__(self):
        self._n = 6
        self.threshold = 5
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

    def last_actions(self):
        if all([not action for action in self.action_cooldown_dict.values()]):
            action_cooldown = deepcopy(self.action_cooldown_dict)
            action_cooldown[Actions.NONE] = 20
            return [action_cooldown[action] for action in Actions]

        epoch = time.time()
        return [0 if self.action_cooldown_dict[action] == 0 else epoch - self.action_cooldown_dict[action]
                for action in Actions]

    def get_env(self):
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
                    self.observation = [*(records[0] - records[1]), *self.last_actions()]
                time.sleep(.5)

        return threading.Thread(target=fetcher, daemon=True)

    def sample(self):
        return self.action_space.sample()

    def action(self, action):
        return self.action_space.action(action)

    def step(self, action: int):
        result = self.action_space.action(action)
        time.sleep(.5)

        reward = Actions(action).action_reward() - self.action_cooldown(action) + self.hunger_factor(action)
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

        if action_key == Actions.NONE:
            return 0

        current_time = time.time()
        p_100 = Actions(action).action_reward()
        cooldown_val = max(cooldown - current_time + self.action_cooldown_dict[action_key], 0)
        self.action_cooldown_dict[action_key] = current_time

        return p_100 * (cooldown_val / 100)

    def hunger_factor(self, action: int):
        action_key: Actions = Actions(action)
        last_exec = self.action_cooldown_dict[action_key]
        delta = time.time() - last_exec

        if delta <= self.threshold:
            return 0

        p_100 = Actions(action).action_reward()

        return min(delta - self.threshold, 1) * p_100

    def reset(self):
        self.action_space.reset()
        time.sleep(.5)
        self.action_cooldown_dict = {action: 0 for action in Actions}
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
