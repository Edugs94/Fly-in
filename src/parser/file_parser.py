import sys
from src.schemas.simulation_map import SimulationMap
from src.parser.processors.hub_processor import HubProcessor
from src.parser.processors.start_hub_processor import StartHubProcessor
from src.parser.processors.end_hub_processor import EndHubProcessor
from src.parser.processors.connection_processor import ConnectionProcessor
from src.parser.processors.drone_processor import DroneProcessor


class FileParser:
    """Class to parse input file and populate the SimulationMap."""

    def __init__(self) -> None:
        """Initializes FileParser with an empty map and processors."""
        self.simulation_map = SimulationMap(
            nb_drones=0,
            start_hub=None,
            end_hub=None,
            hubs={},
            connections=[],
        )

        self.processors = {
            "hub": HubProcessor(),
            "start_hub": StartHubProcessor(),
            "end_hub": EndHubProcessor(),
            "connection": ConnectionProcessor(),
            "nb_drones": DroneProcessor(),
        }

    def parse(self, filename: str) -> SimulationMap:
        """Reads, processes the file and validates map completeness."""
        try:
            with open(filename, "r") as f:
                for line_num, line in enumerate(f, start=1):
                    line = line.strip()

                    if not line or line.startswith("#"):
                        continue

                    if ":" not in line:
                        print(
                            f"[ERROR] Syntax error in {filename} at line "
                            f"{line_num}: Missing ':' separator.",
                            file=sys.stderr,
                        )
                        continue

                    key, content = line.split(":", 1)
                    key = key.strip().lower()
                    data = content.strip().split()

                    processor = self.processors.get(key)

                    if not processor:
                        print(
                            f"[ERROR] Unknown entity type '{key}' in "
                            f"{filename} at line {line_num}.",
                            file=sys.stderr,
                        )
                        continue

                    try:
                        processor.process(data, self.simulation_map)
                    except ValueError as e:
                        print(
                            f"[ERROR] Semantic error in {filename} at line "
                            f"{line_num}: {e}",
                            file=sys.stderr,
                        )
                        sys.exit(1)

        except OSError as e:
            print(
                f"[ERROR] Error reading input file: {e.strerror}: "
                f"'{e.filename}'",
                file=sys.stderr,
            )
            sys.exit(2)

        if self.simulation_map.start_hub is None:
            print("[ERROR] Map is missing a Start Hub.", file=sys.stderr)
            sys.exit(1)

        if self.simulation_map.end_hub is None:
            print("[ERROR] Map is missing an End Hub.", file=sys.stderr)
            sys.exit(1)

        return self.simulation_map
