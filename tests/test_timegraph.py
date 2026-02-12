import pytest
from src.schemas.hubs import Hub
from src.schemas.connection import Connection
from src.schemas.definitions import ZoneType, NodeCategory
from src.schemas.simulation_map import SimulationMap
from src.solver.time_graph import TimeGraph
from src.solver.models import TimeNode


@pytest.fixture
def simple_simulation() -> SimulationMap:
    hub_a = Hub(
        name="A",
        category=NodeCategory.START,
        type=ZoneType.NORMAL,
        x=0,
        y=0,
        zone=ZoneType.NORMAL,
    )
    hub_b = Hub(
        name="B",
        category=NodeCategory.INTERMEDIATE,
        type=ZoneType.NORMAL,
        x=1,
        y=0,
        zone=ZoneType.NORMAL,
    )
    hub_c = Hub(
        name="C",
        category=NodeCategory.END,
        type=ZoneType.NORMAL,
        x=2,
        y=0,
        zone=ZoneType.NORMAL,
    )

    hubs = {"A": hub_a, "B": hub_b, "C": hub_c}
    connections = {
        "A": {"B": Connection(source="A", target="B", max_link_capacity=2)},
        "B": {"C": Connection(source="B", target="C", max_link_capacity=1)},
        "C": {},
    }

    return SimulationMap(nb_drones=2, hubs=hubs, connections=connections)


@pytest.fixture
def restricted_simulation() -> SimulationMap:
    hub_a = Hub(
        name="A",
        category=NodeCategory.START,
        type=ZoneType.NORMAL,
        x=0,
        y=0,
        zone=ZoneType.NORMAL,
    )
    hub_r = Hub(
        name="R",
        category=NodeCategory.INTERMEDIATE,
        type=ZoneType.RESTRICTED,
        x=1,
        y=0,
        zone=ZoneType.RESTRICTED,
    )
    hub_c = Hub(
        name="C",
        category=NodeCategory.END,
        type=ZoneType.NORMAL,
        x=2,
        y=0,
        zone=ZoneType.NORMAL,
    )

    hubs = {"A": hub_a, "R": hub_r, "C": hub_c}
    connections = {
        "A": {"R": Connection(source="A", target="R", max_link_capacity=1)},
        "R": {"C": Connection(source="R", target="C", max_link_capacity=1)},
        "C": {},
    }

    return SimulationMap(nb_drones=1, hubs=hubs, connections=connections)


@pytest.fixture
def blocked_simulation() -> SimulationMap:
    hub_a = Hub(
        name="A",
        category=NodeCategory.START,
        type=ZoneType.NORMAL,
        x=0,
        y=0,
        zone=ZoneType.NORMAL,
    )
    hub_blocked = Hub(
        name="BLOCKED",
        category=NodeCategory.INTERMEDIATE,
        type=ZoneType.BLOCKED,
        x=1,
        y=0,
        zone=ZoneType.BLOCKED,
    )
    hub_c = Hub(
        name="C",
        category=NodeCategory.END,
        type=ZoneType.NORMAL,
        x=2,
        y=0,
        zone=ZoneType.NORMAL,
    )

    hubs = {"A": hub_a, "BLOCKED": hub_blocked, "C": hub_c}
    connections = {
        "A": {
            "BLOCKED": Connection(
                source="A", target="BLOCKED", max_link_capacity=1
            )
        },
        "BLOCKED": {
            "C": Connection(source="BLOCKED", target="C", max_link_capacity=1)
        },
        "C": {},
    }

    return SimulationMap(nb_drones=1, hubs=hubs, connections=connections)


def test_time_graph_initialization(simple_simulation: SimulationMap) -> None:
    """Verify that TimeGraph builds itself
    automatically upon initialization."""
    max_time = 5
    graph = TimeGraph(simple_simulation, max_time)

    assert graph.max_time == max_time
    # Graph should be built automatically (not empty)
    expected_nodes = 3 * (max_time + 1)  # 3 hubs * 6 time steps
    assert len(graph.nodes) == expected_nodes
    assert len(graph.edges) > 0
    assert len(graph.adjacency) > 0


def test_build_graph_creates_all_nodes(
    simple_simulation: SimulationMap,
) -> None:
    """Verify that TimeGraph creates nodes
    for each hub at every time step."""
    max_time = 3
    graph = TimeGraph(simple_simulation, max_time)

    expected_nodes = 3 * (max_time + 1)
    assert len(graph.nodes) == expected_nodes

    for hub_name in ["A", "B", "C"]:
        for t in range(max_time + 1):
            assert (hub_name, t) in graph.nodes


def test_build_graph_excludes_blocked_hubs(
    blocked_simulation: SimulationMap,
) -> None:
    """Verify that TimeGraph skips creating nodes for blocked hubs."""
    max_time = 3
    graph = TimeGraph(blocked_simulation, max_time)

    for t in range(max_time + 1):
        assert ("A", t) in graph.nodes
        assert ("C", t) in graph.nodes
        assert ("BLOCKED", t) not in graph.nodes


def test_travel_time_normal_zone(simple_simulation: SimulationMap) -> None:
    """Verify that normal zones have a travel time of 1 turn."""
    graph = TimeGraph(simple_simulation, 5)
    hub_b = simple_simulation.hubs["B"]

    travel_time = graph._get_travel_time(hub_b)
    assert travel_time == 1


def test_travel_time_restricted_zone(
    restricted_simulation: SimulationMap,
) -> None:
    """Verify that restricted zones require 2 turns for traversal."""
    graph = TimeGraph(restricted_simulation, 5)
    hub_r = restricted_simulation.hubs["R"]

    travel_time = graph._get_travel_time(hub_r)
    assert travel_time == 2


def test_build_graph_creates_movement_edges(
    simple_simulation: SimulationMap,
) -> None:
    """Verify that TimeGraph creates edges between
    connected hubs with correct capacity."""
    max_time = 3
    graph = TimeGraph(simple_simulation, max_time)

    edges_a_to_b = [
        e
        for e in graph.edges
        if e.source.hub.name == "A" and e.target.hub.name == "B"
    ]

    assert len(edges_a_to_b) > 0

    for edge in edges_a_to_b:
        assert edge.source.time + 1 == edge.target.time
        assert edge.max_capacity == 2


def test_build_graph_respects_restricted_travel_time(
    restricted_simulation: SimulationMap,
) -> None:
    """Verify that edges to restricted zones
    span 2 time steps while normal edges span 1."""
    max_time = 5
    graph = TimeGraph(restricted_simulation, max_time)

    edges_a_to_r = [
        e
        for e in graph.edges
        if e.source.hub.name == "A" and e.target.hub.name == "R"
    ]

    for edge in edges_a_to_r:
        assert edge.duration == 2

    edges_r_to_c = [
        e
        for e in graph.edges
        if e.source.hub.name == "R" and e.target.hub.name == "C"
    ]

    for edge in edges_r_to_c:
        assert edge.duration == 1


def test_build_graph_creates_wait_edges(
    simple_simulation: SimulationMap,
) -> None:
    """Verify that TimeGraph creates wait
    edges for staying at the same hub."""
    max_time = 3
    graph = TimeGraph(simple_simulation, max_time)

    wait_edges = [
        e for e in graph.edges if e.source.hub.name == e.target.hub.name
    ]

    assert len(wait_edges) > 0

    for edge in wait_edges:
        assert edge.duration == 1
        assert edge.max_capacity == 1


def test_build_graph_respects_capacity(
    simple_simulation: SimulationMap,
) -> None:
    """Verify that edges maintain the correct
    capacity from connection definitions."""
    max_time = 3
    graph = TimeGraph(simple_simulation, max_time)

    edges_a_to_b = [
        e
        for e in graph.edges
        if e.source.hub.name == "A" and e.target.hub.name == "B"
    ]

    for edge in edges_a_to_b:
        assert edge.max_capacity == 2

    edges_b_to_c = [
        e
        for e in graph.edges
        if e.source.hub.name == "B" and e.target.hub.name == "C"
    ]

    for edge in edges_b_to_c:
        assert edge.max_capacity == 1


def test_build_graph_respects_max_time(
    simple_simulation: SimulationMap,
) -> None:
    """Verify that no edges extend beyond the maximum time boundary."""
    max_time = 2
    graph = TimeGraph(simple_simulation, max_time)

    for edge in graph.edges:
        assert edge.target.time <= max_time


def test_build_graph_no_edges_beyond_max_time(
    restricted_simulation: SimulationMap,
) -> None:
    """Verify that edges from restricted zones do not exceed max_time limit."""
    max_time = 3
    graph = TimeGraph(restricted_simulation, max_time)

    for edge in graph.edges:
        assert edge.target.time <= max_time


def test_time_node_creation(simple_simulation: SimulationMap) -> None:
    """Verify that TimeNode correctly stores
    hub reference, time, and zone attributes."""
    hub = simple_simulation.hubs["A"]
    node = TimeNode(hub, 0)

    assert node.hub == hub
    assert node.time == 0
    assert not node.is_priority
    assert not node.is_end


def test_time_node_equality() -> None:
    """Verify that two TimeNodes with same hub and time are equal."""
    hub1 = Hub(
        name="A",
        category=NodeCategory.START,
        type=ZoneType.NORMAL,
        x=0,
        y=0,
    )
    hub2 = Hub(
        name="A",
        category=NodeCategory.START,
        type=ZoneType.NORMAL,
        x=0,
        y=0,
    )

    node1 = TimeNode(hub1, 5)
    node2 = TimeNode(hub2, 5)

    assert node1 == node2


def test_time_node_hash() -> None:
    """Verify that TimeNodes with same hub and time have the same hash."""
    hub = Hub(
        name="A",
        category=NodeCategory.START,
        type=ZoneType.NORMAL,
        x=0,
        y=0,
    )

    node1 = TimeNode(hub, 5)
    node2 = TimeNode(hub, 5)

    assert hash(node1) == hash(node2)


def test_add_node_skips_blocked_hubs(
    blocked_simulation: SimulationMap,
) -> None:
    """Verify that _add_node does not create nodes for blocked hubs."""
    graph = TimeGraph(blocked_simulation, 5)
    blocked_hub = blocked_simulation.hubs["BLOCKED"]

    graph._add_node(blocked_hub, 0)

    assert ("BLOCKED", 0) not in graph.nodes


def test_build_graph_with_empty_connections() -> None:
    """Verify that build_graph still creates wait
    edges for hubs with no outgoing connections."""
    hub_a = Hub(
        name="A",
        category=NodeCategory.START,
        type=ZoneType.NORMAL,
        x=0,
        y=0,
    )

    hubs = {"A": hub_a}
    connections: dict[str, dict[str, Connection]] = {"A": {}}

    simulation = SimulationMap(nb_drones=1, hubs=hubs, connections=connections)
    graph = TimeGraph(simulation, 3)

    for t in range(4):
        assert ("A", t) in graph.nodes

    wait_edges = [e for e in graph.edges if e.source.hub.name == "A"]
    assert len(wait_edges) == 3


def test_nodes_have_correct_attributes(
    simple_simulation: SimulationMap,
) -> None:
    """Verify that TimeNodes store correct hub
    reference, time, and zone information."""
    graph = TimeGraph(simple_simulation, 3)

    start_node = graph.nodes[("A", 0)]
    assert start_node.hub.name == "A"
    assert start_node.time == 0
    assert not start_node.is_priority

    end_node = graph.nodes[("C", 1)]
    assert end_node.hub.name == "C"
    assert end_node.time == 1
    assert end_node.is_end


def test_graph_with_priority_zone() -> None:
    """Verify that TimeNodes correctly identify priority zones."""
    hub_p = Hub(
        name="P",
        category=NodeCategory.INTERMEDIATE,
        type=ZoneType.PRIORITY,
        x=0,
        y=0,
        zone=ZoneType.PRIORITY,
    )

    hubs = {"P": hub_p}
    connections: dict[str, dict[str, Connection]] = {"P": {}}

    simulation = SimulationMap(nb_drones=1, hubs=hubs, connections=connections)
    graph = TimeGraph(simulation, 2)

    priority_node = graph.nodes[("P", 0)]
    assert priority_node.is_priority


def test_complex_multi_path_graph() -> None:
    """Verify that build_graph correctly handles multiple
    paths and respects time constraints."""
    hub_a = Hub(
        name="A",
        category=NodeCategory.START,
        type=ZoneType.NORMAL,
        x=0,
        y=0,
    )
    hub_b = Hub(
        name="B",
        category=NodeCategory.INTERMEDIATE,
        type=ZoneType.NORMAL,
        x=1,
        y=0,
    )
    hub_c = Hub(
        name="C",
        category=NodeCategory.INTERMEDIATE,
        type=ZoneType.NORMAL,
        x=1,
        y=1,
    )
    hub_d = Hub(
        name="D",
        category=NodeCategory.END,
        type=ZoneType.NORMAL,
        x=2,
        y=0,
    )

    hubs = {"A": hub_a, "B": hub_b, "C": hub_c, "D": hub_d}
    connections = {
        "A": {
            "B": Connection(source="A", target="B", max_link_capacity=2),
            "C": Connection(source="A", target="C", max_link_capacity=1),
        },
        "B": {"D": Connection(source="B", target="D", max_link_capacity=1)},
        "C": {"D": Connection(source="C", target="D", max_link_capacity=1)},
        "D": {},
    }

    simulation = SimulationMap(nb_drones=2, hubs=hubs, connections=connections)
    graph = TimeGraph(simulation, 4)

    assert len(graph.nodes) == 4 * 5

    edges_from_a = [e for e in graph.edges if e.source.hub.name == "A"]
    assert len(edges_from_a) > 0

    edges_to_d = [e for e in graph.edges if e.target.hub.name == "D"]
    assert len(edges_to_d) > 0

    for edge in graph.edges:
        assert edge.target.time <= 4


def test_edge_duration_calculation(simple_simulation: SimulationMap) -> None:
    """Verify that edge duration is correctly
    calculated as the time difference between nodes."""
    graph = TimeGraph(simple_simulation, 5)

    edges = graph.edges
    for edge in edges:
        expected_duration = edge.target.time - edge.source.time
        assert edge.duration == expected_duration


def test_no_edges_from_nonexistent_nodes(
    simple_simulation: SimulationMap,
) -> None:
    """Verify that all edges reference nodes that exist in the graph."""
    graph = TimeGraph(simple_simulation, 2)

    for edge in graph.edges:
        assert edge.source in graph.nodes.values()
        assert edge.target in graph.nodes.values()
