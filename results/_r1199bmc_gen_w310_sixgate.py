# -*- coding: utf-8 -*-
"""r1199 bm-c: generate the W310 PRE-FINALIZE six-gate from the frozen W309 lineage
(_r1197bmc_w309_sixgate.py) as a canon-clone.

Law compliance (r1168/r1171/r1184 pitfall family):
  * a count table is printed BEFORE writing (never trust eyeballed ordinals),
  * three face classes handled separately: numeric face (seed bands / ledger totals /
    boundary seeds), wave-label face (single-pass regex alternation -- no double shift),
    and derived labels (ordinal 72nd->73rd, lineage citation r1195->r1197),
  * every replacement is count-asserted and the produced file is re-counted.
"""
import io
import re
import sys

SRC = 'results/_r1197bmc_w309_sixgate.py'
DST = 'results/_r1199bmc_w310_sixgate.py'
t = io.open(SRC, encoding='utf-8').read()

# ---- numeric / semantic face: exact literals (each must appear exactly once) ----
SPECIAL = [
    ('A_BASE, B_BASE = 695101, 697101', 'A_BASE, B_BASE = 697301, 699301'),
    ('PREV_TOTAL, PREV_K = 1101941, 675520', 'PREV_TOTAL, PREV_K = 1104141, 677720'),
    ("'a_seed_base_695101': '695101' in seg", "'a_seed_base_697301': '697301' in seg"),
    ("'b_exit_seed_base_697101': '697101' in seg",
     "'b_exit_seed_base_699301': '699301' in seg"),
    ("law sec.4 W309 A: 695_101..697_100", "law sec.4 W310 A: 697_301..699_300"),
    ("law sec.4 W309 B: 697_101..697_300", "law sec.4 W310 B: 699_301..699_500"),
    ("'692901' in w308_seg and '694901'", "'695101' in w308_seg and '697101'"),
    ('1,101,941/K=675,520', '1,104,141/K=677,720'),
    # r1179/r1184 heal: the "cut on the NEXT row" self-reference is NOT part of the
    # wave cascade -- the source's next-row marker (310) is THIS row's own marker now,
    # so leaving it un-shifted truncates seg to zero chars (all row_faces false).
    ("if '310: {' in seg:", "if '311: {' in seg:"),
    ("seg = seg[:seg.find('310: {')]", "seg = seg[:seg.find('311: {')]"),
]
print('== special (numeric/semantic) count table ==')
for old, new in SPECIAL:
    c = t.count(old)
    print('%3d  %s' % (c, old[:78]))
    assert c == 1, 'special literal count %d != 1: %r' % (c, old)
    t = t.replace(old, new)

# ---- wave-label face: ONE pass, alternation ordered longest-first ----
WAVE_MAP = {
    'W309': 'W310', 'W308': 'W309',
    'w309': 'w310', 'w308': 'w309',
    'r1197': 'r1199', 'r1195': 'r1197',
    '72nd': '73rd',
}
pat = re.compile(r'W309|W308|w309|w308|(?<![0-9])309(?![0-9])|(?<![0-9])308(?![0-9])'
                 r'|r1197|r1195|72nd')


def _sub(m):
    g = m.group(0)
    if g in WAVE_MAP:
        return WAVE_MAP[g]
    return {'309': '310', '308': '309'}[g]


print('== wave-label pass ==')
before = {k: t.count(k) for k in ('W309', 'W308', 'w309', 'w308', 'r1197', 'r1195')}
print(before)
out = pat.sub(_sub, t)

# ---- post-generation assertions (count the NEW faces, not the old ones) ----
CHECKS = [
    ('WAVE = 310', 1),
    ('PREV = 309', 1),
    ('A_BASE, B_BASE = 697301, 699301', 1),
    ('PREV_TOTAL, PREV_K = 1104141, 677720', 1),
    ("'W310 five-face freeze splice'", 1),
    ('_w310bmc_freeze_receipt.json', 3),
    ('law sec.4 W310 A: 697_301..699_300', 1),
    ('law sec.4 W310 B: 699_301..699_500', 1),
    ('results/p2cal_ext/n1_w310', 1),
    ('research/PERPETUAL_N1_W310_PREREG.md', 1),
    ('_n1_face_adjudication_w310.json', 1),
    ('results/perpetual_faces/n1_w309_results.json', 2),
    ("fr['upstream_w309']", 1),
    ('_r1199bmc_w310_sixgate.json', 1),
    ('_r1197bmc_w309_sixgate.py, 73rd consecutive', 1),
    ('W310 wave row missing', 1),
    ('310: {"batch": "PERPETUAL-N1-W310"', 1),
    ('prior_wave_309_boundary_kept', 1),
    ('w309_finalize_present', 3),
    ('"w309_finalize_product_present"', 1),
    ('k309pos', 2),
    ('after309', 4),
    ('_set_wave(310)', 2),
    ('_set_wave(309)', 4),
    ('_set_wave(305)', 2),
    ("if '311: {' in seg:", 1),
    ("seg[:seg.find('311: {')]", 1),
]
print('== post-generation count table ==')
bad = []
for lit, want in CHECKS:
    got = out.count(lit)
    flag = '' if got == want else '  <-- MISMATCH'
    print('%3d/%3d  %s%s' % (got, want, lit[:70], flag))
    if got != want:
        bad.append((lit, got, want))
BANNED = ['695_101..697_100', '692901', '1101941', '675520', '1,101,941', '72nd']
for b in BANNED:
    if b in out:
        bad.append(('BANNED still present: ' + b, out.count(b), 0))
if bad:
    print('GENERATOR FAIL', bad)
    raise SystemExit(1)

io.open(DST, 'w', encoding='utf-8', newline='\n').write(out)
print('WROTE', DST, len(out), 'bytes')