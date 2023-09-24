from contextlib import asynccontextmanager
from typing import AsyncIterator

from redis.asyncio import Redis

from .config import Settings, get_settings


class Cache:
    def __init__(
            self,
            settings: Settings,
    ) -> None:
        self.settings = settings
        self.url = f"{settings.REDIS_URL}?decode_responses=True"
        self.engine = Redis.from_url(self.url)
        self.ctx_conn = asynccontextmanager(self.get_conn)

    async def get_conn(self) -> AsyncIterator[Redis]:
        async with self.engine.client() as conn:
            yield conn


redis_client = Cache(get_settings())


async def conn_cache() -> AsyncIterator[Redis]:
    async with redis_client.ctx_conn() as conn:
        yield conn
