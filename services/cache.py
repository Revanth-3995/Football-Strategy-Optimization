import redis
from backend.config import settings

redis_client = redis.Redis.from_url(settings.REDIS_URL, decode_responses=True)

def get_cache(key: str) -> str | None:
    return redis_client.get(key)

def set_cache(key: str, value: str, expire: int = 3600):
    redis_client.set(key, value, ex=expire)