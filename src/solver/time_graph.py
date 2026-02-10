from src.solver.models import TimeNode, TimeEdge, CapacityTracker
from src.schemas.simulation_map import SimulationMap
from src.schemas.hubs import Hub
from src.schemas.definitions import ZoneType
from typing import Any


class TimeGraph:
    def __init__(self, turns: int) -> None:
        """
        Init for creation of Time Expanded Graph
        """
        self.adjacency: dict[TimeNode, list[TimeEdge]] = {}
        self.physical_trackers = {}
        self.turns: int = turns

    def _create_nodes(self, simulation_map: SimulationMap) -> None:
        """Gets all nodes from simulation map, creates
        their respective TimeNodes and stores them in a dictionary"""
        for i in range(self.turns + 1):
            for hub in simulation_map.hubs.values():
                if hub.zone != ZoneType.BLOCKED:
                    new_time_node = TimeNode(hub, i)
                    self.adjacency[new_time_node] = []

    def _get_physical_tracker(
        self, source_name: str, target_name: str, capacity: int
    ) -> CapacityTracker:
        """
        Helper to get/create a shared tracker for a physical connection.
        Uses sorted() so A->B and B->A share the same instance.
        """
        link_key = tuple(sorted((source_name, target_name)))

        if link_key not in self.physical_trackers:
            self.physical_trackers[link_key] = CapacityTracker(
                max_link_capacity=capacity, current_drones=0
            )

        return self.physical_trackers[link_key]

    def _create_edges(self, simulation_map: SimulationMap) -> None:
        """Creates all conections between TimeNodes"""
        for node in self.adjacency.keys():
            if node.time != self.turns:
                """Creation of the wait connection"""
                wait_target = TimeNode(node.hub, node.time + 1)

                if wait_target in self.adjacency:
                    wait_tracker = CapacityTracker(node.hub.max_drones, 0)
                    wait_edge = TimeEdge(node, wait_target, wait_tracker)
                    self.adjacency[node].append(wait_edge)

                neighbors = simulation_map.connections.get(node.hub.name, {})
                """Creation of the rest of connections"""
                for target_name, connection in neighbors.items():

                    arrival_time = node.time + connection.cost

                    if arrival_time > self.turns:
                        continue

                    target_hub = simulation_map.hubs[target_name]

                    target_time_node = TimeNode(target_hub, arrival_time)

                    if target_time_node in self.adjacency:

                        shared_tracker = self._get_physical_tracker(
                            node.hub.name,
                            target_hub.name,
                            connection.max_link_capacity,
                        )

                        move_edge = TimeEdge(
                            node, target_time_node, shared_tracker
                        )
                        self.adjacency[node].append(move_edge)

    def build(self, simulation_map: SimulationMap) -> None:
        """
        Main method to build the time expansion graph.
        """
        self._create_nodes(simulation_map)
        self._create_edges(simulation_map)