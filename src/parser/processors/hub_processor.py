from src.parser.processors.base import LineProcessor
from src.schemas.simulation_map import SimulationMap
from src.schemas.hubs import Hub
from pydantic import ValidationError
from typing import Any


class HubProcessor(LineProcessor):
    """Creates Hub parsing fixed format: name x y [key=val key=val]"""

    ALLOWED_KEYS = {"zone", "color", "max_drones"}

    def process(self, data: list[str], current_map: SimulationMap) -> None:

        if current_map.nb_drones == 0:
            raise ValueError("Drone number must be defined in the first line")

        if len(data) < 3:
            raise ValueError("Missing Hub mandatory parameters")

        if data[0].strip() in current_map.hubs:
            raise ValueError(f"Hub name '{data[0]}' is duplicated")

        hub_params: dict[str, Any] = {
            "name": data[0].strip(),
            "x": int(data[1]),
            "y": int(data[2]),
        }

        if len(data) == 4:
            opt_str = data[3]

            if not (opt_str.startswith("[") and opt_str.endswith("]")):
                raise ValueError("Optional parameters must be enclosed in []")

            content = opt_str[1:-1].strip()

            if content:
                pairs = content.split(" ")

                for pair in pairs:
                    if "=" not in pair:
                        raise ValueError(
                            f"Invalid format '{pair}'. Expected key=value"
                        )

                    key, value = pair.split("=", 1)

                    if key not in self.ALLOWED_KEYS:
                        raise ValueError(
                            f"Unknown parameter '{key}'. "
                            f"Allowed: {self.ALLOWED_KEYS}"
                        )

                    hub_params[key] = value

        try:
            new_hub = Hub(**hub_params)
        except ValidationError as e:
            raise ValueError(f"Hub validation failed: {e}")

        current_map.hubs[new_hub.name] = new_hub
