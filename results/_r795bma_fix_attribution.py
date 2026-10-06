# -*- coding: utf-8 -*-
"""r795 bm-a W165 session-attribution surgical fix (honest-attribution law):
the r794 deriv generator assumed the whole W165 chain would land in one
session (r794), but git facts are: pre-seat push 4bdf63090 + gate/probe
receipts = r793 window (commit msg 'round 793: W165 pre-seat push'),
deriv tools = r794, freeze landing = r795 (this window). The generator's
single-step session blanket also produced PHANTOM filenames
(_r794bma_w164_band_gate.json / _r794bma_w164_probe_receipt.json never
existed; the real receipts are _r793bma_w165_*). This script rewrites the
landed W165 faces (pf block / n1 entry+mat+claim / prereg md) to the
honest attribution, and updates the verify-suite anchors to match.
Every edit is count-asserted (exactly-once) and AST/parse-checked."""
import ast
import io

PF = "scripts/perpetual_faces.py"
N1 = "scripts/perpetual_faces_n1.py"
PRE = "research/PERPETUAL_N1_W165_PREREG.md"
VER = "results/_r794bma_w165_freeze_verify.py"

# (old, new, expected_count, where)
EDITS = [
    # --- pf block: freeze session r795 (W164 precedent: block head = freeze window) ---
    ("# W165 (bm-a r794 freeze, seat MSG-2026-10-06-205x-bma-w165-seat",
     "# W165 (bm-a r795 freeze, seat MSG-2026-10-06-205x-bma-w165-seat", 1, "pf head"),
    # --- pre-seat push session = r793 (git fact: 4bdf63090 = round 793 commit) ---
    ("pre-freeze r565 law (r794 pre-seat",
     "pre-freeze r565 law (r793 pre-seat", 1, "pf push"),
    ("behind-0 at fetch (r794 pre-seat",
     "behind-0 at fetch (r793 pre-seat", 1, "pf ff"),
    ("at fetch (r794 pre-seat push), zero merge, zero \"",
     "at fetch (r793 pre-seat push), zero merge, zero \"", 1, "n1 entry ff"),
    ("#     at fetch (r794 pre-seat push), zero merge, zero",
     "#     at fetch (r793 pre-seat push), zero merge, zero", 1, "n1 mat ff"),
    # --- gate/probe receipts: phantom filenames -> real r793 files ---
    ("results/_r794bma_w164_band_gate.json: A = FIRST-CLEAN",
     "results/_r793bma_w165_band_gate.json: A = FIRST-CLEAN", 1, "pf gate cite"),
    ("results/_r794bma_w164_probe_receipt.json; scan face =",
     "results/_r793bma_w165_probe_receipt.json; scan face =", 1, "pf probe cite"),
    ("\"results/_r794bma_w164_band_gate.json; W165+ projection \"",
     "\"results/_r793bma_w165_band_gate.json; W165+ projection \"", 1, "n1 entry gate"),
    ("always on. ADMIT receipt results/_r794bma_w164_band_gate.json;",
     "always on. ADMIT receipt results/_r793bma_w165_band_gate.json;", 1, "n1 mat gate"),
    ("\"results/_r794bma_w164_band_gate.json, law sec.4 W165 row, \"",
     "\"results/_r793bma_w165_band_gate.json, law sec.4 W165 row, \"", 1, "n1 claim gate"),
    # --- gate-derived session = r793 ---
    ("# W165+ projection (gate-derived r794): A first-clean",
     "# W165+ projection (gate-derived r793): A first-clean", 1, "pf proj"),
    # --- freeze session on mat/claim/band-facts faces = r795 ---
    ("# --- W165 materializer face (r794 bm-a freeze, own-series law",
     "# --- W165 materializer face (r795 bm-a freeze, own-series law", 1, "n1 mat head"),
    ("# band facts (law sec.4 W165 row, r794): A = FIRST-CLEAN past",
     "# band facts (law sec.4 W165 row, r795): A = FIRST-CLEAN past", 1, "n1 bandfacts"),
    ("\"r794 bm-a] \"",
     "\"r795 bm-a] \"", 1, "n1 claim tail"),
    # --- prereg md: L1 freeze window / L3 push session / L5 receipts / L13 seat
    #     session / L36 freeze window + probe session ---
    ("第八十一枚自有波【r794】",
     "第八十一枚自有波【r795】", 1, "pre L1"),
    ("4bdf63090（r794 pre-seat push·zero --no-verify）",
     "4bdf63090（r793 pre-seat push·zero --no-verify）", 1, "pre L3 push"),
    ("pre-seat probe r794 与冻结窗 gate r794 同窗双跑",
     "pre-seat probe r793 与冻结窗 gate r793 同窗双跑", 1, "pre L3 dualrun"),
    ("ADMIT 回执 results/_r794bma_w165_band_gate.json rc0 实跑",
     "ADMIT 回执 results/_r793bma_w165_band_gate.json rc0 实跑", 1, "pre L3 gate"),
    ("ADMIT 回执=results/_r794bma_w165_band_gate.json 单态门全腿实跑",
     "ADMIT 回执=results/_r793bma_w165_band_gate.json 单态门全腿实跑", 1, "pre L5 gate"),
    ("pre-seat probe results/_r794bma_w165_probe.py 先跑",
     "pre-seat probe results/_r793bma_w165_probe.py 先跑", 1, "pre L5 probe"),
    ("本机 r794 席位 MSG-2026-10-06-205x 投影",
     "本机 r793 席位 MSG-2026-10-06-205x 投影", 1, "pre L13 seat"),
    ("本波机验 ADMIT 回执在场=r794 bm-a 冻结窗",
     "本波机验 ADMIT 回执在场=r795 bm-a 冻结窗", 1, "pre L36 freeze"),
    ("（pre-seat probe r794 先跑·双窗 derive 恒等）",
     "（pre-seat probe r793 先跑·双窗 derive 恒等）", 1, "pre L36 probe"),
    # --- verify suite anchors (read-only file, keep it consistent with the landed faces) ---
    ("print(\"leg5: W166+ projection prose == r794 gate leg3 verbatim PASS\")",
     "print(\"leg5: W166+ projection prose == r793 gate leg3 verbatim PASS\")", 1, "ver print"),
    ("assert \"r794 pre-seat\" in pf2 and \"r794 pre-seat\" in n2, \"push session\"",
     "assert \"r793 pre-seat\" in pf2 and \"r793 pre-seat\" in n2, \"push session\"", 1, "ver leg6"),
    ("i2 = pf2.find(\"    # W165 (bm-a r794 freeze\")",
     "i2 = pf2.find(\"    # W165 (bm-a r795 freeze\")", 1, "ver leg7 anchor"),
    ("ce2 = n2.find('\"r794 bm-a] \"', cs2) + len('\"r794 bm-a] \"')",
     "ce2 = n2.find('\"r795 bm-a] \"', cs2) + len('\"r795 bm-a] \"')", 1, "ver leg7 claim"),
]

FILES = {PF: [], N1: [], PRE: [], VER: []}
for old, new, cnt, where in EDITS:
    tgt = None
    for f in FILES:
        src = io.open(f, encoding="utf-8", newline="").read()
        if src.count(old):
            tgt = f
            break
    assert tgt is not None, f"target not found for: {where}: {old[:60]!r}"
    src = io.open(tgt, encoding="utf-8", newline="").read()
    n = src.count(old)
    assert n == cnt, f"{where}: count {n} != {cnt}"
    FILES[tgt].append((old, new, where))

for f, edits in FILES.items():
    src = io.open(f, encoding="utf-8", newline="").read()
    for old, new, where in edits:
        src = src.replace(old, new, 1)
    io.open(f, "w", encoding="utf-8", newline="").write(src)
    if f.endswith(".py"):
        ast.parse(src)
    print(f"{f}: {len(edits)} edits landed, AST/parse PASS")

# post-fix residue scan: no r794-session narrative may remain in the new
# W165 faces (r794 as DERIV-TOOL filename prefix _r794bma_ stays legitimate
# in tool files, not in these landed faces)
pf = io.open(PF, encoding="utf-8", newline="").read()
n1 = io.open(N1, encoding="utf-8", newline="").read()
pre = io.open(PRE, encoding="utf-8", newline="").read()
EO = '"engine_owner": "bm-a"},'
i2 = pf.find("    # W165 (bm-a r")
j2 = pf.find(EO, i2) + len(EO)
pfblk = pf[i2:j2]
w2 = n1.find("# --- W165 materializer face")
t3 = n1.find("# --- T-141 s2 lane face", w2)
mat = n1[w2:t3]
k2 = n1.find('165: {"batch"')
m2 = n1.find(EO, k2) + len(EO)
entry = n1[k2:m2]
cs2 = n1.find('"+ W165 materializer face')
ce2 = n1.find('"r795 bm-a] "', cs2) + len('"r795 bm-a] "')
claim = n1[cs2:ce2]
for tag, seg in (("pf", pfblk), ("entry", entry), ("mat", mat), ("claim", claim), ("prereg", pre)):
    r = seg.count("r794")
    assert r == 0, f"r794 residue {r} in new {tag} face"
print("residue scan CLEAN: zero r794 in all five landed W165 faces")
