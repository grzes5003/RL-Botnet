import logging
import sys

import pandas as pd

from supervisor.models import ModelAbc
from sklearn.svm import OneClassSVM

from supervisor.superv import get_container


class OneClassSVMImpl(ModelAbc):
    def __init__(self):
        super().__init__()
        logging.basicConfig(level=logging.INFO,
                            format=f'[BBB][%(asctime)s][%(levelname)s] %(message)s')
        self.threshold = .3

    def learn(self, df: pd.DataFrame) -> OneClassSVM:
        df = df.dropna()
        self._model: OneClassSVM = OneClassSVM(gamma='auto')\
            .fit(OneClassSVMImpl.drop_timestamp(df))
        return self._model

    def detect(self, df: pd.DataFrame):
        df = df.dropna()
        return self._model.predict(OneClassSVMImpl.drop_timestamp(df))


if __name__ == '__main__':
    cont_name = None
    if len(sys.argv) == 3 and sys.argv[1] in ['-n', '--name']:
        cont_name = sys.argv[2]

    df = pd.read_csv('../resources/mgr-m1-1/test_record_3_diff.csv')
    detector = OneClassSVMImpl()

    detector.learn(df)
    detector.listener(container_name=cont_name)
    print('done')
