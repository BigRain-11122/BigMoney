# -*- coding: utf-8 -*-
"""r787 bm-c W192 freeze stage-1 probe (r776 fragment-needle law: full
string-face inventory empirically probed BEFORE TOK).

Leg A: dump the four LIVE W191-era faces (the exact inserted content of
the bm-a r894 five-face freeze, recovered mechanically from the
insertion anchors -- r894 emitted-tool mechanics mirrored):
  PF   = the W191 N1_BANDS block (comment+prose+191 row) between the
         last two EO+NL anchors and the dict close;
  EN   = the W191 WAVE_CONFIGS entry (leading IND23 stripped);
  MAT  = the W191 materializer block (no leading indent);
  CL   = the W191 PASS-claim attribution (between '"r894 bm-a] "' and
         the T-141 s2 fragment).
Leg B: AST-extract the PF/EN/MAT/CL pair lists from the r894 EMITTED
freeze-edits tool (results/_r894bma_w191_freeze_edits.py --
extraction-from-emission law) and print every NEW side (= the live W191
block fragments = the OLD sides of the W192 roll) for S91 crafting.
Fail-loud asserts throughout; zero writes to live faces."""
import ast
import io
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
NL = "\r\n"
EO = '"engine_owner": "bm-a"},'
IND23 = " " * 23

pf = io.open(r"scripts/perpetual_faces.py", encoding="utf-8", newline="").read()
n1 = io.open(r"scripts/perpetual_faces_n1.py", encoding="utf-8", newline="").read()

# ---- Leg A: face dumps ----------------------------------------------------
seg = EO + NL + "}"
k1 = pf.rfind(seg)
assert k1 > 0, "pf row-close segment not found"
k0 = pf.rfind(EO + NL, 0, k1)
assert k0 > 0, "pf prior EO anchor not found"
pfblk = pf[k0 + len(EO + NL):k1 + len(EO)]
assert pfblk.startswith("    # W191 (bm-a r894 freeze"), "pf blk head: %r" % pfblk[:60]
assert '191: {"a": (435_004, 437_003)' in pfblk and pfblk.endswith(EO), \
    "pf blk tail: %r" % pfblk[-60:]
io.open(r"results/_r787bmc_w192_probe_pf_block.txt", "w", encoding="utf-8",
        newline="").write(pfblk)
print("A.PF dumped", len(pfblk), "B; head", repr(pfblk[:120]))
print("A.PF tail", repr(pfblk[-160:]))

seg = EO + NL + IND23 + "}"
k1 = n1.rfind(seg)
assert k1 > 0, "n1 entry-close segment not found"
k0 = n1.rfind(EO + NL, 0, k1)
assert k0 > 0, "n1 prior EO anchor not found"
entry = n1[k0 + len(EO + NL):k1 + len(EO)]
assert entry.startswith(IND23 + '191: {"batch"'), "entry head: %r" % entry[:80]
entry = entry[len(IND23):]
assert entry.startswith('191: {"batch"') and entry.endswith(EO), \
    "entry tail: %r" % entry[-60:]
io.open(r"results/_r787bmc_w192_probe_n1_entry.txt", "w", encoding="utf-8",
        newline="").write(entry)
print("A.EN dumped", len(entry), "B; head", repr(entry[:100]))
print("A.EN tail", repr(entry[-160:]))

mi = n1.find("# --- W191 materializer face")
assert mi > 0, "mat head not found"
tj = n1.find("    # --- T-141 s2 lane face", mi)
assert tj > mi, "T-141 anchor not found"
mat = n1[mi:tj]
if mat.endswith(NL):
    mat = mat[: -len(NL)]
assert not mat.startswith(" "), "mat leading indent?"
io.open(r"results/_r787bmc_w192_probe_n1_mat.txt", "w", encoding="utf-8",
        newline="").write(mat)
print("A.MAT dumped", len(mat), "B")
pos = []
p = mat.find("_set_wave(")
while p >= 0:
    pos.append(mat[p:mat.find(")", p) + 1])
    p = mat.find("_set_wave(", p + 1)
print("A.MAT _set_wave calls:", pos)
print("A.MAT head", repr(mat[:200]))
print("A.MAT tail", repr(mat[-260:]))

ci = n1.find('"r894 bm-a] "')
assert ci > 0, "claim stamp not found"
tj2 = n1.find('"+ T-141 s2 "', ci)
assert tj2 > ci, "T-141 claim fragment not found"
line_start = n1.rfind(NL, 0, ci) + len(NL)
claim = n1[line_start:tj2 + len('"+ T-141 s2 "')]
assert claim.startswith(" " * 10 + '"r894 bm-a] "'), "claim head: %r" % claim[:40]
claim = claim[10:]
io.open(r"results/_r787bmc_w192_probe_n1_claim.txt", "w", encoding="utf-8",
        newline="").write(claim)
print("A.CL dumped", len(claim), "B; full", repr(claim))

# ---- Leg B: pair inventory from the r894 EMITTED tool --------------------
src = io.open(r"results/_r894bma_w191_freeze_edits.py", encoding="utf-8",
              newline="").read()
tree = ast.parse(src)


def ev(n):
    if isinstance(n, ast.Constant):
        return n.value
    if isinstance(n, ast.BinOp) and isinstance(n.op, ast.Add):
        return ev(n.left) + ev(n.right)
    raise AssertionError("unsupported node %r" % (ast.dump(n)[:60],))


inv = {}
for node in tree.body:
    if isinstance(node, ast.Assign) and len(node.targets) == 1 and \
       isinstance(node.targets[0], ast.Name) and \
       node.targets[0].id in ("PF_PAIRS", "EN_PAIRS", "MAT_PAIRS",
                              "CL_PAIRS") and isinstance(node.value, ast.List):
        out = []
        for el in node.value.elts:
            assert isinstance(el, ast.Tuple) and len(el.elts) == 3
            out.append((ev(el.elts[0]), ev(el.elts[1]), ev(el.elts[2])))
        inv[node.targets[0].id] = out
for k in ("PF_PAIRS", "EN_PAIRS", "MAT_PAIRS", "CL_PAIRS"):
    assert k in inv, k + " not extracted"
print("B.extracted:", {k: len(v) for k, v in inv.items()})
for k in ("PF_PAIRS", "EN_PAIRS", "MAT_PAIRS", "CL_PAIRS"):
    print("==== %s NEW sides (W192 roll OLD inputs) ====" % k)
    for i, (_old, new, cnt) in enumerate(inv[k]):
        print("[%02d] c%d %r" % (i, cnt, new))
