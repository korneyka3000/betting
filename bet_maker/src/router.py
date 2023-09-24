from time import time
from typing import Annotated, Tuple

from fastapi import (
    APIRouter,
    Body,
    Depends,
    HTTPException,
    Response,
    status,
)
from redis.asyncio import Redis

from utils.redis_client import conn_cache
from utils.schemas.base import UpdateEventStatus
from utils.schemas.bets import (
    AggregateBets,
    BetDB,
    BetIn,
    BetsOut,
)
from utils.schemas.events import Event, EventOut

from .service import check_bet_in, http_get

router = APIRouter(
    tags=["Bets"],
)


@router.get(
    "/events",
    response_model=list[EventOut],
)
async def get_current_active_events():
    return await http_get("/api/events?is_active=true")


@router.post(
    "/bet",
    status_code=201,
    response_model=BetDB,
)
async def create_bet(
        r: Annotated[Redis, Depends(conn_cache)],
        data: Annotated[Tuple[Event, BetIn], Depends(check_bet_in)],
):
    event, bet = data
    if event.deadline < time():
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail="Event is out of time",
        )
    dict_data = bet.model_dump()
    dict_data.update({"event_id": event.id, "status": event.status})
    to_redis = BetDB(**dict_data)

    is_bet_key_exists = await r.json().get("bets", f"$.event:{event.id}")

    if not is_bet_key_exists:
        await r.json().set("bets", f".event:{event.id}", [])
    await r.json().arrappend("bets", f".event:{event.id}", to_redis.model_dump(mode='json'))

    return to_redis


@router.get(
    "/bets",
    response_model=list[BetsOut],
)
async def get_all_bets(
        r: Annotated[Redis, Depends(conn_cache)],
):
    data = await r.json().get('bets', '.')
    data = AggregateBets(bet=data)
    return data.total


@router.patch(
    "/{event_id}/status",
)
async def change_status(
        r: Annotated[Redis, Depends(conn_cache)],
        event_id: str,
        new_status: Annotated[UpdateEventStatus, Body()],
        response: Response,
):
    is_exists = await r.json().get("bets", f"$.event:{event_id}")
    if is_exists:
        key = f"event:{event_id}..status"
        async with r.pipeline() as pipe:
            await pipe.json().set("bets", f"$.{key}", new_status.value)
            await pipe.execute()
        return {"event_id": event_id, "status": new_status.value.name}
    response.status_code = status.HTTP_406_NOT_ACCEPTABLE
    return {f"No bets for event: {event_id}"}
