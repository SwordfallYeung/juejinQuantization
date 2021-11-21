# coding=utf-8
from __future__ import print_function, absolute_import
from gm.api import *


# 策略中必须有init方法
def init(context):
    # 订阅浦发银行的tick
    subscribe(symbols='SHSE.600000', frequency='60s')

#  on_bar , 来根据数据推送进行逻辑处理
def on_bar(context, bars):
    # 打印当前获取的bar信息
    print(bars)

if __name__ == '__main__':
    # 在终端仿真交易和实盘交易的启动策略按钮默认是实时模式，运行回测默认是回测模式，在外部IDE里运行策略需要修改成对应的运行模式
    # mode=MODE_LIVE 实时模式, 回测模式的相关参数不生效
    # mode=MODE_BACKTEST  回测模式
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
        filename='backTestMain.py',
        mode=MODE_BACKTEST,
        token='f19251d783b38a297687724d2cb0d1d481f14718',
        backtest_start_time='2021-11-18 08:00:00',
        backtest_end_time='2021-11-18 16:00:00',
        backtest_adjust=ADJUST_PREV,
        backtest_initial_cash=10000000,
        backtest_commission_ratio=0.0001,
        backtest_slippage_ratio=0.0001)
