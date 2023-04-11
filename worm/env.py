import dataclasses
import random
import time

import psutil

from worm.action import ActionBot, Actions


class Env:

    @dataclasses.dataclass
    class ObservationSpace:
        low = [0, 0, 0, -10000, 0]
        high = [100, 100, 10, 10000, 1500000]

    def __init__(self):
        self._n = 6
        self.action_space = ActionBot()

    @staticmethod
    def cpu_usage():
        return psutil.cpu_percent()

    @staticmethod
    def ram_usage():
        return psutil.virtual_memory().percent

    @staticmethod
    def net_packets():
        return psutil.net_io_counters().packets_recv,\
            psutil.net_io_counters().packets_sent

    @staticmethod
    def net_bytes():
        return psutil.net_io_counters().bytes_recv,\
            psutil.net_io_counters().bytes_sent

    @staticmethod
    def get_env():
        return *Env.net_bytes(), *Env.net_packets(), Env.ram_usage(), Env.cpu_usage()

    def sample(self):
        return self.action_space.sample()

    def action(self, action):
        return self.action_space.action(action)

    def step(self, action: Actions):
        self.action_space.action(action)
        time.sleep(.5)

        reward = action.action_reward()  # Binary sparse rewards
        observation = self._get_obs()
        info = self._get_info()

        return observation, reward, False, False, info

    def reset(self):
        self.action_space.reset()
        observation = self._get_obs()
        info = self._get_info()

        return observation

    def _get_obs(self):
        # return {"agent": self._agent_location, "target": self._target_location}
        return self.get_env()

    def _get_info(self):
        # return {"distance": np.linalg.norm(self._agent_location - self._target_location, ord=1)}
        return {}

    def observation_space(self):
        return self.ObservationSpace

    @property
    def n(self):
        return self._n
