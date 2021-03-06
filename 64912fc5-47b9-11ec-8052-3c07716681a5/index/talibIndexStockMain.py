# coding=utf-8
from __future__ import print_function, absolute_import
from gm.api import *
import pandas as pd
import numpy as np
import talib


# 策略中必须有init方法
def init(context): 
    # 取历史数据，取到上市首日
    data = history(symbol='SHSE.603260', frequency='1d', start_time='2021-04-20', end_time='2021-11-22', fields='symbol,bob,high,low,close', adjust=ADJUST_PREV, adjust_end_time='2021-11-20', df=True)
    # 将数据转化为dataframe格式
    data['bob'] = data['bob'].apply(lambda x: x.strftime('%Y-%m-%d')).tolist()

    '''https://bbs.myquant.cn/topic/1910/2'''
    # 获取合盛硅业MA指标 至少需要7个月数据 均线的获取
    data['MA5']=talib.MA(data['close'], timeperiod=5)
    #MA5=talib.MA(data['close'], timeperiod=5)
    #MA10=talib.MA(data['close'], timeperiod=10)
    data['MA10']=talib.MA(data['close'], timeperiod=10)
    #MA20=talib.MA(data['close'], timeperiod=20)
    data['MA20']=talib.MA(data['close'], timeperiod=20)
    #MA60=talib.MA(data['close'], timeperiod=60)
    data['MA60']=talib.MA(data['close'], timeperiod=60)
    print (data)
    
    # 获取合盛硅业MACD指标 至少需要7个月数据
    data['macddiff'], data['macddea'], data['macd'] = talib.MACDEXT(data['close'], fastperiod=12, fastmatype=1, slowperiod=26, slowmatype=1, signalperiod=9, signalmatype=1)
    data['macd'] = data['macd'] * 2
    print(data)
    
    # 获取合盛硅业RSI指标 至少需要7个月数据
    data['rsi6'] = talib.RSI(data['close'], timeperiod=6)
    data['rsi12'] = talib.RSI(data['close'], timeperiod=12)
    data['rsi24'] = talib.RSI(data['close'], timeperiod=24)
    print(data)

    # 获取合盛硅业WR指标 至少需要7个月数据
    data['will10'] = abs(talib.WILLR(data['high'],data['low'],data['close'], timeperiod=10))
    data['will6'] = abs(talib.WILLR(data['high'],data['low'],data['close'], timeperiod=6))
    data['will20'] = abs(talib.WILLR(data['high'],data['low'],data['close'], timeperiod=20))
    data['will80'] = abs(talib.WILLR(data['high'],data['low'],data['close'], timeperiod=80))
    print(data)

    # 获取合盛硅业KDJ指标 至少需要2个月数据
    


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
        filename='talibIndexStockMain.py',
        mode=MODE_BACKTEST,
        token='f19251d783b38a297687724d2cb0d1d481f14718',
        backtest_start_time='2020-11-01 08:00:00',
        backtest_end_time='2020-11-10 16:00:00',
        backtest_adjust=ADJUST_PREV,
        backtest_initial_cash=10000000,
        backtest_commission_ratio=0.0001,
        backtest_slippage_ratio=0.0001)

