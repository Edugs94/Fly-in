import os
from typing import Dict, List, Tuple
from src.schemas.simulation_map import SimulationMap
from src.schemas.drone import Drone
from src.schemas.definitions import ZoneType
from src.visualization.assets_manager import AssetsManager
from src.visualization.coord_transformer import CoordTransformer

os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "hide"
import pygame  # noqa


class VisualSimulation:
    """Handles the visual rendering of simulation."""

    def __init__(
        self,
        simulation: SimulationMap,
        drones: Dict[int, Drone],
        output_lines: List[str],
    ):
        self.simulation = simulation
        self.drones = drones
        self.output_lines = output_lines
        self.current_turn = 0
        self.max_turn = len(output_lines)

        self.animation_progress = 0.0
        self.turn_duration_ms = 1000
        self.simulation_ended_printed = False
        self.drone_frame = 0
        self.drone_frame_timer = 0.0
        self.drone_frame_duration = 20

    def run(self) -> None:
        """Main loop for visual simulation."""
        pygame.init()
        info = pygame.display.Info()
        width = int(info.current_w * 0.7)
        height = int(info.current_h * 0.7)

        transformer = CoordTransformer()
        transformer.define_limits(self.simulation, width, height)
        radius = transformer.calculate_radius(self.simulation)

        window = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Fly-in")

        assets = AssetsManager(width, height, int(radius * 2))
        background = assets.get_background()
        hub_sprites = assets.get_all_hub_sprites()

        font = pygame.font.Font(None, 52)
        small_font = pygame.font.Font(None, 24)

        clock = pygame.time.Clock()
        running = True
        last_ms = pygame.time.get_ticks()

        while running:
            current_ms = pygame.time.get_ticks()
            delta_ms = current_ms - last_ms
            last_ms = current_ms

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False

            self.animation_progress += delta_ms / self.turn_duration_ms
            if self.animation_progress >= 1.0:
                self._print_turn_output()
                self._advance_turn()

            self.drone_frame_timer += delta_ms
            if self.drone_frame_timer >= self.drone_frame_duration:
                self.drone_frame = (self.drone_frame + 1) % 4
                self.drone_frame_timer = 0.0

            window.blit(background, (0, 0))

            self._draw_connections(window, transformer, radius)
            self._draw_hubs(window, transformer, hub_sprites, assets)
            self._draw_drones(window, transformer, assets, radius)
            self._draw_ui(window, font, small_font, width, height)

            pygame.display.flip()
            clock.tick(60)

        pygame.quit()

    def _advance_turn(self) -> None:
        """Advance to next turn."""
        if self.current_turn < self.max_turn:
            self.current_turn += 1
            self.animation_progress = 0.0

    def _print_turn_output(self) -> None:
        """Print the output for current turn to terminal."""
        if self.current_turn < len(self.output_lines):
            print(self.output_lines[self.current_turn])
        elif not self.simulation_ended_printed:
            print("Simulation ended. Press 'Esc' to exit")
            self.simulation_ended_printed = True

    def _get_interpolated_position(
        self, drone: Drone, transformer: CoordTransformer
    ) -> Tuple[float, float]:
        """Get drone position interpolated between turns."""

        curr_x, curr_y = drone.get_position_at_turn(self.current_turn)

        next_turn = self.current_turn + 1
        next_x, next_y = drone.get_position_at_turn(next_turn)

        interp_x = curr_x + (next_x - curr_x) * self.animation_progress
        interp_y = curr_y + (next_y - curr_y) * self.animation_progress

        return transformer.transform(interp_x, interp_y)

    def _draw_connections(
        self,
        window: pygame.Surface,
        transformer: CoordTransformer,
        radius: int,
    ) -> None:
        """Draw all connections between hubs."""
        for source_name, targets in self.simulation.connections.items():
            source_hub = self.simulation.hubs.get(source_name)
            if source_hub:
                for target_name in targets:
                    target_hub = self.simulation.hubs.get(target_name)
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
                            radius // 12,
                        )

    def _draw_hubs(
        self,
        window: pygame.Surface,
        transformer: CoordTransformer,
        hub_sprites: dict,
        assets: AssetsManager,
    ) -> None:
        """Draw all hubs with their zone indicators."""
        for hub in self.simulation.hubs.values():
            x, y = transformer.transform(hub.x, hub.y)

            c_name = getattr(hub, "color", "white")
            sprite = hub_sprites.get(c_name, hub_sprites["white"])
            rect = sprite.get_rect(center=(x, y))
            window.blit(sprite, rect)

            hub_w, hub_h = rect.size

            if hub.zone == ZoneType.BLOCKED:
                forbidden_img = assets.get_forbidden()
                forb_orig_w, forb_orig_h = forbidden_img.get_size()
                forb_aspect = forb_orig_w / forb_orig_h
                forb_w = int(hub_w * 1.5)
                forb_h = int(hub_h * 0.65 * 1.5)
                scaled_h = int(forb_w / forb_aspect)
                if scaled_h > forb_h:
                    forb_w = int(forb_h * forb_aspect)
                else:
                    forb_h = scaled_h
                forbidden_scaled = pygame.transform.smoothscale(
                    forbidden_img, (forb_w, forb_h)
                )
                forb_y = rect.top + forb_h // 2
                forb_rect = forbidden_scaled.get_rect(center=(x, forb_y))
                window.blit(forbidden_scaled, forb_rect)

            elif hub.zone == ZoneType.PRIORITY:
                star_img = assets.get_star()
                star_orig_w, star_orig_h = star_img.get_size()
                star_aspect = star_orig_w / star_orig_h
                scale = 0.75
                if star_aspect > 1:
                    star_w = int(hub_w * scale)
                    star_h = int(star_w / star_aspect)
                else:
                    star_h = int(hub_h * scale)
                    star_w = int(star_h * star_aspect)
                star_scaled = pygame.transform.smoothscale(
                    star_img, (star_w, star_h)
                )
                extra_offset_x = int(hub_w * 0.3)
                extra_offset_y = int(hub_h * 0.1)
                star_x = rect.left + star_w // 2 - extra_offset_x
                star_y = rect.centery + extra_offset_y
                star_rect = star_scaled.get_rect(center=(star_x, star_y))
                window.blit(star_scaled, star_rect)

            elif hub.zone == ZoneType.RESTRICTED:
                jam_img = assets.get_drone_jam()
                jam_orig_w, jam_orig_h = jam_img.get_size()
                jam_aspect = jam_orig_w / jam_orig_h
                scale = 0.75
                if jam_aspect > 1:
                    jam_w = int(hub_w * scale)
                    jam_h = int(jam_w / jam_aspect)
                else:
                    jam_h = int(hub_h * scale)
                    jam_w = int(jam_h * jam_aspect)
                jam_scaled = pygame.transform.smoothscale(
                    jam_img, (jam_w, jam_h)
                )
                extra_offset_x = int(hub_w * 0.3)
                extra_offset_y = int(hub_h * 0.1)
                jam_x = rect.left + jam_w // 2 - extra_offset_x
                jam_y = rect.centery + extra_offset_y
                jam_rect = jam_scaled.get_rect(center=(jam_x, jam_y))
                window.blit(jam_scaled, jam_rect)

    def _draw_drones(
        self,
        window: pygame.Surface,
        transformer: CoordTransformer,
        assets: AssetsManager,
        radius: int,
    ) -> None:
        """Draw all drones at their current positions."""
        drone_sprite = assets.get_drone(self.drone_frame)

        for drone_id, drone in self.drones.items():
            if drone.delivered and len(drone.path) > 0:
                last_turn = drone.path[-1][0]
                if self.current_turn > last_turn:
                    continue

            x, y = self._get_interpolated_position(drone, transformer)

            drone_size = int(radius * 1.2)
            scaled_drone = pygame.transform.scale(
                drone_sprite, (drone_size, drone_size)
            )
            rect = scaled_drone.get_rect(center=(x, y))
            window.blit(scaled_drone, rect)

    def _draw_ui(
        self,
        window: pygame.Surface,
        font: pygame.font.Font,
        small_font: pygame.font.Font,
        width: int,
        height: int,
    ) -> None:
        """Draw UI elements (turn counter, controls, current output)."""
        turn_text = font.render(
            f"TURN: {self.current_turn}/{self.max_turn}",
            True,
            (0, 0, 0),
        )
        window.blit(turn_text, (10, 10))
