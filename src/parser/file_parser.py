import sys
from src.schemas.simulation_map import SimulationMap
from src.schemas.definitions import NodeCategory
from src.parser.processors.hub_processor import HubProcessor
from src.parser.processors.connection_processor import ConnectionProcessor
from src.parser.processors.drone_processor import DroneProcessor


class FileParser:
    """Class to parse input file and populate the SimulationMap."""

    def __init__(self) -> None:
        """Initializes FileParser with an empty map and processors."""
        self.simulation_map = SimulationMap(
            nb_drones=0,
            hubs={},
            graph={},
        )

        self.processors = {
            "hub": HubProcessor(NodeCategory.INTERMEDIATE),
            "start_hub": HubProcessor(NodeCategory.START),
            "end_hub": HubProcessor(NodeCategory.END),
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
                            f"[ERROR] Line {line_num}: Missing ':' separator.",
                            file=sys.stderr,
                        )
                        continue

                    key, content = line.split(":", 1)
                    key = key.strip().lower()
                    data = content.lower().strip().split(" ", 3)

                    processor = self.processors.get(key)

                    if not processor:
                        print(
                            f"[ERROR] Line {line_num}: Unknown "
                            f"entity type '{key}'.",
                            file=sys.stderr,
                        )
                        continue

                    try:
                        processor.process(data, self.simulation_map)
                    except ValueError as e:
                        print(f"[ERROR] Line {line_num}: {e}", file=sys.stderr)
                        sys.exit(1)

        except OSError as e:
            print(
                f"[ERROR] Error reading input file: {e.strerror}: "
                f"'{e.filename}'",
                file=sys.stderr,
            )
            sys.exit(2)

        start_hub = None
        end_hub = None

        for hub in self.simulation_map.hubs.values():
            if hub.category == NodeCategory.START:
                start_hub = hub
            elif hub.category == NodeCategory.END:
                end_hub = hub

        if start_hub is None:
            print("[ERROR] Map is missing a Start Hub.", file=sys.stderr)
            sys.exit(1)

        if end_hub is None:
            print("[ERROR] Map is missing an End Hub.", file=sys.stderr)
            sys.exit(1)

        if start_hub.max_drones > self.simulation_map.nb_drones:
            print(
                "[ERROR] Start Hub max capacity lower than "
                "the drones number on simulation",
                file=sys.stderr,
            )
            sys.exit(1)

        if end_hub.max_drones > self.simulation_map.nb_drones:
            print(
                "[ERROR] End Hub max capacity lower than "
                "the drones number on simulation",
                file=sys.stderr,
            )
            sys.exit(1)

        for node in self.simulation_map.graph:
            neighbors = self.simulation_map.graph[node]
            for target in neighbors:
                target_hub = self.simulation_map.hubs[target]
                self.simulation_map.graph[node][target] = self.simulation_map.graph[node][target].copy()

                if target_hub.zone.value == "blocked":
                    self.simulation_map.graph[node][target]['cost'] = float('inf')

                elif target_hub.zone.value == "restricted":
                    self.simulation_map.graph[node][target]['cost'] = 2
                    self.simulation_map.graph[node][target]['turns'] = 2

                elif target_hub.zone.value == "priority":
                    self.simulation_map.graph[node][target]['cost'] = 0

                else:
                    self.simulation_map.graph[node][target]['cost'] = 1
                    self.simulation_map.graph[node][target]['turns'] = 1

        return self.simulation_map
