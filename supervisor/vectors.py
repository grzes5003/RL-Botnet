from dataclasses import dataclass
from datetime import datetime


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

    def into_series(self, df):
        ...