from __future__ import annotations
from src.schemas.hubs import Hub
from src.schemas.definitions import ZoneType, NodeCategory


class EdgeTracker:
    def __init__(self) -> None:
        self.edge_tracker: dict[tuple[TimeEdge, int], int] = {}

class TimeNode:
    """
    Represents a specific physical Hub at a specific simulation time step.
    """

    def __init__(self, hub: Hub, time: int) -> None:
        self.hub: Hub = hub
        self.time: int = time
        self.is_priority: bool = self.hub.zone == ZoneType.PRIORITY
        self.is_end: bool = hub.category == NodeCategory.END

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
    Represents a directed edge between two TimeNodes in the Time-Expanded Graph.
    """

    def __init__(self, source: TimeNode, target: TimeNode, max_capacity: int = 1) -> None:
        self.source = source
        self.target = target
        self.duration = target.time - source.time
        self.max_capacity = max_capacity

    def __hash__(self) -> int:
        return hash((self.source , self.target))

    def use_edge(self, tracker: EdgeTracker) -> None:
        """
        Registers the occupation of this edge.
        """
        for turn in range(self.duration):
            tracker.edge_tracker[(self, self.source.time + turn)] += 1

    def is_traversable(self, tracker: EdgeTracker) -> bool:
        """
        Checks if the physical edge has sufficient capacity for the entire duration of the traversal.
        """
        for turn in range(self.duration):
            current_occupation = tracker.edge_tracker.get((self, self.source.time + turn), 0)
            if current_occupation >= self.max_capacity:
                return False
        return True
