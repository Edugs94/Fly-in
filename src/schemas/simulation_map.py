from pydantic import BaseModel
from typing import Any
from src.schemas.hubs import Hub


class SimulationMap(BaseModel):
    """Map class with map file settings"""

    nb_drones: int

    hubs: dict[str, Hub]
    connections: dict[str, Any]
