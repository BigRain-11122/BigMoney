# r964 marker-contamination REPAIR (P0): rebase --continue committed marker-laden
# faces because resolver run#2 crashed on list-shaped merge-base. Sides from git
# objects: origin-side = f84576913 (bm-c r846 close), estate-side = 10aa56a2b
# (my first-rebase estate commit, resolver#1-clean faces).
# Laws: ALL_FACES -> merge_face union (dict-shaped sides only); dashboard twins
# -> ts-probe + js byte-copy SAME side (r943/r952 canon).
import subprocess, json, re, sys, os

GIT = r"C:\Program Files\Git\cmd\git.exe"
ORIGIN_SIDE = 'f84576913'
ESTATE_SIDE = '10aa56a2b'

def show(ref, path):
    r = subprocess.run([GIT, 'show', f'{ref}:{path}'], capture_output=True)
    return r.stdout if r.returncode == 0 else None

TS_SHAPE = re.compile(r'^20\d{2}-')

def deep_ts_probe(obj, best):
    if isinstance(obj, dict):
        for k, v in obj.items():
            if isinstance(v, str) and TS_SHAPE.match(v) and re.search(r'[T ]\d{2}:\d{2}', v):
                if best[0] is None or v > best[0]:
                    best[0] = v
            else:
                deep_ts_probe(v, best)
    elif isinstance(obj, list):
        for v in obj:
            deep_ts_probe(v, best)

def write(path, data):
    with open(path, 'wb') as f:
        f.write(data)
    if path.endswith('.json'):
        json.loads(open(path, 'rb').read())
    # marker scan (the gate this repair exists for)
    assert b'<<<<<<<' not in data and b'>>>>>>>' not in data, f'markers in {path}'

report = {}
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'scripts'))
import merge_lane_views as mlv

ALLFACE_FILES = [
    'results/compute_audit.json',
    'results/regime_state.json',
    'results/update_status.json',
    'results/lhb_update_status.json',
    'results/futures_update_status.json',
    'results/token_usage.json',
]
def unwrap(obj):
    """Estate-side faces from resolver#1 are tuple-wrapped [merged, notes] --
    element[0] is the proper merged dict. Unwrap to merge-able shape."""
    if isinstance(obj, list) and len(obj) == 2 and isinstance(obj[0], dict) \
            and isinstance(obj[1], list):
        return obj[0]
    return obj

for p in ALLFACE_FILES:
    face = mlv.detect_face(p)
    sources = []
    for ref, label in ((ORIGIN_SIDE, f'{ORIGIN_SIDE} origin-side'), (ESTATE_SIDE, f'{ESTATE_SIDE} estate-side')):
        b = show(ref, p)
        if b is None:
            continue
        try:
            obj = json.loads(b)
        except Exception:
            continue
        obj = unwrap(obj)
        if not isinstance(obj, dict):
            continue
        sources.append((label, obj))
    if not sources:
        raise SystemExit(f'no dict-shaped side for {p} -- fail-closed')
    merged, notes = mlv.merge_face(face, sources)
    data = json.dumps(merged, ensure_ascii=False, indent=1).encode('utf-8')
    write(p, data)
    report[p] = {'side': 'merge_face union', 'bytes': len(data), 'n_sources': len(sources), 'notes': notes}

# dashboard twins: ts-probe decides, js byte-copied SAME side
for jp, sp in [('results/dashboard_status.json', 'results/dashboard_status.js')]:
    ts = {}
    sides = {}
    for ref in (ORIGIN_SIDE, ESTATE_SIDE):
        b = show(ref, jp)
        if b is None:
            continue
        best = [None]
        try:
            deep_ts_probe(json.loads(b), best)
        except Exception:
            best = [None]
        ts[ref] = best[0]
        sides[ref] = b
    o, e = ts.get(ORIGIN_SIDE), ts.get(ESTATE_SIDE)
    take = ORIGIN_SIDE if (o is not None and (e is None or o >= e)) else ESTATE_SIDE
    write(jp, sides[take])
    js = show(take, sp)
    if js is not None:
        write(sp, js)
    report[f'{jp} (+js twin)'] = {'side': take, 'ts': ts.get(take), 'other_ts': ts.get(ORIGIN_SIDE if take == ESTATE_SIDE else ESTATE_SIDE)}

print(json.dumps(report, ensure_ascii=False, indent=1))
