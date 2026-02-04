import sys
from src.parser.file_parser import FileParser


def main():

    if len(sys.argv) != 2:
        print("[ERROR] Usage: python3 main.py <map_file.txt>", file=sys.stderr)
        sys.exit(1)

    map_file = sys.argv[1]

    print(f"Loading map from '{map_file}'...")
    parser = FileParser()
    sim_map = parser.parse(map_file)

    print("\n" + "=" * 40)
    print("       SIMULATION MAP SUMMARY")
    print("=" * 40)

    print(f"Total Drones: {sim_map.nb_drones}")

    print("-" * 40)
    print(
        f"Start Hub: {sim_map.start_hub.name} (x={sim_map.start_hub.x}, y={sim_map.start_hub.y})"
    )
    print(
        f"End Hub:   {sim_map.end_hub.name} (x={sim_map.end_hub.x}, y={sim_map.end_hub.y})"
    )

    print("-" * 40)
    print(f"Hubs ({len(sim_map.hubs)} total):")
    for name, hub in sim_map.hubs.items():
        role = "[NORMAL]"
        if hub == sim_map.start_hub:
            role = "[START] "
        if hub == sim_map.end_hub:
            role = "[END]   "

        print(f"  - {role} {name:<10} | Pos: ({hub.x}, {hub.y})")

    print("-" * 40)
    print(f"Connections ({len(sim_map.connections)} total):")
    for conn in sim_map.connections:
        print(
            f"  - {conn.source} <--> {conn.target} | Capacity: {conn.max_link_capacity}"
        )

    print("=" * 40 + "\n")


if __name__ == "__main__":
    main()
