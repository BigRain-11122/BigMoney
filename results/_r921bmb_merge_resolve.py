import subprocess, json, sys

GIT = r'C:\Program Files\Git\cmd\git.exe'


def run(args, check=True):
    r = subprocess.run([GIT] + args, capture_output=True, text=True, encoding='utf-8')
    if check and r.returncode != 0:
        print('GIT FAIL:', args, r.stderr[:300])
        sys.exit(2)
    return r


def side_pick(path, side):
    run(['checkout', side, '--', path])
    run(['add', path])
    print(f'  {path} -> {side}')


# --- whole-face side picks ---
ours_faces = [
    'fleet/machine-health.json',            # deep max-date 00:11 > 23:36 (r917 law)
    'results/_attrition_guard_scan.json',   # probe ts 00:20:23 > 23:58:02
    'results/_r686bmb_d19_check.json',       # bm-b probe face, r920 advance receipt (bm-b namespace owner)
    'results/d19_watermark.json',           # ts 00:21:15 > 23:23:01 (r920 advance receipt)
    'results/scorecard_v1.json',            # data-identical, ours newer generated (legal stale-takeover derive)
    'results/strategy_scorecard.json',      # data-identical, ours newer generated
    'results/fundamental_b_layer_filter.json',  # ts 00:15:43 > 23:13:23, deterministic regen
    'results/futures_update_status.json',   # ts 00:14:40 > 23:11:12
    'results/lhb_update_status.json',       # ts 00:14:39 > 23:11:10
    'results/regime_state.json',            # ts 00:13:22 > 23:09:38
]
theirs_faces = [
    'results/daily_scorecard.json',         # theirs forward_guard as_of 23:13 > ours 21:57 (fresher paper state)
    'results/dashboard_status.json',        # theirs fund_premium age_min 81 < ours 143 + heat 23:11 > 21:51 (bm-a host canonical)
    'results/dashboard_status.js',           # twin of above
    'results/paper_export/latest.json',     # theirs generated_from_state 23:13:30 > ours 21:57:23
]

print('== side picks ==')
for p in ours_faces:
    side_pick(p, '--ours')
for p in theirs_faces:
    side_pick(p, '--theirs')

# --- compute_audit.json: history union + latest=newer ---
print('== compute_audit union ==')
o = json.loads(run(['show', ':2:results/compute_audit.json']).stdout)
t = json.loads(run(['show', ':3:results/compute_audit.json']).stdout)


def row_key(r):
    return json.dumps(r, sort_keys=True, ensure_ascii=False)


union = []
seen = set()
for r in t.get('history', []) + o.get('history', []):
    k = row_key(r)
    if k not in seen:
        seen.add(k)
        union.append(r)
latest = o['latest'] if o['latest'].get('ts', '') > t['latest'].get('ts', '') else t['latest']
merged = {'latest': latest, 'history': union}
with open('results/compute_audit.json', 'w', encoding='utf-8', newline='') as f:
    json.dump(merged, f, ensure_ascii=False, indent=2)
    f.write('\n')
run(['add', 'results/compute_audit.json'])
print(f'  history: ours={len(o["history"])} theirs={len(t["history"])} -> union={len(union)}; latest ts={latest.get("ts")}')

# --- verify no UU left ---
r = run(['ls-files', '-u'])
if r.stdout.strip():
    print('UU REMAINS:', r.stdout)
    sys.exit(2)
print('== all conflicts resolved, zero UU ==')
