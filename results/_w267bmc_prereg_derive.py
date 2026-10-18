# -*- coding: utf-8 -*-
# r1087 bm-c: W267 prereg derive (count-asserted ordered transform + marker-extracted block replaces).
# Canon-clone of _w266bmc_prereg_derive.py per age() machine-needle law (shift-map one generation).
# Source = committed frozen W266 prereg AT THE FREEZE COMMIT 595433d63c (git 595433d63c:research/PERPETUAL_N1_W266_PREREG.md,
# 22,970 bytes -- the frozen pre-run face; sec7/8 placeholders intact). Extracted to
# results/_w267bmc_w266_frozen_face.txt THIS window (r1087); byte-verified:
# disk==blob sha1 417bc0b887c53d38c55abbb4c7f1777ea65d22e2, sha256_16 a273485226cbeefa.
# TEMPLATE-FACE DISCLOSURE (r1052/r1049 law): HEAD twin a9b453235f0b50afe3605b6f9d9e16bc06b5edc5 = the
# CURRENT HEAD face = the POST-CYCLE face with sec.7/8 BACKFILLED by the r1086 W266 cycle (fivekeys+backfill
# closeout 5f6c14efd4). Deriving from the backfilled face would fabricate W267 sec.7/8 from W266's measured
# numbers -- the r1049/r1052 precedent requires the 595433d63c frozen pre-run face.
# W267 facts (all machine-derived, never transcribed):
#   - seat probe ADMIT receipt results/_w267bmc_20261018_probe_receipt.json (bm-c r1086-continuation
#     window authored+run live, seat rides origin 942ebd5885 per r565 early-visibility law,
#     MSG-20261018-1025-bmc-w267-seat landed; bm-a r1052 raced the same bands and YIELDED per fleet
#     README sec.4 commit-time order -- both probes live-ADMIT identical bands, zero fact divergence).
#     STAIRCASE CONTINUES: A naive 602_501..604_500 REFUSED at start (registered W266 B band
#     602_501..602_700 sits INSIDE the naive A window) -> A first-clean 602_701..604_700 hops=1
#     (SIXTEENTH consecutive A-hop, W266 prereg sec.5 item5 post-W266-REGISTERED pre-disclosure
#     confirmed live per r587, ZERO divergence) / B naive 602_701..602_900 REFUSED at start (lands
#     INSIDE the own-wave W267 A first-clean window 602_701..604_700) -> own-A reservation cascade
#     hop past 604_700 -> 604_701..604_900 hops=1 (SEVENTEENTH consecutive above-own-A landing);
#     seed_admit FREE x2 (A base=602701 span=2000 / B base=604701 span=200); leg0 rows=264
#     owner_rows=256 bmc_rows=85 ordinal=257; leg2 conflicts=0; leg3 origin_vacancy=true.
#   - upstream W266 finalize LANDED (bm-c r1086 window one-pass, n1_w266_results.json landed via
#     007ec5e713 10:21:39, fivekeys 6/6 receipt results/_r1086bmc_w266_fivekeys.json + sec.7/8
#     backfilled 5f6c14efd4): merged K=583,120 / ledger 1,009,535 EXACT (1,007,335+2,200) / merged mu
#     -0.09273858056660722 (8dp -0.09273858) / sigma 0.24507392133976638 (8dp 0.24507392) /
#     se_mu@K583,120 0.000321 (held-flat) / W266-only mu -0.09878527272727272 (8dp -0.09878527) /
#     A p95 0.3268 / K-lift +0.0001 / n_eff_held 1,007,335 / line_pre_w266 1.1957 / line_merged@583,120
#     1.1958 / key1 gap 0.0060 in-band<0.02; splice dc71ecc3f9 10:11:41 (r1086 58th-gen absorb of the
#     dead 09:25-09:50 window estate per O-20261018-0948 root-cure diagnosis); post-splice heal
#     839bf365f7; engine self-burn 12/12 batched ledger appends bc7cab9893+18f6ffe931.
# Needle-count pre-flight evidence: results/_w267bmc_needle_probe.py + _r1087bmc_ctx_dump{,2}.py
# (measured live on T0 + block-classification THIS window; floors below match every measured count;
# r1077 measured-counts law -- all 18 raw W267 instances classified: 2 non-block leg-covered
# [skip-ahead face + sec.5.5 face] + 16 block-interior; 07:0x x4 = 2 non-block + 2 block-interior).
# Same-window needle heals disclosed:
# (1) NO date-roll heal needed this generation: the W266 seat-probe receipt and the W267 seat-probe
#     receipt are BOTH dated 20261018 (_w265bmc_20261017 count=0 in T0) -- the _w266bmc->_w267bmc
#     roll lands the correct date directly.
# (2) RAM face live-measured THIS window: psutil 4.94GB free (~5GB) + nvidia-smi 6% util / 3.4G VRAM
#     resident / ZERO active GPU burn -- r1086 face "~3GB / 3% / 3.2G" updated to the honest current.
# (3) se_mu chain true-history correction (r1059 canon-embed advice): post-roll form carries
#     W264 0.000323 (FALSE -- true W264 measured 0.000322) and a raw trailing "W266 投影" colliding
#     with the rolled W266 label -> POST_LEG rewrites the tail with true history W263 **0.000323** /
#     W264 **0.000322** / W265 **0.000321** / W266 **0.000321** (measured per fivekeys key5
#     se_mu_narrowing 0.000321) and appends the W267 projection 0.000321.
# (4) K-lift POST_LEG: post-roll form carries "键 W266 实测 K-lift **0.0000**·line_merged@K580,920
#     **1.1956**·line_pre_w265 1.1956" (lowercase line_pre_w265 NOT rolled by the W-roll --
#     case-sensitive) -- corrected to the true W266 anchors "键 W266 实测 K-lift **0.0001**·
#     line_merged@K583,120 **1.1958**·line_pre_w266 1.1957" (k_lift_delta=+0.0001 per
#     _r1086bmc_w266_fivekeys, first positive micro-move since W258).
# (5) low-RAM precedent ledger append: W266 freeze-window ~5G bm-c anchor appended via POST_LEG
#     (chain precedent every-wave append, b6_ram paradigm; the wave-roll had shifted the W263 26G
#     bm-a anchor onto the W264 label and the W264 7G onto W265 -- both restored + true W266 anchor
#     appended).
# (6) n_eff_held_equal 996,335 carried verbatim per W263/W264/W265/W266 derive precedent (static
#     precedent-chain face; the live n_eff anchors are machine-verified from receipts in the
#     gates below).
# (7) finalize-window stamp roll: W266 finalize one-pass landed 10:21:39 (n1_w266_results generated
#     @ 007ec5e713); T1 carries the W265-era 07:0x stamps x4 (two block-interior copies discarded
#     by block replacement) -> POST_LEG rolls all to 10:2x.
import io, os, sys, datetime, subprocess, hashlib, re, json

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(REPO, "results", "_w267bmc_w266_frozen_face.txt")
OUT = os.path.join(REPO, "research", "PERPETUAL_N1_W267_PREREG.md")
GIT = "C:/Program Files/Git/cmd/git.exe"

def git_out(args):
    r = subprocess.run([GIT] + args, capture_output=True, cwd=REPO)
    if r.returncode != 0:
        raise SystemExit("git fail %r: %s" % (args, r.stderr.decode("utf-8", "replace")))
    return r.stdout.decode("utf-8", "replace").strip()

# --- source byte-identity gates ---
_blob_expect = "417bc0b887c53d38c55abbb4c7f1777ea65d22e2"   # freeze-commit face @ 595433d63c
_ho = git_out(["hash-object", SRC])
assert _ho == _blob_expect, "SRC blob mismatch: got %s expect %s" % (_ho, _blob_expect)
_fc = git_out(["rev-parse", "595433d63c:research/PERPETUAL_N1_W266_PREREG.md"])
assert _fc == _blob_expect, "freeze-commit blob mismatch: %s" % _fc
_hb = git_out(["rev-parse", "HEAD:research/PERPETUAL_N1_W266_PREREG.md"])
assert _hb == "a9b453235f0b50afe3605b6f9d9e16bc06b5edc5", "HEAD tpl twin face drifted: %s" % _hb

T0 = io.open(SRC, encoding="utf-8", newline="").read()
assert len(T0.encode("utf-8")) == 22970, "SRC size drift: %d" % len(T0.encode("utf-8"))
assert hashlib.sha256(T0.encode("utf-8")).hexdigest()[:16] == "a273485226cbeefa", "SRC sha mismatch"

# --- chain-fact existence gates (zero transcription) ---
for sha in ("595433d63c", "dc71ecc3f9", "839bf365f", "007ec5e713", "942ebd5885", "bc7cab9893", "18f6ffe931"):
    git_out(["cat-file", "-e", sha + "^{commit}"])
_ci = git_out(["show", "-s", "--format=%ci", "dc71ecc3f9"])   # 2026-10-18 10:11:41 +0800
_m = re.match(r"2026-10-18 (\d{2}):(\d{2})", _ci)
assert _m, "splice commit ts unexpected: %r" % _ci
SPLICE_T = "%s:%sx" % (_m.group(1), _m.group(2)[0])           # 10:1x
_fz = git_out(["show", "-s", "--format=%ci", "007ec5e713"])    # 2026-10-18 10:21:39 +0800
assert _fz.startswith("2026-10-18 10:2"), "finalize commit ts unexpected: %r" % _fz

# --- finalize-anchor machine-verify gates (fivekeys receipt + results json, live) ---
with open(os.path.join(REPO, "results", "_r1086bmc_w266_fivekeys.json"), encoding="utf-8") as f:
    fk = json.load(f)
assert round(fk["merged"]["mu"], 8) == -0.09273858, "merged mu drift: %r" % fk["merged"]["mu"]
assert round(fk["merged"]["sigma"], 8) == 0.24507392, "sigma drift: %r" % fk["merged"]["sigma"]
assert round(fk["merged"]["se_mu_k583120"], 6) == 0.000321, "se_mu drift: %r" % fk["merged"]["se_mu_k583120"]
assert round(fk["w266_only"]["mu"], 8) == -0.09878527, "w266-only mu drift: %r" % fk["w266_only"]["mu"]
assert round(fk["a_band"]["full_sharpe_p95"], 4) == 0.3268, "p95 drift: %r" % fk["a_band"]["full_sharpe_p95"]
assert round(fk["skill_line"]["k_lift_delta"], 4) == 0.0001, "k-lift drift: %r" % fk["skill_line"]["k_lift_delta"]
assert fk["skill_line"]["n_eff_held"] == 1007335, "n_eff_held drift: %r" % fk["skill_line"]["n_eff_held"]
assert round(fk["skill_line"]["line_pre_w266"], 4) == 1.1957, "line_pre drift: %r" % fk["skill_line"]["line_pre_w266"]
assert round(fk["skill_line"]["line_merged_583120"], 4) == 1.1958, "line_merged drift: %r" % fk["skill_line"]["line_merged_583120"]
assert fk["merged"]["k"] == 583120, "K drift: %r" % fk["merged"]["k"]
assert fk["ledger_identity"]["total"] == 1009535 and fk["ledger_identity"]["exact"], "ledger identity drift"
_k1 = [c for c in fk["checks"] if c["name"] == "key1_w266_vs_merged_mu_gap"][0]
assert round(_k1["value"], 4) == 0.0060 and _k1["pass"], "key1 gap drift: %r" % _k1["value"]
assert fk["all_pass"] is True, "fivekeys not all_pass"
with open(os.path.join(REPO, "results", "perpetual_faces", "n1_w266_results.json"), encoding="utf-8") as f:
    res = json.load(f)
assert res["skill_line_v2_k_lift"]["n_eff_held_equal"] == 1007335
assert round(res["skill_line_v2_k_lift"]["line_pre_w266"], 4) == 1.1957
assert round(res["skill_line_v2_k_lift"]["line_merged_583120"], 4) == 1.1958
assert round(res["null_pool_cumulative"]["se_mu_at_k583120"], 6) == 0.000321
with open(os.path.join(REPO, "results", "perpetual_faces", "n1_w265_results.json"), encoding="utf-8") as f:
    res5 = json.load(f)
assert round(res5["null_pool_cumulative"]["se_mu_at_k580920"], 6) == 0.000321, "W265 se_mu chain verify"
with open(os.path.join(REPO, "results", "_w267bmc_20261018_probe_receipt.json"), encoding="utf-8") as f:
    pr = json.load(f)
assert pr["verdict"] == "ADMIT"
assert pr["bands"]["A"] == [602701, 604700] and pr["bands"]["B"] == [604701, 604900]
assert pr["legs"]["leg1"]["hops_A"] == 1 and pr["legs"]["leg1"]["hops_B"] == 1
assert pr["legs"]["leg0"]["owner_rows"] == 256 and pr["legs"]["leg0"]["bmc_rows"] == 85
assert pr["legs"]["leg0"]["ordinal"] == 257
assert pr["legs"]["leg0"]["w266_finalize_anchors"]["ledger_total"] == 1009535
assert pr["legs"]["leg0"]["w266_finalize_anchors"]["merged_n"] == 583120
assert round(pr["legs"]["leg0"]["w266_finalize_anchors"]["skill_line_delta_k_lift"], 4) == 0.0001
assert pr["legs"]["leg2"]["conflicts"] == 0 and pr["legs"]["leg3"]["origin_vacancy"] is True

P1, P2, P3 = "\x01W\x01", "\x01N\x01", "\x01B\x01"

VMAP = [
    # ---- explicit wave-free legs BEFORE the wave rolls (compound needles first) ----
    ("A-ext seed=600_501..602_500", "A-ext seed=602_701..604_700"),
    ("B-ext exit seed=602_501..602_700", "B-ext exit seed=604_701..604_900"),
    ("entry rng=**600_501+j**\uff08\u4e0e A[j] \u540c\u6e90\u914d\u5bf9\u8bed\u4e49\u9010\u5b57", "entry rng=**602_701+j**\uff08\u4e0e A[j] \u540c\u6e90\u914d\u5bf9\u8bed\u4e49\u9010\u5b57"),
    # seat/provenance faces (W267 seat published bm-c r1086-continuation, rides origin 942ebd5885)
    ("\u5e2d\u4f4d\u516c\u793a=MSG-20261018-0719-bmc-w266-seat \u5df2\u63a8 origin ace19ba85b r565 \u5f8b\uff08bm-c r1084 \u5e2d\u00b7queue-head seat-first lane\uff09",
     "\u5e2d\u4f4d\u516c\u793a=MSG-20261018-1025-bmc-w267-seat \u5df2\u63a8 origin 942ebd5885 r565 \u5f8b\uff08bm-c r1086 \u5e2d\u00b7queue-head seat-first lane\uff09"),
    ("\u5e2d\u4f4d\u516c\u793a MSG-20261018-0719-bmc-w266-seat \u5148\u63a8 origin ace19ba85b r565 \u5f8b",
     "\u5e2d\u4f4d\u516c\u793a MSG-20261018-1025-bmc-w267-seat \u5148\u63a8 origin 942ebd5885 r565 \u5f8b"),
    # wave-number + vacancy faces
    ("\u6ce2\u53f7 266", "\u6ce2\u53f7 267"),
    ("r1084 \u5e2d\u4f4d\u7a97\u5b9e\u8dd1\uff1aorigin inbox \u96f6 W266 \u5e2d\u4f4d\u5916\u673a\u547d\u4e2d", "r1086 \u5e2d\u4f4d\u7a97\u5b9e\u8dd1\uff1aorigin inbox \u96f6 W267 \u5e2d\u4f4d\u5916\u673a\u547d\u4e2d"),
    ("\u96f6 266 \u884c", "\u96f6 267 \u884c"),
    ("\u96f6 skip-ahead W267/W268 \u5e2d\u4f4d\u58f0\u660e", "\u96f6 skip-ahead W268/W269 \u5e2d\u4f4d\u58f0\u660e"),
    ("\u6c60\u7b2c 264 \u679a", "\u6c60\u7b2c 265 \u679a"),
    # ordinals + own-wave faces
    ("\u7b2c 256 \u6ce2", "\u7b2c 257 \u6ce2"),
    ("bm-c \u7b2c\u516b\u5341\u4e94\u679a\u81ea\u6709\u6ce2", "bm-c \u7b2c\u516b\u5341\u516d\u679a\u81ea\u6709\u6ce2"),
    ("probe leg0 bmc_rows=84 attempt-continuity face\uff08r1084 \u7a97\u7b97\u6cd5\u00b7bm-c own seat+bmc live rows 84 \u5b9e\u8bfb\uff09\u2014\u2014freeze \u65f6 live derive bmc rows 84+\u5019\u9009=\u7b2c 85 \u679a EXACT",
     "probe leg0 bmc_rows=85 attempt-continuity face\uff08r1086 \u7a97\u7b97\u6cd5\u00b7bm-c own seat+bmc live rows 85 \u5b9e\u8bfb\uff09\u2014\u2014freeze \u65f6 live derive bmc rows 85+\u5019\u9009=\u7b2c 86 \u679a EXACT"),
    ("engine_owner==bm-c 84 \u884c\u6ce8\u518c", "engine_owner==bm-c 85 \u884c\u6ce8\u518c"),
    # engine live-read faces (bm-c instance, r1087 window)
    ("saturation_engine.py status live-read r1085\uff1aburns_active=[] queue_next=[] \u5b9e\u8bfb\u00b7heartbeat \u65b0\u9c9c",
     "saturation_engine.py status live-read r1087\uff1aburns_active=[] queue_next=[] \u5b9e\u8bfb\u00b7heartbeat \u65b0\u9c9c"),
    ("\u672c\u673a bm-c \u5b9e\u4f8b\u00b7heartbeat \u65b0\u9c9c\u5b9e\u8bfb r1085 \u7a97\u00b7\u961f\u5217\u7a7a\u8f6c idle",
     "\u672c\u673a bm-c \u5b9e\u4f8b\u00b7heartbeat \u65b0\u9c9c\u5b9e\u8bfb r1087 \u7a97\u00b7\u961f\u5217\u7a7a\u8f6c idle"),
    ("\u5f15\u64ce\u5b9e\u51b5\u6ce8\u8bb0\uff08\u672c\u673a bm-c \u5b9e\u4f8b heartbeat \u65b0\u9c9c r1085 \u7a97\u5b9e\u8bfb",
     "\u5f15\u64ce\u5b9e\u51b5\u6ce8\u8bb0\uff08\u672c\u673a bm-c \u5b9e\u4f8b heartbeat \u65b0\u9c9c r1087 \u7a97\u5b9e\u8bfb"),
    # runner CLI wave
    ("--wave 266/finalize --wave 266", "--wave 267/finalize --wave 267"),
    # sec8 placeholder projection-label bump (W268+ face)
    ("\u00a75.5 W267+ \u6295\u5f71\u627f\u63a5\u673a\u8bc1", "\u00a75.5 W268+ \u6295\u5f71\u627f\u63a5\u673a\u8bc1"),
    # ---- lowercase chained rolls (result/script faces) ----
    ("n1_w266", P2), ("n1_w265", "n1_w266"), (P2, "n1_w267"),
    ("_w266bmc", P3), ("_w265bmc", "_w266bmc"), (P3, "_w267bmc"),
    # ---- wave-number roll (chained placeholders) ----
    ("W266", P1), ("W265", "W266"), ("W264", "W265"), ("W263", "W264"), ("W262", "W263"), ("W261", "W262"),
    ("W260", "W261"), ("W259", "W260"), ("W258", "W259"), ("W257", "W258"), ("W256", "W257"),
    ("W255", "W256"), ("W254", "W255"), (P1, "W267"),
]

VMAP_FLOORS = {
    # explicit legs (all measured == 1 on T0, needle probe r1087)
    "A-ext seed=600_501..602_500": 1,
    "B-ext exit seed=602_501..602_700": 1,
    "entry rng=**600_501+j**\uff08\u4e0e A[j] \u540c\u6e90\u914d\u5bf9\u8bed\u4e49\u9010\u5b57": 1,
    "\u5e2d\u4f4d\u516c\u793a=MSG-20261018-0719-bmc-w266-seat \u5df2\u63a8 origin ace19ba85b r565 \u5f8b\uff08bm-c r1084 \u5e2d\u00b7queue-head seat-first lane\uff09": 1,
    "\u5e2d\u4f4d\u516c\u793a MSG-20261018-0719-bmc-w266-seat \u5148\u63a8 origin ace19ba85b r565 \u5f8b": 1,
    "\u6ce2\u53f7 266": 1,
    "r1084 \u5e2d\u4f4d\u7a97\u5b9e\u8dd1\uff1aorigin inbox \u96f6 W266 \u5e2d\u4f4d\u5916\u673a\u547d\u4e2d": 1,
    "\u96f6 266 \u884c": 1,
    "\u96f6 skip-ahead W267/W268 \u5e2d\u4f4d\u58f0\u660e": 1,
    "\u6c60\u7b2c 264 \u679a": 1,
    "\u7b2c 256 \u6ce2": 1,
    "bm-c \u7b2c\u516b\u5341\u4e94\u679a\u81ea\u6709\u6ce2": 1,
    "probe leg0 bmc_rows=84 attempt-continuity face\uff08r1084 \u7a97\u7b97\u6cd5\u00b7bm-c own seat+bmc live rows 84 \u5b9e\u8bfb\uff09\u2014\u2014freeze \u65f6 live derive bmc rows 84+\u5019\u9009=\u7b2c 85 \u679a EXACT": 1,
    "engine_owner==bm-c 84 \u884c\u6ce8\u518c": 1,
    "saturation_engine.py status live-read r1085\uff1aburns_active=[] queue_next=[] \u5b9e\u8bfb\u00b7heartbeat \u65b0\u9c9c": 1,
    "\u672c\u673a bm-c \u5b9e\u4f8b\u00b7heartbeat \u65b0\u9c9c\u5b9e\u8bfb r1085 \u7a97\u00b7\u961f\u5217\u7a7a\u8f6c idle": 1,
    "\u5f15\u64ce\u5b9e\u51b5\u6ce8\u8bb0\uff08\u672c\u673a bm-c \u5b9e\u4f8b heartbeat \u65b0\u9c9c r1085 \u7a97\u5b9e\u8bfb": 1,
    "--wave 266/finalize --wave 266": 1,
    "\u00a75.5 W267+ \u6295\u5f71\u627f\u63a5\u673a\u8bc1": 1,
    # lowercase rolls (measured on T0)
    "n1_w266": 4, "n1_w265": 6, "_w266bmc": 4, "_w265bmc": 1,
    # wave rolls (MEASURED live on T0, results/_w267bmc_needle_probe.py r1087 window;
    # measured-counts law r1077: W263 raw 4 and W264 raw 4 this generation)
    "W266": 35, "W265": 62, "W264": 4, "W263": 4, "W262": 2, "W261": 1, "W260": 1,
    "W259": 1, "W258": 1, "W257": 1, "W256": 1, "W255": 1, "W254": 1,
    # block-marker stability floors (raw template face; ctx-dump r1087 verified span-unique x8)
    "engine_owner \u884c 255 \u6ce8\u518c\u5728\u518c\uff08\u8868\u5c3e": 1,
    "prev=**\u5c4a\u65f6\u7a7a\u7a97\u6d3b\u94fe\u5934 derive \u7981\u624b\u6284**": 1,
    "\uff08**A \u9762=STAIRCASE-AFFECTS-A": 1,
    "entry rng seed=**600_501+j**": 1,
    "exit rng=**602_501+j**": 1,
    "probe W267+ \u6295\u5f71 A naive 602_501..604_500 CLEAN hops=0": 1,
    "5. **W267+ \u6295\u5f71\uff08probe \u673a\u8bc1 leg4": 1,
    "\u672c\u4ef6=\u5e2d\u4f4d\u7a97\u540e\u9996\u7a97\u51bb\u7ed3\u4ef6\uff1b\u4e94\u9762\u51bb\u7ed3\u62fc\u63a5\u811a\u672c": 1,
    "\uff08gate0.5 \u7eff\u00b7\u7f16\u8f91\u5668 loud abort \u515c\u5e95\uff09**\u3002": 1,
    "owner per chain-order law\uff09**\u3011\u3011\uff09": 1,
    "verify at W267 prereg\uff0chop \u94fe\u9010\u8df3\u5728 probe \u56de\u6267\u3002": 1,
    "\uff08\u89c1 \u00a75 item5\uff09\u3002": 1,
    "seed_admit_gate rc0 \u53cc\u5e26 FREE": 1,
    "n_eff_held_equal 996,335": 1,
    "\u6ce8\u518c+\u70e7\u5f55+finalize \u5168\u843d\u5730": 2,
    "\uff08W265 \u6ce8\u518c+\u70e7\u5f55+finalize \u5168\u843d\u5730\uff09": 1,
    "\u5e2d\u4f4d\u65f6\u5373\u89e3\u9501": 2,
    # zero-floors (absence assertions on T0; ctx-dump2 r1087 measured all == 0)
    "waits-upstream ARMED": 0,
    "1,009,535": 0, "602_701..604_700": 0, "604_701..604_900": 0,
    "\u22120.09273858": 0, "0.24507392": 0, "\u22120.09878527": 0, "0.3268": 0,
    "10:2x": 0, "585,320": 0, "604_701..606_700": 0, "604_901..605_100": 0,
    "_w267bmc_20261018": 0, "MSG-20261018-1025": 0, "942ebd5885": 0,
    "578,720": 0, "1,005,135": 0,
}

def xf(t):
    for o, n in VMAP:
        t = t.replace(o, n)
    return t

for o, f in VMAP_FLOORS.items():
    c = T0.count(o)
    if f == 0:
        if c:
            raise SystemExit("VMAP FLOOR(0) FAIL: %r count=%d (expect 0)" % (o, c))
        continue
    if c < f:
        raise SystemExit("VMAP FLOOR FAIL: %r count=%d floor=%d" % (o, c, f))

T1 = xf(T0)

# ---------------- post-roll correction legs (needles exist only in T1 after the rolls) ----------------
VMAP_POST_LEGS = [
    # finalize-window stamp roll (heal (7)): W266 finalize one-pass landed 10:21:39; T1 carries the
    # W265-era 07:0x stamps x4 (two block-interior copies discarded by block replacement)
    ("07:0x", "10:2x", 2),
    # sec.5 item1 measured keys -> W266 actuals (n1_w266_results + fivekeys machine values)
    ("\uff08W266 \u5b9e\u6d4b\u952e **\u22120.09271568**\u00b7K=580,920 \u5408\u5e76\u6c60\u00b7W266-only \u5b9e\u6d4b **\u22120.08956582**\uff09",
     "\uff08W266 \u5b9e\u6d4b\u952e **\u22120.09273858**\u00b7K=583,120 \u5408\u5e76\u6c60\u00b7W266-only \u5b9e\u6d4b **\u22120.09878527**\uff09", 1),
    ("W2..W266 \u5171\u4e8c\u767e\u516d\u5341\u56db\u9762\u5b9e\u6d4b mu \u7a33\u5b9a\u5148\u4f8b", "W2..W266 \u5171\u4e8c\u767e\u516d\u5341\u4e94\u9762\u5b9e\u6d4b mu \u7a33\u5b9a\u5148\u4f8b", 1),
    ("W266-only vs merged \u5b9e\u5dee 0.0031 \u5728\u5e26\u5185", "W266-only vs merged \u5b9e\u5dee 0.0060 \u5728\u5e26\u5185", 1),
    # sec.5 item2 sigma key
    ("\u952e **0.24504118**=W266 \u5408\u5e76\u6c60\u5b9e\u6d4b", "\u952e **0.24507392**=W266 \u5408\u5e76\u6c60\u5b9e\u6d4b", 1),
    # sec.5 item3 p95 anchor
    ("\u4e0e W266 A \u6863 p95\uff08**0.3149** \u5b9e\u6d4b\u951a\uff09", "\u4e0e W266 A \u6863 p95\uff08**0.3268** \u5b9e\u6d4b\u951a\uff09", 1),
    # sec.5 item4 K-lift chain + line faces (heal (4): lowercase line_pre_w265 NOT rolled by the
    # W-roll; true W266 anchors K-lift +0.0001 + line_merged@583,120 1.1958 + line_pre_w266 1.1957)
    ("\u952e W266 \u5b9e\u6d4b K-lift **0.0000**\u00b7line_merged@K580,920 **1.1956**\u00b7line_pre_w265 1.1956\u00b7n_eff_held_equal 996,335",
     "\u952e W266 \u5b9e\u6d4b K-lift **0.0001**\u00b7line_merged@K583,120 **1.1958**\u00b7line_pre_w266 1.1957\u00b7n_eff_held_equal 996,335", 1),
    ("\u2192W263 **0.000323**\u2192W264 **0.000323**\u2192W265 **0.000322**\u2192W266 **0.000321**\u2192W267 \u6295\u5f71 0.000321\u3011",
     "\u2192W263 **0.000323**\u2192W264 **0.000322**\u2192W265 **0.000321**\u2192W266 **0.000321**\u2192W267 \u6295\u5f71 0.000321\u3011", 1),
    # sec.4 merged-pool anchor face (W266 finalize landed)
    ("W1..W266 \u5df2\u843d\u8d26 580,920 \u5b9e\u6d4b", "W1..W266 \u5df2\u843d\u8d26 583,120 \u5b9e\u6d4b", 1),
    # sec.7/8 backfill paradigm rows -> the W266 cycle (bm-c r1086)
    ("bm-c r1084 W266 \u00a77 \u8303\u5f0f", "bm-c r1086 W266 \u00a77 \u8303\u5f0f", 1),
    ("bm-c r1084 W266 \u00a78 \u8303\u5f0f", "bm-c r1086 W266 \u00a78 \u8303\u5f0f", 1),
    # RAM face live-measured THIS window (heal (2)): psutil 4.94GB free ~5GB + nvidia-smi 6% /
    # 3.4G VRAM resident / zero active GPU burn -- gen-only lane idle, LLM retired standing
    ("\u672c\u7a97 free RAM ~3GB\uff08bm-c \u5e95\u76d8\u5e38\u9a7b\u00b724G \u7269\u7406\u5185\u5b58\u673a\u00b7CEO \u5468\u672b\u7528\u673a\u6001\u00b7GPU=gen-only \u8f66\u9053\u7a7a\u7a97\uff08nvidia-smi \u5b9e\u8bfb 3%\u00b73.2G VRAM \u5e38\u9a7b\u00b7\u96f6\u5728\u98de\u70e7\u6279\uff09\u00b7LLM \u6001\u5df2\u9000\u5f79 gen \u4e13\u7528\u8f66\u9053\u00b7\u5f15\u64ce\u961f\u5217\u7a7a\u8f6c\u00b7CPU \u8f66\u9053\u72ec\u7acb\u5982\u5b9e\u6ce8\u8bb0\uff09",
     "\u672c\u7a97 free RAM ~5GB\uff08bm-c \u5e95\u76d8\u5e38\u9a7b\u00b724G \u7269\u7406\u5185\u5b58\u673a\u00b7CEO \u5468\u672b\u7528\u673a\u6001\u00b7GPU=gen-only \u8f66\u9053\u7a7a\u7a97\uff08nvidia-smi \u5b9e\u8bfb 6%\u00b73.4G VRAM \u5e38\u9a7b\u00b7\u96f6\u5728\u98de\u70e7\u6279\uff09\u00b7LLM \u6001\u5df2\u9000\u5f79 gen \u4e13\u7528\u8f66\u9053\u00b7\u5f15\u64ce\u961f\u5217\u7a7a\u8f6c\u00b7CPU \u8f66\u9053\u72ec\u7acb\u5982\u5b9e\u6ce8\u8bb0\uff09", 1),
    # low-RAM precedent ledger append (heal (5)): W266 freeze-window ~5G bm-c anchor
    # (the wave-roll had shifted the W263 26G bm-a anchor onto the W264 label and the W264 7G onto
    # W265 -- restore both + append the true W266 anchor)
    ("\u00b7W244 \u51bb\u7ed3\u7a97 41.9G bm-a \u5b9e\u951a\u00b7W264 \u51bb\u7ed3\u7a97 26G bm-a \u5b9e\u951a\u00b7W265 \u51bb\u7ed3\u7a97 7G bm-c \u5b9e\u951a\u00b7W266 \u51bb\u7ed3\u7a97 3G bm-c \u5b9e\u951a\uff09",
     "\u00b7W244 \u51bb\u7ed3\u7a97 41.9G bm-a \u5b9e\u951a\u00b7W263 \u51bb\u7ed3\u7a97 26G bm-a \u5b9e\u951a\u00b7W264 \u51bb\u7ed3\u7a97 7G bm-c \u5b9e\u951a\u00b7W265 \u51bb\u7ed3\u7a97 3G bm-c \u5b9e\u951a\u00b7W266 \u51bb\u7ed3\u7a97 ~5G bm-c \u5b9e\u951a\uff09", 1),
]

for o, n, f in VMAP_POST_LEGS:
    c = T1.count(o)
    if c < f:
        raise SystemExit("VMAP POST FLOOR FAIL: %r count=%d floor=%d" % (o, c, f))
    T1 = T1.replace(o, n)

# ---------------- block replacements (needles marker-matched on T1; NEW = final) ----------------
NEW = {}

NEW["b_title"] = (
    "engine_owner \u884c 256 \u6ce8\u518c\u5728\u518c\uff08\u8868\u5c3e W266 \u884c\u3010bm-c r1086 \u4e94\u9762\u51bb\u7ed3 splice dc71ecc3f9 \u843d\u5730 @@SPLICE_T@@\u00b7selftest 9/9\u3011"
    "+\u5f15\u64ce\u81ea\u71c3 12/12 \u5206\u7247\u5df2\u843d\u3010results/p2cal_ext/n1_w266/ 12/12\u00b7ledger append bc7cab9893+18f6ffe931\u3011"
    "\u00b7**W266 finalize \u5df2\u843d\u5730**\u3010n1_w266_results.json \u673a\u8bfb\u00b7\u51c0\u8d26\u672c\u951a\u5934 1,009,535\u00b7K=583,120 \u5408\u5e76\u6c60\u00b7W266 finalize one-pass bm-c r1086 \u7a97 10:2x\u00b7estate chain r1086 dc71ecc3f9+007ec5e713\u3011\uff09"
    "+\u672c\u5019\u9009=bm-c \u81ea\u6709\u5e2d\u81ea\u6709\u6ce2\u3010live-derive face\uff1a\u5e2d\u9762 own-seat face\uff08bm-c r1086 \u5e2d\u4f4d MSG-20261018-1025-bmc-w267-seat \u5df2\u63a8 origin 942ebd5885"
    "\u00b7probe receipt _w267bmc_20261018 \u673a\u8bc1\u00b7bands ADMIT verbatim\u00b7queue-head seat-first lane\uff09"
    "\u2192freeze \u65f6 live derive bmc rows 85+\u5019\u9009=\u7b2c 86 \u679a EXACT\u00b7\u4ee5 freeze \u65f6 live derive \u4e3a\u51c6 r587/r359\u3011"
    "\u3010bm-c \u5faa\u73af\u73ed r1086 \u5e2d\u4f4d\u7a97 2026-10-18 10:2x\u00b7CEO \u586b\u8f7d\u4ee4 standing+2026-10-10 ~23:1x RE-ISSUE+O-20261013-2215 CPU \u5e38\u5f00\u4ee4"
    "\u00b7**W267=bm-c own-wave window per chain-order law\uff08W264 bm-a\u2192W265 bm-c\u2192W266 bm-c\u2192W267 bm-c own-turn rotation\u00b7bm-a \u5e2d r1052 \u660e\u8ba9 bm-c\u00b7MSG-1025 owner per chain-order law\uff09**\u3011\u3011\uff09"
)

NEW["b_prev"] = (
    "prev=**\u5c4a\u65f6\u7a7a\u7a97\u6d3b\u94fe\u5934 derive \u7981\u624b\u6284**\u2014\u2014\u8d77\u7a3f\u7a97\u5b9e\u51b5\uff08**\u951a\u6eda\u94fe\u9762 r576/r590 \u5f8b**\uff09\uff1a"
    "**W1..W266 N1 \u6ce8\u518c\u5168\u90e8\u843d\u5730**\u3010W266=\u6ce8\u518c+12/12 \u5206\u7247\u5df2\u70e7\u00b7**finalize \u5df2\u843d\u5730**\u2014\u2014\u6700\u65b0\u5df2 finalize \u951a=**W266**"
    "\u3010\u51c0\u8d26\u672c\u951a\u5934 **1,009,535**\u00b7K=583,120 \u5408\u5e76\u6c60\u00b7n1_w266_results.json \u673a\u8bfb\u00b7W266 finalize one-pass bm-c r1086 \u7a97 10:2x\u3011\u3011\uff1b"
    "**\u96f6\u5728\u98de\u4e0a\u6e38\u5e2d\u2014\u2014\u300c\u96f6\u5728\u98de\u4e0a\u6e38\u94fe\u524d\u300d\u65ad\u8a00\u9002\u7528\u4e14\u5e72\u51c0\u524d\u7f6e\u6210\u7acb**\uff08\u4e0a\u6e38 W266 \u5e2d\u4f4d\u5df2\u95ed\u94fe=\u6ce8\u518c+\u70e7\u5f55+finalize \u5168\u843d\u5730\u00b7\u96f6\u5728\u98de\uff09\uff1b"
    "finalize \u952e\u5e8f\u524d\u7f6e=\u5c4a\u65f6\u6309 registry \u952e derive \u590d\u6838 FAIL-CLOSED r307 \u4e24\u6001\u4f8b\u6052\u5728\uff1b"
    "\u7d2f\u8ba1 null \u6c60=583,120+2,200\uff08\u672c\u6ce2\uff09=**585,320 \u6295\u5f71**\uff08\u673a\u68b0\u7b97\u00b7\u6295\u5f71\u9762\u4ec5\u62ab\u9732\u00b7finalize \u8fd0\u884c\u65f6\u6309 registry \u952e derive \u514d\u75ab\uff09\u3002"
)

NEW["b_band"] = (
    "\uff08**A \u9762=STAIRCASE-AFFECTS-A\u00b71-HOP WALK \u5f62\u6001\uff08W239 staircase era \u540e\u7b2c\u5341\u516d\u6b21\u8fde\u7eed A-hop\uff09**\uff1a"
    "A \u9762\u7b97\u672f\u7eed\u5e26 602_501..604_500\uff08\u81ea\u6ce8\u518c W266 A \u5c3e 602_500 \u7eed\uff09"
    "\u5728\u5e2d\u4f4d\u7a97\u5b87\u5b99\uff08post-W266-REGISTERED \u7ec8\u6001\u6ce8\u518c\uff09\u8d77\u70b9\u5373 REFUSED"
    "\uff08\u6ce8\u518c W266 B \u5e26 602_501..602_700 \u843d naive A \u7a97\u5185=staircase re-emergence affects A \u627f\u88ad"
    "\u00b7W266 prereg \u00a75 item5 post-W266-REGISTERED pre-disclosure \u5151\u73b0 r587 \u5982\u5b9e\u62ab\u9732\uff09"
    "\u2192walk \u8d8a\u6ce8\u518c W266 B \u5c3e 602_700\u2192A first-clean **602_701..604_700**\u00b7**hops=1**\u00b7"
    "**A \u843d\u4f4d base==\u6ce8\u518c\u524d\u6ce2 B \u5c3e+1\uff08602_700+1\uff09\u673a\u68c0\u5173\u7cfb**"
    "\uff08A_hop_chain 1 \u8df3 verbatim leg1 \u673a\u8bc1\u3014window 602_501..604_500\u2192jump 602_701\u00b7refuser band 602_501..602_700\u3015"
    "\u00b7A_clean_at_naive_start=false\u00b7A_staircase_hop_past_W266_B=true"
    "\u00b7A base>=registered prior-wave B tail+1 floor relation\uff09\u00b7\u975e\u8f6c\u5f55 r587 \u524d\u5411\u5355\u8c03\u65ad\u8a00\u5728\u8d70\u518c\uff09\uff1b"
    "**B-ext exit seed=604_701..604_900**\uff08**B \u9762=1-HOP own-A RESERVATION CASCADE\u00b7\u843d\u4f4d\u9ad8\u4e8e\u672c\u6ce2 A \u7a97\u5f62\u6001\uff08\u7b2c\u5341\u4e03\u6b21\u8fde\u7eed above-own-A \u843d\u4f4d\uff09**\uff1a"
    "B naive \u7eed\u5e26 602_701..602_900\uff08\u81ea\u6ce8\u518c W266 B \u5c3e 602_700+1 \u7eed\uff09"
    "\u5728\u5e2d\u4f4d\u7a97\u5b87\u5b99\uff08post-W266-REGISTERED \u7ec8\u6001\u6ce8\u518c\uff09\u8d77\u70b9\u5373 REFUSED"
    "\uff08naive B \u7a97 602_701..602_900 \u843d\u672c\u6ce2 A first-clean \u7a97 602_701..604_700 \u5185"
    "=own-A reservation cascade standard leg \u5f3a\u5236\u00b7probe leg1 B_semantics \u673a\u8bc1\u00b7B_naive_refused_at_start=true\uff09"
    "\u2014\u2014**own-A reservation standard leg \u8d8a\u672c\u6ce2 A \u7a97 602_701..604_700**\uff081 hop\uff09"
    "\u2192**1 hop** \u843d\u4f4d **604_701..604_900**\u00b7**B \u843d\u4f4d base==\u672c\u6ce2 A \u7a97\u5c3e+1\uff08604_700+1\uff09EXACT \u673a\u68c0\u5173\u7cfb**"
    "\uff08B_hop lands-inside-A=false\u00b7B_lands_above_own_A=true\u00b7B_hop_chain 1 \u8df3 verbatim \u5728 probe \u56de\u6267 leg1 \u673a\u8bc1"
    "\u00b7\u975e\u8f6c\u5f55 r587\u00b7AB \u540c\u7a97\u4e92\u65a5\u9762 leg2 \u5f8b\u5728\u573a\uff09\uff1b"
    "**W266 prereg \u00a75 item5 \u6295\u5f71\u627f\u63a5\u9762\u6ce8\u8bb0\u5151\u73b0+\u843d\u4f4d\u4e00\u81f4\u5982\u9762**\uff1a"
    "\u6295\u5f71\u9884\u8a00 W267 A naive 602_501..604_500 \u5c06\u88ab\u6ce8\u518c W266 B \u5e26\u62d2\uff08staircase affects A \u627f\u88ad\u00b7\u7b2c\u5341\u516d\u6b21\u8fde\u7eed A-hop\uff09"
    "\u4e0e B own-A reservation cascade \u4e0a\u79fb\u2014\u2014\u672c\u7a97 live re-derive \u4e0e\u6295\u5f71\u5b8c\u5168\u4e00\u81f4\uff08\u96f6\u5206\u6b67\u5982\u5b9e\u6ce8\u8bb0\u00b7\u7981\u8f6c\u5f55\u6295\u5f71 r587 \u9762\u5728\u573a\uff09\u3002"
    "R268\uff1aW267 \u5e26\uff08A 602_701..604_700/B 604_701..604_900\uff09\u6ce8\u518c\u540e\u5bf9 W268+ \u7684\u62d2\u9762\u5f71\u54cd=W267 \u51bb\u7ed3\u65b9 leg4 \u524d\u77bb\u5df2\u673a\u8bc1\uff08\u89c1 \u00a75 item5\uff09\u3002"
)

NEW["b3_a"] = (
    "entry rng seed=**602_701+j**\uff08\u6cd5\u5178 \u00a74 W267 \u884c A=602_701..604_700\u00b7"
    "**STAIRCASE-AFFECTS-A\u00b71-HOP WALK \u5f62\u6001\uff08W239 staircase era \u540e\u7b2c\u5341\u516d\u6b21\u8fde\u7eed A-hop\uff09**\uff1a"
    "A \u7b97\u672f\u7eed\u5e26 602_501..604_500\uff08\u81ea\u6ce8\u518c W266 A \u5c3e 602_500 \u7eed\uff09"
    "\u5728\u5e2d\u4f4d\u7a97\u5b87\u5b99\uff08post-W266-REGISTERED \u7ec8\u6001\u6ce8\u518c\uff09\u8d77\u70b9\u5373 REFUSED"
    "\uff08\u6ce8\u518c W266 B \u5e26 602_501..602_700 \u843d naive A \u7a97\u5185=W266 prereg \u00a75 item5 post-W266-REGISTERED pre-disclosure \u5151\u73b0\u00b7r587 \u627f\u88ad\u62ab\u9732\uff09"
    "\u2192walk \u8d8a\u6ce8\u518c W266 B \u5c3e 602_700\u2192A first-clean 602_701..604_700\u00b7**hops=1**\u00b7"
    "**A \u843d\u4f4d base==\u6ce8\u518c\u524d\u6ce2 B \u5c3e+1\uff08602_700+1\uff09\u673a\u68c0\u5173\u7cfb**"
    "\uff08A_hop_chain 1 \u8df3 verbatim probe leg1 \u673a\u8bc1\u00b7A_clean_at_naive_start=false\u00b7A_staircase_hop_past_W266_B=true\uff09"
    "\u00b7\u975e\u8f6c\u5f55 r587\u00b7ADMIT \u56de\u6267\u5728\u573a\uff09\uff1bp=`BASELINE_P"
)

NEW["b3_b"] = (
    "exit rng=**604_701+j**\uff08\u6cd5\u5178 \u00a74 W267 \u884c B=604_701..604_900\u00b7"
    "**1-HOP own-A RESERVATION CASCADE\u00b7\u843d\u4f4d\u9ad8\u4e8e\u672c\u6ce2 A \u7a97\u5f62\u6001**\uff1a"
    "B naive \u7eed\u5e26 602_701..602_900\uff08\u81ea\u6ce8\u518c W266 B \u5c3e 602_700+1 \u7eed\uff09"
    "\u5728\u5e2d\u4f4d\u7a97\u5b87\u5b99\uff08post-W266-REGISTERED \u7ec8\u6001\u6ce8\u518c\uff09\u8d77\u70b9\u5373 REFUSED"
    "\uff08naive B \u7a97\u843d\u672c\u6ce2 A first-clean \u7a97 602_701..604_700 \u5185=own-A reservation cascade standard leg\u00b7probe leg1 B_semantics \u673a\u8bc1\uff09"
    "\u2192own-A reservation \u8d8a\u672c\u6ce2 A \u7a97 602_701..604_700\u21921 hop \u843d\u4f4d 604_701..604_900\u00b7"
    "**B \u843d\u4f4d base==\u672c\u6ce2 A \u7a97\u5c3e+1\uff08604_700+1\uff09\u673a\u68c0\u5173\u7cfb**"
    "\uff08B_hop lands-inside-A=false\u00b7B_lands_above_own_A=true\u00b7B_hop_chain 1 \u8df3 verbatim \u5728 probe \u56de\u6267"
    "\u00b7\u7b2c\u5341\u4e03\u6b21\u8fde\u7eed above-own-A \u843d\u4f4d\u5982\u5b9e\u6ce8\u8bb0\uff09"
    "\u00b7\u975e\u8f6c\u5f55 r587\u00b7\u4e0e W266 prereg \u00a75 item5 \u6295\u5f71\u627f\u63a5\u9762\u6ce8\u8bb0\u5151\u73b0+\u843d\u4f4d\u96f6\u5206\u6b67\u62ab\u9732\u6536\u655b\u00b7ADMIT \u56de\u6267\u5728\u573a\uff09\uff1bp_exit=`P_EXIT=0.05`"
)

NEW["b_claim_proj"] = (
    "probe W268+ \u6295\u5f71 A naive 604_701..606_700 CLEAN hops=0\uff08\u96f6 live refusers\uff09/ B naive 604_901..605_100 CLEAN hops=0 "
    "**\u4f46\u843d naive W268 A \u7a97\u5185**\u2192own-A reservation cascade \u4e0b staircase \u7ea7\u8054\u4e0a\u79fb **staircase face \u5ef6\u7eed live re-derive governs \u9884\u62ab\u9732**"
    "\uff08\u6295\u5f71 A naive 604_701..606_700 CLEAN\u00b7hops=0\u2014\u2014**post-W267-REGISTERED \u9884\u62ab\u9732\uff1anaive W268 A \u8d77\u70b9 604_701 \u5c06\u88ab\u6ce8\u518c W267 B \u5e26 604_701..604_900 \u62d2=staircase affects A \u7b2c\u5341\u4e03\u6b21\u8fde\u7eed A-hop \u9884\u671f**\uff1b"
    "\u6295\u5f71 B naive 604_901..605_100 clean \u4f46\u843d naive W268 A \u7a97 604_701..606_700 \u5185\u2014\u2014"
    "**above-own-A \u627f\u88ad face\uff1aW267 B 604_701..604_900 \u843d\u672c\u6ce2 A \u7a97\u4e4b\u4e0a\u3014\u7b2c\u5341\u4e03\u6b21\u8fde\u7eed\u3015\u00b7W267 A \u9762 1-hop=staircase affects A\u3014\u7b2c\u5341\u516d\u6b21\u8fde\u7eed\u3015\u00b7"
    "W268 \u51bb\u7ed3\u65b9\u7981\u5047\u8bbe staircase A-base==prior-B-tail+1 \u6216 B-base==own-A-tail+1 \u6052\u7b49\u00b7\u987b\u91cd\u8bfb live trace\u00b7\u6ce8\u518c W267 B \u5e26\u5c06\u62d2 naive W268 A \u7a97\u4ec5\u5f53\u91cd\u53e0\u2014\u2014"
    "**W268 freezer \u627f\u63a5\u9762\u5f3a\u5236\u6ce8\u8bb0\uff1a\u987b\u5728 post-W267 \u5b87\u5b99\u91cd derive \u4e14 derive B \u65f6\u9884\u7559\u672c\u6ce2 A \u7a97\u00b7W141 \u5148\u4f8b\u00b7never transcribe r587**\uff09"
)

NEW["b5_projection"] = (
    "5. **W268+ \u6295\u5f71\uff08probe \u673a\u8bc1 leg4\u00b7\u4e0b\u6ce2\u51bb\u7ed3\u65b9\u590d\u6838\u975e\u8f6c\u6284 r587 \u5f8b\uff09**\uff1aA naive first-clean 604_701..606_700 **CLEAN**\uff08hops=0\u00b7pre-W267 \u5b87\u5b99\u96f6 live refusers\uff09\u2014\u2014"
    "**post-W267-REGISTERED \u9884\u62ab\u9732\uff1anaive W268 A \u8d77\u70b9 604_701 \u5c06\u88ab\u6ce8\u518c W267 B \u5e26 604_701..604_900 \u62d2\uff08staircase-affects-A \u7b2c\u5341\u4e03\u6b21\u8fde\u7eed A-hop \u9884\u671f\uff09**\uff1b"
    "B naive **604_901..605_100 CLEAN\uff08hops=0\uff09\u4f46\u843d\u6295\u5f71 A \u7a97 604_701..606_700 \u5185**\uff08W268p_B_lands_inside_W268p_A_naive=true\u2014\u2014"
    "**staircase face \u5ef6\u7eed**\uff1aW267 A 602_701..604_700+B 604_701..604_900 \u6ce8\u518c\u540e naive W268 A \u7a97\u8d77\u70b9\u5373\u88ab\u6ce8\u518c W267 B \u5e26\u62d2\uff08staircase affects A \u627f\u88ad\u00b7\u7b2c\u5341\u4e03\u6b21\u8fde\u7eed A-hop \u9884\u671f\uff09"
    "\u2192A first-clean \u5c06\u4e0a\u79fb\u00b7B own-A reservation cascade \u843d\u4f4d\u76f8\u5e94\u4e0a\u79fb\u2014\u2014post-W267 \u5b87\u5b99 live re-derive \u5fc5\u53d8\u00b7\u7981\u8f6c\u5f55\u6295\u5f71\uff09\uff1b"
    "**W268 \u51bb\u7ed3\u65b9\u7981\u5047\u8bbe staircase A-base==prior-B-tail+1 \u6216 B-base==own-A-tail+1 \u6052\u7b49\u00b7\u987b\u91cd\u8bfb live trace**"
    "\uff08W251 \u8d77 staircase affects A\u00b7W252/W253/W254/W255/W256/W257/W258/W259/W260/W261/W262/W263/W264/W265/W266/W267=A/B \u53cc 1-hop \u5f62\u6001\u8fde\u7eed\u5341\u516d\u6ce2\u5982\u5b9e\u6ce8\u8bb0\u00b7seed-gap face \u5df2\u4e8e W252 \u7ec8\u7ed3=A \u9996\u8df3\u5982\u5b9e\u6ce8\u8bb0\uff09"
    "\u2014\u2014W268 \u51bb\u7ed3\u65b9\u5fc5\u987b\u5728 post-W267 \u6ce8\u518c\u5b87\u5b99\u91cd derive \u4e14 derive B \u65f6\u9884\u7559\u672c\u6ce2 A \u7a97 602_701..604_700+\u672c\u6ce2 B \u5e26 604_701..604_900"
    "\u2014\u2014leg2 \u5f8b/E36 \u5361\u00b7W141 \u5148\u4f8b\uff1bverify at W268 prereg\uff0chop \u94fe\u9010\u8df3\u5728 probe \u56de\u6267\u3002"
)

NEW["b_gated"] = (
    "\u672c\u4ef6=\u5e2d\u4f4d\u7a97\u540e\u9996\u7a97\u51bb\u7ed3\u4ef6\uff1b\u4e94\u9762\u51bb\u7ed3\u62fc\u63a5\u811a\u672c results/_w267bmc_freeze_edits.py"
    "\uff08\u6309 _w266bmc_freeze_edits.py \u6a21\u677f\u6d3e\u751f\u00b7gate0.5 \u81ea\u67e5 W266 \u884c+W266 finalize \u4ef6\u5728\u573a=\u5df2\u7eff\u00b7\u672a\u843d\u5373 loud abort \u515c\u5e95\uff09"
    "=**splice \u6267\u884c\u7a97\u6d3e\u751f\u843d\u5730\uff08r1086/r1087 W266 \u5148\u4f8b\u5b9e\u65f6\u95f4\u7ebf\uff1aprereg 595433d63c \u843d\u4e8e r1085 \u7a97\u00b7splice dc71ecc3f9 \u843d\u4e8e r1086 \u6267\u884c\u7a97 @@SPLICE_T@@\u2014\u2014"
    "**W267 freeze \u9762\uff1aW266 own-wave finalize \u5df2\u843d\u5730=\u5e2d\u4f4d\u65f6\u5373\u89e3\u9501\u2014\u2014\u5e2d\u4f4d+prereg \u672c\u7a97\u843d\u5730 per seat-first law O-20261010-2350 \u00a72\u00b7"
    "splice \u6267\u884c\u7a97\u5f00\u95e8\uff08gate0.5 \u7eff\u00b7\u7f16\u8f91\u5668 loud abort \u515c\u5e95\uff09**\u3002"
)

# marker pairs: (block, start_marker, end_marker) -- needles matched on T1 (post-roll faces)
BLOCKS = [
    ("b_title", "engine_owner \u884c 255 \u6ce8\u518c\u5728\u518c\uff08\u8868\u5c3e", "owner per chain-order law\uff09**\u3011\u3011\uff09"),
    ("b_prev", "prev=**\u5c4a\u65f6\u7a7a\u7a97\u6d3b\u94fe\u5934 derive \u7981\u624b\u6284**", "\uff08\u673a\u68b0\u7b97\u00b7\u6295\u5f71\u9762\u4ec5\u62ab\u9732\u00b7finalize \u8fd0\u884c\u65f6\u6309 registry \u952e derive \u514d\u75ab\uff09\u3002"),
    ("b_band", "\uff08**A \u9762=STAIRCASE-AFFECTS-A", "\uff08\u89c1 \u00a75 item5\uff09\u3002"),
    ("b3_a", "entry rng seed=**600_501+j**", "\uff1bp=`BASELINE_P"),
    ("b3_b", "exit rng=**602_501+j**", "\uff1bp_exit=`P_EXIT=0.05`"),
    ("b_claim_proj", "probe W267+ \u6295\u5f71 A naive 602_501..604_500 CLEAN hops=0", "never transcribe r587**\uff09"),
    ("b5_projection", "5. **W267+ \u6295\u5f71\uff08probe \u673a\u8bc1 leg4", "verify at W267 prereg\uff0chop \u94fe\u9010\u8df3\u5728 probe \u56de\u6267\u3002"),
    ("b_gated", "\u672c\u4ef6=\u5e2d\u4f4d\u7a97\u540e\u9996\u7a97\u51bb\u7ed3\u4ef6\uff1b\u4e94\u9762\u51bb\u7ed3\u62fc\u63a5\u811a\u672c", "\uff08gate0.5 \u7eff\u00b7\u7f16\u8f91\u5668 loud abort \u515c\u5e95\uff09**\u3002"),
]

T2 = T1
for name, sm, em in BLOCKS:
    c = T2.count(sm)
    assert c == 1, "BLOCK %s start-marker count=%d (expect 1)" % (name, c)
    i = T2.index(sm)
    j = T2.find(em, i)
    assert j > i, "BLOCK %s end-marker not found after start" % name
    j += len(em)
    NEWTXT = NEW[name].replace("@@SPLICE_T@@", SPLICE_T)
    T2 = T2[:i] + NEWTXT + T2[j:]
    assert NEWTXT in T2, "BLOCK %s NEW not inserted" % name

# ---------------- post gates ----------------
MUST = [
    "PERPETUAL-N1-W267", "research/PERPETUAL_N1_W267_PREREG.md",
    "602_701..604_700", "604_701..604_900", "585,320", "1,009,535", "583,120",
    "n1_w267_results.json", "MSG-20261018-1025-bmc-w267-seat", "942ebd5885",
    "\u6c60\u7b2c 265 \u679a", "\u7b2c\u516b\u5341\u516d\u679a", "\u7b2c 257 \u6ce2", "\u7b2c 86 \u679a",
    "STAIRCASE-AFFECTS-A", "\u7b2c\u5341\u516d\u6b21\u8fde\u7eed A-hop", "\u7b2c\u5341\u4e03\u6b21\u8fde\u7eed above-own-A",
    "_w267bmc_20261018", "--wave 267/finalize --wave 267",
    "W266 finalize one-pass bm-c r1086", "n_eff_held_equal 996,335",
    "\u22120.09273858", "0.24507392", "\u22120.09878527", "\uff08**0.3268** \u5b9e\u6d4b\u951a\uff09",
    "\u952e W266 \u5b9e\u6d4b K-lift **0.0001**", "line_merged@K583,120 **1.1958**", "line_pre_w266 1.1957",
    "\u5b9e\u5dee 0.0060 \u5728\u5e26\u5185", "\u5171\u4e8c\u767e\u516d\u5341\u4e94\u9762", "W2..W266",
    "engine_owner==bm-c 85 \u884c\u6ce8\u518c", "engine_owner \u884c 256 \u6ce8\u518c\u5728\u518c",
    "probe leg0 bmc_rows=85 attempt-continuity face\uff08r1086 \u7a97\u7b97\u6cd5\u00b7bm-c own seat+bmc live rows 85 \u5b9e\u8bfb\uff09",
    "bm-c \u5faa\u73af\u73ed r1086 \u5e2d\u4f4d\u7a97", "\u672c\u7a97 free RAM ~5GB", "\u672c\u673a bm-c \u5b9e\u4f8b",
    "W267=bm-c own-wave window per chain-order law",
    "595433d63c", "dc71ecc3f9", "bc7cab9893", "18f6ffe931", "007ec5e713",
    "W268+ \u6295\u5f71", "W268p_B_lands_inside_W268p_A_naive", "verify at W268 prereg",
    "_w267bmc_freeze_edits.py", "_w266bmc_freeze_edits.py \u6a21\u677f\u6d3e\u751f",
    "bm-c r1086 W266 \u00a77 \u8303\u5f0f", "bm-c r1086 W266 \u00a78 \u8303\u5f0f",
    "\uff08\u4e0a\u6e38 W266 \u5e2d\u4f4d\u5df2\u95ed\u94fe=\u6ce8\u518c+\u70e7\u5f55+finalize \u5168\u843d\u5730\u00b7\u96f6\u5728\u98de\uff09",
    "W206/W211..W266 \u4f4e RAM \u5b9e\u70e7\u5148\u4f8b", "W263 \u51bb\u7ed3\u7a97 26G bm-a \u5b9e\u951a", "W264 \u51bb\u7ed3\u7a97 7G bm-c \u5b9e\u951a",
    "W265 \u51bb\u7ed3\u7a97 3G bm-c \u5b9e\u951a", "W266 \u51bb\u7ed3\u7a97 ~5G bm-c \u5b9e\u951a",
    "\u5e2d\u4f4d\u65f6\u5373\u89e3\u9501", "\uff08\u89c1 \u00a75 item5\uff09\u3002", "R268\uff1aW267 \u5e26",
    "\u2192W263 **0.000323**\u2192W264 **0.000322**\u2192W265 **0.000321**\u2192W266 **0.000321**\u2192W267 \u6295\u5f71 0.000321\u3011",
    "602_700+1", "604_700+1",
    "A_staircase_hop_past_W266_B=true", "B_lands_above_own_A=true",
    "seed_admit_gate rc0 \u53cc\u5e26 FREE",
    "\u6ce2\u53f7 267", "\u96f6 267 \u884c", "\u96f6 skip-ahead W268/W269 \u5e2d\u4f4d\u58f0\u660e",
    "\uff08W266 \u6ce8\u518c+\u70e7\u5f55+finalize \u5168\u843d\u5730\uff09",
]
for s in MUST:
    assert s in T2, "MUST-HAVE missing: %r" % s

MUST_NOT = [
    "A-ext seed=600_501", "B-ext exit seed=602_501",
    "600_501..602_500", "602_501..604_500 CLEAN", "600_301..602_300",
    "GATED on", "finalize PENDING", "pending \u6295\u5f71 derive",
    "580,920", "1,007,335", "**583,120 \u6295\u5f71**", "line_merged@K580,920",
    "\u22120.09271568", "0.24504118", "\u22120.08956582", "**0.3149**", "\u5b9e\u5dee 0.0031 \u5728\u5e26\u5185",
    "07:0x", "19:2x", "queue_depth",
    "MSG-20261018-0719", "ace19ba85b", "e57215a2c", "a47517f792", "93298b7e33", "c72805837c", "2e622ee447",
    "bmc_rows=84", "bmc rows 84+\u5019\u9009", "\u7b2c 85 \u679a", "\u7b2c 256 \u6ce2", "\u7b2c\u516b\u5341\u4e94\u679a",
    "engine_owner==bm-c 84 \u884c\u6ce8\u518c",
    "r1084 \u5e2d", "r1084 \u5e2d\u4f4d\u7a97\u5b9e\u8dd1", "r1084 \u7a97\u7b97\u6cd5",
    "\u672c\u7a97 free RAM ~3GB", "\u8ba9\u8def\u6001", "3%\u00b73.2G VRAM",
    "W267p_", "W266p_", "W265p_",
    "line_pre_w265", "\u952e W265 \u5b9e\u6d4b K-lift", "\u952e W264 \u5b9e\u6d4b K-lift",
    "verify at W267 prereg",
    "W267+ \u6295\u5f71", "W266+ \u6295\u5f71",
    "\u7b2c\u5341\u4e94\u6b21\u8fde\u7eed A-hop", "\u7b2c\u5341\u516d\u6b21\u8fde\u7eed above-own-A", "\u8fde\u7eed\u5341\u4e94\u6ce2", "\u5171\u4e8c\u767e\u516d\u5341\u56db\u9762",
    "_w265bmc_freeze_edits_TOL.py",
    "n1_w265_results.json", "n1_w264_results.json",
    "W2..W265", "W136..W265",
    "\u6ce2\u53f7 266", "\u96f6 266 \u884c",
]
for s in MUST_NOT:
    assert s not in T2, "MUST-NOT-HAVE present: %r (count=%d)" % (s, T2.count(s))

# pinned count gates
assert T2.count("W268+ \u6295\u5f71") == 3, "W268+ count=%d (expect 3 = \u00a75.5 rolled + b5 + b6 claim)" % T2.count("W268+ \u6295\u5f71")
assert T2.count("W267+ \u6295\u5f71") == 0, "W267+ count=%d (expect 0)" % T2.count("W267+ \u6295\u5f71")
assert T2.count("hops=1") == 2, "hops=1 count=%d (expect 2)" % T2.count("hops=1")
assert T2.count("hops=0") == 5, "hops=0 count=%d (expect 5)" % T2.count("hops=0")
assert T2.count("\u7b2c\u5341\u516d\u6b21\u8fde\u7eed A-hop") == 3, "A16 count=%d (expect 3 = b_band x2 + b3_a)" % T2.count("\u7b2c\u5341\u516d\u6b21\u8fde\u7eed A-hop")
assert T2.count("\u7b2c\u5341\u4e03\u6b21\u8fde\u7eed A-hop") == 3, "A17 count=%d (expect 3 = b5 x2 + b6)" % T2.count("\u7b2c\u5341\u4e03\u6b21\u8fde\u7eed A-hop")
assert T2.count("\u7b2c\u5341\u4e03\u6b21\u8fde\u7eed above-own-A") == 2, "B17 count=%d (expect 2 = b_band + b3_b)" % T2.count("\u7b2c\u5341\u4e03\u6b21\u8fde\u7eed above-own-A")
assert T2.count("\u7b2c\u5341\u516d\u6b21\u8fde\u7eed above-own-A") == 0, "B16 count=%d (expect 0)" % T2.count("\u7b2c\u5341\u516d\u6b21\u8fde\u7eed above-own-A")
assert T2.count("\u8fde\u7eed\u5341\u516d\u6ce2") == 1, "16-wave count=%d (expect 1 = b5 NEW)" % T2.count("\u8fde\u7eed\u5341\u516d\u6ce2")
assert T2.count("602_701..604_700") >= 5, "own-A count=%d (expect >=5)" % T2.count("602_701..604_700")
assert T2.count("604_701..604_900") >= 4, "own-B count=%d (expect >=4)" % T2.count("604_701..604_900")
assert T2.count("602_501..602_700") >= 3, "reg-W266-B count=%d (expect >=3)" % T2.count("602_501..602_700")
assert T2.count("602_701..602_900") == 3, "B-naive count=%d (expect 3 = b_band x2 + b3_b)" % T2.count("602_701..602_900")
assert T2.count("602_501..604_500") == 4, "A-naive count=%d (expect 4 = b_band x3 + b3_a)" % T2.count("602_501..604_500")
assert T2.count("604_701..606_700") == 5, "W268p-A count=%d (expect 5 = b6 x3 + b5 x2)" % T2.count("604_701..606_700")
assert T2.count("604_901..605_100") == 3, "W268p-B count=%d (expect 3 = b6 x2 + b5)" % T2.count("604_901..605_100")
assert T2.count("\u5e2d\u4f4d\u65f6\u5373\u89e3\u9501") == 2, "unlock count=%d (expect 2)" % T2.count("\u5e2d\u4f4d\u65f6\u5373\u89e3\u9501")
assert T2.count("_w267bmc_20261018") == 3, "probe-receipt count=%d (expect 3 = 2 non-block + b_title)" % T2.count("_w267bmc_20261018")
assert T2.count("1,009,535") == 2, "ledger count=%d (expect 2 = b_title + b_prev)" % T2.count("1,009,535")
assert T2.count("583,120") >= 3, "merged-K count=%d (expect >=3)" % T2.count("583,120")

# residue scan: all X_Y..X_Y windows well-formed
for m in re.finditer(r"(\d{3}_\d{3})\.\.(\d{3}_\d{3})", T2):
    lo = int(m.group(1).replace("_", "")); hi = int(m.group(2).replace("_", ""))
    assert lo <= hi, "malformed window %s" % m.group(0)

io.open(OUT, "w", encoding="utf-8", newline="").write(T2)
print("W267 PREREG DERIVE OK -> %s (%d bytes, %d lines)" % (OUT, len(T2.encode("utf-8")), T2.count("\n") + 1))
print("splice commit face: dc71ecc3f9 @ " + SPLICE_T)
print("blocks replaced: %s" % ", ".join(n for n, _, _ in BLOCKS))
print("vmap legs: %d floors: %d post-legs: %d MUST: %d MUST_NOT: %d" % (
    len(VMAP), len(VMAP_FLOORS), len(VMAP_POST_LEGS), len(MUST), len(MUST_NOT)))
print("src blob-verified == 417bc0b887c53d38c55abbb4c7f1777ea65d22e2 @ 595433d63c (frozen pre-run face; HEAD post-backfill twin a9b453235f disclosed, NOT used)")
print("out sha256_16: %s" % hashlib.sha256(T2.encode("utf-8")).hexdigest()[:16])



