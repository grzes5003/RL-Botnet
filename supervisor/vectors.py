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
