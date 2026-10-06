import json
from pathlib import Path

from python.evaluate import evaluate, inspect_submitted_tests, parse_pytest_counts


def test_parse_pytest_counts():
    assert parse_pytest_counts("4 passed, 2 failed, 1 skipped", 1) == (4, 2, 1)
    assert parse_pytest_counts("3 passed", 0) == (3, 0, 0)
    assert parse_pytest_counts("collection failed", 2) == (0, 1, 0)


def test_inspect_submitted_tests_counts_assertions(tmp_path: Path):
    tests = tmp_path / "tests"
    tests.mkdir()
    (tests / "test_solution.py").write_text(
        "def test_a():\n    assert 1 == 1\n\ndef test_b():\n    assert 2 == 2\n",
        encoding="utf8",
    )
    result = inspect_submitted_tests(tmp_path)
    assert result["test_functions"] == 2
    assert result["assert_statements"] == 2
    assert result["syntax_errors"] == []


def test_temperature_known_good_patch_passes(tmp_path: Path):
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    (workspace / "solution.py").write_text(
        "def to_celsius(fahrenheit):\n    return (fahrenheit - 32) * 5 / 9\n",
        encoding="utf8",
    )
    output = tmp_path / "result.json"
    result = evaluate("bugfix-temperature", workspace, output)
    assert result["task_success"] is True
    assert result["functional_tests"]["passed"] == 3
    assert json.loads(output.read_text(encoding="utf8"))["task_success"] is True


def test_temperature_broken_patch_fails(tmp_path: Path):
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    (workspace / "solution.py").write_text(
        "def to_celsius(fahrenheit):\n    return fahrenheit\n",
        encoding="utf8",
    )
    result = evaluate("bugfix-temperature", workspace, tmp_path / "result.json")
    assert result["task_success"] is False
    assert result["functional_tests"]["failed"] > 0
