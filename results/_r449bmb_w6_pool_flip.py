# r449 bm-b: INNOVATION-QUOTA-SLOT-6 pool flip ready->done + result_ref
# (W5 r250 5d45f86d2 precedent; canonical double-write per Tools/fill_ladder
#  _write_pool_double r399 law: shared first, lane same bytes, both atomic).
# Surgical single-entry edit; json re-validated after write; byte-identity assert.
import json, sys, os, datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'Tools'))
from fill_ladder import _write_pool_double  # canonical writer

ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), '..'))
SHARED = os.path.join(ROOT, 'results', 'runnable_pool.json')
LANE = os.path.join(ROOT, 'results', 'runnable_pool.bm-b.json')

RESULT_REF = (
    "results/innovation_quota/RRG-ROTATION-P1.json "
    "(r449 bm-b flip per SLOT-1/2/4/5 precedent; autofill burn 06:40:01 pid 37644 "
    "dead zero-zombie + verdict landed 06:40:17 + bm-b lane attrition row 06:40:34 "
    "+ trials_ledger 355,371->355,375 linear; adopt-verify-close anchors: prereg "
    "sha16 982899ca5dc905ed zero-touch + runner sha16 06ffd1aba437bf1c triple-anchor): "
    "judged-negative ALL 4 cells -- RRG-BASE-X1 -0.0039 / RRG-BASE-X2 -0.3036 / "
    "RRG-UNC-X1 -0.4202 / RRG-UNC-X2 -0.5098 vs line 1.1949 NULL-TERM-DOMINATED "
    "(first non-passive-dominant quota line, N_eff 355,375); DSR 2e-06/0/0/0; "
    "family PBO 0.3 observe band; G1 0/4 -> no G2 face, no T-34 intake; turnover "
    "budget breach both base cells 143.23/124.94 entries/yr vs 50/yr (unc "
    "34.84/12.9 ok); beat_24m all <=0.085; pool-EW bench +2.39% ann vs all four "
    "cells negative; zoo #91 family closed per law s5 + reopen note 3 channels "
    "(industry-pure pool / RS window family / adaptive-hub quadrants); prereg "
    "s7/s8 backfilled r449; 48h CEO face due 2026-10-02 06:40"
)

with open(SHARED, encoding='utf-8') as f:
    pool = json.load(f)

hits = 0
for e in pool.get('entries', []):
    if e.get('id') == 'INNOVATION-QUOTA-SLOT-6':
        assert e.get('status') == 'ready', f"pre-flip status {e.get('status')!r} != ready"
        e['status'] = 'done'
        e['result_ref'] = RESULT_REF
        for s in e.get('shards', []):
            if s.get('key') == 'main':
                assert s.get('status') == 'ready', f"shard status {s.get('status')!r}"
                s['status'] = 'done'
                s['checkpoint'] = ("burn complete 06:40:01-06:40:34 "
                                   "(verdict + attrition + trials_ledger landed, adopt r449 bm-b)")
        hits += 1
assert hits == 1, f"expected exactly 1 SLOT-6 entry, found {hits}"

pool['updated_at'] = datetime.datetime.now().strftime('2026-09-30 %H:%M:%S')

_write_pool_double(SHARED, LANE, pool)

# post-write validation: both files parse, byte-identical, entry done in both
b_shared = open(SHARED, 'rb').read()
b_lane = open(LANE, 'rb').read()
assert b_shared == b_lane, "shared/lane byte-identity FAILED"
for path in (SHARED, LANE):
    d2 = json.loads(open(path, encoding='utf-8').read())
    ent = [e for e in d2['entries'] if e.get('id') == 'INNOVATION-QUOTA-SLOT-6']
    assert len(ent) == 1 and ent[0]['status'] == 'done'
    assert ent[0]['shards'][0]['status'] == 'done'
    assert 'judged-negative ALL 4 cells' in ent[0]['result_ref']
print("SLOT-6 flip LANDED: shared+lane byte-identical, entry done, result_ref set")
