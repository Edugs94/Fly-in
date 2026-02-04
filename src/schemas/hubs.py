from pydantic import Field, field_validator
from src.schemas.base import MapEntity
from src.schemas.definitions import ZoneType


class Hub(MapEntity):
    """Hub Class Validation"""

    x: int
    y: int
    max_drones: int = Field(ge=1, default=1)
    zone: ZoneType = Field(default=ZoneType.NORMAL)
    color: str | None = Field(default=None)

    @field_validator('name')
    @classmethod
    def _validate_name(cls, v: str) -> str:
        if '-' in v:
            raise ValueError(f"Invalid hub name '{v}': cannot contain dashes")
        return v


class StartHub(Hub):
    '''Class for starting point'''
    pass


class EndHub(Hub):
    '''Class for ending point'''
    pass
