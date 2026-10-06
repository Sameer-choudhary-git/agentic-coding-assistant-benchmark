import express from 'express';
import fs from 'node:fs';
import path from 'node:path';
import { spawn } from 'node:child_process';
import { getTask, listTasks, validateTaskAssets } from './tasks.js';
import { createRun, getRun, getRunDirectory, listRunSummaries, saveRun } from './runs.js';

const app = express();
const port = Number(process.env.PORT ?? 3000);
const host = process.env.HOST ?? '127.0.0.1';
app.use(express.json({ limit: '64kb' }));

app.get('/health', (_req, res) => res.json({ status: 'ok', service: 'agentic-coding-assistant-benchmark' }));
app.get('/tasks', (_req, res) => res.json({ tasks: listTasks().map(({ starterDir: _s, evalDir: _e, ...task }) => task) }));
app.get('/tasks/:taskId', (req, res) => {
  const task = getTask(req.params.taskId);
  if (!task) return res.status(404).json({ error: 'task_not_found' });
  const { starterDir: _s, evalDir: _e, ...publicTask } = task;
  return res.json(publicTask);
});
app.get('/assistants', (_req, res) => res.json({ assistants: [
  { id: 'github-copilot', label: 'GitHub Copilot', runMode: 'manual' },
  { id: 'cursor', label: 'Cursor', runMode: 'manual' },
  { id: 'claude-code', label: 'Claude Code', runMode: 'manual' },
  { id: 'codex', label: 'Codex (specify exact product in run notes)', runMode: 'manual' },
] }));
app.get('/runs', (_req, res) => res.json({ runs: listRunSummaries() }));

app.post('/runs', (req, res) => {
  const taskId = typeof req.body?.taskId === 'string' ? req.body.taskId : '';
  const assistantId = typeof req.body?.assistantId === 'string' ? req.body.assistantId : '';
  if (!/^[a-z0-9-]{1,64}$/.test(assistantId)) return res.status(400).json({ error: 'assistantId must contain only lowercase letters, digits, and hyphens' });
  const task = getTask(taskId);
  if (!task) return res.status(404).json({ error: 'task_not_found' });
  validateTaskAssets(task);
  const record = createRun(task, assistantId);
  return res.status(201).json({
    run: record,
    prompt: task.prompt,
    instructions: `Open this fresh workspace in the selected assistant: ${record.workspace}. Give it the prompt exactly as returned. Do not expose evaluator files. When done, call POST /runs/${record.runId}/evaluate.`,
  });
});

app.post('/runs/:runId/notes', (req, res) => {
  const record = getRun(req.params.runId);
  if (!record) return res.status(404).json({ error: 'run_not_found' });
  const notes = typeof req.body?.notes === 'string' ? req.body.notes.slice(0, 4000) : '';
  record.operatorNotes = notes;
  saveRun(record);
  return res.json({ run: record });
});

app.post('/runs/:runId/evaluate', async (req, res) => {
  const record = getRun(req.params.runId);
  if (!record) return res.status(404).json({ error: 'run_not_found' });
  if (record.status === 'evaluating') return res.status(409).json({ error: 'run_already_evaluating' });
  const task = getTask(record.taskId);
  if (!task) return res.status(500).json({ error: 'task_definition_missing' });
  const runDir = getRunDirectory(record.runId)!;
  const diffFile = path.join(runDir, 'patch.diff');
  const resultFile = record.resultFile;
  record.status = 'evaluating';
  saveRun(record);
  const git = spawn('git', ['diff', '--no-ext-diff', '--binary', 'HEAD'], { cwd: record.workspace, timeout: 10_000 });
  let diff = '';
  let gitError = '';
  git.stdout.setEncoding('utf8'); git.stdout.on('data', (chunk: string) => { diff += chunk; });
  git.stderr.setEncoding('utf8'); git.stderr.on('data', (chunk: string) => { gitError += chunk; });
  const gitExit = await new Promise<number>((resolve) => git.on('close', (code) => resolve(code ?? 1)));
  fs.writeFileSync(diffFile, gitExit === 0 ? diff : `git diff failed: ${gitError}`);
  const localVenvPython = path.resolve('.venv/bin/python');
  const pythonExecutable = process.env.PYTHON ?? (fs.existsSync(localVenvPython) ? localVenvPython : 'python3');
  const py = spawn(pythonExecutable, [path.resolve('python/evaluate.py'), '--task', task.id, '--workspace', record.workspace, '--out', resultFile], { cwd: process.cwd(), timeout: 120_000 });
  let stdout = ''; let stderr = '';
  py.stdout.setEncoding('utf8'); py.stdout.on('data', (chunk: string) => { stdout += chunk; });
  py.stderr.setEncoding('utf8'); py.stderr.on('data', (chunk: string) => { stderr += chunk; });
  const exitCode = await new Promise<number>((resolve) => py.on('close', (code) => resolve(code ?? 1)));
  record.finishedAt = new Date().toISOString();
  record.status = exitCode === 0 ? 'completed' : 'failed';
  saveRun(record);
  const result = fs.existsSync(resultFile) ? JSON.parse(fs.readFileSync(resultFile, 'utf8')) : null;
  return res.status(exitCode === 0 ? 200 : 500).json({ run: record, result, stdout, stderr, exitCode });
});

app.get('/runs/:runId', (req, res) => {
  const record = getRun(req.params.runId);
  if (!record) return res.status(404).json({ error: 'run_not_found' });
  const result = fs.existsSync(record.resultFile) ? JSON.parse(fs.readFileSync(record.resultFile, 'utf8')) : null;
  return res.json({ run: record, result });
});

app.listen(port, host, () => console.log(`Benchmark API listening on http://${host}:${port}`));
