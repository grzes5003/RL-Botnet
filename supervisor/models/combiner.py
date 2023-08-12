import argparse
from concurrent.futures import ThreadPoolExecutor

import pandas as pd

from supervisor.models.IsolationForests import IsolationForestsImpl
from supervisor.models.LocalOutlierFactor import LocalOutlierFactorImpl
from supervisor.models.OneClassSVM import OneClassSVMImpl

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        prog='ProgramName',
        description='What the program does',
        epilog='Text at the bottom of help')
    parser.add_argument('-n', '--name', help='name of the container', required=False)
    parser.add_argument('-i', '--input', help='input file', required=False)
    parser.add_argument('-e', '--eval', action='store_true', help='evaluation', required=False)
    parser.add_argument('-u', '--ubuntu', action='store_true', help='is ubuntu', required=False)
    args = parser.parse_args()

    input_file = '../resources/mgr-m1-1/test_record_long_diff.csv'
    # input_file = '../resources/mgr-m1-1/test_record_random_diff.csv'
    if args.input:
        input_file = args.input

    ev = False
    is_ubuntu = False

    if args.eval:
        ev = True
    if args.ubuntu:
        # filepath = '../resources/mgr-m1-1/test_record_with_qdl_diff.csv'
        is_ubuntu = True

    df = pd.read_csv(input_file)
    detectors = [LocalOutlierFactorImpl(eval=ev), IsolationForestsImpl(eval=ev)] #, OneClassSVMImpl(eval=ev)]

    [detector.learn(df) for detector in detectors]
    with ThreadPoolExecutor(max_workers=5) as executor:
        pool = []
        for detector in detectors:
            print(detector.__class__.__name__)
            future = executor.submit(detector.listener, container_name=args.name, is_ubuntu=is_ubuntu)
            pool.append(future)
        for future in pool:
            future.result()
    print('done')
