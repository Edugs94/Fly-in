from collections import deque
from typing import Optional
from src.schemas.simulation_map import SimulationMap
from src.schemas.definitions import ZoneType, NodeCategory


def estimate_min_path_length(simulation: SimulationMap) -> int:
    """
    Estimates minimum path length using BFS on static graph.
    Accounts for restricted zones costing 2 turns.
    Returns -1 if no path available
    """
    start_hub: Optional[str] = None
    for hub in simulation.hubs.values():
        if hub.category == NodeCategory.START:
            start_hub = hub.name

    if start_hub is None:
        return -1

    end_hubs = set(
        name
        for name, hub in simulation.hubs.items()
        if hub.category == NodeCategory.END
    )

    visited: dict[str, int] = {}
    queue = deque([(start_hub, 0)])

    while queue:
        current, cost_accumulated = queue.popleft()

        if current in end_hubs:
            return cost_accumulated

        if current in visited:
            continue

        visited[current] = cost_accumulated

        if current in simulation.connections:
            for neighbor in simulation.connections[current]:
                if neighbor not in visited:
                    hub_obj = simulation.hubs.get(neighbor)
                    if (
                        hub_obj is not None
                        and hub_obj.zone != ZoneType.BLOCKED
                    ):
                        cost = 2 if hub_obj.zone == ZoneType.RESTRICTED else 1
                        queue.append((neighbor, cost_accumulated + cost))

    return -1


def estimate_max_time(simulation: SimulationMap) -> int:
    """
    Estimates time needed for all drones to reach END.

    Formula: min_path_length + (nb_drones - 1)

    Reasoning:
    - In worst case (bottleneck with capacity=1), drones go one by one
    - Drone 1 arrives at: min_path
    - Drone 2 arrives at: min_path + 1
    - Drone N arrives at: min_path + (N-1)

    This guarantees solution on first attempt.
    """
    min_path = estimate_min_path_length(simulation)
    if min_path <= 0:
        return -1

    return min_path + simulation.nb_drones - 1
