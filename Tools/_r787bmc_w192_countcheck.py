# -*- coding: utf-8 -*-
"""r787 bm-c W192 freeze preflight (pre-write audit, zero mutation):
replicates G3-G9 exactly (chunk extraction with 4-space-indent start
marker, table roll, cfg/mat/pf insertions, all post-insert asserts,
AST gate) -- a full dry run of the freeze WITHOUT writing the target
files. If this passes, the real freeze script will pass every gate up
to G9; G10 write + G11 py_compile/post-import are then near-riskless."""
import ast
import importlib.util
import os
import sys
import textwrap

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FE = os.path.join(ROOT, "Tools", "_r787bmc_w192_freeze_edits.py")
N1P = os.path.join(ROOT, "scripts", "perpetual_faces_n1.py")
PFP = os.path.join(ROOT, "scripts", "perpetual_faces.py")

spec = importlib.util.spec_from_file_location("fe", FE)
fe = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fe)  # __main__ guard: main() not called

src = open(FE, encoding="utf-8", errors="replace").read()
ns = {"SEAT_SHA": fe.SEAT_SHA, "W191_FREEZE_SHA": fe.W191_FREEZE_SHA}
for name, endmark in (
        ("R", "\n    for k, (old, new, cnt) in enumerate(R):"),
        ("RC", "\n    for k, (old, new, cnt) in enumerate(RC):"),
        ("RP", "\n    for k, (old, new, cnt) in enumerate(RP):")):
    i = src.find("    %s = [" % name)
    assert i >= 0, "table %s not found in source" % name
    j = src.find(endmark, i)
    assert j > i, "table %s end marker not found" % name
    exec(textwrap.dedent(src[i:j]), ns)

n1_raw = open(N1P, encoding="utf-8", errors="replace", newline="").read()
pf_raw = open(PFP, encoding="utf-8", errors="replace", newline="").read()
n1n = n1_raw.replace("\r\n", "\n")
pfn = pf_raw.replace("\r\n", "\n")


def rep(text, old, new, expect, tag):
    n = text.count(old)
    assert n == expect, "REPLACEMENT COUNT MISMATCH [%s]: got %d expect %d\nliteral=%r" % (
        tag, n, expect, old[:120])
    return text.replace(old, new)


def chunk(text, start_marker, end_marker, stag):
    i = text.find(start_marker)
    assert i >= 0, "start marker not found [%s]" % stag
    j = text.find(end_marker, i)
    assert j > i, "end marker not found [%s]" % stag
    return text[i:j]


mat191 = chunk(n1n, "    # --- W191 materializer face",
               "\n    # --- T-141 s2 lane face", "mat191")
cfg191 = chunk(n1n, '    191: {"batch": "PERPETUAL-N1-W191",',
              '"engine_owner": "bm-a"},', "cfg191")
cfg191_full = cfg191 + '"engine_owner": "bm-a"},'
pf191 = chunk(pfn, "    # W191 (bm-a r894 freeze, seat MSG-2026-10-08-2130-bma-w191-seat",
              '"engine_owner": "bm-a"},', "pf191")
pf191_full = pf191 + '"engine_owner": "bm-a"},'
assert n1n.count(cfg191_full) == 1, "cfg191 not unique"
assert pfn.count(pf191_full) == 1, "pf191 not unique"
assert mat191.rstrip("\n").endswith("_set_wave(2)"), "mat191 tail drift"
assert mat191.startswith("    # --- W191 materializer face"), "mat191 indent head"

m = mat191
for k, (old, new, cnt) in enumerate(ns["R"]):
    m = rep(m, old, new, cnt, "mat-%02d" % k)
mat192 = m
c = cfg191_full
for k, (old, new, cnt) in enumerate(ns["RC"]):
    c = rep(c, old, new, cnt, "cfg-%02d" % k)
p = pf191_full
for k, (old, new, cnt) in enumerate(ns["RP"]):
    p = rep(p, old, new, cnt, "pf-%02d" % k)

# ---- G8 dry run ----
assert n1n.count(cfg191_full) == 1
n1_b = n1n.replace(cfg191_full, cfg191_full + "\n" + c, 1)
assert n1_b.count(c) == 1 and n1_b.count(cfg191_full) == 1
w191_pos = n1_b.find("# --- W191 materializer face")
assert w191_pos >= 0
t141 = n1_b.find("    # --- T-141 s2 lane face", w191_pos)
assert t141 > w191_pos, "T-141 marker not found after W191 block"
n1_final = n1_b[:t141] + mat192 + "\n" + n1_b[t141:]
assert n1_final.count("# --- W192 materializer face") == 1
assert n1_final.count("# --- W191 materializer face") == 1
assert n1_final.count("    # --- T-141 s2 lane face") == 1
pf_final = pfn.replace(pf191_full, pf191_full + "\n" + p, 1)
assert pf_final.count(pf191_full) == 1 and pf_final.count(
    '192: {"a": (437_204, 439_203)') == 1

# structural spot-checks mirroring the W191 in-file pattern
assert "\n    # --- W192 materializer face (r787 bm-c freeze" in n1_final, \
    "W192 comment not at 4-space indent"
assert "_set_wave(2)\n    # --- T-141 s2 lane face" in n1_final, \
    "W192 tail glued to T-141 header"
assert '192: {"batch": "PERPETUAL-N1-W192",' in n1_final, "n1 cfg row missing"
assert '"shard_subdir": "n1_w192", "out_name": "n1_w192_results.json",' in n1_final
assert '"a_seed_base": 437_204' in n1_final and '"b_exit_seed_base": 439_204' in n1_final
assert '"engine_owner": "bm-c"},' in n1_final, "n1 row owner missing"
assert '192: {"a": (437_204, 439_203), "b_exit": (439_204, 439_403),' in pf_final
assert '"engine_owner": "bm-c"},' in pf_final, "pf row owner missing"

# ---- G9 AST gate dry run ----
ast.parse(n1_final)
ast.parse(pf_final)

print("PREFLIGHT PASS: tables R=%d RC=%d RP=%d; G4-G8 all asserts green; "
      "AST gate green; n1_final=%dB pf_final=%dB (zero writes)" % (
          len(ns["R"]), len(ns["RC"]), len(ns["RP"]),
          len(n1_final), len(pf_final)))
sys.exit(0)
