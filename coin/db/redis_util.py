import redis
import os 
from dotenv import load_dotenv
load_dotenv()

class RedisAccess:
    def __init__(self, host, port, password=None):
        self.host = host
        self.port = port
        self.password = password
        self.connection = self._connect()

    def _connect(self):
        return redis.Redis(host=self.host, port=self.port, password=self.password)

    # Add your methods for accessing Redis here
redis_host = os.getenv("REDIS_HOST", "localhost")
# Usage example:
redis_access = RedisAccess(host=redis_host, port=6379)

# Example method for accessing Redis
def get_value(key):
    return redis_access.connection.get(key)

# Example method for setting a value in Redis
def set_value(key, value):
    return redis_access.connection.set(key, value)

# Example method for deleting a key in Redis
def delete_key(key):
    return redis_access.connection.delete(key)