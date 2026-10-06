# -*- coding: utf-8 -*-
"""r794 bm-a W165 freeze post-edit verify suite (r781 law: edit-write and
assert-suite separated -- this file is read-only verification of the
landed W165 freeze; it never edits)."""
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
gate = json.load(open("results/_r793bma_w165_band_gate.json", encoding="utf-8"))
assert gate["verdict"] == "ADMIT" and gate["bands"] == {"A": "377804_379803", "B": "379804_380003"}, gate
leg3 = gate["legs"]["leg3"]
W166p_A, W166p_B = "379_804..381_803", "380_004..380_203"
assert leg3["W166p_A"] == "379804..381803" and leg3["W166p_B"] == "380004..380203", leg3
probe = json.load(open("results/_r793bma_w165_probe_receipt.json", encoding="utf-8"))
assert probe["verdict"] == "ADMIT" and probe["legs"]["leg1"]["A"] == [377804, 379803], probe
assert gate["legs"]["leg0b"]["own_seat_on_origin"] is True, "seat leg0b"
assert gate["legs"]["leg0"]["ordinal"] == 155 and gate["legs"]["leg0"]["bma_ordinal"] == 81, "ordinal drift"
print("leg1: gate/probe receipts ADMIT re-read PASS (155th wave, bm-a 81st)")

# 2. live registry faces
sys.path.insert(0, ".")
sys.path.insert(0, "scripts")
import importlib
import perpetual_faces as pf
importlib.reload(pf)
assert sorted(pf.N1_BANDS)[-1] == 165 and len(pf.N1_BANDS) == 163, "row count drift"
assert pf.N1_BANDS[165] == {"a": (377_804, 379_803), "b_exit": (379_804, 380_003),
                            "engine_owner": "bm-a"}, "W165 row drift"
assert pf.N1_BANDS[164] == {"a": (375_604, 377_603), "b_exit": (377_604, 377_803),
                            "engine_owner": "bm-a"}, "W164 row survived"
assert pf.N1_BANDS[163] == {"a": (373_404, 375_403), "b_exit": (375_404, 375_603),
                            "engine_owner": "bm-a"}, "W163 row survived"
import perpetual_faces_n1 as n1mod
importlib.reload(n1mod)
cfg = n1mod.WAVE_CONFIGS[165]
assert cfg["a_seed_base"] == 377_804 and cfg["b_exit_seed_base"] == 379_804, "seed bases"
assert cfg["shard_subdir"] == "n1_w165" and cfg["out_name"] == "n1_w165_results.json", "paths"
assert cfg["prereg"].startswith("research/PERPETUAL_N1_W165_PREREG.md"), "prereg citation"
assert cfg.get("engine_owner") == "bm-a", "engine_owner"
assert os.path.exists(os.path.join("research", "PERPETUAL_N1_W165_PREREG.md")), "prereg on disk"
print("leg2: N1_BANDS 163 rows tail W165 + WAVE_CONFIGS[165] live-import PASS")

# 3. materializer chain 138..163 (n=26)
w2 = n2.find("# --- W165 materializer face")
t3 = n2.find("# --- T-141 s2 lane face", w2)
assert 0 < w2 < t3, "W165 mat block missing"
blk2 = n2[w2:t3]
rows = re.findall(r"assert pf\.N1_BANDS\[(\d+)\]",
                  blk2[blk2.find("assert pf.N1_BANDS[138]"):
                        blk2.find("# prior-wave disjointness")])
assert rows == [str(x) for x in range(138, 165)], rows
assert '"registered W164 row parity drift (r307; bm-a r792)"' in blk2, "W164 chain row prose"
assert "_set_wave(165)" in blk2, "W165 set_wave face"
assert "own-wave A window reserved jumps to 379_804, first-clean " in blk2, \
    "W165 jump-fragment face (@JB@ lineage migrated)"
assert "own-wave A window reserved jumps to 377_604, first-clean" not in blk2, \
    "vmap-leak residue in new block"
# the @ABASE@ face fired twice in the mat block (band-facts comment +
# assert prose), both landing on the prior-B-tail+1 value 377_803+1
assert '"W164 B band tail 377_803+1 (arithmetic continuation "' in blk2, \
    "mat A-base assert prose"
assert "B band tail 375_403+1" not in blk2 and "B band tail 375_603+1" not in blk2, \
    "stale mat A-base prose residue"
# N3-R1 ruling constant (MSG-183x) protected; seat tail shifted
assert "used-seed band 70_000..70_005 (MSG-183x)" in blk2, "N3-R1 ruling constant damaged"
assert "seat MSG-205x tail" in blk2, "seat-tail shift missing"
print("leg3: W165 materializer chain 138..163 n=26 + healed-fragment + @ABASE@ double-face PASS")

# 4. full-file malformed-window scans (r773 pit law leg 3)
for path, txt in ((PF, pf2), (N1, n2)):
    bad = [m.group() for m in re.finditer(r"(\d{3})_(\d{3})\.\.(\d{3})_(\d{3})", txt)
           if int(m.group(3)) < int(m.group(1))]
    assert not bad, f"malformed windows in {path}: {bad[:4]}"
    assert "364_404..364_203" not in txt and "364_604..362_603" not in txt, \
        f"r772 residue in {path}"
print("leg4: malformed-window scans CLEAN on both files")

# 5. W166+ projection prose == gate leg3 verbatim
assert f"# {W166p_A} CLEAN hops=0 / B first-clean {W166p_B}" in pf2, "pf W166p prose"
assert "W166 A window; W166 freezer MUST re-derive on the post-W165" in pf2, "pf freezer prose"
# r776 fragment-needle law: within-fragment shapes only
assert '"W166 A window; W166 freezer MUST re-derive on the "' in n2, "n1 freezer fragment"
assert '"W165 B band 379_804..380_003 will refuse the naive "' in n2, "n1 refuse fragment"
assert f"A first-clean {W166p_A} " in n2 and f"B first-clean {W166p_B} CLEAN" in n2, "n1 W166p prose"
print("leg5: W166+ projection prose == r793 gate leg3 verbatim PASS")

# 6. honesty faces
assert "move deferred to the W166 finalize window (W165 seat still in" in pf2, "pf self-ack frag1"
assert "fleet/inbox at freeze time -- honest state);" in pf2, "pf self-ack frag2"
assert "move deferred to the W166 finalize window (W165 seat still in" in n2, "mat self-ack frag1"
assert "fleet/inbox at freeze time -- honest state)." in n2, "mat self-ack frag2"
assert "payload = seat MSG + pre-seat probe + probe receipt;" in pf2, "pf 3-item payload face"
assert '"seat MSG + pre-seat probe + probe receipt; "' in n2, "entry 3-item payload face"
assert "= seat MSG + pre-seat probe + probe receipt;" in n2, "mat 3-item payload face"
assert "r793 pre-seat" in pf2 and "r793 pre-seat" in n2, "push session"
assert "direct fast-forward behind-0" in pf2 and "direct fast-forward behind-0" in n2, \
    "direct-FF delivery face"
assert '"number law after the REGISTERED W164 row bm-a r792 freeze "' in n2, "W164-row cite frag1"
assert '"f7d34e5a7, SINGLE STATE zero seat gap W2..W164 all "' in n2, "W164-row cite frag2"
assert '"finalize one-pass bm-a r793, net chain head 766,212, "' in n2, "entry-tail frag"
assert n2.count("W164 finalize one-pass bm-a r793") == 1, "W164 finalize one-pass count"
assert "W164 bm-a r793 one-pass" in n2, "COP face"
assert "bm-a r792 freeze f7d34e5a7" in n2, "mat header registered-row citation (anti-drift)"
assert "18231a529" not in blk2, "stale W163 sha residue in new block"
assert "766,212" in n2 and "358,720" in n2, "ledger/K faces"
# the W164 entry's own frozen face stays untouched (git history face)
i163 = n2.find('164: {"batch"')
seg163 = n2[i163:n2.find('"engine_owner": "bm-a"},', i163)]
assert "bm-a r789 freeze" in seg163 and "18231a529" in seg163, \
    "W164 entry frozen face must stay untouched (r307 two-state law)"
print("leg6: honesty faces PASS (self-ack deferred to W166 / 3-item payload / direct-FF / anti-drift registered-row / W164 entry frozen intact)")

# 7. stale-scan in the NEW W165 blocks only (frozen faces keep their history)
EO = '"engine_owner": "bm-a"},'
i2 = pf2.find("    # W165 (bm-a r795 freeze")
j2 = pf2.find(EO, i2) + len(EO)
newpfblk = pf2[i2:j2]
k2 = n2.find('165: {"batch"')
m2 = n2.find(EO, k2) + len(EO)
newentry = n2[k2:m2]
cs2 = n2.find('"+ W165 materializer face')
ce2 = n2.find('"r795 bm-a] "', cs2) + len('"r795 bm-a] "')
newclaim = n2[cs2:ce2]
assert i2 > 0 and k2 > 0 and cs2 > 0, "new W165 block anchors missing"
# the mat CHAIN rows (138..163 parity asserts) are verbatim prior-wave
# pinned constants (r307) -- historical band values there are legitimate;
# scan only the freshly vmap'd pre (header) + post (band-facts) faces
ci2 = blk2.find("assert pf.N1_BANDS[138]")
cj2 = blk2.find("# prior-wave disjointness")
mat_new_faces = blk2[:ci2] + blk2[cj2:]
for tag, seg in (("pf", newpfblk), ("entry", newentry), ("mat", mat_new_faces),
                 ("claim", newclaim)):
    for stale in ("r789 gate", "r790 sec8", "r792 pre-seat", "W164 (bm-a r792",
                  "bm-a r794 freeze, seat", "MSG-2026-10-06-194x", "469d40896",
                  "bma-w164-seat", "seat MSG-194x tail", "MSG-175x", "bma-w163-seat",
                  "merge-absorb", "375_404..377_403", "375_404..375_603",
                  "375_604..377_603", "375_604..375_803", "373_204", "373_404",
                  "373_603", "373_403", "371_204", "375_203", "375_403", "375_404",
                  "375_604", "375_803", "377_403", "764,012", "356,520", "761,812",
                  "354,320", "ee04482a2", "678a07d4f", "6957f509e", "18231a529",
                  "1d43d7906", "bm-b r779", "a2d002357", "twentieth",
                  "twenty-first", "twenty-third", "seventy-seventh",
                  "seventy-eighth", "seventy-ninth",
                  "ONE HUNDRED-AND-FIFTY-THIRD", "ONE HUNDRED-AND-FIFTY-FOURTH",
                  "engine_owner rows 151", "engine_owner rows 153",
                  "rows 78 + candidate", "rows 79 + candidate", "facts helper",
                  "arc generator", "164: {", "r785 gate", "r786 sec8"):
        assert stale not in seg, f"stale {stale!r} residue in new W165 {tag} block"
print("leg7: new-block stale scans CLEAN (pf/entry/mat/claim)")

# 8. seat + prereg artifacts on origin/disk (W165 seat still in fleet/inbox
# at freeze time -- honest deferred state; self-ack lands at the W165
# finalize window or earlier via the observer lane)
assert os.path.exists("fleet/inbox/MSG-2026-10-06-205x-bma-w165-seat.md") or \
    os.path.exists("fleet/inbox/processed/MSG-2026-10-06-205x-bma-w165-seat.md"), "seat file"
r = __import__("subprocess").run(["git", "ls-tree", "--name-only", "-r", "origin/main",
                                  "--", "fleet/inbox/", "fleet/inbox/processed/"],
                                 capture_output=True)
assert b"fleet/inbox/MSG-2026-10-06-205x-bma-w165-seat.md" in r.stdout or \
    b"fleet/inbox/processed/MSG-2026-10-06-205x-bma-w165-seat.md" in r.stdout, \
    "seat on origin (r565 law)"
print("leg8: seat published on origin + prereg on disk PASS")

print("W165 FREEZE VERIFY SUITE rc0 ALL PASS")
