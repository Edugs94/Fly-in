# Fly-in: Multi-Drone Routing Solver

An optimal routing system for multiple drones that uses a time-expanded graph (TEG) and a modified Dijkstra's algorithm to solve complex aerial logistics problems.

## 🎯 Overview

Fly-in solves the problem of finding optimal routes for multiple drones from a starting point to a destination, respecting:

- **Connection Capacities**: Limits on the number of drones that can use a link simultaneously
- **Restricted Zones**: Areas that require 2 turns to traverse
- **Priority Zones**: Nodes that maximize travel efficiency
- **Hub Capacity Constraints**: Limits on drones at each node

## ✨ Key Features

### Time-Expanded Graph (TEG)
The project leverages a **Time-Expanded Graph** to elegantly model the routing problem:
- Transforms a static graph into a dynamic space-time representation
- Each node is a tuple `(hub, time_step)` rather than just a hub
- Connections become natural temporal dependencies
- **Wait actions** are treated as regular edges, not special cases

**Why TEG?**
- **Unified Edge Model**: Waiting at a hub is just a self-loop edge from `(hub, t)` to `(hub, t+1)`, eliminating complex nested if-else logic
- **Standard Graph Search**: Enables clean Dijkstra implementation without special waiting logic
- **Transparent Capacity Handling**: Both movement and waiting respect capacity constraints uniformly
- **Natural Time Representation**: Time is an explicit dimension, not implicit in algorithm logic

### Modified Dijkstra Algorithm
- **Lexicographic Optimization**: Optimizes first by time (turns), then by priority (priority zones traversed)
- **Sequential Multi-Drone Solving**: Solves for each drone sequentially while respecting already-consumed capacities
- **Guaranteed Optimality**: Maximum time calculation ensures first-attempt success for all drones

### Robust Map Validation
- Type-safe file parsing with Pydantic validation
- Path existence verification (START → END)
- Automatic optimal time calculation
- Comprehensive error reporting

### Intelligent Output
- **Normal Zones**: Simplified format `D1-destination`
- **Restricted Zones**: Connection format `D1-source-destination`
- **In-Flight Tracking**: Records drone movements between time steps

## 📊 Understanding Time-Expanded Graphs

### What is a TEG?

A Time-Expanded Graph replicates each node for every possible time step and connects them to form a graph that explicitly represents time as a dimension. This elegant technique eliminates the need for intricate conditional logic when handling waiting states—waiting is simply another edge in the graph, identical to movement edges.

#### Standard Graph Example

Consider a simple network:

**Original Graph:**

![Example Graph](assets/eg_graph_colors_horizontal.png)

The problem with this static representation: How do we handle waiting? How do we represent that a drone might arrive at different nodes at different times? Standard graph algorithms don't naturally support temporal dynamics.

### TEG Solution

A Time-Expanded Graph creates separate nodes for each time step:

**Same Graph as TEG (3 time steps):**

![TEG Expansion](assets/TEG_colors.png)

Notice how:
- Each hub appears once per time step
- **Horizontal edges** are "wait" operations (staying at the same hub)
- **Diagonal edges** are movements between hubs
- Restricted zones would take 2 time steps in case they exist
- The graph structure cleanly handles all temporal dynamics without conditional logic

### TEG Advantages Over Direct Modeling

**Without TEG** (traditional approach):
```python
# Complex logic for waiting
if at_node and can_wait:
    current_time += 1
    if check_capacity(...):
        proceed()
# Multiple branches for movement vs. waiting
# Special cases for restricted zones
# Nested conditionals become intricate and error-prone

# Critical complexity: capacity must be checked for the NEXT turn, not current
# For vertices: check capacity of destination hub at time t+1
if hub_capacity[destination][t + 1] > current_drones[destination][t + 1]:
    allow_move()
# For edges: check if connection will be available at time t (departure time)
if edge_usage[connection][t] < edge_capacity[connection]:
    allow_traversal()
# This temporal offset logic is error-prone and must be manually tracked
```

**With TEG** (clean approach):
```python
# All transitions are edges - unified treatment
for edge in adjacency[current_node]:
    if edge.is_traversable():
        consider_path(edge.target)
# Capacity checks are automatic: edge.target already represents (hub, t+1)
# No manual time offset calculations needed
```

The key insight is that **without TEG**, you must manually verify capacity constraints at the **next time step** rather than the current one:
- **Vertex capacity**: When moving to hub H, you need `capacity(H, t+1)`, not `capacity(H, t)`
- **Edge capacity**: When traversing connection C at time t, you check `usage(C, t)` against its limit

With TEG, this complexity vanishes because nodes already encode time. When you check `edge.target.can_enter()`, you're automatically checking the capacity at the correct future time step—the temporal dimension is built into the graph structure itself.

**Benefits realized**:
- ✅ **Elimination of intricate nested conditionals**: All actions (wait, move, traverse restricted) are uniform edges
- ✅ **Waiting treated identically to movement**: No special handling of wait logic
- ✅ **Capacity constraints applied uniformly**: Both edges and nodes enforce capacity through shared mechanism
- ✅ **Restricted zones implicit in structure**: 2-turn zones automatically represented through graph connectivity
- ✅ **Reusability of standard algorithms**: Dijkstra and other graph algorithms work unchanged
- ✅ **Explicit time dimension**: Time evolution is clear and maintainable

## 🚀 Quick Start

### Prerequisites
- Python 3.1+
- pip

### Installation

```bash
# Clone repository
git clone <repo-url>
cd Fly-in

# Create virtual environment (recommended)
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Basic Usage

```bash
# Solve a map
python3 main_solver.py maps/easy/01_linear_path.txt

# Visualize the time-expanded graph structure
python3 main_timegraph.py maps/easy/01_linear_path.txt
```

## 📄 Map File Format

Maps are defined in `.txt` files with the following structure:

```
# METADATA
NB_DRONES 2

# HUBS: name type zone x y [max_drones]
HUB start START NORMAL 0 0 5
HUB waypoint1 INTERMEDIATE NORMAL 1 0 3
HUB goal END NORMAL 2 0 2

# CONNECTIONS: source target [capacity]
CONNECTION start waypoint1 1
CONNECTION waypoint1 goal 1
```

### Data Types

**Zones (ZoneType)**:
- `NORMAL`: Requires 1 turn to traverse
- `RESTRICTED`: Requires 2 turns to traverse (automatically represented in TEG)
- `PRIORITY`: Maximizes efficiency (preferred in tie-breaking)
- `BLOCKED`: Excluded from graph

**Categories (NodeCategory)**:
- `START`: Initial point (all drones begin here)
- `INTERMEDIATE`: Waypoint
- `END`: Destination

## 🏗️ Software Architecture

### Core Components

#### Parser (`src/parser/`)
- **FileParser**: Main entry point for map validation
- **Processors**: Specialized handlers for different data sections
  - `HubProcessor`: Validates hub definitions
  - `DroneProcessor`: Processes drone count
  - `ConnectionProcessor`: Validates connections
  - `BaseProcessor`: Common validation logic

#### Data Models (`src/schemas/`)
- **Pydantic-based** type validation
- `Hub`: Location definition with capacity constraints
- `Connection`: Link definition with bandwidth
- `SimulationMap`: Complete map representation

#### Solver Engine (`src/solver/`)

**TimeGraph** (`time_graph.py`):
- Auto-constructs upon instantiation
- Builds nodes: one per (hub, time) pair
- Creates edges:
  - Movement edges: respect connection capacity
  - Wait edges: respect hub capacity
  - Restricted zones: automatically span 2 time steps
- Builds adjacency dictionary for O(1) neighbor lookup

**FlowSolver** (`flow_solver.py`):
- Consumes pre-built TimeGraph
- Implements modified Dijkstra for drone routing
- Tracks edge and node usage via `EdgeTracker`
- Generates simulation output

**Supporting Models** (`models.py`):
- `TimeNode`: (hub, time, drones_present)
- `TimeEdge`: (source, target, capacity, usage)
- `EdgeTracker`: Maintains usage statistics

#### Utilities
- `time_estimator.py`: Calculates optimal max_time = min_path_length + (nb_drones - 1)
- `dijkstra.py`: Supporting search functions

### Data Flow

```
Map File
   ↓
Parser → SimulationMap (validated)
   ↓
TimeGraph (auto-constructs)
   ├─ Creates all (hub, t) nodes
   ├─ Adds movement edges
   ├─ Adds wait edges
   └─ Builds adjacency dict
   ↓
FlowSolver
   ├─ For each drone: Modified Dijkstra
   ├─ Tracks reservations
   └─ Generates output
   ↓
Output (turn-by-turn movements)
```

## 🎯 Algorithm Details

### Modified Dijkstra with Priority

```python
cost = (time_steps, -priority_count)
```

- **Primary**: Minimize `time_steps` (turns to destination)
- **Secondary**: Maximize `priority_count` (priority zones traversed)

This lexicographic ordering ensures:
1. All drones reach the goal as quickly as possible
2. When multiple paths have equal time, prefer priority zones

### Sequential Multi-Drone Resolution

For each drone (1 to nb_drones):
1. Find shortest path from START to END using modified Dijkstra
2. Reserve all edges and nodes in the path (increment usage counters)
3. Continue to next drone

**Optimality Guarantee**: With max_time = min_path + (nb_drones - 1), even the most constrained bottleneck (1-drone capacity) has a guaranteed solution path.

## 📈 Example Execution

### Input: `maps/easy/01_linear_path.txt`

```
NB_DRONES 2

HUB start START NORMAL 0 0
HUB waypoint1 INTERMEDIATE NORMAL 1 0
HUB waypoint2 INTERMEDIATE NORMAL 2 0
HUB goal END NORMAL 3 0

CONNECTION start waypoint1 1
CONNECTION waypoint1 waypoint2 1
CONNECTION waypoint2 goal 1
```

### Output

```
D1-waypoint1
D1-waypoint2 D2-waypoint1
D1-goal D2-waypoint2
D2-goal
```

**Interpretation**:
- **Turn 0 → 1**: Drone 1 moves to waypoint1
- **Turn 1 → 2**: Drone 1 moves to waypoint2; Drone 2 moves to waypoint1
- **Turn 2 → 3**: Drone 1 arrives at goal; Drone 2 moves to waypoint2
- **Turn 3 → 4**: Drone 2 arrives at goal

## 🧪 Testing

```bash
# Run all tests
python3 -m pytest tests/ -v

# Run only graph tests
python3 -m pytest tests/test_timegraph.py -v

# Run only parser tests
python3 -m pytest tests/test_parsing.py -v

# With coverage report
python3 -m pytest tests/ --cov=src
```

**Coverage**: 62 tests covering all core functionality

## 🔍 Debugging Tools

### Visualize Time-Expanded Graph

```bash
python3 main_timegraph.py maps/easy/01_linear_path.txt
```

Shows:
- Nodes at each time step
- Movement and wait edges
- Edge capacities and usage

### Automatic Map Validation

The solver automatically:
- Validates START → END path existence
- Calculates optimal `max_time`
- Rejects unsolvable maps with clear error messages

## 📋 Dependencies

| Package | Purpose |
|---------|---------|
| `pydantic` | Type-safe data validation |
| `rich` | Colored CLI output |
| `pytest` | Test framework |
| `mypy` | Static type checking |
| `flake8` | Code linting |

## 🎓 Key Concepts

### Multi-Commodity Flow
The problem is essentially a multi-commodity flow problem where each commodity is a drone with capacity constraints at nodes and edges.

### Lexicographic Dijkstra
Uses tuples for comparison: first time, then -priority. This enables simultaneous optimization of multiple objectives.

### Greedy vs. Optimal
Sequential drone-by-drone solving is optimal when the bottleneck capacity is 1-drone, which is guaranteed by the max_time calculation.

## 📊 Map Difficulty Levels

### Easy
- Linear or simple branching flows
- Ample capacities
- Minimal restricted zones

### Medium
- Loops and deadlock traps
- Priority zones
- Critical route optimization

### Hard
- Multiple constraint layers
- Critical bottlenecks
- Combined challenges

### Challenger
- Maximum complexity
- Requires perfect algorithm
- Extreme validation

## 📝 References

- **Dijkstra's Algorithm**: Shortest path computation
- **Time-Expanded Networks**: Standard in flow and scheduling theory
- **Multi-Commodity Flow**: Optimization with multiple resources
- **Lexicographic Optimization**: Multi-objective optimization

---

**Last Updated**: February 2026
