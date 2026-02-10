from __future__ import annotations
from src.schemas.hubs import Hub
from src.schemas.definitions import ZoneType


class TimeNode:
    """
    Represents a specific Hub at a specific simulation turn (t).
    """

    def __init__(self, hub: Hub, time: int):
        self.hub = hub
        self.time = time
        self.is_priority = (self.hub.zone == ZoneType.PRIORITY)

    def __eq__(self, other: object) -> bool:
        """
        Checks equality based on hub name and time.
        """
        if isinstance(other, TimeNode):
            return self.hub.name == other.hub.name and self.time == other.time
        return False

    def __hash__(self) -> int:
        """
        Generates a unique hash for using this object as a dictionary key.
        """
        return hash((self.hub.name, self.time))


class CapacityTracker:
    '''
    Tracker for capacity of each TimeEdge
    '''
    def __init__(self, max_link_capacity: int, current_drones: int) -> None:
        self.max_link_capacity = max_link_capacity
        self.current_drones = current_drones

    def add_flow(self, amount) -> bool:
        if self.max_link_capacity >= amount + self.current_drones:
            self.current_drones += amount
            return True
        else:
            return False


class TimeEdge:
    """
    Representation an Edge on the Time-Expanded Graph
    """

    def __init__(
        self, source: TimeNode, target: TimeNode, tracker: CapacityTracker
    ) -> None:
        """
        Docstring for __init__
        """
        self.source = source
        self.target = target
        self.tracker = tracker

    def add_drones(self, amount: int = 1) -> bool:
        """
        Adding drones to the Edge
        """
        return self.tracker.add_flow(amount)
