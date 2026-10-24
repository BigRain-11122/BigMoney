# -*- coding: utf-8 -*-
"""r1203 bm-c: generate the W312 PRE-FINALIZE six-gate from the frozen W311 lineage
(results/_r1201bmc_w311_sixgate.py) as a canon-clone.

Law compliance (r1168/r1171/r1184 pitfall family):
  * count table printed BEFORE writing (never trust eyeballed ordinals),
  * face classes handled separately: exact semantic literals (seed bases / ledger
    totals / boundary seeds / band captions / set_wave pins), single-pass wave-token
    cascade (W311->W312, w311->w312, r1201->r1203 ...), and the self-reference
    "cut on the NEXT row" marker jumped by hand past the new wave (r1179 heal family),
  * every replacement count-asserted and the produced file re-counted.
"""
import io
import re

SRC = 'results/_r1201bmc_w311_sixgate.py'
DST = 'results/_r1203bmc_w312_sixgate.py'
t = io.open(SRC, encoding='utf-8').read()

# ---- exact semantic face (each literal must appear exactly the stated count) ----
SPECIAL = [
    (1, 'A_BASE, B_BASE = 699501, 701501', 'A_BASE, B_BASE = 701701, 703701'),
    (1, 'PREV_TOTAL, PREV_K = 1106341, 679920', 'PREV_TOTAL, PREV_K = 1108541, 682120'),
    (1, "WAVE = 311", "WAVE = 312"),
    (1, "PREV = 310", "PREV = 311"),
    (1, "'a_seed_base_699501': '699501' in seg", "'a_seed_base_701701': '701701' in seg"),
    (1, "'b_exit_seed_base_701501': '701501' in seg",
        "'b_exit_seed_base_703701': '703701' in seg"),
    (1, 'law sec.4 W311 A: 699_501..701_500', 'law sec.4 W312 A: 701_701..703_700'),
    (1, 'law sec.4 W311 B: 701_501..701_700', 'law sec.4 W312 B: 703_701..703_900'),
    (1, "'697301' in w310_seg and '699301' in w310_seg",
        "'699501' in @PSEG@ and '701501' in @PSEG@"),
    (1, '1,106,341/K=679,920', '1,108,541/K=682,120'),
    (1, 'shard-7/9/10 finished 16:13:51-53', 'shard-7/9/10 finished 17:22:48-49'),
    (1, "if '312: {' in seg:", "if '@CUTA@: {' in seg:"),
    (1, "seg = seg[:seg.find('312: {')]", "seg = seg[:seg.find('@CUTA@: {')]"),
    (1, "if '311: {' in w310_seg:", "if '@CUTB@: {' in @SEGB@:"),
    (1, "w310_seg = w310_seg[:w310_seg.find('311: {')]",
        "@SEGB@ = @SEGB@[:@SEGB@.find('@CUTB@: {')]"),
    (1, "'311: {\"batch\": \"PERPETUAL-N1-W311\"'", "'312: {\"batch\": \"PERPETUAL-N1-W312\"'"),
    (1, "re.search(r'310:", "re.search(r'311:"),
    # set_wave birth-station pins (bump high -> low so the second pass cannot re-hit)
    (2, '_set_wave(311)', '_set_wave(312)'),
    (4, '_set_wave(310)', '_set_wave(311)'),
    # presence-gate key names carry their own wave literals (2 sites each: dict + assert)
    (2, "'w311_block_has_311'", "'w312_block_has_312'"),
    (2, "'w311_block_has_310'", "'w312_block_has_311'"),
    (2, "'w311_block_has_305'", "'w312_block_has_305'"),
    (2, "'whole_file_311_count'", "'whole_file_312_count'"),
    (2, "'whole_file_310_count'", "'whole_file_311_count'"),
    (1, "prior_wave_310_boundary_kept", "prior_wave_311_boundary_kept"),
    (2, "k310pos", "k311pos"),
    (4, "after310", "after311"),
]
print('== special (numeric/semantic) count table ==')
for want, old, new in SPECIAL:
    c = t.count(old)
    print('%3d/%3d  %s' % (c, want, old[:78]))
    assert c == want, 'special literal count %d != %d: %r' % (c, want, old)
    t = t.replace(old, new)

# ---- wave-token face: ONE pass, alternation ordered longest-first ----
TOK = {
    'W311': 'W312', 'W310': 'W311',
    'w311': 'w312', 'w310': 'w311',
    'r1201': 'r1203', 'r1199': 'r1201',
    '74th': '75th',
}
pat = re.compile(r'W311|W310|w311|w310|r1201|r1199|74th')
print('== wave-token pass ==')
print({k: t.count(k) for k in TOK})
out = pat.sub(lambda m: TOK[m.group(0)], t)

# ---- sentinel resolution AFTER the cascade (r1201 live-fire: cascade-must-not-re-hit) ----
for sent, val, want in (('@PSEG@', 'w311_seg', 2), ('@SEGB@', 'w311_seg', 4),
                        ('@CUTA@', '313', 2), ('@CUTB@', '312', 2)):
    assert out.count(sent) == want, (sent, out.count(sent), want)
    out = out.replace(sent, val)

# ---- post-generation assertions (count the NEW faces) ----
CHECKS = [
    ('WAVE = 312', 1),
    ('PREV = 311', 1),
    ('A_BASE, B_BASE = 701701, 703701', 1),
    ('PREV_TOTAL, PREV_K = 1108541, 682120', 1),
    ("'W312 five-face freeze splice'", 1),
    ('_w312bmc_freeze_receipt.json', 3),
    ('law sec.4 W312 A: 701_701..703_700', 1),
    ('law sec.4 W312 B: 703_701..703_900', 1),
    ('results/p2cal_ext/n1_w312', 1),
    ('research/PERPETUAL_N1_W312_PREREG.md', 1),
    ('_n1_face_adjudication_w312.json', 1),
    ('results/perpetual_faces/n1_w311_results.json', 2),
    ("fr['upstream_w311']", 1),
    ('_r1203bmc_w312_sixgate.json', 1),
    ('_r1201bmc_w311_sixgate.py, 75th consecutive', 1),
    ('W312 wave row missing', 1),
    ('312: {"batch": "PERPETUAL-N1-W312"', 1),
    ('prior_wave_311_boundary_kept', 1),
    ('w311_finalize_present', 3),
    ('"w311_finalize_product_present"', 1),
    ('k311pos', 2),
    ('after311', 4),
    ('_set_wave(312)', 2),
    ('_set_wave(311)', 4),
    ('_set_wave(305)', 2),
    ("if '313: {' in seg:", 1),
    ("seg[:seg.find('313: {')]", 1),
    ("if '312: {' in w311_seg:", 1),
    ("w311_seg[:w311_seg.find('312: {')]", 1),
]
print('== post-generation count table ==')
bad = []
for lit, want in CHECKS:
    got = out.count(lit)
    flag = '' if got == want else '  <-- MISMATCH'
    print('%3d/%3d  %s%s' % (got, want, lit[:70], flag))
    if got != want:
        bad.append((lit, got, want))
BANNED = ['699_501..701_500', '701_501..701_700', '1106341', '679920', '1,106,341',
          '74th', "'312: {' in seg", 'w310', '@PSEG@', '@SEGB@', '@CUTA@', '@CUTB@']
for b in BANNED:
    if b in out:
        bad.append(('BANNED still present: ' + b, out.count(b), 0))
if bad:
    print('GENERATOR FAIL', bad)
    raise SystemExit(1)

io.open(DST, 'w', encoding='utf-8', newline='\n').write(out)
print('WROTE', DST, len(out), 'bytes')