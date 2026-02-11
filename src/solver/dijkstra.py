from __future__ import annotations
import heapq
from typing import Dict, List, Optional, Tuple
from src.solver.models import TimeNode, TimeEdge
from src.solver.time_graph import TimeGraph
from src.schemas.definitions import NodeCategory, ZoneType


class DijkstraSolver:
    """
    Implements Dijkstra's algorithm on a Time-Expanded Graph.
    Finds the shortest path from a START node to any END node.
    """

    def __init__(self, time_graph: TimeGraph) -> None:
        self.time_graph = time_graph
        self.adjacency: Dict[TimeNode, List[TimeEdge]] = (
            self._build_adjacency()
        )

    def _build_adjacency(self) -> Dict[TimeNode, List[TimeEdge]]:
        """
        Builds an adjacency list from the TimeGraph edges.
        Maps each TimeNode to a list of outgoing TimeEdges.
        """
        adjacency: Dict[TimeNode, List[TimeEdge]] = {
            node: [] for node in self.time_graph.nodes.values()
        }

        for edge in self.time_graph.edges:
            if edge.source in adjacency:
                adjacency[edge.source].append(edge)

        return adjacency

    def find_start_nodes(self) -> List[TimeNode]:
        """
        Returns all TimeNodes at time=0 that are START hubs.
        """
        return [
            node
            for node in self.time_graph.nodes.values()
            if node.time == 0 and node.hub.category == NodeCategory.START
        ]

    def find_end_nodes(self) -> List[TimeNode]:
        """
        Returns all TimeNodes that are END hubs (any time).
        """
        return [
            node
            for node in self.time_graph.nodes.values()
            if node.hub.category == NodeCategory.END
        ]

    def solve(
        self, start_node: TimeNode
    ) -> Optional[Tuple[List[TimeNode], int]]:
        """
        Finds the shortest path from start_node to any END node.
        If multiple paths have the same cost, prefers paths with more PRIORITY hubs.
        """
        start_priority = 1 if start_node.hub.zone == ZoneType.PRIORITY else 0

        best: Dict[TimeNode, Tuple[int, int]] = {
            start_node: (0, start_priority)
        }

        parents: Dict[TimeNode, Optional[TimeNode]] = {start_node: None}

        pq: List[Tuple[int, int, int, TimeNode]] = [
            (0, -start_priority, id(start_node), start_node)
        ]

        visited: set[TimeNode] = set()

        while pq:
            current_dist, neg_priority_count, _, current_node = heapq.heappop(
                pq
            )
            current_priority = -neg_priority_count

            if current_node in visited:
                continue
            visited.add(current_node)

            if current_node.hub.category == NodeCategory.END:
                path = self._reconstruct_path(parents, current_node)
                return (path, current_dist)

            for edge in self.adjacency.get(current_node, []):
                neighbor = edge.target

                if neighbor in visited:
                    continue

                edge_cost = edge.duration
                new_dist = current_dist + edge_cost

                neighbor_priority = (
                    1 if neighbor.hub.zone == ZoneType.PRIORITY else 0
                )
                new_priority_count = current_priority + neighbor_priority

                current_best = best.get(neighbor)

                should_update = (
                    current_best is None
                    or new_dist < current_best[0]
                    or (
                        new_dist == current_best[0]
                        and new_priority_count > current_best[1]
                    )
                )

                if should_update:
                    best[neighbor] = (new_dist, new_priority_count)
                    parents[neighbor] = current_node
                    heapq.heappush(
                        pq,
                        (
                            new_dist,
                            -new_priority_count,
                            id(neighbor),
                            neighbor,
                        ),
                    )

        return None

    def _reconstruct_path(
        self, parents: Dict[TimeNode, Optional[TimeNode]], end_node: TimeNode
    ) -> List[TimeNode]:
        """
        Reconstructs the path from start to end using the parent dictionary.
        """
        path = []
        current: Optional[TimeNode] = end_node

        while current is not None:
            path.append(current)
            current = parents.get(current)

        path.reverse()
        return path

    def solve_all_starts(self) -> List[Tuple[TimeNode, List[TimeNode], int]]:
        """
        Finds shortest paths from all START nodes to any END node.
        """
        results = []
        start_nodes = self.find_start_nodes()

        for start in start_nodes:
            result = self.solve(start)
            if result:
                path, cost = result
                results.append((start, path, cost))

        return results
