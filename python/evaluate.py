#!/usr/bin/env python3
"""Run hidden task checks against a workspace and emit a JSON result."""
from __future__ import annotations

import argparse
import ast
import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TASKS = ROOT / "tasks"


def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


def run_command(command: list[str], cwd: Path, timeout: int = 60, extra_env: dict[str, str] | None = None) -> dict:
    started = time.monotonic()
    env = os.environ.copy()
    if extra_env:
        env.update(extra_env)
    try:
        result = subprocess.run(command, cwd=cwd, env=env, capture_output=True, text=True, timeout=timeout, check=False)
        return {"command": command, "exit_code": result.returncode, "stdout": result.stdout[-12000:], "stderr": result.stderr[-12000:], "duration_seconds": round(time.monotonic() - started, 3), "timed_out": False}
    except subprocess.TimeoutExpired as exc:
        return {"command": command, "exit_code": 124, "stdout": str(exc.stdout or "")[-12000:], "stderr": str(exc.stderr or "")[-12000:], "duration_seconds": round(time.monotonic() - started, 3), "timed_out": True}


def parse_pytest_counts(output: str, exit_code: int) -> tuple[int, int, int]:
    counts = {key: 0 for key in ("passed", "failed", "skipped", "error")}
    for key in counts:
        matches = re.findall(rf"(\d+) {key}", output)
        if matches:
            counts[key] = int(matches[-1])
    if exit_code and counts["failed"] == 0 and counts["error"] == 0:
        counts["error"] = 1
    return counts["passed"], counts["failed"] + counts["error"], counts["skipped"]


def inspect_submitted_tests(workspace: Path) -> dict:
    candidates = list((workspace / "tests").glob("test_*.py")) if (workspace / "tests").exists() else []
    functions = 0
    assertions = 0
    syntax_errors: list[str] = []
    for file in candidates:
        try:
            tree = ast.parse(file.read_text(encoding="utf8"))
        except (SyntaxError, UnicodeDecodeError) as exc:
            syntax_errors.append(f"{file.name}: {exc}")
            continue
        functions += sum(isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name.startswith("test_") for node in ast.walk(tree))
        assertions += sum(isinstance(node, ast.Assert) for node in ast.walk(tree))
    return {"test_files": [str(p.relative_to(workspace)) for p in candidates], "test_functions": functions, "assert_statements": assertions, "syntax_errors": syntax_errors}


def evaluate(task_id: str, workspace: Path, out: Path) -> dict:
    task_dir = TASKS / task_id
    eval_dir = task_dir / "eval"
    if not task_dir.is_dir() or not eval_dir.is_dir() or not workspace.is_dir():
        raise ValueError("unknown task or workspace")
    hidden_tests = sorted(eval_dir.glob("test_*.py"))
    if not hidden_tests:
        raise ValueError(f"no evaluator tests found for {task_id}")
    started_at = utcnow()
    pythonpath = str(workspace) + os.pathsep + os.environ.get("PYTHONPATH", "")
    test_env = {"PYTHONPATH": pythonpath}
    py_compile = run_command([sys.executable, "-m", "compileall", "-q", "."], workspace, timeout=30)
    pytest_command = [sys.executable, "-m", "pytest", "-q", "--disable-warnings", *[str(p) for p in hidden_tests]]
    pytest = run_command(pytest_command, workspace, timeout=90, extra_env=test_env)
    passed, failed, skipped = parse_pytest_counts(pytest["stdout"] + "\n" + pytest["stderr"], pytest["exit_code"])
    submitted_tests = None
    submitted_tests_run = None
    submitted_tests_pass = True
    if task_id == "test-port-validator":
        submitted_tests = inspect_submitted_tests(workspace)
        submitted_tests_run = run_command([sys.executable, "-m", "pytest", "-q", "tests/test_solution.py"], workspace, timeout=60, extra_env=test_env)
        submitted_tests_pass = submitted_tests_run["exit_code"] == 0
    ruff = run_command([sys.executable, "-m", "ruff", "check", ".", "--output-format", "json"], workspace, timeout=30)
    lint_findings = []
    try:
        lint_findings = json.loads(ruff["stdout"] or "[]") if ruff["stdout"].strip() else []
    except json.JSONDecodeError:
        lint_findings = [{"message": (ruff["stdout"] + ruff["stderr"])[-2000:]}]
    if submitted_tests is not None:
        quality_pass = submitted_tests["test_functions"] >= 3 and submitted_tests["assert_statements"] >= 5 and not submitted_tests["syntax_errors"] and submitted_tests_pass
    else:
        quality_pass = True
    test_pass = pytest["exit_code"] == 0 and failed == 0 and passed > 0
    task_success = test_pass and py_compile["exit_code"] == 0 and quality_pass
    result = {
        "schema_version": "1.0", "task_id": task_id, "workspace": str(workspace.resolve()),
        "started_at": started_at, "finished_at": utcnow(), "task_success": task_success,
        "functional_tests": {"passed": passed, "failed": failed, "skipped": skipped, "all_passed": test_pass},
        "compile": {"passed": py_compile["exit_code"] == 0, **py_compile},
        "quality": {"ruff_available": "No module named ruff" not in (ruff["stderr"] + ruff["stdout"]), "ruff_exit_code": ruff["exit_code"], "new_findings_not_baselined": lint_findings},
        "submitted_test_quality": submitted_tests,
        "submitted_tests_execution": submitted_tests_run,
        "commands": {"pytest": pytest, "ruff": ruff},
        "notes": ["Static checks are signals, not proof of maintainability or security.", "Security scanning is not configured by default; install and configure Semgrep before reporting SAST results."],
    }
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2) + "\n", encoding="utf8")
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--task", required=True)
    parser.add_argument("--workspace", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    try:
        result = evaluate(args.task, args.workspace.resolve(), args.out.resolve())
    except Exception as exc:
        print(json.dumps({"error": str(exc)}), file=sys.stderr)
        return 2
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
