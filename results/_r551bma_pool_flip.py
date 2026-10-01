"""r551 bm-a: LOWAMP-P3 ghost-ready dual-flip (r488/r489/r309 law, r509
raw-text surgical law).

Three-way reconciliation DONE before this flip (see round report):
  SENS: claim closed ok bm-a 02:09:38 exit 0 (pool_claims/...bm-a.json),
        product on origin sens.jsonl 500/500 rows (r550 sole-copy rescue).
  LAEDGE-LEGACY-X2: cross-burn adjudicated per r498 (r550 salvage commit
        79a86bd71): 1254/1254 key-aligned science-identical, origin bm-c
        side kept (claim closed bm-c 01:51:26); bm-a duplicate discarded.
  NULLS: NOT touched -- in-flight on bm-b (466/2000, claim heartbeat
        02:22:08 fresh, progress-leader law yield MSG cfd09364a).

Dual-layer flip (r489): entry.status + shard.status -> done, with true
provenance from the closed claim files (no fabricated timestamps).
Format law r500/r509: flat-0-key + CRLF preserved byte-level (raw-text
anchored replacement only, no re-serialization).
"""
import json
import sys

PATH = 'results/runnable_pool.json'
raw = open(PATH, 'rb').read().readdecode = None
raw = open(PATH, 'rb').read().decode('utf-8')
CRLF = '\r\n'


def flip_entry(eid, done_by, done_at, shard_owner, shard_done_at, note):
    i = raw.find('"' + eid + '"')
    assert i > 0, eid + ' anchor not found'
    blk = raw[i:i + 4000]
    # entry-level status = first occurrence in block
    e_old = '"status": "ready"'
    e_pos = blk.find(e_old)
    assert e_pos > 0, eid + ' entry status not found'
    assert blk.find(e_old, e_pos + 1) > 0, eid + ' shard status missing'
    # insertion after entry status line
    e_line_end = blk.find(CRLF, e_pos)
    e_ins = ('"done_by": "' + done_by + '",' + CRLF +
             '"done_at": "' + done_at + '",' + CRLF)
    blk2 = (blk[:e_line_end + 2] + e_ins + blk[e_line_end + 2:])
    # shard-level status = occurrence after "shards"
    s_pos0 = blk2.find('"shards"')
    s_pos = blk2.find(e_old, s_pos0)
    assert s_pos > 0, eid + ' shard status not found'
    s_line_end = blk2.find(CRLF, s_pos)
    s_ins = ('"done_at": "' + shard_done_at + '",' + CRLF +
             '"flip_note": "' + note + '"')
    if shard_owner:
        s_ins = '"owner": "' + shard_owner + '",' + CRLF + s_ins
    blk3 = (blk2[:s_line_end + 2] + s_ins + blk2[s_line_end + 2:])
    # also flip the shard status itself (first occurrence after shards)
    s2 = blk3.find(e_old, blk3.find('"shards"'))
    blk3 = blk3[:s2] + '"status": "done"' + blk3[s2 + len(e_old):]
    # and flip the entry status (first occurrence in block)
    e2 = blk3.find(e_old)
    blk3 = blk3[:e2] + '"status": "done"' + blk3[e2 + len(e_old):]
    return raw[:i] + blk3 + raw[i + 4000:]


raw = flip_entry(
    'LOWAMP-P3-SENS',
    'bm-a',
    '2026-10-02 02:09:38',
    'bm-a',
    '2026-10-02 02:09:38',
    'r551 observation-round dual-flip (r309/r489/r509): claim closed ok '
    'exit 0 (pool_claims/LOWAMP-P3-SENS/lowamp-p3-sens-0of1.bm-a.json), '
    'product on origin sens.jsonl 500/500 rows (r550 sole-copy rescue '
    '79a86bd71); daemon harvest missed the flip (r488 family)')

raw = flip_entry(
    'LOWAMP-P3-CELL-LAEDGE-LEGACY-X2',
    'bm-c',
    '2026-10-02 01:51:26',
    None,
    '2026-10-02 01:51:26',
    'r551 observation-round dual-flip (r309/r489/r509): cross-burn '
    'adjudicated per r498 (r550 salvage 79a86bd71) -- 1254/1254 '
    'key-aligned science-identical, origin bm-c side kept (claim closed '
    '01:51:26), bm-a duplicate 02:10:58 discarded per determinism law')

# sanity: full-file parse + entry statuses
p = json.loads(raw)
ents = p.get('entries', p if isinstance(p, list) else [])
if isinstance(ents, dict):
    ents = list(ents.values())
st = {e.get('id'): e.get('status') for e in ents
      if str(e.get('id', '')).startswith('LOWAMP-P3')}
assert st['LOWAMP-P3-SENS'] == 'done', st
assert st['LOWAMP-P3-CELL-LAEDGE-LEGACY-X2'] == 'done', st
assert st['LOWAMP-P3-NULLS'] == 'ready', st
sh = {}
for e in ents:
    if e.get('id') in ('LOWAMP-P3-SENS', 'LOWAMP-P3-CELL-LAEDGE-LEGACY-X2'):
        for s in e.get('shards', []):
            sh[e['id']] = (s.get('status'), s.get('owner'), s.get('done_at'))
assert all(v[0] == 'done' for v in sh.values()), sh
print('flip verified:', sh)

with open(PATH, 'wb') as fh:
    fh.write(raw.encode('utf-8'))
print('written bytes:', len(raw.encode('utf-8')))
