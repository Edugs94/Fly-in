from pydantic import ValidationError
from src.parser.processors.base_processor import LineProcessor
from src.schemas.simulation_map import SimulationMap
from src.schemas.connection import Connection


class ConnectionProcessor(LineProcessor):
    """Creates Connection parsing format: source-target [key=val]"""

    ALLOWED_KEYS = {"max_link_capacity"}

    def _validate_name(self, data: list[str]) -> None:
        if not data:
            raise ValueError("Invalid Map Entity empty name")
        if " " in data[0]:
            raise ValueError(f"Invalid name '{data[0]} cannot contain spaces")

    def _do_process(self, data: list[str], current_map: SimulationMap) -> None:
        if current_map.nb_drones == 0:
            raise ValueError("Drones number must be defined in the first line")

        if len(data) < 1:
            raise ValueError("Missing connection data")

        raw_names = data[0]

        if raw_names.count("-") != 1:
            raise ValueError(
                f"Invalid connection format '{raw_names}'. "
                "Expected 'Source-Target'"
            )

        source, target = raw_names.split("-")

        if source == target:
            raise ValueError("Connection must be between two different hubs")

        if not source or not target:
            raise ValueError(
                f"Invalid connection format '{raw_names}'"
                ". Names are required."
            )

        valid_hub_names = current_map.hubs.keys()
        if source not in valid_hub_names:
            raise ValueError(f"Hub '{source}' is not defined.")
        if target not in valid_hub_names:
            raise ValueError(f"Hub '{target}' is not defined.")

        if (
            source in current_map.connections
            and target in current_map.connections[source]
        ):
            raise ValueError(
                f"Connection between '{source}' and '{target}'"
                " already exists"
            )

        max_link_capacity = 1
        current_drones = 0

        if len(data) > 2:
            raise ValueError(
                "Invalid format. Spaces not allowed inside parameters."
            )

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

                    try:
                        int_value = int(value)
                        if key == "max_link_capacity":
                            max_link_capacity = int_value
                        elif key == "current_drones":
                            current_drones = int_value
                    except ValueError:
                        raise ValueError(
                            f"Value for '{key}' must be an integer"
                        )

        try:
            new_connection = Connection(
                source=source,
                target=target,
                max_link_capacity=max_link_capacity,
                current_drones=current_drones,
            )
        except ValidationError as e:
            raise ValueError(
                f"Connection validation failed: {e.errors()[0]['msg']}"
            )

        if source not in current_map.connections:
            current_map.connections[source] = {}
        if target not in current_map.connections:
            current_map.connections[target] = {}

        current_map.connections[source][target] = new_connection
        current_map.connections[target][source] = new_connection
