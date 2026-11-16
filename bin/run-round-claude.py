#!/usr/bin/env python3
"""Claude Code backend for refine; preserves the shared ledger/meta contract."""
import argparse
import datetime
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parent))
import refine_lib as L


def command(executable, schema, effort, session=None):
    args = [executable, '-p', '--model', 'opus', '--effort', effort,
            '--output-format', 'json', '--json-schema', schema,
            '--tools', 'Read,Grep,Glob', '--allowedTools', 'Read,Grep,Glob',
            '--permission-mode', 'dontAsk', '--disable-slash-commands',
            '--strict-mcp-config', '--mcp-config', '{"mcpServers":{}}',
            '--settings', '{"disableAllHooks":true}', '--no-chrome']
    if session: args += ['--resume', session]
    return args


def extract_result(value):
    if (value.get('type') != 'result' or value.get('subtype') != 'success'
            or value.get('is_error') is not False or not value.get('session_id')
            or not isinstance(value.get('structured_output'), dict)):
        raise ValueError('Claude did not return a successful structured review')
    return value['structured_output']


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--run-dir', required=True)
    ap.add_argument('--round', type=int, required=True)
    ap.add_argument('--kind', choices=['full', 'delta', 'confirm'], required=True)
    ap.add_argument('--effort', choices=['high', 'medium', 'low'])
    ap.add_argument('--no-assemble', action='store_true')
    ap.add_argument('--repair')
    a = ap.parse_args()
    run = Path(a.run_dir).resolve()
    meta = L.read_kv(str(run / 'run.meta'))
    effort = a.effort or (L.delta_effort(meta['effort']) if a.kind == 'delta' else meta['effort'])
    prefix = f'round-{a.round}'
    output, record = run / (prefix + '.json'), run / (prefix + '.meta')
    prompt = run / ('.prompt-' + prefix + '.md')
    event = run / ('.claude-' + prefix + ('.repair' if a.repair else '') + '.jsonl')
    old = L.read_kv(str(record)) if record.exists() else {}
    if a.repair and (not old.get('thread_id') or 'repair_exit' in old):
        raise ValueError('Repair requires a prior session and is allowed once')
    if not a.repair and (output.exists() or record.exists()):
        raise ValueError('Existing attempt: preserve it explicitly before rerunning; refusing overwrite')
    if not a.no_assemble and not a.repair:
        subprocess.run([sys.executable, str(Path(__file__).with_name('assemble-prompt.py')),
                        '--run-dir', str(run), '--round', str(a.round), '--kind', a.kind], check=True)
    text = (f'Your prior array was invalid: {a.repair}. Re-emit the complete review with the correction, changing no findings.'
            if a.repair else prompt.read_text(encoding='utf-8'))
    if a.repair:
        shutil.copy2(output, run / (f'.{prefix}.attempt1.json'))
        shutil.copy2(record, run / (f'.{prefix}.attempt1.meta.pre'))
    executable = shutil.which('claude') or shutil.which('claude.exe')
    if not executable:
        candidate = Path.home() / '.local' / 'bin' / 'claude.exe'
        if candidate.is_file(): executable = str(candidate)
    if not executable: raise ValueError('Claude Code executable not found')
    schema = Path(__file__).resolve().parents[1] / 'review.schema.json'
    started = datetime.datetime.now(datetime.timezone.utc).isoformat()
    began = time.monotonic()
    with event.open('w', encoding='utf-8') as stdout, (run / ('.claude-' + prefix + '.stderr')).open('w', encoding='utf-8') as stderr:
        process = subprocess.Popen(command(executable, json.dumps(json.loads(schema.read_text())), effort,
                                           old.get('thread_id') if a.repair else None),
                                   cwd=meta['worktree'], stdin=subprocess.PIPE, stdout=stdout, stderr=stderr,
                                   text=True, encoding='utf-8', creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
        try: process.communicate(text, timeout=1800)
        except subprocess.TimeoutExpired:
            if os.name == 'nt': subprocess.run(['taskkill', '/PID', str(process.pid), '/T', '/F'], capture_output=True)
            else: process.kill()
            process.communicate()
    rc = process.returncode
    value = {}
    try: value = json.loads(event.read_text(encoding='utf-8'))
    except (ValueError, OSError): pass
    usage = value.get('usage', {})
    pre = 'repair_' if a.repair else ''
    result = old if a.repair else dict(kind=a.kind, head=L.git(meta['worktree'], 'rev-parse', '--short', 'HEAD'),
                                     thread_id=value.get('session_id', ''), effort=effort, started_at=started, reviewer='claude-opus')
    result.update({pre+'exit': str(rc), pre+'duration_s': str(int(time.monotonic()-began)),
                   pre+'input_tokens': str(sum(usage.get(k, 0) for k in ['input_tokens', 'cache_read_input_tokens', 'cache_creation_input_tokens'])),
                   pre+'cached_input_tokens': str(usage.get('cache_read_input_tokens', 0)),
                   pre+'output_tokens': str(usage.get('output_tokens', 0)), pre+'reasoning_output_tokens': ''})
    if a.repair:
        result.pop('parsed', None)
        result.pop('parse_failed', None)
    try:
        if rc != 0: raise ValueError(f'Claude exited {rc}')
        review = extract_result(value)
    except ValueError:
        result[pre+'exit'] = str(rc or 1)
        L.write_kv(str(record), result)
        raise
    L.write_kv(str(record), result)
    temporary = output.with_suffix('.json.tmp')
    temporary.write_text(json.dumps(review, indent=2)+'\n', encoding='utf-8')
    temporary.replace(output)
    print(f'round {a.round} Claude Opus complete: {result[pre+"duration_s"]}s')
    print(record.read_text())


if __name__ == '__main__':
    try: main()
    except (ValueError, OSError, subprocess.SubprocessError) as error:
        print(f'CLAUDE FAILURE: {error}', file=sys.stderr)
        sys.exit(1)
