import subprocess, json, sys

GIT = r'C:\Program Files\Git\cmd\git.exe'


def run(args, check=True):
    r = subprocess.run([GIT] + args, capture_output=True, text=True, encoding='utf-8')
    if check and r.returncode != 0:
        print('GIT FAIL:', args, r.stderr[:300])
        sys.exit(2)
    return r


theirs = ['results/futures_update_status.json', 'results/lhb_update_status.json',
          'results/regime_state.json', 'results/update_status.json',
          'results/scorecard_v1.json', 'results/strategy_scorecard.json']
ours = ['results/queue_head_collision_probe.json']

for p in theirs + ours:
    side = '--theirs' if p in theirs else '--ours'
    run(['checkout', side, '--', p])
    run(['add', p])
    print(f'  {p} -> {side}')

# compute_audit union + latest=newer
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
latest = t['latest'] if t['latest'].get('ts', '') > o['latest'].get('ts', '') else o['latest']
with open('results/compute_audit.json', 'w', encoding='utf-8', newline='') as f:
    json.dump({'latest': latest, 'history': union}, f, ensure_ascii=False, indent=2)
    f.write('\n')
run(['add', 'results/compute_audit.json'])
print(f'  compute_audit union: {len(o["history"])}+{len(t["history"])} -> {len(union)}, latest={latest.get("ts")}')

r = run(['ls-files', '-u'])
if r.stdout.strip():
    print('UU REMAINS:', r.stdout)
    sys.exit(2)
print('zero UU, ready to conclude')
