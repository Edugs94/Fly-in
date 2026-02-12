from __future__ import annotations
from typing import Dict, List, Optional, Set
from src.schemas.hubs import Hub
from src.schemas.simulation_map import SimulationMap
from src.schemas.definitions import ZoneType
from src.solver.models import TimeNode, TimeEdge


class TimeGraph:
    """
    Constructs and manages the Time-Expanded Graph by
    connecting nodes across time steps.
    Builds itself automatically upon instantiation.
    """

    def __init__(self, simulation: SimulationMap, max_time: int) -> None:
        self.max_time = max_time
        self.nodes: Set[TimeNode] = set()
        self._node_lookup: Dict[tuple[str, int], TimeNode] = {}
        self.edges: List[TimeEdge] = []
        self.simulation: SimulationMap = simulation
        self.adjacency: Dict[TimeNode, List[TimeEdge]] = {}
        self._build_graph()

    def get_node(self, hub_name: str, time: int) -> Optional[TimeNode]:
        """Returns the TimeNode for a given hub name and time, or None."""
        return self._node_lookup.get((hub_name, time))

    def _add_node(self, hub: Hub, turn: int) -> None:
        """
        Creates and stores a TimeNode if it does not already exist.
        Drone counts are tracked via _reserve_path, not initialization.
        """
        key = (hub.name, turn)
        if key not in self._node_lookup and hub.zone != ZoneType.BLOCKED:
            node = TimeNode(hub, turn, 0)
            self.nodes.add(node)
            self._node_lookup[key] = node

    def _add_edge(
        self, source: TimeNode, target: TimeNode, max_capacity: int = 1
    ) -> None:
        """
        Creates a TimeEdge between two TimeNodes
        and stores it in the edge list.
        """
        new_edge = TimeEdge(source, target, max_capacity)
        self.edges.append(new_edge)

    def _get_travel_time(self, target_hub: Hub) -> int:
        """
        Returns the travel time to reach a hub based on its zone type.
        RESTRICTED zones take 2 turns, all others take 1 turn.
        """
        if target_hub.zone == ZoneType.RESTRICTED:
            return 2
        return 1

    def _build_graph(self) -> None:
        """
        Populates the graph while excluding hubs
        and connections marked as BLOCKED.
        RESTRICTED zones require 2 time steps to traverse.
        Also builds the adjacency dictionary.
        """
        hubs_dict = self.simulation.hubs
        connections = self.simulation.connections
        valid_hubs: Dict[str, Hub] = {
            name: hub for name, hub in hubs_dict.items()
            if hub.zone != ZoneType.BLOCKED
        }

        for t in range(self.max_time + 1):
            for hub in valid_hubs.values():
                self._add_node(hub, t)

        for t in range(self.max_time):
            for source_name, targets in connections.items():
                for target_name, connection in targets.items():
                    if (
                        source_name not in valid_hubs
                        or target_name not in valid_hubs
                    ):
                        continue

                    target_hub = valid_hubs[target_name]
                    travel_time = self._get_travel_time(target_hub)
                    arrival_time = t + travel_time

                    if arrival_time > self.max_time:
                        continue

                    source_node = self.get_node(source_name, t)
                    target_node = self.get_node(target_name, arrival_time)

                    if source_node and target_node:
                        self._add_edge(
                            source_node,
                            target_node,
                            connection.max_link_capacity,
                        )

            for hub in valid_hubs.values():
                wait_source = self.get_node(hub.name, t)
                wait_target = self.get_node(hub.name, t + 1)

                if wait_source and wait_target:
                    self._add_edge(
                        wait_source, wait_target, wait_source.hub.max_drones
                    )

        self._build_adjacency()

    def _build_adjacency(self) -> None:
        """Builds the adjacency dictionary from the graph edges."""
        self.adjacency = {node: [] for node in self.nodes}
        for edge in self.edges:
            if edge.source in self.adjacency:
                self.adjacency[edge.source].append(edge)
