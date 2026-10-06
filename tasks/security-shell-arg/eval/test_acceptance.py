from unittest.mock import patch
from solution import run_report


def test_runs_without_shell_and_passes_argument_as_single_value():
    with patch("solution.subprocess.run") as mocked:
        expected = object()
        mocked.return_value = expected
        result = run_report("report; touch /tmp/not-run")
    assert result is expected
    args, kwargs = mocked.call_args
    assert args[0] == ["report-tool", "report; touch /tmp/not-run"]
    assert kwargs.get("shell", False) is False
    assert kwargs.get("check") is False
    assert kwargs.get("capture_output") is True
