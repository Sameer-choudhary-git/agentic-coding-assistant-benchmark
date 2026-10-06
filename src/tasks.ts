import fs from 'node:fs';
import path from 'node:path';

export type Task = {
  id: string;
  title: string;
  category: string;
  difficulty: 'easy' | 'medium' | 'hard';
  language: string;
  prompt: string;
  starterDir: string;
  evalDir: string;
};

const root = path.resolve(process.cwd(), 'tasks');
const entries: Omit<Task, 'starterDir' | 'evalDir'>[] = [
  { id: 'bugfix-temperature', title: 'Fix Fahrenheit-to-Celsius conversion', category: 'bug_fix', difficulty: 'easy', language: 'python', prompt: 'Fix to_celsius(fahrenheit) in solution.py. It currently returns the wrong value. The function must convert Fahrenheit to Celsius using the standard formula and return a float. Do not change the public function name.' },
  { id: 'feature-slugify', title: 'Implement URL slug generation', category: 'feature', difficulty: 'easy', language: 'python', prompt: 'Implement slugify(text) in solution.py. Return lowercase ASCII words separated by one hyphen; trim leading/trailing hyphens; collapse whitespace and punctuation separators; ignore non-ASCII characters. Examples: "Hello, World!" -> "hello-world", "  A  B " -> "a-b".' },
  { id: 'security-shell-arg', title: 'Remove shell-injection risk', category: 'security_remediation', difficulty: 'medium', language: 'python', prompt: 'Make run_report(user_arg) safe from shell injection. Preserve the behavior of invoking the report utility with user_arg as its single argument. Use subprocess without a shell and return subprocess.run(...) so callers can inspect the result. Do not execute the report utility in tests.' },
  { id: 'refactor-user-parser', title: 'Refactor user record parsing', category: 'refactoring', difficulty: 'medium', language: 'python', prompt: 'Refactor parse_user(record) to improve readability and validation while preserving its documented behavior. It accepts "id,name,email" and returns a dict with integer id, stripped name, and lowercase stripped email. Reject malformed records, blank names/emails, and non-integer IDs with ValueError. Keep the public function name and return structure.' },
  { id: 'test-port-validator', title: 'Add tests for port validation', category: 'testing', difficulty: 'easy', language: 'python', prompt: 'Add a pytest test file for is_valid_port(value) in solution.py. Cover valid boundary values 1 and 65535; invalid boundaries 0 and 65536; a typical valid port; and invalid types/strings. Do not change solution.py unless necessary to make the existing documented API testable. Tests must assert behavior, not merely call the function.' },
  { id: 'repo-reasoning', title: 'Document repository configuration flow', category: 'repository_reasoning', difficulty: 'medium', language: 'python', prompt: 'Inspect this small repository and write docs/config-flow.md explaining which function reads the service configuration, the precedence of its sources, and the default timeout. Cite the exact file and function names in the note. Do not modify application behavior.' },
];

export function listTasks(): Task[] {
  return entries.map((entry) => ({
    ...entry,
    starterDir: path.join(root, entry.id, 'starter'),
    evalDir: path.join(root, entry.id, 'eval'),
  }));
}

export function getTask(id: string): Task | undefined {
  return listTasks().find((task) => task.id === id);
}

export function validateTaskAssets(task: Task): void {
  if (!fs.existsSync(task.starterDir) || !fs.existsSync(task.evalDir)) {
    throw new Error(`Task assets missing for ${task.id}`);
  }
}
