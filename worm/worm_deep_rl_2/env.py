import collections
import logging
import threading
import time

import numpy as np
import psutil
from tf_agents.trajectories import time_step as ts
from tf_agents.environments import py_environment
from tf_agents.specs import BoundedArraySpec

from actions import ActionBot, Actions


class Env(py_environment.PyEnvironment):
    def __init__(self):
        self.low = [0, 0, 0, 0, -10000, 0]
        self.high = [100, 100, 10, 10, 10000, 1500000]

        self._observation_spec = BoundedArraySpec(
            shape=(6,),  # Assuming 6-dimensional observation space
            dtype=np.float32,  # Data type
            minimum=self.low,  # Lower bounds
            maximum=self.high  # Upper bounds
        )

        self._action_spec = BoundedArraySpec(
            shape=(1,),  # Assuming 6-dimensional action space
            dtype=np.int,  # Data type
            minimum=0,  # Lower bounds
            maximum=6  # Upper bounds
        )

        self.threshold = 5
        self.action_space = ActionBot()
        self.lock = threading.Lock()
        self.observation = None

        self.fetcher_handle = self.observer()
        self.fetcher_handle.start()

    @property
    def n(self):
        return 6

    def action_spec(self):
        return self._action_spec

    def observation_spec(self):
        return self._observation_spec

    def _reset(self):
        self.action_space.reset()
        self.action_cooldown_dict = {action: 0 for action in Actions}

        return ts.restart(self._get_obs())

    def _step(self, action):
        result = self.action_space.action(action)
        time.sleep(1)

        reward = Actions(action).action_reward() - self.action_cooldown(action) + self.hunger_factor(action)
        if result == -1:
            reward *= 0.5
        elif result == -2:
            reward = 0

        return ts.transition(self._get_obs(), reward)

    ##########################################
    #           Reward methods               #
    ##########################################

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

    ##########################################
    #           Support methods              #
    ##########################################

    def observer(self):
        # logging.info("Starting observer thread")

        def fetcher():
            # logging.info("Starting fetcher thread")
            records = collections.deque(2 * [None], 2)

            while True:
                records.appendleft(self.get_env())
                if records[1] is None:
                    continue
                with self.lock:
                    self.observation = records[0] - records[1]
                    # logging.info(f"New observation: {self.observation}")
                time.sleep(.5)

        return threading.Thread(target=fetcher, daemon=True)

    def _get_obs(self):
        with self.lock:
            return self.observation

    def _get_info(self):
        return {}

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
