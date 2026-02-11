import sys
from src.parser.file_parser import FileParser
from src.solver.time_graph import TimeGraph
from src.solver.flow_solver import FlowSolver


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 main_solver.py <map_file.txt> [max_time]")
        sys.exit(1)

    map_file = sys.argv[1]
    max_time = int(sys.argv[2]) if len(sys.argv) > 2 else 10

    parser = FileParser()
    simulation = parser.parse(map_file)

    print(f"Map: {map_file}")
    print(f"Number of drones: {simulation.nb_drones}")
    print(f"Max time: {max_time}")

    tg = TimeGraph(max_time=max_time)
    hubs_list = simulation.hubs.values() if isinstance(simulation.hubs, dict) else simulation.hubs
    tg.build_graph(hubs_list, simulation.connections)

    print(f"\nTimeGraph built: {len(tg.nodes)} nodes, {len(tg.edges)} edges")

    solver = FlowSolver(tg, simulation.nb_drones)
    solver.solve_all_drones()

    solver.print_movements()
    solver.print_summary()


if __name__ == "__main__":
    main()