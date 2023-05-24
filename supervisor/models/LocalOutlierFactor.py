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
        self._model: LocalOutlierFactor = LocalOutlierFactor(contamination=0.01, novelty=True)\
            .fit(LocalOutlierFactorImpl.drop_timestamp(df).values)
        return self._model

    def detect(self, df: pd.DataFrame):
        df = df.dropna()
        return self._model.predict(LocalOutlierFactorImpl.drop_timestamp(df))


if __name__ == '__main__':
    cont_name = None
    if len(sys.argv) == 3 and sys.argv[1] in ['-n', '--name']:
        cont_name = sys.argv[2]

    df = pd.read_csv('../resources/mgr-m1-1/test_record_3_diff.csv')
    detector = LocalOutlierFactorImpl()

    detector.learn(df)
    detector.listener(container_name=cont_name)
    print('done')
