# -*- coding: utf-8 -*-
"""r805 bm-a W167 freeze post-edit verify suite (r781 law: edit-write and
assert-suite separated -- this file is read-only verification of the
landed W167 freeze; it never edits)."""
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
gate = json.load(open("results/_r801bma_w167_band_gate.json", encoding="utf-8"))
assert gate["verdict"] == "ADMIT" and gate["bands"] == {"A": "382204_384203", "B": "384204_384403"}, gate
leg3 = gate["legs"]["leg3"]
W168p_A, W168p_B = "384_204..386_203", "384_404..384_603"
assert leg3["W168p_A"] == "384204..386203" and leg3["W168p_B"] == "384404..384603", leg3
probe = json.load(open("results/_r801bma_w167_probe_receipt.json", encoding="utf-8"))
assert probe["verdict"] == "ADMIT" and probe["legs"]["leg1"]["A"] == [382204, 384203], probe
assert gate["legs"]["leg0b"]["own_seat_on_origin"] is True, "seat leg0b"
assert gate["legs"]["leg0"]["ordinal"] == 157 and gate["legs"]["leg0"]["bma_ordinal"] == 83, "ordinal drift"
w166res = json.load(open("results/perpetual_faces/n1_w166_results.json", encoding="utf-8"))
assert w166res["null_pool_cumulative"]["merged"]["n_values"] == 363120, "W166 K anchor"
print("leg1: gate/probe receipts ADMIT re-read PASS (157th wave, bm-a 83rd; W166 K=363,120 anchor)")

# 2. live registry faces
sys.path.insert(0, ".")
sys.path.insert(0, "scripts")
import importlib
import perpetual_faces as pf
importlib.reload(pf)
assert sorted(pf.N1_BANDS)[-1] == 167 and len(pf.N1_BANDS) == 165, "row count drift"
assert pf.N1_BANDS[167] == {"a": (382_204, 384_203), "b_exit": (384_204, 384_403),
                            "engine_owner": "bm-a"}, "W167 row drift"
assert pf.N1_BANDS[166] == {"a": (380_004, 382_003), "b_exit": (382_004, 382_203),
                            "engine_owner": "bm-a"}, "W166 row survived"
assert pf.N1_BANDS[165] == {"a": (377_804, 379_803), "b_exit": (379_804, 380_003),
                            "engine_owner": "bm-a"}, "W165 row survived"
import perpetual_faces_n1 as n1mod
importlib.reload(n1mod)
cfg = n1mod.WAVE_CONFIGS[167]
assert cfg["a_seed_base"] == 382_204 and cfg["b_exit_seed_base"] == 384_204, "seed bases"
assert cfg["shard_subdir"] == "n1_w167" and cfg["out_name"] == "n1_w167_results.json", "paths"
assert cfg["prereg"].startswith("research/PERPETUAL_N1_W167_PREREG.md"), "prereg citation"
assert cfg.get("engine_owner") == "bm-a", "engine_owner"
assert os.path.exists(os.path.join("research", "PERPETUAL_N1_W167_PREREG.md")), "prereg on disk"
print("leg2: N1_BANDS 165 rows tail W167 + WAVE_CONFIGS[167] live-import PASS")

# 3. materializer chain 138..166 (n=29)
w2 = n2.find("# --- W167 materializer face")
t3 = n2.find("# --- T-141 s2 lane face", w2)
assert 0 < w2 < t3, "W167 mat block missing"
blk2 = n2[w2:t3]
rows = re.findall(r"assert pf\.N1_BANDS\[(\d+)\]",
                  blk2[blk2.find("assert pf.N1_BANDS[138]"):
                        blk2.find("# prior-wave disjointness")])
assert rows == [str(x) for x in range(138, 167)], rows
assert '"registered W166 row parity drift (r307; bm-a r799)"' in blk2, "W166 chain row prose"
assert "_set_wave(167)" in blk2, "W167 set_wave face"
assert "own-wave A window reserved jumps to 384_204, first-clean " in blk2, \
    "W167 jump-fragment face (@JB@ lineage migrated)"
assert "own-wave A window reserved jumps to 382_004, first-clean" not in blk2, \
    "vmap-leak residue in new block"
# the @ABASE@ face (band-facts comment + assert prose) lands on the prior-B-tail+1 value 382_203+1
assert '"W166 B band tail 382_203+1 (arithmetic continuation "' in blk2, \
    "mat A-base assert prose"
assert "B band tail 380_003+1" not in blk2 and "B band tail 382_003+1" not in blk2, \
    "stale mat A-base prose residue"
# N3-R1 ruling constant (MSG-183x) protected; seat tail shifted
assert "used-seed band 70_000..70_005 (MSG-183x)" in blk2, "N3-R1 ruling constant damaged"
assert "seat MSG-0056 tail" in blk2, "seat-tail shift missing"
print("leg3: W167 materializer chain 138..166 n=29 + healed-fragment + @ABASE@ face PASS")

# 4. full-file malformed-window scans (r773 pit law leg 3)
for path, txt in ((PF, pf2), (N1, n2)):
    bad = [m.group() for m in re.finditer(r"(\d{3})_(\d{3})\.\.(\d{3})_(\d{3})", txt)
           if int(m.group(3)) < int(m.group(1))]
    assert not bad, f"malformed windows in {path}: {bad[:4]}"
    assert "364_404..364_203" not in txt and "364_604..362_603" not in txt, \
        f"r772 residue in {path}"
print("leg4: malformed-window scans CLEAN on both files")

# 5. W168+ projection prose == gate leg3 verbatim
assert f"# {W168p_A} CLEAN hops=0 / B first-clean {W168p_B}" in pf2, "pf W168p prose"
assert "W168 A window; W168 freezer MUST re-derive on the post-W167" in pf2, "pf freezer prose"
# r776 fragment-needle law: within-fragment shapes only
assert '"W168 A window; W168 freezer MUST re-derive on the "' in n2, "n1 freezer fragment"
assert '"W167 B band 384_204..384_403 will refuse the naive "' in n2, "n1 refuse fragment"
assert f"A first-clean {W168p_A} " in n2 and f"B first-clean {W168p_B} CLEAN" in n2, "n1 W168p prose"
print("leg5: W168+ projection prose == r801 gate leg3 verbatim PASS")

# 6. honesty faces
assert "move deferred to the W168 finalize window (W167 seat still in" in pf2, "pf self-ack frag1"
assert "fleet/inbox at freeze time -- honest state);" in pf2, "pf self-ack frag2"
assert "move deferred to the W168 finalize window (W167 seat still in" in n2, "mat self-ack frag1"
assert "fleet/inbox at freeze time -- honest state)." in n2, "mat self-ack frag2"
assert "payload = seat MSG + pre-seat probe + probe receipt;" in pf2, "pf 3-item payload face"
assert '"seat MSG + pre-seat probe + probe receipt; "' in n2, "entry 3-item payload face"
assert "= seat MSG + pre-seat probe + probe receipt;" in n2, "mat 3-item payload face"
assert "r801 pre-seat" in pf2 and "r801 pre-seat" in n2, "push session"
assert "direct fast-forward behind-0" in pf2 and "direct fast-forward behind-0" in n2, \
    "direct-FF delivery face"
assert '"number law after the REGISTERED W166 row bm-a r799 freeze "' in n2, "W166-row cite frag1"
assert '"c2d6c5e14, SINGLE STATE zero seat gap W2..W166 all "' in n2, "W166-row cite frag2"
assert '"finalize one-pass bm-a r799, net chain head 770,612, "' in n2, "entry-tail frag"
assert n2.count("finalize one-pass bm-a r799") == 2, "W166 finalize one-pass count"
assert "W166 bm-a r799 one-pass" in n2, "COP face"
assert "bm-a r799 freeze c2d6c5e14" in n2, "mat header registered-row citation (anti-drift)"
assert "aebb94d2d" not in blk2, "stale W165 sha residue in new block"
assert "770,612" in n2 and "363,120" in n2, "ledger/K faces"
# the W166 entry's own frozen face stays untouched (git history face);
# the W166 entry cites the W165 registered row (bm-a r795 freeze aebb94d2d)
i166 = n2.find('166: {"batch"')
seg166 = n2[i166:n2.find('"engine_owner": "bm-a"},', i166)]
assert "bm-a r795 freeze" in seg166 and "aebb94d2d" in seg166, \
    "W166 entry frozen face must stay untouched (r307 two-state law)"
# the @CLMS@ face: the NEW W167 claim carries the corrected r805 attribution;
# the frozen W166 claim keeps its historical (stale r795) tail per r307
cs3 = n2.find('"+ W167 materializer face')
ce3 = n2.find('"r805 bm-a] "', cs3) + len('"r805 bm-a] "')
newclaim_txt = n2[cs3:ce3]
assert newclaim_txt.endswith('"r805 bm-a] "'), "W167 claim attribution"
assert "r795 bm-a] " not in newclaim_txt, "stale claim tail leaked into W167 claim"
print("leg6: honesty faces PASS (self-ack deferred to W168 / 3-item payload / direct-FF / anti-drift registered-row / W166 entry frozen intact / @CLMS@ attribution)")

# 7. stale-scan in the NEW W167 blocks only (frozen faces keep their history)
EO = '"engine_owner": "bm-a"},'
i2 = pf2.find("    # W167 (bm-a r805 freeze")
j2 = pf2.find(EO, i2) + len(EO)
newpfblk = pf2[i2:j2]
k2 = n2.find('167: {"batch"')
m2 = n2.find(EO, k2) + len(EO)
newentry = n2[k2:m2]
cs2 = n2.find('"+ W167 materializer face')
ce2 = n2.find('"r805 bm-a] "', cs2) + len('"r805 bm-a] "')
newclaim = n2[cs2:ce2]
assert i2 > 0 and k2 > 0 and cs2 > 0, "new W167 block anchors missing"
# the mat CHAIN rows (138..166 parity asserts) are verbatim prior-wave
# pinned constants (r307) -- historical band values there are legitimate;
# scan only the freshly vmap'd pre (header) + post (band-facts) faces
ci2 = blk2.find("assert pf.N1_BANDS[138]")
cj2 = blk2.find("# prior-wave disjointness")
mat_new_faces = blk2[:ci2] + blk2[cj2:]
for tag, seg in (("pf", newpfblk), ("entry", newentry), ("mat", mat_new_faces),
                 ("claim", newclaim)):
    for stale in ("r793 gate", "r796 sec8", "r797 pre-seat", "W166 (bm-a r799",
                  "bm-a r795 freeze", "r795 bm-a freeze", "MSG-2026-10-06-223x", "d1dc12117",
                  "bma-w166-seat", "seat MSG-223x tail", "MSG-223x", "bma-w165-seat",
                  "merge-absorb", "379_804", "380_004", "380_003", "380_203",
                  "381_803", "382_003", "768,412", "360,920", "aebb94d2d",
                  "f7d34e5a7", "18231a529", "764cd882a", "678a07d4f", "6957f509e",
                  "6ee1207bb", "ee04482a2", "twenty-fourth", "twenty-fifth",
                  "seventy-ninth", "eightieth", "eighty-first",
                  "ONE HUNDRED-AND-FIFTY-FIFTH", "ONE HUNDRED-AND-FIFTY-SIXTH",
                  "engine_owner rows 154", "engine_owner rows 155",
                  "rows 80 + candidate", "rows 81 + candidate", "facts helper",
                  "arc generator", "r789 gate", "r790 sec8", "r785 gate", "r786 sec8"):
        assert stale not in seg, f"stale {stale!r} residue in new W167 {tag} block"
print("leg7: new-block stale scans CLEAN (pf/entry/mat/claim)")

# 8. seat + prereg artifacts on origin/disk (W167 seat still in fleet/inbox
# at freeze time -- honest deferred state; self-ack lands at the W167
# finalize window or earlier via the observer lane)
assert os.path.exists("fleet/inbox/MSG-2026-10-07-0056-bma-w167-seat.md") or \
    os.path.exists("fleet/inbox/processed/MSG-2026-10-07-0056-bma-w167-seat.md"), "seat file"
r = __import__("subprocess").run(["git", "ls-tree", "--name-only", "-r", "origin/main",
                                  "--", "fleet/inbox/", "fleet/inbox/processed/"],
                                 capture_output=True)
assert b"fleet/inbox/MSG-2026-10-07-0056-bma-w167-seat.md" in r.stdout or \
    b"fleet/inbox/processed/MSG-2026-10-07-0056-bma-w167-seat.md" in r.stdout, \
    "seat on origin (r565 law)"
print("leg8: seat published on origin + prereg on disk PASS")

print("W167 FREEZE VERIFY SUITE rc0 ALL PASS")
