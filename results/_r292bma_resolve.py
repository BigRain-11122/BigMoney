# _r292bma_resolve.py - R292 bm-a S0 rebase UU resolve: results/autofill_state.json (mixed-dict+ledger)
# Laws: r203/R208 union zero-loss / r215 cap50 keep-newest / r140 same-second tie->HEAD(ours=upstream)
#       / r245 ASC write-back (producer append order) / r223+r234 CRLF newline translation + EOF no-newline
#       / r185 parse-verify before write-back / classifier GREEN (1 classified, 0 UNKNOWN)
import subprocess, json

def blob(stage):
    b = subprocess.run(['git', 'show', ':%d:results/autofill_state.json' % stage], capture_output=True).stdout
    return b, json.loads(b)

ours_raw, ours = blob(2)      # upstream 1f30f2f4 (bm-b r293 closeout canonically-resolved state)
theirs_raw, theirs = blob(3)  # local 682895ca (bm-a tick dirt ride 03:40:01)

# launches: union zero-loss, dedupe by canonical form
def canon(x):
    return json.dumps(x, sort_keys=True, ensure_ascii=False)

seen = {}
for src in (ours, theirs):
    for item in src['launches']:
        seen[canon(item)] = item
union = list(seen.values())
n_union = len(union)

# cap50 keep-newest (R215): sort ts DESC, keep 50, then re-sort ASC for write-back (r245)
union.sort(key=lambda x: x['ts'], reverse=True)
dropped = union[50:]
capped = union[:50]
capped.sort(key=lambda x: x['ts'])

# last_tick: inner-ts compare, whole-dict assign, same-second tie -> HEAD/ours (r140)
lt_o, lt_t = ours['last_tick'], theirs['last_tick']
last_tick = lt_o if lt_o['ts'] >= lt_t['ts'] else lt_t

merged = {'last_tick': last_tick, 'launches': capped}

# parse-verify (r185) + isinstance assert
out = json.dumps(merged, ensure_ascii=False, indent=1)
back = json.loads(out)
assert isinstance(back['last_tick'], dict), 'last_tick not dict'
assert back['last_tick'] == last_tick
assert len(capped) == min(50, n_union), 'cap semantic broken'
assert n_union == len(set(canon(x) for x in union)), 'union dedupe lossy'
assert list(back.keys()) == ['last_tick', 'launches'], 'top-level key order drift'
assert ours_raw.count(b'\r\n') > ours_raw.count(b'\n') // 2, 'base blob not CRLF-dominant (probe mismatch)'

# write-back: CRLF translation (r223/r234), EOF no-newline (mirror base blob, ends '}'
payload = out.replace('\n', '\r\n')
if payload.endswith('\r\n'):
    payload = payload[:-2]
with open('results/autofill_state.json', 'wb') as f:
    f.write(payload.encode('utf-8'))

with open('results/autofill_state.json', 'rb') as f:
    disk = f.read()
assert json.loads(disk.decode('utf-8')) == back, 'disk round-trip mismatch'
assert disk.endswith(b'}') and not disk.endswith(b'\n'), 'EOF newline mirror broken'

print('RESOLVED n_union=%d capped=%d dropped=%d' % (n_union, len(capped), len(dropped)))
print('last_tick taken (tie->HEAD=upstream):', json.dumps(last_tick, ensure_ascii=False))
for d in dropped:
    print('  aged-out(cap50 keep-newest):', d['ts'], d.get('entry'), d.get('machine'))
print('disk bytes:', len(disk), 'endswith:', repr(disk[-6:]))
