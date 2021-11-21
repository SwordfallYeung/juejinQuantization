# coding=utf-8
from __future__ import print_function, absolute_import
from gm.api import *


# 策略中必须有init方法
def init(context):
    # 同时订阅浦发银行和平安银行,数据全部到齐再触发事件
    # wait_group是否需要等待全部代码的数据到齐再触发事件
    # wait_group_timeout超时时间，从返回第一个bar开始计时， 默认是10s，超时后的bar不再返回
    subscribe(symbols='SHSE.600000,SZSE.000001', frequency='1d', count=5, wait_group=True, wait_group_timeout='10s')

#  on_bar , 来根据数据推送进行逻辑处理
def on_bar(context, bars):
    for bar in bars:
        print(bar['symbol'], bar['eob'])

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
        filename='multiEventMain.py',
        mode=MODE_BACKTEST,
        token='f19251d783b38a297687724d2cb0d1d481f14718',
        backtest_start_time='2020-11-01 08:00:00',
        backtest_end_time='2020-11-10 16:00:00',
        backtest_adjust=ADJUST_PREV,
        backtest_initial_cash=10000000,
        backtest_commission_ratio=0.0001,
        backtest_slippage_ratio=0.0001)
