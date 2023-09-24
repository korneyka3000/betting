from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Body, Depends

from utils.schemas.base import UpdateEventStatus
from utils.schemas.events import Event, EventStatus

from .service import (
    create_event,
    filter_actual,
    get_one,
    notify_bets,
)

router = APIRouter(
    prefix="/api/events",
    tags=["Events"],
)


@router.get(
    "",
    response_model=list[Event],
)
async def get_all_events(
        events: Annotated[list[Event], Depends(filter_actual)],
):
    return events


@router.get(
    "/{event_id}",
    response_model=Event,
)
async def get_event_by_id(
        event: Annotated[Event, Depends(get_one)],
):
    return event


@router.post(
    "",
    status_code=201,
    response_model=Event,
    description=f"AVAILABLE STATUSES: {EventStatus.display_options} | DEADLINE - time to add to current time (int)",
)
async def create_event(
        event: Annotated[Event, Depends(create_event)],
):
    return event


@router.patch(
    "/{event_id}",
    response_model=Event,
)
async def update_event_status(
        event: Annotated[Event, Depends(get_one)],
        status: Annotated[UpdateEventStatus, Body()],
        background_task: BackgroundTasks,
):
    event.status = status.value
    background_task.add_task(notify_bets, event)
    return event
