# -*- coding: utf-8 -*-
"""r775 bm-a W158 freeze post-edit verification leg (edits already landed
by _r775bma_w158_freeze_edits.py run-1; this is the assertions-only replay
for the completed freeze window -- the edit script itself is
non-replayable by design, r370 partial-failure rollback law does not
apply here: run-1 landed all four edits + both AST gates clean)."""
import io
import json
import re
import os
import sys

sys.path.insert(0, ".")
sys.path.insert(0, "scripts")
import importlib
import perpetual_faces as pf
importlib.reload(pf)

PF = r"scripts/perpetual_faces.py"
N1 = r"scripts/perpetual_faces_n1.py"
CRLF = "\r\n"

gate158 = json.load(open("results/_r773bma_w158_band_gate.json", encoding="utf-8"))
leg3 = gate158["legs"]["leg3"]


def u(s):
    def g(part):
        return re.sub(r"(\d)(?=(\d{3})+$)", r"\1_", part)
    a, b = s.split("..")
    return f"{g(a)}..{g(b)}"


W159p_A = u(leg3["W159p_A"])
W159p_B = u(leg3["W159p_B"])
assert W159p_A == "364_404..366_403" and W159p_B == "364_604..364_803"

# --- structural assertions (mirror of the freeze script post-edit leg) ------
assert sorted(pf.N1_BANDS)[-1] == 158 and len(pf.N1_BANDS) == 156, \
    "pf N1_BANDS row-count drift after W158 insert"
assert pf.N1_BANDS[158] == {"a": (362_404, 364_403),
                            "b_exit": (364_404, 364_603),
                            "engine_owner": "bm-a"}, "W158 row face drift"
assert pf.N1_BANDS[157] == {"a": (360_204, 362_203),
                            "b_exit": (362_204, 362_403),
                            "engine_owner": "bm-a"}, "W157 row survived (r560)"

import perpetual_faces_n1 as n1mod
importlib.reload(n1mod)
assert n1mod.WAVE_CONFIGS[158]["a_seed_base"] == 362_404 and \
    n1mod.WAVE_CONFIGS[158]["b_exit_seed_base"] == 364_404, "W158 seed bases drift"
assert n1mod.WAVE_CONFIGS[158]["shard_subdir"] == "n1_w158" and \
    n1mod.WAVE_CONFIGS[158]["out_name"] == "n1_w158_results.json", "W158 path drift"
assert n1mod.WAVE_CONFIGS[158]["prereg"].startswith(
    "research/PERPETUAL_N1_W158_PREREG.md"), "W158 per-wave prereg citation drift"
assert n1mod.WAVE_CONFIGS[157]["a_seed_base"] == 360_204 and \
    n1mod.WAVE_CONFIGS[157]["b_exit_seed_base"] == 362_204, "W157 entry survived"
assert os.path.exists(os.path.join("research", "PERPETUAL_N1_W158_PREREG.md")), \
    "W158 per-wave prereg missing on disk"

n2 = io.open(N1, encoding="utf-8", newline="").read()
w2 = n2.find("# --- W158 materializer face")
assert w2 > 0, "W158 materializer block title missing"
t3 = n2.find("# --- T-141 s2 lane face", w2)
blk2 = n2[w2:t3]
ci2 = blk2.find("assert pf.N1_BANDS[138]")
cj2 = blk2.find("# prior-wave disjointness")
chain_rows2 = re.findall(r"assert pf\.N1_BANDS\[(\d+)\]", blk2[ci2:cj2])
assert chain_rows2 == [str(x) for x in range(138, 158)], chain_rows2

# r773 pit law leg 3: full-file start>end malformed-window scans on BOTH files
for path in (PF, N1):
    txt = io.open(path, encoding="utf-8", newline="").read()
    bad = [m.group() for m in re.finditer(r"(\d{3})_(\d{3})\.\.(\d{3})_(\d{3})", txt)
           if int(m.group(3)) < int(m.group(1))]
    assert not bad, f"malformed windows remain in {path}: {bad[:4]}"
    assert "362_204..362_003" not in txt and "362_404..360_403" not in txt, \
        f"r772 malformed-window residue in {path}"

# W159 projection prose present in the new W158 blocks (gate leg3 verbatim)
pf2 = io.open(PF, encoding="utf-8", newline="").read()
assert f"# {W159p_A} CLEAN hops=0 / B first-clean {W159p_B}" in pf2, "pf W159p prose missing"
assert "W159 A window; W159 freezer MUST re-derive on the post-W158" in pf2, \
    "pf W159 freezer prose missing"
assert "W159 A window; W159 freezer" in n2, "n1 W159 freezer prose missing"
assert f"A first-clean {W159p_A} " in n2 and f"B first-clean {W159p_B} CLEAN" in n2, \
    "n1 entry W159p prose missing"
# claim line present
assert '"r773 bm-a] "' in n2, "W158 PASS-snippet claim tail missing"
# band-gate receipt citations
assert "results/_r773bma_w158_band_gate.json" in pf2 and \
    "results/_r773bma_w158_band_gate.json" in n2, "gate receipt citations missing"
assert "results/_r773bma_w158_probe_receipt.json" in pf2, "probe receipt citation missing"
# seat citations
assert "MSG-2026-10-06-120x-bma-w158-seat" in pf2 and "24aff72f5" in pf2, "seat cite missing"
# stats chain updated (W157 finalize r773)
assert n2.count("741,411") >= 2 and n2.count("343,320") >= 2, "finalize stats not updated"
# r772 freeze sha cite
assert "aed41df3e" in n2, "W157 freeze sha cite missing"

# git diff sanity: only the two intended files carry freeze changes
print("post-edit structural assertions ALL PASS: N1_BANDS 156 rows tail W158, "
      "W157 row/entry intact, WAVE_CONFIGS[158] seeded, chain 138..157 n=20, "
      "W159p prose == r773 gate leg3 verbatim on both files, full-file "
      "malformed-window scans CLEAN, seat/gate/probe citations in place")
