# -*- coding: utf-8 -*-
"""r736 measurement pass: extract W130 face, apply the full W131
transformation chain, and PRINT every needle count (r735 codegen pit
law 2: expects measured on post-prior-replacement text, never taken
from the raw source face). No writes to scripts -- scratch only."""
import io, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
n1 = io.open(os.path.join(ROOT, "scripts", "perpetual_faces_n1.py"), encoding="utf-8").read()
START = "    # --- W130 materializer face"
i0 = n1.find(START)
i1 = n1.find("    # --- T-141 s2 lane face")
assert 0 < i0 < i1, (i0, i1)
face = n1[i0:i1]
io.open(os.path.join(ROOT, ".codely-cli", "scratch_w130_face_source.txt"), "w",
        encoding="utf-8", newline="\n").write(face)
print("face extracted: %d chars" % len(face))

# --- 0a. blanket shift (W130->W131 first, then W129->W130) ---
n_w130 = face.count("W130"); n_w129 = face.count("W129")
face = face.replace("W130", "W131")
face = face.replace("W129", "W130")
print("0a blanket: raw W130=%d W129=%d -> post: W131=%d W130=%d W129=%d"
      % (n_w130, n_w129, face.count("W131"), face.count("W130"), face.count("W129")))
assert face.count("W131") == n_w130 and face.count("W130") == n_w129, "blanket count check"

# --- 0b. B-block needle (post-blanket text) ---
m = re.search(r'assert WAVE_CONFIGS\[131\]\["b_exit_seed_base"\] == 68_502.*?hops=1 ADMIT face"\)', face, re.S)
print("0b B-block needle count:", len(re.findall(
    r'assert WAVE_CONFIGS\[131\]\["b_exit_seed_base"\] == 68_502.*?hops=1 ADMIT face"\)', face, re.S)))
print("0b B-block repr (first 400):")
print(repr(m.group(0)[:400]) if m else "NOT FOUND")

# --- 0c. band facts comment needle ---
m2 = re.search(r'# band facts \(law sec\.4 W131 row, r735\).*?projection\)\.', face, re.S)
print("0c band-facts needle found:", bool(m2))
if m2: print(repr(m2.group(0)[:200]))

# --- specific needles: counts on post-0a text ---
needles = [
    "_r735bma_w130_band_gate.py",
    "MSG-2026-10-05-1658-bma-w130-seat",
    "bm-a r734 freeze 5e8d140ef",
    "W130 finalize one-pass bm-a r735",
    "= W130 bm-a r735 one-pass",
    "net chain head 679,811",
    "K=281,720",
    "ONE HUNDRED-AND-TWENTIETH",
    "forty-sixth",
    "rows 45 + candidate",
    "rows 119 + candidate",
    "(r735 bm-a freeze",
    "below 130 composes",
    "== 303_004 == 303_003 + 1",
    "set(range(303_004, 305_004))",
    "WAVE_CONFIGS[130]",
    "pf.N1_BANDS[130]",
    "_set_wave(130)",
    "if w < 130",
    "range(17, 130)",
    "range(16, 130)",
    "w130_a", "w130_b",
    "arith_a130", "arith_b130",
    "n3r1_used130",
    "n1w130", "n1_w130",
]
print("--- specific needle counts (post-0a, pre-0b) ---")
for nd in needles:
    print("%-45s %d" % (nd, face.count(nd)))

# --- parity block needle (post-0a) ---
m3 = re.search(r'assert pf\.N1_BANDS\[126\] == \{"a": \(295_004.*?r734\)"', face, re.S)
print("--- parity block (W126..W129 rows) found:", bool(m3))
if m3:
    print(repr(m3.group(0)[-200:]))
