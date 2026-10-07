# r804 bm-b pool_red_flags.jsonl recover + satengine live-wins resolve (mid-rebase 3/3 stop)
# Fact-find: marker commit 090b6d877 embedded both sides; recover clean sides from
# base fc367a58e (st2=origin/bm-c-resolved) vs my round commit 2380d6730 (st3).
# Then: tolerant line-union (NO per-line strict json assert -- the assert face that killed
# the resolver mid-script; family: r419 assertion-layer). Dedupe on raw line text.
import subprocess, json, sys

def show(rev, path):
    r = subprocess.run(['git', 'show', rev + ':' + path], capture_output=True)
    if r.returncode != 0:
        print('SHOW FAIL', rev, path, r.stderr.decode('utf-8', 'replace')[:200])
        sys.exit(2)
    return r.stdout

receipt = {}

# ---- 1. pool_red_flags.jsonl tolerant line-union ----
p = 'results/pool_red_flags.jsonl'
b2 = show('fc367a58e', p)
b3 = show('2380d6730', p)
assert b'<<<<<<<' not in b2 and b'<<<<<<<' not in b3, 'marker in source sides'
l2 = b2.decode('utf-8', 'replace').splitlines()
l3 = b3.decode('utf-8', 'replace').splitlines()
seen = set()
merged = []
for ln in l2 + l3:
    s = ln.strip()
    if not s or s in seen:
        continue
    seen.add(s)
    merged.append(ln)
# tolerant validation: raw_decode sweep per line, count compound lines but do NOT abort
compound = 0
dec = json.JSONDecoder()
for ln in merged:
    s = ln.strip()
    try:
        obj, end = dec.raw_decode(s)
        if s[end:].strip():
            compound += 1
    except Exception:
        compound += 1
raw = b2
crlf = b'\r\n' in raw
sep = '\r\n' if crlf else '\n'
with open(p, 'wb') as f:
    f.write((sep.join(merged) + sep).encode('utf-8'))
back = open(p, 'rb').read()
assert b'<<<<<<<' not in back and b'>>>>>>>' not in back and b'=======' not in back, 'marker survived'
receipt[p] = {'recipe': 'jsonl line-union (tolerant)', 'st2_lines': len(l2), 'st3_lines': len(l3),
              'union': len(merged), 'non_strict_lines': compound}
print('pool_red_flags line-union tolerant: %d+%d->%d nonstrict=%d' % (len(l2), len(l3), len(merged), compound))
if compound:
    print('  side2 tail:', l2[-1][:160])
    print('  side3 tail:', l3[-1][:160])
    print('  merged tail:', merged[-1][:160])

# ---- 2. satengine 3 faces: live-wins = st3 (churn commit = newest own-daemon snapshot) ----
def stages_of(path):
    out = subprocess.run(['git', 'ls-files', '-u', '--', path], capture_output=True, text=True).stdout
    res = {}
    for line in out.strip().split('\n'):
        if not line.strip():
            continue
        meta, _, fp = line.partition('\t')
        parts = meta.split()
        if len(parts) >= 3:
            res[parts[2]] = parts[1]
    return res

SAT = ['results/saturation_engine/face_bm-b.json',
       'results/saturation_engine/history_bm-b.jsonl',
       'results/saturation_engine/state_bm-b.json']
for p in SAT:
    st = stages_of(p)
    if not st:
        print('no stages for', p, '(already resolved?)')
        receipt[p] = {'recipe': 'live-wins st3', 'note': 'no stages, skipped'}
        continue
    data = subprocess.run(['git', 'cat-file', '-p', st['3']], capture_output=True).stdout
    if b'<<<<<<<' in data:
        print('MARKER-LEAK ABORT', p)
        sys.exit(2)
    with open(p, 'wb') as f:
        f.write(data)
    receipt[p] = {'recipe': 'live-wins st3 (own daemon newest snapshot, r620 family)',
                  'st2_sha': st['2'][:12], 'st3_sha': st['3'][:12]}
    print('take %-45s <- st3 (live-wins)' % p)

json.dump(receipt, open('results/_r804bmb_tailface_resolve.json', 'w', encoding='utf-8'),
          indent=1, ensure_ascii=False)
r = subprocess.run(['git', 'add', '--', p] + SAT + ['results/_r804bmb_tailface_resolve.json'],
                   capture_output=True, text=True)
if r.returncode != 0:
    print('GIT ADD FAIL:', r.stderr)
    sys.exit(3)
print('tail-face resolver done: %d faces staged' % (len(SAT) + 1))
