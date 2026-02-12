from typing import Dict, List, Tuple
from src.schemas.drone import Drone
from src.solver.models import TimeNode


def create_drones_from_paths(
    drone_paths: Dict[int, List[TimeNode]],
) -> Dict[int, Drone]:
    """
    Creates Drone objects from solver paths.
    """
    drones: Dict[int, Drone] = {}

    for drone_id, path in drone_paths.items():
        if not path:
            continue

        start_node = path[0]
        start_x = start_node.hub.x
        start_y = start_node.hub.y

        positions: List[Tuple[int, int, int]] = []
        for node in path:
            positions.append((node.time, node.hub.x, node.hub.y))

        drones[drone_id] = Drone(
            drone_id=drone_id,
            start_x=start_x,
            start_y=start_y,
            path=positions,
        )

    return drones
