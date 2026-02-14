from typing import List, Tuple, Optional


class Drone:
    """Drone entity for simulation visualization."""

    def __init__(
        self,
        drone_id: int,
        start_x: int,
        start_y: int,
        path: List[Tuple[int, int, int]],
    ) -> None:
        """Initialize a Drone."""
        self.id: int = drone_id
        self.x: float = float(start_x)
        self.y: float = float(start_y)
        self.path: List[Tuple[int, int, int]] = path
        self.delivered: bool = False
        self.in_flight_connection: Optional[str] = None

    def get_position_at_turn(self, turn: int) -> Tuple[float, float]:
        """
        Returns the drone position at a specific turn.
        If in-flight (between hubs), returns the midpoint.
        If turn is past the last position, returns the final position.
        """
        if not self.path:
            return (self.x, self.y)

        last_t, last_x, last_y = self.path[-1]
        if turn >= last_t:
            return (float(last_x), float(last_y))

        prev_pos: Optional[Tuple[int, int, int]] = None

        for t, x, y in self.path:
            if t == turn:
                return (float(x), float(y))
            if t > turn:
                if prev_pos is not None:
                    mid_x = (prev_pos[1] + x) / 2.0
                    mid_y = (prev_pos[2] + y) / 2.0
                    return (mid_x, mid_y)
                break
            prev_pos = (t, x, y)

        return (self.x, self.y)

    def update_position(self, turn: int) -> None:
        """Updates drone position based on current turn."""
        self.x, self.y = self.get_position_at_turn(turn)

    def is_in_flight(self, turn: int) -> bool:
        """Check if drone is in-flight (between two hubs) at given turn."""
        for i, (t, _, _) in enumerate(self.path):
            if t == turn:
                return False
            if t > turn:
                return i > 0  # In-flight if we have a previous position
        return False

    def get_movement_info(self, turn: int) -> Optional[str]:
        """
        Returns movement string for this turn.
        Format: D{id}-{destination} or D{id}-{connection} for restricted.
        Returns None if no movement this turn.
        """
        if self.delivered:
            return None

        if self.in_flight_connection:
            return f"D{self.id}-{self.in_flight_connection}"

        return None

    def __repr__(self) -> str:
        return f"Drone(id={self.id}, pos=({self.x}, {self.y}))"
