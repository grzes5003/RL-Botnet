import os
import time

import pandas as pd
from docker.models.resource import Model

from supervisor.superv import get_container
from supervisor.vectors import Vecs

import collections


def collect_data(time_limit: int):
    cont = get_container()
    records = []
    stats = cont.stats(stream=True, decode=True)

    timeout = time.time() + time_limit
    while timeout > time.time():
        records.append(Vecs.from_read(stats.__next__()))
    return Vecs.into_df(records)


def collect_constant_data(cont=get_container()):
    records = collections.deque(2*[0], 2)
    stats = cont.stats(stream=True, decode=True)

    while True:
        record = stats.__next__()
        print(record)
        records.appendleft(Vecs.from_read(record))
        if records[1] == 0:
            continue
        yield records[0] - records[1]


def save_data(df: pd.DataFrame, file_path: str):
    df.to_csv(file_path, index=False)
    print('ok')


def generate_diff(file_path: str):
    """load dataframe and save to a file with a new name dataframe with difference between rows"""
    df = pd.read_csv(file_path)
    df.loc[:, df.columns != 'time'] = df.loc[:, df.columns != 'time'].diff()
    df = df.dropna()
    df.to_csv(file_path.replace('.csv', '_diff.csv'), index=False)
    print('ok')


if __name__ == '__main__':
    ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

    df = collect_data(240)
    save_data(df, os.path.join(ROOT_DIR, 'resources/mgr-m1-1/test_record_3.csv'))
    print('done')

