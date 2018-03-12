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
            ya = y1 + y2 + y3 + y7
            yb = y4 + y5 + y6 + y7
            if ya == 0:
                ed6 = 0
            else:
                ed6 = (0.1 * y1 + 0.2 * y2 + 0.4 * y3) / ya
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
    g.aa.index = [context.current_dt]
    g.aadataframe = g.aadataframe.append(g.aa)

def initialize(context):
    set_benchmark('000300.XSHG')
    set_option('use_real_price', True) 
    set_order_cost(OrderCost(open_tax=0, close_tax=0.001, \
                             open_commission=0.0003, close_commission=0.0003,\
                             close_today_commission=0, min_commission=5), type='stock')
    #context.portfolios=['000001.XSHE', '000002.XSHE']
    
    context.portfolios = get_index_stocks('000300.XSHG')
    
    g.n=1 # wlx rule. for x calculation nominator
    g.m=5  # wlx rule. for x calculation denominator
    g.P = np.matrix('10 0;0 10')
    g.Ppanel = pd.Panel(np.zeros([len(context.portfolios),2,2]),items=context.portfolios)
    for value in context.portfolios:
        g.Ppanel[value]=g.P
    g.c = 0.01
    g.lmd = 0.9
    multidx=pd.MultiIndex.from_product([context.portfolios,[0,1]])
    g.aa = pd.DataFrame(np.zeros([1, multidx.size]), columns=multidx)
    g.aadataframe = pd.DataFrame(np.zeros([1,multidx.size]),columns=multidx)
    g.waitdays=10 #wait the aa frame become stable
    g.stock_nday_out={} # dict to record stock and holding days. all stock will hold max n days and out
    g.daytolive= 20 # max days to hold a position

    #run_daily(ffb_wlx, 'every_bar')
    #run_daily(stop_retreat,'open')
    #run_daily(stoploss,'open')
    run_daily(exit_fixdays,'open')
    run_daily(trade,'open')

def before_trading_start(context):
    ffb_wlx(context)
    g.waitdays = g.waitdays-1
    for item in g.stock_nday_out.keys():
        g.stock_nday_out[item]['daytolive']=g.stock_nday_out[item]['daytolive']-1
 
def wlx_rule(context,stock):
    aa=g.aadataframe[stock]
    upserise=aa[1]
    downseries=aa[0]
    spread=upserise+downseries
    spread = np.sign(spread)
    spread = spread - spread.shift(1)
    if spread.iloc[-1]==2 and upserise.iloc[-1]>0:
        # 1 is the buy signal
        return -1
    elif spread.iloc[-1]==-2:
        # -1 is the sell signal
        return 1
    else:
        return 0

def trade(context):
    stocklist=context.portfolios
    holding = context.portfolio.positions.keys()
    for value in holding:
        wlx = wlx_rule(context,value)
        if wlx==-1:
            order_target(value, 0)
            if value in g.stock_nday_out.keys():
                g.stock_nday_out.pop(value)
    for value in stocklist:
        if g.waitdays>0:
            continue
        else:
            wlx = wlx_rule(context,value)
            if  wlx==1:
                order_target(value, 1000)
                g.stock_nday_out[value]={'date':context.current_dt,'daytolive':g.daytolive}

def exit_fixdays(context):
    for value in g.stock_nday_out.keys():
        if g.stock_nday_out[value]['daytolive'] < 1:
            order_target(value, 0)
            g.stock_nday_out.pop(value)

def enter_trend(instrument,lookbackdays):
    trends = history(lookbackdays, unit='1d', field='close', security_list=instrument, df=True, skip_paused=False, fq='pre')
    if trends.iloc[0][instrument]<trends.iloc[-1][instrument]:
        return True
    else:
        return False

def stoploss(context):
    for stock in context.portfolio.positions:
        # 如果股票最新价格除以平均成本小于0.9，即亏损超过10%
        if (context.portfolio.positions[stock].price/context.portfolio.positions[stock].avg_cost < 0.9): 
            # 调整stock的持仓为0，即卖出
            order_target(stock, 0) 
            # 输出日志：股票名 止损
            print "Stop loss\n%s 止损" % stock
            
def stop_retreat(context,nday=10,retreat=0.1):
    for stock in context.portfolio.positions:
        prices=history(nday, unit='1d', field='close', security_list=stock, df=True, skip_paused=False, fq='pre')
        ndaymax = prices.max()[stock]
        current_price = context.portfolio.positions[stock].price
        if (ndaymax-current_price)/ndaymax>retreat:
            order_target(stock, 0) 

            
def security_stopprofit(context,profit=0.1,maTime=5,maProfit=0.02):
    if len(context.portfolio.positions)>0:
        for stock in context.portfolio.positions.keys():
            avg_cost = context.portfolio.positions[stock].avg_cost
            #当前最新价格
            current_price = context.portfolio.positions[stock].price
            #最后一次交易时间
            last_buy_time =context.portfolio.positions[stock].transact_time
            #获取最后一次交易时间到当前，stock股票的最高收盘价
            max_close_price=getMaxClose(stock,last_buy_time)
            #获取是否击穿上升趋势线超过3周期的状态
            cross_after3_flag=getCrossAfterStatus(stock,last_buy_time,3)
            #获取股票当前ma值
            ma=getMaValue(stock,maTime)
            #开始判断            
            if  (current_price/max_close_price- 1 >= profit) or (current_price/ma-1>=maProfit) or  cross_after3_flag:
                log.info(str(stock) + '  个股达到止盈线，平仓止盈！')
                order_target_value(stock, 0)

def on_strategy_end(context):
    g.aadataframe.to_csv('aa.csv')