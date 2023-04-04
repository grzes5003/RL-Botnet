import math
import signal

import numpy as np


class Agent:
    @staticmethod
    def sig_handlers():
        signal.signal(signal.SIGUSR1, ...)
        signal.signal(signal.SIGUSR2, ...)
        signal.signal(signal.SIGSTOP, ...)

    def __init__(self, buckets=(1, 1, 6, 12), num_episodes=1000, min_lr=0.1, min_epsilon=0.1, discount=1.0, decay=25):
            self.buckets = buckets
            self.num_episodes = num_episodes
            self.min_lr = min_lr
            self.min_epsilon = min_epsilon
            self.discount = discount
            self.decay = decay

            self.epsilon = None


            # [position, velocity, angle, angular velocity]
            self.upper_bounds = [self.env.observation_space.high[0], 0.5, self.env.observation_space.high[2],
                                 math.radians(50) / 1.]
            self.lower_bounds = [self.env.observation_space.low[0], -0.5, self.env.observation_space.low[2],
                                 -math.radians(50) / 1.]

            self.q_table = np.zeros(self.buckets + (self.env.action_space.n,))

    def choose_action(self, state):
        if np.random.random() < self.epsilon:
            return self.env.action_space.sample()
        else:
            return np.argmax(self.q_table[state])

    def update_q(self, state, action, reward, new_state):
        self.q_table[state][action] += self.learning_rate * (reward + self.discount * np.max(self.q_table[new_state]) - self.q_table[state][action])

    def get_epsilon(self, t):
        return max(self.min_epsilon, min(1., 1. - math.log10((t + 1) / self.decay)))

    def get_learning_rate(self, t):
        return max(self.min_lr, min(1., 1. - math.log10((t + 1) / self.decay)))

    def train(self):
        for e in range(self.num_episodes):
            current_state = self.env.reset()

            self.learning_rate = self.get_learning_rate(e)
            self.epsilon = self.get_epsilon(e)
            done = False

            while not done:
                action = self.choose_action(current_state)
                new_state, reward, done, _ = self.env.step(action)
                self.update_q(current_state, action, reward, new_state)
                current_state = new_state
