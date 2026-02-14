import sys
from src.parser.file_parser import FileParser
from src.solver.time_graph import TimeGraph
from src.solver.flow_solver import FlowSolver
from src.solver.time_estimator import estimate_max_time
from src.schemas.simulation_map import SimulationMap
from src.visualization.visual_simulation import VisualSimulation


def main() -> None:

    if len(sys.argv) < 2:
        map_file = "maps/easy/01_linear_path.txt"

    elif len(sys.argv) == 2:
        map_file = sys.argv[1]

    else:
        print("[ERROR] Usage: python3 fly-in.py"
              " <map_file.txt>", file=sys.stderr)
        sys.exit(1)

    parser = FileParser()
    simulation: SimulationMap = parser.parse(map_file)
    max_turns = estimate_max_time(simulation)

    if max_turns < 0:
        print("ERROR: No path exists from START to END", file=sys.stderr)
        sys.exit(1)

    time_graph = TimeGraph(simulation, max_turns)
    solver = FlowSolver(time_graph, simulation.nb_drones)
    solver.solve_all_drones()

    drones = solver.get_drones()
    output_lines = solver.get_simulation_output()

    visual = VisualSimulation(simulation, drones, output_lines)
    try:
        visual.run()
    except KeyboardInterrupt:
        print("\n[ERROR] Simulation interrupted")


if __name__ == "__main__":
    main()
