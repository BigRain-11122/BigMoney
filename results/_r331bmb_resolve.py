# r331 bm-b S0 post-FF salvage-union resolver (canon: mixed-dict+ledger r245 + append-log line-union)
# Context: 15:10 round session died at 25min timeout before S7; its S6 outputs (x2 rows)
# and autofill keepalive tail (3b8bb712, dropped in S0 converge) preserved in salvage
# files; this script unions them back into upstream FF faces. Zero-loss discipline.
import json, subprocess, sys

def read_bytes(p):
    with open(p, 'rb') as f:
        return f.read()

def detect_eol(b):
    return '\r\n' if b.count(b'\r\n') > (b.count(b'\n') - b.count(b'\r\n')) else '\n'

# --- 1) autofill_state.json: launches union (composite key, cap50, asc re-sort r245) + last_tick newer ---
work = read_bytes('results/autofill_state.json')
salv = read_bytes('results/_r331bmb_autofill_salvage.json')
eol = detect_eol(work)
dw, ds = json.loads(work), json.loads(salv)
lw, ls = dw.get('launches', []), ds.get('launches', [])
def key(r):
    return (r.get('ts'), r.get('machine'), r.get('entry'), r.get('shard'), r.get('pid'), r.get('verdict'))
seen, union = set(), []
for r in lw + ls:
    k = key(r)
    if k not in seen:
        seen.add(k)
        union.append(r)
pre_cap = len(union)
union.sort(key=lambda r: r.get('ts') or '', reverse=True)
union = union[:50]
union.sort(key=lambda r: r.get('ts') or '')  # r245: write-back MUST be ts-asc (producer append order)
dw['launches'] = union
tw, tsv = dw.get('last_tick', {}), ds.get('last_tick', {})
if isinstance(tsv, dict) and (tsv.get('ts') or '') > (tw.get('ts') or ''):
    dw['last_tick'] = tsv  # whole-dict assign, no str() compare (r140)
assert isinstance(dw['last_tick'], dict), 'last_tick must be dict (r140 assert)'
dw['launches'] = union
out = json.dumps(dw, ensure_ascii=False, indent=1)
with open('results/autofill_state.json', 'w', encoding='utf-8', newline='') as f:
    f.write(out.replace('\n', eol))
# parse-verify before add (r185)
chk = json.loads(read_bytes('results/autofill_state.json'))
assert len(chk['launches']) == len(union) and isinstance(chk['last_tick'], dict)
lost_rows = [r for r in ls if key(r) not in seen]
print('autofill_state: work=%d salv=%d union_precap=%d kept=%d (cap50) salvonly_lost=%d last_tick.ts=%s eol=%r' % (
    len(lw), len(ls), pre_cap, len(union), len(lost_rows), chk['last_tick'].get('ts'), eol))
for r in lost_rows:
    print('  LOST salvonly row:', json.dumps(r, ensure_ascii=False)[:200])

# --- 2) x2_watch_log.jsonl: line-union insert of 6 dead-session rows by (ts,trader) ---
xl = [l for l in read_bytes('results/x2_watch_log.jsonl').decode('utf-8').splitlines() if l.strip()]
salv_x2 = [l for l in read_bytes('results/_r331bmb_x2_salvage.jsonl').decode('utf-8-sig').splitlines() if l.strip() and l.startswith('{')]
existing = set()
for l in xl:
    try:
        r = json.loads(l)
        existing.add((r.get('ts'), r.get('trader')))
    except Exception:
        existing.add(('RAW', l))
added = 0
for l in salv_x2:
    r = json.loads(l)
    if (r.get('ts'), r.get('trader')) not in existing:
        xl.append(l)
        added += 1
xl_sorted = []
raws = [l for l in xl if not l.startswith('{')]
js = [l for l in xl if l.startswith('{')]
js.sort(key=lambda l: (json.loads(l).get('ts') or '', json.loads(l).get('trader') or ''))
xl_sorted = raws + js
xeol = detect_eol(read_bytes('results/x2_watch_log.jsonl'))
with open('results/x2_watch_log.jsonl', 'w', encoding='utf-8', newline='') as f:
    f.write(eol.join(xl_sorted) + (xeol if xl_sorted else ''))
print('x2_watch_log: existing=%d salvage=%d added=%d total=%d' % (len(xl) - added, len(salv_x2), added, len(xl_sorted)))
print('RESOLVER OK')
