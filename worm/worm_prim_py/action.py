import logging
import random
import subprocess
import threading
from concurrent.futures import ThreadPoolExecutor
from enum import Enum

from util import fetch_info, generate_range, scan, connect_remote


class Actions(Enum):
    PING = 0
    NONE = 1
    SCAN = 2
    INFECT = 3
    FETCH_INFO = 4

    @classmethod
    def sample(cls):
        return random.choice(list(cls)).value

    @classmethod
    def find_action(cls, iter: int):
        match iter % 10:
            case 1 | 3:
                return cls.SCAN.value
            case 4 | 5 | 9 | 0:
                return cls.FETCH_INFO.value
            case 6 | 7:
                return cls.PING.value
            case 8:
                return cls.INFECT.value
            case _:
                return cls.PING.value


class ActionBot:

    def __init__(self):
        logging.basicConfig(level=logging.DEBUG, format='[WORM][%(asctime)s][%(levelname)s] %(message)s')

        self.thread_pool = ThreadPoolExecutor(max_workers=1)

        self.ping_proc: subprocess.Popen = None
        self.scan_proc: subprocess.Popen = None

        self.last_ip = '10.0.0.1'

        self.busy = threading.Event()

        self.known_hosts = set()
        self.infected_hosts = []

    def _is_busy(self):
        self.busy.is_set()

    def ping_action(self):
        logging.info('pinging...')
        self.busy.set()
        self.ping_proc = subprocess.Popen(f'ping -c 5 10.0.0.12', shell=True, stdout=subprocess.DEVNULL)
        self.ping_proc.wait()
        self.ping_proc = None
        self.busy.clear()
        logging.debug('pinged')

    def scan_action(self):
        logging.info('scanning...')
        self.busy.set()
        self.scan_proc = 1

        _range = generate_range(self.last_ip, '', 5)
        logging.debug(f'{_range=}')
        result = list(scan(_range[0]))
        [self.known_hosts.add(ip[0]) for ip in result if ip[1] == 'open']
        self.last_ip = _range[1]

        logging.info(f'{result=};{self.known_hosts=}')

        self.scan_proc = None
        self.busy.clear()
        logging.info('scanned')
        return result

    def infect_action(self):
        logging.info('infecting...')
        self.busy.set()
        if len(self.known_hosts) == 0:
            return
        host_addr = self.known_hosts.pop()
        connect_remote(host_addr)
        self.infected_hosts.append(host_addr)
        self.busy.clear()
        logging.debug('infected')

    def fetch_info_action(self):
        logging.info('fetching info...')
        self.busy.set()
        for host in self.infected_hosts:
            fetch_info(host)
        self.busy.clear()
        logging.debug('fetched info')

    def none(self):
        """blank action"""
        logging.info('Idling...')

    def reset(self):
        self.thread_pool.shutdown(wait=False, cancel_futures=True)
        if self.ping_proc is not None and self.ping_proc.poll() is None:
            self.ping_proc.kill()
            self.ping_proc = None
        self.thread_pool = ThreadPoolExecutor(max_workers=1)
        self.busy.clear()

    @staticmethod
    def sample():
        """returns action method"""
        return Actions.sample()

    def action(self, action: int) -> int:
        """calls action method based on action int"""
        if self._is_busy():
            return -1

        match action:
            case Actions.SCAN.value:
                self.scan_proc = self.thread_pool.submit(self.scan_action)
            case Actions.PING.value:
                if self.ping_proc is None:
                    self.thread_pool.submit(self.ping_action)
            case Actions.NONE.value:
                self.none()
            case Actions.INFECT.value:
                if len(self.known_hosts) == 0:
                    return -2
                self.thread_pool.submit(self.infect_action)
            case Actions.FETCH_INFO.value:
                self.thread_pool.submit(self.fetch_info_action)
            case _:
                raise ValueError(f'Action {action} not found')
        return 0

    @property
    def n(self):
        return len(Actions)
