import uuid
import redis

def generate_client_id():
    return str(uuid.uuid4())


class RedisManager:
    redis_client = redis.StrictRedis(host="localhost", port=6379, db=0)
    
    @classmethod
    def save(cls, key, field, value):
        cls.redis_client.hset(key, field, value)

    @classmethod
    def get(cls, key, field):
        return cls.redis_client.hget(key, field)

    @classmethod
    def delete(cls, key, field):
        cls.redis_client.hdel(key, field)
