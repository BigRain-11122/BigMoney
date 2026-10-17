# -*- coding: utf-8 -*-
# r1065 bm-c: deep probe -- legs_sec source + header-window rep true form + W258 freeze_edits split face
import io

CANON = "results/_w259bmc_derive_editor.py"
T0 = "results/_w259bmc_freeze_edits.py"
W258FE = "results/_w258bmc_freeze_edits.py"
ce = io.open(CANON, encoding="utf-8", newline="").read()
t0 = io.open(T0, encoding="utf-8", newline="").read()
fe258 = io.open(W258FE, encoding="utf-8", newline="").read()

print("=== canon editor: P5a-header-window rep line (healed form) ===")
i = ce.find("P5a-header-window")
print(ce[max(0, i-420):i+80])
print()
print("=== T0: legs_sec origin (search 'legs_sec =') ===")
i = t0.find("legs_sec = ")
print(t0[max(0, i-700):i+300])
print()
print("=== W258 freeze_edits: split-assert message + kept-assert (for label-roll comparison) ===")
i = fe258.find("leg boundary not found inside")
print(repr(fe258[i-40:i+80]))
i = fe258.find('assert legs_kept.count("assert pf.N1_BANDS[") == 29')
print(repr(fe258[i:i+200]) if i >= 0 else "kept==29 NOT FOUND in W258 freeze_edits")
print()
print("=== T0: estate extraction source (search 'estate' near W259/W258 block) ===")
for pat in ["_b = 259", "_b = 258", "W{_b}", "n1_t4", "legs_sec"]:
    print("count %d for %r" % (t0.count(pat), pat))
i = t0.find("_b = ")
print(repr(t0[i-60:i+120]) if i >= 0 else "_b NOT FOUND")
print()
print("=== T0: the materializer template header line ===")
i = t0.find("# --- W259 materializer face")
print(repr(t0[i-40:i+220]))
