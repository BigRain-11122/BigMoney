# -*- coding: utf-8 -*-
"""r775 bm-a pf.py W157-block projection-prose heal (r774 closeout directive:
W158 freeze window, same-window heal per r773 pit law). The r773 window
healed the n1.py WAVE_CONFIGS cfg prose face; the pf.py W157 comment block
still carries the SAME r772 partial-tokenization malformed windows:
  corrupted: "A first-clean 362_204..362_003" (start>end malformed window)
             "B first-clean 362_404..360_403" (start>end malformed window)
Healed to the r772 gate leg3 machine-derived W158+ projection verbatim
(same source receipt the r773 n1.py heal used -- identical values, one
receipt, no fork face). r587 re-derive-not-transcribe law honored:
heal targets read FROM the gate receipt on disk, asserted band-for-band.
Pure documentation prose face; structured fields/bands/seed bases
machine-verified intact by post-heal structural asserts."""
import ast
import io
import json

PF = r"scripts/perpetual_faces.py"
src = io.open(PF, encoding="utf-8", newline="").read()

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

OLD_A = "362_204..362_003 CLEAN hops=0"      # pf.py comment block: line-broken face
NEW_A = f"{A_target} CLEAN hops=0"
OLD_B = "B first-clean 362_404..360_403"
NEW_B = f"B first-clean {B_target}"
assert src.count(OLD_A) == 1, src.count(OLD_A)
assert src.count(OLD_B) == 1, src.count(OLD_B)
# guard: the healed strings must not already exist (no double-heal face)
assert src.count(NEW_A) == 0 and src.count(NEW_B) == 0, "heal targets already present?"

# the corrupted faces must live INSIDE the W157 comment block (locate both)
i = src.find("    # W157 (bm-a r772 freeze")
k = src.find('157: {"a": (360_204, 362_203)', i)
block = src[i:k]
assert OLD_A in block and OLD_B in block, "corrupted faces not inside the W157 block"
# guard: the healed A-window value must not exist elsewhere pre-heal (count==1 global)
assert src.count(OLD_A) == 1 and src.count(OLD_B) == 1, "corrupted faces not unique"

src = src.replace(OLD_A, NEW_A).replace(OLD_B, NEW_B)
io.open(PF, "w", encoding="utf-8", newline="").write(src)
ast.parse(io.open(PF, encoding="utf-8", newline="").read())
print("pf.py W157-block projection-prose heal landed, AST gate PASS")
print(f"  A: {OLD_A} -> {NEW_A}")
print(f"  B: {OLD_B} -> {NEW_B}")

# post-heal structural verification: W157 row intact + no malformed residue in pf.py
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
src2 = io.open(PF, encoding="utf-8", newline="").read()
assert f"{A_target} CLEAN hops=0" in src2 and f"B first-clean {B_target}" in src2
assert "362_204..362_003" not in src2 and "362_404..360_403" not in src2, \
    "malformed-window residue in pf.py"
# r773 pit law leg: full-file start>end malformed-window regex scan
bad = [m.group() for m in _re.finditer(r"(\d{3})_(\d{3})\.\.(\d{3})_(\d{3})", src2)
       if int(m.group(3)) < int(m.group(1))]
assert not bad, f"malformed windows remain in pf.py: {bad[:4]}"
print("post-heal structural assertions PASS: W157 row intact, projection prose == "
      "r772 gate leg3 verbatim, full-file malformed-window scan CLEAN")
