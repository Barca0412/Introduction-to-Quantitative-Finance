import os
import pandas as pd
from technical import *
pd.set_option('expand_frame_repr', False)  # 当列太多时不换行
pd.set_option('display.max_rows', 5000)  # 最多显示数据的行数

# ====设定测试参数，可以自行修改
# 后续计算N日后涨跌幅所需参数
day_list = [1, 5, 10, 20]
# 测试时间段，可根据数据时间更改
start_time = '20070101'
end_time = '20220930'

# ====获取所有股票数据的股票代码
# 获取股票文件夹路径
file_path = os.path.abspath(os.path.dirname(__file__)) + '/股票数据/'  # 返回当前文件路径
# 获取文件夹下的所有csv文件的文件路径
file_list = os.listdir(file_path)
file_list = [f for f in file_list if '.csv' in f]

# ====遍历每个股票
tables = []
for f in file_list:
    print(f)
    # 读取这个数据的数据
    table = pd.read_csv(os.path.join(file_path, f), encoding='gbk', parse_dates=['交易日期'])

    # 计算你需要的技术指标
    table = technical_indicator(table)

    # 计算未来N日涨跌幅
    for day in day_list:
        table['%s日后涨跌幅' % day] = table['收盘价_复权'].shift(0 - day) / table['收盘价_复权'] - 1
        table['%s日后是否上涨' % day] = table['%s日后涨跌幅' % day] > 0
        table['%s日后是否上涨' % day].fillna(value=False, inplace=True)

    # 选取制定时间范围内的股票
    table = table[table['交易日期'] >= pd.to_datetime(start_time)]
    table = table[table['交易日期'] <= pd.to_datetime(end_time)]

    tables.append(table)

all_table = pd.concat(tables, ignore_index=True)

# =====分析数据
# 计算N日后涨跌幅大于0的概率
for signal, group in all_table.groupby('signal'):
    if signal == 1:
        print('\n', '=' * 10, '看涨信号', '=' * 10)
    elif signal == 0:
        print('\n', '=' * 10, '看跌信号', '=' * 10)
    print(group[[str(i) + '日后涨跌幅' for i in day_list]].describe())
    
    for i in day_list:
        if signal == 1:
            print(str(i) + '天后涨跌幅大于0概率', '\t', float(group[group[str(i) + '日后涨跌幅'] > 0].shape[0]) / group.shape[0])
        elif signal == 0:
            print(str(i) + '天后涨跌幅小于0概率', '\t', float(group[group[str(i) + '日后涨跌幅'] < 0].shape[0]) / group.shape[0])

