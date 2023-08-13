import argparse

import pandas as pd
from sklearn.ensemble import IsolationForest

from supervisor.models.model_abc import ModelAbc


class IsolationForestsImpl(ModelAbc):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.threshold = .2

    def learn(self, df: pd.DataFrame) -> IsolationForest:
        df = df.dropna()
        # , max_features=3)\
        self._model: IsolationForest = IsolationForest(random_state=42, contamination=0.01, max_features=1.0)\
            .fit(IsolationForestsImpl.drop_timestamp(df))
        return self._model

    def detect(self, df: pd.DataFrame):
        df = df.dropna()
        return self._model.predict(IsolationForestsImpl.drop_timestamp(df))


if __name__ == '__main__':
    cont_name = None
    is_ubuntu = False
    eval = False

    parser = argparse.ArgumentParser(description='Isolation Forests')
    parser.add_argument('-n', '--name', type=str, help='container name', required=False)
    parser.add_argument('-u', '--ubuntu', action='store_true', help='is ubuntu', required=False)
    parser.add_argument('-e', '--eval', action='store_true', help='evaluation', required=False)
    args = parser.parse_args()

    filepath = '../resources/mgr-m1-1/test_record_long_diff.csv'
    filepath = '../resources/mgr-m1-1/test_record_3_diff.csv'
    if args.name is not None:
        cont_name = args.name
    if args.ubuntu:
        filepath = '../resources/mgr-m1-1/test_record_with_qdl_diff.csv'
        is_ubuntu = True
    if args.eval:
        eval = True

    df = pd.read_csv(filepath)
    detector = IsolationForestsImpl(eval=eval)
    # if is_ubuntu:
    #     detector.threshold = .2

    detector.learn(df)
    detector.listener(container_name=cont_name, is_ubuntu=is_ubuntu)
    print('done')
