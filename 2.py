# coding: utf-8
import jqdata

def initialize(context):
    set_benchmark('000300.XSHG')
    set_option('use_real_price', True)
    log.info('initialize run only once')
    run_daily(market_open, time='open', reference_security='000300.XSHG')

def market_open(context):
    # 输出开盘时间
    log.info('(market_open):' + str(context.current_dt.time()))

# 下方代码为 IDE 运行必备代码
if __name__ == '__main__':
    import jqsdk
    params = {
        'token':'a4abeeb9f059dd7718d78bfa8b70b389',
        'algorithmId':5,
        'baseCapital':1000000,
        'frequency':'day',
        'startTime':'2017-06-01',
        'endTime':'2017-08-01',
        'name':"Test1",
    }
    jqsdk.run(params)