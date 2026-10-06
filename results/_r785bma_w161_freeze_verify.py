# -*- coding: utf-8 -*-
"""r785 bm-a W161 freeze post-edit verify suite (r781 law: edit-write and
assert-suite separated -- this file is read-only verification of the
landed W161 freeze; it never edits)."""
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
gate = json.load(open("results/_r785bma_w161_band_gate.json", encoding="utf-8"))
assert gate["verdict"] == "ADMIT" and gate["bands"] == {"A": "369004_371003", "B": "371004_371203"}, gate
leg3 = gate["legs"]["leg3"]
W162p_A, W162p_B = "371_004..373_003", "371_204..371_403"
assert leg3["W162p_A"] == "371004..373003" and leg3["W162p_B"] == "371204..371403", leg3
probe = json.load(open("results/_r785bma_w161_probe_receipt.json", encoding="utf-8"))
assert probe["verdict"] == "ADMIT" and probe["legs"]["leg1"]["A"] == [369004, 371003], probe
assert gate["legs"]["leg0b"]["own_seat_on_origin"] is True, "seat leg0b"
print("leg1: gate/probe receipts ADMIT re-read PASS")

# 2. live registry faces
sys.path.insert(0, ".")
sys.path.insert(0, "scripts")
import importlib
import perpetual_faces as pf
importlib.reload(pf)
assert sorted(pf.N1_BANDS)[-1] == 161 and len(pf.N1_BANDS) == 159, "row count drift"
assert pf.N1_BANDS[161] == {"a": (369_004, 371_003), "b_exit": (371_004, 371_203),
                            "engine_owner": "bm-a"}, "W161 row drift"
assert pf.N1_BANDS[160] == {"a": (366_804, 368_803), "b_exit": (368_804, 369_003),
                            "engine_owner": "bm-a"}, "W160 row survived"
assert pf.N1_BANDS[159] == {"a": (364_604, 366_603), "b_exit": (366_604, 366_803),
                            "engine_owner": "bm-a"}, "W159 row survived"
import perpetual_faces_n1 as n1mod
importlib.reload(n1mod)
cfg = n1mod.WAVE_CONFIGS[161]
assert cfg["a_seed_base"] == 369_004 and cfg["b_exit_seed_base"] == 371_004, "seed bases"
assert cfg["shard_subdir"] == "n1_w161" and cfg["out_name"] == "n1_w161_results.json", "paths"
assert cfg["prereg"].startswith("research/PERPETUAL_N1_W161_PREREG.md"), "prereg citation"
assert cfg.get("engine_owner") == "bm-a", "engine_owner"
assert os.path.exists(os.path.join("research", "PERPETUAL_N1_W161_PREREG.md")), "prereg on disk"
print("leg2: N1_BANDS 159 rows tail W161 + WAVE_CONFIGS[161] live-import PASS")

# 3. materializer chain 138..160 (n=23)
w2 = n2.find("# --- W161 materializer face")
t3 = n2.find("# --- T-141 s2 lane face", w2)
assert 0 < w2 < t3, "W161 mat block missing"
blk2 = n2[w2:t3]
rows = re.findall(r"assert pf\.N1_BANDS\[(\d+)\]",
                  blk2[blk2.find("assert pf.N1_BANDS[138]"):
                        blk2.find("# prior-wave disjointness")])
assert rows == [str(x) for x in range(138, 161)], rows
assert '"registered W160 row parity drift (r307; bm-a r783)"' in blk2, "W160 chain row prose"
print("leg3: W161 materializer chain 138..160 n=23 PASS")

# 4. full-file malformed-window scans (r773 pit law leg 3)
for path, txt in ((PF, pf2), (N1, n2)):
    bad = [m.group() for m in re.finditer(r"(\d{3})_(\d{3})\.\.(\d{3})_(\d{3})", txt)
           if int(m.group(3)) < int(m.group(1))]
    assert not bad, f"malformed windows in {path}: {bad[:4]}"
    assert "362_204..362_003" not in txt and "362_404..360_403" not in txt, \
        f"r772 residue in {path}"
print("leg4: malformed-window scans CLEAN on both files")

# 5. W162+ projection prose == gate leg3 verbatim
assert f"# {W162p_A} CLEAN hops=0 / B first-clean {W162p_B}" in pf2, "pf W162p prose"
assert "W162 A window; W162 freezer MUST re-derive on the post-W161" in pf2, "pf freezer prose"
# r776 fragment-needle law: within-fragment shapes only
assert '"W162 A window; W162 freezer MUST re-derive on the "' in n2, "n1 freezer fragment"
assert '"W161 B band 371_004..371_203 will refuse the naive "' in n2, "n1 refuse fragment"
assert f"A first-clean {W162p_A} " in n2 and f"B first-clean {W162p_B} CLEAN" in n2, "n1 W162p prose"
print("leg5: W162+ projection prose == r785 gate leg3 verbatim PASS")

# 6. honesty faces
assert "bm-b r779 read-only-observer processed, a2d002357" in pf2, "pf self-ack"
assert "self-ack inbox->processed move landed (bm-b" in n2, "mat self-ack frag1"
assert "r779 read-only-observer processed, a2d002357)." in n2, "mat self-ack frag2"
assert "r785 pre-seat" in pf2 and "r785 pre-seat" in n2, "push session"
assert "direct fast-forward behind-0" in pf2 and "direct fast-forward behind-0" in n2, \
    "direct-FF delivery face"
assert '"number law after the REGISTERED W160 row bm-a r783 freeze "' in n2, "W160-row cite frag1 heal"
assert '"ee04482a2, SINGLE STATE zero seat gap W2..W160 all "' in n2, "W160-row cite frag2 heal"
assert '"finalize one-pass bm-a r784, net chain head 757,412, "' in n2, "entry-tail frag heal"
assert n2.count("W160 finalize one-pass bm-a r784") == 1, "W160 finalize mat-header heal count"
assert "W160 bm-a r784 one-pass" in n2, "COP face"
assert "bm-a r783 freeze ee04482a2" in n2, "mat header registered-row drift heal"
assert "6957f509e" not in blk2, "mat header stale W158 sha residue in new block"
assert "757,412" in n2 and "349,920" in n2, "ledger/K faces"
# the W160 entry's own frozen face stays untouched (git history)
i160 = n2.find('160: {"batch"')
seg160 = n2[i160:n2.find('"engine_owner": "bm-a"},', i160)]
assert "bm-a r781 freeze" in seg160 and "6ee1207bb" in seg160, \
    "W160 entry frozen face must stay untouched (r307 two-state law)"
print("leg6: honesty faces PASS (self-ack landed bm-b r779 / direct-FF / drift-heal / frozen W160 face intact)")

# 7. stale-scan in the NEW W161 blocks only (frozen faces keep their history)
EO = '"engine_owner": "bm-a"},'
i2 = pf2.find("    # W161 (bm-a r785 freeze")
j2 = pf2.find(EO, i2) + len(EO)
newpfblk = pf2[i2:j2]
k2 = n2.find('161: {"batch"')
m2 = n2.find(EO, k2) + len(EO)
newentry = n2[k2:m2]
cs2 = n2.find('"+ W161 materializer face')
ce2 = n2.find('"r785 bm-a] "', cs2) + len('"r785 bm-a] "')
newclaim = n2[cs2:ce2]
assert i2 > 0 and k2 > 0 and cs2 > 0, "new W161 block anchors missing"
# the mat CHAIN rows (138..160 parity asserts) are verbatim prior-wave
# pinned constants (r307) -- historical band values there are legitimate;
# scan only the freshly vmap'd pre (header) + post (band-facts) faces
ci2 = blk2.find("assert pf.N1_BANDS[138]")
cj2 = blk2.find("# prior-wave disjointness")
mat_new_faces = blk2[:ci2] + blk2[cj2:]
for tag, seg in (("pf", newpfblk), ("entry", newentry), ("mat", mat_new_faces),
                 ("claim", newclaim)):
    for stale in ("r779 gate", "r779 sec8", "r782", "MSG-2026-10-06-162x", "566ec5f86",
                  "merge-absorb", "366_604", "366_804", "362_404", "755,212",
                  "347,720", "r781 freeze", "6ee1207bb"):
        assert stale not in seg, f"stale {stale!r} residue in new W161 {tag} block"
print("leg7: new-block stale scans CLEAN (pf/entry/mat/claim)")

# 8. seat + prereg artifacts on origin/disk (seat moved to processed/ by the
# bm-b r779 read-only-observer during this freeze window -- dual-path check)
assert os.path.exists("fleet/inbox/MSG-2026-10-06-165x-bma-w161-seat.md") or \
    os.path.exists("fleet/inbox/processed/MSG-2026-10-06-165x-bma-w161-seat.md"), "seat file"
r = __import__("subprocess").run(["git", "ls-tree", "--name-only", "-r", "origin/main",
                                  "--", "fleet/inbox/", "fleet/inbox/processed/"],
                                 capture_output=True)
assert (b"fleet/inbox/MSG-2026-10-06-165x-bma-w161-seat.md" in r.stdout or
        b"fleet/inbox/processed/MSG-2026-10-06-165x-bma-w161-seat.md" in r.stdout), \
    "seat on origin (r565 law)"
print("leg8: seat published on origin + prereg on disk PASS")

print("W161 FREEZE VERIFY SUITE rc0 ALL PASS")
