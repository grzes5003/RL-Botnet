from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import pandas as pd
from matplotlib import pyplot as plt
import seaborn as sns


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


@dataclass
class Eval:
    type: str
    iter: int
    anomalies: int

    @staticmethod
    def read_file(path: str):
        with open(path, 'r') as f:
            return re.findall(r"<(.*?)>", f.read())

    @classmethod
    def from_str(cls, read: str):
        # example:
        # <[LocalOutlierFactorImpl]0.0;186;0>
        #
        _type, *rest = read.split(']')
        _type = _type.removeprefix('<')\
            .removeprefix('[')
        rest = rest[0].split(';')
        return cls(
            type=_type,
            iter=int(rest[1]),
            anomalies=int(rest[2])
        )

    def to_dict(self):
        return {
            'type': self.type,
            'iter': self.iter,
            'anomalies': self.anomalies
        }

    @staticmethod
    def into_df(arr: [Vecs]):
        return pd.DataFrame.from_records([item.to_dict() for item in arr])


class Actions(Enum):
    PING = 'pinging...'
    NONE = 'Idling...'
    SCAN = 'scanning...'
    INFECT = 'infecting...'
    FETCH_INFO = 'fetching info...'

    @staticmethod
    def get_values():
        return [a.value for a in Actions]

@dataclass
class Ops:
    operation: Actions

    @classmethod
    def from_str(cls, read: str):
        # example:
        # 2023-05-28T17:24:53.781676732Z [WORM][2023-05-28 17:24:53,781][INFO] fetching info...
        #
        match read:
            case a if Actions.FETCH_INFO.value in a:
                return cls(operation=Actions.FETCH_INFO)
            case a if Actions.SCAN.value in a:
                return cls(operation=Actions.SCAN)
            case a if Actions.NONE.value in a:
                return cls(operation=Actions.NONE)
            case a if Actions.PING.value in a:
                return cls(operation=Actions.PING)
            case a if Actions.INFECT.value in a:
                return cls(operation=Actions.INFECT)
            case _:
                raise ValueError('bad line')

    @staticmethod
    def into_df(arr: [Ops]):
        return pd.DataFrame.from_records([item.to_dict() for item in arr])

    def to_dict(self):
        return {
            'operation': self.operation.name
        }

    @staticmethod
    def filter_file(path: str):
        with open(path, 'r') as f:
            return filter(lambda item: any(val in item for val in Actions.get_values()),
                          re.findall(r"\[WORM].*\.{3}\n", f.read()))

    @staticmethod
    def file2arr(path: str):
        lines = Ops.filter_file(path)
        return [Ops.from_str(line) for line in lines]


if __name__ == '__main__':
    file_path_rl = '../supervisor/resources/results/worm-rl/eval/worm-rl-a-03-actions.log'
    file_path_sarsa = '../supervisor/resources/results/worm-rl/eval/worm-rl-a-05-actions.log'
    file_path_static = '../supervisor/resources/results/worm-static/eval/worm-static-b-01-actions.log'

    res = Ops.file2arr(file_path_rl)
    r1_df = Ops.into_df(res)
    r1_df['type'] = 'worm-static'

    res = Ops.file2arr(file_path_sarsa)
    r2_df = Ops.into_df(res)
    r2_df['type'] = 'worm-rl SARSA'

    res = Ops.file2arr(file_path_static)
    r3_df = Ops.into_df(res)
    r3_df['type'] = 'worm-rl Q-learning'

    df = pd.concat([r1_df, r2_df, r3_df])
    table = (df.groupby(['operation', 'type']).size() / df.groupby('type').size()).unstack()
    sns.set_theme()
    # sns.dark_palette("seagreen")
    sns.heatmap(table, cmap=sns.cm.rocket_r, annot=True, fmt=".2%")

    plt.tight_layout()
    plt.xlabel('Worm type')
    plt.ylabel('Operation')
    plt.title('Operation distribution for worm types \n (static IoT device)')
    plt.subplots_adjust(top=.9)
    plt.show()
    ...

