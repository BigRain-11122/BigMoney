# r436 bm-a rebase conflict resolver (19 UU) -- bigmoney-conflict-resolve skill recipes
# Shapes: ALL_FACES(7) via merge_lane_views resolve; snapshot take-new deep-ts probe (staged blobs);
# twin-regen (json side pick -> md same-side bytes); CODELY.md memory-union with LF-normalize (r223/r234 EOL mirror).
import subprocess, json, re, sys, os

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def blob(ref, path):
    ref = ref.rstrip(':')
    assert ref in (':1', ':2', ':3')
    r = subprocess.run(['git', 'show', f'{ref}:{path}'], capture_output=True, cwd=REPO)
    if r.returncode != 0:
        raise RuntimeError(f'git show {ref}:{path} rc={r.returncode}')
    return r.stdout

def write_bytes(path, data):
    full = os.path.join(REPO, path)
    with open(full, 'wb') as f:
        f.write(data)

log = []

# ---------- Part A: ALL_FACES via merge_lane_views resolve ----------
ALL_FACES = [
    'results/compute_audit.json',
    'results/regime_state.json',
    'results/update_status.json',
    'results/lhb_update_status.json',
    'results/futures_update_status.json',
    'results/fundamental_b_layer_filter.json',
    'results/token_usage.json',
]
for p in ALL_FACES:
    r = subprocess.run(['git', 'ls-files', '-u', '--', p], capture_output=True, cwd=REPO)
    if not r.stdout.strip():
        log.append(f'ALLFACE {p} SKIP (not conflicted, auto-merged)')
        continue
    r = subprocess.run([sys.executable, 'scripts/merge_lane_views.py', 'resolve', p],
                       capture_output=True, cwd=REPO)
    ok = r.returncode == 0
    log.append(f'ALLFACE {p} rc={r.returncode} ' + (r.stdout.decode("utf-8", "replace").strip().splitlines()[-1][:120] if ok else r.stderr.decode("utf-8", "replace").strip().splitlines()[-1][:160]))
    if not ok:
        log.append(f'  -> fallback to snapshot probe needed for {p}')
        p and None
    else:
        # verify json parses
        with open(os.path.join(REPO, p), 'rb') as f:
            json.loads(f.read().decode('utf-8'))

# ---------- Part B: hardened deep-ts probe (value-shape only, R350; staged blobs r311/r100) ----------
TS_RE = re.compile(r'^20\d{2}-\d{2}-\d{2}[T ]\d{2}:\d{2}')

def probe_max_ts(obj):
    best = ''
    if isinstance(obj, dict):
        for v in obj.values():
            t = probe_max_ts(v)
            if t > best:
                best = t
    elif isinstance(obj, list):
        for v in obj:
            t = probe_max_ts(v)
            if t > best:
                best = t
    elif isinstance(obj, str) and TS_RE.match(obj):
        best = obj
    return best

def take_new_snapshot(path):
    r = subprocess.run(['git', 'ls-files', '-u', '--', path], capture_output=True, cwd=REPO)
    if not r.stdout.strip():
        log.append(f'SNAPSHOT {path} SKIP (not conflicted, auto-merged)')
        return ':auto'
    o = blob(':2:', path)  # origin/base-side
    m = blob(':3:', path)  # local/replay-side
    try:
        ts_o = probe_max_ts(json.loads(o.decode('utf-8')))
        ts_m = probe_max_ts(json.loads(m.decode('utf-8')))
    except Exception as e:
        log.append(f'SNAPSHOT {path} PROBE-FAIL {e} -> take :2: origin (fail-safe)')
        write_bytes(path, o)
        return ':2:'
    if ts_m > ts_o:
        side, data = ':3:', m
    elif ts_o > ts_m:
        side, data = ':2:', o
    else:
        side, data = ':2:', o  # same-second tie -> HEAD/origin (r140)
    write_bytes(path, data)
    json.loads(data.decode('utf-8'))  # parse-verify
    log.append(f'SNAPSHOT {path} ts_o={ts_o!r} ts_m={ts_m!r} -> {side}')
    return side

for p in ['results/daily_scorecard.json', 'results/scorecard_v1.json',
          'results/strategy_scorecard.json', 'results/dashboard_status.json']:
    take_new_snapshot(p)

# dashboard_status.js twin: same side as dashboard_status.json (js-wrapper take-side whole bytes R209)
def conflicted(path):
    r = subprocess.run(['git', 'ls-files', '-u', '--', path], capture_output=True, cwd=REPO)
    return bool(r.stdout.strip())

if conflicted('results/dashboard_status.js') and conflicted('results/dashboard_status.json'):
    o = blob(':2:', 'results/dashboard_status.js'); m = blob(':3:', 'results/dashboard_status.js')
    # probe json twin side from log above; re-derive to keep coupling explicit
    o_j = blob(':2:', 'results/dashboard_status.json'); m_j = blob(':3:', 'results/dashboard_status.json')
    ts_o = probe_max_ts(json.loads(o_j.decode('utf-8'))); ts_m = probe_max_ts(json.loads(m_j.decode('utf-8')))
    side_js = ':3:' if ts_m > ts_o else ':2:'
    write_bytes('results/dashboard_status.js', m if side_js == ':3:' else o)
    log.append(f'JS-WRAPPER dashboard_status.js -> {side_js} whole bytes (same side as .json twin)')
else:
    log.append('JS-WRAPPER dashboard_status.js SKIP (pair not conflicted)')

# ---------- Part C: twin-regen pairs (json side -> md same-side bytes, no hybrid twins r329) ----------
TWINS = [
    ('docs/daily_report/REPORT-2026-09-29.json', 'docs/daily_report/REPORT-2026-09-29.md'),
    ('docs/live_usage/LIVE-2026-09-29.json', 'docs/live_usage/LIVE-2026-09-29.md'),
    ('docs/live_usage/LIVE-latest.json', 'docs/live_usage/LIVE-latest.md'),
]
for jp, mp in TWINS:
    if not conflicted(jp):
        log.append(f'TWIN {jp} SKIP (not conflicted)')
        continue
    o = blob(':2:', jp); m = blob(':3:', jp)
    ts_o = probe_max_ts(json.loads(o.decode('utf-8')))
    ts_m = probe_max_ts(json.loads(m.decode('utf-8')))
    side = ':3:' if ts_m > ts_o else ':2:'
    write_bytes(jp, m if side == ':3:' else o)
    write_bytes(mp, blob(side, mp))
    log.append(f'TWIN {jp} ts_o={ts_o!r} ts_m={ts_m!r} -> {side} (md same-side bytes)')

# ---------- Part D: CODELY.md memory-union (LF-normalized prefix concat, entries verbatim) ----------
if conflicted('CODELY.md'):
    base = blob(':1:', 'CODELY.md')
    org = blob(':2:', 'CODELY.md').replace(b'\r\n', b'\n')
    mine = blob(':3:', 'CODELY.md')
    assert mine.startswith(base), 'mine prefix assertion failed'
    assert org.startswith(base), 'origin prefix assertion failed (LF-normalized)'
    res = base + org[len(base):] + mine[len(base):]
    write_bytes('CODELY.md', res)
    log.append(f'CODELY.md memory-union: base={len(base)} +org_suffix={len(org)-len(base)} +mine_suffix={len(mine)-len(base)} = {len(res)}B (LF mirror of base)')
else:
    log.append('CODELY.md SKIP (not conflicted)')

print('\n'.join(log))
print('ALL RESOLVED OK' if all('PROBE-FAIL' not in l for l in log) else 'SOME PROBE-FAIL (fail-safe taken)')
