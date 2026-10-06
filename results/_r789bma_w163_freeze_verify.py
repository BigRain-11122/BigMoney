# -*- coding: utf-8 -*-
"""r789 bm-a W163 freeze post-edit verify suite (r781 law: edit-write and
assert-suite separated -- this file is read-only verification of the
landed W163 freeze; it never edits)."""
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
gate = json.load(open("results/_r789bma_w163_band_gate.json", encoding="utf-8"))
assert gate["verdict"] == "ADMIT" and gate["bands"] == {"A": "373404_375403", "B": "375404_375603"}, gate
leg3 = gate["legs"]["leg3"]
W164p_A, W164p_B = "375_404..377_403", "375_604..375_803"
assert leg3["W164p_A"] == "375404..377403" and leg3["W164p_B"] == "375604..375803", leg3
probe = json.load(open("results/_r789bma_w163_probe_receipt.json", encoding="utf-8"))
assert probe["verdict"] == "ADMIT" and probe["legs"]["leg1"]["A"] == [373404, 375403], probe
assert gate["legs"]["leg0b"]["own_seat_on_origin"] is True, "seat leg0b"
assert gate["legs"]["leg0"]["ordinal"] == 153 and gate["legs"]["leg0"]["bma_ordinal"] == 79, "ordinal drift"
print("leg1: gate/probe receipts ADMIT re-read PASS (153rd wave, bm-a 79th)")

# 2. live registry faces
sys.path.insert(0, ".")
sys.path.insert(0, "scripts")
import importlib
import perpetual_faces as pf
importlib.reload(pf)
assert sorted(pf.N1_BANDS)[-1] == 163 and len(pf.N1_BANDS) == 161, "row count drift"
assert pf.N1_BANDS[163] == {"a": (373_404, 375_403), "b_exit": (375_404, 375_603),
                            "engine_owner": "bm-a"}, "W163 row drift"
assert pf.N1_BANDS[162] == {"a": (371_204, 373_203), "b_exit": (373_204, 373_403),
                            "engine_owner": "bm-a"}, "W162 row survived"
assert pf.N1_BANDS[161] == {"a": (369_004, 371_003), "b_exit": (371_004, 371_203),
                            "engine_owner": "bm-a"}, "W161 row survived"
import perpetual_faces_n1 as n1mod
importlib.reload(n1mod)
cfg = n1mod.WAVE_CONFIGS[163]
assert cfg["a_seed_base"] == 373_404 and cfg["b_exit_seed_base"] == 375_404, "seed bases"
assert cfg["shard_subdir"] == "n1_w163" and cfg["out_name"] == "n1_w163_results.json", "paths"
assert cfg["prereg"].startswith("research/PERPETUAL_N1_W163_PREREG.md"), "prereg citation"
assert cfg.get("engine_owner") == "bm-a", "engine_owner"
assert os.path.exists(os.path.join("research", "PERPETUAL_N1_W163_PREREG.md")), "prereg on disk"
print("leg2: N1_BANDS 161 rows tail W163 + WAVE_CONFIGS[163] live-import PASS")

# 3. materializer chain 138..162 (n=25)
w2 = n2.find("# --- W163 materializer face")
t3 = n2.find("# --- T-141 s2 lane face", w2)
assert 0 < w2 < t3, "W163 mat block missing"
blk2 = n2[w2:t3]
rows = re.findall(r"assert pf\.N1_BANDS\[(\d+)\]",
                  blk2[blk2.find("assert pf.N1_BANDS[138]"):
                        blk2.find("# prior-wave disjointness")])
assert rows == [str(x) for x in range(138, 163)], rows
assert '"registered W162 row parity drift (r307; bm-a r787)"' in blk2, "W162 chain row prose"
assert "_set_wave(163)" in blk2, "W163 set_wave face"
print("leg3: W163 materializer chain 138..162 n=25 PASS")

# 4. full-file malformed-window scans (r773 pit law leg 3)
for path, txt in ((PF, pf2), (N1, n2)):
    bad = [m.group() for m in re.finditer(r"(\d{3})_(\d{3})\.\.(\d{3})_(\d{3})", txt)
           if int(m.group(3)) < int(m.group(1))]
    assert not bad, f"malformed windows in {path}: {bad[:4]}"
    assert "362_204..362_003" not in txt and "362_404..360_403" not in txt, \
        f"r772 residue in {path}"
print("leg4: malformed-window scans CLEAN on both files")

# 5. W164+ projection prose == gate leg3 verbatim
assert f"# {W164p_A} CLEAN hops=0 / B first-clean {W164p_B}" in pf2, "pf W164p prose"
assert "W164 A window; W164 freezer MUST re-derive on the post-W163" in pf2, "pf freezer prose"
# r776 fragment-needle law: within-fragment shapes only
assert '"W164 A window; W164 freezer MUST re-derive on the "' in n2, "n1 freezer fragment"
assert '"W163 B band 375_404..375_603 will refuse the naive "' in n2, "n1 refuse fragment"
assert f"A first-clean {W164p_A} " in n2 and f"B first-clean {W164p_B} CLEAN" in n2, "n1 W164p prose"
print("leg5: W164+ projection prose == r789 gate leg3 verbatim PASS")

# 6. honesty faces
assert "move deferred to the W164 finalize window (W163 seat still in" in pf2, "pf self-ack frag1"
assert "fleet/inbox at freeze time -- honest state);" in pf2, "pf self-ack frag2"
assert "move deferred to the W164 finalize window (W163 seat still in" in n2, "mat self-ack frag1"
assert "fleet/inbox at freeze time -- honest state)." in n2, "mat self-ack frag2"
assert "payload = seat MSG + pre-seat probe + probe receipt;" in pf2, "pf 3-item payload face"
assert '"seat MSG + pre-seat probe + probe receipt; "' in n2, "entry 3-item payload face"
assert "= seat MSG + pre-seat probe + probe receipt;" in n2, "mat 3-item payload face"
assert "r789 pre-seat" in pf2 and "r789 pre-seat" in n2, "push session"
assert "direct fast-forward behind-0" in pf2 and "direct fast-forward behind-0" in n2, \
    "direct-FF delivery face"
assert '"number law after the REGISTERED W162 row bm-a r787 freeze "' in n2, "W162-row cite frag1"
assert '"764cd882a, SINGLE STATE zero seat gap W2..W162 all "' in n2, "W162-row cite frag2"
assert '"finalize one-pass bm-a r788, net chain head 761,812, "' in n2, "entry-tail frag"
assert n2.count("W162 finalize one-pass bm-a r788") == 1, "W162 finalize one-pass count"
assert "W162 bm-a r788 one-pass" in n2, "COP face"
assert "bm-a r787 freeze 764cd882a" in n2, "mat header registered-row citation (anti-drift)"
assert "678a07d4f" not in blk2, "stale W161 sha residue in new block"
assert "761,812" in n2 and "354,320" in n2, "ledger/K faces"
assert "own-wave A window reserved jumps to 375_404, first-clean " in blk2, \
    "W163 jump-fragment face (r787 heal lineage carried via @JB@)"
assert "own-wave A window reserved jumps to 373_204, first-clean" not in blk2, \
    "vmap-leak residue in new block"
# the W162 entry's own frozen face stays untouched (git history face)
i162 = n2.find('162: {"batch"')
seg162 = n2[i162:n2.find('"engine_owner": "bm-a"},', i162)]
assert "bm-a r785 freeze" in seg162 and "678a07d4f" in seg162, \
    "W162 entry frozen face must stay untouched (r307 two-state law)"
print("leg6: honesty faces PASS (self-ack deferred / 3-item payload / direct-FF / anti-drift registered-row / heal lineage carried / W162 entry frozen intact)")

# 7. stale-scan in the NEW W163 blocks only (frozen faces keep their history)
EO = '"engine_owner": "bm-a"},'
i2 = pf2.find("    # W163 (bm-a r789 freeze")
j2 = pf2.find(EO, i2) + len(EO)
newpfblk = pf2[i2:j2]
k2 = n2.find('163: {"batch"')
m2 = n2.find(EO, k2) + len(EO)
newentry = n2[k2:m2]
cs2 = n2.find('"+ W163 materializer face')
ce2 = n2.find('"r789 bm-a] "', cs2) + len('"r789 bm-a] "')
newclaim = n2[cs2:ce2]
assert i2 > 0 and k2 > 0 and cs2 > 0, "new W163 block anchors missing"
# the mat CHAIN rows (138..162 parity asserts) are verbatim prior-wave
# pinned constants (r307) -- historical band values there are legitimate;
# scan only the freshly vmap'd pre (header) + post (band-facts) faces
ci2 = blk2.find("assert pf.N1_BANDS[138]")
cj2 = blk2.find("# prior-wave disjointness")
mat_new_faces = blk2[:ci2] + blk2[cj2:]
for tag, seg in (("pf", newpfblk), ("entry", newentry), ("mat", mat_new_faces),
                 ("claim", newclaim)):
    for stale in ("r785 gate", "r786 sec8", "r787 pre-seat", "r785 bm-a freeze",
                  "bm-a r785 freeze", "MSG-2026-10-06-175x", "1d43d7906", "bma-w162-seat",
                  "MSG-175x", "merge-absorb", "371_004", "371_204", "371_403",
                  "371_203", "373_003", "373_203", "759,612", "352,120", "ee04482a2",
                  "678a07d4f", "6957f509e", "bm-b r779", "a2d002357", "twentieth",
                  "twenty-first", "seventy-seventh", "seventy-eighth",
                  "ONE HUNDRED-AND-FIFTY-SECOND", "engine_owner rows 151",
                  "rows 77 + candidate", "facts helper", "arc generator"):
        assert stale not in seg, f"stale {stale!r} residue in new W163 {tag} block"
print("leg7: new-block stale scans CLEAN (pf/entry/mat/claim)")

# 8. seat + prereg artifacts on origin/disk (W163 seat still in fleet/inbox
# at freeze time -- honest deferred state; self-ack lands at the W163
# finalize window or earlier via the observer lane)
assert os.path.exists("fleet/inbox/MSG-2026-10-06-183x-bma-w163-seat.md") or \
    os.path.exists("fleet/inbox/processed/MSG-2026-10-06-183x-bma-w163-seat.md"), "seat file"
r = __import__("subprocess").run(["git", "ls-tree", "--name-only", "-r", "origin/main",
                                  "--", "fleet/inbox/", "fleet/inbox/processed/"],
                                 capture_output=True)
assert b"fleet/inbox/MSG-2026-10-06-183x-bma-w163-seat.md" in r.stdout or \
    b"fleet/inbox/processed/MSG-2026-10-06-183x-bma-w163-seat.md" in r.stdout, \
    "seat on origin (r565 law)"
print("leg8: seat published on origin + prereg on disk PASS")

print("W163 FREEZE VERIFY SUITE rc0 ALL PASS")
