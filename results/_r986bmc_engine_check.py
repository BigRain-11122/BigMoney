import json, subprocess, re

# 1. Full saturation engine status
r = subprocess.run(['python', 'Tools/saturation_engine.py', 'status'], capture_output=True, text=True, encoding='utf-8', errors='replace')
try:
    d = json.loads(r.stdout)
    print('engine keys:', list(d)[:8])
    # burn/queue faces
    for k in ('queue', 'burns', 'inflight', 'wave', 'seats'):
        if k in d:
            print(k, '=>', json.dumps(d[k], ensure_ascii=False)[:400])
except Exception as e:
    print('raw status head:', r.stdout[:800])

# 2. Engine state file (bm-c face)
try:
    eng = json.load(open('results/saturation_engine_state.bm-c.json', encoding='utf-8'))
    print('--- engine state bm-c (tail fields) ---')
    for k in ('wave', 'current_wave', 'last_wave', 'queue', 'activity_now', 'last_finalize', 'seats'):
        if k in eng:
            print(k, '=>', json.dumps(eng[k], ensure_ascii=False)[:400])
except Exception as e:
    print('engine state read fail:', e)

# 3. Recent engine ledger rows (W23x lineage)
try:
    txt = open('results/n1_engine_ledger.jsonl', encoding='utf-8').read()
    rows = [l for l in txt.strip().splitlines() if l.strip()]
    print('--- last 3 ledger rows (truncated) ---')
    for l in rows[-3:]:
        d = json.loads(l)
        print(json.dumps({k: d.get(k) for k in ('wave', 'ts', 'status', 'action', 'machine') if k in d}, ensure_ascii=False))
except Exception as e:
    print('ledger read fail:', e)
