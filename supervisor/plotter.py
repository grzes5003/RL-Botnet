import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from supervisor.vectors import Log, Eval


def plot_record(df: pd.DataFrame):
    """plot dataframe multiple columns with time on x-axis using seaborn"""

    dfm = df.melt('time', var_name='cols', value_name='vals')

    sns.set_theme(style="darkgrid")
    sns.catplot(data=dfm, x="time", y="vals", kind='point', hue='cols', height=5, aspect=2)
    plt.show()


def file2log(path: str):
    """read file and return list of logs"""
    with open(path, 'r') as f:
        return [Log.from_str(line) for line in f if 'log:' in line]


def plot_learning_curve(df: pd.DataFrame):
    sns.set_theme(style="darkgrid")

    alt_df = df.groupby('log', as_index=False).last()
    sns.lineplot(data=alt_df, x='log', y='reward_sum')

    plt.title('RL reward in each episode')
    plt.xlabel('episode')
    plt.ylabel('reward')

    plt.show()


def plot_detections(df: pd.DataFrame):
    sns.set_theme(style="darkgrid")

    sns.lineplot(data=df, x='iter', y='anomalies', hue='type')

    plt.title('RL reward in each episode')
    plt.xlabel('episode')
    plt.ylabel('number of anomalies')

    plt.show()

def plot_detections_cum(df: pd.DataFrame):
    df['anomalies'] = df.sort_values(['type', 'iter'], ascending=True).groupby('type')['anomalies'].diff()
    # df['anomalies'] = df['anomalies'].cumsum()

    sns.set_theme(style="darkgrid")

    sns.lineplot(data=df, x='iter', y='anomalies', hue='type')

    plt.title('RL reward in each episode')
    plt.xlabel('episode')
    plt.ylabel('number of anomalies')

    plt.show()


if __name__ == '__main__':
    # df = pd.read_csv('resources/mgr-m1-1/test_record_2_diff.csv')
    # plot_record(df)
    #
    # logs = file2log('resources/mgr-m1-1/learning_logs/learn_02.log')
    # plot_learning_curve(Log.into_df(logs))

    text = Eval.read_file('resources/mgr-m1-1/eval_logs/eval_03.log')
    eval_arr = [Eval.from_str(line) for line in text]
    eval_df = Eval.into_df(eval_arr)
    plot_detections(eval_df)
