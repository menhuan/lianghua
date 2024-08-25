"""
币安数据会存在很多个币种，虽然很多，但是我们并不是所有都需要。
如果我们可以配置多个自己选的币种。这里主要是采集数据。
"""
import os
import time
from collections import OrderedDict
import threading

from loguru import logger

from bian_coin import kline, BIFreq
import datetime

from db import utils
from db import redis_util as redis
import traceback 
from dotenv import load_dotenv

load_dotenv()

def get_time(freq):
    return {
        BIFreq.F1: 60 * 1000,
        BIFreq.F5: 5 * 60 * 1000,
        BIFreq.F15: 15 * 60 * 1000,
        BIFreq.F30: 30 * 60 * 1000,
        BIFreq.F60: 60 * 60 * 1000,
        BIFreq.F4H: 4 * 60 * 60 * 1000,
        BIFreq.D: 24 * 60 * 60 * 1000,
    }.get(freq)


# 用来计算时间间隔，每次调用的时间间隔数据,按照一次500来计算吧
def interval_time_end_time(start_time, freq):
    interval_times = os.getenv("times_interval", 1000)
    end_time = start_time + 500 * get_time(freq)
    return end_time


symbols = os.getenv("symbols", "BTCUSDT")
time_query = os.environ.get("time_query","F1")
#这里调用都是毫秒时间
def format_time(time):
    return datetime.datetime.fromtimestamp(time/1000).strftime("%Y-%m-%d %H:%M:%S")


def collect_coin():
    sleep_time = 1
    start = True
    while start:
        try:
            # 采集的开始时间，后面需要更换时间
            sleep_time = os.getenv("sleep_time", 10)
            # 当前时间
            end_time = time.time() * 1000
            start_time = os.getenv("collect_time", 1518057600000)

            # 这个时间戳下面的才进行数据采集
            for symbol in symbols.split(","):
                for _, v in BIFreq.__members__.items():
                    data_count = 0
                    if v.name in time_query.split(","):

                        collect_name = symbol + "_" + v.value

                        doucments = utils.get_last_time('redis',collect_name)
                        logger.info(f"当前开始时间是{start_time},缓存时间是：{doucments}")
                        if doucments is not None:
                            """
                            如果有数据就从这个时间开始
                            存储的是时间戳
                            """
                            if int(start_time) < int(doucments):
                                start_time = doucments 
                                logger.info(f"当前开始时间是{start_time}")
                                logger.info(f"切换数据当前开始的时间是:{(start_time)}")

                        # 小于这个时间就继续获取数据
                        # 获取开始时间
                        while int(start_time) < int(end_time):
                            try:
                                interval_time = interval_time_end_time(int(start_time), v)

                                # 根据时间戳获取数据 
                                bars = kline(symbol, interval=v.value, startTime=int(start_time), endTime=int(end_time),limit=int(os.getenv("times_interval", 1)))
                                start_time = interval_time
                                time.sleep(sleep_time)
                                if(len(bars) == 0):
                                    if collect_name is not None:
                                        utils.save_last_time("redis",collect_name, start_time)
                                    logger.info(f"当前时间{start_time}没有获取到数据")
                                    continue
                                logger.info(f"当前数据条数是:{len(bars)} ")
                                utils.save_kline_to_strogem('influxdb',bars,symbol)
                                data_count = data_count + len(bars)
                                logger.info(f"更新数据进行到{data_count},当前时间是:{ format_time(start_time) },结束时间是：{format_time(end_time)}")
                                if collect_name is not None:
                                    utils.save_last_time("redis",collect_name, start_time)
                            except Exception as e:
                                traceback.print_exc()
                                logger.error(f"K线处理失败,exception:{e}")
                                # 暂时先执行失败，后面再看看如何处理
                                raise e 
                        else:
                            logger.info(f"该币种{symbol}在该时间{v}数据爬取完毕,数据总条数是:{data_count}")
        except Exception as e:
            logger.error(f"获取k线异常,exception:{e}")
        finally:
            time.sleep(60*60*12)
            logger.info("重新访问新的一次数据")


# def get_signals(cat: CzscTraderBICoin) -> OrderedDict:
#     s = OrderedDict({"symbol": cat.symbol, "dt": cat.end_dt, "close": cat.latest_price})
#     # 使用缓存来更新信号的方法
#     s.update(get_s_like_bs(cat.kas[Freq.F30.value], di=1))
#     #s.update(zhen_cang_tu_po_V230204(cat.kas['5分钟'], di=1,n=10))
#     #s.update(zhen_cang_tu_po_V230204(cat.kas['30分钟'], di=1,n=10))
#     return s

# def trader_strategy_base(symbol):
#     tactic = {
#         "symbol": symbol,
#         "base_freq": '15分钟',
#         "freqs": ['30分钟', '60分钟',Freq.F4H.value ,Freq.D.value,Freq.W.value],
#         "get_signals": get_signals,
#         "signals_n": 0,
#     }
#     return tactic


# def notice():
#     while True:
#         try:
#             # 通知，判断是否是要检测的新号，然后发送通知。
#             for symbol in symbols.split(","):
#                 data_path = os.path.join(f"./{symbol}")
#                 dc = BiAnDataCache(data_path, sdt='2010-01-01', edt='20211209')
#                 bars = dc.bian_btc_daily(ts_code=symbol, raw_bar=True, interval=BiFreq.F30.value, frep=Freq.F30)
#                 check_signals_acc(bars,get_signals=get_signals,time_delay=24*60*60,strategy=trader_strategy_base)
#         finally:
#             logger.info("睡眠5分钟")
#             time.sleep(os.getenv("symbol_sleep_time", 5*60*60))


if __name__ == '__main__':
    collect_coin()
    #t1 = threading.Thread(target=coolect_coin)
    # t2 = threading.Thread(target=notice)
    #t1.start()
    # t2.start()