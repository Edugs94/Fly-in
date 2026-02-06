from abc import ABC, abstractmethod
from typing import Any
from src.schemas.simulation_map import SimulationMap


class LineProcessor(ABC):
    """Parent class for implementing abstract methods"""

    def _validate_name(self, data: list[str]) -> None:
        if not data:
            raise ValueError("Invalid Map Entinty empty name")
        if " " in data[0] or "-" in data[0]:
            raise ValueError(f"Invalid name '{data[0]} cannot contain "
                             "spaces or dashes")

    @abstractmethod
    def _do_process(self, data: list[str], current_map: SimulationMap) -> Any:
        """
        Subclasses implement this method instead of 'process'
        """
        pass

    def process(self, data: list[str], current_map: SimulationMap) -> Any:
        """
        Template method: Orchestrates validation and processing.
        This is not overridden in subclasses.
        """
        self._validate_name(data)
        self._do_process(data, current_map)
