"""r992 bm-a stash tick-preservation merge: union append-only lines from 3 held
daemon-tick stashes (16:3x/16:4x/16:5x windows) + take newest snapshot faces.
Law: append-only ledger lines zero-loss; snapshot faces live-wins newest ts.
Drops only the 3 self-created stashes (older stashes untouched per disclosures).
"""
import subprocess, json, sys

def stash_blob(n, path):
    r = subprocess.run(['git', 'show', 'stash@{%d}:%s' % (n, path)], capture_output=True)
    return r.stdout if r.returncode == 0 else None

MINE = [(0, 'daemon ticks 16:5x rebase-race-2'), (1, 'daemon ticks 16:4x race'),
        (2, 'daemon ticks 16:3x rebase-window')]
names = subprocess.check_output(['git', 'stash', 'list']).decode('utf-8', 'replace').splitlines()
for n, tag in MINE:
    if not any(('stash@{%d}' % n) in l and tag in l for l in names):
        print('ABORT: stash %d tag mismatch' % n); sys.exit(2)

JSONL = ['results/saturation_engine/history_bm-a.jsonl', 'results/pool_core_samples.jsonl']
FACES = ['results/saturation_engine/face_bm-a.json', 'results/saturation_engine/state_bm-a.json',
         'results/_sentinel_bm-a.json', 'results/autofill_state.bm-a.json',
         'results/dispatcher_state.bm-a.json']

report = {'jsonl': {}, 'faces': {}}
for p in JSONL:
    try:
        cur = open(p, encoding='utf-8-sig').read().splitlines()
    except FileNotFoundError:
        cur = []
    have = set(cur); added = []
    for n, _ in MINE:
        b = stash_blob(n, p)
        if not b:
            continue
        for line in b.decode('utf-8-sig').splitlines():
            line = line.strip()
            if line and line not in have:
                have.add(line); added.append((n, line))
    if added:
        with open(p, 'a', encoding='utf-8') as f:
            for n, line in sorted(added, key=lambda x: x[1]):
                f.write(line + '\n')
    report['jsonl'][p] = {'recovered_lines': len(added),
                          'from_stashes': sorted(set(n for n, _ in added))}

def face_ts(b):
    try:
        j = json.loads(b.decode('utf-8-sig'))
        for k in ('ts', 'last_tick_ts', 'clock_read', 'updated_at'):
            v = j.get(k) if isinstance(j, dict) else None
            if v:
                return str(v)
        lt = j.get('last_tick') if isinstance(j, dict) else None
        if isinstance(lt, dict):
            for k in ('ts', 'clock_read'):
                if lt.get(k):
                    return str(lt[k])
    except Exception:
        return ''
    return ''

for p in FACES:
    best, best_ts, best_n = None, '', -1
    for n, _ in MINE:
        b = stash_blob(n, p)
        if not b:
            continue
        t = face_ts(b) or ''
        if t >= best_ts:
            best, best_ts, best_n = b, t, n
    if best is None:
        continue
    cur = open(p, 'rb').read() if __import__('os').path.exists(p) else b''
    if p.endswith('.json'):
        json.loads(best.decode('utf-8-sig'))  # parse-verify before write
    if best != cur:
        with open(p, 'wb') as f:
            f.write(best)
    report['faces'][p] = {'took_stash': best_n, 'ts': best_ts, 'changed': best != cur}

print(json.dumps(report, ensure_ascii=False, indent=1))
with open('results/_r992bma_stash_union_receipt.json', 'w', encoding='utf-8') as f:
    json.dump({'machine': 'bm-a', 'round': 992, 'report': report}, f, ensure_ascii=False, indent=1)
