import os
import math
from typing import Tuple
from src.schemas.simulation_map import SimulationMap

os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "hide"
import pygame  # noqa


class CoordTransformer:
    def __init__(self) -> None:
        self.ratio: float = 0.0
        self.x_corrector: float = 0.0
        self.y_corrector: float = 0.0
        self.x_offset: float = 0.0
        self.y_offset: float = 0.0

    def define_limits(
        self,
        simulation: SimulationMap,
        width: int,
        height: int,
        padding: int = 100,
    ) -> None:
        max_x = float("-inf")
        max_y = float("-inf")
        min_x = float("inf")
        min_y = float("inf")

        for hub in simulation.hubs.values():
            if hub.x > max_x:
                max_x = hub.x
            if hub.y > max_y:
                max_y = hub.y
            if hub.x < min_x:
                min_x = hub.x
            if hub.y < min_y:
                min_y = hub.y

        self.x_corrector = min_x
        self.y_corrector = max_y

        map_width = max_x - min_x
        map_height = max_y - min_y

        available_width = width - (padding * 2)
        available_height = height - (padding * 4)

        ratio_x = (
            available_width / map_width if map_width > 0 else float("inf")
        )
        ratio_y = (
            available_height / map_height if map_height > 0 else float("inf")
        )

        self.ratio = min(ratio_x, ratio_y)

        if self.ratio == float("inf"):
            self.ratio = 1.0

        self.x_offset = (
            padding + (available_width - map_width * self.ratio) / 2
        )
        self.y_offset = (
            padding * 2 + (available_height - map_height * self.ratio) / 2
        )

    def transform(
        self, coordinate_x: int | float, coordinate_y: int | float
    ) -> Tuple[float, float]:
        x = (coordinate_x - self.x_corrector) * self.ratio + self.x_offset
        y = (self.y_corrector - coordinate_y) * self.ratio + self.y_offset
        return x, y

    def calculate_radius(self, simulation: SimulationMap) -> int:
        hubs = list(simulation.hubs.values())

        min_dist = float("inf")
        for i in range(len(hubs)):
            for j in range(i + 1, len(hubs)):
                dist = math.hypot(hubs[i].x - hubs[j].x, hubs[i].y - hubs[j].y)
                if dist < min_dist:
                    min_dist = dist

        dist_in_pixels = min_dist * self.ratio
        return int(max(5, min(dist_in_pixels * 0.3, 200)))
