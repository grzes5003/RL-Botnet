import argparse
import sys

import pandas as pd
from sklearn.neighbors import LocalOutlierFactor

from supervisor.models import ModelAbc


class LocalOutlierFactorImpl(ModelAbc):
    def __init__(self):
        super().__init__()
        self.threshold = .3

    def learn(self, df: pd.DataFrame) -> LocalOutlierFactor:
        df = df.dropna()
        self._model: LocalOutlierFactor = LocalOutlierFactor(contamination=0.01, algorithm='ball_tree', novelty=True, p=4)\
            .fit(LocalOutlierFactorImpl.drop_timestamp(df).values)
        return self._model

    def detect(self, df: pd.DataFrame):
        df = df.dropna()
        return self._model.predict(LocalOutlierFactorImpl.drop_timestamp(df))


if __name__ == '__main__':
    cont_name = None
    is_ubuntu = False

    parser = argparse.ArgumentParser(description='Local Outlier Factor')
    parser.add_argument('-n', '--name', type=str, help='container name', required=False)
    parser.add_argument('-u', '--ubuntu', action='store_true', help='is ubuntu', required=False)
    args = parser.parse_args()

    if args.name is not None:
        cont_name = args.name
    if args.ubuntu:
        is_ubuntu = True

    df = pd.read_csv('../resources/mgr-m1-1/test_record_3_diff.csv')
    detector = LocalOutlierFactorImpl()
    # if is_ubuntu:
    #     detector.threshold = .099

    detector.learn(df)
    detector.listener(container_name=cont_name, is_ubuntu=is_ubuntu)
    print('done')
