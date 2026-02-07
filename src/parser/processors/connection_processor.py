from src.parser.processors.base_processor import LineProcessor
from src.schemas.simulation_map import SimulationMap


class ConnectionProcessor(LineProcessor):
    """Creates Connection parsing format: source-target [key=val]"""

    ALLOWED_KEYS = {"max_link_capacity"}

    def _validate_name(self, data: list[str]) -> None:
        if not data:
            raise ValueError("Invalid Map Entinty empty name")
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

        valid_hub_names = current_map.hubs.keys()

        if source not in valid_hub_names:
            raise ValueError(
                f"Error creating connection {data[0]}: "
                f"Hub '{source}' is not defined (or not defined yet)."
            )

        if target not in valid_hub_names:
            raise ValueError(
                f"Error creating connection {data[0]}: "
                f"Hub '{target}' is not defined (or not defined yet)."
            )

        if source in current_map.graph and target in current_map.graph[source]:
            raise ValueError(
                f"Connection between '{source}' and '{target}' already exists"
            )

        conn_attributes = {"max_link_capacity": 1, "cost": 1, "turns": 1}

        if len(data) > 2:
            raise ValueError("Invalid format. Spaces are not allowed "
                             "inside parameters or brackets.")
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
                    conn_attributes[key] = int(value)

        if conn_attributes['max_link_capacity'] <= 0:
            raise ValueError("Connection link capacity must be greater than 0")
        if source not in current_map.graph:
            current_map.graph[source] = {}
        if target not in current_map.graph:
            current_map.graph[target] = {}

        current_map.graph[source][target] = conn_attributes
        current_map.graph[target][source] = conn_attributes
