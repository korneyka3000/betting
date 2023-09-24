from typing import Annotated, Tuple

import aiohttp
from fastapi import Body, HTTPException

from utils.config import get_settings
from utils.redis_client import redis_client
from utils.schemas.bets import BetIn
from utils.schemas.events import Event

settings = get_settings()


async def init_cache_data() -> None:
    async with redis_client.ctx_conn() as r:
        if not await r.exists("bets"):
            await r.json().set("bets", ".", {})


async def http_get(url) -> dict | list[dict]:
    async with aiohttp.ClientSession(
            base_url=f"http://{settings.LP_SERVICE_NAME}:80",
    ) as session:
        async with session.get(url) as r:
            if r.status == 200:
                return await r.json()
            raise HTTPException(status_code=r.status)


async def check_bet_in(data: Annotated[BetIn, Body()]) -> Tuple[Event, BetIn]:
    try:
        event: dict = await http_get(f"/api/events/{data.event_id}")
    except HTTPException as exc:
        raise HTTPException(
            status_code=404,
            detail=f"No such event with id: {data.event_id}",
        ) from exc
    else:
        return Event(**event), data
