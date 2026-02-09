from pydantic import Field
from src.schemas.base import MapEntity


class Connection(MapEntity):
    """Class for links between Hubs"""

    source: str
    target: str
    max_link_capacity: int = Field(ge=1, default=1)
    current_drones: int = Field(ge=0, default=0)
    cost: int = Field(default=1)
