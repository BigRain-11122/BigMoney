# -*- coding: utf-8 -*-
"""r1208 bm-c: generate the W314 PRE-FINALIZE six-gate from the frozen W313 lineage
(results/_r1206bmc_w313_sixgate.py) as a canon-clone.

Pitfall family r1168/r1171/r1184/r1199/r1206:
  * count table printed BEFORE writing,
  * self-reference cut (block 1), prior-wave boundary (block 2), setwave presence
    identifiers handled as blocks / sentinels FIRST,
  * exact numeric literals next,
  * ONE single-pass wave-token cascade (W313->W314, W312->W313) LAST,
  * every replacement count-asserted; produced file re-counted.
"""
import io
import re

SRC = 'results/_r1206bmc_w313_sixgate.py'
DST = 'results/_r1208bmc_w314_sixgate.py'
t = io.open(SRC, encoding='utf-8').read()

OLD1 = """i = n1t.find('313: {"batch": "PERPETUAL-N1-W313"')
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
NEW1 = """i = n1t.find('314: {"batch": "PERPETUAL-N1-W314"')
assert i >= 0, 'W314 wave row missing'
seg = n1t[i:i + 12000]
if '@CUT@: {' in seg:   # r1179 heal: cut on the NEXT row
    seg = seg[:seg.find('@CUT@: {')]
row_faces = {
    'a_seed_base_706101': '706101' in seg,
    'b_exit_seed_base_708101': '708101' in seg,
    'shard_subdir_n1_w314': 'n1_w314' in seg,
    'out_name_n1_w314_results': 'n1_w314_results.json' in seg,
    'engine_owner_bm_c': 'engine_owner=bm-c' in seg,
}
f1 = 'law sec.4 W314 A: 706_101..708_100'
f2 = 'law sec.4 W314 B: 708_101..708_300'"""

OLD2 = """# prior-wave W313 registry boundary faces kept
m311 = re.search(r'312: \\{"batch": "PERPETUAL-N1-W312"', n1t)
w312_seg = n1t[m311.start():m311.start() + 12000] if m311 else ''
if '313: {' in w312_seg:
    w312_seg = w312_seg[:w312_seg.find('313: {')]
boundary = bool(m311) and '701701' in w312_seg and '703701' in w312_seg

# setwave birth-station presence gates (segment-scoped): the W313 block must sit
# after the W313 block's own setwave and carry exactly its own wave pin.
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
NEW2 = """# prior-wave W312 registry boundary faces kept
@M@ = re.search(r'313: \\{"batch": "PERPETUAL-N1-W312"', n1t)
@SEGA@ = n1t[@M@.start():@M@.start() + 12000] if @M@ else ''
if '314: {' in @SEGA@:
    @SEGA@ = @SEGA@[:@SEGA@.find('314: {')]
boundary = bool(@M@) and '703901' in @SEGA@ and '705901' in @SEGA@

# setwave birth-station presence gates (segment-scoped): the W313 block must sit
# after the W312 block's own setwave and carry exactly its own wave pin.
@KPOS@ = n1t.rfind('_set_wave(313)')
@AFTER@ = n1t[@KPOS@ + len('_set_wave(313)'):]
setwave_presence = {
    'w313_block_has_314': '_set_wave(314)' in @AFTER@,
    'w313_block_has_313': '_set_wave(313)' in @AFTER@,
    'w313_block_has_305': '_set_wave(305)' in @AFTER@,
    'whole_file_314_count': n1t.count('_set_wave(314)'),
    'whole_file_313_count': n1t.count('_set_wave(313)'),
    'whole_file_305_count': n1t.count('_set_wave(305)'),
}
setwave_ok = (setwave_presence['w313_block_has_314']
              and not setwave_presence['w313_block_has_313']
              and not setwave_presence['w313_block_has_305']
              and setwave_presence['whole_file_314_count'] == 1
              and setwave_presence['whole_file_313_count'] == 1
              and setwave_presence['whole_file_305_count'] == 1)"""

BLOCKS = [(OLD1, NEW1), (OLD2, NEW2)]
print('== block count table ==')
for old, new in BLOCKS:
    c = t.count(old)
    print('%3d/1  block %r' % (c, old.splitlines()[0][:70]))
    assert c == 1, 'block count %d != 1 for %r' % (c, old.splitlines()[0])
    t = t.replace(old, new)

SPECIAL = [
    (1, 'A_BASE, B_BASE = 703901, 705901', 'A_BASE, B_BASE = 706101, 708101'),
    (1, 'PREV_TOTAL, PREV_K = 1110741, 684320', 'PREV_TOTAL, PREV_K = 1112941, 686520'),
    (1, 'WAVE = 313', 'WAVE = 314'),
    (1, 'PREV = 312', 'PREV = 313'),
    (1, 'prior_wave_312_boundary_kept', 'prior_wave_313_boundary_kept'),
    (1, 'shard-7/9/10 finished 18:33:26-27', 'shard-7/9/10 finished 19:49:36-38'),
    (1, '(bm-c r1201 one-pass 1,110,741/K=684,320)',
        '(bm-c @ANCH@ one-pass 1,112,941/K=686,520)'),
    (1, '_r1203bmc_w312_sixgate.py', '@LIN@'),
    (2, '76th consecutive', '77th consecutive'),
]
print('== special (numeric/lineage) count table ==')
for want, old, new in SPECIAL:
    c = t.count(old)
    print('%3d/%3d  %s' % (c, want, old[:78]))
    assert c == want, 'special literal count %d != %d: %r' % (c, want, old)
    t = t.replace(old, new)

TOK = {'W313': 'W314', 'W312': 'W313', 'w313': 'w314', 'w312': 'w313',
       'r1206': 'r1208'}
pat = re.compile('|'.join(sorted(TOK, key=len, reverse=True)))
print('== wave-token pass ==')
print({k: t.count(k) for k in TOK})
out = pat.sub(lambda m: TOK[m.group(0)], t)

for sent, val in (('@LIN@', '_r1206bmc_w313_sixgate.py'),
                  ('@ANCH@', 'r1206'),
                  ('@M@', 'm312'),
                  ('@SEGA@', 'w313_seg'),
                  ('@KPOS@', 'k313pos'),
                  ('@AFTER@', 'after313'),
                  ('@CUT@', '315')):
    print('sentinel', sent, out.count(sent))
    assert out.count(sent) >= 1, (sent, out.count(sent))
    out = out.replace(sent, val)

CHECKS = [
    ('WAVE = 314', 1),
    ('PREV = 313', 1),
    ('A_BASE, B_BASE = 706101, 708101', 1),
    ('PREV_TOTAL, PREV_K = 1112941, 686520', 1),
    ("'W314 five-face freeze splice'", 1),
    ('_w314bmc_freeze_receipt.json', 3),
    ('law sec.4 W314 A: 706_101..708_100', 1),
    ('law sec.4 W314 B: 708_101..708_300', 1),
    ('results/p2cal_ext/n1_w314', 1),
    ('research/PERPETUAL_N1_W314_PREREG.md', 1),
    ('_n1_face_adjudication_w314.json', 1),
    ('results/perpetual_faces/n1_w313_results.json', 2),
    ("fr['upstream_w313']", 1),
    ('_r1208bmc_w314_sixgate.json', 1),
    ('_r1206bmc_w313_sixgate.py, 77th consecutive', 1),
    ('W314 wave row missing', 1),
    ('314: {"batch": "PERPETUAL-N1-W314"', 1),
    ('prior_wave_313_boundary_kept', 1),
    ('w313_finalize_present', 3),
    ('"w313_finalize_product_present"', 1),
    ('w314_block_has_314', 2),
    ('whole_file_314_count', 2),
    ('k313pos', 2),
    ('after313', 4),
    ('_set_wave(314)', 2),
    ('_set_wave(313)', 4),
    ('_set_wave(305)', 2),
    ("if '315: {' in seg:", 1),
    ("seg[:seg.find('315: {')]", 1),
    ("if '314: {' in w313_seg:", 1),
    ("w313_seg[:w313_seg.find('314: {')]", 1),
    ("r'313: ", 1),
    ('_w314bmc_prereg_derive.py', 1),
    ('_w314bmc_20261024_probe_receipt.json', 1),
    ('_w314bmc_freeze_edits.py', 1),
]
print('== post-generation count table ==')
bad = []
for lit, want in CHECKS:
    got = out.count(lit)
    flag = '' if got == want else '  <-- MISMATCH'
    print('%3d/%3d  %s%s' % (got, want, lit[:70], flag))
    if got != want:
        bad.append((lit, got, want))
BANNED = ['703_901..705_900', '705_901..706_100', '1110741', '684320', '1,110,741',
          '76th', "'314: {' in seg", 'w312', 'W312', 'r1206 bm-c', '@LIN@',
          '@CUT@']
for b in BANNED:
    if b in out:
        bad.append(('BANNED still present: ' + b, out.count(b), 0))
if bad:
    print('GENERATOR FAIL', bad)
    raise SystemExit(1)

io.open(DST, 'w', encoding='utf-8', newline='\n').write(out)
print('WROTE', DST, len(out), 'bytes')