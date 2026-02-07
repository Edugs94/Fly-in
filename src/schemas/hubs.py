from pydantic import Field
from src.schemas.base import MapEntity
from src.schemas.definitions import ZoneType, NodeCategory


class Hub(MapEntity):
    """Hub Class Validation"""

    category: NodeCategory
    type: ZoneType
    x: int
    y: int
    max_drones: int = Field(ge=1, default=1)
    current_drones: int = Field(ge=0, default=0)
    zone: ZoneType = Field(default=ZoneType.NORMAL)
    color: str | None = Field(default=None)
