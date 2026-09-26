# -*- coding: utf-8 -*-
"""R241 T-70 closeout prep: read ticket expectations + B-arm ledger verdicts."""
import io
import json
import glob

print('=== T-70 ticket ===')
for p in glob.glob('fleet/tasks/T-2026-09-26-70-*.json'):
    t = json.load(io.open(p, encoding='utf-8'))
    for k in ('id', 'status', 'title', 'subject', 'mandate', 'description',
              'note', 'progress_r195', 'progress_r208', 'progress_r239',
              'progress_r240'):
        v = t.get(k)
        if v:
            print(f'--{k}--')
            print(str(v)[:800])
    print('all keys:', sorted(t.keys()))

print()
print('=== pilot ledger (B-arm rows + verdict) ===')
try:
    for line in io.open('results/local_coding_pilot/ledger.jsonl',
                        encoding='utf-8'):
        if not line.strip():
            continue
        r = json.loads(line)
        print(json.dumps({k: r.get(k) for k in
                          ('task', 'arm', 'verdict', 'fix_rounds', 'ts',
                           'verdict_basis')}, ensure_ascii=False))
except Exception as e:
    print('ledger ERR', e)

print()
print('=== blind_eval verdict (B-arm criterion-2) ===')
try:
    v = json.load(io.open('results/local_coding_pilot/blind_eval/verdict.json',
                          encoding='utf-8'))
    print(json.dumps(v, ensure_ascii=False)[:700])
except Exception as e:
    print('verdict ERR', e)
