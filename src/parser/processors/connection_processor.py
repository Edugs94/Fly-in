from src.parser.processors.base import LineProcessor
from src.schemas.simulation_map import SimulationMap
from pydantic import ValidationError
from src.schemas.connection import Connection
from typing import Any


class ConnectionProcessor(LineProcessor):
    """Creates Connection parsing format: source-target [key=val]"""

    ALLOWED_KEYS = {"max_link_capacity"}

    def process(self, data: list[str], current_map: SimulationMap) -> None:

        if current_map.nb_drones == 0:
            raise ValueError("Drone number must be defined in the first line")

        if len(data) < 1:
            raise ValueError("Missing connection data")

        raw_names = data[0]

        if raw_names.count("-") != 1:
            raise ValueError(
                f"Invalid connection format '{raw_names}'."
                " Expected 'Source-Target'"
            )

        source, target = raw_names.split("-")

        if source == target:
            raise ValueError("Connection must be between two different hubs")

        if not source or not target:
            raise ValueError(
                f"Invalid connection format '{raw_names}'. "
                "Both source and target names are required."
            )

        forward_link = f"{source}-{target}"
        backward_link = f"{target}-{source}"

        if (
            forward_link in current_map.connections
            or backward_link in current_map.connections
        ):
            raise ValueError(
                f"Connection between '{source}' and '{target}' already exists"
            )

        conn_params: dict[str, Any] = {
            "name": forward_link,
            "source": source,
            "target": target,
        }
        reverse_params: dict[str, Any] = {
            "name": backward_link,
            "source": target,
            "target": source,
        }

        if len(data) == 2:
            opt_str = data[1]

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
                    conn_params[key] = int(value)

        try:
            new_connection = Connection(**conn_params)
            reverse_connection = Connection(**reverse_params)
        except ValidationError as e:
            raise ValueError(f"Connection validation failed: {e}")

        current_map.connections.append(new_connection)
        current_map.connections.append(reverse_connection)
