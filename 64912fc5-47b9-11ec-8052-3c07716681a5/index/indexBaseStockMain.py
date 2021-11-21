# coding=utf-8
from __future__ import print_function, absolute_import
from gm.api import *
import pandas as pd
import numpy as np

def KDJ(symbol, N, M1, M2, start_time, end_time):
    '''
    计算KDJ指标公式
    输入：data <- dataframe, 需包含开盘、收盘、最高、最低价，N, M1, M2 <- int
          end_time <- int 结束时间
    输出： 将K、D、J合并到data后的dataframe
    '''
    # 取历史数据，取到上市首日
    data = history(symbol=symbol, frequency='1d', start_time=start_time, end_time=end_time, fields='symbol,bob,close,low,high', adjust=ADJUST_PREV, df=True)

    #计算前N日最低和最高，缺失值用前n日(n<N)最小值替代
    lowList = data['low'].rolling(N).min()
    lowList.fillna(value=data['low'].expanding().min(), inplace=True)
    highList = data['high'].rolling(N).max()
    highList.fillna(value=data['high'].expanding().max(), inplace=True)
    # 计算rsv
    rsv = (data['close'] - lowList) / (highList - lowList) * 100
    # 计算k,d,j
    data['kdj_k'] = rsv.ewm(alpha=1/M1, adjust=False).mean()  # ewm是指数加权函数
    data['kdj_d'] = data['kdj_k'].ewm(alpha=1/M2, adjust=False).mean()
    data['kdj_j'] = 3.0 * data['kdj_k'] - 2.0 * data['kdj_d']
    return data

def MACD(symbol, start_time, end_time):
    '''
    输入参数： symbol <- str  标的代码
              start_time <- str 起始时间
              end_time <- 结束时间
    输出数据：
             macd <- dataframe macd指标，包括DIFF、DEA、MACD
    '''
    # 取历史数据，取到上市首日
    data = history(symbol=symbol, frequency='1d', start_time=start_time, end_time=end_time, fields='symbol,bob,close', adjust=ADJUST_PREV, df=True)
    # 将数据转化为dataframe格式
    data['bob'] = data['bob'].apply(lambda x: x.strftime('%Y-%m-%d')).tolist()

    # 计算EMA(12)和EMA(16)
    data['EMA12'] = data['close'].ewm(alpha=2 / 13, adjust=False).mean()
    data['EMA26'] = data['close'].ewm(alpha=2 / 27, adjust=False).mean()

    # 计算DIFF、DEA、MACD
    data['DIFF'] = data['EMA12'] - data['EMA26']
    data['DEA'] = data['DIFF'].ewm(alpha=2 / 10, adjust=False).mean()
    data['MACD'] = 2 * (data['DIFF'] - data['DEA'])

    # 上市首日，DIFF、DEA、MACD均为0
    data['DIFF'].iloc[0] = 0
    data['DEA'].iloc[0] = 0
    data['MACD'].iloc[0] = 0

    # 按照起止时间筛选
    MACD = data[(data['bob'] >= start_time)]

    return MACD

def DMA(symbol, start_time, end_time, N1, N2, M):
    ''' 计算DMA
        输入参数：
            symbol <- str  标的代码
            start_time <- str  开始时间
            end_time <- 结束时间
            N1 <- 大周期均值
            N2 <- 小周期均值
        输出参数：
            DMA <- dataframe
    '''
    # 取历史数据，取到上市首日
    data = history(symbol=symbol, frequency='1d', start_time=start_time, end_time=end_time, fields='symbol,bob,close', adjust=ADJUST_PREV, df=True)
    # 将数据转化为dataframe格式
    data['MA1'] = data['close'].rolling(N1).mean()
    data['MA2'] = data['close'].rolling(N2).mean()
    data['DIF'] = data['MA1'] - data['MA2']
    data['AMA'] = data['DIF'].rolling(M).mean()

    # 将数据转化为dataframe格式
    data['bob'] = data['bob'].apply(lambda x: x.strftime('%Y-%m-%d')).tolist()

    # 按起止时间筛选
    DMA = data[(data['bob'] >= start_time)]

    return DMA

# BIAS：乖离率指标计算
# BIAS1 : (CLOSE-N1日的平均值CLOSE）/N1日的平均值CLOSE*100
# BIAS2 : (CLOSE-N2日的平均值CLOSE）/N2日的平均值CLOSE*100
# BIAS3 : (CLOSE-N3日的平均值CLOSE）/N3日的平均值CLOSE*100
def BIAS(symbol, start_time, end_time, N1, N2, N3):
    '''计算乖离率指标
        输入值：symbol <- str 标的代码
              start_time <- str 开始时间
              end_time <- str 结束时间
              N1、N2、N3 <- 移动平均数
        输出值：
            BIAS <- dataframe
    '''
    # 取历史数据，取到上市首日
    data = history(symbol=symbol, frequency='1d', start_time=start_time, end_time=end_time, fields='symbol,bob,close', adjust=ADJUST_PREV, df=True)
    # 将数据转化为dataframe格式
    data['bob'] = data['bob'].apply(lambda x: x.strftime('%Y-%m-%d')).tolist()

    # 计算指标
    data['BIAS1'] = (data['close'] - data['close'].rolling(N1).mean())/data['close'].rolling(N1).mean() * 100
    data['BIAS2'] = (data['close'] - data['close'].rolling(N2).mean())/data['close'].rolling(N2).mean() * 100
    data['BIAS3'] = (data['close'] - data['close'].rolling(N3).mean())/data['close'].rolling(N3).mean() * 100

     # 按时间筛选
    BIAS = data[(data['bob'] >= start_time)]

    return BIAS

# BOLL：BOLL带指标计算
# 中轨线 = N日收盘价平均值
# 上轨线 = 中轨线 + N日收盘价标准差
# 下轨线 = 中轨线 - N日收盘价标准差
def BOLL(symbol, start_time, end_time, N):
    ''' 计算布林带
        输入参数：symbol <- str 标的代码
                start_time <- str 开始日期
                end_time <- str 结束日期
                N <- N日移动平均线
        输出参数：
               BOLL <- dataframe
    '''
    # 取历史数据，取到上市首日
    data = history(symbol=symbol, frequency='1d', start_time=start_time, end_time=end_time, fields='symbol,bob,close', adjust=ADJUST_PREV, adjust_end_time=end_time, df=True)
    # 将数据转化为dataframe格式
    data['bob'] = data['bob'].apply(lambda x: x.strftime('%Y-%m-%d')).tolist()

    # 计算指标
    data['BOLL'] = data['close'].rolling(N).mean()
    data['UB'] = data['BOLL'] + 2 * data['close'].rolling(N).std()
    data['LB'] = data['BOLL'] - 2 * data['close'].rolling(N).std()

    # 按时间筛选
    BOLL = data[(data['bob'] >= start_time)]

    return BOLL

# RSI指标计算
# RSI = N日内收盘价涨数和的均值/N日内收盘价涨和跌的均值*100
def RSI(symbol, start_time, end_time, N1, N2, N3):
    ''' 计算RSI相对强弱指数
        输入参数：symbol <- str 标的代码
                start_time <- str 开始日期
                end_time <- str 结束日期
                N <- N日移动平均线
        输出参数：
               RSI <- dataframe
    '''
    # 取历史数据，取到上市首日
    data = history(symbol=symbol, frequency='1d', start_time=start_time, end_time=end_time, fields='symbol,bob,close,pre_close', adjust=ADJUST_PREV, adjust_end_time=end_time, df=True)
    # 将数据转化为dataframe格式
    data['bob'] = data['bob'].apply(lambda x: x.strftime('%Y-%m-%d')).tolist()

    # 计算指标
    data['change'] = data['close'] - data['pre_close']          # 计算涨跌幅
    data.loc[(data['pre_close'] == 0), 'change'] = 0            # 如果是首日，change记为0
    data['x'] = data['change'].apply(lambda x: max(x, 0))       # 涨跌幅<0换为0

    data['RSI1'] = data['x'].ewm(alpha=1 / N1, adjust=False).mean() / (np.abs(data['change']).ewm(alpha=1/N1, adjust=False).mean()) * 100
    data['RSI2'] = data['x'].ewm(alpha=1 / N2, adjust=False).mean() / (np.abs(data['change']).ewm(alpha=1 / N2, adjust=False).mean()) * 100
    data['RSI3'] = data['x'].ewm(alpha=1 / N3, adjust=False).mean() / (np.abs(data['change']).ewm(alpha=1 / N3, adjust=False).mean()) * 100

    # 输出
    RSI = data[(data['bob'] >= start_time)]

    return RSI

# WR威廉指标计算
# WR(N) = 100 * [HIGH(N)-C] / [HIGH(N)-LOW(N)]
def WR(symbol, start_time, end_time, N1, N2):
    ''' 计算威廉指数
        输入：symbol <- str 标的代码
             start_time <- str 开始时间
             end_time <- 结束时间
             N <- 周期数
        输出：WR <- dataframe
    '''
    # 取历史数据，取到上市首日
    data = history(symbol=symbol, frequency='1d', start_time=start_time, end_time=end_time, fields='symbol,bob,close,high,low', adjust=ADJUST_PREV, adjust_end_time=end_time, df=True)
    # 将数据转化为dataframe格式
    data['bob'] = data['bob'].apply(lambda x: x.strftime('%Y-%m-%d')).tolist()

     # 计算指标
    data['WR1'] = 100 * (data['high'].rolling(N1).max() - data['close']) / (data['high'].rolling(N1).max() - data['low'].rolling(N1).min())
    data['WR2'] = 100 * (data['high'].rolling(N2).max() - data['close']) / (data['high'].rolling(N2).max() - data['low'].rolling(N2).min())

    # 缺失值填充
    data['WR1'].fillna(value=100 * (data['high'].expanding().max() - data['close']) / (data['high'].expanding().max() - data['low'].expanding().min()), inplace=True)
    data['WR2'].fillna(value=100 * (data['high'].expanding().max() - data['close']) / (data['high'].expanding().max() - data['low'].expanding().min()), inplace=True)
    # 输出
    WR = data[(data['bob'] >= start_time)]

    return WR

def MA(symbol, start_time, end_time):
    '''
    含义：求简单移动平均。参数n:n日移动平均值，默认n=5
    用法：MA(X,N)，求X的N日移动平均值。算法：(X1+X2+X3+，，，+Xn)/N。例如：MA(CLOSE,10)表示求10日均价。
    '''
    # 取历史数据，取到上市首日
    data = history(symbol=symbol, frequency='1d', start_time=start_time, end_time=end_time, fields='symbol,bob,close', adjust=ADJUST_PREV, adjust_end_time=end_time, df=True)
    # 将数据转化为dataframe格式
    data['bob'] = data['bob'].apply(lambda x: x.strftime('%Y-%m-%d')).tolist()
    data['MA5']=data['close'].rolling(5).mean()
    data['MA10']=data['close'].rolling(10).mean()
    data['MA20']=data['close'].rolling(20).mean()
    data['MA60']=data['close'].rolling(60).mean()
    data['MA120']=data['close'].rolling(120).mean()
    return data

def EMA(symbol, start_time, end_time):
    '''
    含义：求指数平滑移动平均。参数n:n日指数平滑移动平均。默认m=5
    用法：EMA(X,N)，求X的N日指数平滑移动平均。算法：若Y=EMA(X,N)则Y=[2*X+(N-1)*Y']/(N+1)，其中Y'表示上一周期Y值。例如：EMA(CLOSE,30)表示求30日指数平滑均价。
    '''
    # 取历史数据，取到上市首日
    data = history(symbol=symbol, frequency='1d', start_time=start_time, end_time=end_time, fields='symbol,bob,close', adjust=ADJUST_PREV, adjust_end_time=end_time, df=True)
    # 将数据转化为dataframe格式
    data['bob'] = data['bob'].apply(lambda x: x.strftime('%Y-%m-%d')).tolist()

    data['EMA8']=data['close'].ewm(span=8).mean()
    data['EMA21']=data['close'].ewm(span=21).mean()
    data['EMA50']=data['close'].ewm(span=50).mean()

    return data

# 策略中必须有init方法
def init(context):
    '''https://bbs.myquant.cn/topic/2050/2'''
    # 获取合盛硅业KDJ指标 至少需要2个月数据
    #kdjData = KDJ('SHSE.603260', 9, 3, 3, '2021-9-20', '2021-11-20')
    #print(kdjData)

    # 获取合盛硅业MACD指标 至少需要7个月数据
    #macdData = MACD('SHSE.603260', '2021-04-20', '2021-11-20')
    #print(macdData)

    # 获取合盛硅业DMA指标 至少需要7个月数据
    #dmaData = DMA('SHSE.603260', '2021-04-20', '2021-11-20', N1 = 10, N2 = 50, M = 6)
    #print(dmaData)

    # 获取合盛硅业BIAS指标 至少需要7个月数据
    #biasData = BIAS('SHSE.603260', '2021-04-20', '2021-11-20', N1 = 6, N2 = 12, N3 = 24)
    #print(biasData)

    # 获取合盛硅业BOLL指标 至少需要7个月数据
    #bollData = BOLL('SHSE.603260', '2021-04-20', '2021-11-20', N = 20)
    #print(bollData)
    
    # 获取合盛硅业RSI指标 至少需要7个月数据
    #rsiData = RSI('SHSE.603260', '2021-04-20', '2021-11-20', N1 = 6, N2 = 12, N3 = 24)
    #print(rsiData)

    # 获取合盛硅业WR指标 至少需要7个月数据
    #wrData = WR('SHSE.603260', '2021-04-20', '2021-11-20', N1 = 10, N2 = 6)
    #print(wrData)

    '''https://bbs.myquant.cn/topic/2294/2'''
    # 获取合盛硅业MA指标 至少需要7个月数据
    #maData = MA('SHSE.603260', '2021-01-20', '2021-11-20')
    #print(maData)

    # 获取合盛硅业EMA指标 至少需要7个月数据
    emaData = EMA('SHSE.603260', '2021-01-20', '2021-11-20')
    print(emaData)

if __name__ == '__main__':
    '''
        strategy_id策略ID, 由系统生成
        filename文件名, 请与本文件名保持一致
        mode运行模式, 实时模式:MODE_LIVE回测模式:MODE_BACKTEST
        token绑定计算机的ID, 可在系统设置-密钥管理中生成
        backtest_start_time回测开始时间
        backtest_end_time回测结束时间
        backtest_adjust股票复权方式, 不复权:ADJUST_NONE前复权:ADJUST_PREV后复权:ADJUST_POST
        backtest_initial_cash回测初始资金
        backtest_commission_ratio回测佣金比例
        backtest_slippage_ratio回测滑点比例
        '''
    run(strategy_id='64912fc5-47b9-11ec-8052-3c07716681a5',
        filename='indexBaseStockMain.py',
        mode=MODE_BACKTEST,
        token='f19251d783b38a297687724d2cb0d1d481f14718',
        backtest_start_time='2020-11-01 08:00:00',
        backtest_end_time='2020-11-10 16:00:00',
        backtest_adjust=ADJUST_PREV,
        backtest_initial_cash=10000000,
        backtest_commission_ratio=0.0001,
        backtest_slippage_ratio=0.0001)

