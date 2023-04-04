from enum import Enum


class Signals(Enum):
    START = "kill -10"   # SIGUSR1
    RESET = "kill -12"   # SIGUSR2
    STOP = "kill -19"    # SIGSTOP

    def cmd(self, pid):
        return f'{self.value} {pid}'
