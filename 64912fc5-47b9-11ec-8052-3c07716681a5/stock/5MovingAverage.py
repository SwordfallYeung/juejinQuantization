# coding=utf-8
from __future__ import print_function, absolute_import
from gm.api import *
import pandas as pd

'''
https://bbs.myquant.cn/topic/2320/2
第一步：设置参数、订阅数据。
第二步：每次订阅数据执行on_bar任务，每次计算快慢速均线、买入/卖出触发价，设置通道，跟踪止损。
第三步：每次判断是否形成金叉/死叉、是否突破通道、是否持仓，是否符合策略思路，符合的进行买卖交易。
回测期：2005-07-04 09:00:00到2018-03-05 15:00:00
回测初始资金：1000万
手续费：0.0003
滑点：0.0003

本策略以SHSE.000300为交易标的，短周期为9，长周期为18; 建立均线交叉结合通道突破动态跟踪模型。
1 双均线交叉结合通道突破：
  当均线交叉形成金叉后的Chlen个交易日内价格向上突破买入触发价且无持仓时，进行买入；
  当均线交叉形成死叉后的Chlen个交易日内价格向下突破卖出触发价且有持仓时，进行卖出。
2 跟踪止损: 
  持仓时的价格跌破跟踪止损触发价时进行止损，暂时出场； 
  出场后的ReEntryWindow个交易日内价格向上突破阻力线时再度进场。
回测数据为:SHSE.000300的1d频度bar数据
回测时间为:2005-07-04 09:00:00到2018-03-05 15:00:00
'''

# 策略中必须有init方法
def init(context):
    # 9日快速均线窗口长度
    context.short = 9      
    # 18日慢速均线窗口长度                                        
    context.long = 18     
    # 通道突破周期 12                                         
    context.Chlen = 3 
    # 跟踪止损窗口长度 8                             
    context.TrailWindow = context.short - 1  
    # 再进场通道突破周期 10                      
    context.ReEntryChLen = context.short + 1  
    # 出场到再度进场的最大间隔 15
    context.ReEntryWindow = 2*context.short - 3        
    # 交易状态,2为空仓，1为持仓，1.1为暂时出场            
    context.status = 2     
    # 形成金叉后的时间计数                                        
    context.day_1:int = 0 
    # 形成死叉后的时间计数                                         
    context.day_2:int = 0   
    # 再进场时间计数                                       
    context.day_3:int = 0            
    # 订阅交易标的                              
    context.symbol = 'SHSE.603260'    # 'SHSE.000300'
    # 订阅数据滑窗长度 19                              
    context.period = context.long + 1    

    historyData = history(symbol=context.symbol, frequency='1d', start_time='2020-03-04', end_time='2020-10-02', fields='symbol,bob,close,volume', adjust=ADJUST_PREV, df=True)
    historyData['bob'] = historyData['bob'].apply(lambda x: x.strftime('%Y-%m-%d')).tolist()
    # 计算5日均线、10日均线、20日均线、60日均线、120日均线
    historyData['fiveAvg'] = historyData['close'].rolling(5).mean()
    historyData['tenAvg'] = historyData['close'].rolling(10).mean() 
    historyData['twentyAvg'] = historyData['close'].rolling(20).mean()  
    historyData['sixtyAvg'] = historyData['close'].rolling(60).mean()
    historyData['oneHunTwentyAvg'] = historyData['close'].rolling(120).mean()

    context.historyData = historyData

    # 订阅行情                          
    subscribe(context.symbol, '1d')          
    
def on_bar(context, bars):
    # 获取通过subscribe订阅的数据 
    data = context.data(symbol=context.symbol, frequency='1d', fields='symbol,bob,close,volume')
    data['bob'] = data['bob'].apply(lambda x: x.strftime('%Y-%m-%d')).tolist()
    current_time = data['bob'].values[-1]

    print(current_time)

    context.historyData = context.historyData.append(data, ignore_index=True)
    last = context.historyData.index[-1]
    context.historyData.loc[last, 'fiveAvg'] = context.historyData['close'].tail(5).mean()
    context.historyData.loc[last, 'tenAvg'] = context.historyData['close'].tail(10).mean()
    context.historyData.loc[last, 'twentyAvg'] = context.historyData['close'].tail(20).mean()
    context.historyData.loc[last, 'sixtyAvg'] = context.historyData['close'].tail(60).mean()
    context.historyData.loc[last, 'oneHunTwentyAvg'] = context.historyData['close'].tail(120).mean()
    
    fiveAvg = context.historyData['fiveAvg']
    tenAvg = context.historyData['tenAvg']
    twentyAvg = context.historyData['twentyAvg']
    sixtyAvg = context.historyData['sixtyAvg']
    oneHunTwentyAvg = context.historyData['oneHunTwentyAvg']

    #print(context.historyData)

    # 查询持仓
    pos = context.account().position(symbol=context.symbol, side=PositionSide_Long)  

     # 交易状态,2为空仓
    if context.status == 2:
        # 9日均线上穿18日均线(金叉)，认为价格有上涨趋势 
        if fiveAvg.values[-1] > sixtyAvg.values[-1] and tenAvg.values[-1] > sixtyAvg.values[-1] and twentyAvg.values[-1] > sixtyAvg.values[-1] and  sixtyAvg.values[-1] > oneHunTwentyAvg.values[-1]:
            # 记录形成金叉的时间
            context.day_1 += 1

            # 在形成金叉信号后的Chlen个交易日内(超出时段则无效)
            if context.day_1 >= context.Chlen:
                order_percent(symbol= context.symbol , percent=0.8, side=OrderSide_Buy, order_type=OrderType_Market, position_effect=PositionEffect_Open)
                print('以市价买进到仓位')
                # 交易状态改变，1为持仓
                context.status = 1
    
    # 交易状态,1为持仓
    if context.status == 1:
        # 快速均线下穿慢速均线(死叉)，认为价格有下跌趋势
        if fiveAvg.values[-1] < sixtyAvg.values[-1]:
            # 记录形成死叉的时间
            context.day_2 += 1

            # 在形成死叉信号后的Chlen个交易日内(超出时段则无效)
            if context.day_2 > 1:
               order_close_all()
               print('以市价单全部卖出')
               # 交易状态改变，2为空仓
               context.status = 2
            

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
        filename='5MovingAverage.py',
        mode=MODE_BACKTEST,
        token='f19251d783b38a297687724d2cb0d1d481f14718',
        backtest_start_time='2020-10-03 09:00:00',  #'2020-07-04 09:00:00',
        backtest_end_time='2021-11-22 15:00:00',   # '2021-01-12 15:00:00',
        backtest_adjust=ADJUST_PREV,
        backtest_initial_cash=10000000,
        backtest_commission_ratio=0.0003,
        backtest_slippage_ratio=0.0003)

