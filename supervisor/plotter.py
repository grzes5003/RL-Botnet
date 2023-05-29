import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from supervisor.vectors import Log, Eval


def plot_record(df: pd.DataFrame):
    """plot dataframe multiple columns with time on x-axis using seaborn"""

    dfm = df.melt('time', var_name='cols', value_name='vals')
    dfm['time'] = pd.to_datetime(dfm['time'])

    sns.set_theme(style="darkgrid")
    sns.lineplot(data=dfm, x="time", y="vals", hue='cols')

    plt.xticks(rotation=45)
    plt.tight_layout()
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


def plot_detections_type(paths: [(str, str)]):
    dfs = []
    for path, name in paths:
        text = Eval.read_file(path)
        eval_arr = [Eval.from_str(line) for line in text]
        eval_df = Eval.into_df(eval_arr)
        eval_df['Method'] = name
        dfs.append(eval_df)

    df = pd.concat(dfs)
    df = df[df['type'] == 'IsolationForestsImpl']

    sns.set_theme(style="darkgrid")

    sns.lineplot(data=df, x='iter', y='anomalies', hue='Method')

    plt.title('Number of detected anomalies during evaluation (Isolation Forests)')
    plt.xlabel('Measurement')
    plt.ylabel('Number of anomalies')

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


def plot_ops():
    ...


if __name__ == '__main__':
    # df = pd.read_csv('resources/mgr-m1-1/test_record_3_diff.csv')
    # plot_record(df)

    # logs = file2log('resources/results/worm-rl/logs/worm-rl-a-02.log')
    # plot_learning_curve(Log.into_df(logs))

    # text = Eval.read_file('resources/results/worm-rl/eval/worm-rl-a-05.log')
    # eval_arr = [Eval.from_str(line) for line in text]
    # eval_df = Eval.into_df(eval_arr)
    # plot_detections(eval_df)

    paths = [
        ('resources/results/worm-rl/eval/worm-rl-a-05.log', 'Sarsa'),
        ('resources/results/worm-rl/eval/worm-rl-a-03.log', 'Q-learning'),
        ('resources/results/worm-static/eval/worm-static-a-03.log', 'Static')
    ]
    plot_detections_type(paths)
