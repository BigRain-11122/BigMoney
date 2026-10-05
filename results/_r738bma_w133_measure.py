# -*- coding: utf-8 -*-
"""r738 bm-a W133 registry-insert MEASUREMENT pass (r735 codegen law: rep()
expects are measured on POST-prior-replacement text BEFORE the insert script
is written).  Prints every needle count verbatim for the W133 insert script.
Bloodline: r737 _r737bma_w132_measure.py verbatim + W133 facts.
"""
import io

face = io.open(r".codely-cli\scratch_w132_face_source.txt", encoding="utf-8").read()

# --- 0a. blanket wave-number shift FIRST (measure counts before/after) ---
n_w132 = face.count("W132"); n_w131 = face.count("W131"); n_w130 = face.count("W130")
print(f"RAW counts: W132={n_w132} W131={n_w131} W130={n_w130}")
face = face.replace("W132", "W133")
face = face.replace("W131", "W132")
face = face.replace("W130", "W131")
print(f"POST-0a: W133={face.count('W133')} (expect {n_w132}) "
      f"W132={face.count('W132')} (expect {n_w131}) "
      f"W131={face.count('W131')} (expect {n_w130}) "
      f"W130={face.count('W130')} (expect 0)")
assert face.count("W133") == n_w132 and face.count("W132") == n_w131 \
    and face.count("W131") == n_w130 and face.count("W130") == 0, "blanket drift"

# --- 0b. A/B-block seed-value needles (post-0a text) ---
needles_0b = [
    '== 307_004 == 307_003 + 1',
    'set(range(307_004, 309_004))',
    '== 68_902 == 68_901 + 1',
    'set(range(68_902, 69_102))',
    'arith_a132', 'arith_b132',
]
for nd in needles_0b:
    print(f"count({nd!r}) = {face.count(nd)}")

# --- 0c. specific needles measured on post-0a/0b text (order matters;
#     substring-order law: receipt needle FIRST, parity block LAST) ---
face = face.replace('== 307_004 == 307_003 + 1', '== 309_004 == 309_003 + 1')
face = face.replace('set(range(307_004, 309_004))', 'set(range(309_004, 311_004))')
face = face.replace('== 68_902 == 68_901 + 1', '== 69_102 == 69_101 + 1')
face = face.replace('set(range(68_902, 69_102))', 'set(range(69_102, 69_302))')
face = face.replace('arith_a132', 'arith_a133')
face = face.replace('arith_b132', 'arith_b133')

print("--- receipt/seat needles (substring-order FIRST) ---")
for nd in ['_r737bma_w132_band_gate.py',
           'MSG-2026-10-05-1755-bma-w132-seat',
           'bm-a r736 freeze 8cd6667e8',
           '9c7e85e7f',
           '6e0b0c43f',
           'bm-a r737 freeze',
           'r736 W131 seat MSG-1726 tail',
           '(bm-c r560 same-window',
           'W131 finalize one-pass bm-a r737',
           '= W131 bm-a r737 one-pass',
           'law sec.4 W132 row, r737',
           'wave 132 = first free number']:
    print(f"count({nd!r}) = {face.count(nd)}")

print("--- count needles ---")
for nd in ['WAVE_CONFIGS[132]', 'pf.N1_BANDS[132]', '_set_wave(132)',
           'if w < 132', 'range(17, 132)', 'range(16, 132)',
           'w132_a', 'w132_b', 'n3r1_used132', 'n1w132', 'n1_w132',
           'ONE HUNDRED-AND-TWENTY-SECOND', 'forty-eighth',
           'rows 47 + candidate', 'rows 121 + candidate',
           '684,211', 'K=286,120', 'W131 finalize one-pass bm-a r736',
           'below 132 composes', 'net chain head 684,211',
           'W1..W132', 'W2..W132']:
    print(f"count({nd!r}) = {face.count(nd)}")

# --- parity block: measure the exact current block text ---
import re
m = re.search(r'assert pf\.N1_BANDS\[128\] == \{"a": \(299_004.*?"registered W131 row parity drift \(r307; bm-a r736\)"', face, re.S)
print("parity block found:", bool(m))
if m:
    print("PARITY BLOCK TEXT (verbatim for the insert script):")
    print(repr(m.group(0)))
