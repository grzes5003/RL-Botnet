import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from supervisor.vectors import Log


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


if __name__ == '__main__':
    # df = pd.read_csv('resources/mgr-m1-1/test_record_2_diff.csv')
    # plot_record(df)

    logs = file2log('resources/mgr-m1-1/learning_logs/learn_02.log')
    plot_learning_curve(Log.into_df(logs))
