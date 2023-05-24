import sys
from concurrent.futures import ThreadPoolExecutor

import pandas as pd

from supervisor.models.IsolationForests import IsolationForestsImpl
from supervisor.models.LocalOutlierFactor import LocalOutlierFactorImpl

if __name__ == '__main__':
    cont_name = None
    if len(sys.argv) == 3 and sys.argv[1] in ['-n', '--name']:
        cont_name = sys.argv[2]

    df = pd.read_csv('../resources/mgr-m1-1/test_record_3_diff.csv')
    detectors = [LocalOutlierFactorImpl(), IsolationForestsImpl()]

    [detector.learn(df) for detector in detectors]
    with ThreadPoolExecutor(max_workers=5) as executor:
        pool = []
        for detector in detectors:
            print(detector.__class__.__name__)
            future = executor.submit(detector.listener, container_name=cont_name)
            pool.append(future)
        # pool = [executor.submit(lambda detector: detector.listener(container_name=cont_name), detector) for detector in detectors]
        for future in pool:
            future.result()
    print('done')
