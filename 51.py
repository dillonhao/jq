
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
            numerator = history(g.n+1, unit='1d', field='close', security_list=value, df=True, skip_paused=False, fq='pre')[:-1].mean()
            denominator =history(g.m+1, unit='1d', field='close', security_list=value, df=True, skip_paused=False, fq='pre')[:-1].mean()
            tmp = history(2, unit='1d', field='close', security_list=value, df=True, skip_paused=False, fq='pre')
            r = log(tmp.iloc[1] / tmp.iloc[0])
            avg_return = log(numerator / denominator)
            if np.isnan(avg_return):
                avg_return=0
            y1 = meb(avg_return, 0, c, 2 * c)
            y2 = meb(avg_return, c, 2 * c, 3 * c)
            y3 = meb(avg_return, 2 * c, 3 * c, 3 * c)
            y4 = meb(avg_return, -2 * c, -c, 0)
            y5 = meb(avg_return, -3 * c, -2 * c, -c)
            y6 = meb(avg_return, -3 * c, -3 * c, -2 * c)
            y7 = meb(avg_return, -c, 0, c)
            #print(value,avg_return,y1,y2,y3,y7)
            ya = y1 + y2 + y3 + y7
            yb = y4 + y5 + y6 + y7
            # print(ya,yb)
            if ya == 0:
                ed6 = 0
            else:
                ed6 = (-0.1 * y1 - 0.2 * y2 - 0.4 * y3) / ya
            if yb == 0:
                ed7 = 0
            else:
                ed7 = (0.1 * y4 + 0.2 * y5 + 0.4 * y6) / yb
            X = np.matrix([[ed6], [ed7]])
            K = P * X / (X.T * P * X + lmd)
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
    #g.aadataframe.to_csv('E:/wendou/aa.csv')
    
def initialize(context):
    set_benchmark('000300.XSHG')
    set_option('use_real_price', True) 
    set_order_cost(OrderCost(open_tax=0, close_tax=0.001, \
                             open_commission=0.0003, close_commission=0.0003,\
                             close_today_commission=0, min_commission=5), type='stock')
    context.portfolios=['000001.XSHE', '000002.XSHE', '000008.XSHE', '000009.XSHE', '000027.XSHE', '000039.XSHE', '000060.XSHE', '000061.XSHE', '000063.XSHE', '000069.XSHE', '000100.XSHE', '000156.XSHE', '000157.XSHE', '000166.XSHE', '000333.XSHE', '000338.XSHE', '000402.XSHE', '000413.XSHE', '000415.XSHE', '000423.XSHE', '000425.XSHE', '000503.XSHE', '000538.XSHE', '000540.XSHE', '000555.XSHE', '000559.XSHE', '000568.XSHE', '000623.XSHE', '000625.XSHE', '000627.XSHE', '000630.XSHE', '000651.XSHE', '000671.XSHE', '000686.XSHE', '000709.XSHE', '000712.XSHE', '000718.XSHE', '000725.XSHE', '000728.XSHE', '000738.XSHE', '000750.XSHE', '000768.XSHE', '000776.XSHE', '000778.XSHE', '000783.XSHE', '000792.XSHE', '000793.XSHE', '000800.XSHE', '000826.XSHE', '000839.XSHE', '000858.XSHE', '000876.XSHE', '000895.XSHE', '000917.XSHE', '000938.XSHE', '000963.XSHE', '000977.XSHE', '000983.XSHE', '001979.XSHE', '002007.XSHE', '002008.XSHE', '002024.XSHE', '002027.XSHE', '002049.XSHE', '002065.XSHE']
    #context.portfolios = get_index_stocks('000300.XSHG')
    g.n=1
    g.m=5
    #tmp = history(2, unit='1d', field='close', security_list='000300.XSHG', df=True, skip_paused=False, fq='pre')
    #print(tmp)

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
    g.long_position=0
    #g.subcash = context.stock_account.cash/context.slot
    run_daily(ffb_wlx, 'every_bar')
    run_weekly(trade,1, time='close')

def before_trading_start(context):
    ffb_wlx(context)
    
   
        
def on_strategy_end(context):
    g.aadataframe.to_csv('aa.csv')
    
def trade(context):
    aa = g.aadataframe.tail(1)
    aa = aa.T
    upserise = aa.xs(1,level=1)
    downseries = aa.xs(0,level=1)
    decison=upserise - downseries
    decison.sort_values(by=[0],ascending=False).head(5).index
    print(Context.Portfolio.positions)
    #if g.long_position<g.slot
    