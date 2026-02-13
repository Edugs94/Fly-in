import os
import math
import sys
from src.parser.file_parser import FileParser
from src.schemas.simulation_map import SimulationMap
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame


class CoordTransformer:
    def __init__(self) -> None:
        self.ratio = 0
        self.x_corrector = 0
        self.y_corrector = 0
        self.x_offset = 0
        self.y_offset = 0

    def define_limits(self, simulation: SimulationMap, width: int, height: int, padding: int = 100):
        max_x = float('-inf')
        max_y = float('-inf')
        min_x = float('inf')
        min_y = float('inf')

        for hub in simulation.hubs.values():
            if hub.x > max_x: max_x = hub.x
            if hub.y > max_y: max_y = hub.y
            if hub.x < min_x: min_x = hub.x
            if hub.y < min_y: min_y = hub.y

        self.x_corrector = min_x
        self.y_corrector = max_y

        map_width = max_x - min_x
        map_height = max_y - min_y

        available_width = width - (padding * 2)
        available_height = height - (padding * 2)

        ratio_x = available_width / map_width if map_width > 0 else float('inf')
        ratio_y = available_height / map_height if map_height > 0 else float('inf')

        self.ratio = min(ratio_x, ratio_y)

        if self.ratio == float('inf'):
            self.ratio = 1.0

        final_graph_width = map_width * self.ratio
        final_graph_height = map_height * self.ratio

        self.x_offset = (width - final_graph_width) / 2
        self.y_offset = (height - final_graph_height) / 2

    def transform(self, coordinate_x: int | float, coordinate_y: int | float):
        x = (coordinate_x - self.x_corrector) * self.ratio + self.x_offset
        y = (self.y_corrector - coordinate_y) * self.ratio + self.y_offset
        return x, y

    def calculate_radius(self, simulation: SimulationMap) -> int:
        hubs = list(simulation.hubs.values())
        if len(hubs) < 2: return 30

        min_dist = float('inf')
        for i in range(len(hubs)):
            for j in range(i + 1, len(hubs)):
                dist = math.hypot(hubs[i].x - hubs[j].x, hubs[i].y - hubs[j].y)
                if dist < min_dist: min_dist = dist

        dist_in_pixels = min_dist * self.ratio
        return int(max(5, min(dist_in_pixels * 0.3, 200)))


def get_colored_surface(surface: pygame.Surface, color: tuple) -> pygame.Surface:
    """
    Colors a white image
    """
    colored_surface = surface.copy()

    colored_surface.fill(color, special_flags=pygame.BLEND_RGBA_MULT)

    return colored_surface



def main():
    map_file = sys.argv[1]
    parser = FileParser()
    simulation: SimulationMap = parser.parse(map_file)

    pygame.init()

    width = 1800
    height = 1350
    transformer = CoordTransformer()
    transformer.define_limits(simulation, width, height)
    radius = transformer.calculate_radius(simulation)

    window = pygame.display.set_mode((width, height))


    background_file = "assets/dark_space.jpg"
    raw_image = pygame.image.load(background_file).convert()
    background = pygame.transform.scale(raw_image, (width, height))

    drone_file = "assets/drone.png"
    drone_raw = pygame.image.load(drone_file).convert_alpha()
    drone_original = pygame.transform.scale(drone_raw, (60, 60))

    hub_file = "assets/Retina/star_large.png"
    hub_raw = pygame.image.load(hub_file).convert_alpha()
    diameter = int(radius * 2)
    hub_original = pygame.transform.scale(hub_raw, (diameter, diameter))

    pos_x = width / 2
    pos_y = height / 2
    angle = 0

    running = True
    clock = pygame.time.Clock()

    color_map = {
        "red": (255, 50, 50),
        "green": (50, 255, 50),
        "blue": (50, 50, 255),
        "yellow": (255, 255, 0),
        "white": (255, 255, 255)
    }

    hub_sprites = {}

    for color_name, rgb_value in color_map.items():
        hub_sprites[color_name] = get_colored_surface(hub_original, rgb_value)

    while running:

        window.blit(background, (0, 0))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        for hub in simulation.hubs.values():
            x, y = transformer.transform(hub.x, hub.y)

            c_name = getattr(hub, 'color', 'white')
            sprite = hub_sprites.get(c_name, hub_sprites['white'])

            rect = sprite.get_rect(center=(x, y))
            window.blit(sprite, rect)


        angle += 1
        rotated_drone = pygame.transform.rotate(drone_original, angle)
        drone_rect = rotated_drone.get_rect(center=(pos_x, pos_y))


        # window.blit(rotated_drone, drone_rect)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()