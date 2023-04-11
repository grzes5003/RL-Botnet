from abc import ABC, abstractmethod

import pandas as pd
from sklearn.base import OutlierMixin


class ModelAbc(ABC):

    @abstractmethod
    def __init__(self):
        self._total_anomalies = 0
        self._balance = 0
        self._model: OutlierMixin = None

    @abstractmethod
    def learn(self, df: pd.DataFrame) -> OutlierMixin:
        raise NotImplementedError

    @abstractmethod
    def detect(self, df: pd.DataFrame):
        raise NotImplementedError

    @abstractmethod
    def listener(self):
        raise NotImplementedError

    @property
    def anomalies(self):
        """property returning number of anomalies"""
        return self._total_anomalies

    @anomalies.setter
    def anomalies(self, value):
        """property setter for number of anomalies"""
        self._total_anomalies = value

    @property
    def balance(self):
        """property returning balance"""
        return 0 if self._balance == 0 else self._total_anomalies / self._balance

    def inc_balance(self):
        """property setter for balance"""
        self._balance += 1

    @staticmethod
    def drop_timestamp(df: pd.DataFrame):
        return df.drop(columns=['time'])

    @property
    def total_observations(self):
        return self._balance
