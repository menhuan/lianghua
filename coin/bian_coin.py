from enum import Enum
from typing import List

import requests

from loguru import logger
import pandas as pd

"""
startTime: 1674802800000，时间戳
"""
class BIFreq(Enum):
    F1 = "1m"
    F5 = "5m"
    F15 = "15m"
    F30 = "30m"
    F60 = "1h"
    F4H = "4h"
    D = "1d"
    W = "1w"
    M = "1M"

def binance_kline(request):
    response = requests.get("https://api4.binance.com/api/v3/klines", request)
    logger.info(f"响应结果 code是:{response.status_code}")
    if response.status_code == 200:
        if(len(response.json()) == 0): 
            logger.info(f"输出响应是:{response.text}")
        return response.json()
    elif response.status_code == 429:
        raise Exception("请求过多，被限制！")
    elif response.status_code == 418:
        raise Exception("IP被封禁！")
    else:
        raise Exception("请求变binance数据失败！")
    
    
    



"""
[
  [
    1499040000000,      // k线开盘时间
    "0.01634790",       // 开盘价
    "0.80000000",       // 最高价
    "0.01575800",       // 最低价
    "0.01577100",       // 收盘价(当前K线未结束的即为最新价)
    "148976.11427815",  // 成交量
    1499644799999,      // k线收盘时间
    "2434.19055334",    // 成交额
    308,                // 成交笔数
    "1756.87402397",    // 主动买入成交量
    "28.46694368",      // 主动买入成交额
    "17928899.62484339" // 请忽略该参数
  ]
]
"""
def transfrom_bian_kline_to_all(binance_response: List) :
    result = []
    for index, content in enumerate(binance_response):
        # 将每一根K线转换成 RawBar 对象
        bar =  {
                "dt": str(content[0]),
                "open": content[1],
                "high": content[2],
                "low": content[3],
                "close": content[4],
                "volume": content[5],
                "end_time": content[6],
                "amount": content[7],
                "num_trade": content[8],
                "buy_volume": content[9],
                "buy_amount": content[10],
                "timepoints": content[0],
            }
        result.append(bar)

    return result


def kline(symbol: str = "BTCUSDT",
          interval: str = BIFreq.F1.value,
          startTime: int = None,
          endTime: int = None,
          limit: int = 1000) -> List[dict]:
    request_params = {"symbol": symbol, "interval": interval, "limit": limit, "startTime": startTime,
                      "endTime": endTime}
    logger.info(f"当前请求时间是参数是：{request_params}")
    binance_response = binance_kline(request_params)
    return transfrom_bian_kline_to_all(binance_response=binance_response)

def transfrom_bian_kline_to_df(binance_response: dict) :
    bars = []
    for index, content in enumerate(binance_response):
        # 将每一根K线转换成 RawBar 对象
        bar = dict(symbol=symbol, dt=content[0] + 8 * 60 * 60 * 1000,
                    id=index, freq=interval, open=content[1], close=content[4],
                    high=content[2], low=content[3],
                    vol=content[5],  # 成交量，单位：股
                    amount=content[7],  # 成交额，单位：元
                    _id=(content[0] + 8 * 60 * 60 * 1000)
                    )
        bars.append(bar)
    if not bars:
        logger.info(f"查询数据有问题:request:{request_params},response :{response.json()},status_code :{response.status_code}")
    return bars