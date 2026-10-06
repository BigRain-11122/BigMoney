# r779 bm-b REBASE-window resolver (17-UU, replay of dee6688ec r778-absorb onto origin tip)
# Stage semantics REVERSED per r782 bm-a law: stage2 = onto/origin side, stage3 = replayed (bm-b) side.
# Direction-agnostic: every take-side decision by per-face deep-ts VALUE-SHAPE probe (R350: no key-exclude
# lists; wall-clock values require time-of-day; r756: space->T normalize + numeric compare).
# Twins same-side rule: REPORT md/json, LIVE x4, dashboard js/json (r98/r99/r100/r439bmb).
# Union faces: compute_audit history ts-key union zero-loss; regime_state history/transitions union + state take-new.
import subprocess, json, re, sys
from datetime import datetime

def sh(*args, raw=True):
    r = subprocess.run(list(args), capture_output=True)
    if r.returncode != 0:
        print('FAIL cmd:', args, r.stderr.decode('utf-8', 'replace')[:400]); sys.exit(2)
    return r.stdout

WALL = re.compile(r'^20\d{2}-\d{2}-\d{2}[T ]\d{2}:\d{2}')
def deep_ts(obj):
    best = None
    stack = [obj]
    while stack:
        x = stack.pop()
        if isinstance(x, dict):
            stack.extend(x.values())
        elif isinstance(x, list):
            stack.extend(x)
        elif isinstance(x, str) and WALL.match(x):
            v = datetime.fromisoformat(x.replace(' ', 'T', 1)).replace(tzinfo=None)  # tz-normalized compare (r756 family)
            if best is None or v > best: best = v
    return best

def blob(stage, path):
    b = sh('git', 'show', ':%s:%s' % (stage, path))
    return b

def stage_exists(stage, path):
    r = subprocess.run(['git', 'rev-parse', '--verify', '--quiet', ':%s:%s' % (stage, path)], capture_output=True)
    return r.returncode == 0

def probe(stage, path):
    if not stage_exists(stage, path): return None  # collapsed = already resolved in partial run
    return deep_ts(json.loads(blob(stage, path)))

# ---- twin groups: adjudicate side by freshest coherent max-ts across the group's json faces ----
GROUPS = [
    ['docs/daily_report/REPORT-2026-10-06.json', 'docs/daily_report/REPORT-2026-10-06.md'],
    ['docs/live_usage/LIVE-2026-10-06.json', 'docs/live_usage/LIVE-2026-10-06.md',
     'docs/live_usage/LIVE-latest.json', 'docs/live_usage/LIVE-latest.md'],
    ['results/dashboard_status.json', 'results/dashboard_status.js'],
]
group_side = {}
for g in GROUPS:
    v2 = [probe('2', p) for p in g if p.endswith('.json')]
    v3 = [probe('3', p) for p in g if p.endswith('.json')]
    p2 = max([v for v in v2 if v is not None], default=None)
    p3 = max([v for v in v3 if v is not None], default=None)
    side = '2' if (p3 is None or (p2 is not None and p2 >= p3)) else '3'
    group_side[tuple(g)] = side
    print('group %s -> side %s (s2=%s s3=%s)' % (g[0], side, p2, p3))

SNAPSHOTS = ['results/fundamental_b_layer_filter.json', 'results/futures_update_status.json',
             'results/lhb_update_status.json', 'results/scorecard_v1.json',
             'results/strategy_scorecard.json', 'results/token_usage.json',
             'results/update_status.json']
decisions = {}
for g in GROUPS:
    for p in g: decisions[p] = group_side[tuple(g)]
for p in SNAPSHOTS:
    p2, p3 = probe('2', p), probe('3', p)
    decisions[p] = '2' if (p3 is None or (p2 is not None and p2 >= p3)) else '3'
    print('%s -> side %s (s2=%s s3=%s)' % (p, decisions[p], p2, p3))

# ---- materialize take-side faces byte-verbatim (src sha captured BEFORE add: r611-1 stage-collapse law) ----
def take_bytes(path, side):
    if not stage_exists(side, path):
        print('%s: stage %s collapsed (resolved in partial run) -> skip, parse-verify only' % (path, side))
        json.loads(open(path, 'rb').read().decode('utf-8')) if path.endswith('.json') else None
        return
    b = blob(side, path)
    src_sha = sh('git', 'rev-parse', ':%s:%s' % (side, path)).decode().strip()
    if path.endswith('.json'):
        json.loads(b)  # parse gate r185
    with open(path, 'wb') as f: f.write(b)
    sh('git', 'add', path)
    st = sh('git', 'ls-files', '-s', path).decode().strip().split()
    assert st[1] == src_sha, 'staged sha drift %s: %s != %s' % (path, st[1], src_sha)

for p, side in decisions.items():
    take_bytes(p, side)

# ---- union faces ----
def union_list(a, b, keyfield):
    seen, out = {}, []
    for e in a + b:
        k = e.get(keyfield)
        if k is None: k = json.dumps(e, sort_keys=True)
        if k in seen: continue
        seen[k] = e; out.append(e)
    out.sort(key=lambda e: str(e.get(keyfield) or ''))
    return out

def resolve_union(path, list_keys):
    o = json.loads(blob('2', path)); t = json.loads(blob('3', path))
    merged = dict(o); merged.update(t)  # state fields: newer-side wins (dict update; ts adjudicated below)
    # choose newer state base by deep probe
    if (deep_ts(t) or datetime.min) >= (deep_ts(o) or datetime.min):
        merged = dict(o); merged.update(t)
    else:
        merged = dict(t); merged.update(o)
    for k in list_keys:
        if k in o or k in t:
            merged[k] = union_list(o.get(k, []), t.get(k, []), 'ts' if k == 'history' else 'asof')
            n_a, n_b = len(o.get(k, [])), len(t.get(k, []))
            assert len(merged[k]) >= max(n_a, n_b), 'union loss %s.%s' % (path, k)
            print('%s.%s union %d+%d -> %d zero-loss' % (path, k, n_a, n_b, len(merged[k])))
    data = json.dumps(merged, indent=1, ensure_ascii=False) + '\n'
    json.loads(data)  # parse gate
    with open(path, 'wb') as f: f.write(data.encode('utf-8'))
    sh('git', 'add', path)

resolve_union('results/compute_audit.json', ['history'])
resolve_union('results/regime_state.json', ['history', 'transitions'])

# ---- staged-face conflict-marker scan (r609-3) ----
pat_start = re.compile(rb'^<<<<<<< '); pat_mid = re.compile(rb'^=======$'); pat_end = re.compile(rb'^>>>>>>> ')
out = sh('git', 'diff', '--cached', '--name-only').decode().splitlines()
bad = []
for p in out:
    b = sh('git', 'show', ':' + p)
    for ln in b.splitlines():
        if pat_start.match(ln) or pat_mid.match(ln) or pat_end.match(ln):
            bad.append(p); break
assert not bad, 'real marker leftovers: %r' % bad
print('staged faces scanned:', len(out), 'marker leftovers: 0')
print('RESOLVER OK 17/17: %d take-side byte-verbatim + 2 union zero-loss' % len(decisions))
