import sys
from src.parser.file_parser import FileParser
from rich import print as rprint


def main():

    if len(sys.argv) != 2:
        print("[ERROR] Usage: python3 main.py <map_file.txt>", file=sys.stderr)
        sys.exit(1)

    map_file = sys.argv[1]

    print(f"Loading map from '{map_file}'...")
    parser = FileParser()
    simulation = parser.parse(map_file)

    rprint((vars(simulation)))


if __name__ == "__main__":
    main()
