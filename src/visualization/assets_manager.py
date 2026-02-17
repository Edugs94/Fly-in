import os
from typing import Optional

os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "hide"
import pygame  # noqa


class AssetsManager:
    """
    Manages the loading and scaling of all game assets (images, sprites)
    while maintaining aspect ratios.
    """

    def __init__(
        self, window_width: int, window_height: int, hub_diameter: int
    ) -> None:
        self.window_width = window_width
        self.window_height = window_height
        self.hub_diameter = hub_diameter

        self.background: Optional[pygame.Surface] = None
        self.drone1: Optional[pygame.Surface] = None
        self.drone2: Optional[pygame.Surface] = None
        self.drone3: Optional[pygame.Surface] = None
        self.drone4: Optional[pygame.Surface] = None
        self.hub_sprites: dict[str, pygame.Surface] = {}
        self.star: Optional[pygame.Surface] = None
        self.forbidden: Optional[pygame.Surface] = None
        self.drone_jam: Optional[pygame.Surface] = None

        self.color_map = {
            "red": (255, 50, 50),
            "green": (50, 255, 50),
            "blue": (0, 150, 255),
            "yellow": (255, 255, 0),
            "white": (255, 255, 255),
            "purple": (128, 0, 128),
            "black": (45, 45, 45),
            "brown": (165, 42, 42),
            "orange": (255, 165, 0),
            "maroon": (128, 0, 0),
            "gold": (255, 215, 0),
            "darkred": (139, 0, 0),
            "violet": (238, 130, 238),
            "crimson": (220, 20, 60),
            "rainbow": (0, 0, 0),
        }

        self._load_assets()

    @staticmethod
    def _scale_with_aspect_ratio(
        image: pygame.Surface, target_size: int
    ) -> pygame.Surface:
        """
        Scales an image to fit within target_size
        while maintaining aspect ratio.
        """
        width, height = image.get_size()
        aspect_ratio = width / height

        if aspect_ratio > 1:
            new_width = target_size
            new_height = int(target_size / aspect_ratio)
        else:
            new_height = target_size
            new_width = int(target_size * aspect_ratio)

        return pygame.transform.scale(image, (new_width, new_height))

    @staticmethod
    def _get_colored_surface(
        surface: pygame.Surface, color: tuple
    ) -> pygame.Surface:
        """
        Colors a white image with the specified color.
        """
        colored_surface = surface.copy()
        colored_surface.fill(color, special_flags=pygame.BLEND_RGBA_MULT)
        return colored_surface

    def _load_assets(self) -> None:
        """
        Loads and processes all game assets.
        """
        background_raw = pygame.image.load("assets/background.png").convert()
        self.background = pygame.transform.scale(
            background_raw, (self.window_width, self.window_height)
        )

        drone_raw = pygame.image.load("assets/drone1.png").convert_alpha()
        self.drone1 = pygame.transform.smoothscale(drone_raw, (500, 500))
        drone2_raw = pygame.image.load("assets/drone2.png").convert_alpha()
        self.drone2 = pygame.transform.smoothscale(drone2_raw, (500, 500))
        drone3_raw = pygame.image.load("assets/drone3.png").convert_alpha()
        self.drone3 = pygame.transform.smoothscale(drone3_raw, (500, 500))
        drone4_raw = pygame.image.load("assets/drone4.png").convert_alpha()
        self.drone4 = pygame.transform.smoothscale(drone4_raw, (500, 500))

        hub_raw = pygame.image.load("assets/hub.png").convert_alpha()
        hub_scaled = self._scale_with_aspect_ratio(hub_raw, self.hub_diameter)

        hub_rainbow_raw = pygame.image.load(
            "assets/hub_rainbow.png"
        ).convert_alpha()
        hub_rainbow_scaled = self._scale_with_aspect_ratio(
            hub_rainbow_raw, self.hub_diameter
        )

        star_raw = pygame.image.load("assets/star2.png").convert_alpha()
        self.star = self._scale_with_aspect_ratio(star_raw, self.hub_diameter)

        forbidden_raw = pygame.image.load(
            "assets/forbidden.png"
        ).convert_alpha()
        self.forbidden = self._scale_with_aspect_ratio(
            forbidden_raw, self.hub_diameter
        )

        drone_jam_raw = pygame.image.load(
            "assets/drone_jam.png"
        ).convert_alpha()
        self.drone_jam = self._scale_with_aspect_ratio(
            drone_jam_raw, self.hub_diameter
        )

        for color_name, rgb_value in self.color_map.items():
            if color_name == "rainbow":
                self.hub_sprites[color_name] = hub_rainbow_scaled
            else:
                self.hub_sprites[color_name] = self._get_colored_surface(
                    hub_scaled, rgb_value
                )

    def get_background(self) -> pygame.Surface:
        """Returns the background image."""
        return (
            self.background
            if self.background
            else pygame.Surface((self.window_width, self.window_height))
        )

    def get_drone(self, frame: int = 0) -> pygame.Surface:
        """Returns the drone image for the given frame (0-3)."""
        drones = [self.drone1, self.drone2, self.drone3, self.drone4]
        drone = drones[frame % 4]

        if drone:
            return drone

        radius = 10
        diameter = radius * 2
        error_control_surface = pygame.Surface(
            (diameter, diameter), pygame.SRCALPHA
        )
        pygame.draw.circle(
            error_control_surface, (255, 255, 255), (radius, radius), radius
        )
        return error_control_surface

    def get_hub_sprite(self, color: str) -> pygame.Surface:
        """Returns the hub sprite for the specified color."""
        return self.hub_sprites.get(
            color, self.hub_sprites.get("white", pygame.Surface((10, 10)))
        )

    def get_all_hub_sprites(self) -> dict[str, pygame.Surface]:
        """Returns all hub sprites."""
        return self.hub_sprites

    def get_star(self) -> pygame.Surface:
        """Returns the star image."""
        return self.star if self.star else pygame.Surface((10, 10))

    def get_forbidden(self) -> pygame.Surface:
        """Returns the forbidden image."""
        return self.forbidden if self.forbidden else pygame.Surface((10, 10))

    def get_drone_jam(self) -> pygame.Surface:
        """Returns the drone jam image."""
        return self.drone_jam if self.drone_jam else pygame.Surface((10, 10))
