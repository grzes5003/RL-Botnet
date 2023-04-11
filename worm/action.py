import os
import subprocess


class ActionBot:

    def __init__(self):
        self.ping_proc: subprocess.Popen = None

    def ping_action(self):
        self.ping_proc = subprocess.Popen(f'ping -c 5 10.0.0.12')

    def reset(self):
        if self.ping_proc.poll() is None:
            self.ping_proc.kill()
            self.ping_proc = None

