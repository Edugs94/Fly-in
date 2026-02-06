import pytest
import os
from src.parser.file_parser import FileParser
from src.schemas.definitions import NodeCategory


def test_parser_success_valid_map():
    map_path = os.path.join("tests", "testmaps", "valid_linear.txt")
    parser = FileParser()

    simulation = parser.parse(map_path)

    assert simulation.nb_drones == 2
    assert "start" in simulation.hubs
    assert simulation.hubs["start"].category == NodeCategory.START

    assert "start" in simulation.graph
    assert "waypoint1" in simulation.graph["start"]
    assert simulation.graph["start"]["waypoint1"]["cost"] == 1


def test_file_not_found(capsys):
    map_path = os.path.join("tests", "testmaps", "file_not_found.txt")
    parser = FileParser()
    expected_error = ("[ERROR] Error reading input file: No such file")

    with pytest.raises(SystemExit):
        parser.parse(map_path)

    captured = capsys.readouterr()
    assert expected_error in captured.err


def test_parser_failure_missing_start_hub(capsys):
    map_path = os.path.join("tests", "testmaps", "invalid_no_start.txt")
    parser = FileParser()
    expected_error = "[ERROR] Map is missing a Start Hub."

    with pytest.raises(SystemExit):
        parser.parse(map_path)

    captured = capsys.readouterr()
    assert expected_error in captured.err


def test_parser_failure_missing_end_hub(capsys):
    map_path = os.path.join("tests", "testmaps", "invalid_no_end.txt")
    parser = FileParser()
    expected_error = "[ERROR] Map is missing an End Hub."

    with pytest.raises(SystemExit):
        parser.parse(map_path)

    captured = capsys.readouterr()
    assert expected_error in captured.err
