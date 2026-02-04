from abc import ABC, abstractmethod
from typing import Any
from src.schemas.simulation_map import SimulationMap


class LineProcessor(ABC):
    """Parent class for implementing abstract methods"""

    @abstractmethod
    def process(self, data: list[str], current_map: SimulationMap) -> Any:
        pass
