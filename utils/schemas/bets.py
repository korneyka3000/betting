from uuid import UUID

from pydantic import (
    BaseModel,
    ConfigDict,
    computed_field,
    condecimal,
)

from .base import (
    EventStatus,
    ReverseStatus,
    UniqueID,
)


class BetBasic(BaseModel):
    amount: condecimal(decimal_places=2, gt=0)


class BetIn(BetBasic):
    model_config = ConfigDict(extra="ignore", from_attributes=True)

    event_id: UUID


class BetDB(BetIn, UniqueID):
    status: EventStatus


class BetsOut(BetDB):
    status: ReverseStatus


class AggregateBets(BaseModel):
    model_config = ConfigDict(extra="allow")

    bet: dict[str, list[BetsOut]]

    @computed_field
    @property
    def total(self) -> list[BetsOut]:
        res = []
        for bet in self.bet.values():
            res.extend(bet)
        return res
