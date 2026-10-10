# r962 rebase conflict resolver (canon: bigmoney-conflict-resolve SKILL.md)
# Laws: r100 hardened deep-ts probe (normalize key strip _/-; value must be ^20\d{2}- WITH time-of-day
# for wall-clock probes; date-only must NOT feed max); R350 no key-exclude lists; r311 deep-scan nested;
# r319 probe path existence first; twins take SAME side (json probe decides, md byte-copied same side).
# d19_watermark.json: manual adjudicated = take :2: (origin ts 21:16:28 > local 21:05:27, identical
# watermark shas a20664ec/5437bc4e -> zero information loss).
import subprocess, json, re, sys

def blob(stage, path):
    r = subprocess.run(['git', 'show', f':{stage}:{path}'], capture_output=True)
    if r.returncode != 0:
        return None
    return r.stdout  # bytes

TS_SHAPE = re.compile(r'^20\d{2}-')

def deep_ts_probe(obj, best):
    """Collect ts-shaped wall-clock values (must contain T or space HH:MM) from nested layers."""
    if isinstance(obj, dict):
        for k, v in obj.items():
            nk = str(k).replace('_', '').replace('-', '').lower()
            if isinstance(v, str) and TS_SHAPE.match(v) and (re.search(r'[T ]\d{2}:\d{2}', v)):
                if best[0] is None or v > best[0]:
                    best[0] = v
            else:
                deep_ts_probe(v, best)
    elif isinstance(obj, list):
        for v in obj:
            deep_ts_probe(v, best)

def pick_newer(path):
    b2, b3 = blob(2, path), blob(3, path)
    ts2 = ts3 = None
    try:
        deep_ts_probe(json.loads(b2), [ts2 := None]); ts2 = [None]; deep_ts_probe(json.loads(b2), ts2)
    except Exception:
        ts2 = [None]
    try:
        ts3 = [None]; deep_ts_probe(json.loads(b3), ts3)
    except Exception:
        ts3 = [None]
    t2 = ts2[0] if isinstance(ts2, list) else None
    t3 = ts3[0] if isinstance(ts3, list) else None
    if t3 is not None and (t2 is None or t3 >= t2):
        return 3, b3, t3, t2
    return 2, b2, t2, t3

def write(path, data):
    with open(path, 'wb') as f:
        f.write(data)
    json.loads(open(path, 'rb').read())  # parse-verify before add (r185)

report = {}
# --- snapshot files: hardened deep-ts probe, staged blobs only ---
SNAPSHOTS = [
    'results/scorecard_v1.json',
    'results/strategy_scorecard.json',
    'results/_attrition_guard_scan.json',
]
for p in SNAPSHOTS:
    side, data, tw, tl = pick_newer(p)
    write(p, data)
    report[p] = {'side': f':{side}:', 'ts': tw, 'other_ts': tl}

# --- twins: json probe decides, md byte-copied from SAME side ---
TWINS = [
    ('docs/daily_report/REPORT-2026-10-10.json', 'docs/daily_report/REPORT-2026-10-10.md'),
    ('docs/live_usage/LIVE-2026-10-10.json', 'docs/live_usage/LIVE-2026-10-10.md'),
    ('docs/live_usage/LIVE-latest.json', 'docs/live_usage/LIVE-latest.md'),
]
for jp, mp in TWINS:
    side, data, tw, tl = pick_newer(jp)
    write(jp, data)
    md = blob(side, mp)
    with open(mp, 'wb') as f:
        f.write(md)
    report[f'{jp} (+md twin)'] = {'side': f':{side}:', 'ts': tw, 'other_ts': tl}

# --- d19_watermark.json: manual adjudication (identical shas, take newer receipt ts) ---
d2 = blob(2, 'results/d19_watermark.json')
write('results/d19_watermark.json', d2)
report['results/d19_watermark.json'] = {'side': ':2:', 'reason': 'identical watermark shas both sides; newer receipt ts 21:16:28 > 21:05:27'}

print(json.dumps(report, ensure_ascii=False, indent=1))
