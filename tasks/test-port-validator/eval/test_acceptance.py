from pathlib import Path
from solution import is_valid_port


def test_reference_function_is_well_formed():
    assert is_valid_port(80) is True
    assert is_valid_port(0) is False


def test_submission_includes_test_file():
    assert (Path.cwd() / "tests" / "test_solution.py").is_file(), "create tests/test_solution.py"
