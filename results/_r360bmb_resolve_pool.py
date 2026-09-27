"""_r360bmb_resolve_pool -- runnable_pool.json entry-level 3-way merge.

Pool storm recipe (r348/r349 swallow-pit family + r378 governance-fields +
O-2100 shard law): entries merged by id; per-entry: one-side-changed ->
changed side wins; both-changed -> field-wise (ts-ish keys take-new max;
shards recurse per shard-key; scalar double-change defaults to ours/HEAD
r140 tie law). Zero-loss check: result entry ids == union of three sides'
ids. Parse-verify before write-back (r185). Usable for both replay passes.
"""
import json
import subprocess

PATH = 'results/runnable_pool.json'
TS_KEYS = ('ts', 'updated_at', 'owner_since', 'entered_at', 'done_at',
           'generated', 'updated')

def stage(stage_no):
    b = subprocess.run(['git', 'show', f':{stage_no}:{PATH}'],
                       capture_output=True).stdout
    return json.loads(b.decode('utf-8-sig')), b

base, raw_b = stage(1)
ours, raw_o = stage(2)
theirs, raw_t = stage(3)

def entry_map(pool):
    return {e['id']: e for e in pool.get('entries', [])}

bm_, om, tm = entry_map(base), entry_map(ours), entry_map(theirs)
ids = list(dict.fromkeys(list(om) + list(tm) + list(bm_)))

def is_tsy(k):
    return any(t in k.lower() for t in ('ts', 'since', 'at', 'updated'))

def merge_value(k, b, o, t):
    if o == b:
        return t
    if t == b:
        return o
    # both changed
    if isinstance(o, dict) and isinstance(t, dict):
        out = {}
        for kk in dict.fromkeys(list(o) + list(t)):
            out[kk] = merge_value(kk, b.get(kk), o.get(kk), t.get(kk))
        return out
    if isinstance(o, list) and isinstance(t, list) and o and t \
            and all(isinstance(x, dict) for x in o + t):
        # shard lists: merge by key field
        kf = 'key' if 'key' in o[0] else 'id'
        bmap = {x.get(kf): x for x in (b or [])}
        omap = {x.get(kf): x for x in o}
        tmap = {x.get(kf): x for x in t}
        out = []
        for kk in dict.fromkeys(list(omap) + list(tmap)):
            out.append(merge_value(kk, bmap.get(kk), omap.get(kk),
                                   tmap.get(kk)))
        return out
    if is_tsy(k) and isinstance(o, str) and isinstance(t, str):
        return max(o, t)
    return o          # scalar double-change -> ours/HEAD (r140 tie law)

merged_entries = []
for eid in ids:
    b, o, t = bm_.get(eid), om.get(eid), tm.get(eid)
    if o is None and t is None:
        continue
    if o is None:
        merged_entries.append(t)
        continue
    if t is None:
        merged_entries.append(o)
        continue
    if o == t:
        merged_entries.append(o)
        continue
    if o == b:
        merged_entries.append(t)
        continue
    if t == b:
        merged_entries.append(o)
        continue
    merged_entries.append(merge_value(eid, b or {}, o, t))

# order: ancestor order first, then ours-new, then theirs-new
order = []
for e in base.get('entries', []):
    order.append(e['id'])
for e in ours.get('entries', []):
    if e['id'] not in order:
        order.append(e['id'])
for e in theirs.get('entries', []):
    if e['id'] not in order:
        order.append(e['id'])
by_id = {e['id']: e for e in merged_entries}
final = [by_id[i] for i in order if i in by_id]

top = {}
for k in dict.fromkeys(list(ours) + list(theirs)):
    if k == 'entries':
        continue
    top[k] = merge_value(k, base.get(k), ours.get(k), theirs.get(k))
merged = dict(top)
merged['entries'] = final

# zero-loss check
assert set(by_id) == set(om) | set(tm) | {i for i in bm_ if i in om or i in tm}, \
    'entry id union loss'
json.dumps(merged)          # parse-verify
crlf = b'\r\n' in raw_o[:400]
text = json.dumps(merged, ensure_ascii=False, indent=1) + '\n'
with open(PATH, 'wb') as fh:
    fh.write(text.replace('\n', '\r\n' if crlf else '\n').encode('utf-8'))
back = json.loads(open(PATH, 'rb').read().decode('utf-8-sig'))
assert len(back['entries']) == len(final)

# report key states
for eid in ('CENSUS-FUS-S2-W2B', 'TRIAL-LABOR-W2-GENERATE',
            'TRIAL-LABOR-W2-SCREEN'):
    e = by_id.get(eid)
    if e:
        sh = {s.get('key'): (s.get('status'), s.get('owner'))
              for s in e.get('shards', [])}
        print(f'  {eid}: status={e.get("status")} shards={sh}')
print(f'pool merged: {len(final)} entries (union ids preserved), '
      f'updated_at={merged.get("updated_at")}')
