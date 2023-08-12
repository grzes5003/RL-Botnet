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


def plot_learning_curve(df: pd.DataFrame, algorithm: str = 'DQN'):
    sns.set_theme(style="whitegrid")

    alt_df = df.groupby('log', as_index=False).last()
    sns.lineplot(data=alt_df, x='log', y='reward_sum', color="tab:blue", label="Reward")
    sns.regplot(x=alt_df['log'], y=alt_df['reward_sum'], scatter=False, color="tab:red", label="Regression Line")

    plt.title(f'Reward in each episode ({algorithm})')
    plt.xlabel('Iteration')
    plt.ylabel('Reward')

    plt.show()


def plot_detections(df: pd.DataFrame):
    sns.set_theme(style="darkgrid")

    sns.lineplot(data=df, x='iter', y='anomalies', hue='type')

    plt.title('RL reward in each episode')
    plt.xlabel('episode')
    plt.ylabel('number of anomalies')

    plt.show()


def plot_detections_type(paths: [(str, str)], type: str = 'IsolationForestsImpl', additional: str = 'Isolation Forests, Random IoT device'):
    dfs = []
    for path, name in paths:
        text = Eval.read_file(path)
        eval_arr = [Eval.from_str(line) for line in text]
        eval_df = Eval.into_df(eval_arr)
        eval_df['Method'] = name
        dfs.append(eval_df)

    df = pd.concat(dfs)
    df = df[df['type'] == type]

    sns.set_theme(style="darkgrid")

    sns.lineplot(data=df, x='iter', y='anomalies', hue='Method')

    plt.title(f'Number of detected anomalies during evaluation\n {additional}')
    plt.xlabel('Detector iteration')
    plt.ylabel('Number of detected anomalies')

    plt.xlim(0, 200)
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


def plot_detections_heatmap(path: str):
    text = Eval.read_file(path)
    eval_arr = [Eval.from_str(line) for line in text]
    df = Eval.into_df(eval_arr)

    df = df[df['type'] == 'IsolationForestsImpl']

    sns.set_theme(style="whitegrid")

    # df = df.pivot(index='iter', columns='type', values='anomalies')
    sns.heatmap(df, annot=True, fmt="d", linewidths=.5, cmap="YlGnBu")

    plt.title('Number of detected anomalies during evaluation')
    plt.xlabel('Detector iteration')
    plt.ylabel('Number of detected anomalies')

    plt.show()


def plot_ops():
    paths = [
        ('resources/results/worm-dql/eval/worm-dql-a-02.log', 'DQN'),
        ('resources/results/worm-rl/eval/worm-rl-a-06.log', 'Sarsa'),
        ('resources/results/worm-rl/eval/worm-rl-a-07.log', 'Q-learning'),
        ('resources/results/worm-static/eval/worm-static-a-04.log', 'Static')
    ]
    plot_detections_type(paths, 'IsolationForestsImpl', 'Isolation Forests, Static IoT device')

    paths = [
        ('resources/results/worm-dql/eval/worm-dql-a-02.log', 'DQN'),
        ('resources/results/worm-rl/eval/worm-rl-a-06.log', 'Sarsa'),
        ('resources/results/worm-rl/eval/worm-rl-a-07.log', 'Q-learning'),
        ('resources/results/worm-static/eval/worm-static-a-04.log', 'Static')
    ]
    plot_detections_type(paths, 'LocalOutlierFactorImpl', 'Local Outlier Factor, Static IoT device')

    paths = [
        ('resources/results/worm-dql/eval/worm-dql-b-02.log', 'DQN'),
        ('resources/results/worm-rl/eval/worm-rl-b-06.log', 'Sarsa'),
        ('resources/results/worm-rl/eval/worm-rl-b-07.log', 'Q-learning'),
        ('resources/results/worm-static/eval/worm-static-b-04.log', 'Static')
    ]
    plot_detections_type(paths, 'IsolationForestsImpl', 'Isolation Forests, Random IoT device')

    paths = [
        ('resources/results/worm-dql/eval/worm-dql-b-02.log', 'DQN'),
        ('resources/results/worm-rl/eval/worm-rl-b-06.log', 'Sarsa'),
        ('resources/results/worm-rl/eval/worm-rl-b-07.log', 'Q-learning'),
        ('resources/results/worm-static/eval/worm-static-b-04.log', 'Static')
    ]
    plot_detections_type(paths, 'LocalOutlierFactorImpl', 'Local Outlier Factor, Random IoT device')


if __name__ == '__main__':
    sns.set_style("whitegrid")
    # df = pd.read_csv('resources/mgr-m1-1/test_record_3_diff.csv')
    # plot_record(df)

    path_rl = 'resources/results/worm-rl/logs'
    path_dql = 'resources/results/worm-dql/logs'

    # logs = file2log(f'{path_dql}/worm-dql-a-02.log')
    # logs = file2log(f'{path_rl}/worm-rl-a-07.log')
    # plot_learning_curve(Log.into_df(logs), 'Q-learning')

    # text = Eval.read_file('resources/results/worm-rl/eval/worm-rl-a-05.log')
    # eval_arr = [Eval.from_str(line) for line in text]
    # eval_df = Eval.into_df(eval_arr)
    # plot_detections(eval_df)

    # plot_ops()

    plot_detections_heatmap('resources/results/worm-rl/eval/worm-rl-a-07.log')
