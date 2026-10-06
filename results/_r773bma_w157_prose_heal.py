# -*- coding: utf-8 -*-
"""r773 bm-a W157-entry projection-prose heal (r772 freeze vmap partial-tokenization
malformed-window face; documentation prose ONLY -- structured fields/bands/seed
bases machine-verified intact by the r772 post-edit asserts + this script):
  corrupted: "A first-clean 362_204..362_003" (start>end malformed window)
             "B first-clean 362_404..360_403" (start>end malformed window)
  healed to the r772 gate leg3 machine-derived W158+ projection verbatim:
             gate receipt _r772bma_w157_band_gate.json leg3 W158p_A/W158p_B
r587 re-derive-not-transcribe law honored: heal targets read FROM the gate
receipt on disk, asserted band-for-band, not hand-copied."""
import ast
import io
import json

N1 = r"scripts/perpetual_faces_n1.py"
src = io.open(N1, encoding="utf-8", newline="").read()

gate = json.load(open("results/_r772bma_w157_band_gate.json", encoding="utf-8"))
leg3 = gate["legs"]["leg3"]


import re as _re


def u(s):  # "362204..364203" -> "362_204..364_203" (3-digit grouping from the right)
    def g(part):
        return _re.sub(r"(\d)(?=(\d{3})+$)", r"\1_", part)
    a, b = s.split("..")
    return f"{g(a)}..{g(b)}"


A_target = u(leg3["W158p_A"])
B_target = u(leg3["W158p_B"])
assert A_target == "362_204..364_203" and B_target == "362_404..362_603", (A_target, B_target)

OLD_A = "A first-clean 362_204..362_003"
NEW_A = f"A first-clean {A_target}"
OLD_B = "B first-clean 362_404..360_403"
NEW_B = f"B first-clean {B_target}"
assert src.count(OLD_A) == 1, src.count(OLD_A)
assert src.count(OLD_B) == 1, src.count(OLD_B)
# guard: the healed strings must not already exist (no double-heal face)
assert src.count(NEW_A) == 0 and src.count(NEW_B) == 0, "heal targets already present?"

# the corrupted faces must live INSIDE the W157 entry (locate both)
k = src.find('157: {"batch"')
m = src.find('"engine_owner": "bm-a"},', k)
entry = src[k:m]
assert OLD_A in entry and OLD_B in entry, "corrupted faces not inside the W157 entry"
# guard: no other wave entry carries the corrupted forms
assert src.count(OLD_A) == 1 and src.count(OLD_B) == 1

src = src.replace(OLD_A, NEW_A).replace(OLD_B, NEW_B)
io.open(N1, "w", encoding="utf-8", newline="").write(src)
ast.parse(io.open(N1, encoding="utf-8", newline="").read())
print("W157 entry projection-prose heal landed, AST gate PASS")
print(f"  A: {OLD_A} -> {NEW_A}")
print(f"  B: {OLD_B} -> {NEW_B}")

# post-heal structural verification: W157 entry intact + W158+ prose matches gate leg3
import sys
sys.path.insert(0, ".")
sys.path.insert(0, "scripts")
import importlib
import perpetual_faces as pf
importlib.reload(pf)
assert pf.N1_BANDS[157] == {"a": (360_204, 362_203),
                            "b_exit": (362_204, 362_403),
                            "engine_owner": "bm-a"}, "W157 row drift after heal"
assert sorted(pf.N1_BANDS)[-1] == 157 and len(pf.N1_BANDS) == 155, "row count drift"
import perpetual_faces_n1 as n1mod
importlib.reload(n1mod)
assert n1mod.WAVE_CONFIGS[157]["a_seed_base"] == 360_204 and \
    n1mod.WAVE_CONFIGS[157]["b_exit_seed_base"] == 362_204, "seed bases drift after heal"
src2 = io.open(N1, encoding="utf-8", newline="").read()
assert f"A first-clean {A_target}" in src2 and f"B first-clean {B_target}" in src2
assert "362_204..362_003" not in src2 and "362_404..360_403" not in src2, \
    "malformed-window residue"
print("post-heal structural assertions PASS: W157 row/seed bases intact, "
      "projection prose == r772 gate leg3 verbatim, malformed windows eradicated")
