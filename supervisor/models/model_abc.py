import logging
from abc import ABC, abstractmethod

import pandas as pd
from sklearn.base import OutlierMixin

from supervisor.collector import collect_constant_data
from supervisor.signals import Signals
from supervisor.superv import get_container, send_sig, tape
from supervisor.vectors import Vecs


class ModelAbc(ABC):

    @abstractmethod
    def __init__(self):
        logging.basicConfig(level=logging.INFO,
                            format=f'[{self.__class__.__name__}][%(asctime)s][%(levelname)s] %(message)s')

        self._total_anomalies = 0
        self._balance = 0
        self._model: OutlierMixin = None

        self._limit = 20
        self._observations = []

    @abstractmethod
    def learn(self, df: pd.DataFrame) -> OutlierMixin:
        raise NotImplementedError

    @abstractmethod
    def detect(self, df: pd.DataFrame):
        raise NotImplementedError

    def listener(self, container_name: str = None):
        if self._model is None:
            raise ValueError('Model is not initialized')
        if container_name is None:
            cont = get_container()
        else:
            cont = get_container(name=container_name)
        pid = tape(cont)
        send_sig(cont, pid, Signals.START)
        records = collect_constant_data(cont)
        while True:
            record = records.__next__()
            record = Vecs.into_df([record])
            res = self._model.predict(record.drop(columns=['time']))
            if res[0] == -1:
                self.observation = 1
                self.anomalies += 1
            else:
                self.observation = 0
            self.inc_balance()
            print(f'<[{self.__class__.__name__}]{self.observation};{self.total_observations};{self.anomalies}>')

            # keep track of balance and reset if balance is above threshold
            if self.observation > self.threshold:
                send_sig(cont, pid, Signals.RESET)
                self.reset()

    @property
    def anomalies(self):
        """property returning number of anomalies"""
        return self._total_anomalies

    @anomalies.setter
    def anomalies(self, value):
        """property setter for number of anomalies"""
        self._total_anomalies = value

    @property
    def observation(self):
        if len(self._observations) == 0:
            return 0
        return sum(self._observations) / len(self._observations)

    @observation.setter
    def observation(self, value):
        """updates list with fixed size of observations"""
        if len(self._observations) >= self._limit:
            self._observations.pop(0)
        self._observations.append(value)

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

    def reset(self):
        self._observations = []
