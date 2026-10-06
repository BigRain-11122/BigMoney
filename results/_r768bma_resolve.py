# r768 bm-a merge-conflict resolver: snapshot/unknown/twin faces (deep-ts probe take-new)
# Laws: r311 deep-scan nested ts / r319 probe-path existence / r756 strptime-normalized compare
#       r98/r99/r100 twin-side coupling / r329 md-twin byte-copy from SAME side
#       r767 precedent: _attrition_guard_scan newer-wins
import subprocess, json, sys
from datetime import datetime

def stage_bytes(path, stage):
    r = subprocess.run(['git', 'show', f':{stage}:{path}'], capture_output=True)
    if r.returncode != 0:
        raise RuntimeError(f'stage {stage} read fail: {r.stderr[:200]}')
    return r.stdout

def norm_ts(v):
    if not isinstance(v, str) or len(v) < 19 or not v.startswith('20'):
        return None
    s = v.strip()
    # r756: mixed separators -> normalize space->T before strptime; keep offset if present
    if 'T' not in s[:11]:
        s = s[:10] + 'T' + s[11:]
    try:
        d = datetime.fromisoformat(s)
    except ValueError:
        try:
            d = datetime.fromisoformat(s[:19])
        except ValueError:
            return None
    # tz-uniform compare law (r756 kin): naive -> assume local +08:00, compare must be uniform aware
    from datetime import timezone, timedelta
    if d.tzinfo is None:
        d = d.replace(tzinfo=timezone(timedelta(hours=8)))
    return d

def deep_max_ts(obj):
    best = None
    def scan(o):
        nonlocal best
        if isinstance(o, dict):
            for k, v in o.items():
                if isinstance(v, str):
                    t = norm_ts(v)
                    if t and (best is None or t > best):
                        best = t
                else:
                    scan(v)
        elif isinstance(o, list):
            for v in o:
                scan(v)
    scan(obj)
    return best

def pick_newer(path):
    """snapshot: json both stages, deep-ts compare, write newer side verbatim bytes."""
    ours, theirs = stage_bytes(path, 2), stage_bytes(path, 3)
    jo, jt = json.loads(ours), json.loads(theirs)
    to, tt = deep_max_ts(jo), deep_max_ts(jt)
    if to is None and tt is None:
        side, why = 2, 'both no-ts -> HEAD (r140 tie law)'
    elif to is None:
        side, why = 3, 'ours no-ts'
    elif tt is None:
        side, why = 2, 'theirs no-ts'
    elif to == tt:
        side, why = 2, f'ts tie {to.isoformat()} -> HEAD (r140)'
    else:
        side, why = (2, f'ours newer {to.isoformat()} > {tt.isoformat()}') if to > tt else (3, f'theirs newer {tt.isoformat()} > {to.isoformat()}')
    blob = ours if side == 2 else theirs
    with open(path, 'wb') as f:
        f.write(blob)
    json.loads(blob)  # parse-verify before add (r185)
    print(f'[take-new] {path}: side={":2:ours" if side==2 else ":3:theirs"} ({why})')
    return side

def resolve_twin(json_path, md_paths):
    """twin-regen: pick side by json deep-ts; md twins byte-copied from SAME side blob."""
    ours, theirs = stage_bytes(json_path, 2), stage_bytes(json_path, 3)
    to = deep_max_ts(json.loads(ours))
    tt = deep_max_ts(json.loads(theirs))
    if to is None and tt is None:
        side, why = 2, 'both no-ts -> HEAD'
    elif tt is None or (to is not None and to >= tt):
        side = 2
        why = f'ours {to} >= theirs {tt}' if tt else f'ours {to}, theirs no-ts'
    else:
        side, why = 3, f'theirs {tt} > ours {to}'
    blob = ours if side == 2 else theirs
    with open(json_path, 'wb') as f:
        f.write(blob)
    json.loads(blob)
    print(f'[twin] {json_path}: side={":2:ours" if side==2 else ":3:theirs"} ({why})')
    for md in md_paths:
        b = stage_bytes(md, side)
        with open(md, 'wb') as f:
            f.write(b)
        print(f'[twin-md] {md}: byte-copied from SAME side {":2" if side==2 else ":3"} ({len(b)}B)')
    return side

def resolve_live_group():
    """All 4 LIVE-* twins MUST take the SAME side (r439): decide on dated json + latest json jointly."""
    probes = ['docs/live_usage/LIVE-2026-10-06.json', 'docs/live_usage/LIVE-latest.json']
    to_best, tt_best = None, None
    for p in probes:
        jo = json.loads(stage_bytes(p, 2)); jt = json.loads(stage_bytes(p, 3))
        a, b = deep_max_ts(jo), deep_max_ts(jt)
        if a and (to_best is None or a > to_best): to_best = a
        if b and (tt_best is None or b > tt_best): tt_best = b
    if tt_best and (to_best is None or tt_best > to_best):
        side, why = 3, f'theirs {tt_best} > ours {to_best}'
    else:
        side, why = 2, f'ours {to_best} >= theirs {tt_best}'
    for p in ['docs/live_usage/LIVE-2026-10-06.json', 'docs/live_usage/LIVE-2026-10-06.md',
              'docs/live_usage/LIVE-latest.json', 'docs/live_usage/LIVE-latest.md']:
        b = stage_bytes(p, side)
        if p.endswith('.json'):
            json.loads(b)
        with open(p, 'wb') as f:
            f.write(b)
        print(f'[live-group] {p}: SAME side {":2:ours" if side==2 else ":3:theirs"} ({why}, {len(b)}B)')

if __name__ == '__main__':
    print(f'resolver start: {datetime.now().isoformat(timespec="seconds")}')
    # snapshot faces (fail-closed from ALL_FACES registry; per-run verdict snapshots)
    pick_newer('results/fundamental_b_layer_filter.json')
    pick_newer('results/_attrition_guard_scan.json')
    # twin-regen faces
    resolve_twin('docs/daily_report/REPORT-2026-10-06.json', ['docs/daily_report/REPORT-2026-10-06.md'])
    resolve_live_group()
    print('resolver done OK')
