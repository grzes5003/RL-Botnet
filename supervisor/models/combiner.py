import argparse
import sys
from concurrent.futures import ThreadPoolExecutor

import pandas as pd

from supervisor.models.IsolationForests import IsolationForestsImpl
from supervisor.models.LocalOutlierFactor import LocalOutlierFactorImpl

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        prog='ProgramName',
        description='What the program does',
        epilog='Text at the bottom of help')
    parser.add_argument('-n', '--name', help='name of the container', required=False)
    parser.add_argument('-i', '--input', help='input file', required=False)
    args = parser.parse_args()

    input_file = '../resources/mgr-m1-1/test_record_3_diff.csv'
    # input_file = '../resources/mgr-m1-1/test_record_random_diff.csv'
    if args.input:
        input_file = args.input

    df = pd.read_csv(input_file)
    detectors = [LocalOutlierFactorImpl(), IsolationForestsImpl()]

    [detector.learn(df) for detector in detectors]
    with ThreadPoolExecutor(max_workers=5) as executor:
        pool = []
        for detector in detectors:
            print(detector.__class__.__name__)
            future = executor.submit(detector.listener, container_name=args.name)
            pool.append(future)
        for future in pool:
            future.result()
    print('done')
