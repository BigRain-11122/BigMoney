# r284 bm-a S0 rebase UU resolver: results/autofill_state.json
# Collision: bm-a 01:30 tick-tail commit (e745df48) vs bm-b r287 S0 tick-tail (origin 25adaf8d)
# Recipe (skill mixed-dict+ledger, law r203/R208/r215/r220/r140/r245):
#   launches = union both stage blobs, identity dedupe + field-merge (zero-loss incl. crash_counted flags)
#              -> sort ts desc -> cap 50 (keep newest) -> re-sort ts asc (producer append order, r245)
#   last_tick = compare inner ts, later wins; same-second tie -> HEAD (stage2/ours = origin side, r140)
#   write-back: mirror stage2 formatting (CRLF, indent, no trailing newline)
import subprocess, json, sys

def blob(sha):
    return subprocess.run(['git','cat-file','blob',sha], capture_output=True, check=True).stdout

S2 = '9ac20292'  # ours = HEAD during rebase = origin/bm-b r287 face
S3 = '570c0fe7'  # theirs = bm-a replayed tick-tail commit

raw2, raw3 = blob(S2), blob(S3)
d2, d3 = json.loads(raw2.decode('utf-8')), json.loads(raw3.decode('utf-8'))

def ident(e):
    return (e.get('ts'), e.get('machine'), e.get('pid'), e.get('entry'), e.get('shard'))

# --- launches union with identity dedupe + field merge (superset wins per key) ---
union = {}
for e in d2.get('launches', []) + d3.get('launches', []):
    k = ident(e)
    if k not in union:
        union[k] = dict(e)
    else:
        merged = dict(union[k])
        for f, v in e.items():
            if f not in merged:
                merged[f] = v
        union[k] = merged
entries = list(union.values())
n_crash = sum(1 for e in entries if e.get('crash_counted'))
entries.sort(key=lambda e: e.get('ts'), reverse=True)
entries = entries[:50]
entries.sort(key=lambda e: e.get('ts'))  # write-back order = ts asc (r245)
assert len(entries) <= 50
assert n_crash == sum(1 for e in entries if e.get('crash_counted')), 'crash_counted flags lost in cap/merge'
ts_list = [e['ts'] for e in entries]
assert ts_list == sorted(ts_list), 'launches not ts-asc after write-back sort'

# --- last_tick: inner-ts compare, tie -> ours(HEAD=origin) ---
lt2, lt3 = d2.get('last_tick'), d3.get('last_tick')
if not isinstance(lt2, dict): lt2 = {}
if not isinstance(lt3, dict): lt3 = {}
ts2, ts3 = str(lt2.get('ts','')), str(lt3.get('ts',''))
last_tick = lt2 if ts2 >= ts3 else lt3  # same-second tie -> stage2/HEAD (r140)
assert isinstance(last_tick, dict)

# --- formatting mirror: indent + CRLF + no trailing newline, from stage2 blob ---
lines2 = raw2.decode('utf-8').split('\n')
indent = len(lines2[1]) - len(lines2.lstrip) if False else (len(lines2[1]) - len(lines2[1].lstrip()))
crlf = b'\r\n' in raw2
trailing_nl = raw2.endswith(b'\n')

out = json.dumps({'last_tick': last_tick, 'launches': entries}, indent=indent, ensure_ascii=False)
if trailing_nl and not out.endswith('\n'):
    out += '\n'
data = out.encode('utf-8')
if crlf:
    data = data.replace(b'\n', b'\r\n')

# parse-verify BEFORE write (r185)
json.loads(data.decode('utf-8'))

with open('results/autofill_state.json','wb') as f:
    f.write(data)

print('resolved: launches=%d (union identities=%d, crash_counted preserved=%d) indent=%d crlf=%s trailing_nl=%s'
      % (len(entries), len(union), n_crash, indent, crlf, trailing_nl))
print('last_tick winner: %s %s (ts2=%s ts3=%s, tie->HEAD)' % (last_tick.get('machine'), last_tick.get('verdict'), ts2, ts3))
