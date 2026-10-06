# Project Playbook: Agentic Coding Assistants

## What your group is actually building

Aapka project **sirf Copilot, Cursor, Claude Code aur Codex ka feature-comparison chart nahi** hai. Aapko do connected outputs banane hain:

1. **A small, reproducible benchmarking platform** that gives the same software-engineering task and repository snapshot to each assistant, saves what happened, then tests each resulting code patch.
2. **A six-page IEEE-style comparative research paper** that explains the method, reports the measured results, and discusses quality, security, efficiency, and limitations.

The platform is the practical project. The paper is the evidence-based explanation of what you built and learned. Do not write results, rankings, or numerical conclusions before running the experiments.

## Recommended project scope

Build a backend/CLI prototype, not a large website. Your synopsis explicitly says a frontend is not required. Use TypeScript/Node.js for run management and REST endpoints, Docker for disposable task workspaces, and a Python evaluation harness for tests and analysis.

For a feasible first study, use **12–18 repository tasks**. Cover six task categories: bug fixing, feature implementation, refactoring, test creation/improvement, security remediation, and repository-level reasoning. Include more than one difficulty where possible. Run every task with all four assistants. Aim for two independent runs per assistant-task pair if time and tool access permit. That means:

- Minimum pilot: 6 tasks × 4 assistants × 1 run = 24 runs.
- Feasible MVP: 12 tasks × 4 assistants × 2 runs = 96 runs.
- Stronger study: 18 tasks × 4 assistants × 2 runs = 144 runs.

These are planning targets, not universal sample-size guarantees. If access, time, or cost prevents the stronger design, complete the smaller balanced study and describe it as exploratory. Do not claim statistical certainty from a small sample. Do not attempt to run the entire 500-instance SWE-bench Verified benchmark as your first implementation. The official benchmark documentation lists multiple variants, including 500 Verified instances and a smaller 534-instance Lite set; these require careful setup and should be an optional extension, not a prerequisite for the prototype [4].

Start with **Python repositories/tasks** for the first version. This keeps dependency installation and the evaluation harness manageable. State clearly that results may not generalize to other languages.

## Research questions to use

Use a small set of answerable questions:

- **RQ1 — Functional performance:** How does task completion differ among the four assistants, and does it vary by task category or difficulty?
- **RQ2 — Efficiency and oversight:** How do elapsed time, iterations, tool activity, and human intervention differ across assistants and tasks?
- **RQ3 — Quality and risk:** What test regressions, static-analysis issues, security findings, and maintainability concerns appear in the generated patches?
- **RQ4 — Failure modes:** What recurring errors occur, such as misunderstanding requirements, editing the wrong files, incomplete implementation, dependency problems, repeated failed attempts, or regressions?

The closest prior study in your synopsis compares agents using task-stratified real-world pull-request acceptance data and reports that task type matters substantially. Your study should say how it differs: you will use **controlled task/repository snapshots and post-run automated testing**, rather than treating historical PR acceptance as a direct measure of code correctness [1]. This is a proposed distinction; make sure your final method really implements it.

## Step-by-step work plan

### Step 1 — Freeze the experimental question and exact products

Write a one-page protocol before coding. Identify exactly what each product means in your experiment. Record product name, interface (IDE, terminal, web, or API), model/version if exposed, subscription or access tier, enabled agent mode, date, and settings. “Codex” by itself is ambiguous; specify the exact Codex application or CLI you tested.

Compare the **usable assistant systems**, not the underlying foundation models, unless you can independently control the model. Their context windows, tools, interfaces, and autonomy may differ. Do not claim that your results prove one underlying model is better.

Decide whether each assistant can be run through a supported API/CLI. Some products may need a human operator in the official interface. That is acceptable for a prototype if you use a strict, logged manual adapter. Do not secretly use unsupported automation to make one product easier to operate than another.

### Step 2 — Create the task set

For each task, prepare a clean repository snapshot at a fixed commit. Write a concise issue statement that all assistants receive verbatim. Do not give one assistant extra hints. Record task category, difficulty, language, expected behavior, dependencies, time limit, and source/license.

Each task should have:

- A repository URL or locally archived source, exact commit hash, and license.
- A user-facing issue statement with acceptance criteria.
- Existing tests that pass before the task begins.
- New acceptance tests that fail on the unmodified baseline and pass when the task is correctly solved.
- A set of regression tests that should continue to pass.
- A known-good reference patch used only to validate the task setup, not shown to assistants.
- A difficulty label assigned before running assistants, with a short reason.

Store hidden evaluation tests outside the assistant’s writable repository. Otherwise, an assistant could modify or inspect the grader. Run the tests after the agent session in a separate evaluation step.

Use small, understandable tasks for your custom benchmark. If you reuse SWE-bench, pin the dataset/version and repository commit. SWE-bench provides structured issue, commit, patch, and test information; do not expose a reference patch or hidden tests during a run [4].

### Step 3 — Build the minimal runner

Implement one run at a time first. Avoid building a complicated dashboard. The minimum system should:

1. Accept a task ID and assistant ID.
2. Create a fresh workspace from the task’s fixed commit.
3. Save a run ID, start time, configuration, and task metadata.
4. Invoke the assistant through an adapter or guide a human operator through the same recorded procedure.
5. Enforce a timeout and record any available interaction/iteration data.
6. Save the final patch, stdout/stderr or session log, exit status, and end time.
7. Run the evaluator against that patch.
8. Save the machine-readable result and a human-readable summary.

The assistant should not be allowed to change the evaluator, task manifest, or other assistants’ workspaces. Each run gets a new copy. Keep credentials out of the repository and out of the code-execution container.

### Step 4 — Implement adapters

Use a shared interface so the rest of the system does not care which product is being used. Conceptually, each adapter needs `prepare(task, workspace)`, `run(prompt, timeout)`, and `collect(workspace)` operations. Return a common record containing the final diff, timestamps, available logs, and any available tool-use information.

For an assistant with a supported CLI/API, call that documented interface. For a product that can only be run in an editor, provide a manual procedure: operator opens the assigned clean workspace, pastes the standard prompt, allows the specified tools, stops at the same timeout, and exports the patch/log. Record that run mode was manual. Do not compare a fully autonomous run to a heavily coached run without marking the difference.

### Step 5 — Implement the evaluator

The evaluator should run in a separate container or process after the assistant stops. It should:

1. Verify the patch is present and syntactically valid.
2. Check that the patch does not edit hidden tests or evaluation scripts.
3. Install pinned dependencies from a lock file or prepared image.
4. Run the pre-existing regression tests.
5. Run acceptance tests.
6. Run lint/static quality checks.
7. Run security scanning.
8. Compare outputs with the baseline and save test logs and tool versions.

For Python, a practical starting point is `pytest`, Ruff, and Semgrep. Use the matching language tools if you later add JavaScript/TypeScript tasks. Pin versions in configuration and store the exact commands. Count only **new** warnings/findings relative to the baseline when possible.

### Step 6 — Store every run reproducibly

Use JSON or JSONL rather than manual spreadsheet-only recording. Save source/task manifests, run configs, logs, patches, test results, static/security results, and environment information. Keep secrets, private repositories, and user data out of public artifacts. Document licenses and respect benchmark terms.

### Step 7 — Test your framework before testing assistants

Run the platform against deliberately simple fixtures:

- A known patch that should pass the hidden acceptance tests.
- An empty patch that should fail acceptance tests.
- A patch that breaks an existing test and should be flagged as a regression.
- A patch that edits a forbidden file and should be rejected or flagged.
- A timeout case that should stop cleanly and still save partial logs.
- A rerun of the same configuration that should produce a new run ID without overwriting the first result.

Only start the comparative study once these checks work.

### Step 8 — Run the pilot, correct the protocol, then freeze it

Run one or two tasks with each assistant. The pilot checks that the prompts, adapters, test commands, Docker image, and result schema work. If you change the protocol after seeing pilot results, document the change and do not mix pilot runs into final results unless they were rerun under the frozen protocol.

Before final runs, publish or timestamp an experiment protocol in the repository. Randomize assistant order for each task where practical. Give each assistant a fresh workspace. Do not let a later assistant see a prior assistant’s patch. Use the same prompt, repository state, allowed internet/dependency access, and time limit as far as the products permit. Record every unavoidable difference.

### Step 9 — Run and review all results

Run all task-assistant pairs and save the artifacts. Have two group members independently inspect patches without seeing the assistant name if feasible. Use a fixed short rubric, resolve disagreements, and report that human scoring involves judgment. Classify failures using the taxonomy below.

### Step 10 — Analyze and write

Generate tables and plots directly from the saved JSONL records. Report sample counts and missing data. Compare assistants within the same tasks/categories, rather than only comparing overall averages. Report raw counts and uncertainty. Treat repeated runs on the same task as repeated measurements, not as entirely new independent tasks. With a small task set, emphasize descriptive results and effect sizes rather than strong significance claims.

### Step 11 — Package the submission

Submit the code, task manifests, instructions, a small safe example task, anonymized result data where permitted, the paper, and a short demo. Include exact commands and environment prerequisites. A reviewer should be able to run the framework on the example task without having access to your paid assistant accounts.

## What to code

A reasonable repository layout is:

```text
agent-benchmark/
  README.md
  package.json
  tsconfig.json
  src/
    api/                 # REST routes: tasks, assistants, runs, results
    orchestrator/        # run lifecycle, timeouts, workspace management
    adapters/            # copilot, cursor, claude-code, codex, manual adapter
    storage/             # JSONL/file persistence in MVP
    schemas/             # shared request/result types
  evaluator/
    run_eval.py          # separate evaluator entry point
    tests/               # acceptance and regression test runner
    quality/             # lint/complexity/coverage collection
    security/            # Semgrep invocation and normalization
  tasks/
    task-index.json
    task-001/             # issue text and public metadata only
      task.yaml
      repo-info.json
  eval-private/           # hidden tests; not mounted into agent workspace
  runs/                   # generated per-run JSON, patch, logs, reports
  analysis/
    summarize.py
    make_tables.py
  docker/
    agent-workspace.Dockerfile
    evaluator.Dockerfile
```

For the MVP, use local JSON/JSONL files rather than a database. Add PostgreSQL only if concurrent users or querying needs justify it. Do not add a frontend unless your guide specifically requires one.

Suggested REST endpoints:

```text
GET    /health
GET    /tasks
GET    /tasks/:taskId
GET    /assistants
POST   /runs                  # create/execute one run
GET    /runs/:runId            # status and metadata
GET    /runs/:runId/artifacts  # artifact manifest/paths
POST   /runs/:runId/evaluate   # run evaluator after patch is frozen
GET    /results?taskId=&assistantId=
```

Important controls: validate inputs, use generated run IDs, prevent path traversal, set a timeout, capture subprocess output safely, never shell-concatenate untrusted task text, and write run data atomically so interrupted jobs do not corrupt previous results.

Example task metadata:

```yaml
id: py-bug-001
category: bug_fix
language: python
difficulty: medium
repository: ./repositories/example-project
base_commit: "<exact-git-commit>"
issue_file: issue.md
setup_profile: python-pytest-v1
time_limit_seconds: 1800
network_policy: dependencies_preloaded
acceptance_test_suite: py-bug-001-hidden
regression_test_command: "pytest -q"
quality_profile: python-v1
security_profile: semgrep-python-v1
license: MIT
```

Keep the hidden test suite’s actual path and contents outside the agent-visible task folder. The YAML above names a suite but does not expose it.

## Coding metrics: what to calculate and how

Do not reduce everything to one “AI score.” Report the separate outcomes below. For each metric, define its denominator and when it is measured.

| Dimension | Metric | How to calculate/report |
|---|---|---|
| Functional completion | Task success rate | Number of runs passing all required acceptance tests ÷ valid runs. Also show numerator/denominator and a confidence interval. |
| Partial functionality | Acceptance-test pass fraction | Passed acceptance tests ÷ total acceptance tests for that task. Keep task-specific test counts visible. |
| Regression | Regression rate | Runs with at least one formerly passing regression test failing after the patch ÷ runs with a valid patch. Also report failing test counts. |
| Efficiency | Wall-clock time | End timestamp − start timestamp. Report median and spread; exclude setup time only if the same exclusion rule is used for all tools. |
| Effort | Iterations/tool calls | Count only if the product exposes a reliable count. Mark unavailable rather than estimating. Define what counts as an iteration. |
| Human oversight | Intervention count and minutes | Count prompts, corrections, manual edits, or restarts from the operator. Measure human-active minutes separately from elapsed time. |
| Cost | API usage/cost | Report only if the product provides reliable usage and price data for the exact run. Otherwise state “not available”; do not invent estimates. |
| Code quality | New lint/static warnings | Post-run findings minus baseline findings, categorized by rule/severity. Do not treat a clean linter as proof of good design. |
| Maintainability | Complexity and review rubric | Report change in complexity for touched functions where the tool supports it. Use a predefined human rubric for clarity, scope, tests, and maintainability; use two raters if possible. |
| Security | New SAST findings | Count findings introduced by the patch by severity and rule; compare against baseline and manually validate important findings. Separate false positives. |
| Stability | Run-to-run variation | Show how outcomes vary across repeated runs for the same task and assistant. |
| Failure modes | Coded failure labels | Count runs with requirement misunderstanding, wrong repository context, incomplete work, dependency failure, repeated failed attempts, unsafe change, or regression. Allow multiple labels per run. |

Use exact names for tests and tools. If a task has no valid baseline or its tests are broken, mark it invalid and explain the exclusion; do not silently discard it after seeing which assistant failed.

A compact primary metric set for the paper is: **all-tests-passing task success, regression occurrence, wall-clock time, human intervention, new security findings, and blinded code-review score**. Treat other static metrics as secondary signals.

## Testing plan

### Framework tests

- **Unit tests:** task/result schema validation, run ID generation, timeout logic, metric calculations, path validation, and JSON serialization.
- **Adapter contract tests:** use a fake assistant adapter to test success, empty patch, error exit, timeout, and partial logs. Do not consume real assistant calls in unit tests.
- **Integration tests:** start a task workspace, apply a sample patch, invoke the evaluator, and confirm the saved result includes tests, quality/security outputs, and artifact paths.
- **Isolation tests:** confirm each run starts from the same base commit; agents cannot access hidden tests or alter the evaluator; a previous run’s files do not appear in the next run; credentials are not present in task containers.
- **Failure-recovery tests:** terminate a run midway and verify that its partial state is marked failed/interrupted without overwriting another run.
- **Reproducibility test:** run the same known fixture twice and compare environment metadata and metric calculation. Agent output itself may vary; reproducibility means the procedure and grader are stable, not that stochastic tools produce identical code.

### Task validation tests

Before any assistant evaluation, check that the unmodified repository passes the baseline regression suite, fails the new acceptance tests, and that the reference patch passes both. This “baseline fails / reference solution passes” check prevents broken tasks from contaminating the study.

### Security precautions

Treat assistant-produced code and shell commands as untrusted. Use disposable workspaces, non-root containers where possible, CPU/memory/time limits, and no personal credentials. Pre-cache dependencies or record network policy so one assistant is not advantaged by different package access. Do not run arbitrary outputs on a personal laptop with private files mounted into the container.

## Fair-comparison protocol

For every experiment, keep an experiment manifest with:

- Assistant product/interface, version or model label if exposed, settings, date, and access tier.
- Task ID, repository commit, prompt version, time limit, and allowed tools.
- Workspace image digest, runtime/tool versions, dependency policy, and evaluation version.
- Whether the run was automated or human-operated, and the operator’s intervention count.
- Exclusions, interruptions, and reason for each.

Important: product interfaces and autonomy differ. Capture those differences as part of the study rather than pretending they do not exist. A task-stratified study of historical GitHub pull requests is useful context, but PR acceptance is affected by task mix and repository review practices; it is not identical to a controlled hidden-test pass rate [1]. AIDev is useful for studying agentic contributions in real repositories, but your custom controlled runs answer a different question [2] [3].

## Statistical and analysis plan

Keep the analysis modest and transparent.

- Report raw counts (`passed / total`) alongside every percentage.
- Give success results by assistant, category, and difficulty. Include pooled results only as a secondary summary.
- Use paired comparisons because the same tasks are given to each assistant. For a small sample, show task-level outcomes and bootstrap confidence intervals clustered by task, or use an appropriate paired test if your supervisor approves it.
- For binary paired outcomes, discuss McNemar’s test only when there are enough informative discordant pairs. For continuous paired outcomes such as elapsed time, consider a paired permutation test or Wilcoxon signed-rank test if assumptions and sample size make it reasonable.
- Report effect sizes and uncertainty. If you test many comparisons, disclose the number and control for multiple comparisons or clearly label them exploratory.
- Do not count repeated trials of the same task as independent task instances. Treat trials as nested within task when summarizing uncertainty.
- Avoid declaring “winner” based only on a pooled mean. An assistant may be strong on one task type and weak on another.

The closest prior study explicitly stratifies PR outcomes by task type and warns against treating all task workloads as interchangeable [1]. Use this as a reason to report category-level results. Its observational GitHub data should not be directly compared numerically with your controlled task results.

## Failure taxonomy for manual coding

Use the same labels throughout. A run may have more than one failure:

1. Requirement misunderstood or acceptance criteria missed.
2. Repository navigation/context error or wrong files changed.
3. Incomplete implementation or only superficial fix.
4. New feature works but tests were omitted or ineffective.
5. Existing behavior regressed.
6. Dependency/build/environment problem.
7. Repeated unsuccessful edit/test loop or timeout.
8. Scope creep or unrelated changes.
9. Security weakness or unsafe command/change.
10. No meaningful patch, invalid patch, or tool/interface failure.

Define the labels before final evaluation. Ideally, two people independently label a subset, discuss disagreements, then code the remaining results consistently.

## Paper-ready content

The following is a draft structure and reusable wording. Replace bracketed items after you have conducted the study. Never leave a result placeholder in the submitted paper, and never substitute invented numbers.

### Title

**Agentic Coding Assistants: A Controlled, Task-Stratified Evaluation of GitHub Copilot, Cursor, Claude Code, and Codex**

If your project guide requires the original title, retain it and add “A Controlled Task-Stratified Evaluation” as a subtitle.

### Abstract draft — fill after experiments

> AI coding assistants increasingly perform repository-level tasks such as debugging, feature implementation, testing, and code modification. Their practical value cannot be assessed by code generation alone because functional correctness, regressions, security, execution effort, and human oversight also matter. This study presents a reproducible evaluation framework for comparing GitHub Copilot, Cursor, Claude Code, and [exact Codex product/interface] on a controlled set of [N] software-engineering tasks spanning [categories] and [difficulty levels]. Each assistant receives the same task description and repository snapshot. The framework records [primary metrics] and evaluates resulting patches using acceptance tests, regression tests, static analysis, security scanning, and [human review method]. Across [number] valid runs, [insert measured main result with denominator and uncertainty]. Performance varied by [measured task categories/difficulty, if supported]. We also observed [measured quality/security/oversight finding]. The results suggest [careful interpretation tied to the data]. The study is limited by [sample size, product versions, language, access mode, or other actual limits]. We release [code/task metadata/results, subject to licenses and privacy] to support replication.

**Keywords:** Agentic coding assistants, software engineering, code agents, benchmark, testing, security, reproducibility.

### 1. Introduction — draft

AI coding tools have expanded from inline code suggestions to systems that can inspect a repository, edit multiple files, invoke development tools, run tests, and iterate on a task. GitHub Copilot, Cursor, Claude Code, and Codex offer different workflows and levels of autonomy. As a result, comparing these tools is not simply a matter of asking which one produces more code. A useful comparison must consider whether the requested behavior works, whether existing behavior is preserved, how much time and human oversight are required, and what quality or security issues remain.

Existing evidence uses different evaluation settings. Software-engineering benchmarks measure whether a system can resolve curated repository issues, while studies of real-world pull requests examine outcomes such as review and merge acceptance. These sources are valuable but answer different questions. In particular, real-world acceptance may vary with task type, repository practices, and review context. A recent task-stratified study reports substantial variation across task categories and argues that workload composition matters when comparing agents [1]. Large-scale datasets such as AIDev provide evidence about agent-authored contributions in real GitHub repositories, but observational data alone do not establish how the same systems perform on identical controlled tasks [2] [3].

This project addresses that practical gap by building a reproducible evaluation framework and applying it to a standardized set of repository tasks. Each assistant is given a clean copy of the same repository snapshot and an identical task statement. The resulting patch is assessed with acceptance tests, regression tests, static analysis, security scanning, execution-effort records, and human review. The study compares results by task category and difficulty rather than relying only on a single overall score.

The study makes three contributions. First, it implements a repeatable workflow for preparing tasks, running assistants, collecting patches and logs, and evaluating results. Second, it reports a controlled comparison across [N] tasks in [language(s)], using [number] runs per task-assistant pair. Third, it characterizes observed failure modes and trade-offs among correctness, efficiency, code quality, security, and human intervention. The contribution is a bounded empirical study of the tested products and versions; it is not a claim that one system is universally best.

The remainder of the paper describes relevant background and prior work, the evaluation method, measured results, risks and limitations, and conclusions.

### 2. Background and related work — what to write

Define **coding assistant** as a system that helps produce or modify code. Define **agentic coding assistant** operationally for your study: a tool that can use repository context and one or more development actions beyond a single isolated completion, such as editing files or running tests. Explain that autonomy is a spectrum and that the product, model, interface, tool access, and human involvement all affect observed behavior.

Describe the four tested products only at the level you actually verified. Include the interface, model/version label if available, and date checked. Do not copy marketing claims as measured findings. Use a feature table with columns for product/interface, repository context, tools available, autonomy/run mode, version/date, and notes. Mark unknown fields as “not exposed” rather than guessing.

Discuss three evidence types: benchmark tasks such as SWE-bench; agentic pull-request datasets such as AIDev; and controlled experiments such as your own. SWE-bench offers variants for different evaluation budgets [4]. AIDev’s February 2026 paper describes 932,791 agentic pull requests across 116,211 repositories and five agents, with a curated subset for deeper analysis [2]. Those numbers are tied to that cited release and may change in later dataset versions.

**Citation correction to make in your synopsis:** the 932,791 / 116,211 figures match the later AIDev paper, arXiv:2602.09185 [2]. The earlier cited “The Rise of AI Teammates in Software Engineering (SE) 3.0” preprint, arXiv:2507.15003, describes an earlier dataset snapshot. Cite the source/version matching the number you use. Verify every other 2026 reference’s final title, authors, venue, version, and findings before putting it in the bibliography.

Position your project explicitly against the closest cited study: it examines task-stratified pull-request acceptance in real repositories [1]. Your planned addition is a controlled same-task comparison with patch-level test, regression, and static/security evaluation. Do not claim this is the first such study unless a literature search establishes that claim.

### 3. Methodology — draft to adapt

#### 3.1 Study design

> We conducted a controlled comparative evaluation of [four exact product/interface configurations]. The unit of study was a task-assistant run. Each task was associated with a fixed repository snapshot identified by commit hash, a task statement, acceptance criteria, and prevalidated regression and acceptance tests. The assistants received the same task statement and were given separate fresh workspaces. The experiment was conducted between [dates]. Product and model labels, settings, access tier, run mode, and available tool information were recorded for each run.

#### 3.2 Task set

> The task set contained [N] tasks: [n] bug-fixing, [n] feature implementation, [n] refactoring, [n] test-related, [n] security-remediation, and [n] repository-reasoning tasks. Tasks were labeled [difficulty scheme] before assistant runs. Each task was checked so that the unmodified baseline passed the existing regression tests and failed the new acceptance tests, while a reference implementation passed both. The reference patch and hidden evaluation tests were not exposed to the assistants. We used [language/repository sourcing and licenses].

#### 3.3 Run procedure

> For each task-assistant pair, the orchestrator created a clean workspace from the pinned base commit. The assistant received prompt version [ID] and a time limit of [minutes]. The run ended when the assistant declared completion, the operator stopped it at the limit, or the tool failed. We preserved the final diff, timestamps, tool/session logs when available, exit status, and intervention record. We repeated each pair [R] times using independent workspaces. Assistant execution order was [randomized/rotated/not randomized; explain]. Runs that could not be evaluated were marked invalid according to criteria defined before final analysis.

If some assistants require a human-operated editor and others use a CLI, say so plainly. Record operator activity and interpret this as a limitation, not as equivalent automation.

#### 3.4 Evaluation measures

> Functional completion was measured by passing all acceptance tests. Partial acceptance-test pass fraction was reported as a secondary measure. Regression behavior was measured by failures among tests that passed on the baseline. Efficiency was measured using wall-clock time and [available iteration/tool-call data]. Human oversight was measured by operator interventions and active minutes. Code-quality indicators included [tools/versions and added findings]. Security analysis used [Semgrep ruleset/version] and reported newly introduced findings by severity, followed by manual validation of important findings. Two reviewers [independently/scored together] assessed patch scope, clarity, tests, and maintainability using a [scale]-point rubric.

#### 3.5 Analysis

> We report counts and denominators for all success rates, stratified by task category and difficulty. Because each assistant attempted the same tasks, comparisons are paired at the task level. We report [confidence intervals/effect sizes] and use [statistical method] only where the sample supports it. Repeated runs of the same task are treated as repeated measurements rather than independent task instances. We classify observed failures using a predefined taxonomy. Given the bounded task set, the analysis is interpreted as [exploratory/confirmatory only if properly powered] and is not assumed to generalize to all repositories or software languages.

#### 3.6 Reproducibility and ethics

> We recorded source commit hashes, prompt version, container/runtime versions, evaluator commands, and product configuration details. We used disposable workspaces and did not mount personal credentials into task containers. Repository licenses and benchmark terms were checked. The published artifacts [describe what is shared] exclude secrets and any materials that cannot be redistributed.

### 4. Comparative analysis of assistants

Create a factual comparison table from your own product inspection. Suggested columns:

| Assistant | Exact interface/version | Context/repository access observed | Tools available in your run | Autonomy/run mode | Date/configuration |
|---|---|---|---|---|---|
| GitHub Copilot | [fill] | [fill] | [fill] | [fill] | [fill] |
| Cursor | [fill] | [fill] | [fill] | [fill] | [fill] |
| Claude Code | [fill] | [fill] | [fill] | [fill] | [fill] |
| Codex | [specify exact product] | [fill] | [fill] | [fill] | [fill] |

In the accompanying prose, explain the tested workflow rather than repeating product marketing. If one tool could not expose model version, say “not exposed during the experiment.”

### 5. Evaluation results — insert measured evidence only

Use tables generated from the result files. Recommended result tables:

**Table A — Overall task outcomes**

| Assistant | Valid runs | All acceptance tests passed | Success rate (count/denominator) | Regression runs | Median time | Median interventions |
|---|---:|---:|---:|---:|---:|---:|
| Copilot | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] |
| Cursor | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] |
| Claude Code | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] |
| Codex ([exact product]) | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] |

**Table B — Outcome by category**

| Task category | Assistant | Runs | Passes | Pass rate | Common failure type |
|---|---|---:|---:|---:|---|
| Bug fix | [ ] | [ ] | [ ] | [ ] | [ ] |
| Feature | [ ] | [ ] | [ ] | [ ] | [ ] |
| Refactor | [ ] | [ ] | [ ] | [ ] | [ ] |
| Tests | [ ] | [ ] | [ ] | [ ] | [ ] |
| Security | [ ] | [ ] | [ ] | [ ] | [ ] |
| Repository reasoning | [ ] | [ ] | [ ] | [ ] | [ ] |

**Table C — Quality and security**

| Assistant | New lint findings | Complexity change | New SAST findings by severity | Human review score | Notes |
|---|---:|---:|---|---:|---|
| [fill] | [ ] | [ ] | [ ] | [ ] | [ ] |

Write results in this order: task-set/run counts; functional completion; category/difficulty differences; time and intervention; regression/quality/security; common failure modes. For each claim, state the number of runs and denominator. Say “we observed” rather than “the tool always does.”

### 6. Risks and limitations — draft

> This evaluation has several limitations. First, the task set contains [N] tasks in [language(s)] and may not represent the diversity of production software. Second, products may use different models, context strategies, tools, and interfaces. Product labels and model versions can change over time, so the findings apply to the recorded configurations and dates. Third, manual operation for some tools may introduce operator effects and may not be directly equivalent to automated execution. Fourth, static-analysis and security tools can produce false positives and cannot establish the absence of vulnerabilities. Human review scores also involve judgment despite use of a rubric. Fifth, repeated runs and a small task set limit statistical power. Finally, benchmark success does not directly measure developer productivity or long-term maintenance cost. We therefore interpret the results as evidence about the tested configurations under the stated protocol, not as a universal ranking.

Also discuss risks of agent-generated code, review burden, test gaming/leakage, dependency/network differences, and version drift. Explain how your framework addresses each one, or say when it cannot.

### 7. Open challenges and future directions

Discuss expanding beyond Python, increasing the task set, evaluating longer-running maintenance tasks, incorporating human-developer baselines, measuring review time, testing under changing product versions, validating security findings manually, and studying post-merge outcomes. Keep these as future work; do not imply you completed them.

### 8. Conclusion — draft

> We built [name/version] to support reproducible evaluation of agentic coding assistants and applied it to [N] controlled repository tasks. Under the tested configurations, [insert the main measured findings with counts and uncertainty]. Results [did/did not] vary across task categories, and [insert measured quality, regression, efficiency, or intervention observation]. These findings show why assistant evaluation should consider more than generated code or a single aggregate success rate. The framework and task artifacts provide a basis for replication, subject to the stated product-access and licensing limits. Future work should broaden task and language coverage and examine longer-term code maintenance and developer effort.

## Six-page paper layout

Follow the department’s/IEEE template and confirm whether references count toward the six pages. A practical allocation is:

- Abstract and keywords: about 0.25 page.
- Introduction: about 0.75 page.
- Background and related work: about 0.75 page.
- Methodology: about 1.25 pages.
- Comparative analysis and results: about 1.5 pages.
- Risks, limitations, future work, conclusion: about 0.75 page.
- References: remaining space; prioritize directly relevant, verified sources.

Use figures only if they communicate something important, such as success rate by category, time distributions, or a simple system architecture. Do not shrink text excessively to force the paper into six pages; follow the required template and ask the supervisor how the page limit is interpreted.

## Suggested schedule for a 10-week project

| Week | Main work | Exit condition |
|---|---|---|
| 1 | Freeze research questions, product interfaces, run protocol, and task scope | Approved one-page protocol |
| 2 | Choose 12–18 tasks, pin commits, write prompts and test specifications | Every task has metadata and acceptance criteria |
| 3 | Build workspace manager, storage schema, and fake adapter | One fake run saves a patch and metadata |
| 4 | Build evaluator, baseline/reference validation, and result report | Good, empty, and regression patches grade correctly |
| 5 | Add actual adapters/manual procedure and isolation controls | End-to-end pilot run for each available tool |
| 6 | Pilot, fix issues, freeze protocol and environment | Pilot documented; final protocol versioned |
| 7–8 | Run the balanced evaluation and review patches | All runs accounted for; failures/exclusions explained |
| 9 | Analyze results, generate tables/plots, write findings | Results trace back to raw run artifacts |
| 10 | Finish paper, reproducibility README, demo, and final checks | Another group member can reproduce a sample run |

If the semester is shorter, reduce the number of tasks before reducing fairness or documentation. A balanced, transparent smaller experiment is better than a large incomplete benchmark.

## Final submission checklist

- [ ] Working backend/CLI prototype and source code.
- [ ] Task manifest with exact commits, licenses, prompts, categories, and difficulty labels.
- [ ] Separate hidden acceptance/regression tests, not exposed to the assistants.
- [ ] Adapter instructions and clear statement of automated versus manual runs.
- [ ] Docker/workspace setup and pinned evaluator dependencies.
- [ ] Unit, integration, isolation, timeout, and grader-validation tests.
- [ ] Raw anonymized run records, patches, logs, and evaluation outputs where redistribution is permitted.
- [ ] Analysis scripts that regenerate tables and plots from raw result data.
- [ ] Six-page paper with no fabricated results and verified references.
- [ ] README with setup, commands, limitations, and one sample run.
- [ ] Demo that shows task selection, a run record, evaluator output, and the results summary.

## Verified sources and references

[1] G. Pinna et al., “Comparing AI Coding Agents: A Task-Stratified Analysis of Pull Request Acceptance,” arXiv:2602.08915, 2026. https://arxiv.org/abs/2602.08915

[2] H. Li et al., “AIDev: Studying AI Coding Agents on GitHub,” arXiv:2602.09185, 2026. https://arxiv.org/abs/2602.09185

[3] I. Mazloomzadeh et al., “How Do AI Coding Agents Contribute to Software Development? An Empirical Study of Agentic Pull Requests,” arXiv:2607.21832, 2026. https://arxiv.org/abs/2607.21832

[4] SWE-bench, “SWE-bench Datasets,” official documentation. https://www.swebench.com/SWE-bench/guides/datasets/

[5] SWE-bench, “SWE-bench: Can Language Models Resolve Real-World GitHub Issues?” official project repository. https://github.com/swe-bench/SWE-bench
