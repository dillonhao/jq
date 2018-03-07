
import numpy as np
import pandas as pd
from math import log



def meb(x, a, b, c):
    # return the membership of PL,PM,PS,AZ,NS,NM,NL
    # x is return , a, b, c is the boundary of the membership
    if x <= a:
        return 0.0
    if (x > a) and (x <= b):
        return (x - a) / (b - a)
    if (x > b) and (x <= c):
        return (c - x) / (c - b)
    if x > c:
        return 0.0
    if a == b:
        if x <= b:
            return 1.0
        if (x > b) and (x <= c):
            return (c - x) / (c - b)
        if x > c:
            return 0.0
    if b == c:
        if x <= a:
            return 0.0
        if (x > a) and (x <= b):
            return (x - a) / (b - a)
        if x > b:
            return 1.0

def risk_control(context):
    # control the portfolio risk
    pass

def stock_selection(context):
    # select the stock
    pass
        
def exposure_control(context):
    # control the exposure
    pass

def log_cash(context, bar_dict):
    logger.info("Remaning cash: %r" % context.portfolio.cash, context.portfolio.positions)

def ffb_wlx(context):
    c = context.c
    lmd = context.lmd
    for value in context.portfolios:
        P = np.matrix(context.Ppanel[value])
        aa = context.aa[[value]]
        aai = np.matrix(aa).T
        try:
            numerator = history_bars(value, 1, '1d', 'close').mean()
            denominator = history_bars(value, 5, '1d', 'close').mean()
            tmp = history_bars(value, 2, '1d', 'close')
            r = log(tmp[1] / tmp[0])
            avg_return = log(numerator / denominator)
            y1 = meb(avg_return, 0, c, 2 * c)
            y2 = meb(avg_return, c, 2 * c, 3 * c)
            y3 = meb(avg_return, 2 * c, 3 * c, 3 * c)
            y4 = meb(avg_return, -2 * c, -c, 0)
            y5 = meb(avg_return, -3 * c, -2 * c, -c)
            y6 = meb(avg_return, -3 * c, -3 * c, -2 * c)
            y7 = meb(avg_return, -c, 0, c)
            ya = y1 + y2 + y3 + y7
            yb = y4 + y5 + y6 + y7
            # print(ya,yb)
            if ya == 0:
                ed6 = 0
            else:
                ed6 = (0.1 * y1 + 0.2 * y2 + 0.4 * y3) / ya
            if yb == 0:
                ed7 = 0
            else:
                ed7 = (0.1 * y4 + 0.2 * y5 + 0.4 * y6) / yb
            X = np.matrix([[ed6], [ed7]])
            K = P * X / (X.T * P * X - lmd)
            aat = (aai + K * (r - X.T * aai)).T
            context.Ppanel[value]=(P - K * X.T * P) / lmd
            context.aa[[value]]=aat
        except:
            print("Error when running WLX")
    #context.aa.reset_index(drop=True)
    #context.aa.reindex(index=[context.now])
    context.aa.index = [context.now]
    context.aadataframe = context.aadataframe.append(context.aa)
    #print(context.aa.reindex(index=[context.now]))
    #print()
    context.aadataframe.to_csv('E:/wendou/aa.csv')
    
def initialize(context):
    #scheduler.run_daily(log_cash)
    context.portfolios=[ '600653.XSHG', '600651.XSHG']
    multidx=pd.MultiIndex.from_product([context.portfolios,[0,1]])

    # 是否已发送了order
    context.fired = False
    context.P = np.matrix('10 0;0 10')
    context.Ppanel = pd.Panel(np.zeros([len(context.portfolios),2,2]),items=context.portfolios)

    for value in context.portfolios:
        context.Ppanel[value]=context.P
    context.c = 0.01
    context.lmd = 0.9

    context.aa = pd.DataFrame(np.zeros([1, multidx.size]), columns=multidx)
    context.aadataframe = pd.DataFrame(np.zeros([1,multidx.size]),columns=multidx)
    #context.aapanel = pd.Panel(np.zeros([4,1,2]),items=context.portfolios, minor_axis=[0,1])
    # print(aa)
    # context.c = 0.01
    #for value in context.portfolios:
        #context.value=False #record the order is fired or not
    context.slot = 5
    context.subcash = context.stock_account.cash/context.slot
        
def before_trading(context):
    ffb_wlx(context)
    # calculate the aa, which contains all the in out signal
    # all the descion will make before the trading. The Handle_bar only exe the decision.

# 你选择的证券的数据更新将会触发此段逻辑，例如日或分钟历史数据切片或者是实时数据切片更新
def handle_bar(context, bar_dict):
    # 开始编写你的主要的算法逻辑
    #print(context.aapanel.values)
    # bar_dict[order_book_id] 可以拿到某个证券的bar信息
    # context.portfolio 可以拿到现在的投资组合状态信息
    aaa = context.aadataframe.tail(3)
    a = context.aadataframe.tail(1)
    for value in context.portfolios:
        price_nextday = history_bars(value, 1, '1d', 'close')  
        #if context.value==True:
            #print(price_nextday)
            #order_percent(value, -1)
            #context.value==False
    
        #upcondition = aaa[value].iloc[:,0]>0
        #dncondition = a[value].iloc[:,1]>0
        #if all(upcondition):
        if aaa[value].iloc[:,0].sum()>aaa[value].iloc[:,1].sum():
            #logger.info(price_nextday)
            order_percent(value, 0.2)
            context.value=True
        else:
        #if all(dncondition):
            order_percent(value, -0.2)

    # 使用order_shares(id_or_ins, amount)方法进行落单
    # TODO: 开始编写你的算法吧！
    #aa = context.aa.tail(1)
    #if aa.iloc[0, 0] > 0:
        # order_percent并且传入1代表买入该股票并且使其占有投资组合的100%
    #order_percent(000005.XSHE, 0.2)
        # context.fired = True
    #else:
        #order_percent(context.s1, -0.5)