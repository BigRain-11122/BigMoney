# r332 bm-b S0 rebase-replay UU resolver (canon: mixed-dict+ledger r203/R208/r215/r220/r245, r331 lineage)
# Conflict: replaying local tick commit 3cb9f48a onto origin/main 14e18c3b (bm-a r334 27-UU resolved face)
# Sides: A=HEAD (origin/main tip, post-bm-a-resolution), B=REBASE_HEAD (3cb9f48a, my 16:00:02 tick keepalive)
# Recipe: launches composite-key union -> ts desc -> cap50 -> ts asc write-back (r245);
#         last_tick inner-ts whole-dict take-newer, same-second tie -> HEAD (r140);
#         EOL mirror from producer-side blob, newline='' translation (r223/r234); strict parse before add (r185)
import json, subprocess, sys

def show_bytes(rev):
    return subprocess.run(['git', 'show', rev + ':results/autofill_state.json'],
                          capture_output=True, check=True).stdout

def detect_eol(b):
    crlf = b.count(b'\r\n')
    lf = b.count(b'\n') - crlf
    return '\r\n' if crlf >= lf else '\n'

raw_a, raw_b = show_bytes('HEAD'), show_bytes('REBASE_HEAD')
eol = detect_eol(raw_b) or detect_eol(raw_a)
da, db = json.loads(raw_a.decode('utf-8')), json.loads(raw_b.decode('utf-8'))
la, lb = da.get('launches', []), db.get('launches', [])

def key(r):
    return (r.get('ts'), r.get('machine'), r.get('entry'), r.get('shard'), r.get('pid'), r.get('verdict'))

seen, union = set(), []
for r in la + lb:
    k = key(r)
    if k not in seen:
        seen.add(k)
        union.append(r)
pre_cap = len(union)
union.sort(key=lambda r: r.get('ts') or '', reverse=True)
union = union[:50]
union.sort(key=lambda r: r.get('ts') or '')  # r245: write-back MUST be ts-asc (producer append order)
res = dict(da)  # base face = HEAD; carry over any keys only present in tick side (zero-loss)
for k in db:
    res.setdefault(k, db[k])
res['launches'] = union
ta, tb = da.get('last_tick', {}), db.get('last_tick', {})
if isinstance(tb, dict) and (tb.get('ts') or '') > (ta.get('ts') or ''):
    res['last_tick'] = tb  # whole-dict assign, inner-ts compare only (r140; same-second tie keeps HEAD)
assert isinstance(res.get('last_tick'), dict), 'last_tick must be dict (r140 assert)'
out = json.dumps(res, ensure_ascii=False, indent=1)
with open('results/autofill_state.json', 'w', encoding='utf-8', newline='') as f:
    f.write(out.replace('\n', eol))
chk = json.loads(open('results/autofill_state.json', 'rb').read().decode('utf-8'))
assert chk['launches'] == union and isinstance(chk['last_tick'], dict)
b_only_rows = [r for r in lb if key(r) not in {key(x) for x in la}]
print('autofill_state: A=%d B=%d union_precap=%d kept=%d(cap50) Bonly_absorbed=%d last_tick.ts=%s eol=%r keys_A-only=%s keys_B-only=%s' % (
    len(la), len(lb), pre_cap, len(union), len(b_only_rows), chk['last_tick'].get('ts'), eol,
    sorted(set(da) - set(db)), sorted(set(db) - set(da))))
print('RESOLVER OK')
