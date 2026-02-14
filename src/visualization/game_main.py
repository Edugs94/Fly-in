import os
import math
import sys
from src.parser.file_parser import FileParser
from src.schemas.simulation_map import SimulationMap
from src.visualization.assets_manager import AssetsManager
from src.schemas.definitions import ZoneType

os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "hide"
import pygame  # noqa


class CoordTransformer:
    def __init__(self) -> None:
        self.ratio = 0
        self.x_corrector = 0
        self.y_corrector = 0
        self.x_offset = 0
        self.y_offset = 0

    def define_limits(
        self,
        simulation: SimulationMap,
        width: int,
        height: int,
        padding: int = 100,
    ):
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
        available_height = height - (padding * 2)

        ratio_x = (
            available_width / map_width if map_width > 0 else float("inf")
        )
        ratio_y = (
            available_height / map_height if map_height > 0 else float("inf")
        )

        self.ratio = min(ratio_x, ratio_y)

        if self.ratio == float("inf"):
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
        if len(hubs) < 2:
            return 30

        min_dist = float("inf")
        for i in range(len(hubs)):
            for j in range(i + 1, len(hubs)):
                dist = math.hypot(hubs[i].x - hubs[j].x, hubs[i].y - hubs[j].y)
                if dist < min_dist:
                    min_dist = dist

        dist_in_pixels = min_dist * self.ratio
        return int(max(5, min(dist_in_pixels * 0.3, 200)))


def main():
    map_file = sys.argv[1]
    parser = FileParser()
    simulation: SimulationMap = parser.parse(map_file)

    pygame.init()
    info = pygame.display.Info()
    width = info.current_w * 0.7
    height = info.current_h * 0.7

    transformer = CoordTransformer()
    transformer.define_limits(simulation, width, height)
    radius = transformer.calculate_radius(simulation)

    window = pygame.display.set_mode((width, height))

    assets = AssetsManager(width, height, int(radius * 2))
    background = assets.get_background()
    drone = assets.get_drone()
    hub_sprites = assets.get_all_hub_sprites()

    running = True
    clock = pygame.time.Clock()

    while running:

        window.blit(background, (0, 0))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        for source_name, targets in simulation.connections.items():
            source_hub = simulation.hubs.get(source_name)
            if source_hub:
                for target_name in targets:
                    target_hub = simulation.hubs.get(target_name)
                    if target_hub:
                        x1, y1 = transformer.transform(
                            source_hub.x, source_hub.y
                        )
                        x2, y2 = transformer.transform(
                            target_hub.x, target_hub.y
                        )
                        pygame.draw.line(
                            window,
                            (100, 180, 255),
                            (x1, y1),
                            (x2, y2),
                            radius // 4,
                        )

        for hub in simulation.hubs.values():
            x, y = transformer.transform(hub.x, hub.y)

            c_name = getattr(hub, "color", "white")
            sprite = hub_sprites.get(c_name, hub_sprites["white"])
            rect = sprite.get_rect(center=(x, y))
            window.blit(sprite, rect)

            # BLOCKED: forbidden.png over the upper half of the hub
            if hub.zone == ZoneType.BLOCKED:
                forbidden_img = assets.get_forbidden()
                hub_w, hub_h = rect.size
                forb_orig_w, forb_orig_h = forbidden_img.get_size()
                forb_aspect = forb_orig_w / forb_orig_h
                # We want forbidden to cover the width of the hub and the upper half
                forb_w = int(hub_w * 1.5)
                forb_h = int(hub_h * 0.65 * 1.5)
                # Adjust the height to maintain aspect ratio, but never larger than the calculated height
                scaled_h = int(forb_w / forb_aspect)
                if scaled_h > forb_h:
                    forb_w = int(forb_h * forb_aspect)
                else:
                    forb_h = scaled_h
                forbidden_img_scaled = pygame.transform.smoothscale(forbidden_img, (forb_w, forb_h))
                # Position centered in x, and a bit lower to better cover the upper half
                forb_x = x
                forb_y = rect.top + forb_h // 2
                forbidden_rect = forbidden_img_scaled.get_rect(center=(forb_x, forb_y))
                window.blit(forbidden_img_scaled, forbidden_rect)

            # PRIORITY: star.png center left (0.75 ratio, keep aspect ratio)
            elif hub.zone == ZoneType.PRIORITY:
                star_img = assets.get_star()
                hub_w, hub_h = rect.size
                # TODO: optimize this scaling into a function, used in every sprite
                star_orig_w, star_orig_h = star_img.get_size()
                star_aspect = star_orig_w / star_orig_h
                scale = 0.75
                if star_aspect > 1:
                    star_w = int(hub_w * scale)
                    star_h = int(star_w / star_aspect)
                else:
                    star_h = int(hub_h * scale)
                    star_w = int(star_h * star_aspect)
                star_img_scaled = pygame.transform.smoothscale(star_img, (star_w, star_h))
                # Center left, same offset as drone_jam
                extra_offset_x = int(hub_w * 0.3)  # more to the left
                extra_offset_y = int(hub_h * 0.1)  # a bit lower
                star_x = rect.left + star_w // 2 - extra_offset_x
                star_y = rect.centery + extra_offset_y
                star_rect = star_img_scaled.get_rect(center=(star_x, star_y))
                window.blit(star_img_scaled, star_rect)

            # RESTRICTED: drone_jam.png center left (0.75 ratio,keep asp-ratio)
            elif hub.zone == ZoneType.RESTRICTED:
                jam_img = assets.get_drone_jam()
                hub_w, hub_h = rect.size
                jam_orig_w, jam_orig_h = jam_img.get_size()
                jam_aspect = jam_orig_w / jam_orig_h
                scale = 0.75
                if jam_aspect > 1:
                    jam_w = int(hub_w * scale)
                    jam_h = int(jam_w / jam_aspect)
                else:
                    jam_h = int(hub_h * scale)
                    jam_w = int(jam_h * jam_aspect)
                jam_img_scaled = pygame.transform.smoothscale(jam_img, (jam_w, jam_h))
                # Move more to the left and a bit lower
                extra_offset_x = int(hub_w * 0.3)  # more to the left
                extra_offset_y = int(hub_h * 0.1)  # a bit lower
                jam_x = rect.left + jam_w // 2 - extra_offset_x
                jam_y = rect.centery + extra_offset_y
                jam_rect = jam_img_scaled.get_rect(center=(jam_x, jam_y))
                window.blit(jam_img_scaled, jam_rect)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()
