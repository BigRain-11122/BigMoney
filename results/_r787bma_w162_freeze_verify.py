# -*- coding: utf-8 -*-
"""r787 bm-a W162 freeze post-edit verify suite (r781 law: edit-write and
assert-suite separated -- this file is read-only verification of the
landed W162 freeze; it never edits)."""
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
gate = json.load(open("results/_r787bma_w162_band_gate.json", encoding="utf-8"))
assert gate["verdict"] == "ADMIT" and gate["bands"] == {"A": "371204_373203", "B": "373204_373403"}, gate
leg3 = gate["legs"]["leg3"]
W163p_A, W163p_B = "373_204..375_203", "373_404..373_603"
assert leg3["W163p_A"] == "373204..375203" and leg3["W163p_B"] == "373404..373603", leg3
probe = json.load(open("results/_r787bma_w162_probe_receipt.json", encoding="utf-8"))
assert probe["verdict"] == "ADMIT" and probe["legs"]["leg1"]["A"] == [371204, 373203], probe
assert gate["legs"]["leg0b"]["own_seat_on_origin"] is True, "seat leg0b"
assert gate["legs"]["leg0"]["ordinal"] == 152 and gate["legs"]["leg0"]["bma_ordinal"] == 78, "ordinal drift"
print("leg1: gate/probe receipts ADMIT re-read PASS (152nd wave, bm-a 78th)")

# 2. live registry faces
sys.path.insert(0, ".")
sys.path.insert(0, "scripts")
import importlib
import perpetual_faces as pf
importlib.reload(pf)
assert sorted(pf.N1_BANDS)[-1] == 162 and len(pf.N1_BANDS) == 160, "row count drift"
assert pf.N1_BANDS[162] == {"a": (371_204, 373_203), "b_exit": (373_204, 373_403),
                            "engine_owner": "bm-a"}, "W162 row drift"
assert pf.N1_BANDS[161] == {"a": (369_004, 371_003), "b_exit": (371_004, 371_203),
                            "engine_owner": "bm-a"}, "W161 row survived"
assert pf.N1_BANDS[160] == {"a": (366_804, 368_803), "b_exit": (368_804, 369_003),
                            "engine_owner": "bm-a"}, "W160 row survived"
import perpetual_faces_n1 as n1mod
importlib.reload(n1mod)
cfg = n1mod.WAVE_CONFIGS[162]
assert cfg["a_seed_base"] == 371_204 and cfg["b_exit_seed_base"] == 373_204, "seed bases"
assert cfg["shard_subdir"] == "n1_w162" and cfg["out_name"] == "n1_w162_results.json", "paths"
assert cfg["prereg"].startswith("research/PERPETUAL_N1_W162_PREREG.md"), "prereg citation"
assert cfg.get("engine_owner") == "bm-a", "engine_owner"
assert os.path.exists(os.path.join("research", "PERPETUAL_N1_W162_PREREG.md")), "prereg on disk"
print("leg2: N1_BANDS 160 rows tail W162 + WAVE_CONFIGS[162] live-import PASS")

# 3. materializer chain 138..161 (n=24)
w2 = n2.find("# --- W162 materializer face")
t3 = n2.find("# --- T-141 s2 lane face", w2)
assert 0 < w2 < t3, "W162 mat block missing"
blk2 = n2[w2:t3]
rows = re.findall(r"assert pf\.N1_BANDS\[(\d+)\]",
                  blk2[blk2.find("assert pf.N1_BANDS[138]"):
                        blk2.find("# prior-wave disjointness")])
assert rows == [str(x) for x in range(138, 162)], rows
assert '"registered W161 row parity drift (r307; bm-a r785)"' in blk2, "W161 chain row prose"
assert "_set_wave(162)" in blk2, "W162 set_wave face"
print("leg3: W162 materializer chain 138..161 n=24 PASS")

# 4. full-file malformed-window scans (r773 pit law leg 3)
for path, txt in ((PF, pf2), (N1, n2)):
    bad = [m.group() for m in re.finditer(r"(\d{3})_(\d{3})\.\.(\d{3})_(\d{3})", txt)
           if int(m.group(3)) < int(m.group(1))]
    assert not bad, f"malformed windows in {path}: {bad[:4]}"
    assert "362_204..362_003" not in txt and "362_404..360_403" not in txt, \
        f"r772 residue in {path}"
print("leg4: malformed-window scans CLEAN on both files")

# 5. W163+ projection prose == gate leg3 verbatim
assert f"# {W163p_A} CLEAN hops=0 / B first-clean {W163p_B}" in pf2, "pf W163p prose"
assert "W163 A window; W163 freezer MUST re-derive on the post-W162" in pf2, "pf freezer prose"
# r776 fragment-needle law: within-fragment shapes only
assert '"W163 A window; W163 freezer MUST re-derive on the "' in n2, "n1 freezer fragment"
assert '"W162 B band 373_204..373_403 will refuse the naive "' in n2, "n1 refuse fragment"
assert f"A first-clean {W163p_A} " in n2 and f"B first-clean {W163p_B} CLEAN" in n2, "n1 W163p prose"
print("leg5: W163+ projection prose == r787 gate leg3 verbatim PASS")

# 6. honesty faces
assert "move deferred to the W163 finalize window (W162 seat still in" in pf2, "pf self-ack frag1"
assert "fleet/inbox at freeze time -- honest state);" in pf2, "pf self-ack frag2"
assert "move deferred to the W163 finalize window (W162 seat still in" in n2, "mat self-ack frag1"
assert "fleet/inbox at freeze time -- honest state)." in n2, "mat self-ack frag2"
assert "facts helper" in pf2 and "facts helper" in n2, "payload facts-helper face"
assert "r787 pre-seat" in pf2 and "r787 pre-seat" in n2, "push session"
assert "direct fast-forward behind-0" in pf2 and "direct fast-forward behind-0" in n2, \
    "direct-FF delivery face"
assert '"number law after the REGISTERED W161 row bm-a r785 freeze "' in n2, "W161-row cite frag1"
assert '"678a07d4f, SINGLE STATE zero seat gap W2..W161 all "' in n2, "W161-row cite frag2"
assert '"finalize one-pass bm-a r786, net chain head 759,612, "' in n2, "entry-tail frag"
assert n2.count("W161 finalize one-pass bm-a r786") == 1, "W161 finalize one-pass count"
assert "W161 bm-a r786 one-pass" in n2, "COP face"
assert "bm-a r785 freeze 678a07d4f" in n2, "mat header registered-row citation (anti-drift)"
assert "ee04482a2" not in blk2, "stale W160 sha residue in new block"
assert "759,612" in n2 and "352,120" in n2, "ledger/K faces"
assert "own-wave A window reserved jumps to 373_204, first-clean " in blk2, \
    "W162 healed-fragment face (r787 heal carried via @JB@)"
assert "own-wave A window reserved jumps to 368_804, first-clean" not in blk2, \
    "vmap-leak residue in new block"
# the W161 entry's own frozen face stays untouched (git history face)
i161 = n2.find('161: {"batch"')
seg161 = n2[i161:n2.find('"engine_owner": "bm-a"},', i161)]
assert "bm-a r783 freeze" in seg161 and "ee04482a2" in seg161, \
    "W161 entry frozen face must stay untouched (r307 two-state law)"
print("leg6: honesty faces PASS (self-ack deferred / facts-helper payload / direct-FF / anti-drift registered-row / heal carried / W161 entry frozen intact)")

# 7. stale-scan in the NEW W162 blocks only (frozen faces keep their history)
EO = '"engine_owner": "bm-a"},'
i2 = pf2.find("    # W162 (bm-a r787 freeze")
j2 = pf2.find(EO, i2) + len(EO)
newpfblk = pf2[i2:j2]
k2 = n2.find('162: {"batch"')
m2 = n2.find(EO, k2) + len(EO)
newentry = n2[k2:m2]
cs2 = n2.find('"+ W162 materializer face')
ce2 = n2.find('"r787 bm-a] "', cs2) + len('"r787 bm-a] "')
newclaim = n2[cs2:ce2]
assert i2 > 0 and k2 > 0 and cs2 > 0, "new W162 block anchors missing"
# the mat CHAIN rows (138..161 parity asserts) are verbatim prior-wave
# pinned constants (r307) -- historical band values there are legitimate;
# scan only the freshly vmap'd pre (header) + post (band-facts) faces
ci2 = blk2.find("assert pf.N1_BANDS[138]")
cj2 = blk2.find("# prior-wave disjointness")
mat_new_faces = blk2[:ci2] + blk2[cj2:]
for tag, seg in (("pf", newpfblk), ("entry", newentry), ("mat", mat_new_faces),
                 ("claim", newclaim)):
    for stale in ("r783 gate", "r784 sec8", "r785 pre-seat", "r785 bm-a freeze",
                  "bm-a r783 freeze", "MSG-2026-10-06-165x", "0371f2093", "bma-w161-seat",
                  "MSG-165x", "merge-absorb", "369_004", "368_804", "369_003",
                  "371_003", "757,412", "349,920", "ee04482a2", "6957f509e",
                  "bm-b r779", "a2d002357", "twentieth", "seventy-seventh",
                  "ONE HUNDRED-AND-FIFTY-FIRST", "engine_owner rows 150",
                  "rows 76 + candidate", "W161 arc generator"):
        assert stale not in seg, f"stale {stale!r} residue in new W162 {tag} block"
print("leg7: new-block stale scans CLEAN (pf/entry/mat/claim)")

# 8. seat + prereg artifacts on origin/disk (W162 seat still in fleet/inbox
# at freeze time -- honest deferred state; self-ack lands at the W162
# finalize window)
assert os.path.exists("fleet/inbox/MSG-2026-10-06-175x-bma-w162-seat.md") or \
    os.path.exists("fleet/inbox/processed/MSG-2026-10-06-175x-bma-w162-seat.md"), "seat file"
r = __import__("subprocess").run(["git", "ls-tree", "--name-only", "-r", "origin/main",
                                  "--", "fleet/inbox/", "fleet/inbox/processed/"],
                                 capture_output=True)
assert b"fleet/inbox/MSG-2026-10-06-175x-bma-w162-seat.md" in r.stdout or \
    b"fleet/inbox/processed/MSG-2026-10-06-175x-bma-w162-seat.md" in r.stdout, \
    "seat on origin (r565 law)"
assert os.path.exists("results/_r787bma_w162_w161prose_heal.py"), "heal script on disk"
print("leg8: seat published on origin + prereg on disk + heal script PASS")

print("W162 FREEZE VERIFY SUITE rc0 ALL PASS")
