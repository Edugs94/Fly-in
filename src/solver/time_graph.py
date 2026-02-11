from __future__ import annotations
from typing import Dict, List, Tuple
from src.schemas.hubs import Hub
from src.schemas.simulation_map import SimulationMap
from src.schemas.definitions import ZoneType
from src.solver.models import TimeNode, TimeEdge


class TimeGraph:
    """
    Constructs and manages the Time-Expanded Graph by connecting nodes across time steps.
    """

    def __init__(self, max_time: int) -> None:
        self.max_time = max_time
        self.nodes: Dict[Tuple[str, int], TimeNode] = {}
        self.edges: List[TimeEdge] = []

    def _add_node(self, hub: Hub, turn: int) -> None:
        """
        Creates and stores a TimeNode if it does not already exist.
        """
        key = (hub.name, turn)
        if key not in self.nodes and hub.zone != ZoneType.BLOCKED:
            self.nodes[key] = TimeNode(hub, turn)

    def _add_edge(self, source: TimeNode, target: TimeNode, max_capacity: int = 1) -> None:
        """
        Creates a TimeEdge between two TimeNodes and stores it in the edge list.
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

    def build_graph(self, hubs: list[Hub], connections: dict) -> None:
        """
        Populates the graph while excluding hubs and connections marked as BLOCKED.
        RESTRICTED zones require 2 time steps to traverse.
        """
        valid_hubs = {
            hub.name: hub for hub in hubs
            if hub.zone != ZoneType.BLOCKED
        }

        for t in range(self.max_time + 1):
            for hub in valid_hubs.values():
                self._add_node(hub, t)

        for t in range(self.max_time):
            for source_name, targets in connections.items():
                for target_name, connection in targets.items():
                    if source_name not in valid_hubs or target_name not in valid_hubs:
                        continue

                    target_hub = valid_hubs[target_name]
                    travel_time = self._get_travel_time(target_hub)
                    arrival_time = t + travel_time

                    if arrival_time > self.max_time:
                        continue

                    source_node = self.nodes.get((source_name, t))
                    target_node = self.nodes.get((target_name, arrival_time))

                    if source_node and target_node:
                        self._add_edge(source_node, target_node, connection.max_link_capacity)

            for hub in valid_hubs.values():
                wait_source = self.nodes.get((hub.name, t))
                wait_target = self.nodes.get((hub.name, t + 1))

                if wait_source and wait_target:
                    self._add_edge(wait_source, wait_target)