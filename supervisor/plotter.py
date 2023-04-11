import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt


def plot_record(df: pd.DataFrame):
    """plot dataframe multiple columns with time on x-axis using seaborn"""

    dfm = df.melt('time', var_name='cols', value_name='vals')

    sns.set_theme(style="darkgrid")
    sns.catplot(data=dfm, x="time", y="vals", kind='point', hue='cols', height=5, aspect=2)
    plt.show()


if __name__ == '__main__':
    df = pd.read_csv('resources/mgr-m1-1/test_record_2_diff.csv')
    plot_record(df)
