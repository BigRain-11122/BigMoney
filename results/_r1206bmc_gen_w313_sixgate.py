# -*- coding: utf-8 -*-
"""r1206 bm-c: generate the W313 PRE-FINALIZE six-gate from the frozen W312 lineage
(results/_r1203bmc_w312_sixgate.py) as a canon-clone.

Law compliance (r1168/r1171/r1184/r1192 pitfall family):
  * count table printed BEFORE writing,
  * face classes handled separately: block-level replacements for the self-reference
    cuts ("cut on the NEXT row") and the setwave presence block (identifiers k311pos
    / after311 carry no w-token so a cascade never touches them), exact numeric
    literals, then ONE single-pass wave-token cascade (W311->W312, W312->W313),
  * every replacement count-asserted and the produced file re-counted.
"""
import io
import re

SRC = 'results/_r1203bmc_w312_sixgate.py'
DST = 'results/_r1206bmc_w313_sixgate.py'
t = io.open(SRC, encoding='utf-8').read()

# ---------------- block 1: own-wave row faces + self-reference cut ----------------
OLD1 = """i = n1t.find('312: {"batch": "PERPETUAL-N1-W312"')
assert i >= 0, 'W312 wave row missing'
seg = n1t[i:i + 12000]
if '313: {' in seg:   # r1179 heal: cut on the NEXT row
    seg = seg[:seg.find('313: {')]
row_faces = {
    'a_seed_base_701701': '701701' in seg,
    'b_exit_seed_base_703701': '703701' in seg,
    'shard_subdir_n1_w312': 'n1_w312' in seg,
    'out_name_n1_w312_results': 'n1_w312_results.json' in seg,
    'engine_owner_bm_c': 'engine_owner=bm-c' in seg,
}
f1 = 'law sec.4 W312 A: 701_701..703_700'
f2 = 'law sec.4 W312 B: 703_701..703_900'"""
NEW1 = """i = n1t.find('313: {"batch": "PERPETUAL-N1-W313"')
assert i >= 0, 'W313 wave row missing'
seg = n1t[i:i + 12000]
if '314: {' in seg:   # r1179 heal: cut on the NEXT row
    seg = seg[:seg.find('314: {')]
row_faces = {
    'a_seed_base_703901': '703901' in seg,
    'b_exit_seed_base_705901': '705901' in seg,
    'shard_subdir_n1_w313': 'n1_w313' in seg,
    'out_name_n1_w313_results': 'n1_w313_results.json' in seg,
    'engine_owner_bm_c': 'engine_owner=bm-c' in seg,
}
f1 = 'law sec.4 W313 A: 703_901..705_900'
f2 = 'law sec.4 W313 B: 705_901..706_100'"""

# ---------------- block 2: prior-wave boundary + setwave presence (identifiers) -------
OLD2 = """# prior-wave W311 registry boundary faces kept
m310 = re.search(r'311: \\{"batch": "PERPETUAL-N1-W311"', n1t)
w311_seg = n1t[m310.start():m310.start() + 12000] if m310 else ''
if '312: {' in w311_seg:
    w311_seg = w311_seg[:w311_seg.find('312: {')]
boundary = bool(m310) and '699501' in w311_seg and '701501' in w311_seg

# setwave birth-station presence gates (segment-scoped): the W312 block must sit
# after the W311 block's own setwave and carry exactly its own wave pin.
k311pos = n1t.rfind('_set_wave(311)')
after311 = n1t[k311pos + len('_set_wave(311)'):]
setwave_presence = {
    'w312_block_has_312': '_set_wave(312)' in after311,
    'w312_block_has_311': '_set_wave(311)' in after311,
    'w312_block_has_305': '_set_wave(305)' in after311,
    'whole_file_312_count': n1t.count('_set_wave(312)'),
    'whole_file_311_count': n1t.count('_set_wave(311)'),
    'whole_file_305_count': n1t.count('_set_wave(305)'),
}
setwave_ok = (setwave_presence['w312_block_has_312']
              and not setwave_presence['w312_block_has_311']
              and not setwave_presence['w312_block_has_305']
              and setwave_presence['whole_file_312_count'] == 1
              and setwave_presence['whole_file_311_count'] == 1
              and setwave_presence['whole_file_305_count'] == 1)"""
NEW2 = """# prior-wave W312 registry boundary faces kept
m311 = re.search(r'312: \\{"batch": "PERPETUAL-N1-W311"', n1t)
@SEG@ = n1t[m311.start():m311.start() + 12000] if m311 else ''
if '@CUTB@: {' in @SEG@:
    @SEG@ = @SEG@[:@SEG@.find('@CUTB@: {')]
boundary = bool(m311) and '701701' in @SEG@ and '703701' in @SEG@

# setwave birth-station presence gates (segment-scoped): the W313 block must sit
# after the W312 block's own setwave and carry exactly its own wave pin.
k312pos = n1t.rfind('_set_wave(312)')
after312 = n1t[k312pos + len('_set_wave(312)'):]
setwave_presence = {
    'w313_block_has_313': '_set_wave(313)' in after312,
    'w313_block_has_312': '_set_wave(312)' in after312,
    'w313_block_has_305': '_set_wave(305)' in after312,
    'whole_file_313_count': n1t.count('_set_wave(313)'),
    'whole_file_312_count': n1t.count('_set_wave(312)'),
    'whole_file_305_count': n1t.count('_set_wave(305)'),
}
setwave_ok = (setwave_presence['w313_block_has_313']
              and not setwave_presence['w313_block_has_312']
              and not setwave_presence['w313_block_has_305']
              and setwave_presence['whole_file_313_count'] == 1
              and setwave_presence['whole_file_312_count'] == 1
              and setwave_presence['whole_file_305_count'] == 1)"""

BLOCKS = [(OLD1, NEW1), (OLD2, NEW2)]
print('== block count table ==')
for old, new in BLOCKS:
    c = t.count(old)
    print('%3d/1  block %r' % (c, old.splitlines()[0][:70]))
    assert c == 1, 'block count %d != 1 for %r' % (c, old.splitlines()[0])
    t = t.replace(old, new)

# ---------------- exact numeric / lineage literals ----------------
SPECIAL = [
    (1, 'A_BASE, B_BASE = 701701, 703701', 'A_BASE, B_BASE = 703901, 705901'),
    (1, 'PREV_TOTAL, PREV_K = 1108541, 682120', 'PREV_TOTAL, PREV_K = 1110741, 684320'),
    (1, 'WAVE = 312', 'WAVE = 313'),
    (1, 'PREV = 311', 'PREV = 312'),
    (1, 'prior_wave_311_boundary_kept', 'prior_wave_312_boundary_kept'),
    (1, '1,108,541/K=682,120', '1,110,741/K=684,320'),
    (1, 'shard-7/9/10 finished 17:22:48-49', 'shard-7/9/10 finished 18:33:26-27'),
    (1, '_r1201bmc_w311_sixgate.py', '@LIN@'),
    (2, '75th consecutive', '76th consecutive'),
]
print('== special (numeric/lineage) count table ==')
for want, old, new in SPECIAL:
    c = t.count(old)
    print('%3d/%3d  %s' % (c, want, old[:78]))
    assert c == want, 'special literal count %d != %d: %r' % (c, want, old)
    t = t.replace(old, new)

# ---------------- wave-token face: ONE pass (no double shift) ----------------
TOK = {'W312': 'W313', 'W311': 'W312', 'w312': 'w313', 'w311': 'w312',
       'r1203': 'r1206'}
pat = re.compile(r'W312|W311|w312|w311|r1203')
print('== wave-token pass ==')
print({k: t.count(k) for k in TOK})
out = pat.sub(lambda m: TOK[m.group(0)], t)

# ---------------- sentinel resolution AFTER the cascade ----------------
for sent, val in (('@LIN@', '_r1203bmc_w312_sixgate.py'),
                  ('@SEG@', 'w312_seg'), ('@CUTB@', '313')):
    print('sentinel', sent, out.count(sent))
    assert out.count(sent) >= 1, (sent, out.count(sent))
    out = out.replace(sent, val)

# ---------------- post-generation assertions ----------------
CHECKS = [
    ('WAVE = 313', 1),
    ('PREV = 312', 1),
    ('A_BASE, B_BASE = 703901, 705901', 1),
    ('PREV_TOTAL, PREV_K = 1110741, 684320', 1),
    ("'W313 five-face freeze splice'", 1),
    ('_w313bmc_freeze_receipt.json', 3),
    ('law sec.4 W313 A: 703_901..705_900', 1),
    ('law sec.4 W313 B: 705_901..706_100', 1),
    ('results/p2cal_ext/n1_w313', 1),
    ('research/PERPETUAL_N1_W313_PREREG.md', 1),
    ('_n1_face_adjudication_w313.json', 1),
    ('results/perpetual_faces/n1_w312_results.json', 2),
    ("fr['upstream_w312']", 1),
    ('_r1206bmc_w313_sixgate.json', 1),
    ('_r1203bmc_w312_sixgate.py, 76th consecutive', 1),
    ('W313 wave row missing', 1),
    ('313: {"batch": "PERPETUAL-N1-W313"', 1),
    ('prior_wave_312_boundary_kept', 1),
    ('w312_finalize_present', 3),
    ('"w312_finalize_product_present"', 1),
    ('k312pos', 2),
    ('after312', 4),
    ('_set_wave(313)', 2),
    ('_set_wave(312)', 4),
    ('_set_wave(305)', 2),
    ("if '314: {' in seg:", 1),
    ("seg[:seg.find('314: {')]", 1),
    ("if '313: {' in w312_seg:", 1),
    ("w312_seg[:w312_seg.find('313: {')]", 1),
    ("r'312: ", 1),
    ('_w313bmc_prereg_derive.py', 1),
    ('_w313bmc_20261024_probe_receipt.json', 1),
    ('_w313bmc_freeze_edits.py', 1),
    ('1,110,741/K=684,320', 1),
]
print('== post-generation count table ==')
bad = []
for lit, want in CHECKS:
    got = out.count(lit)
    flag = '' if got == want else '  <-- MISMATCH'
    print('%3d/%3d  %s%s' % (got, want, lit[:70], flag))
    if got != want:
        bad.append((lit, got, want))
BANNED = ['701_701..703_700', '703_701..703_900', '1108541', '682120', '1,108,541',
          '75th', "'313: {' in seg", 'w311', 'W311', 'r1203 bm-c', '@LIN@']
for b in BANNED:
    if b in out:
        bad.append(('BANNED still present: ' + b, out.count(b), 0))
if bad:
    print('GENERATOR FAIL', bad)
    raise SystemExit(1)

io.open(DST, 'w', encoding='utf-8', newline='\n').write(out)
print('WROTE', DST, len(out), 'bytes')