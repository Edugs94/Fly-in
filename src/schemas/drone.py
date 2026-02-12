from typing import List, Tuple


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
        self.x: int = start_x
        self.y: int = start_y
        self.path: List[Tuple[int, int, int]] = path

    def get_position_at_turn(self, turn: int) -> Tuple[int, int]:
        """Returns the drone position at a specific turn."""
        for t, x, y in self.path:
            if t == turn:
                return (x, y)
            if t > turn:
                break
        return (self.x, self.y)

    def update_position(self, turn: int) -> None:
        """Updates drone position based on current turn."""
        self.x, self.y = self.get_position_at_turn(turn)

    def __repr__(self) -> str:
        return f"Drone(id={self.id}, pos=({self.x}, {self.y}))"
