import redis
import logging
from backend.config import settings

logger = logging.getLogger(__name__)

class MemoryRedis:
    def __init__(self):
        self._data = {}
    
    def get(self, key):
        return self._data.get(key)
    
    def set(self, key, value, ex=None):
        self._data[key] = value
        return True
    
    def ping(self):
        return True

try:
    redis_client = redis.Redis.from_url(settings.REDIS_URL, decode_responses=True, socket_connect_timeout=1)
    redis_client.ping()
    logger.info("Connected to Redis successfully.")
except Exception as e:
    logger.warning(f"Could not connect to Redis (falling back to memory): {e}")
    redis_client = MemoryRedis()

def get_cache(key: str) -> str | None:
    try:
        return redis_client.get(key)
    except Exception:
        return None

def set_cache(key: str, value: str, expire: int = 3600):
    try:
        redis_client.set(key, value, ex=expire)
    except Exception:
        pass