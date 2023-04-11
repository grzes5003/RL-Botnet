import pandas as pd
from sklearn.ensemble import IsolationForest

from supervisor.collector import collect_constant_data
from supervisor.models.model_abc import ModelAbc
from supervisor.vectors import Vecs


class IsolationForestsImpl(ModelAbc):
    def __init__(self):
        super().__init__()

    def learn(self, df: pd.DataFrame) -> IsolationForest:
        df = df.dropna()
        self._model: IsolationForest = IsolationForest(random_state=42, contamination=0.01)\
            .fit(IsolationForestsImpl.drop_timestamp(df))
        return self._model

    def detect(self, df: pd.DataFrame):
        df = df.dropna()
        return self._model.predict(IsolationForestsImpl.drop_timestamp(df))

    def listener(self):
        if self._model is None:
            raise ValueError('Model is not initialized')
        records = collect_constant_data()
        while True:
            record = records.__next__()
            record = Vecs.into_df([record])
            res = self._model.predict(record.drop(columns=['time']))
            print(res[0])
            if res[0] == -1:
                self.anomalies += 1
            self.inc_balance()
            print(self.balance, self.total_observations, self.anomalies)


if __name__ == '__main__':
    df = pd.read_csv('../resources/mgr-m1-1/test_record_3_diff.csv')
    detector = IsolationForestsImpl()
    detector.learn(df)
    detector.listener()
    print('done')
