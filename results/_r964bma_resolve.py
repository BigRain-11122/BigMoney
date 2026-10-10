# r964 rebase conflict resolver (canon: bigmoney-conflict-resolve SKILL.md; r962 bloodline)
# Laws: r140 same-second tie -> :2: (origin/HEAD during rebase, r351 stage map);
# r100 deep-ts probe wall-clock only; twins json probe decides + md byte-copy SAME side;
# ALL_FACES -> merge_lane_views merge_face (union recipes, zero hand-rolled merges).
import subprocess, json, re, sys, os, tempfile

GIT = r"C:\Program Files\Git\cmd\git.exe"

def blob(stage, path):
    r = subprocess.run([GIT, 'show', f':{stage}:{path}'], capture_output=True)
    if r.returncode != 0:
        return None
    return r.stdout  # bytes

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

def pick_newer(path):
    """r140: strict-greater for :3: (local); tie or missing -> :2: (origin)."""
    b2, b3 = blob(2, path), blob(3, path)
    t2 = [None]; t3 = [None]
    try:
        deep_ts_probe(json.loads(b2 or b'null'), t2)
    except Exception:
        t2 = [None]
    try:
        deep_ts_probe(json.loads(b3 or b'null'), t3)
    except Exception:
        t3 = [None]
    if b3 is not None and t3[0] is not None and (t2[0] is None or t3[0] > t2[0]):
        return 3, b3, t3[0], t2[0]
    if b2 is not None:
        return 2, b2, t2[0], t3[0]
    return 3, b3, t3[0], t2[0]

def write(path, data):
    with open(path, 'wb') as f:
        f.write(data)
    if path.endswith('.json'):
        json.loads(open(path, 'rb').read())  # parse-verify before add (r185)

report = {}

# --- 1) ALL_FACES via merge_lane_views merge_face (union recipes) ---
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
for p in ALLFACE_FILES:
    face = mlv.detect_face(p)
    sources = []
    b2, b3, b1 = blob(2, p), blob(3, p), blob(1, p)
    if b2 is not None:
        sources.append((":2: base-side", json.loads(b2)))
    if b3 is not None:
        sources.append((":3: replay-side", json.loads(b3)))
    if b1 is not None:
        sources.append((":1: merge-base", json.loads(b1)))
    merged = mlv.merge_face(face, sources)
    merged = json.dumps(merged, ensure_ascii=False, indent=1).encode('utf-8')
    write(p, merged)
    report[p] = {'side': 'merge_face union', 'bytes': len(merged)}

# --- 2) snapshots: hardened deep-ts probe ---
SNAPSHOTS = [
    'results/_attrition_guard_scan.json',
    'results/daily_scorecard.json',
    'results/fundamental_b_layer_filter.json',
    'results/paper_export/export-2026-10-09.json',
    'results/paper_export/latest.json',
]
for p in SNAPSHOTS:
    side, data, tw, tl = pick_newer(p)
    write(p, data)
    report[p] = {'side': f':{side}:', 'ts': tw, 'other_ts': tl}

# --- 3) twins: json probe decides, md byte-copied from SAME side ---
TWINS = [
    ('docs/daily_report/REPORT-2026-10-11.json', 'docs/daily_report/REPORT-2026-10-11.md'),
    ('docs/live_usage/LIVE-2026-10-11.json', 'docs/live_usage/LIVE-2026-10-11.md'),
    ('docs/live_usage/LIVE-latest.json', 'docs/live_usage/LIVE-latest.md'),
]
for jp, mp in TWINS:
    side, data, tw, tl = pick_newer(jp)
    write(jp, data)
    md = blob(side, mp)
    if md is not None:
        with open(mp, 'wb') as f:
            f.write(md)
    report[f'{jp} (+md twin)'] = {'side': f':{side}:', 'ts': tw, 'other_ts': tl}

print(json.dumps(report, ensure_ascii=False, indent=1))
