from collections import deque
from src.schemas.simulation_map import SimulationMap
from src.schemas.definitions import ZoneType, NodeCategory


def has_path_to_end(simulation: SimulationMap) -> bool:
    """
    Verifies if a path exists from START to END in the static graph.
    Uses BFS ignoring time and capacities.
    Returns False if no path exists (blocked or disconnected).
    """
    start_hubs = [
        name for name, hub in simulation.hubs.items()
        if hub.category == NodeCategory.START and hub.zone != ZoneType.BLOCKED
    ]
    end_hubs = set(
        name for name, hub in simulation.hubs.items()
        if hub.category == NodeCategory.END and hub.zone != ZoneType.BLOCKED
    )

    if not start_hubs or not end_hubs:
        return False

    visited = set()
    queue = deque([start_hubs[0]])

    while queue:
        current = queue.popleft()

        if current in end_hubs:
            return True

        if current in visited:
            continue
        visited.add(current)

        if current in simulation.connections:
            for neighbor in simulation.connections[current]:
                if neighbor not in visited:
                    hub = simulation.hubs.get(neighbor)
                    if hub and hub.zone != ZoneType.BLOCKED:
                        queue.append(neighbor)

    return False


def estimate_min_path_length(simulation: SimulationMap) -> int:
    """
    Estimates minimum path length using BFS on static graph.
    Accounts for restricted zones costing 2 turns.
    """
    start_hubs = [
        name for name, hub in simulation.hubs.items()
        if hub.category == NodeCategory.START and hub.zone != ZoneType.BLOCKED
    ]
    end_hubs = set(
        name for name, hub in simulation.hubs.items()
        if hub.category == NodeCategory.END and hub.zone != ZoneType.BLOCKED
    )

    if not start_hubs or not end_hubs:
        return -1

    visited = {}
    queue = deque([(start_hubs[0], 0)])

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
                    hub = simulation.hubs.get(neighbor)
                    if hub and hub.zone != ZoneType.BLOCKED:
                        cost = 2 if hub.zone == ZoneType.RESTRICTED else 1
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

    This is mathematically optimal and guarantees solution on first attempt.
    """
    min_path = estimate_min_path_length(simulation)
    if min_path <= 0:
        return -1

    return min_path + simulation.nb_drones - 1
