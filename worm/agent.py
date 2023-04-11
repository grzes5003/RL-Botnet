import math
import random
import signal

from worm import env
from worm.env import Env


class Agent:

    def handle_sigstop(self):
        print('got SIGSTOP')
        self.done = True

    def sig_handlers(self):
        signal.signal(signal.SIGUSR1, ...)
        signal.signal(signal.SIGUSR2, ...)
        signal.signal(signal.SIGSTOP, self.handle_sigstop)

    def __init__(self, buckets=(10, 10, 10, 10), num_episodes=100, min_lr=0.1, min_epsilon=0.1, discount=1.0,
                 decay=25):
        self.sig_handlers()
        self.env = env.Env()

        self.buckets = buckets
        self.num_episodes = num_episodes
        self.min_lr = min_lr
        self.min_epsilon = min_epsilon
        self.discount = discount
        self.decay = decay

        self.epsilon = None
        self.done = False

        # [rx_bytes,tx_bytes,rx_packets,tx_packets,ram_usage,cpu_usage]
        self.upper_bounds = self.env.observation_space().high
        self.lower_bounds = self.env.observation_space().low

        self.q_table = Agent.init_q_table(self.env.action_space.n, self.env.n)

    def discretize_state(self, obs):
        discretized = list()
        for i in range(len(obs)):
            scaling = (obs[i] + abs(self.lower_bounds[i])) / (self.upper_bounds[i] - self.lower_bounds[i])
            new_obs = int(round((self.buckets[i] - 1) * scaling))
            new_obs = min(self.buckets[i] - 1, max(0, new_obs))
            discretized.append(new_obs)
        return tuple(discretized)

    def choose_action(self, state):
        if Agent.random_float < self.epsilon:
            return self.env.action_space.sample()
        else:
            return Agent.argmax(self.q_table[state])

    def update_q(self, state, action, reward, new_state):
        self.q_table[state][action] += self.learning_rate * (
                    reward + self.discount * max(self.q_table[new_state]) - self.q_table[state][action])

    def get_epsilon(self, t):
        return max(self.min_epsilon, min(1., 1. - math.log10((t + 1) / self.decay)))

    def get_learning_rate(self, t):
        return max(self.min_lr, min(1., 1. - math.log10((t + 1) / self.decay)))

    def train(self):
        for e in range(self.num_episodes):
            current_state = self.discretize_state(self.reset())

            self.learning_rate = self.get_learning_rate(e)
            self.epsilon = self.get_epsilon(e)

            while not self.done:
                action = self.choose_action(current_state)
                obs, reward, _, _ = self.env.step(action)
                new_state = self.discretize_state(obs)
                self.update_q(current_state, action, reward, new_state)
                current_state = new_state

    @staticmethod
    def init_q_table(n, m):
        """return array of n by m zeros"""
        return [[0 for _ in range(m)] for _ in range(n)]

    def init_table(self, tpl):
        """return array of zeros in shape of tuple"""
        # TODO implement np.zeros()

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
