import sys
from src.parser.file_parser import FileParser
from src.solver.time_graph import TimeGraph
from src.solver.flow_solver import FlowSolver
from src.solver.time_estimator import estimate_max_time, has_path_to_end
from src.schemas.simulation_map import SimulationMap
from src.visualization.visual_simulation import VisualSimulation


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python3 main_visual.py <map_file.txt>", file=sys.stderr)
        sys.exit(1)

    map_file = sys.argv[1]

    # Parse map
    parser = FileParser()
    simulation: SimulationMap = parser.parse(map_file)

    # Validate path exists
    if not has_path_to_end(simulation):
        print("ERROR: No path exists from START to END", file=sys.stderr)
        sys.exit(1)

    # Solve
    max_turns = estimate_max_time(simulation)
    time_graph = TimeGraph(simulation, max_turns)
    solver = FlowSolver(time_graph, simulation.nb_drones)
    solver.solve_all_drones()

    # Get results
    drones = solver.get_drones()
    output_lines = solver.get_simulation_output()

    # Run visual simulation
    visual = VisualSimulation(simulation, drones, output_lines)
    visual.run()


if __name__ == "__main__":
    main()
