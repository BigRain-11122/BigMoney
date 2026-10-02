import subprocess, os, sys, json

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(REPO)

def run(args, env=None, binary=False):
    r = subprocess.run(args, capture_output=True, env=env)
    if r.returncode != 0:
        print('FAIL', args[:3], r.stderr.decode('utf-8','replace')[:300]); sys.exit(1)
    return r.stdout

ORIGIN = run(['git','rev-parse','origin/main']).decode().strip()

# --- union 1: pool_core_samples.jsonl (r570 law: origin base + local-only dict lines) ---
origin_pool = run(['git','show',ORIGIN+':results/pool_core_samples.jsonl'])
origin_lines = [l for l in origin_pool.decode('utf-8').splitlines() if l.strip()]
origin_set = set(origin_lines)
local_pool = open('results/pool_core_samples.jsonl','rb').read().decode('utf-8')
local_lines = [l for l in local_pool.splitlines() if l.strip()]
kept = []
for l in local_lines:
    if l in origin_set: continue
    try:
        if isinstance(json.loads(l), dict): kept.append(l)
    except Exception: pass
nl = '\r\n' if b'\r\n' in origin_pool else '\n'
pool_bytes = (nl.join(origin_lines + kept) + nl).encode('utf-8')
pool_blob = run(['git','hash-object','-w','--stdin'], env=dict(os.environ, GIT_INDEX_FILE=''), _=None) if False else None
# hash-object via stdin:
import tempfile
tf = os.path.abspath('_tmp_pool_union.jsonl')
open(tf,'wb').write(pool_bytes)
pool_blob = run(['git','hash-object','-w',tf]).decode().strip()
os.remove(tf)
print('pool union:', len(origin_lines), '+', len(kept), '=', len(origin_lines)+len(kept), 'blob', pool_blob[:12])

# --- union 2: CODELY.md (origin bytes + my r580 entries appended) ---
origin_c = run(['git','show',ORIGIN+':CODELY.md']).decode('utf-8')
mine_c = run(['git','show','HEAD:CODELY.md']).decode('utf-8')
marker = '- [2026-10-02 14:5x r580 bm-a]'
i = mine_c.find(marker)
assert i >= 0, 'r580 marker not found in HEAD CODELY'
my_entries = mine_c[i:]
assert marker not in origin_c, 'origin already has r580 entries'
codely_bytes = (origin_c + my_entries).encode('utf-8')
if not origin_c.endswith('\n'): codely_bytes = (origin_c + '\n' + my_entries).encode('utf-8')
tf2 = os.path.abspath('_tmp_codely_union.md')
open(tf2,'wb').write(codely_bytes)
codely_blob = run(['git','hash-object','-w',tf2]).decode().strip()
os.remove(tf2)
print('codely union blob', codely_blob[:12])

# --- payload assembly ---
PAYLOAD = {}  # path -> (mode, sha)
def head_ls(path):
    out = run(['git','ls-tree','HEAD','--',path]).decode().strip()
    parts = out.split('\t')
    meta = parts[0].split(' ')
    return meta[0], meta[2]

for p in ['fleet/machines/bm-a.json','results/_attrition_guard_scan.json',
          'results/autofill_state.bm-a.json','results/compute_audit.bm-a.json',
          'results/compute_audit.json','results/pool_dualrun.bm-a.jsonl',
          'results/saturation_engine/face_bm-a.json','results/saturation_engine/history_bm-a.jsonl',
          'results/saturation_engine/ledger_bm-a.jsonl','results/saturation_engine/state_bm-a.json',
          'round_reports-bm-a.md','state-bm-a.json']:
    m, s = head_ls(p)
    PAYLOAD[p] = (m, s)
PAYLOAD['results/pool_core_samples.jsonl'] = ('100644', pool_blob)
PAYLOAD['CODELY.md'] = ('100644', codely_blob)
# n1_w94 shards: all current working-tree files (HEAD-committed 0-2 + newer)
wdir = 'results/p2cal_ext/n1_w94'
for fn in sorted(os.listdir(wdir)):
    fp = os.path.join(wdir, fn)
    b = run(['git','hash-object','-w',fp]).decode().strip()
    PAYLOAD[wdir+'/'+fn] = ('100644', b)
print('payload files:', len(PAYLOAD))

# --- surgical index ---
env = dict(os.environ); env['GIT_INDEX_FILE'] = os.path.abspath('_tmp_surg3')
if os.path.exists('_tmp_surg3'): os.remove('_tmp_surg3')
run(['git','read-tree',ORIGIN], env=env)
for p,(m,s) in PAYLOAD.items():
    run(['git','update-index','--add','--cacheinfo',f'{m},{s},{p}'], env=env)
tree = run(['git','write-tree'], env=env).decode().strip()

# --- assertions: zero deletions vs origin; delta == payload set ---
d = run(['git','diff-tree','--name-status','-r',ORIGIN,tree]).decode().strip().splitlines()
dels = [l for l in d if l.startswith('D')]
changed = sorted(l.split('\t')[-1] for l in d if l.strip())
assert not dels, 'deletions: %s' % dels
assert changed == sorted(PAYLOAD.keys()), 'delta mismatch: %s' % set(changed)^set(PAYLOAD)
print('assertions: deletions=0, delta==payload (%d files)' % len(changed))

msg = run(['git','log','-1','--format=%B','HEAD']).decode().strip()
new_sha = run(['git','commit-tree',tree,'-p',ORIGIN,'-m',msg], env=env).decode().strip()
print('new_sha:', new_sha)
r = subprocess.run(['git','push','origin',new_sha+':main'], capture_output=True)
print('push rc:', r.returncode, r.stderr.decode('utf-8','replace')[-150:] if r.returncode else 'OK')
print(new_sha)
