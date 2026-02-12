from __future__ import annotations
from collections import defaultdict
from src.schemas.hubs import Hub
from src.schemas.definitions import ZoneType, NodeCategory


class EdgeTracker:
    """Tracks edge usage across time for capacity management."""

    def __init__(self) -> None:
        self.edge_drones: dict[tuple[TimeEdge, int], int] = defaultdict(int)

    def get_current_drones(self, edge: TimeEdge, time: int) -> int:
        """Get current drone count on edge at specific time."""
        return self.edge_drones[(edge, time)]

    def add_drone(self, edge: TimeEdge, time: int) -> None:
        """Register a drone using the edge at specific time."""
        self.edge_drones[(edge, time)] += 1


class TimeNode:
    """
    Represents a specific physical Hub at a specific simulation time step.
    """

    def __init__(self, hub: Hub, time: int, initial_drones: int = 0) -> None:
        self.hub: Hub = hub
        self.time: int = time
        self.is_priority: bool = self.hub.zone == ZoneType.PRIORITY
        self.is_end: bool = hub.category == NodeCategory.END
        self.current_drones: int = initial_drones

    def can_enter(self) -> bool:
        """Check if a drone can enter this node."""
        return self.current_drones < self.hub.max_drones

    def add_drone(self) -> None:
        """Register a drone entering this node."""
        self.current_drones += 1

    def __eq__(self, other: object) -> bool:
        if isinstance(other, TimeNode):
            return self.hub.name == other.hub.name and self.time == other.time
        return False

    def __hash__(self) -> int:
        return hash((self.hub.name, self.time))

    def __repr__(self) -> str:
        return f"TimeNode({self.hub.name}, t={self.time})"


class TimeEdge:
    """
    Represents a directed edge between two
    TimeNodes in the Time-Expanded Graph.
    """

    def __init__(
        self, source: TimeNode, target: TimeNode, max_capacity: int = 1
    ) -> None:
        self.source = source
        self.target = target
        self.duration = target.time - source.time
        self.max_capacity = max_capacity

    def __hash__(self) -> int:
        return hash((self.source, self.target))

    def is_traversable(self, tracker: EdgeTracker) -> bool:
        """
        Checks if the edge has sufficient capacity
        for the entire duration of the traversal.
        """
        for turn in range(self.duration):
            current_drones = tracker.get_current_drones(
                self, self.source.time + turn
            )
            if current_drones >= self.max_capacity:
                return False
        return True

    def use_edge(self, tracker: EdgeTracker) -> None:
        """
        Registers the occupation of this edge for all turns of traversal.
        """
        for turn in range(self.duration):
            tracker.add_drone(self, self.source.time + turn)
