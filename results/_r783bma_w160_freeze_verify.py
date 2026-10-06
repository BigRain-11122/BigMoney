# -*- coding: utf-8 -*-
"""r783 bm-a W160 freeze post-edit verify suite (r781 law: edit-write and
assert-suite separated -- this file is read-only verification of the
landed W160 freeze; it never edits)."""
import ast
import io
import json
import re
import os
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
PF = r"scripts/perpetual_faces.py"
N1 = r"scripts/perpetual_faces_n1.py"
pf2 = io.open(PF, encoding="utf-8", newline="").read()
n2 = io.open(N1, encoding="utf-8", newline="").read()

# 0. AST gates
ast.parse(pf2)
ast.parse(n2)
print("leg0: AST gates PASS on both files")

# 1. machine-derived facts re-read from on-disk receipts (r587)
gate = json.load(open("results/_r783bma_w160_band_gate.json", encoding="utf-8"))
assert gate["verdict"] == "ADMIT" and gate["bands"] == {"A": "366804_368803", "B": "368804_369003"}, gate
leg3 = gate["legs"]["leg3"]
W161p_A, W161p_B = "368_804..370_803", "369_004..369_203"
assert leg3["W161p_A"] == "368804..370803" and leg3["W161p_B"] == "369004..369203", leg3
probe = json.load(open("results/_r782bma_w160_probe_receipt.json", encoding="utf-8"))
assert probe["verdict"] == "ADMIT" and probe["legs"]["leg1"]["A"] == [366804, 368803], probe
print("leg1: gate/probe receipts ADMIT re-read PASS")

# 2. live registry faces
sys.path.insert(0, ".")
sys.path.insert(0, "scripts")
import importlib
import perpetual_faces as pf
importlib.reload(pf)
assert sorted(pf.N1_BANDS)[-1] == 160 and len(pf.N1_BANDS) == 158, "row count drift"
assert pf.N1_BANDS[160] == {"a": (366_804, 368_803), "b_exit": (368_804, 369_003),
                            "engine_owner": "bm-a"}, "W160 row drift"
assert pf.N1_BANDS[159] == {"a": (364_604, 366_603), "b_exit": (366_604, 366_803),
                            "engine_owner": "bm-a"}, "W159 row survived"
assert pf.N1_BANDS[158] == {"a": (362_404, 364_403), "b_exit": (364_404, 364_603),
                            "engine_owner": "bm-a"}, "W158 row survived"
import perpetual_faces_n1 as n1mod
importlib.reload(n1mod)
cfg = n1mod.WAVE_CONFIGS[160]
assert cfg["a_seed_base"] == 366_804 and cfg["b_exit_seed_base"] == 368_804, "seed bases"
assert cfg["shard_subdir"] == "n1_w160" and cfg["out_name"] == "n1_w160_results.json", "paths"
assert cfg["prereg"].startswith("research/PERPETUAL_N1_W160_PREREG.md"), "prereg citation"
assert cfg.get("engine_owner") == "bm-a", "engine_owner"
assert os.path.exists(os.path.join("research", "PERPETUAL_N1_W160_PREREG.md")), "prereg on disk"
print("leg2: N1_BANDS 158 rows tail W160 + WAVE_CONFIGS[160] live-import PASS")

# 3. materializer chain 138..159 (n=22)
w2 = n2.find("# --- W160 materializer face")
t3 = n2.find("# --- T-141 s2 lane face", w2)
assert 0 < w2 < t3, "W160 mat block missing"
blk2 = n2[w2:t3]
rows = re.findall(r"assert pf\.N1_BANDS\[(\d+)\]",
                  blk2[blk2.find("assert pf.N1_BANDS[138]"):
                        blk2.find("# prior-wave disjointness")])
assert rows == [str(x) for x in range(138, 160)], rows
assert '"registered W159 row parity drift (r307; bm-a r781)"' in blk2, "W159 chain row prose"
print("leg3: W160 materializer chain 138..159 n=22 PASS")

# 4. full-file malformed-window scans (r773 pit law leg 3)
for path, txt in ((PF, pf2), (N1, n2)):
    bad = [m.group() for m in re.finditer(r"(\d{3})_(\d{3})\.\.(\d{3})_(\d{3})", txt)
           if int(m.group(3)) < int(m.group(1))]
    assert not bad, f"malformed windows in {path}: {bad[:4]}"
    assert "362_204..362_003" not in txt and "362_404..360_403" not in txt, \
        f"r772 residue in {path}"
print("leg4: malformed-window scans CLEAN on both files")

# 5. W161+ projection prose == gate leg3 verbatim
assert f"# {W161p_A} CLEAN hops=0 / B first-clean {W161p_B}" in pf2, "pf W161p prose"
assert "W161 A window; W161 freezer MUST re-derive on the post-W160" in pf2, "pf freezer prose"
# r776 fragment-needle law: within-fragment shapes only
assert '"W161 A window; W161 freezer MUST re-derive on the "' in n2, "n1 freezer fragment"
assert '"W160 B band 368_804..369_003 will refuse the naive "' in n2, "n1 refuse fragment"
assert f"A first-clean {W161p_A} " in n2 and f"B first-clean {W161p_B} CLEAN" in n2, "n1 W161p prose"
print("leg5: W161+ projection prose == r783 gate leg3 verbatim PASS")

# 6. honesty faces
assert "move deferred to the W160 finalize window (seat still in" in pf2, "pf self-ack"
assert "self-ack inbox->processed move deferred to the" in n2, "mat self-ack"
assert "W160 finalize window (seat still in fleet/inbox at freeze" in n2, "mat self-ack tail"
assert "r782 pre-seat" in pf2 and "r782 pre-seat" in n2, "push session"
assert '"number law after the REGISTERED W159 row bm-a r781 freeze "' in n2, "W159-row cite frag1"
assert '"6ee1207bb, SINGLE STATE zero seat gap W2..W159 all "' in n2, "W159-row cite frag2"
assert n2.count("W159 finalize one-pass bm-a r782") == 1, "W159 finalize mat-header heal count"
assert '"finalize one-pass bm-a r782, net chain head 755,212, "' in n2, "entry-tail frag heal"
assert "finalize one-pass bm-a r783" not in n2, "stale r783 finalize residue"
assert "W159 bm-a r782 one-pass" in n2, "COP face"
assert "755,212" in n2 and "347,720" in n2, "ledger/K faces"
# the W159 entry's own frozen (drifted) face stays untouched (git history)
i159 = n2.find('159: {"batch"')
seg159 = n2[i159:n2.find('"engine_owner": "bm-a"},', i159)]
assert "bm-a r773 freeze" in seg159 and "aed41df3e" in seg159, \
    "W159 entry frozen face must stay untouched (r307 two-state law)"
print("leg6: honesty faces PASS (self-ack deferred / drift-heal / r782 push / frozen W159 face intact)")

# 7. seat + prereg + banned gate artifacts on disk
assert os.path.exists("fleet/inbox/MSG-2026-10-06-162x-bma-w160-seat.md") or \
    os.path.exists("fleet/inbox/processed/MSG-2026-10-06-162x-bma-w160-seat.md"), "seat file"
r = __import__("subprocess").run(["git", "ls-tree", "--name-only", "origin/main", "--",
                                  "fleet/inbox/"], capture_output=True)
assert b"MSG-2026-10-06-162x-bma-w160-seat.md" in r.stdout, "seat on origin (r565 law)"
print("leg7: seat published on origin + prereg on disk PASS")

print("W160 FREEZE VERIFY SUITE rc0 ALL PASS")
