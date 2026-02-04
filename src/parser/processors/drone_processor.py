from src.parser.processors.base import LineProcessor
from src.schemas.simulation_map import SimulationMap


class DroneProcessor(LineProcessor):
    """Calculates the number of drones"""

    def process(self, data: list[str], current_map: SimulationMap) -> None:

        if len(data) != 1:
            raise ValueError("Incorrect number of drones")
        if int(data[0]) <= 0:
            raise ValueError("Number of drones must be greater than 0")
        if current_map.nb_drones != 0:
            raise ValueError("Number of drones defined more than 1 times")
        current_map.nb_drones = int(data[0])
