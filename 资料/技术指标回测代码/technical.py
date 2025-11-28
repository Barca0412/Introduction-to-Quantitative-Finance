def technical_indicator(table):

    # =======以下计算指标的公式，可以修改
    table['LOW_N'] = table['最低价_复权'].rolling(40).min()
    table['HIGH_N'] = table['最高价_复权'].rolling(40).max()
    table['RSV'] = (table['收盘价_复权'] - table['LOW_N']) / (table['HIGH_N'] - table['LOW_N']) * 100
    table['K'] = table['RSV'].ewm(span=(3-1), adjust=False).mean()
    table['D'] = table['K'].ewm(span=(3-1), adjust=False).mean()


    # =======以下计算交易信号，可以修改
    # 金叉死叉信号
    table.loc[(table['K'].shift(1) <= table['D'].shift(1)) & (table['K'] > table['D']), 'signal'] = 1  # 买入信号
    table.loc[(table['K'].shift(1) >= table['D'].shift(1)) & (table['K'] < table['D']), 'signal'] = 0  # 卖出信号


    return table
