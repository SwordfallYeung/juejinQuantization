# coding=utf-8
from __future__ import print_function, absolute_import
from gm.api import *


# 策略中必须有init方法
def init(context):
    # 获取到交易标的基本信息，与时间无关
    huShenDf = get_instrumentinfos(symbols=None, exchanges=['SHSE','SZSE'], sec_types=SEC_TYPE_STOCK , names=None, fields='symbol,sec_name', df=True)
    print(huShenDf)

    # 上证指数成分股
    #huDf = get_constituents(index='SHSE.000001', fields='symbol, weight', df=True)
    #print(huDf)
    # 深证成指成分股
    #shenDf = get_constituents(index='SZSE.399001', fields='symbol, weight', df=True)
    #print(shenDf)
    # 创业板指成分股
    #chuangDf = get_constituents(index='SZSE.399006', fields='symbol, weight', df=True)
    #print(chuangDf)

    

def algo(context):
    # 以市价购买200股浦发银行股票， price在市价类型不生效
    order_volume(symbol='SHSE.600000', volume=200, side=OrderSide_Buy,
                 order_type=OrderType_Market, position_effect=PositionEffect_Open, price=0)

# 查看最终的回测结果
def on_backtest_finished(context, indicator):
    print(indicator)


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
        filename='allSymbolMain.py',
        mode=MODE_BACKTEST,
        token='f19251d783b38a297687724d2cb0d1d481f14718',
        backtest_start_time='2020-11-01 08:00:00',
        backtest_end_time='2020-11-10 16:00:00',
        backtest_adjust=ADJUST_PREV,
        backtest_initial_cash=10000000,
        backtest_commission_ratio=0.0001,
        backtest_slippage_ratio=0.0001)

