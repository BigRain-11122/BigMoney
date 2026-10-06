# -*- coding: utf-8 -*-
"""r809 bm-a W168 freeze post-edit verify suite (r781 law: edit-write and
assert-suite separated -- this file is read-only verification of the
landed W168 freeze; it never edits)."""
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
gate = json.load(open("results/_r806bma_w168_band_gate.json", encoding="utf-8"))
assert gate["verdict"] == "ADMIT" and gate["bands"] == {"A": "384404_386403", "B": "386404_386603"}, gate
leg3 = gate["legs"]["leg3"]
W169p_A, W169p_B = "386_404..388_403", "386_604..386_803"
assert leg3["W169p_A"] == "386404..388403" and leg3["W169p_B"] == "386604..386803", leg3
probe = json.load(open("results/_r806bma_w168_probe_receipt.json", encoding="utf-8"))
assert probe["verdict"] == "ADMIT" and probe["legs"]["leg1"]["A"] == [384404, 386403], probe
assert gate["legs"]["leg0b"]["own_seat_on_origin"] is True, "seat leg0b"
assert gate["legs"]["leg0"]["ordinal"] == 158 and gate["legs"]["leg0"]["bma_ordinal"] == 84, "ordinal drift"
w167res = json.load(open("results/perpetual_faces/n1_w167_results.json", encoding="utf-8"))
assert w167res["null_pool_cumulative"]["merged"]["n_values"] == 365320, "W167 K anchor"
print("leg1: gate/probe receipts ADMIT re-read PASS (158th wave, bm-a 84th; W167 K=365,320 anchor)")

# 2. live registry faces
sys.path.insert(0, ".")
sys.path.insert(0, "scripts")
import importlib
import perpetual_faces as pf
importlib.reload(pf)
assert sorted(pf.N1_BANDS)[-1] == 168 and len(pf.N1_BANDS) == 166, "row count drift"
assert pf.N1_BANDS[168] == {"a": (384_404, 386_403), "b_exit": (386_404, 386_603),
                            "engine_owner": "bm-a"}, "W168 row drift"
assert pf.N1_BANDS[167] == {"a": (382_204, 384_203), "b_exit": (384_204, 384_403),
                            "engine_owner": "bm-a"}, "W167 row survived"
assert pf.N1_BANDS[166] == {"a": (380_004, 382_003), "b_exit": (382_004, 382_203),
                            "engine_owner": "bm-a"}, "W166 row survived"
import perpetual_faces_n1 as n1mod
importlib.reload(n1mod)
cfg = n1mod.WAVE_CONFIGS[168]
assert cfg["a_seed_base"] == 384_404 and cfg["b_exit_seed_base"] == 386_404, "seed bases"
assert cfg["shard_subdir"] == "n1_w168" and cfg["out_name"] == "n1_w168_results.json", "paths"
assert cfg["prereg"].startswith("research/PERPETUAL_N1_W168_PREREG.md"), "prereg citation"
assert cfg.get("engine_owner") == "bm-a", "engine_owner"
assert os.path.exists(os.path.join("research", "PERPETUAL_N1_W168_PREREG.md")), "prereg on disk"
print("leg2: N1_BANDS 166 rows tail W168 + WAVE_CONFIGS[168] live-import PASS")

# 3. materializer chain 138..167 (n=30)
w2 = n2.find("# --- W168 materializer face")
t3 = n2.find("# --- T-141 s2 lane face", w2)
assert 0 < w2 < t3, "W168 mat block missing"
blk2 = n2[w2:t3]
rows = re.findall(r"assert pf\.N1_BANDS\[(\d+)\]",
                  blk2[blk2.find("assert pf.N1_BANDS[138]"):
                        blk2.find("# prior-wave disjointness")])
assert rows == [str(x) for x in range(138, 168)], rows
assert '"registered W167 row parity drift (r307; bm-a r805)"' in blk2, "W167 chain row prose"
assert "_set_wave(168)" in blk2, "W168 set_wave face"
assert "own-wave A window reserved jumps to 386_404, first-clean " in blk2, \
    "W168 jump-fragment face (@JB@ lineage migrated)"
assert "own-wave A window reserved jumps to 384_204, first-clean" not in blk2, \
    "vmap-leak residue in new block"
# the @ABASE@ face (band-facts comment + assert prose) lands on the prior-B-tail+1 value 384_403+1
assert '"W167 B band tail 384_403+1 (arithmetic continuation "' in blk2, \
    "mat A-base assert prose"
assert "B band tail 382_203+1" not in blk2 and "B band tail 384_203+1" not in blk2, \
    "stale mat A-base prose residue"
# N3-R1 ruling constant (MSG-183x) protected; seat tail shifted
assert "used-seed band 70_000..70_005 (MSG-183x)" in blk2, "N3-R1 ruling constant damaged"
assert "seat MSG-0259 tail" in blk2, "seat-tail shift missing"
print("leg3: W168 materializer chain 138..167 n=30 + healed-fragment + @ABASE@ face PASS")

# 4. full-file malformed-window scans (r773 pit law leg 3)
for path, txt in ((PF, pf2), (N1, n2)):
    bad = [m.group() for m in re.finditer(r"(\d{3})_(\d{3})\.\.(\d{3})_(\d{3})", txt)
           if int(m.group(3)) < int(m.group(1))]
    assert not bad, f"malformed windows in {path}: {bad[:4]}"
    assert "364_404..364_203" not in txt and "364_604..362_603" not in txt, \
        f"r772 residue in {path}"
    assert "362_204..362_003" not in txt and "362_404..360_403" not in txt, \
        f"r772 malformed-window residue in {path}"
print("leg4: malformed-window scans CLEAN on both files")

# 5. W169+ projection prose == gate leg3 verbatim
assert f"# {W169p_A} CLEAN hops=0 / B first-clean {W169p_B}" in pf2, "pf W169p prose"
assert "W169 A window; W169 freezer MUST re-derive on the post-W168" in pf2, "pf freezer prose"
# r776 fragment-needle law: within-fragment shapes only
assert '"W169 A window; W169 freezer MUST re-derive on the "' in n2, "n1 freezer fragment"
assert '"W168 B band 386_404..386_603 will refuse the naive "' in n2, "n1 refuse fragment"
assert f"A first-clean {W169p_A} " in n2 and f"B first-clean {W169p_B} CLEAN" in n2, "n1 W169p prose"
print("leg5: W169+ projection prose == r806 gate leg3 verbatim PASS")

# 6. honesty faces
assert "move already landed pre-freeze (bm-c r650 consumed-archived the" in pf2, "pf self-ack frag1"
assert "fleet/inbox/processed at 03:27:53 -- honest state);" in pf2, "pf self-ack frag2"
assert "move already landed pre-freeze (bm-c r650 consumed-archived the" in n2, "mat self-ack frag1"
assert "fleet/inbox/processed at 03:27:53 -- honest state)." in n2, "mat self-ack frag2"
assert "move deferred to the W169 finalize window" not in pf2 and \
    "move deferred to the W169 finalize window" not in n2, "stale deferred prose leaked into W168 faces"
assert "payload = seat MSG + pre-seat probe + probe receipt;" in pf2, "pf 3-item payload face"
assert '"seat MSG + pre-seat probe + probe receipt; "' in n2, "entry 3-item payload face"
assert "= seat MSG + pre-seat probe + probe receipt;" in n2, "mat 3-item payload face"
assert "r806 pre-seat" in pf2 and "r806 pre-seat" in n2, "push session"
assert "direct fast-forward behind-0" in pf2 and "direct fast-forward behind-0" in n2, \
    "direct-FF delivery face"
assert '"number law after the REGISTERED W167 row bm-a r805 freeze "' in n2, "W167-row cite frag1"
assert '"f61835690, SINGLE STATE zero seat gap W2..W167 all "' in n2, "W167-row cite frag2"
assert '"finalize one-pass bm-a r806, net chain head 772,812, "' in n2, "entry-tail frag"
assert n2.count("finalize one-pass bm-a r806") == 2, "W167 finalize one-pass count"
assert "W167 bm-a r806 one-pass" in n2, "COP face"
assert "bm-a r805 freeze f61835690" in n2, "mat header registered-row citation (anti-drift)"
assert "c2d6c5e14" not in blk2, "stale W166 sha residue in new block"
assert "772,812" in n2 and "365,320" in n2, "ledger/K faces"
# the W167 entry's own frozen face stays untouched (git history face);
# the W167 entry cites the W166 registered row (bm-a r799 freeze c2d6c5e14)
i167 = n2.find('167: {"batch"')
seg167 = n2[i167:n2.find('"engine_owner": "bm-a"},', i167)]
assert "bm-a r799 freeze" in seg167 and "c2d6c5e14" in seg167, \
    "W167 entry frozen face must stay untouched (r307 two-state law)"
# the @CLMS@ face: the NEW W168 claim carries the rolled r809 attribution;
# the frozen W167 claim keeps its correct r805 tail (healed lineage, r307)
cs3 = n2.find('"+ W168 materializer face')
ce3 = n2.find('"r809 bm-a] "', cs3) + len('"r809 bm-a] "')
newclaim_txt = n2[cs3:ce3]
assert newclaim_txt.endswith('"r809 bm-a] "'), "W168 claim attribution"
assert "r805 bm-a] " not in newclaim_txt, "stale claim tail leaked into W168 claim"
cs4 = n2.find('"+ W167 materializer face')
assert 0 < cs4 < cs3, "W167 frozen claim still precedes W168 claim"
frozen167 = n2[cs4:n2.find('"r805 bm-a] "', cs4) + len('"r805 bm-a] "')]
assert frozen167.endswith('"r805 bm-a] "'), "W167 frozen claim tail intact (r307)"
print("leg6: honesty faces PASS (self-ack already-landed TRUTH / 3-item payload / direct-FF / anti-drift registered-row / W167 entry frozen intact / @CLMS@ r809 attribution)")

# 7. stale-scan in the NEW W168 blocks only (frozen faces keep their history)
EO = '"engine_owner": "bm-a"},'
i2 = pf2.find("    # W168 (bm-a r809 freeze")
j2 = pf2.find(EO, i2) + len(EO)
newpfblk = pf2[i2:j2]
k2 = n2.find('168: {"batch"')
m2 = n2.find(EO, k2) + len(EO)
newentry = n2[k2:m2]
cs2 = n2.find('"+ W168 materializer face')
ce2 = n2.find('"r809 bm-a] "', cs2) + len('"r809 bm-a] "')
newclaim = n2[cs2:ce2]
assert i2 > 0 and k2 > 0 and cs2 > 0, "new W168 block anchors missing"
# the mat CHAIN rows (138..167 parity asserts) are verbatim prior-wave
# pinned constants (r307) -- historical band values there are legitimate;
# scan only the freshly vmap'd pre (header) + post (band-facts) faces
ci2 = blk2.find("assert pf.N1_BANDS[138]")
cj2 = blk2.find("# prior-wave disjointness")
mat_new_faces = blk2[:ci2] + blk2[cj2:]
for tag, seg in (("pf", newpfblk), ("entry", newentry), ("mat", mat_new_faces),
                 ("claim", newclaim)):
    for stale in ("r793 gate", "r796 sec8", "r797 gate", "r799 sec8",
                  "r797 pre-seat", "r801 pre-seat", "W166 (bm-a r799",
                  "W167 (bm-a r805", "bm-a r795 freeze", "r795 bm-a freeze",
                  "bm-a r799 freeze", "r799 bm-a freeze",
                  "MSG-2026-10-06-223x", "MSG-2026-10-07-0056", "982424c5f",
                  "d1dc12117", "bma-w166-seat", "bma-w167-seat", "MSG-223x",
                  "MSG-0056", "seat MSG-0056 tail", "merge-absorb",
                  "gate-derived r797", "gate-derived r801",
                  "move deferred to the W169",
                  "379_804", "380_004", "380_003", "380_203", "381_803",
                  "382_003", "382_004", "382_203", "382_204", "382_403",
                  "384_003", "384_203", "768,412", "360,920", "770,612",
                  "363,120", "aebb94d2d", "c2d6c5e14", "f7d34e5a7",
                  "18231a529", "764cd882a", "678a07d4f", "6957f509e",
                  "6ee1207bb", "ee04482a2", "twenty-fourth", "twenty-fifth",
                  "twenty-sixth", "seventy-ninth", "eightieth", "eighty-first",
                  "eighty-second", "ONE HUNDRED-AND-FIFTY-FIFTH",
                  "ONE HUNDRED-AND-FIFTY-SIXTH", "ONE HUNDRED-AND-FIFTY-SEVENTH",
                  "engine_owner rows 154", "engine_owner rows 155",
                  "engine_owner rows 156", "rows 80 + candidate",
                  "rows 81 + candidate", "rows 82 + candidate", "facts helper",
                  "arc generator", "r789 gate", "r790 sec8", "r785 gate",
                  "r786 sec8", "n1w165", "n1_w165", "n1w166", "n1_w166",
                  "n1w167", "n1_w167", "PERPETUAL-N1-W165", "PERPETUAL_N1_W165",
                  "PERPETUAL-N1-W166", "PERPETUAL_N1_W166",
                  "PERPETUAL-N1-W167", "PERPETUAL_N1_W167"):
        assert stale not in seg, f"stale {stale!r} residue in new W168 {tag} block"
print("leg7: new-block stale scans CLEAN (pf/entry/mat/claim)")

# 8. seat + prereg artifacts on origin/disk (W168 seat consumed-archived to
# fleet/inbox/processed by bm-c r650 at 03:27:53 BEFORE this freeze window --
# honest already-landed state disclosed in the faces)
assert os.path.exists("fleet/inbox/MSG-2026-10-07-0259-bma-w168-seat.md") or \
    os.path.exists("fleet/inbox/processed/MSG-2026-10-07-0259-bma-w168-seat.md"), "seat file"
r = __import__("subprocess").run(["git", "ls-tree", "--name-only", "-r", "origin/main",
                                  "--", "fleet/inbox/", "fleet/inbox/processed/"],
                                 capture_output=True)
assert b"fleet/inbox/MSG-2026-10-07-0259-bma-w168-seat.md" in r.stdout or \
    b"fleet/inbox/processed/MSG-2026-10-07-0259-bma-w168-seat.md" in r.stdout, \
    "seat on origin (r565 law)"
print("leg8: seat published on origin + prereg on disk PASS")

print("W168 FREEZE VERIFY SUITE rc0 ALL PASS")
