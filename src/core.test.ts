import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import { listTasks, getTask } from './tasks.js';

test('catalog contains six benchmark tasks across requested categories', () => {
  const tasks = listTasks();
  assert.equal(tasks.length, 6);
  assert.deepEqual(new Set(tasks.map((task) => task.category)), new Set([
    'bug_fix', 'feature', 'security_remediation', 'refactoring', 'testing', 'repository_reasoning',
  ]));
  for (const task of tasks) {
    assert.ok(fs.existsSync(task.starterDir), `starter missing: ${task.id}`);
    assert.ok(fs.existsSync(task.evalDir), `evaluator missing: ${task.id}`);
  }
});

test('task lookup rejects unknown identifiers', () => {
  assert.equal(getTask('not-a-task'), undefined);
});

test('task prompts exist and are non-empty', () => {
  for (const task of listTasks()) assert.ok(task.prompt.length > 40);
});
