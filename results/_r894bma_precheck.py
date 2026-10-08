# -*- coding: utf-8 -*-
# r894 pre-build verification: live anchors + dump equivalence + pair NEW-side token presence
import io
import ast

n1 = io.open(r"scripts/perpetual_faces_n1.py", encoding="utf-8", newline="").read()
pf = io.open(r"scripts/perpetual_faces.py", encoding="utf-8", newline="").read()
NL = "\r\n"
IND10 = " " * 10

seg = '"r892 bm-a] "' + NL + IND10 + '"+ T-141 s2 "'
print("claim anchor count:", n1.count(seg))
print("T-141 header count:", n1.count("    # --- T-141 s2 lane face"))
print("EO+NL+} in pf:", pf.count('"engine_owner": "bm-a"},' + NL + "}"))
print("EO+NL+IND23+} in n1:", n1.count('"engine_owner": "bm-a"},' + NL + " " * 23 + "}"))

blk = io.open(r"results/_r893bma_w191_probe_pf_block.txt", encoding="utf-8", newline="").read()
print("pf dump in live:", pf.count(blk))
entry = io.open(r"results/_r893bma_w191_probe_n1_entry.txt", encoding="utf-8", newline="").read()
print("entry dump with IND23 in live:", n1.count(" " * 23 + entry))
mat = io.open(r"results/_r893bma_w191_probe_n1_mat.txt", encoding="utf-8", newline="").read()
print("mat dump+4sp in live:", n1.count("    " + mat))
claim = io.open(r"results/_r893bma_w191_probe_n1_claim.txt", encoding="utf-8", newline="").read()
print("claim dump+IND10 in live:", n1.count(IND10 + claim))

src = io.open(r"results/_r892bma_w190_freeze_edits.py", encoding="utf-8", newline="").read()
tree = ast.parse(src)


def ev(n):
    if isinstance(n, ast.Constant):
        return n.value
    if isinstance(n, ast.BinOp) and isinstance(n.op, ast.Add):
        return ev(n.left) + ev(n.right)
    if isinstance(n, ast.Name) and n.id == "NL":
        return NL
    raise AssertionError(ast.dump(n)[:60])


pairs = []
for node in tree.body:
    if isinstance(node, ast.Assign) and getattr(node.targets[0], "id", "") in (
            "PF_PAIRS", "EN_PAIRS", "MAT_PAIRS", "CL_PAIRS"):
        for el in node.value.elts:
            pairs.append((ev(el.elts[0]), ev(el.elts[1]), el.elts[2].value))
print("total pairs:", len(pairs))
allnew = "\n".join(n for _, n, _ in pairs)
for tok in ("430_604..432_603", "430_404..432_403", "430_604..430_803",
            "430_404..430_603", "428_404..430_403", "428_204..430_203",
            "428_404..428_603", "428_204..428_403", "ONE HUNDRED-AND-NINETIETH",
            "823,128", "413,720", "r892 sec8", "bm-a r892-window",
            "(r307; bm-a r890)", "r891 receipt machine-read",
            "jumps to 434_804, first-clean ", "434_804 and lands ",
            "== 432_804 == 432_803 + 1", "set(range(432_804, 434_804))",
            "assert WAVE_CONFIGS[190]", "432_604..432_803", "432_804..433_003"):
    print(repr(tok[:34]), allnew.count(tok))
