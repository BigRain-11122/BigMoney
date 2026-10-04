# r692 bm-b probe5: full pool diff N2 hunks (no truncation) + bm-a heartbeat origin-truth
import subprocess, json

# 1. full diff of runnable_pool.json between pre-merge r691 close (ec6b78963) and current HEAD
r = subprocess.run(['git', 'diff', 'ec6b78963', 'HEAD', '--', 'results/runnable_pool.json'],
                   capture_output=True, text=True, encoding='utf-8')
diff = r.stdout or ''
n2hunks = []
cur = []
keep = False
for ln in diff.splitlines():
    if ln.startswith('@@'):
        if keep and cur:
            n2hunks.append('\n'.join(cur))
        cur = [ln]
        keep = False
    else:
        cur.append(ln)
        if 'GENERATE' in ln or 'generate-0of1' in ln or 'n2-w15' in ln:
            keep = True
if keep and cur:
    n2hunks.append('\n'.join(cur))

# 2. bm-a heartbeat via origin (subprocess raw bytes)
r2 = subprocess.run(['git', 'show', 'origin/main:fleet/machines/bm-a.json'], capture_output=True)
hb_a = json.loads(r2.stdout.decode('utf-8')) if r2.returncode == 0 else {}

out = {
    'n2_related_hunks': n2hunks,
    'hunk_count': len(n2hunks),
    'bm_a': {'last_seen': hb_a.get('last_seen'), 'verdict': hb_a.get('verdict'),
             'current_task': (hb_a.get('current_task') or '')[:600]},
}
with open('results/_r692bmb_dualclaim_evidence.json', 'w', encoding='utf-8') as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
print('hunks:', len(n2hunks))
for h in n2hunks:
    print(h[:1200])
    print('=====')
print('bm-a hb last_seen:', hb_a.get('last_seen'))
print('bm-a task:', (hb_a.get('current_task') or '')[:500])
