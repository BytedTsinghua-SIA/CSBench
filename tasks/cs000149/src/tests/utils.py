import json
import os
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NODE = os.environ.get("NODE", "node")

NODE_RUNNER = r"""
const path = require('path');
const payloadText = process.env.NODE_PAYLOAD || '{}';
let payload;
try {
  payload = JSON.parse(payloadText);
} catch (err) {
  process.stdout.write(JSON.stringify({ ok: false, error: 'invalid payload' }));
  process.exit(0);
}
const modulePath = payload.module;
const fnName = payload.function;
const args = payload.args || [];
(async () => {
  try {
    if (!modulePath || !fnName) {
      throw new Error('missing module or function');
    }
    const mod = require(path.resolve(modulePath));
    const fn = mod[fnName];
    if (typeof fn !== 'function') {
      throw new Error('function not found');
    }
    const result = await fn(...args);
    process.stdout.write(JSON.stringify({ ok: true, result }));
  } catch (err) {
    const message = err && err.message ? err.message : String(err);
    process.stdout.write(JSON.stringify({ ok: false, error: message }));
  }
})();
"""


def run_node(module_path, function_name, args=None, env=None):
    payload = {
        "module": str(ROOT / module_path),
        "function": function_name,
        "args": args or [],
    }
    merged_env = os.environ.copy()
    if env:
        merged_env.update(env)
    merged_env["NODE_PAYLOAD"] = json.dumps(payload)
    result = subprocess.run(
        [NODE, "-e", NODE_RUNNER],
        cwd=ROOT,
        env=merged_env,
        capture_output=True,
        text=True,
        check=False,
    )
    output = result.stdout.strip() or result.stderr.strip()
    data = json.loads(output)
    return data
