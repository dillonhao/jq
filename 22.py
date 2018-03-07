
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

def ffb_wlx(context):
    c = g.c
    lmd = g.lmd
    for value in context.portfolios:
        P = np.matrix(g.Ppanel[value])
        aa = g.aa[[value]]
        aai = np.matrix(aa).T

        try:
            numerator = history(g.n, unit='1d', field='close', security_list=value, df=True, skip_paused=False, fq='pre').mean()
            denominator =history(g.m, unit='1d', field='close', security_list=value, df=True, skip_paused=False, fq='pre').mean()
            tmp = history(2, unit='1d', field='close', security_list=value, df=True, skip_paused=False, fq='pre')
            print(type(tmp))
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
            g.Ppanel[value]=(P - K * X.T * P) / lmd
            g.aa[[value]]=aat
        except e:
            print(e)
    #g.aa.reset_index(drop=True)
    #g.aa.reindex(index=[context.now])
    g.aa.index = [context.current_dt]
    g.aadataframe = g.aadataframe.append(g.aa)
    #print(g.aa.reindex(index=[g.now]))
    #print()
    g.aadataframe.to_csv('E:/wendou/aa.csv')
    
def initialize(context):
    set_benchmark('000300.XSHG')
    set_option('use_real_price', True) 
    set_order_cost(OrderCost(open_tax=0, close_tax=0.001, \
                             open_commission=0.0003, close_commission=0.0003,\
                             close_today_commission=0, min_commission=5), type='stock')
    context.portfolios=[ '600653.XSHG', '600651.XSHG']
    g.stocks = get_index_stocks('000300.XSHG')
    g.n=1
    g.m=5
    tmp = history(2, unit='1d', field='close', security_list='000300.XSHG', df=True, skip_paused=False, fq='pre')
    print(tmp[0])

    multidx=pd.MultiIndex.from_product([context.portfolios,[0,1]])

    # 是否已发送了order
    g.fired = False
    g.P = np.matrix('10 0;0 10')
    g.Ppanel = pd.Panel(np.zeros([len(context.portfolios),2,2]),items=context.portfolios)

    for value in context.portfolios:
        g.Ppanel[value]=g.P
    g.c = 0.01
    g.lmd = 0.9

    g.aa = pd.DataFrame(np.zeros([1, multidx.size]), columns=multidx)
    g.aadataframe = pd.DataFrame(np.zeros([1,multidx.size]),columns=multidx)
    g.slot = 5
    #g.subcash = context.stock_account.cash/context.slot
    #run_daily(ffb_wlx, 'every_bar')
    
def before_trading(context):
    ffb_wlx(context)
    # calculate the aa, which contains all the in out signal
    # all the descion will make before the trading. The Handle_bar only exe the decision.

# 你选择的证券的数据更新将会触发此段逻辑，例如日或分钟历史数据切片或者是实时数据切片更新
def handle_bar(context, bar_dict):
    # 开始编写你的主要的算法逻辑
    #print(g.aapanel.values)
    # bar_dict[order_book_id] 可以拿到某个证券的bar信息
    # context.portfolio 可以拿到现在的投资组合状态信息
    aaa = g.aadataframe.tail(3)
    a = g.aadataframe.tail(1)
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
            g.value=True
        else:
        #if all(dncondition):
            order_percent(value, -0.2)

    # 使用order_shares(id_or_ins, amount)方法进行落单
    # TODO: 开始编写你的算法吧！
    #aa = g.aa.tail(1)
    #if aa.iloc[0, 0] > 0:
        # order_percent并且传入1代表买入该股票并且使其占有投资组合的100%
    #order_percent(000005.XSHE, 0.2)
        # g.fired = True
    #else:
        #order_percent(g.s1, -0.5)