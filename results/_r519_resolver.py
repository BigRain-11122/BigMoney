# r519 rebase resolver: same-window dual-machine S6 derive-face collision (r505 recipe)
# classes: ts-newer for idempotent rewrite faces; EOF-union for CODELY; claims-union for T-141; sig-union for crash_fuse
import subprocess, json, re, sys

def stage(side, path):
    return subprocess.check_output(['git', 'show', side + path])

TS_RE = re.compile(r'"(?:ts|generated_at|updated|generated|asof|written_at)"\s*:\s*"([0-9T:.+\- ]+)"')

def ts_of(b):
    s = b.decode('utf-8-sig', errors='replace')
    m = TS_RE.findall(s)
    return max(m) if m else ''

DERIVE = [
    'docs/daily_report/REPORT-2026-10-01.json', 'docs/daily_report/REPORT-2026-10-01.md',
    'docs/live_usage/LIVE-2026-10-01.json', 'docs/live_usage/LIVE-2026-10-01.md',
    'docs/live_usage/LIVE-latest.json', 'docs/live_usage/LIVE-latest.md',
    'results/_attrition_guard_scan.json', 'results/compute_audit.json',
    'results/dashboard_status.js', 'results/dashboard_status.json',
    'results/fundamental_b_layer_filter.json', 'results/futures_update_status.json',
    'results/lhb_update_status.json', 'results/regime_state.json',
    'results/scorecard_v1.json', 'results/strategy_scorecard.json',
    'results/token_usage.json', 'results/update_status.json',
]

for p in DERIVE:
    o = stage(':2:', p)   # ours = origin/bm-b side
    t = stage(':3:', p)   # theirs = my commit side
    to, tt = ts_of(o), ts_of(t)
    pick, side = (t, 'mine') if (tt and (not to or tt >= to)) else (o, 'origin')
    open(p, 'wb').write(pick)
    print(p, '->', side, '| origin_ts=', to, 'mine_ts=', tt)

# CODELY.md: EOF row union (base + origin rows + my row)
o = stage(':2:', 'CODELY.md').decode('utf-8-sig').rstrip('\n')
t = stage(':3:', 'CODELY.md').decode('utf-8-sig').rstrip('\n')
base = subprocess.check_output(['git', 'show', ':1:CODELY.md']).decode('utf-8-sig').rstrip('\n')
o_rows = [r for r in o.split('\n') if r not in base.split('\n')]
t_rows = [r for r in t.split('\n') if r not in base.split('\n')]
union = base + ('\n' + '\n'.join(o_rows + t_rows) if (o_rows or t_rows) else '')
open('CODELY.md', 'w', encoding='utf-8', newline='').write(union + '\n')
print('CODELY union: origin rows', len(o_rows), '+ mine rows', len(t_rows))

# T-141: claims dict union
p = 'fleet/tasks/T-2026-10-01-141-P1.json'
o = json.loads(stage(':2:', p).decode('utf-8-sig'))
t = json.loads(stage(':3:', p).decode('utf-8-sig'))
t.setdefault('claims', {}).update(o.get('claims', {}))
open(p, 'w', encoding='utf-8', newline='').write(json.dumps(t, ensure_ascii=False, indent=1) + '\n')
print('T-141 claims union keys:', sorted(t.get('claims', {}).keys()))

# crash_fuse.json: sig-key union
p = 'results/crash_fuse.json'
o = json.loads(stage(':2:', p).decode('utf-8-sig'))
t = json.loads(stage(':3:', p).decode('utf-8-sig'))
merged = dict(o)
for k, v in t.items():
    if k in merged and isinstance(merged[k], dict) and isinstance(v, dict):
        mk = dict(merged[k])
        mk.update(v)
        merged[k] = mk
    else:
        merged[k] = v
open(p, 'w', encoding='utf-8', newline='').write(json.dumps(merged, ensure_ascii=False, indent=1) + '\n')
print('crash_fuse top-key union:', sorted(merged.keys()))
