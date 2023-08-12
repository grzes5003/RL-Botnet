import argparse
import logging
import sys

import pandas as pd

from supervisor.models import ModelAbc
from sklearn.svm import OneClassSVM

from supervisor.superv import get_container


class OneClassSVMImpl(ModelAbc):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        logging.basicConfig(level=logging.INFO,
                            format=f'[BBB][%(asctime)s][%(levelname)s] %(message)s')
        self.threshold = .3

    def learn(self, df: pd.DataFrame) -> OneClassSVM:
        df = df.dropna()
        self._model: OneClassSVM = OneClassSVM(kernel='rbf', gamma='auto')\
            .fit(OneClassSVMImpl.drop_timestamp(df))
        return self._model

    def detect(self, df: pd.DataFrame):
        df = df.dropna()
        return self._model.predict(OneClassSVMImpl.drop_timestamp(df))


if __name__ == '__main__':
    cont_name = None
    is_ubuntu = False
    eval = False

    parser = argparse.ArgumentParser(description='Local Outlier Factor')
    parser.add_argument('-n', '--name', type=str, help='container name', required=False)
    parser.add_argument('-u', '--ubuntu', action='store_true', help='is ubuntu', required=False)
    parser.add_argument('-e', '--eval', action='store_true', help='evaluation', required=False)
    args = parser.parse_args()

    filepath = '../resources/mgr-m1-1/test_record_long_diff.csv'
    if args.name is not None:
        cont_name = args.name
    if args.ubuntu:
        is_ubuntu = True
        filepath = '../resources/mgr-m1-1/test_record_with_qdl_diff.csv'
    if args.eval:
        eval = True

    df = pd.read_csv(filepath)
    detector = OneClassSVMImpl(eval=eval)

    detector.learn(df)
    detector.listener(container_name=cont_name, is_ubuntu=is_ubuntu)
    print('done')
