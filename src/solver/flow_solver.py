from __future__ import annotations
import heapq
from collections import defaultdict
from typing import Dict, List, Optional, Tuple
from src.solver.models import TimeNode, TimeEdge
from src.solver.time_graph import TimeGraph
from src.schemas.definitions import NodeCategory, ZoneType


class CapacityTracker:
    """
    Tracks edge and node usage across all drones to enforce capacity constraints.
    """

    def __init__(self) -> None:
        self.edge_usage: Dict[Tuple[str, str, int], int] = defaultdict(int)
        self.node_usage: Dict[Tuple[str, int], int] = defaultdict(int)

    def can_use_edge(self, edge: TimeEdge) -> bool:
        """Check if an edge has available capacity."""
        key = (edge.source.hub.name, edge.target.hub.name, edge.source.time)
        return self.edge_usage[key] < edge.max_capacity

    def can_use_node(self, node: TimeNode) -> bool:
        """Check if a node has available capacity."""
        key = (node.hub.name, node.time)
        return self.node_usage[key] < node.hub.max_drones

    def use_edge(self, edge: TimeEdge) -> None:
        """Mark an edge as used."""
        key = (edge.source.hub.name, edge.target.hub.name, edge.source.time)
        self.edge_usage[key] += 1

    def use_node(self, node: TimeNode) -> None:
        """Mark a node as used."""
        key = (node.hub.name, node.time)
        self.node_usage[key] += 1

    def reserve_path(self, path: List[TimeNode], edges: List[TimeEdge]) -> None:
        """Reserve all nodes and edges in a path (except start node at t=0)."""
        for node in path:
            if node.hub.category == NodeCategory.START and node.time == 0:
                continue
            self.use_node(node)
        for edge in edges:
            self.use_edge(edge)


class FlowSolver:
    """
    Solves the multi-drone routing problem using Dijkstra with capacity constraints.
    """

    def __init__(self, time_graph: TimeGraph, nb_drones: int) -> None:
        self.time_graph = time_graph
        self.nb_drones = nb_drones
        self.capacity_tracker = CapacityTracker()
        self.adjacency: Dict[TimeNode, List[TimeEdge]] = self._build_adjacency()
        self.drone_paths: Dict[int, List[TimeNode]] = {}

    def _build_adjacency(self) -> Dict[TimeNode, List[TimeEdge]]:
        """Builds an adjacency list from the TimeGraph edges."""
        adjacency: Dict[TimeNode, List[TimeEdge]] = {
            node: [] for node in self.time_graph.nodes.values()
        }
        for edge in self.time_graph.edges:
            if edge.source in adjacency:
                adjacency[edge.source].append(edge)
        return adjacency

    def _get_edge(self, source: TimeNode, target: TimeNode) -> Optional[TimeEdge]:
        """Get the edge between two nodes."""
        for edge in self.adjacency.get(source, []):
            if edge.target == target:
                return edge
        return None

    def find_start_nodes(self) -> List[TimeNode]:
        """Returns all TimeNodes at time=0 that are START hubs."""
        return [
            node for node in self.time_graph.nodes.values()
            if node.time == 0 and node.hub.category == NodeCategory.START
        ]

    def solve_for_drone(self, drone_id: int, start_node: TimeNode) -> Optional[List[TimeNode]]:
        """
        Finds the shortest path for a drone respecting current capacity constraints.
        """
        start_priority = 1 if start_node.hub.zone == ZoneType.PRIORITY else 0

        best: Dict[TimeNode, Tuple[int, int]] = {start_node: (0, start_priority)}
        parents: Dict[TimeNode, Optional[TimeNode]] = {start_node: None}
        pq: List[Tuple[int, int, int, TimeNode]] = [
            (0, -start_priority, id(start_node), start_node)
        ]
        visited: set[TimeNode] = set()

        while pq:
            current_dist, neg_priority_count, _, current_node = heapq.heappop(pq)
            current_priority = -neg_priority_count

            if current_node in visited:
                continue
            visited.add(current_node)

            if current_node.hub.category == NodeCategory.END:
                path = self._reconstruct_path(parents, current_node)
                return path

            for edge in self.adjacency.get(current_node, []):
                neighbor = edge.target

                if neighbor in visited:
                    continue

                if not self.capacity_tracker.can_use_edge(edge):
                    continue
                is_start_node = (neighbor.hub.category == NodeCategory.START and neighbor.time == 0)
                if not is_start_node and not self.capacity_tracker.can_use_node(neighbor):
                    continue

                edge_cost = edge.duration
                new_dist = current_dist + edge_cost

                neighbor_priority = 1 if neighbor.hub.zone == ZoneType.PRIORITY else 0
                new_priority_count = current_priority + neighbor_priority

                current_best = best.get(neighbor)
                should_update = (
                    current_best is None or
                    new_dist < current_best[0] or
                    (new_dist == current_best[0] and new_priority_count > current_best[1])
                )

                if should_update:
                    best[neighbor] = (new_dist, new_priority_count)
                    parents[neighbor] = current_node
                    heapq.heappush(pq, (new_dist, -new_priority_count, id(neighbor), neighbor))

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

    def solve_all_drones(self) -> Dict[int, List[TimeNode]]:
        """
        Solves paths for all drones sequentially, respecting capacity constraints.
        """
        start_nodes = self.find_start_nodes()

        if not start_nodes:
            print("No START nodes found!")
            return {}

        start_node = start_nodes[0]

        for drone_id in range(1, self.nb_drones + 1):
            path = self.solve_for_drone(drone_id, start_node)

            if path:
                self.drone_paths[drone_id] = path
                edges = self._get_path_edges(path)
                self.capacity_tracker.reserve_path(path, edges)
            else:
                print(f"Drone {drone_id}: No valid path found!")

        return self.drone_paths

    def print_movements(self) -> None:
        """
        Prints the movement of each drone at each turn.
        """
        if not self.drone_paths:
            print("No paths computed. Run solve_all_drones() first.")
            return

        max_time = max(
            path[-1].time for path in self.drone_paths.values() if path
        )

        print("\n" + "=" * 60)
        print("DRONE MOVEMENTS")
        print("=" * 60)

        for t in range(max_time + 1):
            print(f"\n--- Turn {t} ---")
            movements = []

            for drone_id, path in sorted(self.drone_paths.items()):
                current_pos = None
                next_pos = None

                for i, node in enumerate(path):
                    if node.time == t:
                        current_pos = node
                        if i + 1 < len(path):
                            next_pos = path[i + 1]
                        break

                if current_pos:
                    if next_pos and next_pos.hub.name != current_pos.hub.name:
                        movements.append(
                            f"Drone {drone_id} moves from {current_pos.hub.name} to {next_pos.hub.name}"
                        )
                    elif next_pos and next_pos.hub.name == current_pos.hub.name:
                        movements.append(
                            f"Drone {drone_id} waits at {current_pos.hub.name}"
                        )
                    else:
                        movements.append(
                            f"Drone {drone_id} arrived at {current_pos.hub.name} (END)"
                        )

            for movement in movements:
                print(f"  {movement}")

    def print_summary(self) -> None:
        """Prints a summary of all drone paths."""
        print("\n" + "=" * 60)
        print("PATH SUMMARY")
        print("=" * 60)

        for drone_id, path in sorted(self.drone_paths.items()):
            path_str = " -> ".join(f"{n.hub.name}(t={n.time})" for n in path)
            total_time = path[-1].time if path else 0
            print(f"\nDrone {drone_id}:")
            print(f"  Path: {path_str}")
            print(f"  Total time: {total_time} turns")
