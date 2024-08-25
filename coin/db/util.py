import datetime

import db.redis_util as redis
import db.influxdb as influxdb
from loguru import logger
"""
根据不同的action，返回想要的时间
"""
def get_last_time(action,key=None):
    current_time = datetime.datetime.now()
    if action == 'redis':
        return redis.get_value(key)
    elif action == 'mongo':
        return current_time
    else:
        raise ValueError(f'Invalid action:{action}')

def save_last_time(action,key,value):
    if action == 'redis':
        result = redis.set_value(key,value)
        logger.info(f'save_last_time:{result},value:{value}')
    elif action == 'mongo':
        return value
    else:
        raise ValueError('Invalid action')


def save_kline_to_strogem(action,kline,symbol):
    if action == 'influxdb':
        influxdb.insert_coin_data_into_influxdb(symbol,kline)
    else:
        raise ValueError(f'Invalid action:{action}')

# Example usage
get_last_time('redis',"test_key")