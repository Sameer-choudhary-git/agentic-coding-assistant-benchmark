import fs from 'node:fs';
import path from 'node:path';
import { randomUUID } from 'node:crypto';
import { execFileSync } from 'node:child_process';
import type { Task } from './tasks.js';

const runRoot = path.resolve(process.cwd(), 'runs');
export type RunRecord = {
  runId: string;
  taskId: string;
  assistantId: string;
  status: 'ready' | 'evaluating' | 'completed' | 'failed';
  startedAt: string;
  finishedAt?: string;
  workspace: string;
  resultFile: string;
  operatorNotes?: string;
};

function ensureRunRoot(): void { fs.mkdirSync(runRoot, { recursive: true }); }
function recordPath(runId: string): string { return path.join(runRoot, runId, 'run.json'); }

export function createRun(task: Task, assistantId: string): RunRecord {
  ensureRunRoot();
  const runId = randomUUID();
  const dir = path.join(runRoot, runId);
  const workspace = path.join(dir, 'workspace');
  fs.mkdirSync(workspace, { recursive: true });
  fs.cpSync(task.starterDir, workspace, { recursive: true, errorOnExist: true });
  // A local baseline commit makes both modifications and newly added files visible in patch.diff.
  execFileSync('git', ['init', '-q'], { cwd: workspace, stdio: 'ignore' });
  execFileSync('git', ['config', 'user.name', 'Benchmark Runner'], { cwd: workspace, stdio: 'ignore' });
  execFileSync('git', ['config', 'user.email', 'benchmark@example.invalid'], { cwd: workspace, stdio: 'ignore' });
  execFileSync('git', ['add', '-A'], { cwd: workspace, stdio: 'ignore' });
  execFileSync('git', ['commit', '-q', '-m', 'benchmark task baseline'], { cwd: workspace, stdio: 'ignore' });
  const record: RunRecord = {
    runId, taskId: task.id, assistantId, status: 'ready',
    startedAt: new Date().toISOString(), workspace,
    resultFile: path.join(dir, 'result.json'),
  };
  fs.writeFileSync(recordPath(runId), JSON.stringify(record, null, 2) + '\n', { flag: 'wx' });
  fs.writeFileSync(path.join(dir, 'prompt.md'), `# Task ${task.id}\n\n${task.prompt}\n`, { flag: 'wx' });
  return record;
}

export function getRun(runId: string): RunRecord | undefined {
  if (!/^[0-9a-f-]{36}$/i.test(runId)) return undefined;
  const file = recordPath(runId);
  if (!fs.existsSync(file)) return undefined;
  return JSON.parse(fs.readFileSync(file, 'utf8')) as RunRecord;
}

export function saveRun(record: RunRecord): void {
  const file = recordPath(record.runId);
  const temp = `${file}.tmp`;
  fs.writeFileSync(temp, JSON.stringify(record, null, 2) + '\n');
  fs.renameSync(temp, file);
}

export function getRunDirectory(runId: string): string | undefined {
  const record = getRun(runId);
  return record ? path.dirname(recordPath(runId)) : undefined;
}

export function listRunSummaries(limit = 100): RunRecord[] {
  ensureRunRoot();
  return fs.readdirSync(runRoot, { withFileTypes: true })
    .filter((entry) => entry.isDirectory())
    .map((entry) => getRun(entry.name))
    .filter((record): record is RunRecord => Boolean(record))
    .sort((a, b) => b.startedAt.localeCompare(a.startedAt))
    .slice(0, limit);
}
