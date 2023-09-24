import random as r
from decimal import Decimal as Dec
from time import time

from pydantic import BaseModel, Field, field_validator
from pydantic.types import condecimal

from .base import EventStatus, ReverseStatus, UniqueID


def create_coefficient() -> Dec:
    random_float = round(r.uniform(0.01, 1), 2)
    return Dec(Dec(str(random_float)).quantize(Dec('1.00')) * r.randint(1, 5))


def create_deadline_time() -> int:
    return int(time()) + r.randint(100, 600)


def add_time_to_current_time(to_add: int) -> int:
    return int(time() + to_add)


class Event(UniqueID):
    coefficient: condecimal(decimal_places=2, gt=0) = Field(default_factory=create_coefficient)  # type: ignore
    deadline: int = Field(default_factory=create_deadline_time, gt=0)
    status: EventStatus


class EventOut(Event):
    status: ReverseStatus


class EventCreate(Event):
    coefficient: condecimal(decimal_places=2, gt=0)
    deadline: int = Field(gt=0, examples=["666"])

    @field_validator("deadline", mode="before")
    @classmethod
    def add_time(cls, v) -> int:
        return int(time()) + v


class EventsData(BaseModel):
    storage: dict[str, Event] = {}
