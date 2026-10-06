# Agentic Coding Assistant Benchmark

A ready-to-run MVP for controlled, task-based comparisons of GitHub Copilot, Cursor, Claude Code, and Codex. It includes a TypeScript REST API, six sample tasks, isolated per-run workspaces, hidden acceptance checks, and a Python evaluator.

## What is included

- **Six task categories:** bug fix, feature implementation, security remediation, refactoring, test writing, and repository reasoning.
- **Fresh workspace per run:** every run starts by copying only that task's starter files. Evaluator tests are not copied into the task workspace, but this local MVP is not a hardened secrecy boundary if an assistant has access to the parent filesystem.
- **Manual assistant workflow:** the API creates a workspace and standard prompt. Open the workspace using whichever assistant you are evaluating, complete the task, then ask the API to evaluate it.
- **Automated grading:** pytest acceptance checks, Python compilation, optional Ruff lint output, timing, and JSON results.
- **No claims about a universal winner:** this is a small educational MVP and sample task suite, not a production benchmark or a statistically powered study.

The products are deliberately marked `manual`. This repository does not pretend that their different proprietary interfaces and authentication methods are interchangeable or automatically invoke your accounts. You must record exact product/version and operator interventions. You do not need to write tests or task code to try the included sample suite.

## Requirements

- Node.js 20 or newer
- Python 3.11 or newer
- Git
- npm

Docker is not required by the current local-MVP workflow. Each assistant run gets a separate directory, but manual runs are **not a security sandbox**. Do not open untrusted or destructive assistant-generated code on a machine with sensitive files mounted. The evaluator executes submitted Python in a subprocess. For research-grade/untrusted tasks, run the evaluator and assistants in disposable non-root containers/VMs with resource and network limits.

## Install and start

```bash
npm install
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
npm run dev
```

The API listens at `http://127.0.0.1:3000` by default. Set `PORT` to change the port or `HOST` to override the bind address. Keep it on a trusted local machine; no authentication is enabled.

Check health and task list:

```bash
curl http://127.0.0.1:3000/health
curl http://127.0.0.1:3000/tasks
```

## Run one assistant on one task

Create a new clean run (replace assistant ID with `github-copilot`, `cursor`, `claude-code`, or `codex`):

```bash
curl -s http://127.0.0.1:3000/runs \\
  -H 'content-type: application/json' \\
  -d '{"taskId":"bugfix-temperature","assistantId":"claude-code"}'
```

The response gives the run ID, exact task prompt, and workspace path. Open that path in the product you are evaluating and give the assistant the prompt verbatim. The included tasks are toy examples, so do not use these six tasks as conclusive evidence about real-world software engineering performance.

When the assistant finishes, run evaluation using the returned UUID:

```bash
curl -s -X POST http://127.0.0.1:3000/runs/RUN_ID/evaluate
```

The response includes `task_success`, test counts, compilation status, Ruff output, and paths to saved artifacts under `runs/RUN_ID/`. The assistant output is never automatically considered correct because it says it finished.

To inspect past run records:

```bash
curl http://127.0.0.1:3000/runs
curl http://127.0.0.1:3000/runs/RUN_ID
```

There is intentionally no route to disclose hidden tests. The only public task endpoint returns the task statement and metadata.

## Included tasks

| ID | Category | Goal |
|---|---|---|
| `bugfix-temperature` | Bug fix | Correct Fahrenheit-to-Celsius calculation |
| `feature-slugify` | Feature | Implement slug normalization |
| `security-shell-arg` | Security remediation | Avoid shell injection in subprocess invocation |
| `refactor-user-parser` | Refactoring | Validate and normalize a user record |
| `test-port-validator` | Test writing | Write substantive pytest coverage for a port validator |
| `repo-reasoning` | Repository reasoning | Document configuration source precedence |

For `test-port-validator`, success requires at least three submitted test functions, at least five Python `assert` statements, valid syntax, and passing grader checks. This is a simple automatic proxy for test quality; human review is still recommended.

## Evaluation details and limitations

- Task success for ordinary tasks means all hidden acceptance checks pass. For the testing task it also requires the simple test-quality threshold documented above.
- Each task's evaluator tests are stored in `tasks/<task-id>/eval/`; only `starter/` is copied into a run workspace. Keep evaluator tests private if you later publish a benchmark variant.
- Baseline regression testing, a second blinded reviewer, cost/API usage, token counts, and Semgrep security analysis are **not yet implemented** in this MVP. Ruff is a quality signal, not a security scanner. Do not describe unavailable metrics as measured.
- The API returns one run at a time. For the paper, run every assistant on the same task prompt with a fresh workspace, rotate/randomize run order, repeat pairs if possible, and record product version, model label, date, access mode, human interventions, and any failed runs.
- Do not compare results across different task mixes without showing category-level results. Repeated runs on the same task are not independent task instances.
- Task repositories are synthetic fixtures written for this educational scaffold; they are not SWE-bench tasks. The tool does not ship external benchmark data or reference solutions.

## Development checks

```bash
npm run check
python -m compileall -q python tasks
python -m pytest -q tasks/*/eval
```

These commands run the framework unit tests and check Python syntax. The framework tests include known-good and intentionally broken patches to verify the grader. The benchmark task graders themselves are run by the evaluator after an assistant produces a patch.

## Result storage

Each run produces a `run.json`, `prompt.md`, `patch.diff`, and `result.json` in `runs/<uuid>/`. Run directories are git-ignored by default. Back up results separately if you need them for the paper. Do not publish API keys, credentials, private code, or task material you cannot redistribute.

## Security and research integrity

This is a local student prototype, not a hardened multi-user service. It binds to localhost by default and has no authentication. Keep it local. Use disposable, least-privileged environments for untrusted assistant output. Keep the grader separate from the agent workspace. Define exclusions and analysis rules before seeing final outcomes, report numerators/denominators, and never fabricate results.

## Project structure

```text
src/                     TypeScript API, task catalog, run manager
python/evaluate.py       Python grading entry point
tasks/<id>/starter/      Files visible to the coding assistant
tasks/<id>/eval/         Evaluator-only task checks
runs/                    Generated run artifacts (git-ignored)
```

## License

MIT. Review external benchmark/tool terms before extending this scaffold with external datasets or repositories.
