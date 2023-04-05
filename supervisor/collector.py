import os
import time

import pandas as pd

from supervisor import get_container
from vectors import Vecs


def collect_data(time_limit: int):
    cont = get_container()
    records = []

    timeout = time.time() + time_limit
    while timeout > time.time():
        stats = cont.stats(stream=False)
        print(stats)
        records.append(Vecs.from_read(stats))
        time.sleep(.05)
    return Vecs.into_df(records)


def save_data(df: pd.DataFrame, file_path: str):
    df.to_csv(file_path, index=False)
    print('ok')


if __name__ == '__main__':
    ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

    df = collect_data(120)
    save_data(df, os.path.join(ROOT_DIR, 'resources/mgr-m1-1/test_record.csv'))
    print('done')

