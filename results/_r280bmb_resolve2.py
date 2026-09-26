# r280bm-b rebase collision resolver #2: results/autofill_state.json
# mixed-dict+ledger (skill recipe r203/R208/r215/r220): launches union by ts,
# cap 50 (keep newest), write back RE-SORTED ts ASC (r245 law: producer append
# order face); last_tick = whole-dict by inner ts compare (same-second tie ->
# HEAD side = theirs-during-rebase... actually ours-vs-theirs read from blobs);
# EOL/indent mirror base blob; parse-verify before write (r185 law).
import json, subprocess, sys

PATH = 'results/autofill_state.json'

def blob(rev):
    r = subprocess.run(['git', 'show', rev + ':' + PATH], capture_output=True)
    if r.returncode != 0:
        print('FATAL read', rev, r.stderr.decode('utf-8', 'replace')); sys.exit(1)
    return r.stdout

# during rebase: HEAD-side = upstream (origin face), the commit being applied = mine
theirs = blob('HEAD')      # upstream lineage (bm-a faces + prior)
mine = blob('REBASE_HEAD') if False else None
# REBASE_HEAD not always addressable in this git; use the replayed commit sha
sha = subprocess.run(['git', 'log', '-1', '--format=%H', 'REBASE_HEAD'],
                     capture_output=True, text=True).stdout.strip()
mine = blob(sha or 'HEAD')

def load(b):
    return json.loads(b.decode('utf-8-sig'))

A, B = load(theirs), load(mine)

la, lb = A.get('launches', []), B.get('launches', [])
seen, union = set(), []
for x in la + lb:
    k = (x.get('ts'), x.get('machine'), x.get('shard') or x.get('entry'),
         x.get('verdict'))
    if k not in seen:
        seen.add(k)
        union.append(x)
union.sort(key=lambda x: x.get('ts', ''), reverse=True)
union = union[:50]
union.sort(key=lambda x: x.get('ts', ''))   # r245: write back ts ASC

ta, tb = A.get('last_tick', {}), B.get('last_tick', {})
ta_ts, tb_ts = str(ta.get('ts', '')), str(tb.get('ts', ''))
last = ta if ta_ts >= tb_ts else tb        # same-second tie -> HEAD-side (upstream A)

merged = dict(A)
for k in B:
    if k not in ('launches', 'last_tick'):
        merged[k] = B[k]
merged['launches'] = union
merged['last_tick'] = last
assert isinstance(merged['last_tick'], dict), 'last_tick must stay a dict'

base_blob = theirs
indent = 1
try:
    second = base_blob.decode('utf-8-sig').splitlines()[1]
    indent = len(second) - len(second.lstrip(' '))
except Exception:
    pass
crlf = b'\r\n' in base_blob
bom = base_blob.startswith(b'\xef\xbb\xbf')
tail_nl = base_blob.endswith(b'\n')
out = json.dumps(merged, ensure_ascii=False, indent=indent)
out_b = out.encode('utf-8')
if crlf:
    out_b = out_b.replace(b'\n', b'\r\n')
if bom:
    out_b = b'\xef\xbb\xbf' + out_b
if tail_nl and not out_b.endswith(b'\n'):
    out_b += b'\n'
with open(PATH, 'wb') as f:
    f.write(out_b)
json.loads(open(PATH, 'rb').read().decode('utf-8-sig'))   # r185 parse-verify
print('OK autofill_state resolved: launches union=%d (pre A=%d B=%d), last_tick ts=%s, crlf=%s indent=%d bom=%s'
      % (len(union), len(la), len(lb), last.get('ts'), crlf, indent, bom))
