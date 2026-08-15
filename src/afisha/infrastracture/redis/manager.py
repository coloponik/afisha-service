from redis.asyncio import Redis

from afisha.core.config import RedisConfig


class RedisClient:
    def __init__(self, redis: Redis) -> None:
        self.client = redis

    async def close(self) -> None:
        await self.client.close()


def create_redis_client(config: RedisConfig) -> RedisClient:
    redis = Redis.from_url(
        config.url,
        decode_responses=True
    )

    return RedisClient(redis)
