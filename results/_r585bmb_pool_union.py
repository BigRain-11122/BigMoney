# r585 bm-b: inspect 14 unioned history_bm-a rows + pool_core_samples union
# (origin verbatim base + local-only rows, r570/r524 domain law)
import subprocess, sys, os, json
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
REPO = r'C:\Fluxgroup\FluxGroup\quant\bigmoney'
os.chdir(REPO)
CREATE = 0x08000000

def run(cmd, check=True):
    r = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8',
                       errors='replace', creationflags=CREATE)
    if check and r.returncode != 0:
        print('FAIL rc=%d: %s' % (r.returncode, ' '.join(cmd)))
        print(r.stderr[-500:]); sys.exit(1)
    return r

# 1. what did the history_bm-a union append? (rows now in worktree beyond origin blob)
rb = subprocess.run(['git', 'show', 'origin/main:results/saturation_engine/history_bm-a.jsonl'],
                     capture_output=True, creationflags=CREATE)
okeys = set(l.rstrip(b'\r\n') for l in rb.stdout.splitlines() if l.strip())
with open('results/saturation_engine/history_bm-a.jsonl', 'rb') as f:
    lb = f.read()
print('--- history_bm-a local rows beyond origin (%d):' %
      sum(1 for l in lb.splitlines() if l.strip() and l.rstrip(b'\r\n') not in okeys))
for l in lb.splitlines():
    if l.strip() and l.rstrip(b'\r\n') not in okeys:
        try:
            o = json.loads(l)
            print('  wave=%s machine=%s shard=%s done_at=%s orphan=%s' % (
                o.get('wave'), o.get('machine'), o.get('shard'),
                o.get('done_at', o.get('ts', ''))[:19], o.get('orphan_reconciled')))
        except Exception as e:
            print('  UNPARSEABLE: %s (%s)' % (l[:100], e))

# 2. pool_core_samples union: origin verbatim + local-only dict rows
rb = subprocess.run(['git', 'show', 'origin/main:results/pool_core_samples.jsonl'],
                    capture_output=True, creationflags=CREATE)
ob = rb.stdout
with open('results/pool_core_samples.jsonl', 'rb') as f:
    lb = f.read()
okeys = set(l.rstrip(b'\r\n') for l in ob.splitlines() if l.strip())
new_rows = []
for l in lb.splitlines():
    if not l.strip() or l.rstrip(b'\r\n') in okeys:
        continue
    obj = json.loads(l)
    assert isinstance(obj, dict), 'non-dict local row'
    new_rows.append(l.rstrip(b'\r\n'))
ub = ob if (not ob or ob.endswith(b'\n')) else ob + b'\n'
ub += b''.join(nr + b'\n' for nr in new_rows)
with open('results/pool_core_samples.jsonl', 'wb') as f:
    f.write(ub)
nl = sum(1 for l in ub.splitlines() if l.strip())
for l in ub.splitlines():
    if l.strip():
        assert isinstance(json.loads(l), dict)
print('pool_core_samples union: origin_rows=%d appended=%d total=%d (all dict)' %
      (len([l for l in ob.splitlines() if l.strip()]), len(new_rows), nl))
r = run(['git', 'diff', '--stat', 'results/pool_core_samples.jsonl'])
print(r.stdout.strip())
