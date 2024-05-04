from collections import Counter
import pandas as pd
from easier_nlp.Colorful_Console import ColoredText as CT

def list_to_freqdf(raw_list, list_name="word", show_details=False):
    freq = Counter(raw_list)  # 对列表中的元素进行频率统计
    # 将词频统计结果转换为dataframe，单词的列的名称是list_name，词频的列的名称是count
    df = pd.DataFrame(list(freq.items()), columns=[list_name, 'count'])
    df = df.sort_values(by='count', ascending=False)  # 按照词频降序排列
    df['id'] = range(1, len(df) + 1)  # 为df新增一列，代表词的id
    df['freq'] = df['count'] / df['count'].sum()  # 词频百分比
    if show_details:
        print(CT("频率统计：").blue(), freq)
        print(CT("词频统计结果：").blue())
        print(df.head(5))
    return df
