from typing import List
from influxdb_client import InfluxDBClient
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
from distutils.util import strtobool

import random
from datetime import datetime, timedelta
from typing import List, Dict
from influxdb_client import InfluxDBClient, Bucket, Organization
from dotenv import load_dotenv
import os 
from loguru import logger
import json
load_dotenv()
influxdb_host = os.getenv("INFLUXDB_HOST", "localhost")
token=os.environ.get('INFLUXDB_TOKEN')
org=os.environ.get('org')
INFLUXDB_V2_VERIFY_SSL=strtobool(os.environ.get('INFLUXDB_V2_VERIFY_SSL','False'))
INFLUXDB_V2_TIMEOUT=int(os.environ.get('INFLUXDB_V2_TIMEOUT','30000'))
logger.info(f"加载环境变量:{influxdb_host},{token},{INFLUXDB_V2_VERIFY_SSL}")
DATABASE = os.getenv("DATABASE", "binance")

client = InfluxDBClient(url=f'{influxdb_host}', token=f"{token}", org=f"{org}",verify_ssl=INFLUXDB_V2_VERIFY_SSL,timeout=INFLUXDB_V2_TIMEOUT) # type: ignore


# 查询最新数据
def query_latest_data(database, measurement):
    query_api = client.query_api()
    print("开始输出内容")
    query = f"""from(bucket:\"{database}\")
                |> range(start: -30d) 
                |> filter(fn: (r) => r._measurement == \"{measurement}\")
                |>  pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value") """
    #result = query_api.query(query).to_values(columns=['_field', '_value','_time'])
    result = query_api.query_data_frame(query)
    print(f"输出结果\n:{result}")
    return result



# 插入数据
def insert_data_into_influxdb(database, measurement, data_list: List[dict]):
    write_api = client.write_api(write_options=SYNCHRONOUS)
    points = [
        Point
        .measurement(measurement)
        .time(data['timepoints'], WritePrecision.MS)
        .field("dt", data['dt'])
        .field("open", data['open'])
        .field("high", data['high'])
        .field("low", data['low'])
        .field("close", data['close'])
        .field("volume", data['volume'])
        .field("st", data['end_time'])
        .field("amount", data['amount'])
        .field("num_trade", data['num_trade'])
        .field("buy_volume", data['buy_volume'])
        .field("buy_amount", data['buy_amount'])
        for data in data_list
    ]
    response = write_api.write(database,f"{org}", points)
    logger.info(f"运行结束:{response}")

def insert_coin_data_into_influxdb(measurement, data_list: List[dict]):
   insert_data_into_influxdb(DATABASE,measurement, data_list)

def generate_data(start_time: datetime, end_time: datetime, num_points: int) -> List[Dict[str, any]]:
    time_step = (end_time - start_time) / num_points
    return [
        {
            "time": (start_time + i * time_step).isoformat(),
            "field1": random.random(),
            "field2": random.random(),
        }
        for i in range(num_points)
    ]


def create_dataexample():
    start_time = datetime.now() - timedelta(days=1)
    end_time = datetime.now()
    data_list = generate_data(start_time, end_time, 100)
    print("输出数据")
    insert_data_into_influxdb("mydb", "my_measurement", data_list)



if __name__ == '__main__':
    #create_dataexample()
    query_latest_data("binance","my_measurement")