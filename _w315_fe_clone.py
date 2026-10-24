# -*- coding: utf-8 -*-
"""Canon-clone the W314 splice editor into the W315 splice editor (bm-c r1209).

r1208 pit family discipline: W tokens ride ONE single-pass map; pure numeric
faces (registry row prefix, cfg dict key, pickaxe anchors, wave field) are
written straight to the target value; ledger anchors are parked behind
pure-letter sentinels before the +2200 band pass so the band roll cannot eat
them (r1184/r1199 family); cumulative prose chains keep the prior-wave form and
are bumped exactly once.
"""
import re

SRC = 'results/_w314bmc_freeze_edits.py'
OUT = 'results/_w315bmc_freeze_edits.py'
t = open(SRC, encoding='utf-8').read()
assert t.count('\r\n') == 0, 'source should be LF'
src = t

# ---------------------------------------------------------------- 1. park ledger anchors
LEDGER = {
    'ZZLGR1': ('1_112_941', '1_115_141'),
    'ZZLGR2': ('686_520', '688_720'),
    'ZZLGR3': ('1,112,941', '1,115,141'),
    'ZZLGR4': ('686,520', '688,720'),
}
counts = {}
for sent, (old, new) in LEDGER.items():
    counts[old] = t.count(old)
    assert counts[old] >= 1, 'ledger anchor %s not found' % old
    t = t.replace(old, sent)

# ---------------------------------------------------------------- 2. single-pass token map
PAIRS = {
    # wave tokens (single pass: 314->315, 313->314, 315->316)
    'W313': 'W314',
    'W314': 'W315',
    'W315': 'W316',
    # lowercase artifact names (same single pass, never chained)
    'n1_w313': 'n1_w314',
    'n1_w314': 'n1_w315',
    # seat identity
    'MSG-20261024-1915-bmc-w314-seat.md': 'MSG-20261024-2045-bmc-w315-seat.md',
    'MSG-20261024-1915-bmc-w314-seat': 'MSG-20261024-2045-bmc-w315-seat',
    'd683bad881': '7f5421ec6f',
    # receipts
    '_w314bmc_20261024_probe_receipt.json': '_w315bmc_20261024_probe_receipt.json',
    '_w314bmc_freeze_receipt.json': '_w315bmc_freeze_receipt.json',
    # pure numeric faces (written straight to target, never cascaded)
    '314: {': '315: {',
    'NEW_W = 314': 'NEW_W = 315',
    'PREV_W = 313': 'PREV_W = 314',
    'PRIOR_W = 312': 'PRIOR_W = 313',
    'len(owner_rows_live) == 303 and len(bma_rows_live) == 130 and len(bmc_rows_live) == 132':
        'len(owner_rows_live) == 304 and len(bma_rows_live) == 130 and len(bmc_rows_live) == 133',
    '(expect 303/130/132)': '(expect 304/130/133)',
    'upstream_w313': 'upstream_w314',
    "'308: {\"a\"'": "'313: {\"a\"'",
    '"wave": 313': '"wave": 314',
    'wave 314: ': 'wave 315: ',
    # ordinal prose (single pass, never chained)
    'SIXTY-SEVENTH': 'SIXTY-EIGHTH',
    'SIXTY-EIGHTH': 'SIXTY-NINTH',
    'THREE HUNDRED AND TWELFTH': 'THREE HUNDRED AND THIRTEENTH',
    'HUNDRED-AND-THIRTY-FIRST': 'HUNDRED-AND-THIRTY-SECOND',
    '172 parity rows': '173 parity rows',
    # parity span counts (66 -> 67 fresh legs)
    '(66) are': '(67) are',
    'legs (66) added': 'legs (67) added',
    # window clock / rounds
    '2026-10-24 19:4x': '2026-10-24 20:4x',
    'r1207': 'r1209',
    'r1208': 'r1209',
}
keys = sorted(PAIRS, key=len, reverse=True)
pat = re.compile('|'.join(re.escape(k) for k in keys))
hit = {}
def _rep(m):
    hit[m.group(0)] = hit.get(m.group(0), 0) + 1
    return PAIRS[m.group(0)]
t = pat.sub(_rep, t)
for k in PAIRS:
    print('map %-42r hits=%d' % (k, hit.get(k, 0)))

# ---------------------------------------------------------------- 3. +2200 band roll
TOK = re.compile(r'(?<![\d_])(\d{3})_(\d{3})(?![\d_])')


def roll(m):
    v = int(m.group(1)) * 1000 + int(m.group(2)) + 2200
    return '%03d_%03d' % (v // 1000, v % 1000)


t, nband = TOK.subn(roll, t)
print('band tokens rolled:', nband)

# ---------------------------------------------------------------- 4. restore ledger anchors
for sent, (old, new) in LEDGER.items():
    assert t.count(sent) >= 1, '%s count %d' % (sent, t.count(sent))
    t = t.replace(sent, new)

# ---------------------------------------------------------------- 5. post fixes (must run after the maps)
POST = [
    # downstream freezer is one wave further than the cloned text says
    ('W315 freezer MUST', 'W316 freezer MUST', 3),
    ('downstream W315 seat', 'downstream W316 seat', 1),
    # backfill precedent round (W314 finalize window), not the W313 one
    ('same r1205 W315 precedent', 'same r1209 W314 precedent', 1),
]
for old, new, expect in POST:
    n = t.count(old)
    if expect:
        assert n == expect, 'post %r hits=%d != %d' % (old, n, expect)
    t = t.replace(old, new)

# receipt placeholder-heal field: restate accurately for this wave
old_ph = ('"prereg_placeholder_heal": "research/PERPETUAL_N1_W315_PREREG.md froze at the r1209 derive window '
          'with sec.7/sec.8 prose placeholders still OPEN (no @@SEAT tokens -- gate0.5 placeholder assertions pass); '
          'sec.7/sec.8 mechanical backfill is this wave\'s own post-finalize step (same r1209 W314 precedent); '
          'judging criteria untouched"')
new_ph = ('"prereg_backfill_face": "research/PERPETUAL_N1_W315_PREREG.md froze with sec.7 carried VERBATIM from the '
          'post-W314-finalize face at HEAD and sec.8 pre-rebuilt for this wave (no @@SEAT placeholder tokens); '
          'the mechanical finalize-time rewrite of sec.7/sec.8 is this wave\'s own post-finalize step '
          '(r1207/r1208 W314 precedent); judging criteria untouched"')
assert t.count(old_ph) == 1, 'placeholder-heal field not found as expected'
t = t.replace(old_ph, new_ph)

# replace the stale "152 parity / 122 fresh" style claims if any leaked
assert 'W316 freezer MUST' in t

open(OUT, 'w', encoding='utf-8', newline='\n').write(t)
print('WROTE %s bytes=%d lines=%d' % (OUT, len(t.encode('utf-8')), t.count('\n') + 1))
print('sanity: W315 x%d W314 x%d W316 x%d' % (t.count('W315'), t.count('W314'), t.count('W316')))