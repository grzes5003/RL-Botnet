import random
import subprocess
from enum import Enum


class Actions(Enum):
    PING = 0
    NONE = 1

    @classmethod
    def sample(cls):
        return random.choice(list(cls))

    def action_reward(self):
        match self:
            case Actions.PING:
                return 20
            case Actions.NONE:
                return 0
            case _:
                raise ValueError(f'Action {self} not found')


class ActionBot:

    def __init__(self):
        self.ping_proc: subprocess.Popen = None

    def ping_action(self):
        self.ping_proc = subprocess.Popen(f'ping -c 5 10.0.0.12', shell=True)

    def none(self):
        """blank action"""
        pass

    def reset(self):
        if self.ping_proc is not None and self.ping_proc.poll() is None:
            self.ping_proc.kill()
            self.ping_proc = None

    @staticmethod
    def sample():
        """returns action method"""
        return Actions.sample()

    def action(self, action: Actions):
        """calls action method based on action int"""
        match action:
            case Actions.PING:
                if self.ping_proc is None:
                    self.ping_action()
            case Actions.NONE:
                self.none()
            case _:
                raise ValueError(f'Action {action} not found')

    @property
    def n(self):
        return len(Actions)
