import argparse
import logging
import sys

import pandas as pd
from sklearn.ensemble import IsolationForest

from supervisor.models.model_abc import ModelAbc


class IsolationForestsImpl(ModelAbc):
    def __init__(self):
        super().__init__()
        self.threshold = .3

    def learn(self, df: pd.DataFrame) -> IsolationForest:
        df = df.dropna()
        self._model: IsolationForest = IsolationForest(random_state=42, contamination=0.01, max_features=.9)\
            .fit(IsolationForestsImpl.drop_timestamp(df))
        return self._model

    def detect(self, df: pd.DataFrame):
        df = df.dropna()
        return self._model.predict(IsolationForestsImpl.drop_timestamp(df))


if __name__ == '__main__':
    cont_name = None
    is_ubuntu = False

    parser = argparse.ArgumentParser(description='Isolation Forests')
    parser.add_argument('-n', '--name', type=str, help='container name', required=False)
    parser.add_argument('-u', '--ubuntu', action='store_true', help='is ubuntu', required=False)
    args = parser.parse_args()

    if args.name is not None:
        cont_name = args.name
    if args.ubuntu:
        is_ubuntu = True

    df = pd.read_csv('../resources/mgr-m1-1/test_record_3_diff.csv')
    detector = IsolationForestsImpl()
    if is_ubuntu:
        detector.threshold = .099

    detector.learn(df)
    detector.listener(container_name=cont_name, is_ubuntu=is_ubuntu)
    print('done')
