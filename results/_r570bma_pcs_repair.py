# -*- coding: utf-8 -*-
"""r570 bm-a: pool_core_samples.jsonl corruption repair (union face).

Local file was clobbered at ~10:17 by a shell-level redirect (attrition
guard scan output written into the shared jsonl -- 71 fragment lines),
followed by 7 legitimate dict-row appends. Origin canon = 750 valid rows.

Repair = union: origin 750 rows as base + any local-only valid dict rows
appended (dedupe by full-line identity). Byte-level: preserve origin bytes
verbatim, append only genuinely-new rows with '\n' terminators matching
the file's EOL shape.
"""
import subprocess, json, sys

raw = subprocess.check_output(['git', 'show', 'origin/main:results/pool_core_samples.jsonl'])
origin_text = raw.decode('utf-8')
origin_lines = origin_text.splitlines()
assert len(origin_lines) == 750, f'origin shape drift: {len(origin_lines)}'
eol = '\r\n' if origin_text.count('\r\n') * 2 > origin_text.count('\n') else '\n'
origin_set = set(origin_lines)

loc_lines = open('results/pool_core_samples.jsonl', encoding='utf-8').read().splitlines()
new_rows = []
for ln in loc_lines:
    s = ln.strip()
    if not s:
        continue
    try:
        r = json.loads(s)
    except Exception:
        continue
    if isinstance(r, dict) and s not in origin_set:
        new_rows.append(s)
print('origin rows: 750 | local valid new rows:', len(new_rows))
for r in new_rows:
    d = json.loads(r)
    print('  new:', d.get('ts'), '| verdict:', d.get('verdict'), '| keys:', sorted(d.keys())[:6])

# verify all origin rows are dict-shaped (sanity)
bad = 0
for ln in origin_lines:
    try:
        if not isinstance(json.loads(ln), dict):
            bad += 1
    except Exception:
        bad += 1
assert bad == 0, f'origin has bad rows: {bad}'

# rewrite = origin bytes verbatim + new rows appended
out = origin_text
if not out.endswith('\n'):
    out += eol
for r in new_rows:
    out += r + eol if r + eol not in out else ''
open('results/pool_core_samples.jsonl', 'wb').write(out.encode('utf-8'))

# post-verify: every line valid dict, count = 750 + len(new_rows)
final_lines = open('results/pool_core_samples.jsonl', encoding='utf-8').read().splitlines()
cnt = 0
for ln in final_lines:
    s = ln.strip()
    if not s:
        continue
    assert isinstance(json.loads(s), dict), 'post-verify: non-dict row survived'
    cnt += 1
assert cnt == 750 + len(new_rows), f'post count {cnt} != {750 + len(new_rows)}'
print(f'REPAIR OK: {cnt} rows (750 origin + {len(new_rows)} local-new), all dict-shaped')
