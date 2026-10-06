# -*- coding: utf-8 -*-
# r788 bm-a merge-window resolver for results/runnable_pool.bm-a.json (2-UU window)
# Laws: R31 lane authority (bm-a lane) + per-face newer-wins (r773 evidence-per-window law)
#       + r312 done-absorption blocked by deliberate re-queue heal (bm-b r781/r782 mirror heal).
# Decisions (probe receipts: _r788bma_pool_probe3/4.py):
#   FUND-QUALITY-P1-NULLS   -> OURS   owner_since 17:52:10 > theirs 17:24:10 (both bm-b keepalive)
#   FUND-DIVLOWVOL-P1-NULLS -> OURS   owner_since 17:52:10 > theirs 17:24:10 (both bm-b keepalive)
#   FUND-VALUE-P1-NULLS     -> THEIRS re-queue ready face @18:08:24 (deliberate bm-b mirror heal,
#                              stale done@15:50:03 retired per r312-block note)
import subprocess, json, copy

P = 'results/runnable_pool.bm-a.json'
def blob(spec):
    return json.loads(subprocess.run(['git', 'show', spec], capture_output=True).stdout)

ours = blob(':2:' + P)      # merge window: stage2 = ours = HEAD (local bm-a)
theirs = blob(':3:' + P)    # stage3 = theirs = MERGE_HEAD (origin)

merged = copy.deepcopy(ours)

def find_entry(d, eid):
    for i, e in enumerate(d['entries']):
        if e['id'] == eid:
            return i, e
    return None, None

# 1) FUND-VALUE: take theirs whole entry (ready re-queue + shard owner_since 18:08:24)
i_o, e_o = find_entry(merged, 'FUND-VALUE-P1-NULLS')
i_t, e_t = find_entry(theirs, 'FUND-VALUE-P1-NULLS')
assert e_o is not None and e_t is not None, 'entries must exist on both sides'
merged['entries'][i_o] = copy.deepcopy(e_t)

# 2) QUALITY/DIVLOWVOL: keep ours (already in merged); assert the shard values
for eid, want_os in (('FUND-QUALITY-P1-NULLS', '2026-10-06 17:52:10'),
                     ('FUND-DIVLOWVOL-P1-NULLS', '2026-10-06 17:52:10')):
    _, e = find_entry(merged, eid)
    assert e['shards'][0]['owner_since'] == want_os, eid + ' shard owner_since must be ours-newer'

# 3) everything else must be identical between the two sides (probe3: only 3 shards differ)
def canon(d):
    return {e['id']: json.dumps(e, sort_keys=True, ensure_ascii=False) for e in d['entries']}
co, ct, cm = canon(ours), canon(theirs), canon(merged)
only3 = {k for k in co if co[k] != ct[k]}
assert only3 == {'FUND-QUALITY-P1-NULLS', 'FUND-DIVLOWVOL-P1-NULLS', 'FUND-VALUE-P1-NULLS'}, only3
for k in co:
    if k not in only3:
        assert cm[k] == co[k], 'untouched entry drifted: ' + k
assert cm['FUND-VALUE-P1-NULLS'] == ct['FUND-VALUE-P1-NULLS'], 'FUND-VALUE must equal theirs'
assert len(merged['entries']) == 403, 'entry count must stay 403'

# format-mirror: detect indent + line ending from the ours blob bytes
raw = subprocess.run(['git', 'show', ':2:' + P], capture_output=True).stdout
crlf = b'\r\n' in raw
indent = 1  # the pool writer uses indent=1 (established by probe of raw face)
out = json.dumps(merged, ensure_ascii=False, indent=indent)
if raw.endswith(b'\n'):
    out += '\n'
data = out.encode('utf-8')
if crlf:
    data = data.replace(b'\n', b'\r\n')
open(P, 'wb').write(data)

# post-write verify
back = json.load(open(P, encoding='utf-8'))
_, ev = find_entry(back, 'FUND-VALUE-P1-NULLS')
assert ev['status'] == 'ready' and ev['shards'][0]['owner_since'] == '2026-10-06 18:08:24'
_, eq = find_entry(back, 'FUND-QUALITY-P1-NULLS')
assert eq['shards'][0]['owner_since'] == '2026-10-06 17:52:10'
_, ed = find_entry(back, 'FUND-DIVLOWVOL-P1-NULLS')
assert ed['shards'][0]['owner_since'] == '2026-10-06 17:52:10'
print('resolved+written: 403 entries; FUND-VALUE=theirs(ready@18:08:24); '
      'QUALITY/DIVLOWVOL=ours(17:52:10); parse-verified; crlf=%s' % crlf)
