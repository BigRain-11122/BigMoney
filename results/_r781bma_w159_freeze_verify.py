# -*- coding: utf-8 -*-
"""r781 bm-a W159 freeze verify (asserts-only re-run after the edits
landed; the in-script post-edit suite halted on the r776-law
fragment-broken needle inherited from the r775 bloodline -- L310-style
'contiguous' needles are false-negatives across python-string fragment
boundaries; fragment-safe needles used here)."""
import ast
import io
import os
import re
import sys

PF = r"scripts/perpetual_faces.py"
N1 = r"scripts/perpetual_faces_n1.py"

# AST gates on both edited files
for p in (PF, N1):
    ast.parse(io.open(p, encoding="utf-8", newline="").read())
print("AST gates PASS both files")

sys.path.insert(0, ".")
sys.path.insert(0, "scripts")
import importlib
import perpetual_faces as pf
importlib.reload(pf)
assert sorted(pf.N1_BANDS)[-1] == 159 and len(pf.N1_BANDS) == 157, \
    "pf N1_BANDS row-count drift after W159 insert"
assert pf.N1_BANDS[159] == {"a": (364_604, 366_603),
                            "b_exit": (366_604, 366_803),
                            "engine_owner": "bm-a"}, "W159 row face drift"
assert pf.N1_BANDS[158] == {"a": (362_404, 364_403),
                            "b_exit": (364_404, 364_603),
                            "engine_owner": "bm-a"}, "W158 row survived (r560)"
import perpetual_faces_n1 as n1mod
importlib.reload(n1mod)
assert n1mod.WAVE_CONFIGS[159]["a_seed_base"] == 364_604 and \
    n1mod.WAVE_CONFIGS[159]["b_exit_seed_base"] == 366_604, "W159 seed bases drift"
assert n1mod.WAVE_CONFIGS[159]["shard_subdir"] == "n1_w159" and \
    n1mod.WAVE_CONFIGS[159]["out_name"] == "n1_w159_results.json", "W159 path drift"
assert n1mod.WAVE_CONFIGS[159]["prereg"].startswith("research/PERPETUAL_N1_W159_PREREG.md"), \
    "W159 per-wave prereg citation drift"
assert os.path.exists(os.path.join("research", "PERPETUAL_N1_W159_PREREG.md")), \
    "W159 per-wave prereg missing on disk"
print("registry faces PASS: N1_BANDS 157 rows tail W159; WAVE_CONFIGS[159] seeded; prereg on disk")

n2 = io.open(N1, encoding="utf-8", newline="").read()
w2 = n2.find("# --- W159 materializer face")
t3 = n2.find("# --- T-141 s2 lane face", w2)
assert 0 < w2 < t3, "W159 mat block anchors"
blk2 = n2[w2:t3]
chain_rows2 = re.findall(r"assert pf\.N1_BANDS\[(\d+)\]",
                         blk2[blk2.find("assert pf.N1_BANDS[138]"):
                              blk2.find("# prior-wave disjointness")])
assert chain_rows2 == [str(x) for x in range(138, 159)], chain_rows2
assert 'assert pf.N1_BANDS[158] == {"a": (362_404, 364_403),' in blk2 and \
    '"registered W158 row parity drift (r307; bm-a r775)"' in blk2, "W158 row assert missing"
print("materializer chain PASS: 138..158 n=21, W158 row appended")

# r773 pit law leg 3: full-file start>end malformed-window scans on BOTH files
for path in (PF, N1):
    txt = io.open(path, encoding="utf-8", newline="").read()
    bad = [m.group() for m in re.finditer(r"(\d{3})_(\d{3})\.\.(\d{3})_(\d{3})", txt)
           if int(m.group(3)) < int(m.group(1))]
    assert not bad, f"malformed windows remain in {path}: {bad[:4]}"
print("full-file malformed-window scans CLEAN on both files")

# W160 projection prose (gate leg3 verbatim) + freezer fragments
pf2 = io.open(PF, encoding="utf-8", newline="").read()
assert "# 366_604..368_603 CLEAN hops=0 / B first-clean 366_804..367_003" in pf2, \
    "pf W160p prose missing"
assert "W160 A window; W160 freezer MUST re-derive on the post-W159" in pf2, \
    "pf W160 freezer prose missing"
assert '"W160 A window; W160 freezer MUST re-derive on the "' in n2, "n1 W160 freezer fragment missing"
assert '"W159 B band 366_604..366_803 will refuse the naive "' in n2, "n1 W159-band refuse fragment missing"
assert "A first-clean 366_604..368_603 " in n2 and "B first-clean 366_804..367_003 CLEAN" in n2, \
    "n1 W160p prose missing"
print("W160p projection prose PASS (gate leg3 verbatim, both files)")

# honesty faces landed
assert "merge-absorb behind-delivery at fetch (r779 pre-seat" in pf2, "pf delivery fixup missing"
assert "bm-c r625 read-only-observer processed, e203e96c7" in pf2, "pf self-ack fixup missing"
assert "delivery window = merge-absorb behind-delivery " in n2, "n1 delivery fixup missing"
assert "bm-c r625 read-only-observer processed, e203e96c7" in n2, "mat self-ack fixup missing"
assert "bm-a r775 freeze 6957f509e" in n2, "W158 freeze citation missing"
assert "W158 finalize one-pass bm-a r778" in n2 and "753,012" in n2 and "345,520" in n2, \
    "W158 finalize facts missing"
# corrupted historical faces remain eradicated
for path in (PF, N1):
    txt = io.open(path, encoding="utf-8", newline="").read()
    assert "362_204..362_003" not in txt and "362_404..360_403" not in txt, \
        f"r772 malformed-window residue in {path}"
# seat citation faces
assert "MSG-2026-10-06-142x-bma-w159-seat" in pf2 and "7b60d09da" in pf2, "pf seat face"
assert "results/_r779bma_w159_band_gate.json" in pf2, "pf gate receipt face"
assert "results/_r779bma_w159_probe_receipt.json" in pf2, "pf probe receipt face"
print("honesty + citation faces PASS (merge-absorb delivery, bm-c r625 self-ack, "
      "r775/6957f509e W158 freeze, r778/753,012/345,520 finalize, 142x/7b60d09da seat)")
print("VERIFY rc0: all post-edit structural assertions PASS")
