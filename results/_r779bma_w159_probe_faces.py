# -*- coding: utf-8 -*-
"""r779 bm-a W159 freeze pre-TOK probe: dump the on-disk W158 faces (pf block,
n1 entry, materializer block, PASS claim) BEFORE writing the freeze-editor
TOK (r773 pit law leg 1: full string-face inventory empirically probed)."""
import io

PF = r"scripts/perpetual_faces.py"
N1 = r"scripts/perpetual_faces_n1.py"
pfs = io.open(PF, encoding="utf-8", newline="").read()
n1s = io.open(N1, encoding="utf-8", newline="").read()

i = pfs.find("    # W158 (bm-a r773 freeze")
assert i > 0, "pf W158 block not found"
j = pfs.find('"engine_owner": "bm-a"},', i) + len('"engine_owner": "bm-a"},')
blk = pfs[i:j]
io.open(r"results/_r779bma_w159_pf_block158.txt", "w", encoding="utf-8", newline="").write(blk)
print("pf W158 block:", len(blk), "bytes, CRLF-lines:", blk.count("\r\n"))

k = n1s.find('158: {"batch"')
assert k > 0, "n1 W158 entry not found"
m = n1s.find('"engine_owner": "bm-a"},', k) + len('"engine_owner": "bm-a"},')
ent = n1s[k:m]
io.open(r"results/_r779bma_w159_entry158.txt", "w", encoding="utf-8", newline="").write(ent)
print("n1 W158 entry:", len(ent), "bytes")

w = n1s.find("# --- W158 materializer face")
t2 = n1s.find("# --- T-141 s2 lane face", w)
assert 0 < w < t2, "materializer anchors missing"
mat = n1s[w:t2]
io.open(r"results/_r779bma_w159_mat_block.txt", "w", encoding="utf-8", newline="").write(mat)
print("n1 W158 materializer block:", len(mat), "bytes")

cs = n1s.find('"+ W158 materializer face')
assert cs > 0, "W158 claim start not found"
ce = n1s.find('"r775 bm-a] "', cs) + len('"r775 bm-a] "')
claim = n1s[cs:ce]
io.open(r"results/_r779bma_w159_claim158.txt", "w", encoding="utf-8", newline="").write(claim)
print("n1 W158 PASS claim:", len(claim), "bytes")

# key needle counts across BOTH files (r745 pre-write law)
for f, txt in ((PF, pfs), (N1, n1s)):
    for needle in ("362_404..364_403", "364_404..364_603", "362_204..364_203",
                   "362_404..362_603", "362_204..362_403", "364_404..366_403",
                   "364_604..364_803", "364_603+1", "364_403+1",
                   "set(range(362_404, 364_404))", "set(range(364_404, 364_604))",
                   '"a_seed_base": 362_404', '"b_exit_seed_base": 364_404',
                   '158: {"a": (362_404, 364_403)', '159: {"a": (',
                   "W159 A window; W159 freezer", "engine_owner rows 147",
                   "rows 73 + candidate", "seventy-fourth", "seventeenth",
                   "ONE HUNDRED-AND-FORTY-EIGHTH", "741,411", "343,320",
                   "MSG-2026-10-06-120x", "24aff72f5", "aed41df3e",
                   "_r773bma", "r775", "r773", "W158", "w158", "W157", "w157"):
        print(f"{f.split('/')[-1]} | {needle!r} = {txt.count(needle)}")
