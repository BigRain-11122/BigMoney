# -*- coding: utf-8 -*-
"""r737 bm-a W132 registry-insert MEASUREMENT pass (r735 codegen law: rep()
expects are measured on POST-prior-replacement text BEFORE the insert script
is written).  Prints every needle count verbatim for the W132 insert script.
Bloodline: r736 _r736bma_w131_measure.py verbatim + W132 facts.
"""
import io

face = io.open(r".codely-cli\scratch_w131_face_source.txt", encoding="utf-8").read()

# --- 0a. blanket wave-number shift FIRST (measure counts before/after) ---
n_w131 = face.count("W131"); n_w130 = face.count("W130"); n_w129 = face.count("W129")
print(f"RAW counts: W131={n_w131} W130={n_w130} W129={n_w129}")
face = face.replace("W131", "W132")
face = face.replace("W130", "W131")
face = face.replace("W129", "W130")
print(f"POST-0a: W132={face.count('W132')} (expect {n_w131}) "
      f"W131={face.count('W131')} (expect {n_w130}) "
      f"W130={face.count('W130')} (expect {n_w129}) "
      f"W129={face.count('W129')} (expect 0)")
assert face.count("W132") == n_w131 and face.count("W131") == n_w130 \
    and face.count("W130") == n_w129 and face.count("W129") == 0, "blanket drift"

# --- 0b. A/B-block seed-value needles (post-0a text) ---
needles_0b = [
    '== 305_004 == 305_003 + 1',
    'set(range(305_004, 307_004))',
    '== 68_702 == 68_701 + 1',
    'set(range(68_702, 68_902))',
    'arith_a131', 'arith_b131',
]
for nd in needles_0b:
    print(f"count({nd!r}) = {face.count(nd)}")

# --- 0c. specific needles measured on post-0a/0b text (order matters;
#     substring-order law: receipt needle FIRST, parity block LAST) ---
face = face.replace('== 305_004 == 305_003 + 1', '== 307_004 == 307_003 + 1')
face = face.replace('set(range(305_004, 307_004))', 'set(range(307_004, 309_004))')
face = face.replace('== 68_702 == 68_701 + 1', '== 68_902 == 68_901 + 1')
face = face.replace('set(range(68_702, 68_902))', 'set(range(68_902, 69_102))')
face = face.replace('arith_a131', 'arith_a132')
face = face.replace('arith_b131', 'arith_b132')

print("--- receipt/seat needles (substring-order FIRST) ---")
for nd in ['_r736bma_w131_band_gate.py',
           'MSG-2026-10-05-1726-bma-w131-seat',
           'bm-a r735 freeze 0b8b308db',
           'fde20e3a1',
           'd09d5fe6a',
           'bm-a r736 freeze',
           'r735 W130 gate-tail']:
    print(f"count({nd!r}) = {face.count(nd)}")

print("--- arithmetic-tail comment needles (inside 0b message strings) ---")
for nd in ['past the W131 \n        "registered A band tail',
           'past the W131 "']:
    print(f"count({nd!r}) = {face.count(nd)}")

print("--- count needles ---")
for nd in ['WAVE_CONFIGS[131]', 'pf.N1_BANDS[131]', '_set_wave(131)',
           'if w < 131', 'range(17, 131)', 'range(16, 131)',
           'w131_a', 'w131_b', 'n3r1_used131', 'n1w131', 'n1_w131',
           'ONE HUNDRED-AND-TWENTY-FIRST', 'forty-seventh',
           'rows 46 + candidate', 'rows 120 + candidate',
           '682,011', 'K=283,920', 'W130 finalize one-pass bm-a r736',
           'below 131 composes', 'net chain head 682,011',
           'W1..W131', 'W2..W131']:
    print(f"count({nd!r}) = {face.count(nd)}")

# --- parity block: measure the exact current block text ---
import re
m = re.search(r'assert pf\.N1_BANDS\[127\] == \{"a": \(297_004.*?"registered W130 row parity drift \(r307; bm-a r735\)"', face, re.S)
print("parity block found:", bool(m))
if m:
    print("PARITY BLOCK TEXT (verbatim for the insert script):")
    print(repr(m.group(0)))
