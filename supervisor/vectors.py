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


def plot_static(file_path_rl, file_path_sarsa, file_path_dqn, file_path_static, type: str = 'static'):

    # file_path_rl = '../supervisor/resources/results/worm-rl/eval/worm-rl-a-03-actions.log'
    # file_path_sarsa = '../supervisor/resources/results/worm-rl/eval/worm-rl-a-05-actions.log'
    # file_path_static = '../supervisor/resources/results/worm-static/eval/worm-static-b-01-actions.log'

    res = Ops.file2arr(file_path_static)
    r1_df = Ops.into_df(res)
    r1_df['type'] = 'Static worm'

    res = Ops.file2arr(file_path_sarsa)
    r2_df = Ops.into_df(res)
    r2_df['type'] = 'SARSA'

    res = Ops.file2arr(file_path_rl)
    r3_df = Ops.into_df(res)
    r3_df['type'] = 'Q-learning'

    res = Ops.file2arr(file_path_dqn)
    r4_df = Ops.into_df(res)
    r4_df['type'] = 'DQN'

    df = pd.concat([r1_df, r2_df, r3_df, r4_df])
    table = (df.groupby(['operation', 'type']).size() / df.groupby('type').size()).unstack()
    sns.set_theme()
    plt.figure(figsize=(10, 5))
    # sns.dark_palette("seagreen")
    heatmap = sns.heatmap(table, cmap="crest", annot=True, fmt=".2%")

    # plt.tight_layout()
    plt.xlabel('Worm type')
    plt.ylabel('Operation')
    heatmap.set_title(f'Operation distribution for worm types \n ({type} IoT device)',
                  fontdict={'fontsize': 15}, pad=12)
    # plt.subplots_adjust(top=0.9, bottom=0.2, left=0.2, right=0.9, hspace=0.5,)
    plt.show()


def plot_dist(file_path_rl, file_path_sarsa, file_path_dqn, file_path_static, type: str = 'static'):
    res = Ops.file2arr(file_path_static)
    r1_df = Ops.into_df(res)
    r1_df['type'] = 'Static worm'

    res = Ops.file2arr(file_path_sarsa)
    r2_df = Ops.into_df(res)
    r2_df['type'] = 'SARSA'

    res = Ops.file2arr(file_path_rl)
    r3_df = Ops.into_df(res)
    r3_df['type'] = 'Q-learning'

    res = Ops.file2arr(file_path_dqn)
    r4_df = Ops.into_df(res)
    r4_df['type'] = 'DQN'

    df = pd.concat([r1_df, r2_df, r3_df, r4_df])
    table = (df.groupby(['operation', 'type']).size() / df.groupby('type').size()).unstack()

    # melted_df = pd.melt(table, id_vars='operation', var_name='model', value_name='value')
    # melted_df.columns = ['action_type', 'model', 'value']
    #
    # melted_df = melted_df.rename(columns={'operation': 'action_type'})

    table = table.stack().reset_index().rename(columns={0: 'value'})

    sns.displot(table, x="value", col="operation", hue="type", kind="kde", common_norm=False)
    plt.show()

def plot_dist2(file_path_rl, file_path_sarsa, file_path_dqn, file_path_static, type: str = 'static'):
    order = ['NONE', 'PING', 'SCAN', 'INFECT', 'FETCH_INFO']

    palette = sns.color_palette("coolwarm", 3)
    res = Ops.file2arr(file_path_static)
    r1_df = Ops.into_df(res)
    r1_df['type'] = 'Static worm'

    res = Ops.file2arr(file_path_sarsa)
    r2_df = Ops.into_df(res)
    r2_df['type'] = 'SARSA'

    res = Ops.file2arr(file_path_rl)
    r3_df = Ops.into_df(res)
    r3_df['type'] = 'Q-learning'

    res = Ops.file2arr(file_path_dqn)
    r4_df = Ops.into_df(res)
    r4_df['type'] = 'DQN'

    df = pd.concat([r2_df, r3_df, r4_df])

    sns.catplot(df.reset_index(), x="operation", y="index", hue="type", kind="violin")
    # sns.catplot(df.reset_index(), x="operation", y="index", hue="type", kind="swarm")
    # sns.catplot(df.reset_index(), x="operation", y="index", hue="type", order=order)
    # sns.displot(df, x="value", hue="type", kind="kde", common_norm=False, palette=palette)
    plt.ylim(0, 450)

    # plt.tight_layout()
    plt.ylabel('Iteration')
    plt.xlabel('Action type')
    # plt.title(f'Operation distribution for worm types \n ({type} IoT device)', fontdict={'fontsize': 15}, pad=12)
    # plot.set_titles(f'Operation distribution for worm types \n ({type} IoT device)',
    #               fontdict={'fontsize': 15}, pad=12)
    plt.show()


if __name__ == '__main__':
    file_path_rl = '../supervisor/resources/results/worm-rl/eval/worm-rl-a-07-actions.log'
    file_path_dqn = '../supervisor/resources/results/worm-dql/eval/worm-dql-a-02-actions.log'
    file_path_sarsa = '../supervisor/resources/results/worm-rl/eval/worm-rl-a-06-actions.log'
    file_path_static = '../supervisor/resources/results/worm-static/eval/worm-static-actions.log'

    # plot_static(file_path_rl, file_path_sarsa, file_path_dqn, file_path_static, type='Static')
    plot_dist2(file_path_rl, file_path_sarsa, file_path_dqn, file_path_static, type='Static')

    file_path_rl = '../supervisor/resources/results/worm-rl/eval/worm-rl-b-07-actions.log'
    file_path_dqn = '../supervisor/resources/results/worm-dql/eval/worm-dql-b-02-actions.log'
    file_path_sarsa = '../supervisor/resources/results/worm-rl/eval/worm-rl-b-06-actions.log'
    file_path_static = '../supervisor/resources/results/worm-static/eval/worm-static-actions.log'

    # plot_static(file_path_rl, file_path_sarsa, file_path_dqn, file_path_static, type='Random')
    plot_dist2(file_path_rl, file_path_sarsa, file_path_dqn, file_path_static, type='Random')

    ...

