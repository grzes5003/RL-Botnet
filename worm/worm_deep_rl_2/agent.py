import argparse
import logging
import math
import platform
import random
import signal
import threading
import time
from abc import abstractmethod

import numpy as np
from keras.models import Sequential
from keras.layers import Dense
import tensorflow as tf

import env


class Agent:
    def handle_sigterm(self, *_):
        logging.info('got SIGTERM')
        if self._run:
            return
        self.cooldown_done = True

    def handle_sigusr1(self, *_):
        logging.info('got SIGUSR1')
        if self._run:
            return self.run()
        self.train()

    def handle_sigusr2(self, *_):
        logging.info('got SIGUSR2')
        if self._run:
            return
        self.done = True

    def sig_handlers(self):
        if platform.system() == 'Linux':
            logging.info('Setting up signal handlers')
            signal.signal(signal.SIGUSR1, self.handle_sigusr1)
            signal.signal(signal.SIGUSR2, self.handle_sigusr2)
        signal.signal(signal.SIGTERM, self.handle_sigterm)

    def __init__(self, buckets=(5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5), num_episodes=50, min_lr=0.10,
                 min_epsilon=0.15, discount=.9, decay=20, *, run: bool = False, path: str = None):
        logging.basicConfig(level=logging.INFO, format='[WORM][%(asctime)s][%(levelname)s] %(message)s')
        self._run = run
        self.path = path

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
        self.cooldown_done = False

        self._qtable_file = '/worm/dqn_model.h5'

        # [rx_bytes,tx_bytes,rx_packets,tx_packets,ram_usage,cpu_usage]

    def get_epsilon(self, t):
        return max(self.min_epsilon, min(1., 1. - math.log10((t + 1) / self.decay)))

    def get_learning_rate(self, t):
        return max(self.min_lr, min(1., 1. - math.log10((t + 1) / self.decay)))

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
        result = self.env.reset()
        if self._run:
            return result
        while not self.cooldown_done:
            time.sleep(.1)
        time.sleep(.5)
        logging.info('Cooldown done')
        return result


    @abstractmethod
    def choose_action(self, state):
        raise NotImplementedError

    @abstractmethod
    def train(self):
        raise NotImplementedError

    def run(self):
        self.epsilon = -1
        logging.info('Running started...')
        time_step = self.reset()

        while not self.done:
            action = self.choose_action(time_step.observation)
            time_step = self.env.step(action)

        logging.info('Running finished...')

    @abstractmethod
    def load(self, path: str = None):
        raise NotImplementedError

    @abstractmethod
    def save(self, path: str = None):
        raise NotImplementedError


class AgentDQN(Agent):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Initialize DQN-specific parameters
        self.replay_memory = []  # Replay memory for experience replay
        self.batch_size = 32     # Batch size for training the neural network

        self.q_network = self.build_q_network()

        if self._run:
            logging.info('Agent in run mode')
            self.load(path=self.path)
        logging.info('DQN Agent initialized...')

    def build_q_network(self):
        model = Sequential()
        model.add(Dense(8, activation='relu', input_dim=len(self.buckets), name='input_layer'))
        model.add(Dense(16, activation='relu', name='hidden_layer'))
        model.add(Dense(8, activation='relu', name='hidden_layer2'))
        model.add(Dense(self.env.action_space.n, activation='linear', name='output_layer'))
        model.compile(optimizer='adam', loss='mean_squared_error')
        return model

    def choose_action(self, state):
        if np.random.random() < self.epsilon:
            return self.env.action_space.sample()
        q_values = self.q_network.predict(np.array([state]), verbose=0)[0]
        return np.argmax(q_values)

    def update_dqn(self, batch):
        states, actions, rewards, new_states, dones = zip(*batch)

        q_values = self.q_network.predict(np.array(states))
        q_values_new = self.q_network.predict(np.array(new_states))

        for i in range(len(batch)):
            target = rewards[i]
            if not dones[i]:
                target += self.discount * np.max(q_values_new[i])
            q_values[i][actions[i]] = target

        self.q_network.fit(np.array(states), q_values, verbose=0)

    def train(self):
        logging.info('Training started...')
        for e in range(self.num_episodes):
            print(f'Episode {e} started...')
            reward_sum = 0.0
            time_step = self.reset()

            self.epsilon = self.get_epsilon(e)
            self.done = False
            self.cooldown_done = False

            while not self.done:
                action = self.choose_action(time_step.observation)
                next_time_step = self.env.step(action)
                reward = next_time_step.reward
                done = next_time_step.is_last()

                reward_sum += reward
                new_state = next_time_step.observation

                self.replay_memory.append((time_step.observation, action, reward, new_state, done))
                if len(self.replay_memory) > self.batch_size:
                    indices = np.random.choice(len(self.replay_memory), size=self.batch_size, replace=False)
                    batch = [self.replay_memory[i] for i in indices]
                    self.update_dqn(batch)

                time_step = next_time_step
                if done:
                    break

                logging.info(f'log:{e};reward={reward.item():.2f};{action=};{reward_sum=}')
        logging.info('Training finished...')
        self.save('dqn_model.h5')

    def load(self, path: str = None):
        if path is None:
            path = self.path
        self.q_network = tf.keras.models.load_model(path)
        logging.info('Agent\'s DQN model loaded...')

    def save(self, path: str = None):
        if path is None:
            path = self.path
        self.q_network.save(path)
        logging.info('Agent\'s DQN model saved...')


if __name__ == '__main__':
    print('Agent starting...')

    parser = argparse.ArgumentParser(description='Agent')
    parser.add_argument('-r', '--run', action='store_true', help='Run mode')
    parser.add_argument('-f', '--file', type=str, help='File to load')
    args = parser.parse_args()

    agent = AgentDQN(run=args.run, path=args.file)

    threading.Event().wait()
    print('Agent finished...')

