import pandas as pd
from sklearn.ensemble import IsolationForest


def learn(df: pd.DataFrame):
    clf = IsolationForest(random_state=42).fit(df)


if __name__ == '__main__':
    ...

