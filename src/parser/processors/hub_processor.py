from src.parser.processors.base_processor import LineProcessor
from src.schemas.simulation_map import SimulationMap
from src.schemas.hubs import Hub
from src.schemas.definitions import ZoneType, NodeCategory
from pydantic import ValidationError
from typing import Any


class HubProcessor(LineProcessor):
    """Creates Hub parsing fixed format: name x y [key=val key=val]"""

    ALLOWED_KEYS = {"zone", "color", "max_drones"}

    def __init__(
        self, category: NodeCategory = NodeCategory.INTERMEDIATE
    ) -> None:
        """Initializes the processor with a specific node category."""
        self.category = category

    def _do_process(self, data: list[str], current_map: SimulationMap) -> None:

        if current_map.nb_drones == 0:
            raise ValueError("Drones number must be defined in the first line")

        if len(data) < 3:
            raise ValueError("Missing Hub mandatory parameters")

        name = data[0].strip()

        if name in current_map.hubs:
            raise ValueError(f"Hub name '{name}' is duplicated")

        if self.category in (NodeCategory.START, NodeCategory.END):
            for hub in current_map.hubs.values():
                if hub.category == self.category:
                    cat = self.category.value.capitalize()
                    raise ValueError(f"{cat} Hub is duplicated")

        hub_params: dict[str, Any] = {
            "name": name,
            "x": int(data[1]),
            "y": int(data[2]),
            "category": self.category,
            "type": ZoneType.NORMAL,
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

        if self.category in (NodeCategory.START, NodeCategory.END):
            if "max_drones" not in hub_params:
                hub_params["max_drones"] = current_map.nb_drones

        try:
            new_hub = Hub(**hub_params)
        except ValidationError as e:
            raise ValueError(f"Hub validation failed: {e}")

        current_map.hubs[name] = new_hub
