import pytest
from pathlib import Path
from src.parser.file_parser import FileParser
from src.schemas.definitions import NodeCategory


def test_parser_success_valid_map(tmp_path: Path) -> None:
    content = """nb_drones: 2
                start_hub: start 0 0
                end_hub: end 10 10
                hub: waypoint1 5 5
                connection: start-waypoint1
                connection: waypoint1-end
                """
    d_file = tmp_path / "valid_linear.txt"
    d_file.write_text(content, encoding="utf-8")

    parser = FileParser()
    simulation = parser.parse(str(d_file))

    assert simulation.nb_drones == 2
    assert "start" in simulation.hubs
    assert simulation.hubs["start"].category == NodeCategory.START
    assert "start" in simulation.connections
    assert "waypoint1" in simulation.connections["start"]


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#                                 FILE TESTS
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -


def test_file_not_found(
    capsys: pytest.CaptureFixture[str], tmp_path: Path
) -> None:
    map_path = tmp_path / "non_existent_file.txt"
    parser = FileParser()
    expected_error = "No such file"

    with pytest.raises(SystemExit):
        parser.parse(str(map_path))

    captured = capsys.readouterr()
    assert expected_error in captured.err


def test_empty_file(
    capsys: pytest.CaptureFixture[str], tmp_path: Path
) -> None:
    content = ""
    d_file = tmp_path / "empty.txt"
    d_file.write_text(content, encoding="utf-8")

    parser = FileParser()
    expected_error = "[ERROR] Empty file"

    with pytest.raises(SystemExit):
        parser.parse(str(d_file))

    captured = capsys.readouterr()
    assert expected_error in captured.err


def test_missing_separator(
    capsys: pytest.CaptureFixture[str], tmp_path: Path
) -> None:
    content = """nb_drones: 5
                start_hub start 0 0
                end_hub: goal 10 10
                """
    d_file = tmp_path / "missing_separator.txt"
    d_file.write_text(content, encoding="utf-8")

    parser = FileParser()
    expected_error = "Missing ':' separator"

    with pytest.raises(SystemExit):
        parser.parse(str(d_file))

    captured = capsys.readouterr()
    assert expected_error in captured.err


def test_garbage_variables1(
    capsys: pytest.CaptureFixture[str], tmp_path: Path
) -> None:
    content = """nb_droes: 5
                start_hub: hub 0 0
                end_hub: goal 10 10
                """
    d_file = tmp_path / "map_garbage.txt"
    d_file.write_text(content, encoding="utf-8")

    parser = FileParser()
    expected_error = "Unknown entity"

    with pytest.raises(SystemExit):
        parser.parse(str(d_file))

    captured = capsys.readouterr()
    assert expected_error in captured.err


def test_garbage_variables2(
    capsys: pytest.CaptureFixture[str], tmp_path: Path
) -> None:
    content = """nb_drones: 5
                start_hub: hub 0 0
                end_hub: goal 10 10
                garbage: goal 5 10
                """
    d_file = tmp_path / "map_garbage.txt"
    d_file.write_text(content, encoding="utf-8")

    parser = FileParser()
    expected_error = "Unknown entity"

    with pytest.raises(SystemExit):
        parser.parse(str(d_file))

    captured = capsys.readouterr()
    assert expected_error in captured.err


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#                                   TESTS DRONES
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -


def test_wrong_order(
    capsys: pytest.CaptureFixture[str], tmp_path: Path
) -> None:
    content = """start_hub: hub 0 0
                end_hub: goal 10 10
                nb_drones: 5
                """
    d_file = tmp_path / "any.txt"
    d_file.write_text(content, encoding="utf-8")

    parser = FileParser()
    expected_error = "Drones number must be defined in the first"

    with pytest.raises(SystemExit):
        parser.parse(str(d_file))

    captured = capsys.readouterr()
    assert expected_error in captured.err


def test_0_drones(capsys: pytest.CaptureFixture[str], tmp_path: Path) -> None:
    content = """nb_drones: 0
                start_hub: hub 0 0
                end_hub: goal 10 10
                """
    d_file = tmp_path / "any.txt"
    d_file.write_text(content, encoding="utf-8")

    parser = FileParser()
    expected_error = "Number of drones must be greater than 0"

    with pytest.raises(SystemExit):
        parser.parse(str(d_file))

    captured = capsys.readouterr()
    assert expected_error in captured.err


def test_missing_drones(
    capsys: pytest.CaptureFixture[str], tmp_path: Path
) -> None:
    content = """start_hub: hub 0 0
                end_hub: goal 10 10
                """
    d_file = tmp_path / "any.txt"
    d_file.write_text(content, encoding="utf-8")

    parser = FileParser()
    expected_error = "Drones number must be defined in the first"

    with pytest.raises(SystemExit):
        parser.parse(str(d_file))

    captured = capsys.readouterr()
    assert expected_error in captured.err


def test_non_numeric_drones(
    capsys: pytest.CaptureFixture[str], tmp_path: Path
) -> None:
    content = """nb_drones: five
                start_hub: hub 0 0
                end_hub: goal 10 10
                """
    d_file = tmp_path / "any.txt"
    d_file.write_text(content, encoding="utf-8")

    parser = FileParser()
    expected_error = "invalid literal for"

    with pytest.raises(SystemExit):
        parser.parse(str(d_file))

    captured = capsys.readouterr()
    assert expected_error in captured.err


def test_negative_drones(
    capsys: pytest.CaptureFixture[str], tmp_path: Path
) -> None:
    content = """nb_drones: -3
                start_hub: hub 0 0
                end_hub: goal 10 10
                """
    d_file = tmp_path / "any.txt"
    d_file.write_text(content, encoding="utf-8")

    parser = FileParser()
    expected_error = "Number of drones must be greater than 0"

    with pytest.raises(SystemExit):
        parser.parse(str(d_file))

    captured = capsys.readouterr()
    assert expected_error in captured.err


def test_duplicate_drones_line(
    capsys: pytest.CaptureFixture[str], tmp_path: Path
) -> None:
    content = """nb_drones: 3
                nb_drones: 3
                start_hub: hub 0 0
                end_hub: goal 10 10
                """
    d_file = tmp_path / "any.txt"
    d_file.write_text(content, encoding="utf-8")

    parser = FileParser()
    expected_error = "Number of drones defined more than 1 times"

    with pytest.raises(SystemExit):
        parser.parse(str(d_file))

    captured = capsys.readouterr()
    assert expected_error in captured.err


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#                                   TESTS HUBS
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -


def test_missing_start(
    capsys: pytest.CaptureFixture[str], tmp_path: Path
) -> None:
    content = """nb_drones: 5
                end_hub: goal 10 10
                hub: roof1 3 4
                """
    d_file = tmp_path / "invalid_no_start.txt"
    d_file.write_text(content, encoding="utf-8")

    parser = FileParser()
    expected_error = "Map is missing a Start Hub"

    with pytest.raises(SystemExit):
        parser.parse(str(d_file))

    captured = capsys.readouterr()
    assert expected_error in captured.err


def test_missing_end(
    capsys: pytest.CaptureFixture[str], tmp_path: Path
) -> None:
    content = """nb_drones: 5
                start_hub: start 0 0
                hub: roof1 3 4
                """
    d_file = tmp_path / "invalid_no_end.txt"
    d_file.write_text(content, encoding="utf-8")

    parser = FileParser()
    expected_error = "Map is missing an End Hub"

    with pytest.raises(SystemExit):
        parser.parse(str(d_file))

    captured = capsys.readouterr()
    assert expected_error in captured.err


def test_duplicate_starts(
    capsys: pytest.CaptureFixture[str], tmp_path: Path
) -> None:
    content = """nb_drones: 5
                start_hub: start 0 0
                start_hub: alo 0 0
                end_hub: goal 10 10
                hub: roof1 3 4
                """
    d_file = tmp_path / "any.txt"
    d_file.write_text(content, encoding="utf-8")

    parser = FileParser()
    expected_error = "Start Hub is duplicated"

    with pytest.raises(SystemExit):
        parser.parse(str(d_file))

    captured = capsys.readouterr()
    assert expected_error in captured.err


def test_duplicate_ends(
    capsys: pytest.CaptureFixture[str], tmp_path: Path
) -> None:
    content = """nb_drones: 5
                start_hub: start 0 0
                end_hub: goal 10 18
                end_hub: gol 10 10
                hub: roof1 3 4
                """
    d_file = tmp_path / "any.txt"
    d_file.write_text(content, encoding="utf-8")

    parser = FileParser()
    expected_error = "End Hub is duplicated"

    with pytest.raises(SystemExit):
        parser.parse(str(d_file))

    captured = capsys.readouterr()
    assert expected_error in captured.err


def test_invalid_name_format(
    capsys: pytest.CaptureFixture[str], tmp_path: Path
) -> None:
    content = """nb_drones: 5
                start_hub: start 0 0
                end_hub: goal 10 18
                hub: roof1-1 3 4
                """
    d_file = tmp_path / "any.txt"
    d_file.write_text(content, encoding="utf-8")

    parser = FileParser()
    expected_error = "cannot contain spaces or dashes"

    with pytest.raises(SystemExit):
        parser.parse(str(d_file))

    captured = capsys.readouterr()
    assert expected_error in captured.err


def test_invalid_name_format2(
    capsys: pytest.CaptureFixture[str], tmp_path: Path
) -> None:
    content = """nb_drones: 5
                start_hub: start 0 0
                end_hub: goal-1 10 18
                hub: roof1 3 4
                """
    d_file = tmp_path / "any.txt"
    d_file.write_text(content, encoding="utf-8")

    parser = FileParser()
    expected_error = "cannot contain spaces or dashes"

    with pytest.raises(SystemExit):
        parser.parse(str(d_file))

    captured = capsys.readouterr()
    assert expected_error in captured.err


def test_missing_coordinates(
    capsys: pytest.CaptureFixture[str], tmp_path: Path
) -> None:
    content = """nb_drones: 5
                start_hub: start 0 0
                end_hub: goal 1 1
                hub: roof1
                connection: start-roof1
                """
    d_file = tmp_path / "any.txt"
    d_file.write_text(content, encoding="utf-8")

    parser = FileParser()
    expected_error = "Missing Hub mandatory parameters"

    with pytest.raises(SystemExit):
        parser.parse(str(d_file))

    captured = capsys.readouterr()
    assert expected_error in captured.err


def test_string_coordinates(
    capsys: pytest.CaptureFixture[str], tmp_path: Path
) -> None:
    content = """nb_drones: 5
                start_hub: start 0 0
                end_hub: goal 1 1
                hub: roof1 a c
                connection: start-roof1
                """
    d_file = tmp_path / "any.txt"
    d_file.write_text(content, encoding="utf-8")

    parser = FileParser()
    expected_error = "invalid literal"

    with pytest.raises(SystemExit):
        parser.parse(str(d_file))

    captured = capsys.readouterr()
    assert expected_error in captured.err


def test_duplicated_coordinates(
    capsys: pytest.CaptureFixture[str], tmp_path: Path
) -> None:
    content = """nb_drones: 5
                start_hub: start 0 0
                end_hub: goal 1 1
                hub: roof1 1 1
                connection: start-roof1
                """
    d_file = tmp_path / "any.txt"
    d_file.write_text(content, encoding="utf-8")

    parser = FileParser()
    expected_error = "Hub coordinates duplicated"

    with pytest.raises(SystemExit):
        parser.parse(str(d_file))

    captured = capsys.readouterr()
    assert expected_error in captured.err


def test_unknown_type_zone(
    capsys: pytest.CaptureFixture[str], tmp_path: Path
) -> None:
    content = """nb_drones: 5
                start_hub: start 0 0
                end_hub: goal 1 1
                hub: roof1 1 2 [zone=error]
                connection: start-roof1
                """
    d_file = tmp_path / "any.txt"
    d_file.write_text(content, encoding="utf-8")

    parser = FileParser()
    expected_error = (
        "Hub validation failed. Input should be 'normal',"
        " 'blocked', 'restricted' or 'priority'"
    )

    with pytest.raises(SystemExit):
        parser.parse(str(d_file))

    captured = capsys.readouterr()
    assert expected_error in captured.err


def test_invalid_capacity(
    capsys: pytest.CaptureFixture[str], tmp_path: Path
) -> None:
    content = """nb_drones: 5
                start_hub: start 0 0 [max_drones=3]
                end_hub: goal 1 1
                hub: roof1 1 2
                connection: start-roof1
                """
    d_file = tmp_path / "any.txt"
    d_file.write_text(content, encoding="utf-8")

    parser = FileParser()
    expected_error = "Hub capacity must be equal or greater than"

    with pytest.raises(SystemExit):
        parser.parse(str(d_file))

    captured = capsys.readouterr()
    assert expected_error in captured.err


def test_invalid_capacity2(
    capsys: pytest.CaptureFixture[str], tmp_path: Path
) -> None:
    content = """nb_drones: 5
                start_hub: start 0 0
                end_hub: goal 1 1
                hub: roof1 1 2 [max_drones=-3]
                connection: start-roof1
                """
    d_file = tmp_path / "any.txt"
    d_file.write_text(content, encoding="utf-8")

    parser = FileParser()
    expected_error = "Input should be greater than or equal to 1"

    with pytest.raises(SystemExit):
        parser.parse(str(d_file))

    captured = capsys.readouterr()
    assert expected_error in captured.err


def test_wrong_metadata1(
    capsys: pytest.CaptureFixture[str], tmp_path: Path
) -> None:
    content = """nb_drones: 5
                start_hub: start 0 0
                end_hub: goal 1 1
                hub: roof1 1 2 [wrong
                connection: start-roof1
                """
    d_file = tmp_path / "any.txt"
    d_file.write_text(content, encoding="utf-8")

    parser = FileParser()
    expected_error = "Optional parameters must be enclosed in []"

    with pytest.raises(SystemExit):
        parser.parse(str(d_file))

    captured = capsys.readouterr()
    assert expected_error in captured.err


def test_wrong_metadata2(
    capsys: pytest.CaptureFixture[str], tmp_path: Path
) -> None:
    content = """nb_drones: 5
                start_hub: start 0 0
                end_hub: goal 1 1
                hub: roof1 1 2 [wrong_key]
                connection: start-roof1
                """
    d_file = tmp_path / "any.txt"
    d_file.write_text(content, encoding="utf-8")

    parser = FileParser()
    expected_error = "Expected key=value"

    with pytest.raises(SystemExit):
        parser.parse(str(d_file))

    captured = capsys.readouterr()
    assert expected_error in captured.err


def test_wrong_metadata3(
    capsys: pytest.CaptureFixture[str], tmp_path: Path
) -> None:
    content = """nb_drones: 5
                start_hub: start 0 0
                end_hub: goal 1 1
                hub: roof1 1 2 [wrong_key=value]
                connection: start-roof1
                """
    d_file = tmp_path / "any.txt"
    d_file.write_text(content, encoding="utf-8")

    parser = FileParser()
    expected_error = "Unknown parameter"

    with pytest.raises(SystemExit):
        parser.parse(str(d_file))

    captured = capsys.readouterr()
    assert expected_error in captured.err


def test_wrong_metadata4(
    capsys: pytest.CaptureFixture[str], tmp_path: Path
) -> None:
    content = """nb_drones: 5
                start_hub: start 0 0
                end_hub: goal 1 1
                hub: roof1 1 2 [wrong_key = wrong]
                connection: start-roof1
                """
    d_file = tmp_path / "any.txt"
    d_file.write_text(content, encoding="utf-8")

    parser = FileParser()
    expected_error = "Expected key=value"

    with pytest.raises(SystemExit):
        parser.parse(str(d_file))

    captured = capsys.readouterr()
    assert expected_error in captured.err


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#                                   CONNECTIONS
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -


def test_undefined_hub(
    capsys: pytest.CaptureFixture[str], tmp_path: Path
) -> None:
    content = """nb_drones: 5
                start_hub: start 0 0
                end_hub: goal 1 1
                connection: start-roof1
                """
    d_file = tmp_path / "any.txt"
    d_file.write_text(content, encoding="utf-8")

    parser = FileParser()
    expected_error = "is not defined"

    with pytest.raises(SystemExit):
        parser.parse(str(d_file))

    captured = capsys.readouterr()
    assert expected_error in captured.err


def test_undefined_hub2(
    capsys: pytest.CaptureFixture[str], tmp_path: Path
) -> None:
    content = """nb_drones: 5
                start_hub: start 0 0
                end_hub: goal 1 1
                hub: roof1 1 2
                connection: start-roof1
                connection: goal-roof2
                """
    d_file = tmp_path / "any.txt"
    d_file.write_text(content, encoding="utf-8")

    parser = FileParser()
    expected_error = "is not defined"

    with pytest.raises(SystemExit):
        parser.parse(str(d_file))

    captured = capsys.readouterr()
    assert expected_error in captured.err


def test_space_separator(
    capsys: pytest.CaptureFixture[str], tmp_path: Path
) -> None:
    content = """nb_drones: 5
                start_hub: start 0 0
                end_hub: goal 1 1
                hub: roof1 1 2
                connection: start roof1
                """
    d_file = tmp_path / "any.txt"
    d_file.write_text(content, encoding="utf-8")

    parser = FileParser()
    expected_error = "Invalid connection format"

    with pytest.raises(SystemExit):
        parser.parse(str(d_file))

    captured = capsys.readouterr()
    assert expected_error in captured.err


def test_extra_hub(capsys: pytest.CaptureFixture[str], tmp_path: Path) -> None:
    content = """nb_drones: 5
                start_hub: start 0 0
                end_hub: goal 1 1
                hub: roof1 1 2
                connection: start-roof2-roof1
                """
    d_file = tmp_path / "any.txt"
    d_file.write_text(content, encoding="utf-8")

    parser = FileParser()
    expected_error = "Invalid connection format"

    with pytest.raises(SystemExit):
        parser.parse(str(d_file))

    captured = capsys.readouterr()
    assert expected_error in captured.err


def test_self_loop(capsys: pytest.CaptureFixture[str], tmp_path: Path) -> None:
    content = """nb_drones: 5
                start_hub: start 0 0
                end_hub: goal 1 1
                hub: roof1 1 2
                connection: start-start
                """
    d_file = tmp_path / "any.txt"
    d_file.write_text(content, encoding="utf-8")

    parser = FileParser()
    expected_error = "Connection must be between two different hubs"

    with pytest.raises(SystemExit):
        parser.parse(str(d_file))

    captured = capsys.readouterr()
    assert expected_error in captured.err


def test_duplicate_connection(
    capsys: pytest.CaptureFixture[str], tmp_path: Path
) -> None:
    content = """nb_drones: 5
                start_hub: start 0 0
                end_hub: goal 1 1
                hub: roof1 1 2
                connection: start-roof1
                connection: roof1-start
                """
    d_file = tmp_path / "any.txt"
    d_file.write_text(content, encoding="utf-8")

    parser = FileParser()
    expected_error = "already exists"

    with pytest.raises(SystemExit):
        parser.parse(str(d_file))

    captured = capsys.readouterr()
    assert expected_error in captured.err


def test_invalid_metadata(
    capsys: pytest.CaptureFixture[str], tmp_path: Path
) -> None:
    content = """nb_drones: 5
                start_hub: start 0 0
                end_hub: goal 1 1
                hub: roof1 1 2
                connection: start-roof1 [this_is_invalid]
                """
    d_file = tmp_path / "any.txt"
    d_file.write_text(content, encoding="utf-8")

    parser = FileParser()
    expected_error = "Expected key=value"

    with pytest.raises(SystemExit):
        parser.parse(str(d_file))

    captured = capsys.readouterr()
    assert expected_error in captured.err


def test_invalid_metadata2(
    capsys: pytest.CaptureFixture[str], tmp_path: Path
) -> None:
    content = """nb_drones: 5
                start_hub: start 0 0
                end_hub: goal 1 1
                hub: roof1 1 2
                connection: start-roof1 [this_is_invali
                """
    d_file = tmp_path / "any.txt"
    d_file.write_text(content, encoding="utf-8")

    parser = FileParser()
    expected_error = "Optional parameters must be enclosed in []"

    with pytest.raises(SystemExit):
        parser.parse(str(d_file))

    captured = capsys.readouterr()
    assert expected_error in captured.err


def test_invalid_metadata3(
    capsys: pytest.CaptureFixture[str], tmp_path: Path
) -> None:
    content = """nb_drones: 5
                start_hub: start 0 0
                end_hub: goal 1 1
                hub: roof1 1 2
                connection: start-roof1 [this_is_invalid=5]
                """
    d_file = tmp_path / "any.txt"
    d_file.write_text(content, encoding="utf-8")

    parser = FileParser()
    expected_error = "Unknown parameter"

    with pytest.raises(SystemExit):
        parser.parse(str(d_file))

    captured = capsys.readouterr()
    assert expected_error in captured.err


def test_invalid_metadata4(
    capsys: pytest.CaptureFixture[str], tmp_path: Path
) -> None:
    content = """nb_drones: 5
                start_hub: start 0 0
                end_hub: goal 1 1
                hub: roof1 1 2
                connection: start-roof1 [max_link_capacity=a]
                """
    d_file = tmp_path / "any.txt"
    d_file.write_text(content, encoding="utf-8")

    parser = FileParser()
    expected_error = "Value for 'max_link_capacity' must be an integer"

    with pytest.raises(SystemExit):
        parser.parse(str(d_file))

    captured = capsys.readouterr()
    assert expected_error in captured.err


def test_invalid_metadata5(
    capsys: pytest.CaptureFixture[str], tmp_path: Path
) -> None:
    content = """nb_drones: 5
                start_hub: start 0 0
                end_hub: goal 1 1
                hub: roof1 1 2
                connection: start-roof1 [max_link_capacity=0]
                """
    d_file = tmp_path / "any.txt"
    d_file.write_text(content, encoding="utf-8")

    parser = FileParser()
    expected_error = "Connection validation failed"

    with pytest.raises(SystemExit):
        parser.parse(str(d_file))

    captured = capsys.readouterr()
    assert expected_error in captured.err


def test_invalid_metadata6(
    capsys: pytest.CaptureFixture[str], tmp_path: Path
) -> None:
    content = """nb_drones: 5
                start_hub: start 0 0
                end_hub: goal 1 1
                hub: roof1 1 2
                connection: start-roof1 [max_link_capacity=- 1]
                """
    d_file = tmp_path / "any.txt"
    d_file.write_text(content, encoding="utf-8")

    parser = FileParser()
    expected_error = "Invalid format"

    with pytest.raises(SystemExit):
        parser.parse(str(d_file))

    captured = capsys.readouterr()
    assert expected_error in captured.err


def test_invalid_metadata7(
    capsys: pytest.CaptureFixture[str], tmp_path: Path
) -> None:
    content = """nb_drones: 5
                start_hub: start 0 0
                end_hub: goal 1 1
                hub: roof1 1 2
                connection: start-roof1 [max_link_capacity=-]
                """
    d_file = tmp_path / "any.txt"
    d_file.write_text(content, encoding="utf-8")

    parser = FileParser()
    expected_error = "Value for 'max_link_capacity' must be an intege"

    with pytest.raises(SystemExit):
        parser.parse(str(d_file))

    captured = capsys.readouterr()
    assert expected_error in captured.err
