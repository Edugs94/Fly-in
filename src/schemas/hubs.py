from pydantic import Field
from src.schemas.base import MapEntity
from src.schemas.definitions import ZoneType


class Hub(MapEntity):
    x: int = Field(ge=0)
    y: int = Field(ge=0)
    max_drones: int = Field(ge=1, default=1)
    zone: ZoneType = Field(default=ZoneType.NORMAL)
    color: str | None = Field(default=None)
