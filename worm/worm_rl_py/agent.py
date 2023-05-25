import logging
import math
import platform
import random
import signal
import sys
import threading
import unittest

import numpy as np
import env


class Agent:

    def handle_sigterm(self, *_):
        print('got SIGTERM')
        if self._run:
            return
        self.done = True

    def handle_sigusr1(self, *_):
        print('got SIGUSR1')
        if self._run:
            return self.run()
        self.train()

    def handle_sigusr2(self, *_):
        print('got SIGUSR2')
        if self._run:
            return
        self.done = True

    def sig_handlers(self):
        if platform.system() == 'Linux':
            signal.signal(signal.SIGUSR1, self.handle_sigusr1)
            signal.signal(signal.SIGUSR2, self.handle_sigusr2)
        signal.signal(signal.SIGTERM, self.handle_sigterm)

    def __init__(self, buckets=(5, 5, 5, 5, 5, 5), num_episodes=300, min_lr=0.1,
                 min_epsilon=0.1, discount=.9, decay=25, *, run: bool = False, path: str = None):
        logging.basicConfig(level=logging.INFO, format='[WORM][%(asctime)s][%(levelname)s] %(message)s')
        self._run = run

        self.sig_handlers()
        self.env = env.Env()
        self.env.observer()

        self.buckets = buckets
        self.num_episodes = num_episodes
        self.min_lr = min_lr
        self.min_epsilon = min_epsilon
        self.discount = discount
        self.decay = decay

        self.epsilon = None
        self.done = False

        self._qtable_file = '/worm/qtable.npy'

        # [rx_bytes,tx_bytes,rx_packets,tx_packets,ram_usage,cpu_usage]
        self.upper_bounds = self.env.observation_space().high
        self.lower_bounds = self.env.observation_space().low

        self.q_table = np.zeros(self.buckets + (self.env.action_space.n,))
        if self._run:
            self.load(path=path)
        logging.info('Agent initialized...')

    def discretize_state(self, obs):
        discretized = list()
        for i in range(len(obs)):
            obs[i] = min(obs[i], self.upper_bounds[i])
            obs[i] = max(obs[i], self.lower_bounds[i])

            scaling = (obs[i] + abs(self.lower_bounds[i])) / (self.upper_bounds[i] - self.lower_bounds[i])
            new_obs = int(round((self.buckets[i] - 1) * scaling))
            new_obs = min(self.buckets[i] - 1, max(0, new_obs))
            discretized.append(new_obs)
        return tuple(discretized)

    def choose_action(self, state):
        if np.random.random() < self.epsilon:
            return self.env.action_space.sample()
        else:
            return np.argmax(self.q_table[state])

    def update_q(self, state, action, reward, new_state):
        state = tuple(state)
        self.q_table[state][action] += self.learning_rate * (
                reward + self.discount * np.max(self.q_table[new_state]) - self.q_table[state][action])

    def get_epsilon(self, t):
        return max(self.min_epsilon, min(1., 1. - math.log10((t + 1) / self.decay)))

    def get_learning_rate(self, t):
        return max(self.min_lr, min(1., 1. - math.log10((t + 1) / self.decay)))

    def train(self):
        logging.info('Training started...')
        for e in range(self.num_episodes):
            print(f'Episode {e} started...')
            reward_sum = 0.0
            current_state = self.discretize_state(self.reset())

            self.learning_rate = self.get_learning_rate(e)
            self.epsilon = self.get_epsilon(e)

            while not self.done:
                action = self.choose_action(current_state)
                obs, reward, _, _, _ = self.env.step(action)
                new_state = self.discretize_state(obs)
                self.update_q(current_state, action, reward, new_state)
                current_state = new_state
                reward_sum += reward
                logging.info(f'log:{e};{reward=};{action=};{reward_sum=}')
        logging.info('Training finished...')
        self.save('qtable.csv')

    def run(self):
        self.epsilon = -1
        logging.info('Running started...')
        while not self.done:
            action = self.choose_action(self.discretize_state(self.reset()))
            self.env.step(action)
        logging.info('Running finished...')

    def load(self, path: str = None):
        if path is None:
            path = self._qtable_file
        self.q_table = np.load(path)
        logging.debug('Agent\'s qtable loaded...')

    def save(self, path: str = None):
        if path is None:
            path = self._qtable_file
        np.save(path, self.q_table)
        logging.debug('Agent\'s qtable saved...')

    @staticmethod
    def random_float():
        """returns random number between 0 and 1"""
        return random.getrandbits(32) / (1 << 32)

    @staticmethod
    def argmax(arr: [float]):
        """returns index of max value in array"""
        return arr.index(max(arr))

    def reset(self):
        self.done = False
        return self.env.reset()


class TestAgent(unittest.TestCase):
    def test_discretize_state(self):
        self.assertEquals(Agent(buckets=(10, 10, 10, 10, 10, 10))
                          .discretize_state([51.0, 50.1, 5.1, 5.1, 0.1, 750000.1]),
                          (5, 5, 5, 5, 5, 5))


if __name__ == '__main__':
    print('Agent starting...')
    _run = False
    _file = None
    if len(sys.argv) > 1 and sys.argv[1] in ['-r', '--run']:
        _run = True
    if len(sys.argv) > 1 and ['-f'] in sys.argv:
        idx = sys.argv.index('-f') or sys.argv.index('--file')
        _file = sys.argv[idx+1]
    agent = Agent(run=_run, path=_file)
    threading.Event().wait()
    print('Agent finished...')
