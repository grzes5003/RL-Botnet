

import pandas as pd
from sklearn.ensemble import IsolationForest

from supervisor.collector import collect_constant_data
from supervisor.models.model_abc import ModelAbc
from supervisor.signals import Signals
from supervisor.superv import get_container, send_sig, tape
from supervisor.vectors import Vecs


class IsolationForestsImpl(ModelAbc):
    def __init__(self):
        super().__init__()
        self.threshold = .3

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
        cont = get_container()
        pid = tape(cont)
        send_sig(cont, pid, Signals.START)
        records = collect_constant_data(cont)
        while True:
            record = records.__next__()
            record = Vecs.into_df([record])
            res = self._model.predict(record.drop(columns=['time']))
            print(res[0])
            if res[0] == -1:
                self.observation = 1
            else:
                self.observation = 0
            self.inc_balance()
            print(self.observation, self.total_observations, self.anomalies)

            # keep track of balance and reset if balance is above threshold
            if self.observation > self.threshold:
                send_sig(cont, pid, Signals.RESET)
                self.reset()


if __name__ == '__main__':
    df = pd.read_csv('../resources/mgr-m1-1/test_record_3_diff.csv')
    detector = IsolationForestsImpl()
    detector.learn(df)
    detector.listener()
    print('done')
