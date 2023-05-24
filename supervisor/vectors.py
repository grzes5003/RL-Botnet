from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
import pandas as pd


@dataclass
class Vecs:
    time: datetime
    rx_bytes: int
    rx_packets: int
    tx_bytes: int
    tx_packets: int

    ram_usage: int
    cpu_usage: int

    @classmethod
    def from_read(cls, read: dict):
        eth = read['networks']['eth0']
        time = datetime.fromisoformat(read['read'])

        ram_usage = read['memory_stats']['usage']
        cpu_usage = read['cpu_stats']['cpu_usage']['total_usage']

        return cls(
            rx_bytes=eth['rx_bytes'],
            tx_bytes=eth['tx_bytes'],
            rx_packets=eth['rx_packets'],
            tx_packets=eth['tx_packets'],
            ram_usage=ram_usage,
            cpu_usage=cpu_usage,
            time=time
            )

    def to_dict(self):
        return {
            'rx_bytes': self.rx_bytes,
            'tx_bytes': self.tx_bytes,
            'rx_packets': self.rx_packets,
            'tx_packets': self.tx_packets,
            'ram_usage': self.ram_usage,
            'cpu_usage': self.cpu_usage,
            'time': self.time
        }

    @staticmethod
    def into_df(arr: [Vecs]):
        return pd.DataFrame.from_records([item.to_dict() for item in arr])

    @staticmethod
    def diff(arr: [Vecs]):
        """return difference between items from array"""
        return [arr[i] - arr[i - 1] for i in range(1, len(arr))]

    def __sub__(self, other: Vecs):
        return Vecs(
            rx_bytes=self.rx_bytes - other.rx_bytes,
            tx_bytes=self.tx_bytes - other.tx_bytes,
            rx_packets=self.rx_packets - other.rx_packets,
            tx_packets=self.tx_packets - other.tx_packets,
            ram_usage=self.ram_usage - other.ram_usage,
            cpu_usage=self.cpu_usage - other.cpu_usage,
            time=self.time
        )


@dataclass
class Log:
    log: int
    reward: float
    action: int
    reward_sum: float

    @classmethod
    def from_str(cls, read: str):
        # example:
        # [WORM][2023-05-22 20:05:13,046][INFO] log:0:reward=10.0;action=2,reward_sum=10.0
        #

        if 'log:' not in read:
            raise ValueError('bad line')
        vals = read.split('log:')[-1]\
            .replace(':', ';')\
            .replace(',', ';')\
            .split(';')
        return cls(
            log=int(vals[0]),
            reward=float(vals[1].split('=')[-1]),
            action=int(vals[2].split('=')[-1]),
            reward_sum=float(vals[3].split('=')[-1])
        )

    def to_dict(self):
        return {
            'log': self.log,
            'reward': self.reward,
            'action': self.action,
            'reward_sum': self.reward_sum
        }

    @staticmethod
    def into_df(arr: [Vecs]):
        return pd.DataFrame.from_records([item.to_dict() for item in arr])
