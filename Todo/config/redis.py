import os
import redis
from .settings import REDIS_HOST, REDIS_PORT

REDIS_CLIENT = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    db=0,
    decode_responses=True,
)
