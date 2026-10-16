# -*- coding: utf-8 -*-
# r1063 bm-c: W259 prereg derive (count-asserted ordered transform + marker-extracted block replaces).
# Canon-clone of _w258bmc_prereg_derive.py per age() machine-needle law (shift-map one generation).
# Source = committed frozen W258 prereg AT THE FREEZE COMMIT 824b46d31 (git 824b46d31:research/PERPETUAL_N1_W258_PREREG.md,
# 44,096 bytes -- the frozen pre-run face; sec7/8 placeholders intact). Extracted to
# results/_w259bmc_w258_frozen_face.txt THIS window via python subprocess bytes (blob f3dce7a1f073f0c7903f42d31097a07395911f12,
# byte-verified hash-object == rev-parse @ 824b46d31; sha256_16 f412a772695ec76e measured pre-flight).
# TEMPLATE-FACE DISCLOSURE (needle-face divergence, honest): HEAD twin 3eaccd1dada01f4ceff017953fafef15ea0555b4 = the
# CURRENT HEAD face = the POST-CYCLE face with sec.7/8 BACKFILLED by the r1062 window (W258 actual results).
# Deriving from the backfilled face would fabricate W259 sec.7/8 "跑后实证" from W258's measured numbers -- the
# r1049/r1052/r1056/r1058/r1061 precedent (derive always from the PRIOR wave's FREEZE-COMMIT face, "frozen pre-run face;
# sec7/8 placeholders intact") and the prereg semantics both require f3dce7a1. Both faces measured this window
# (rev-parse 824b46d31:=f3dce7a1 / HEAD:=3eaccd1d); divergence disclosed in header + closeout;
# 3eaccd1d recorded as the post-backfill twin, NOT used as template.
# W259 facts (all machine-derived, never transcribed):
#   - seat probe ADMIT receipt results/_w259bmc_20261017_probe_receipt.json (r1062 window, seat rides
#     origin 16dba0e70 per r565 early-visibility law, MSG-20261017-0704-bmc-w259-seat landed in fleet/inbox/).
#     STAIRCASE CONTINUES: A naive 584_901..586_900 REFUSED at start (registered W258 B band 584_901..585_100 sits INSIDE
#     the naive A window) -> A first-clean 585_101..587_100 hops=1 (EIGHTH consecutive A-hop, W258 prereg sec.5 item5
#     A-CLEAN-at-naive pre-W258-universe projection superseded live r587, divergence disclosed) / B naive
#     585_101..585_300 REFUSED at start (lands INSIDE the own-wave W259 A first-clean window 585_101..587_100) ->
#     own-A reservation cascade hop past 587_100 -> 587_101..587_300 hops=1 (NINTH consecutive above-own-A landing);
#     seed_admit FREE x2 (A base=585101 span=2000 / B base=587101 span=200); leg0 rows=256 owner_rows=248
#     bmc_rows=78 bmc_ordinal=79 ordinal=249; leg2 conflicts=0; leg3 origin_vacancy=true;
#     leg4 W260+ projection: A naive 587_101..589_100 CLEAN hops=0 BUT post-W259-REGISTERED the naive W260 A
#     start 587_101 is REFUSED by the registered W259 B band 587_101..587_300 (NINTH consecutive A-hop expected)
#     AND the W260 B naive 587_301..587_500 lands inside the own-A reservation face.
#   - upstream W258 finalize landed (r1062 52nd-gen absorb-continuation window, ledger 989,735+2,200=991,935 EXACT):
#     merged K=565,520 / merged mu -0.09276683318008204 (8dp anchor -0.09276683) / sigma 0.24503365523916693 (8dp 0.24503366) /
#     se_mu@K565,520 0.000326 held-flat / W258-only mu -0.09565813636363636 (8dp -0.09565814) / A p95 0.3108 / K-lift 0.0000
#     back-to-zero in-band / n_eff_held 989,735 / line_pre_w258 1.1948 / line_merged@565,520 1.1948 /
#     own-slice vs pre-wave merged gap 0.0028913031835543224 in-band<0.02 back-to-small-gap family after W257 chain-max 0.0141
#     (results/perpetual_faces/n1_w258_results.json + results/_r1062bmc_w258_fivekeys.json, all six keys PASS)
#   - W258 chain: prereg freeze 824b46d31 LANDED by r1061 window + five-face freeze splice r1062-dead-window LANDED
#     37ccebffd (dual-sha16 pf 38da334ef0a033d2->dca9e66660f0c4ac / n1 e37b483340aa67ba->381d26df7e6d6b7f; W258 block
#     parity 116 rows kept W211..W239 29 + dropped W240..W256 17 + fresh W240..W257 18; kept/dropped split boundary
#     MOVES 239->240 per r1062 splice NEW FACE) + engine self-burn 12/12 (ledger appends 122485949+cc72046d7 batched 6+6
#     self-committed) + r1062 continuation sixgate PRE-FINALIZE 20th consecutive (triple identity n1 381d26df7e6d6b7f /
#     pf dca9e66660f0c4ac @ 37ccebffd) + finalize one-pass 991,935/K=565,520 + fivekeys 6/6 + sec.7/8 backfilled +
#     W259 seat published 16dba0e70.
# Needle-count pre-flight evidence: results/_w259bmc_needle_probe.py (THIS window, ALL floors below measured live
# on T0 by the probe -- results/_w259bmc_needle_counts.txt 336 faces; counts match every VMAP_FLOORS entry below;
# position-probe classified 985,335/983,135/561,120 as b1-HIST-span faces (no legs, verbatim-preserved by block replace)).
# Same-window needle heals disclosed:
# (1) NARROWED-TIMESTAMP-LEG heal vs the W258 canon: the canon's bare ("05:1x"->next) roll leg is REPLACED here by two
#     specific legs ("bm-c r1060 窗 05:1x" compound + "已落账键·05:1x" + "已落账键·05:1x finalize one-pass" family) --
#     position-probe found the x1 historical W230-leg timestamp face "n1_w230_results.json·05:1x" at T0[4421] OUTSIDE all
#     blocks which the bare roll would have corrupted (historical face, must stay 05:1x verbatim);
# (2) the two chained-W-roll consumed-label heals (se_mu chain + low-RAM list, consumed label shifts one per generation
#     per r1059 canon-embed advice -- this generation's consumed label = W253) are PRE-AUTHORED below in their
#     consumed-label rolled forms;
# (3) se_mu chain POST-LEG needle includes the bold-close "**" forms measured live (the W258 canon needle face as
#     transcribed earlier lacked the closing bold on the tail value -- live grep this window measured the true
#     face "→W257 **0.000326**】" and the POST_LEG below is authored against the measured form, floor-asserted);
# (4) 561,120 (x1, b1-HIST W256-finalize leg) gets NO roll leg this generation (pure historical face now; the W258
#     canon rolled it because its T0 still carried live prior-K faces).
# RAM face: this r1063 freeze window live-measures ~1.3G free (MEMORYSTATUSEX ullAvailPhys round 1dp at 07:4x;
# 27b LLM still resident per gpu 14,630MiB/16,384MiB + engine queue empty live-read this window -- honest face carried).
import io, os, sys, datetime, subprocess, hashlib, re

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(REPO, "results", "_w259bmc_w258_frozen_face.txt")
OUT = os.path.join(REPO, "research", "PERPETUAL_N1_W259_PREREG.md")
GIT = "C:/Program Files/Git/cmd/git.exe"

# --- source byte-identity gates ---
_blob_expect = "f3dce7a1f073f0c7903f42d31097a07395911f12"   # freeze-commit face @ 824b46d31
_ho = subprocess.run([GIT, "hash-object", SRC], capture_output=True, text=True, cwd=REPO).stdout.strip()
assert _ho == _blob_expect, "SRC blob mismatch: got %s expect %s" % (_ho, _blob_expect)
_fc = subprocess.run([GIT, "rev-parse", "824b46d31:research/PERPETUAL_N1_W258_PREREG.md"],
                     capture_output=True, text=True, cwd=REPO).stdout.strip()
assert _fc == _blob_expect, "freeze-commit blob mismatch: got %s expect %s" % (_fc, _blob_expect)
_hb = subprocess.run([GIT, "rev-parse", "HEAD:research/PERPETUAL_N1_W258_PREREG.md"],
                     capture_output=True, text=True, cwd=REPO).stdout.strip()
assert _hb == "3eaccd1dada01f4ceff017953fafef15ea0555b4", "HEAD tpl twin face drifted: %s" % _hb

T0 = io.open(SRC, encoding="utf-8", newline="").read()
assert hashlib.sha256(T0.encode("utf-8")).hexdigest()[:16] == "f412a772695ec76e", "SRC sha mismatch"

P1, P2, P3 = "\x01W\x01", "\x01N\x01", "\x01B\x01"

now = datetime.datetime.now()
FREEZE_T = "%02d:%dx" % (now.hour, now.minute // 10)

# b1-HIST-span position asserts (needle heals (4): pure-historical faces carry no legs)
_ib1s = T0.index("+W246=bm-a r1016 prereg derive")
_ib1e = T0.index("W259 freezer 承接面）】。")
for _ph in ("985,335", "983,135", "561,120"):
    _pp = T0.index(_ph)
    assert _ib1s <= _pp <= _ib1e, "pure-historical face %s outside b1 HIST span (pos %d)" % (_ph, _pp)

# machine-extracted historical spans (from T0 PRE-roll bytes: zero transcription for carried content)
_i_b1 = T0.index("+W246=bm-a r1016 prereg derive")
_j_b1 = T0.index("——本波上游链=")
HIST_B1 = T0[_i_b1:_j_b1]  # W246..W257 chain legs verbatim (frozen template bytes)
_i_b6 = T0.index("·W250 冻结窗 RAM 未记录（r1046 死窗")
_b6_end = "W240 冻结窗 33.2G bm-a 实锚）"
_j_b6 = T0.index(_b6_end) + len(_b6_end)
HIST_B6 = T0[_i_b6:_j_b6]  # W250..W240 freeze-window RAM ledger verbatim

VMAP = [
    # projection first, then line_merged face, then prior-K bare, then ledger heads (order-critical)
    ("565,520 投影", "567,720 投影"),
    ("line_merged@K563,320 **1.1947**", "line_merged@K565,520 **1.1948**"),
    ("563,320", "565,520"),
    ("989,735", "991,935"),
    ("987,535", "989,735"),
    # sec5 measured keys -> W258 measured faces (n1_w258_results.json + _r1062bmc_w258_fivekeys.json machine values)
    ("−0.09275554", "−0.09276683"),
    ("−0.10688227", "−0.09565814"),
    ("0.24502959", "0.24503366"),
    ("实差 0.0141 在带内", "实差 0.0029 在带内"),
    ("（**0.2973** 实测锚）", "（**0.3108** 实测锚）"),
    # band values outside block regions (staircase-8th-hop + own-A reservation cascade faces)
    ("A-ext seed=582_901..584_900", "A-ext seed=585_101..587_100"),
    ("entry rng seed=**582_901+j**", "entry rng seed=**585_101+j**"),
    ("entry rng=**582_901+j**", "entry rng=**585_101+j**"),
    ("exit rng=**584_901+j**", "exit rng=**587_101+j**"),
    ("A base=582901 span=2000 checked=2000 verdict=FREE", "A base=585101 span=2000 checked=2000 verdict=FREE"),
    ("B base=584901 span=200 checked=200 verdict=FREE", "B base=587101 span=200 checked=200 verdict=FREE"),
    ("R259：W258", "R260：W259"),
    # base-relation faces (block-external occurrences; block NEW uses the same new faces)
    ("582_900+1", "585_100+1"),
    ("584_900+1", "587_100+1"),
    # seat / provenance faces (W259 seat published r1062 window, rides origin 16dba0e70)
    ("MSG-20261017-0517-bmc-w258-seat", "MSG-20261017-0704-bmc-w259-seat"),
    ("d0d0d04a4", "16dba0e70"),
    ("（bm-c r1060 席·queue-head FREEZE-UNBLOCKED 发布）", "（bm-c r1062 席·queue-head FREEZE-UNBLOCKED 发布）"),
    ("（bm-c r1060 席位", "（bm-c r1062 席位"),
    ("（r1060 席位窗实跑", "（r1062 席位窗实跑"),
    # finalize window faces (narrowed-leg family per needle heal (1): NO bare 05:1x roll --
    # the x1 historical W230-leg "n1_w230_results.json·05:1x" must stay verbatim)
    ("bm-c r1060 窗 05:1x", "bm-c r1062 窗 07:0x"),
    ("已落账键·05:1x finalize one-pass", "已落账键·07:0x finalize one-pass"),
    ("已落账键·05:1x", "已落账键·07:0x"),
    # engine live-read + RAM head (bm-c current window honest: ~1.3G free live-measured THIS r1063 freeze window;
    # 27b LLM resident per gpu_mem_used 14.6G/16G + engine queue empty live-read this window)
    ("saturation_engine.py status live-read r1061", "saturation_engine.py status live-read r1063"),
    ("本窗 free RAM ~3.5GB（bm-c 底盘常驻·24G 物理内存机·LLM 态 27b 常驻+引擎队列空转·CPU 车道独立如实注记）",
     "本窗 free RAM ~1.3GB（bm-c 底盘常驻·24G 物理内存机·LLM 态 27b 常驻+引擎队列空转·CPU 车道独立如实注记）"),
    # wave-number roll (chained placeholders)
    ("W258", P1), ("W257", "W258"), ("W256", "W257"), ("W255", "W256"), ("W254", "W255"), ("W253", "W254"), (P1, "W259"),
    # result-file names (chained)
    ("n1_w258", P2), ("n1_w257", "n1_w258"), ("n1_w256", "n1_w257"), (P2, "n1_w259"),
    # probe/freeze script basenames (chained; current face _w259bmc <- template _w258bmc; date-STABLE 10-17->10-17)
    ("_w258bmc", P3), ("_w257bmc", "_w258bmc"), ("_w256bmc", "_w257bmc"), (P3, "_w259bmc"),
    # runner CLI wave
    ("--wave 258", "--wave 259"),
    ("波号 258", "波号 259"),
    # pool/engine ordinals
    ("第 256 枚", "第 257 枚"),
    ("第 248 波", "第 249 波"),
    ("bm-c 第七十八枚自有波", "bm-c 第七十九枚自有波"),
    # subsumption-order fix: compound needle contains 第 78 枚 -> MUST run before any bare roll
    ("bmc rows 77+候选=第 78 枚 EXACT", "bmc rows 78+候选=第 79 枚 EXACT"),
    ("第 78 枚", "第 79 枚"),
    ("probe leg0 bmc_rows=77 attempt-continuity face（r1060 窗算法·bm-c own seat+bmc live rows 77 实读）",
     "probe leg0 bmc_rows=78 attempt-continuity face（r1062 窗算法·bm-c own seat+bmc live rows 78 实读）"),
    ("engine_owner==bm-c 77 行注册", "engine_owner==bm-c 78 行注册"),
    ("engine_owner 行 247 注册在册", "engine_owner 行 248 注册在册"),
    # registry scan faces
    ("全二百五十五行注册 N1 带表", "全二百五十六行注册 N1 带表"),
    ("freeze 窗 live derive 255 行单态 owner rows 247", "freeze 窗 live derive 256 行单态 owner rows 248"),
    ("probe leg0 机证 255 行〔", "probe leg0 机证 256 行〔"),
    ("席位窗 probe leg0 实测 255 行〔", "席位窗 probe leg0 实测 256 行〔"),
    ("perpetual_faces.py 零 256 行", "perpetual_faces.py 零 257 行"),
    ("共二百五十五面实测", "共二百五十六面实测"),
    # sec8 placeholder projection-label bump (W260+ face)
    ("§5.5 W259+ 投影承接机证", "§5.5 W260+ 投影承接机证"),
]

VMAP_FLOORS = {
    "565,520 投影": 1, "line_merged@K563,320 **1.1947**": 1,
    "563,320": 7, "561,120": 1,   # 561,120 = b1-HIST W256-finalize leg K, preserved verbatim (position-asserted)
    "989,735": 3, "987,535": 2, "985,335": 1, "983,135": 1,   # 985,335/983,135 = b1-HIST historical heads, verbatim
    "−0.09275554": 1, "−0.10688227": 1, "0.24502959": 1, "实差 0.0141 在带内": 1,
    "（**0.2973** 实测锚）": 1,
    "A-ext seed=582_901..584_900": 1,
    "entry rng seed=**582_901+j**": 1, "entry rng=**582_901+j**": 1,
    "exit rng=**584_901+j**": 1,
    "A base=582901 span=2000 checked=2000 verdict=FREE": 1,
    "B base=584901 span=200 checked=200 verdict=FREE": 1,
    "R259：W258": 1,
    "W258": 33, "W257": 67, "W256": 8, "W255": 7, "W254": 7, "W253": 7, "W252": 9, "W251": 9, "W250": 7,
    "W259": 18,   # projection label, NOT in the roll (block-replaced; floor documentation)
    "n1_w258": 4, "n1_w257": 3, "n1_w256": 1, "n1_w255": 1,
    "_w258bmc": 4, "_w257bmc": 2, "_w256bmc": 1,
    "_w258bmc_20261017": 3,
    "--wave 258": 2, "波号 258": 1,
    "第 256 枚": 1, "第 248 波": 1, "bm-c 第七十八枚自有波": 1,
    "bmc rows 77+候选=第 78 枚 EXACT": 2, "第 78 枚": 2,
    "probe leg0 bmc_rows=77 attempt-continuity face（r1060 窗算法·bm-c own seat+bmc live rows 77 实读）": 1,
    "engine_owner==bm-c 77 行注册": 1, "engine_owner 行 247 注册在册": 1,
    "全二百五十五行注册 N1 带表": 1,
    "freeze 窗 live derive 255 行单态 owner rows 247": 1,
    "probe leg0 机证 255 行〔": 1, "席位窗 probe leg0 实测 255 行〔": 1,
    "perpetual_faces.py 零 256 行": 1,
    "共二百五十五面实测": 1,
    "表尾 W257 行": 2,
    "pre-W258 全二百五十五行注册 N1 带表": 1,
    "§5.5 W259+ 投影承接机证": 1,
    "（bm-c r1060 席·queue-head FREEZE-UNBLOCKED 发布）": 1,
    "（bm-c r1060 席位": 1, "（r1060 席位窗实跑": 1,
    "bm-c r1060 窗 05:1x": 1, "已落账键·05:1x finalize one-pass": 1, "已落账键·05:1x": 1, "05:1x": 4,   # 4 = compound + 已落账键 x2 + b1-HIST W257-finalize leg (verbatim-preserved)
    "saturation_engine.py status live-read r1061": 1,
    "本窗 free RAM ~3.5GB（bm-c 底盘常驻·24G 物理内存机·LLM 态 27b 常驻+引擎队列空转·CPU 车道独立如实注记）": 1,
    "582_900+1": 4, "584_900+1": 2,
    # block-marker stability floors (raw template face; T1 marker = post-roll form asserted in BLOCKS)
    "（**A 面=STAIRCASE-AFFECTS-A": 1,
    "已如实披露非分叉）": 1,
    "法典 §4 W258 行 A=582_901..584_900": 1,
    "法典 §4 W258 行 B=584_901..585_100": 1,
    "披露收敛·ADMIT 回执在场）": 1,
    "非转录 r587·ADMIT 回执在场）": 1,
    "5. **W259+ 投影（probe 机证 leg4": 1,
    "verify at W259 prereg，hop 链逐跳在 probe 回执。": 1,
    "·probe W259+ 投影 A naive 584_901..586_900 CLEAN hops=0": 1,
    "never transcribe r587**）": 1,
    "·W258 冻结窗 3.5G bm-c 实锚": 1,
    "·W250 冻结窗 RAM 未记录（r1046 死窗": 1,
    "W240 冻结窗 33.2G bm-a 实锚）": 1,
    "selftest W258 face（": 1, "零假设零风险。": 1,
    "+W246=bm-a r1016 prereg derive": 1,
    "——本波上游链=": 1,
    "W259 freezer 承接面）】。": 1,
    "W240..W257 leg（18 行）构成 W258 块 parity 116 行": 1, "W240..W256 legs（17 行）": 1,
    "W253/W254/W255/W256/W257/W258=A/B 双 1-hop 形态连续七波": 1,
    "r1059/W257 先例 freeze-prep 同式": 1,
    "n_eff_held_equal 987,535": 1,
    "line_pre_w257 1.1948": 1,
    "键 W257 实测 K-lift **−0.0001**": 1,
    "bm-c r1060 W257 §7 范式": 1, "bm-c r1060 W257 §8 范式": 1,
    "W243/W246/W248/W249/W250/W251/W252/W253/W254/W255/W256/W257 低 RAM 实烧先例": 1,
    "第 255 枚": 0, "第 247 波": 0, "bm-c 第七十七枚自有波": 0, "第 77 枚": 0, "第 76 枚": 0,
    "582_901..584_900": 11, "584_901..585_100": 10, "582_701..582_900": 3,
    "584_901..586_900": 5, "585_101..585_300": 3,
    "582_701..584_700": 4, "582_901..583_100": 4,
    "STAIRCASE-AFFECTS-A": 2, "hops=1": 2, "hops=0": 5,
    "第七次连续 A-hop": 3, "第八次连续 A-hop": 3, "第七次连续": 5, "第八次连续": 7,
    "第八次连续 above-own-A": 3, "第七次连续 above-own-A": 0, "第九次连续": 0, "W260": 0,
    "queue-head FREEZE-UNBLOCKED lane": 1, "queue-head FREEZE-UNBLOCKED 承接": 1,
    "本候选=bm-c 自有席自有波": 1, "seed_admit_gate rc0 双带 FREE": 1,
    "zero post-splice heal": 5, "（W138..W206+": 1,
    "PERPETUAL-N1-W258": 4, "563,320 合并池": 3, "n1_w258_results.json": 2,
    "bm-c 循环班 r1061 freeze 窗 2026-10-17": 1,
    # zero-floors (absence assertions on T0)
    "waits-upstream ARMED": 0,
    "（**B 面=CLEAN": 0,
    "991,935": 0, "994,135": 0, "567,720": 0, "0.3108": 0, "565,520 合并池": 0,
    "−0.09276683": 0, "−0.09565814": 0, "0.24503366": 0, "实差 0.0029 在带内": 0,
    "585_101..587_100": 0, "587_101..587_300": 0, "587_101..589_100": 0, "587_301..587_500": 0,
    "585_100+1": 0, "587_100+1": 0,
    "A base=585101 span=2000 checked=2000 verdict=FREE": 0,
    "B base=587101 span=200 checked=200 verdict=FREE": 0,
    "R260：W259": 0, "n1_w259": 0, "_w259bmc": 0, "--wave 259": 0, "波号 259": 0,
    "第 257 枚": 0, "第 249 波": 0, "bm-c 第七十九枚自有波": 0, "bmc rows 78+候选=第 79 枚 EXACT": 0, "第 79 枚": 0,
    "第九次连续 A-hop": 0, "第九次连续 above-own-A": 0, "W259p_B_lands_inside_W260p_A_naive": 0,
    "16dba0e70": 0, "（bm-c r1062 席": 0, "（r1062 席位窗实跑": 0, "07:0x": 0,
    "line_pre_w258": 0, "键 W258 实测 K-lift": 0, "bm-c r1062 W258 §7 范式": 0,
    "engine_owner==bm-c 78 行注册": 0, "engine_owner 行 248 注册在册": 0,
    "全二百五十六行注册 N1 带表": 0, "freeze 窗 live derive 256 行单态 owner rows 248": 0,
    "probe leg0 机证 256 行〔": 0, "席位窗 probe leg0 实测 256 行〔": 0,
    "perpetual_faces.py 零 257 行": 0, "共二百五十六面实测": 0,
    "§5.5 W260+ 投影承接机证": 0,
    "MSG-20261017-0704-bmc-w259-seat": 0,
    "_w256bmc_20261016": 0, "_w256bmc_20261017": 0, "_w257bmc_20261017": 0,
    "dca9e66660f0c4ac": 0, "381d26df7e6d6b7f": 0, "37ccebffd": 0, "122485949": 0, "cc72046d7": 0, "824b46d31": 0,
    "W260p_": 0, "W260 冻结方": 0, "W260 freezer": 0,
    "A_staircase_hop_past_W258_B": 0, "A_clean_at_naive_start=true": 0,
    "pre-W259 全二百五十六行注册 N1 带表": 0, "表尾 W258 行": 0,
    "本波上游链=W1..W258 finalize 全落地": 0,
    "·W257 冻结窗 4G": 0, "·W256 冻结窗 3.3G": 0, "·W255 冻结窗 2.0G": 0,
}

# floors for POST-chain correction legs (needles exist only in T1 after the pre-chain legs run;
#  pre-authored consumed-label forms per r1059 canon-embed advice -- this generation's consumed label = W253)
VMAP_POST_LEGS = [
    # se_mu narrowing chain: wave roll consumed the W253 label; restore it and append true W258 se 0.000326
    # (W258 key5 = held-flat per fivekeys receipt; chain values re-anchored to true history)
    ("→W249 **0.000332**→W250 **0.000331**→W251 **0.000330**→W252 **0.000330**→W254 **0.000329**→W255 **0.000328**→W256 **0.000328**→W257 **0.000327**→W258 **0.000326**】",
     "→W249 **0.000332**→W250 **0.000331**→W251 **0.000330**→W252 **0.000330**→W253 **0.000329**→W254 **0.000328**→W255 **0.000328**→W256 **0.000327**→W257 **0.000326**→W258 **0.000326**】", 1),
    # line_pre face: lowercase w-token escapes the uppercase W-roll (r1045 derive precedent);
    # W258 actual line_pre_w258 = 1.1948 (n1_w258_results skill_line machine value)
    ("line_pre_w257 1.1948", "line_pre_w258 1.1948", 1),
    # K-lift value face: wave roll W257->W258 relabeled the anchor; W258 true K-lift = 0.0000 back-to-zero
    # (in-band disclosed honest)
    ("键 W258 实测 K-lift **−0.0001**", "键 W258 实测 K-lift **0.0000**", 1),
    # sec7/8 backfill paradigm rows (W258 sec.7/8 backfilled by the r1062 window)
    ("bm-c r1060 W258 §7 范式", "bm-c r1062 W258 §7 范式", 1),
    ("bm-c r1060 W258 §8 范式", "bm-c r1062 W258 §8 范式", 1),
    # low-RAM precedent list: rolled T1 form lost the W253 label; restore it
    # (engine self-burn 12/12 r1062 window on this low-RAM machine; chain precedent every-wave append;
    #  pre-authored consumed-label form -- W253 consumed by the chained roll, W258 appended via the roll itself)
    ("W252/W254/W255/W256/W257/W258 低 RAM 实烧先例", "W252/W253/W254/W255/W256/W257/W258 低 RAM 实烧先例", 1),
    # freeze-prep precedent face (W258 prereg derive window = r1061, LANDED 824b46d31)
    ("r1059/W258 先例 freeze-prep 同式", "r1061/W258 先例 freeze-prep 同式", 1),
]

def xf(t):
    for o, n in VMAP:
        t = t.replace(o, n)
    return t

for o, f in VMAP_FLOORS.items():
    if f == 0:
        if T0.count(o):
            raise SystemExit("VMAP FLOOR(0) FAIL: %r count=%d (expect 0)" % (o, T0.count(o)))
        continue
    if T0.count(o) < f:
        raise SystemExit("VMAP FLOOR FAIL: %r count=%d floor=%d" % (o, T0.count(o), f))

T1 = xf(T0)

# freeze-window live face: regex-extract the r1061 stamp (zero transcription) -> r1063 + runtime FREEZE_T
# (NO date roll this generation: the W259 freeze window is the SAME 2026-10-17 as the W258 freeze window,
#  hours later in the same day -- only the round stamp and time roll)
_fw_pat = re.compile(r"bm-c 循环班 r1061 freeze 窗 2026-10-17 \d{2}:\dx")
_fw_hits = _fw_pat.findall(T1)
assert len(_fw_hits) == 1, "freeze-window stamp count=%d (expect 1): %r" % (len(_fw_hits), _fw_hits)
T1 = T1.replace(_fw_hits[0], "bm-c 循环班 r1063 freeze 窗 2026-10-17 " + FREEZE_T)

# post-chain correction legs: needles exist only in T1 (post chained rolls); floors checked on T1
for o, n, f in VMAP_POST_LEGS:
    if T1.count(o) < f:
        raise SystemExit("VMAP POST FLOOR FAIL: %r count=%d floor=%d" % (o, T1.count(o), f))
    T1 = T1.replace(o, n)

# ---------------- block replacements (needles marker-extracted from T1; NEW = final) ----------------
NEW = {}

WL = "（W138..W206+" + "+".join("W%d" % n for n in range(211, 259)) + "）"  # 69 estate + W211..W258 = 117 rows

NEW["b_band_ab"] = (
    "（**A 面=STAIRCASE-AFFECTS-A·1-HOP WALK 形态（W239 staircase era 后第八次连续 A-hop）**："
    "A 面算术续带 584_901..586_900（自注册 W258 A 尾 584_900 续）"
    "在席位窗宇宙（post-W258-REGISTERED 终态注册·freeze-UNBLOCKED）起点即 REFUSED"
    "（注册 W258 B 带 584_901..585_100 落 naive A 窗内=staircase re-emergence affects A 承袭·"
    "W258 prereg §5.5 item5 A-CLEAN-at-naive pre-W258-universe projection superseded live r587 如实披露）"
    "→walk 越注册 W258 B 尾 585_100→A first-clean **585_101..587_100**·**hops=1**·"
    "**A 落位 base==注册前波 B 尾+1（585_100+1）机检关系**"
    "（A_hop_chain 1 跳 verbatim leg1 机证〔window 584_901..586_900→jump 585_101·refuser band 584_901..585_100〕"
    "·A_clean_at_naive_start=false·A_staircase_hop_past_W258_B=true"
    "·A base>=registered prior-wave B tail+1 floor relation）"
    "·非转录 r587 前向单调断言在走册）；"
    "**B-ext exit seed=587_101..587_300**（**B 面=1-HOP own-A RESERVATION CASCADE·落位高于本波 A 窗形态（第九次连续 above-own-A 落位）**："
    "B naive 续带 585_101..585_300（自注册 W258 B 尾 585_100+1 续）"
    "在席位窗宇宙（post-W258-REGISTERED 终态注册·freeze-UNBLOCKED）起点即 REFUSED"
    "（naive B 窗 585_101..585_300 落本波 A first-clean 窗 585_101..587_100 内"
    "=own-A reservation cascade standard leg 强制·probe leg1 B_semantics 机证·B_naive_refused_at_start=true）"
    "——**own-A reservation standard leg 越本波 A 窗 585_101..587_100**（1 hop）"
    "→**1 hop** 落位 **587_101..587_300**·**B 落位 base==本波 A 窗尾+1（587_100+1）EXACT 机检关系**"
    "（B_hop lands-inside-A=false·B_lands_above_own_A=true·B_hop_chain 1 跳 verbatim 在 probe 回执 leg1 机证"
    "·非转录 r587·AB 同窗互斥面 leg2 律在场）；"
    "**W258 prereg §5.5 item5 投影承接面注记兑现+落位分歧如实披露**："
    "投影预言 W259 A naive 584_901..586_900 CLEAN（pre-W258 宇宙零 live refusers）——本窗 live re-derive A 面起点即被注册 W258 B 带拒"
    "（投影 A-CLEAN 未兑现=staircase affects A 承袭·第八次连续 A-hop）"
    "→A first-clean 上移 585_101..587_100→B naive 585_101..585_300 相应落本波 A 窗内→own-A reservation cascade 上移 587_101..587_300"
    "（post-W258 宇宙 live re-derive 必变·W258 prereg §5.5 已披露 live re-derive governs·禁转录投影 r587·"
    "落位高于投影=新拒面如实注记·已如实披露非分叉）"
)

NEW["b3_a_bandface"] = (
    "法典 §4 W259 行 A=585_101..587_100·**STAIRCASE-AFFECTS-A·1-HOP WALK 形态（W239 staircase era 后第八次连续 A-hop）**："
    "A 算术续带 584_901..586_900（自注册 W258 A 尾 584_900 续）"
    "在席位窗宇宙（post-W258-REGISTERED 终态注册·freeze-UNBLOCKED）起点即 REFUSED"
    "（注册 W258 B 带 584_901..585_100 落 naive A 窗内=W258 prereg §5.5 item5 A-CLEAN-at-naive 投影被 live re-derive 超越·r587 superseded 披露）"
    "→walk 越注册 W258 B 尾 585_100→A first-clean 585_101..587_100·**hops=1**·"
    "**A 落位 base==注册前波 B 尾+1（585_100+1）机检关系**"
    "（A_hop_chain 1 跳 verbatim probe leg1 机证·A_clean_at_naive_start=false·A_staircase_hop_past_W258_B=true）"
    "·非转录 r587·ADMIT 回执在场）"
)

NEW["b3_b_bandface"] = (
    "法典 §4 W259 行 B=587_101..587_300·**1-HOP own-A RESERVATION CASCADE·落位高于本波 A 窗形态**："
    "B naive 续带 585_101..585_300（自注册 W258 B 尾 585_100+1 续）"
    "在席位窗宇宙（post-W258-REGISTERED 终态注册）起点即 REFUSED"
    "（naive B 窗落本波 A first-clean 窗 585_101..587_100 内=own-A reservation cascade standard leg·probe leg1 B_semantics 机证）"
    "→own-A reservation 越本波 A 窗 585_101..587_100→1 hop 落位 587_101..587_300·"
    "**B 落位 base==本波 A 窗尾+1（587_100+1）机检关系**"
    "（B_hop lands-inside-A=false·B_lands_above_own_A=true·B_hop_chain 1 跳 verbatim 在 probe 回执"
    "·第九次连续 above-own-A 落位如实注记）"
    "·非转录 r587·与 W258 prereg §5.5 item5 投影承接面注记兑现+落位上移分歧披露收敛·ADMIT 回执在场）"
)

NEW["b1_chain_tail"] = (
    HIST_B1
    + "+W258=bm-c r1061 prereg derive（machine-SUB from frozen W257 tpl 88ae1c8e @ c7fbc443c pre-backfill face per r1052/r1049 law·derive LANDED 824b46d31·banned_direction_gate rc0·needle-count pre-flight 222 faces 全 floors 预验·4 disclosed same-window needle-heals 全 face-inventory divergences 零内容缺陷〔PN1 prior-batch face absent + bare 03:5x HIST survivor + n1_w255 HIST survivor + W252 consumed-label forms pre-authored〕）"
    + "+五面冻结 splice（r1062 死窗 06:2x LANDED 37ccebffd〔editor canon-clone _w257bmc_derive_editor.py→_w258bmc_derive_editor.py age() machine-needle law·E63 10th-gen FOUR-LEVEL replay chain mk255/mk256/mk257/age + machine-splice builder _r1062bmc_build_editor.py + needle preflight 134 faces ALL PASS + kept/dropped split boundary MOVES 239->240 per frozen W258 prereg sec.3 mandate〕·dual-sha16 pf 38da334ef0a033d2→dca9e66660f0c4ac / n1 e37b483340aa67ba→381d26df7e6d6b7f·W258 块 parity 116 rows〔kept W211..W239 29 + dropped W240..W256 17 + fresh W240..W257 18〕·bands A 582_901..584_900 SEVENTH A-hop / B 584_901..585_100 EIGHTH above-own-A per ADMIT receipt·W257 anchors ledger 989,735/K=563,320 machine-read·zero post-splice heal·absorb-verified n1 TRIPLE identity worktree==receipt post==LANDED @ 37ccebffd）"
    + "+引擎自燃 12/12（mtime-watch auto-ignite engine lane·ledger appends 122485949+cc72046d7 batched 6+6 self-committed）"
    + "+bm-c r1062 finalize one-pass 已落（K=565,520·账本头 991,935 机读·n1_w258_results.json·07:0x·fivekeys 6/6 ALL PASS·sixgate PRE-FINALIZE 20th consecutive 正相〔triple identity n1 381d26df7e6d6b7f / pf dca9e66660f0c4ac @ 37ccebffd〕·K-lift 0.0000 back-to-zero）"
    "——本波上游链=W1..W258 finalize 全落地·零在飞上游席·干净前置**；"
    "席位公示=MSG-20261017-0704-bmc-w259-seat 已推 origin 16dba0e70 先于本冻结"
    "【r565 律·席位先行·bm-c r1062 窗发布·queue-head FREEZE-UNBLOCKED 承接·W258 own-wave finalize 已落=席位时即解锁】；"
    "下游 W260+ 投影见 §5.5（probe 机证 leg4·W260 freezer 承接面）】。"
)

NEW["b5_projection"] = (
    "5. **W260+ 投影（probe 机证 leg4·下波冻结方复核非转抄 r587 律）**：A naive first-clean 587_101..589_100 **CLEAN**（hops=0·pre-W259 宇宙零 live refusers）——"
    "**post-W259-REGISTERED 预披露：naive W260 A 起点 587_101 将被注册 W259 B 带 587_101..587_300 拒（staircase-affects-A 第九次连续 A-hop 预期）**；"
    "B naive **587_301..587_500 CLEAN（hops=0）但落投影 A 窗 587_101..589_100 内**（W260p_B_lands_inside_W260p_A_naive=true——"
    "**staircase face 延续**：W259 A 585_101..587_100+B 587_101..587_300 注册后 naive W260 A 窗起点即被注册 W259 B 带拒（staircase affects A 承袭·第九次连续 A-hop 预期）"
    "→A first-clean 将上移·B own-A reservation cascade 落位相应上移——post-W259 宇宙 live re-derive 必变·禁转录投影）；"
    "**W260 冻结方禁假设 staircase A-base==prior-B-tail+1 或 B-base==own-A-tail+1 恒等·须重读 live trace**"
    "（W251 起 staircase affects A·W252/W253/W254/W255/W256/W257/W258/W259=A/B 双 1-hop 形态连续八波如实注记·seed-gap face 已于 W252 终结=A 首跳如实注记）"
    "——W260 冻结方必须在 post-W259 注册宇宙重 derive 且 derive B 时预留本波 A 窗 585_101..587_100+本波 B 带 587_101..587_300"
    "——leg2 律/E36 卡·W141 先例；verify at W260 prereg，hop 链逐跳在 probe 回执。"
)

NEW["b6_ram"] = "·W259 冻结窗 1.3G bm-c 实锚" + HIST_B6

NEW["b7_claim_projection"] = (
    "·probe W260+ 投影 A naive 587_101..589_100 CLEAN hops=0（零 live refusers）/ B naive 587_301..587_500 CLEAN hops=0 **但落 naive W260 A 窗内**"
    "→own-A reservation cascade 下 staircase 级联上移 **staircase face 延续 live re-derive governs 预披露**"
    "（投影 A naive 587_101..589_100 CLEAN·hops=0——**post-W259-REGISTERED 预披露：naive W260 A 起点 587_101 将被注册 W259 B 带 587_101..587_300 拒=staircase affects A 第九次连续 A-hop 预期**；"
    "投影 B naive 587_301..587_500 clean 但落 naive W260 A 窗 587_101..589_100 内——"
    "**above-own-A 承袭 face：W259 B 587_101..587_300 落本波 A 窗之上〔第九次连续〕·W259 A 面 1-hop=staircase affects A〔第八次连续〕·"
    "W260 冻结方禁假设 staircase A-base==prior-B-tail+1 或 B-base==own-A-tail+1 恒等·须重读 live trace·注册 W259 B 带将拒 naive W260 A 窗仅当重叠"
    "——**W260 freezer 承接面强制注记：须在 post-W259 宇宙重 derive 且 derive B 时预留本波 A 窗·W141 先例·never transcribe r587**）"
)

NEW["b8_selftest"] = (
    "selftest W259 face（A=staircase-hop honest-walk past the registered prior-wave B band 断言"
    "（A_hop_chain 与 probe 回执逐跳恒等·A 第八次连续跳=W239 staircase era 后承袭如实注记·A 落位不落任何已注册带内）"
    "·B=own-A reservation 1-hop lands-above-own-A 断言（B_hop_chain 与 probe 回执逐跳恒等·B 落位不落本波 A 窗内=同窗互斥断言·第九次连续 above-own-A 如实注记）·W258 行 parity 腿"
    "**estate 提取面注记**：冻结拼接脚本的 parity estate（W138..W206 69 行 full-span·r858 absorb 代）从**本机 W258 块物理字节**提取"
    "（结构已知·提取自证断言 69 行 range 恒等在场）——W258 块的自有 W241..W257 legs（17 行）不入 estate 路径"
    "·提取后新增 W241..W258 leg（18 行）构成 W259 块 parity 117 行" + WL + "·零假设零风险。"
)

# marker pairs: (block, start_marker, end_marker) -- needles matched on T1 (post-roll faces)
BLOCKS = [
    ("b_band_ab", "（**A 面=STAIRCASE-AFFECTS-A", "已如实披露非分叉）"),
    ("b3_a_bandface", "法典 §4 W259 行 A=582_901..584_900", "非转录 r587·ADMIT 回执在场）"),
    ("b3_b_bandface", "法典 §4 W259 行 B=584_901..585_100", "披露收敛·ADMIT 回执在场）"),
    ("b5_projection", "5. **W259+ 投影（probe 机证 leg4", "verify at W259 prereg，hop 链逐跳在 probe 回执。"),
    ("b7_claim_projection", "·probe W259+ 投影 A naive 584_901..586_900 CLEAN hops=0", "never transcribe r587**）"),
    ("b6_ram", "·W259 冻结窗 3.5G bm-c 实锚", "W240 冻结窗 33.2G bm-a 实锚）"),
    ("b8_selftest", "selftest W259 face（", "零假设零风险。"),
    ("b1_chain_tail", "+W246=bm-a r1016 prereg derive", "W259 freezer 承接面）】。"),
]

T2 = T1
for name, sm, em in BLOCKS:
    c = T2.count(sm)
    assert c == 1, "BLOCK %s start-marker count=%d (expect 1)" % (name, c)
    i = T2.index(sm)
    j = T2.find(em, i)
    assert j > i, "BLOCK %s end-marker not found after start" % name
    j += len(em)
    T2 = T2[:i] + NEW[name] + T2[j:]
    assert NEW[name] in T2, "BLOCK %s NEW not inserted" % name

# ---------------- post gates ----------------
MUST = [
    "PERPETUAL-N1-W259", "research/PERPETUAL_N1_W259_PREREG.md",
    "585_101..587_100", "587_101..587_300", "991,935", "565,520", "567,720",
    "n1_w259_results.json", "MSG-20261017-0704-bmc-w259-seat", "16dba0e70",
    "第 257 枚", "第七十九枚", "第 249 波", "第 79 枚",
    "STAIRCASE-AFFECTS-A", "第八次连续 A-hop", "第九次连续 above-own-A",
    "_w259bmc_20261017", "--wave 259", "波号 259",
    "W258=bm-c r1061 prereg derive", "r1062 finalize one-pass",
    "n_eff_held_equal 989,735", "−0.09276683", "0.24503366", "−0.09565814",
    "（**0.3108** 实测锚）", "bm-c 循环班 r1063 freeze 窗", "本窗 free RAM ~1.3GB",
    "→W249 **0.000332**→W250 **0.000331**→W251 **0.000330**→W252 **0.000330**→W253 **0.000329**→W254 **0.000328**→W255 **0.000328**→W256 **0.000327**→W257 **0.000326**→W258 **0.000326**】",
    "queue-head FREEZE-UNBLOCKED lane", "seed_admit_gate rc0 双带 FREE",
    "A base=585101", "B base=587101",
    "bm-c r1062 W258 §7 范式", "bm-c r1062 W258 §8 范式",
    "W260 freezer 承接面", "verify at W260 prereg",
    "selftest W259 face", "W241..W258 leg（18 行）构成 W259 块 parity 117 行",
    "键 W258 实测 K-lift **0.0000**", "line_merged@K565,520 **1.1948**", "line_pre_w258 1.1948",
    "实差 0.0029 在带内", "已落账键·07:0x", "bm-c r1062 窗 07:0x",
    "r1061/W258 先例 freeze-prep 同式", "256 行单态", "probe leg0 机证 256 行",
    "_w259bmc_freeze_edits", "_w258bmc_freeze_edits", "本波上游链=W1..W258 finalize 全落地",
    "engine_owner==bm-c 78 行注册", "bmc rows 78", "bmc_rows=78",
    "queue-head FREEZE-UNBLOCKED 承接", "A 落位 base==注册前波 B 尾+1（585_100+1）",
    "B 落位 base==本波 A 窗尾+1（587_100+1）",
    "W258 块的自有 W241..W257 legs（17 行）",
    "bm-c r1062 席位", "bm-c r1062 席·queue-head FREEZE-UNBLOCKED 发布",
    "post-W258-REGISTERED 终态注册", "席位窗 probe leg0 实测 256 行",
    "W243/W246/W248/W249/W250/W251/W252/W253/W254/W255/W256/W257/W258 低 RAM 实烧先例", "·W259 冻结窗 1.3G bm-c 实锚",
    "本候选=bm-c 自有席自有波", "R260：W259 带从未指派",
    "B_hop lands-inside-A=false", "B_lands_above_own_A=true", "A_staircase_hop_past_W258_B=true",
    "§5.5 W260+ 投影承接机证", "exit rng=**587_101+j**", "B-ext exit seed=587_101..587_300",
    "A-ext seed=585_101..587_100",
    "probe leg0 bmc_rows=78 attempt-continuity face（r1062 窗算法·bm-c own seat+bmc live rows 78 实读）",
    "584_901..586_900", "585_101..585_300", "587_101..589_100", "587_301..587_500",
    "A_clean_at_naive_start=false",
    "表尾 W258 行", "pre-W259 全二百五十六行注册 N1 带表", "共二百五十六面实测",
    "engine_owner 行 248 注册在册", "freeze 窗 live derive 256 行单态 owner rows 248",
    "W258 splice 先于席位窗已落地",
    "W258 own-wave finalize 已落=席位时即解锁",
    "n1_w258_results.json",
    "924e87b3f02afb72", "7b550e65716e0ada", "d4a9d7164ba9490e", "c6dfb4291c09be1e",
    "e166afc6c", "b1414b81a", "f931cf102", "72d292ea3",
    "aa6102e35", "31c9e4872", "1c7112fd9", "5996e2c93",
    "ad9776287dd52280", "986e9162b86e0c7f",
    "d93e644b38fae882", "38da334ef0a033d2", "e37b483340aa67ba",
    "550293d3f", "9b848c2e0", "370d6c81", "c7fbc443c",
    "sixgate PRE-FINALIZE 20th consecutive",
    "（r1062 席位窗实跑", "（bm-c r1062 席位",
    "zero post-splice heal", "dca9e66660f0c4ac", "381d26df7e6d6b7f", "37ccebffd", "122485949", "cc72046d7", "824b46d31",
    "（W138..W206+",
    "W252/W253/W254/W255/W256/W257/W258/W259=A/B 双 1-hop 形态连续八波",
    "W260p_B_lands_inside_W260p_A_naive",
]
for s in MUST:
    assert s in T2, "MUST-HAVE missing: %r" % s

MUST_NOT = [
    "**A-ext seed=582_901", "571_901", "571_900", "567_501", "567_500", "545_301", "545_300", "545_500", "565_501",
    "FIRST-CLEAN·hops=0", "13-HOP", "13 hops", "A_hop_chain=[] 空集", "A_clean_at_naive_start=true",
    "573_901..574_100", "573_900", "573_901", "574_101..574_300", "576_101..578_100", "576_301..576_500",
    "578_501..578_700", "578_301..580_300",
    "−0.09273764", "0.24503097", "−0.09241377", "**0.3092**", "实差 0.0003 在带内",
    "−0.09275554", "0.24502959", "−0.10688227", "**0.2973**", "实差 0.0141 在带内",
    "line_merged@K563,320", "556,720 合并池", "累计 null 池=556,720",
    "cb79242ed", "MSG-20261016-22xx", "bmc-w255-seat", "第 76 枚", "第七十六枚", "第 253 枚", "第 245 波",
    "第 78 枚", "第七十八枚", "第 256 枚", "第 77 枚", "第七十七枚",
    "engine_owner 行 244", "owner rows 244", "bmc rows 74", "bmc_rows=74", "engine_owner==bm-c 74",
    "engine_owner 行 246", "owner rows 246", "bmc rows 76", "bmc_rows=76", "engine_owner==bm-c 76",
    "engine_owner 行 247", "owner rows 247", "bmc rows 77+候选", "bmc_rows=77", "engine_owner==bm-c 77",
    "252 行", "二百五十二行注册", "二百五十二面实测", "251 行", "二百五十一行注册", "二百五十一面实测",
    "253 行单态", "机证 253 行", "实测 253 行", "254 行单态", "机证 254 行", "实测 254 行",
    "255 行单态", "机证 255 行", "实测 255 行",
    "r1060 窗算法", "（bm-c r1060 席", "（r1060 席位窗实跑",
    "bm-c r1060 窗", "bm-c 循环班 r1061", "live-read r1061", "已落账键·05:1x finalize one-pass",
    "波号 258", "--wave 258", "R259：W258",
    "verify at W259 prereg", "W259 freezer 承接面", "W259p_", "W259 冻结方",
    "键 W257 实测 K-lift", "键 W253 实测 K-lift", "键 W254 实测 K-lift", "键 W255 实测 K-lift", "键 W256 实测 K-lift", "line_pre_w253", "line_pre_w254", "line_pre_w255", "line_pre_w256", "line_pre_w257",
    "（**B 面=CLEAN", "waits-upstream ARMED",
    "（bm-c r1043 席", "第 75 枚",
    "selftest W258 face", "本窗 free RAM ~3.5GB",
    "第四次连续 A-hop", "第五次连续 A-hop", "第五次连续 above-own-A", "第四次连续 above-own-A",
    "第六次连续 A-hop", "第六次连续 above-own-A", "第七次连续 A-hop", "第七次连续", "第七次连续 above-own-A", "第六次连续",
    "571_901..573_900", "573_901..575_900",
    "·W255 冻结窗 2.0G", "·W256 冻结窗 3.3G", "·W257 冻结窗 4G", "·W258 冻结窗 3.5G",
    "_w255bmc_20261016", "_w255bmc_20261017", "_w256bmc_20261016", "_w256bmc_20261017", "_w257bmc_20261017",
    "MSG-20261017-0517-bmc-w258-seat", "d0d0d04a4", "27ee6e95a",
    "563,320 合并池",
    "W259p_B_lands_inside_W259p_A_naive",
]
for s in MUST_NOT:
    assert s not in T2, "MUST-NOT-HAVE present: %r (count=%d)" % (s, T2.count(s))

# same-window heal (r1063 run3, disclosed): '565,520 合并池' REMOVED from MUST_NOT -- it is the
# CORRECT rolled W259 pre-pool face (bare 563,320->565,520 leg rolls T0's 3 current-wave pool
# faces at §0 anchor/§4/§5; canon _w258bmc_prereg_derive.py precedent lists only the
# fully-rolled-away label in MUST_NOT). Pinned here as a positive count gate instead.
assert T2.count("565,520 合并池") == 3, "565,520 合并池 count=%d (expect 3 = §0+§4+§5 rolled pre-pool faces)" % T2.count("565,520 合并池")

# projection-fulfillment count gates
assert T2.count("W259+ 投影") == 0, "W259+ 投影 count=%d (expect 0)" % T2.count("W259+ 投影")
assert T2.count("W260+ 投影") == 4, "W260+ 投影 count=%d (expect 4 = b1 tail + b5 title + b7 claim + sec8 rolled)" % T2.count("W260+ 投影")
assert T2.count("hops=1") == 2, "hops=1 count=%d (expect 2 = 带位 A + §3 A)" % T2.count("hops=1")
assert T2.count("hops=0") == 5, "hops=0 count=%d (expect 5 = b5 x2 + b7 x3)" % T2.count("hops=0")
assert T2.count("第七次连续") == 0, "第七次连续 count=%d (expect 0)" % T2.count("第七次连续")
assert T2.count("第六次连续 A-hop") == 0, "第六次连续 A-hop count=%d (expect 0)" % T2.count("第六次连续 A-hop")
assert T2.count("第八次连续 A-hop") == 3, "第八次连续 A-hop count=%d (expect 3 = b_band_ab x2 + b3_a x1 own faces)" % T2.count("第八次连续 A-hop")
assert T2.count("第九次连续 A-hop") == 3, "第九次连续 A-hop count=%d (expect 3 = b5 pre-registered face x2 + b7 projection face)" % T2.count("第九次连续 A-hop")
assert T2.count("第九次连续") == 7, "第九次连续 count=%d (expect 7 = A-hop x3 + above-own-A x3 + 〔第九次连续〕 x1)" % T2.count("第九次连续")
assert T2.count("第八次连续") == 5, "第八次连续 count=%d (expect 5 = A-hop x3 + b8 连续跳 x1 + 〔第八次连续〕 x1)" % T2.count("第八次连续")
assert T2.count("第八次连续 above-own-A") == 0, "第八次连续 above-own-A count=%d (expect 0 = block-replaced)" % T2.count("第八次连续 above-own-A")
assert T2.count("第九次连续 above-own-A") == 3, "第九次连续 above-own-A count=%d (expect 3 = b_band_ab x1 + b3_b x1 + b7 x1)" % T2.count("第九次连续 above-own-A")
assert T2.count("第七次连续 above-own-A") == 0, "第七次连续 above-own-A count=%d (expect 0)" % T2.count("第七次连续 above-own-A")
assert T2.count("582_901..583_100") == 0, "582_901..583_100 count=%d (expect 0 = block-replaced)" % T2.count("582_901..583_100")
assert T2.count("582_701..584_700") == 0, "582_701..584_700 count=%d (expect 0 = block-replaced)" % T2.count("582_701..584_700")
assert T2.count("584_901..586_900") == 4, "584_901..586_900 count=%d (expect 4 = b_band_ab x3 [续带 + hop-chain verbatim + 投影兑现 quote] + b3_a x1)" % T2.count("584_901..586_900")
assert T2.count("585_101..585_300") == 4, "585_101..585_300 count=%d (expect 4 = b_band_ab x3 [B naive 续带 + 落 A 窗内 + 投影兑现 tail] + b3_b x1)" % T2.count("585_101..585_300")
assert T2.count("578_501..578_700") == 0, "578_501..578_700 count=%d (expect 0)" % T2.count("578_501..578_700")
assert T2.count("578_301..580_300") == 0, "578_301..580_300 count=%d (expect 0)" % T2.count("578_301..580_300")
assert T2.count("576_101..578_100") == 0, "576_101..578_100 count=%d (expect 0)" % T2.count("576_101..578_100")
assert T2.count("576_301..576_500") == 0, "576_301..576_500 count=%d (expect 0)" % T2.count("576_301..576_500")

# diagnostics (non-fatal; prior-wave band faces legitimately referenced in NEW blocks)
print("diag counts: 582_901..584_900=%d 584_901..585_100=%d (prior-wave band refs in NEW blocks + any outside-block survivors)" % (
    T2.count("582_901..584_900"), T2.count("584_901..585_100")))

# residue scan: all X_Y..X_Y windows well-formed
for m in re.finditer(r"(\d{3}_\d{3})\.\.(\d{3}_\d{3})", T2):
    lo = int(m.group(1).replace("_", "")); hi = int(m.group(2).replace("_", ""))
    assert lo <= hi, "malformed window %s" % m.group(0)

io.open(OUT, "w", encoding="utf-8", newline="").write(T2)
print("W259 PREREG DERIVE OK -> %s (%d bytes, %d lines)" % (OUT, len(T2.encode("utf-8")), T2.count("\n") + 1))
print("freeze window face: bm-c 循环班 r1063 freeze 窗 2026-10-17 " + FREEZE_T)
print("blocks replaced: %s" % ", ".join(n for n, _, _ in BLOCKS))
print("vmap legs: %d floors: %d post-legs: %d MUST: %d MUST_NOT: %d" % (len(VMAP), len(VMAP_FLOORS), len(VMAP_POST_LEGS), len(MUST), len(MUST_NOT)))
print("src blob-verified == f3dce7a1f073f0c7903f42d31097a07395911f12 @ 824b46d31 (frozen pre-run face; HEAD post-backfill twin 3eaccd1d disclosed, NOT used)")
