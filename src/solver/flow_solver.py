from __future__ import annotations
import heapq
from typing import Dict, List, Optional, Tuple
from src.solver.models import TimeNode, TimeEdge, EdgeTracker
from src.solver.time_graph import TimeGraph
from src.schemas.definitions import NodeCategory, ZoneType


class FlowSolver:
    """
    Solves the multi-drone routing problem
    using Dijkstra with capacity constraints.
    Uses a pre-built TimeGraph with adjacency dictionary.
    """

    def __init__(self, time_graph: TimeGraph, nb_drones: int) -> None:
        self.time_graph = time_graph
        self.nb_drones = nb_drones
        self.tracker = EdgeTracker()
        self.drone_paths: Dict[int, List[TimeNode]] = {}

    def _get_edge(
        self, source: TimeNode, target: TimeNode
    ) -> Optional[TimeEdge]:
        """Get the edge between two nodes."""
        for edge in self.time_graph.adjacency.get(source, []):
            if edge.target == target:
                return edge
        return None

    def find_start_node(self) -> TimeNode:
        """Returns the TimeNode at time=0 that is the START hub."""
        for node in self.time_graph.nodes.values():
            if node.time == 0 and node.hub.category == NodeCategory.START:
                return node
        raise ValueError("No START node found at time=0")

    def solve_for_drone(
        self, drone_id: int, start_node: TimeNode
    ) -> Optional[List[TimeNode]]:
        """
        Finds the shortest path for a drone using modified Dijkstra.

        Uses tuple (turns, -priorities) for comparison:
        - Primary: minimize turns (time to reach destination)
        - Secondary: maximize priorities (prefer paths through priority zones)

        At equal turns, the path with more priority zones is selected.
        """
        start_priority = 1 if start_node.hub.zone == ZoneType.PRIORITY else 0

        best: Dict[TimeNode, Tuple[int, int]] = {
            start_node: (0, start_priority)
        }
        parents: Dict[TimeNode, Optional[TimeNode]] = {start_node: None}
        pq: List[Tuple[Tuple[int, int], int, TimeNode]] = [
            ((0, -start_priority), id(start_node), start_node)
        ]
        visited: set[TimeNode] = set()

        while pq:
            (current_dist, neg_priority), _, current_node = heapq.heappop(pq)
            current_priority = -neg_priority

            if current_node in visited:
                continue
            visited.add(current_node)

            if current_node.hub.category == NodeCategory.END:
                path = self._reconstruct_path(parents, current_node)
                return path

            for edge in self.time_graph.adjacency.get(current_node, []):
                neighbor = edge.target

                if neighbor in visited:
                    continue

                if not edge.is_traversable(self.tracker):
                    continue

                is_start_at_zero = (
                    neighbor.hub.category == NodeCategory.START
                    and neighbor.time == 0
                )
                if not is_start_at_zero and not neighbor.can_enter():
                    continue

                new_dist = current_dist + edge.duration
                neighbor_priority = (
                    1 if neighbor.hub.zone == ZoneType.PRIORITY else 0
                )
                new_priority = current_priority + neighbor_priority

                current_best = best.get(neighbor)
                new_cost = (new_dist, -new_priority)
                best_cost = (
                    (current_best[0], -current_best[1])
                    if current_best
                    else None
                )

                if best_cost is None or new_cost < best_cost:
                    best[neighbor] = (new_dist, new_priority)
                    parents[neighbor] = current_node
                    heapq.heappush(
                        pq,
                        (new_cost, id(neighbor), neighbor),
                    )

        return None

    def _reconstruct_path(
        self, parents: Dict[TimeNode, Optional[TimeNode]], end_node: TimeNode
    ) -> List[TimeNode]:
        """Reconstructs the path from start to end."""
        path = []
        current: Optional[TimeNode] = end_node
        while current is not None:
            path.append(current)
            current = parents.get(current)
        path.reverse()
        return path

    def _get_path_edges(self, path: List[TimeNode]) -> List[TimeEdge]:
        """Get all edges used in a path."""
        edges = []
        for i in range(len(path) - 1):
            edge = self._get_edge(path[i], path[i + 1])
            if edge:
                edges.append(edge)
        return edges

    def _reserve_path(self, path: List[TimeNode]) -> None:
        """Reserve all nodes and edges in a path."""
        edges = self._get_path_edges(path)

        for edge in edges:
            edge.use_edge(self.tracker)

        for node in path:
            node.add_drone()

    def solve_all_drones(self) -> Dict[int, List[TimeNode]]:
        """
        Solves paths for all drones sequentially,
        respecting capacity constraints.
        """
        start_node = self.find_start_node()

        for drone_id in range(1, self.nb_drones + 1):
            path = self.solve_for_drone(drone_id, start_node)

            if path:
                self.drone_paths[drone_id] = path
                self._reserve_path(path)
            else:
                print(f"Drone {drone_id}: No valid path found!")

        return self.drone_paths

    def _get_connection_name(self, source_name: str, target_name: str) -> str:
        """Returns the connection name in format source-target."""
        return f"{source_name}-{target_name}"

    def _is_in_flight_to_restricted(
        self, drone_id: int, current_time: int
    ) -> Optional[str]:
        """
        Check if drone is in flight toward a restricted zone.
        Returns connection name if in flight, None otherwise.
        """
        path = self.drone_paths.get(drone_id)
        if not path:
            return None

        for i, node in enumerate(path):
            if i + 1 < len(path):
                next_node = path[i + 1]
                if (
                    node.time < current_time
                    and next_node.time > current_time
                    and next_node.hub.zone == ZoneType.RESTRICTED
                ):
                    return self._get_connection_name(
                        node.hub.name, next_node.hub.name
                    )
        return None

    def get_simulation_output(self) -> List[str]:
        """
        Generates the simulation output in the required format.
        Returns a list of strings, one per turn.
        """
        if not self.drone_paths:
            return []

        output_lines: List[str] = []
        delivered: set[int] = set()

        max_time = max(
            path[-1].time for path in self.drone_paths.values() if path
        )

        for t in range(max_time):
            movements: List[str] = []

            for drone_id, path in sorted(self.drone_paths.items()):
                if drone_id in delivered:
                    continue

                current_node = None
                next_node = None

                for i, node in enumerate(path):
                    if node.time == t:
                        current_node = node
                        if i + 1 < len(path):
                            next_node = path[i + 1]
                        break

                if current_node is None:
                    in_flight = self._is_in_flight_to_restricted(drone_id, t)
                    if in_flight:
                        movements.append(f"D{drone_id}-{in_flight}")
                    continue

                if next_node and next_node.hub.name == current_node.hub.name:
                    continue

                if next_node:
                    destination = next_node.hub.name
                    if next_node.hub.zone == ZoneType.RESTRICTED:
                        connection = self._get_connection_name(
                            current_node.hub.name, next_node.hub.name
                        )
                        movements.append(f"D{drone_id}-{connection}")
                    else:
                        movements.append(f"D{drone_id}-{destination}")

                    if next_node.hub.category == NodeCategory.END:
                        delivered.add(drone_id)

            if movements:
                output_lines.append(" ".join(movements))

        return output_lines

    def print_simulation_output(self) -> None:
        """Prints the simulation output in the required format."""
        output = self.get_simulation_output()
        for line in output:
            print(line)
