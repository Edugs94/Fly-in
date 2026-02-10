import sys
import os
from rich import print as rprint
from src.parser.file_parser import FileParser
from src.solver.time_graph import TimeGraph

def main():
    if len(sys.argv) != 2:
        rprint("[bold red][ERROR] Usage: python3 main.py <map_file.txt>[/bold red]")
        sys.exit(1)

    map_file = sys.argv[1]
    if not os.path.exists(map_file):
        rprint(f"[bold red][ERROR] The file '{map_file}' does not exist.[/bold red]")
        sys.exit(1)

    rprint(f"[bold white]Loading map from '{map_file}'...[/bold white]")

    parser = FileParser()
    simulation_map = parser.parse(map_file)

    turns = 5
    rprint(f"\n[bold green]Initializing TimeGraph with {turns} turns...[/bold green]")

    graph = TimeGraph(turns)
    graph.build(simulation_map)

    rprint("\n[bold blue]--- CONNECTION VERIFICATION (t=0 and t=1) ---[/bold blue]")

    for node, edges in graph.adjacency.items():
        if node.time < 2:
            rprint(f"[yellow]Origin:[/yellow] {node.hub.name} (t={node.time})")

            if not edges:
                rprint("   (No outgoing edges)")

            for edge in edges:
                edge_type = "WAIT" if edge.target.hub.name == node.hub.name else "MOVE"
                color = "dim" if edge_type == "WAIT" else "bold white"

                rprint(f"   --> [{color}]{edge_type}[/{color}] to [cyan]{edge.target.hub.name}[/cyan] (t={edge.target.time}) "
                       f"| Capacity: {edge.tracker.max_link_capacity}")

            print("-" * 30)

if __name__ == "__main__":
    main()