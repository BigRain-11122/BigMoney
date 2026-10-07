# _r832bma_resolve.py -- r832 S0 rebase conflict resolver for r831 pick (22-face batch)
# Classes per bigmoney-conflict-resolve skill (classifier 19 GREEN + 3 manual):
#   twins: json deep-ts probe take-new, md byte-copy same side (r327/r329)
#   snapshots: deep-ts probe take-new (r311/D-20260927-09, r100 probe hardening, tie->:2: r140)
#   append-logs: line union zero loss (r188)
#   satengine face/state (UNKNOWN): own-machine daemon live -> :2: (ours-live-wins)
#   attrition_guard_scan: snapshot deep-ts probe take-new
# Stage law: :2: = base side (origin/HEAD), :3: = replay side (r351 directed law).
import json, re, subprocess, sys

def blob(stage, path):
    r = subprocess.run(['git', 'show', f':{stage}:{path}'], capture_output=True)
    if r.returncode != 0:
        return None
    return r.stdout

DT_RE = re.compile(r'^20\d{2}-\d{2}-\d{2}')
KEY_HINTS = ('ts', 'updated', 'generated', 'cutoff', 'date', 'time', 'asof', 'seen', 'at')

def deep_ts(obj, best=''):
    # r311: ts truth may live in nested layers; r100: normalize key, value must look like a datetime
    if isinstance(obj, dict):
        for k, v in obj.items():
            nk = str(k).replace('_', '').replace('-', '').lower()
            if any(nk.startswith(h) for h in KEY_HINTS) and isinstance(v, str) and DT_RE.match(v):
                if v > best:
                    best = v
            best = deep_ts(v, best)
    elif isinstance(obj, list):
        for v in obj:
            best = deep_ts(v, best)
    return best

def write_bytes(path, data):
    with open(path, 'wb') as f:
        f.write(data)

def take_new_json(path):
    b2, b3 = blob(2, path), blob(3, path)
    j2 = json.loads(b2.decode('utf-8')) if b2 else None
    j3 = json.loads(b3.decode('utf-8')) if b3 else None
    t2, t3 = deep_ts(j2), deep_ts(j3)
    side = 2 if t2 >= t3 else 3  # tie -> :2: (r140)
    write_bytes(path, (b2 if side == 2 else b3))
    return f'{path}: t2={t2 or "-"} t3={t3 or "-"} -> :{side}:'

def twin(tj, tm):
    line = take_new_json(tj)  # decides side by json generated_at
    # md byte-copy from SAME side as json pick (r329: no hybrid twins)
    b2, b3 = blob(2, tj), blob(3, tj)
    j2, j3 = json.loads(b2), json.loads(b3)
    side = 2 if deep_ts(j2) >= deep_ts(j3) else 3
    write_bytes(tm, blob(side, tm))
    return line + f' {tm}: byte-copy :{side}:'

def union_lines(path):
    b2, b3 = blob(2, path), blob(3, path)
    l2 = b2.decode('utf-8', 'replace').splitlines() if b2 else []
    l3 = b3.decode('utf-8', 'replace').splitlines() if b3 else []
    seen, out = set(), []
    for ln in l2 + l3:
        if ln not in seen:
            seen.add(ln)
            out.append(ln)
    data = ('\n'.join(out) + '\n').encode('utf-8')
    write_bytes(path, data)
    return f'{path}: union |A|={len(l2)} |B|={len(l3)} -> {len(out)} (loss=0)'

def take_stage(path, stage):
    write_bytes(path, blob(stage, path))
    return f'{path}: take :{stage}: (ours-live-wins)'

report = []
# twins (r327/r329)
report.append(twin('docs/daily_report/REPORT-2026-10-07.json', 'docs/daily_report/REPORT-2026-10-07.md'))
report.append(twin('docs/live_usage/LIVE-2026-10-07.json', 'docs/live_usage/LIVE-2026-10-07.md'))
report.append(twin('docs/live_usage/LIVE-latest.json', 'docs/live_usage/LIVE-latest.md'))
# snapshots (deep-ts take-new)
for p in ['results/dashboard_status.json', 'results/fundamental_b_layer_filter.json',
          'results/scorecard_v1.json', 'results/strategy_scorecard.json',
          'results/_attrition_guard_scan.json']:
    report.append(take_new_json(p))
# append-logs (union)
for p in ['results/pool_core_samples.jsonl', 'results/saturation_engine/history_bm-a.jsonl',
          'results/saturation_engine/ledger_bm-a.jsonl']:
    report.append(union_lines(p))
# own-machine daemon live faces (UNKNOWN -> live wins = :2:)
report.append(take_stage('results/saturation_engine/face_bm-a.json', 2))
report.append(take_stage('results/saturation_engine/state_bm-a.json', 2))
for r in report:
    print(r)
# parse-verify every json touched (r185)
for p in ['results/dashboard_status.json', 'results/fundamental_b_layer_filter.json',
          'results/scorecard_v1.json', 'results/strategy_scorecard.json',
          'results/_attrition_guard_scan.json', 'results/saturation_engine/face_bm-a.json',
          'results/saturation_engine/state_bm-a.json',
          'docs/daily_report/REPORT-2026-10-07.json', 'docs/live_usage/LIVE-2026-10-07.json',
          'docs/live_usage/LIVE-latest.json']:
    json.load(open(p, encoding='utf-8'))
print('PARSE-VERIFY OK (10 json)')
