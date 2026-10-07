# r824 bm-a rebase-conflict resolver (SKILL.md bigmoney-conflict-resolve recipes)
# UU set: twin-regen-md x2 groups (same-side law) + snapshots (deep ts probe, newest wins)
# + 1 UNKNOWN manually classified: results/_attrition_guard_scan.json
#   = guard scan evidence snapshot (full overwrite each scan run -> snapshot semantics,
#     newest scan ts wins wholesale; not a ledger).
# Stage law (r351): :2: = origin side (THEIRS in rebase), :3: = local side (OURS in rebase).
# md twins MUST be byte-copied from the SAME side blob as their json twin (r329).
import subprocess, json, re, sys

def stage_bytes(path, stage):
    r = subprocess.run(['git', 'show', f':{stage}:{path}'], capture_output=True)
    if r.returncode != 0:
        raise SystemExit(f'stage read fail {path}:{stage}: {r.stderr.decode("utf-8","replace")[:200]}')
    return r.stdout

def deep_ts(obj, _depth=0):
    """Deep-scan nested layers for a wall-clock ts (r311/D-09 law)."""
    if _depth > 6:
        return ''
    if isinstance(obj, dict):
        best = ''
        for k, v in obj.items():
            nk = str(k).replace('_', '').replace('-', '').lower()
            if nk.startswith(('ts', 'generated', 'updated', 'scannedat', 'donets', 'lastscan')) \
               and isinstance(v, str) and re.match(r'^20\d{2}-', v):
                if v > best:
                    best = v
            sub = deep_ts(v, _depth + 1)
            if sub > best:
                best = sub
        return best
    if isinstance(obj, list):
        best = ''
        for it in obj:
            sub = deep_ts(it, _depth + 1)
            if sub > best:
                best = sub
        return best
    return ''

def pick_side_json(path):
    b2 = stage_bytes(path, 2)
    b3 = stage_bytes(path, 3)
    try:
        o2 = json.loads(b2)
        o3 = json.loads(b3)
    except Exception as ex:
        raise SystemExit(f'{path}: parse fail {ex}')
    t2, t3 = deep_ts(o2), deep_ts(o3)
    side = 2 if t2 >= t3 else 3   # tie -> origin side (r140 same-sec HEAD-side; rebase onto origin)
    print(f'  {path}: origin_ts={t2!r} local_ts={t3!r} -> side {side}')
    return (2 if side == 2 else 3), (b2 if side == 2 else b3)

def take_new_bytes(path):
    b2 = stage_bytes(path, 2)
    b3 = stage_bytes(path, 3)
    # snapshot: probe json sides when possible; byte-copy chosen side whole
    try:
        t2 = deep_ts(json.loads(b2))
        t3 = deep_ts(json.loads(b3))
    except Exception:
        t2 = t3 = ''
    side = 2 if t2 >= t3 else 3
    print(f'  {path}: origin_ts={t2!r} local_ts={t3!r} -> side {side}')
    return b2 if side == 2 else b3

def write(path, data):
    with open(path, 'wb') as f:
        f.write(data)

# --- twin groups: json decides the side, md copies same-side bytes ---
groups = [
    ['docs/daily_report/REPORT-2026-10-07.json', 'docs/daily_report/REPORT-2026-10-07.md'],
    ['docs/live_usage/LIVE-2026-10-07.json', 'docs/live_usage/LIVE-2026-10-07.md',
     'docs/live_usage/LIVE-latest.json', 'docs/live_usage/LIVE-latest.md'],
]
for g in groups:
    side, jb = pick_side_json(g[0])
    write(g[0], jb)
    for twin in g[1:]:
        write(twin, stage_bytes(twin, side))
    print(f'  group side={side} -> {len(g)} twins written')

# --- dashboard twins: js wrapper + json MUST take same side (R209 family) ---
side, jb = pick_side_json('results/dashboard_status.json')
write('results/dashboard_status.json', jb)
write('results/dashboard_status.js', stage_bytes('results/dashboard_status.js', side))
print(f'  dashboard pair side={side} (js byte-copied, wrapper preserved)')

# --- plain snapshots ---
for p in ['results/fundamental_b_layer_filter.json',
          'results/futures_update_status.json',
          'results/lhb_update_status.json',
          'results/scorecard_v1.json',
          'results/strategy_scorecard.json',
          'results/_attrition_guard_scan.json']:
    write(p, take_new_bytes(p))

# --- verify: every written json file parses; md twins are markdown (byte-copied, no json check) ---
for g in groups + [['results/dashboard_status.json']]:
    for p in g:
        if p.endswith('.json'):
            json.load(open(p, encoding='utf-8'))
for p in ['results/fundamental_b_layer_filter.json', 'results/futures_update_status.json',
          'results/lhb_update_status.json', 'results/scorecard_v1.json',
          'results/strategy_scorecard.json', 'results/_attrition_guard_scan.json']:
    json.load(open(p, encoding='utf-8'))
js = open('results/dashboard_status.js', encoding='utf-8').read()
assert js.lstrip().startswith('window.DASH_DATA'), 'js wrapper stripped!'
print('ALL PARSE-VERIFIED + js wrapper intact')
