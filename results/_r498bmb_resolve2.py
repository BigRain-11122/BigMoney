# r498 re-fire rebase resolver: results/runnable_pool.json (r489 dual-layer + r498-bm-a AA-envelope law)
# Policy: origin/new-base (:2) is the newest shared truth (claim visibility = origin refs, r297);
#         replayed daemon flip (:3) semantics = n1w3-0 shard/entry done -> must be preserved (status lattice: done wins).
# Zero-loss assertion: every entry/shard in :2 preserved; every done state in :3 preserved.
import subprocess, json, sys

def blob(stage):
    r = subprocess.run(['git', 'show', ':%d:results/runnable_pool.json' % stage], capture_output=True)
    if r.returncode != 0:
        print('STAGE_READ_FAIL', stage, r.stderr.decode()[:200]); sys.exit(2)
    return r.stdout

base = blob(1); origin = blob(2); ours = blob(3)
b, o, u = json.loads(base), json.loads(origin), json.loads(ours)

# detect line ending + indent from origin blob (r223/r234: mirror producer format)
crlf = b'\r\n' in origin[:2000]
indent = None
probe = origin.decode('utf-8', 'replace').splitlines()
for ln in probe[1:6]:
    s = ln.rstrip('\r\n')
    if s.startswith(' '):
        indent = len(s) - len(s.lstrip(' ')); break
if indent is None: indent = 1

def index_entries(doc):
    # runnable_pool structure: {"entries": [...]} or list -- handle both
    items = doc.get('entries', doc) if isinstance(doc, dict) else doc
    return {it.get('entry', it.get('id', '?')): it for it in items}, items

oi, o_items = index_entries(o)
ui, u_items = index_entries(u)
bi, b_items = index_entries(b)

STATUS_RANK = {'done': 3, 'running': 2, 'ready': 1, 'waiting': 0, 'parked': 0}

merged = {k: dict(v) for k, v in oi.items()}  # start from origin (newest shared face)
changes = []
for k, uv in ui.items():
    if k not in merged:
        merged[k] = dict(uv); changes.append('ADD_ENTRY ' + k); continue
    mv = merged[k]
    # merge shard layer
    ush = {s.get('shard', '?'): s for s in (uv.get('shards') or [])}
    msh = {s.get('shard', '?'): s for s in (mv.get('shards') or [])}
    for sn, sv in ush.items():
        if sn not in msh:
            msh[sn] = sv; changes.append('ADD_SHARD %s/%s' % (k, sn)); continue
        mst, ust = msh[sn].get('status'), sv.get('status')
        if STATUS_RANK.get(ust, -1) > STATUS_RANK.get(mst, -1):
            msh[sn] = sv; changes.append('UP_SHARD %s/%s %s->%s' % (k, sn, mst, ust))
        elif ust == mst and sv.get('done_at') and not msh[sn].get('done_at'):
            msh[sn].update(sv); changes.append('FILL_DONE_AT %s/%s' % (k, sn))
    mv['shards'] = list(msh.values())
    # merge entry layer (done wins; keep origin owner/status unless ours upgrades)
    if STATUS_RANK.get(uv.get('status'), -1) > STATUS_RANK.get(mv.get('status'), -1):
        for f in ('status', 'done_at', 'owner', 'owner_since', 'finalize', 'finalized_at'):
            if f in uv: mv[f] = uv[f]
        changes.append('UP_ENTRY %s %s->%s' % (k, mv.get('status'), uv.get('status')))
    elif uv.get('done_at') and not mv.get('done_at'):
        mv['done_at'] = uv['done_at']; changes.append('FILL_ENTRY_DONE_AT ' + k)

# rebuild document preserving origin's top-level shape
if isinstance(o, dict):
    out = dict(o)
    key = 'entries' if 'entries' in o else None
    if key:
        out[key] = [merged[k] for k in [it.get('entry', it.get('id', '?')) for it in o[key]]]
        # append entries only in ours
        known = set()
        for it in o[key]: known.add(it.get('entry', it.get('id', '?')))
        for k, v in merged.items():
            if k not in known: out[key].append(v)
    else:
        out = {'entries': list(merged.values())}
    for k in out:
        if k != (key or 'entries') and k not in ('entries',) and not isinstance(out[k], (list, dict)):
            pass
else:
    out = list(merged.values())

text = json.dumps(out, ensure_ascii=False, indent=indent)
if crlf: text = text.replace('\n', '\r\n')
with open('results/runnable_pool.json', 'w', encoding='utf-8', newline='') as f:
    f.write(text + ('\r\n' if crlf else '\n'))

# validation: zero-loss assertion (r489 dual-state reconciliation both layers)
mi, _ = index_entries(json.loads(open('results/runnable_pool.json', encoding='utf-8').read()))
loss = []
for k, uv in ui.items():
    if k not in mi: loss.append('ENTRY_LOST ' + k); continue
    for s in (uv.get('shards') or []):
        sn = s.get('shard', '?')
        mm = {x.get('shard', '?'): x for x in (mi[k].get('shards') or [])}
        if sn not in mm: loss.append('SHARD_LOST %s/%s' % (k, sn))
        elif s.get('status') == 'done' and mm[sn].get('status') != 'done': loss.append('DONE_LOST %s/%s' % (k, sn))
    if uv.get('status') == 'done' and mi[k].get('status') != 'done': loss.append('ENTRY_DONE_LOST ' + k)
for k in oi:
    if k not in mi: loss.append('ORIGIN_ENTRY_LOST ' + k)
print('CHANGES:', changes if changes else 'origin-already-has-all (pure AA, origin kept)')
print('LOSS:', loss if loss else 'NONE -- zero-loss assert PASS')
print('POOL_SIZE merged=%d origin=%d ours=%d' % (len(mi), len(oi), len(ui)))
sys.exit(1 if loss else 0)
