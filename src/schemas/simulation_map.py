from pydantic import BaseModel
from typing import Any


class SimulationMap(BaseModel):
    """Map class with map file settings"""

    nb_drones: int

    hubs: dict[str, Any]
    connections: dict[str, Any]
