import asyncio
from time import time
from typing import Annotated

import aiohttp
from fastapi import HTTPException, Path, Query, status

from utils.config import get_settings
from utils.schemas.events import (
    Event,
    EventCreate,
    EventsData,
    EventStatus,
)

events = EventsData()
settings = get_settings()


async def init_events_data() -> None:
    for _ in range(20):
        event = Event(status=EventStatus.IN_PROCESS)
        to_storage: dict[str, Event] = {event.id: event}
        events.storage.update(to_storage)


async def filter_actual(is_active: Annotated[bool, Query()] = False) -> list[Event]:
    if is_active:
        result_list = []
        for _event_id, event in events.storage.items():
            if time() < event.deadline:
                result_list.append(event)
        return result_list
    return list(events.storage.values())


async def get_one(event_id: Annotated[str, Path()]) -> Event:
    if event_id in events.storage:
        return events.storage[event_id]
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="No Such Event",
    )


def create_event(event: EventCreate) -> Event:
    if event.id in events.storage:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Event with such id already exists",
        )
    data_to_add = {event.id: event}
    events.storage.update(data_to_add)
    return event


async def notify_bets(event: Event) -> None:
    async with aiohttp.ClientSession(f"http://{settings.BET_SERVICE_NAME}:80") as session:
        no_success = True
        counter = 0
        while no_success:
            url = f"/{event.id}/status"
            async with session.patch(url, json={"value": event.status.value}) as res:
                if res.status not in (200, 406):
                    # Сомнительная реализация, для того что если вдруг меняешь статус события
                    # и что-то пошло не так
                    if counter > 10:
                        break
                    await asyncio.sleep(10)
                else:
                    break
