import logging
import math
import platform
import random
import signal
import sys
import threading
import time
import unittest

from action import ActionBot, Actions


class Agent:
    def handle_sigterm(self, *_):
        print('got SIGTERM; no action')

    def handle_sigusr1(self, *_):
        print('got SIGUSR1')
        self.run()

    def handle_sigusr2(self, *_):
        print('got SIGUSR2; no action')

    def sig_handlers(self):
        if platform.system() == 'Linux':
            signal.signal(signal.SIGUSR1, self.handle_sigusr1)
            signal.signal(signal.SIGUSR2, self.handle_sigusr2)
        signal.signal(signal.SIGTERM, self.handle_sigterm)

    def __init__(self):
        logging.basicConfig(level=logging.INFO, format='[WORM][%(asctime)s][%(levelname)s] %(message)s')

        self.done = False
        self.sig_handlers()
        self.iter = 0
        self.action_space = ActionBot()

    def run(self):
        while not self.done:
            logging.info(f'iter: {self.iter}')
            action = self.find_action()
            _ = self.action_space.action(action)
            time.sleep(.5)

            self.iter += 1

    def find_action(self):
        return Actions.find_action(self.iter)


if __name__ == '__main__':
    print('Agent starting...')
    agent = Agent()
    threading.Event().wait()
    print('Agent finished...')
