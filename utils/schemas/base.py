import uuid
from enum import Enum
from functools import lru_cache
from typing import Annotated

from pydantic import (
    BaseModel,
    BeforeValidator,
    Field,
)


def uuid_to_str() -> str:
    return str(uuid.uuid4())


class UniqueID(BaseModel):
    id: str = Field(default_factory=uuid_to_str)


class EventStatus(int, Enum):
    IN_PROCESS = 1
    DONE_WIN_HOME_TEAM = 2
    DONE_LOSE_HOME_TEAM = 3

    @classmethod
    @property
    @lru_cache
    def display_options(cls) -> str:  # noqa
        return ', '.join([f"{member.name}: {member.value}" for member in cls])


class UpdateEventStatus(BaseModel):
    value: EventStatus


def int_to_str(v: int) -> str:
    return EventStatus(v).name


ReverseStatus = Annotated[str, BeforeValidator(int_to_str)]
