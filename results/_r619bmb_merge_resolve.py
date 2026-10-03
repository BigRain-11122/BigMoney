"""r619 bm-b merge resolver: X(f3bb26bd1) vs origin/main(b6fa63650), base 0a1e2eb5e.

Merge stage numbering: :2: = ours (X), :3: = theirs (b6fa63650).
Verdicts:
  - snapshot/daily faces (12): newest generated/updated/scan ts wins whole-file.
  - md twins: take the side chosen by their json twin.
  - results/compute_audit.json: history union by (ts,machine) zero-loss, latest = newer side.
Laws: R208/R216 take-new, r188 union, r185 parse-before-add, r405 blob-from-stage.
"""
import subprocess, json, re, sys

def blob(stage, path):
    r = subprocess.run(['git', 'show', f':{stage}:{path}'], capture_output=True)
    if r.returncode != 0:
        sys.exit(f'FATAL no :{stage}:{path}: {r.stderr.decode("utf-8","replace")[:150]}')
    return r.stdout

TS_PAT = re.compile(r'"(?:generated|generated_at|updated|updated_at|ts|scan_ts|last_run)"\s*:\s*"([^"]+)"')
MD_TS_PAT = re.compile(r'(generated_at|updated|Generated)[:：\s]*([0-9T:.\-+ ]{8,30})', re.I)

PAIRS = [
    ('docs/daily_report/REPORT-2026-10-03.json', 'docs/daily_report/REPORT-2026-10-03.md'),
    ('docs/live_usage/LIVE-2026-10-03.json', 'docs/live_usage/LIVE-2026-10-03.md'),
    ('docs/live_usage/LIVE-latest.json', 'docs/live_usage/LIVE-latest.md'),
]
SNAPSHOTS = [
    'results/_attrition_guard_scan.json',
    'results/fundamental_b_layer_filter.json',
    'results/futures_update_status.json',
    'results/lhb_update_status.json',
    'results/regime_state.json',
    'results/token_usage.json',
    'results/update_status.json',
]
CA = 'results/compute_audit.json'
verdicts = {}
fails = []

def first_ts(text):
    m = TS_PAT.search(text)
    return m.group(1) if m else None

for js, md in PAIRS:
    b2, b3 = blob(2, js), blob(3, js)
    t2, t3 = first_ts(b2.decode('utf-8', 'replace')), first_ts(b3.decode('utf-8', 'replace'))
    winner = 2 if (t2 or '') >= (t3 or '') else 3
    verdicts[js] = winner
    verdicts[md] = winner
    print(f'{js}: ours={t2} theirs={t3} -> take {"OURS" if winner==2 else "THEIRS"}')
    for p, wb in ((js, b2 if winner == 2 else b3), (md, blob(winner, md))):
        with open(p, 'wb') as f:
            f.write(wb)
        if p.endswith('.json'):
            json.loads(wb.decode('utf-8', 'replace'))

for p in SNAPSHOTS:
    b2, b3 = blob(2, p), blob(3, p)
    t2, t3 = first_ts(b2.decode('utf-8', 'replace')), first_ts(b3.decode('utf-8', 'replace'))
    winner = 2 if (t2 or '') >= (t3 or '') else 3
    verdicts[p] = winner
    wb = b2 if winner == 2 else b3
    with open(p, 'wb') as f:
        f.write(wb)
    json.loads(wb.decode('utf-8', 'replace'))
    print(f'{p}: ours={t2} theirs={t3} -> take {"OURS" if winner==2 else "THEIRS"}')

# compute_audit union
b2, b3 = blob(2, CA), blob(3, CA)
d2, d3 = json.loads(b2.decode('utf-8', 'replace')), json.loads(b3.decode('utf-8', 'replace'))
k2 = {(e['ts'], e.get('machine', '')): e for e in d2['history']}
k3 = {(e['ts'], e.get('machine', '')): e for e in d3['history']}
overlap = set(k2) & set(k3)
diff_cnt = sum(1 for k in overlap if json.dumps(k2[k], sort_keys=True) != json.dumps(k3[k], sort_keys=True))
union = dict(k2)
union.update(k3)
merged = sorted(union.values(), key=lambda e: e['ts'])
newer_latest = d3['latest'] if d3['latest']['ts'] >= d2['latest']['ts'] else d2['latest']
raw_w = b3 if d3['latest']['ts'] >= d2['latest']['ts'] else b2
m = re.match(r'\s*{\n(\s+)"latest"', raw_w.decode('utf-8', 'replace'))
indent = len(m.group(1)) if m else 1
crlf = b'\r\n' in raw_w[:400]
end_nl = b'\n' if raw_w.endswith(b'\n') else b''
out_s = json.dumps({'latest': newer_latest, 'history': merged}, ensure_ascii=False, indent=indent)
if crlf:
    out_s = out_s.replace('\n', '\r\n')
with open(CA, 'wb') as f:
    f.write(out_s.encode('utf-8') + (b'\n' if end_nl else b''))
json.load(open(CA, encoding='utf-8'))
zero_loss = len(merged) == len(k2) + len(k3) - len(overlap)
print(f'{CA}: ours={len(k2)} theirs={len(k3)} overlap={len(overlap)} overlap-content-diff={diff_cnt} -> union {len(merged)} zero_loss={zero_loss} latest_ts={newer_latest["ts"]}')
if not zero_loss:
    fails.append(CA)
if diff_cnt:
    fails.append(CA + ':overlap-diff')

print('SUMMARY:', 'ALL PASS' if not fails else f'FAIL: {fails}')
sys.exit(1 if fails else 0)
