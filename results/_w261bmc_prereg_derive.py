# -*- coding: utf-8 -*-
# r1066 bm-c: W261 prereg derive (count-asserted ordered transform + marker-extracted block replaces).
# Canon-clone of _w260bmc_prereg_derive.py per age() machine-needle law (shift-map one generation).
# Source = committed frozen W260 prereg AT THE FREEZE COMMIT 0f33f9abc (git 0f33f9abc:research/PERPETUAL_N1_W260_PREREG.md,
# 47,643 bytes -- the frozen pre-run face; sec7/8 placeholders intact). Extracted to
# results/_w261bmc_w260_frozen_face.txt THIS window (byte-verified: disk==blob a7d34500ae5a3b3cd6a983f03c7dd32455598649,
# sha256_16 87a4c206a35e0584 == hash-object == rev-parse @ 0f33f9abc).
# TEMPLATE-FACE DISCLOSURE (needle-face divergence, honest): HEAD twin 4c684526295124ab72a51ab99bec377e51278508 = the
# CURRENT HEAD face = the POST-CYCLE face with sec.7/8 BACKFILLED by the r1065 closeout window. Deriving from the
# backfilled face would fabricate W261 sec.7/8 from W260's measured numbers -- the r1049/r1052/r1056/r1058/r1061/r1065
# precedent (derive always from the PRIOR wave's FREEZE-COMMIT face, "frozen pre-run face; sec7/8 placeholders intact")
# requires a7d34500. Both faces measured THIS window (rev-parse 0f33f9abc:=a7d34500 / HEAD:=4c684526); divergence
# disclosed in header + closeout; 4c684526 recorded as the post-backfill twin, NOT used as template.
# W261 facts (all machine-derived, never transcribed):
#   - seat probe ADMIT receipt results/_w261bmc_20261017_probe_receipt.json (r1065 closeout window, seat rides
#     origin cf23c4553 per r565 early-visibility law, MSG-20261017-1225-bmc-w261-seat landed in fleet/inbox/).
#     STAIRCASE CONTINUES: A naive 589_301..591_300 REFUSED at start (registered W260 B band 589_301..589_500 sits INSIDE
#     the naive A window) -> A first-clean 589_501..591_500 hops=1 (TENTH consecutive A-hop, W260 prereg sec.5.5 item5
#     A-CLEAN-at-naive pre-W260-universe projection superseded live r587, divergence disclosed) / B naive
#     589_501..589_700 REFUSED at start (lands INSIDE the own-wave W261 A first-clean window 589_501..591_500)
#     -> own-A reservation cascade hop past 591_500 -> 591_501..591_700 hops=1 (ELEVENTH consecutive above-own-A landing);
#     seed_admit FREE x2 (A base=589501 span=2000 / B base=591501 span=200); leg0 rows=258 owner_rows=250
#     bmc_rows=80 bma_rows=129 bmb_rows=41 ordinal=251; leg2 conflicts=0; leg3 origin_vacancy=true;
#     leg4 W262+ projection: A naive 591_501..593_500 CLEAN hops=0 BUT post-W261-REGISTERED the naive W262 A
#     start 591_501 is REFUSED by the registered W261 B band 591_501..591_700 (ELEVENTH consecutive A-hop expected)
#     AND the W262 B naive 591_701..591_900 lands inside the own-A reservation face.
#   - upstream W260 finalize landed (r1065 dead-window chain, ledger 994,135+2,200=996,335 EXACT, generated 12:10:37):
#     merged K=569,920 / merged mu -0.0927307283478383 (8dp anchor -0.09273073) / sigma 0.2450393458614433 (8dp 0.24503935) /
#     se_mu@K569,920 0.000325 held-flat / W260-only mu -0.09156054545454545 (8dp -0.09156055) / A p95 0.3292 / K-lift 0.0 held-flat
#     / n_eff_held 994,135 / line_pre_w260 1.195 / line_merged@569,920 1.195 /
#     own-slice vs pre-wave merged gap 0.00117018 in-band<0.02 (|−0.09156055−(−0.09273073)| = 0.0012 chain tightened family)
#     (results/perpetual_faces/n1_w260_results.json + results/_r1065bmc_w260_fivekeys.json, all six keys PASS)
#   - W260 chain: prereg freeze 0f33f9abc LANDED by dead-r1065 window B (machine-SUB from frozen W259 tpl b2a353f38 @
#     b709bc2cc pre-backfill face per r1052/r1049 law; needle-count pre-flight 244 faces; 1 disclosed gate-heal) +
#     five-face freeze splice LANDED e8a9d5d67 (dual-sha16 pf bfd877ee61d6b456->31d5dc07baee6620 / n1
#     57a139af18df580d->f40a82c450f32c5a; W260 block parity 118 rows [estate W138..W206 69 + kept W211..W241 31 +
#     fresh W242..W259 18; kept/dropped split boundary MOVES 241->242 per frozen W260 prereg sec.3 mandate]) +
#     engine self-burn 12/12 (ledger appends 63ef15c4f+9598cf5cb batched 6+6 self-committed) + sixgate PRE-FINALIZE
#     22nd consecutive (triple identity n1 f40a82c450f32c5a / pf 31d5dc07baee6620 @ e8a9d5d67) + finalize one-pass
#     996,335/K=569,920 (12:1x) + fivekeys 6/6 + sec.7/8 backfilled by the r1065 closeout window.
# Needle-count pre-flight evidence: results/_w261bmc_needle_probe.py (r1066 window, ALL floors below measured live
# on T0 by the probe -- results/_w261bmc_needle_counts.txt; counts match every VMAP_FLOORS entry below; post-roll T1
# forms for POST_LEG authoring extracted by the probe simulation: se_mu chain / low-RAM list / K-lift / line_pre /
# sec7-8 paradigm / freeze-prep / freeze-window stamp).
# Same-window needle heals disclosed (all face-inventory divergences zero content defects):
# (1) the bare ("已落账键·08:5x"->"已落账键·12:1x") leg is canon-symmetric REDUNDANT (the only T0 face carries the
#     " finalize one-pass" suffix and is converted by the compound leg first; the bare leg is a harmless no-op,
#     kept per the W259/W260 canon leg inventory);
# (2) NO K-lift POST_LEG this generation: the post-roll face "键 W260 实测 K-lift **0.0000**" is already TRUE
#     (n1_w260_results.json line_delta_k_lift=0.0 held-flat-at-zero) -- the W260 canon needed the leg because the rolled
#     label carried the W258 value; this generation rolls a true 0.0000 onto a true-0.0000 wave (2nd consecutive);
# (3) RAM face honest update: prior face "本窗 free RAM ~2GB（...LLM 态 27b 常驻...）" -> THIS window live-measures
#     ~11GB free (GlobalMemoryStatusEx 10.9GB, 12:4x) AND the bm-c LLM face was RETIRED by CEO order O-20261017-0953
#     (27b fill-gap mode decommissioned, ollama disabled, gen-only lane) -- the parenthetical is updated to the honest
#     retired state, disclosed here + closeout;
# (4) pre-authored consumed-label forms per r1059 canon-embed advice: this generation's consumed label = W254
#     (se_mu chain + low-RAM list), pre-authored directly in VMAP_POST_LEGS.
# (5) floor heal from the live-run audit (results/_r1066bmc_floor_audit.py: all 231 floors re-counted on T0 in
#     one shot after the first run's VMAP FLOOR FAIL): '987,535' floor 2->1 (actual=1 -- b1-HIST W257-era
#     historical ledger head appears ONCE in the frozen W260 face; the W259-template twin of this needle
#     carried 2, pattern-assumed floor corrected to the live count. Zero content impact: NO VMAP leg consumes
#     this needle -- it survives verbatim via the HIST_B1 extract; sole other 230 floors all matched exactly).
import io, os, sys, datetime, subprocess, hashlib, re

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(REPO, "results", "_w261bmc_w260_frozen_face.txt")
OUT = os.path.join(REPO, "research", "PERPETUAL_N1_W261_PREREG.md")
GIT = "C:/Program Files/Git/cmd/git.exe"

# --- source byte-identity gates ---
_blob_expect = "a7d34500ae5a3b3cd6a983f03c7dd32455598649"   # freeze-commit face @ 0f33f9abc
_ho = subprocess.run([GIT, "hash-object", SRC], capture_output=True, text=True, cwd=REPO).stdout.strip()
assert _ho == _blob_expect, "SRC blob mismatch: got %s expect %s" % (_ho, _blob_expect)
_fc = subprocess.run([GIT, "rev-parse", "0f33f9abc:research/PERPETUAL_N1_W260_PREREG.md"],
                     capture_output=True, text=True, cwd=REPO).stdout.strip()
assert _fc == _blob_expect, "freeze-commit blob mismatch: got %s expect %s" % (_fc, _blob_expect)
_hb = subprocess.run([GIT, "rev-parse", "HEAD:research/PERPETUAL_N1_W260_PREREG.md"],
                     capture_output=True, text=True, cwd=REPO).stdout.strip()
assert _hb == "4c684526295124ab72a51ab99bec377e51278508", "HEAD tpl twin face drifted: %s" % _hb

T0 = io.open(SRC, encoding="utf-8", newline="").read()
assert hashlib.sha256(T0.encode("utf-8")).hexdigest()[:16] == "87a4c206a35e0584", "SRC sha mismatch"

P1, P2, P3 = "\x01W\x01", "\x01N\x01", "\x01B\x01"

now = datetime.datetime.now()
FREEZE_T = "%02d:%dx" % (now.hour, now.minute // 10)

# b1-HIST-span position asserts (pure-historical faces carry no legs)
_ib1s = T0.index("+W246=bm-a r1016 prereg derive")
_ib1e = T0.index("W261 freezer 承接面）】。")
for _ph in ("985,335", "983,135", "561,120"):
    _pp = T0.index(_ph)
    assert _ib1s <= _pp <= _ib1e, "pure-historical face %s outside b1 HIST span (pos %d)" % (_ph, _pp)

# machine-extracted historical spans (from T0 PRE-roll bytes: zero transcription for carried content)
_i_b1 = T0.index("+W246=bm-a r1016 prereg derive")
_j_b1 = T0.index("——本波上游链=")
HIST_B1 = T0[_i_b1:_j_b1]  # W246..W260 chain legs verbatim (frozen template bytes)
_i_b6 = T0.index("·W250 冻结窗 RAM 未记录（r1046 死窗")
_b6_end = "W240 冻结窗 33.2G bm-a 实锚）"
_j_b6 = T0.index(_b6_end) + len(_b6_end)
HIST_B6 = T0[_i_b6:_j_b6]  # W250..W240 freeze-window RAM ledger verbatim

VMAP = [
    # projection first, then line_merged face, then prior-K bare, then ledger heads (order-critical)
    ("569,920 投影", "572,120 投影"),
    ("line_merged@K567,720 **1.1949**", "line_merged@K569,920 **1.195**"),
    ("567,720", "569,920"),
    ("994,135", "996,335"),
    ("991,935", "994,135"),
    ("989,735", "991,935"),
    # sec5 measured keys -> W260 measured faces (n1_w260_results.json + _r1065bmc_w260_fivekeys.json machine values)
    ("−0.09273526", "−0.09273073"),
    ("−0.08462", "−0.09156055"),
    ("0.24503750", "0.24503935"),
    ("实差 0.0081 在带内", "实差 0.0012 在带内"),
    ("（**0.3234** 实测锚）", "（**0.3292** 实测锚）"),
    # band values outside block regions (staircase-10th-hop + own-A reservation cascade faces)
    ("A-ext seed=587_301..589_300", "A-ext seed=589_501..591_500"),
    ("entry rng seed=**587_301+j**", "entry rng seed=**589_501+j**"),
    ("entry rng=**587_301+j**", "entry rng=**589_501+j**"),
    ("exit rng=**589_301+j**", "exit rng=**591_501+j**"),
    ("A base=587301 span=2000 checked=2000 verdict=FREE", "A base=589501 span=2000 checked=2000 verdict=FREE"),
    ("B base=589301 span=200 checked=200 verdict=FREE", "B base=591501 span=200 checked=200 verdict=FREE"),
    ("R261：W260", "R262：W261"),
    # base-relation faces (block-external occurrences; block NEW uses the same new faces)
    ("587_300+1", "589_500+1"),
    ("589_300+1", "591_500+1"),
    # seat / provenance faces (W261 seat published r1065 closeout window, rides origin cf23c4553)
    ("MSG-20261017-0910-bmc-w260-seat", "MSG-20261017-1225-bmc-w261-seat"),
    ("9fa2c8aed", "cf23c4553"),
    ("（bm-c r1064 席·queue-head FREEZE-UNBLOCKED 发布）", "（bm-c r1065 席·queue-head FREEZE-UNBLOCKED 发布）"),
    ("（bm-c r1064 席位", "（bm-c r1065 席位"),
    ("（r1064 席位窗实跑", "（r1065 席位窗实跑"),
    # finalize window faces (narrowed-leg family per W260 canon heal (3): NO bare 08:5x roll beyond the
    # compound -- the x1 historical W230-leg "n1_w230_results.json·05:1x" and the b1-HIST W258/W259 legs stay verbatim)
    ("bm-c r1064 窗 08:5x", "bm-c r1065 窗 12:1x"),
    ("已落账键·08:5x finalize one-pass", "已落账键·12:1x finalize one-pass"),
    ("已落账键·08:5x", "已落账键·12:1x"),
    # engine live-read + RAM head (bm-c current window honest: ~11GB free live-measured THIS r1066 freeze window;
    # LLM face RETIRED per CEO order O-20261017-0953 gen-only lane + engine queue empty live-read this window)
    ("saturation_engine.py status live-read r1065", "saturation_engine.py status live-read r1066"),
    ("本窗 free RAM ~2GB（bm-c 底盘常驻·24G 物理内存机·LLM 态 27b 常驻+引擎队列空转·CPU 车道独立如实注记）",
     "本窗 free RAM ~11GB（bm-c 底盘常驻·24G 物理内存机·LLM 态已退役 gen 专用车道·引擎队列空转·CPU 车道独立如实注记）"),
    # wave-number roll (chained placeholders)
    ("W260", P1), ("W259", "W260"), ("W258", "W259"), ("W257", "W258"), ("W256", "W257"), ("W255", "W256"), ("W254", "W255"), (P1, "W261"),
    # result-file names (chained)
    ("n1_w260", P2), ("n1_w259", "n1_w260"), ("n1_w258", "n1_w259"), (P2, "n1_w261"),
    # probe/freeze script basenames (chained; current face _w261bmc <- template _w260bmc; date-STABLE 10-17->10-17)
    ("_w260bmc", P3), ("_w259bmc", "_w260bmc"), ("_w258bmc", "_w259bmc"), (P3, "_w261bmc"),
    # runner CLI wave
    ("--wave 260", "--wave 261"),
    ("波号 260", "波号 261"),
    # pool/engine ordinals
    ("第 258 枚", "第 259 枚"),
    ("第 250 波", "第 251 波"),
    ("bm-c 第八十枚自有波", "bm-c 第八十一枚自有波"),
    # subsumption-order fix: compound needle contains 第 80 枚 -> MUST run before any bare roll
    ("bmc rows 79+候选=第 80 枚 EXACT", "bmc rows 80+候选=第 81 枚 EXACT"),
    ("第 80 枚", "第 81 枚"),
    ("probe leg0 bmc_rows=79 attempt-continuity face（r1064 窗算法·bm-c own seat+bmc live rows 79 实读）",
     "probe leg0 bmc_rows=80 attempt-continuity face（r1065 窗算法·bm-c own seat+bmc live rows 80 实读）"),
    ("engine_owner==bm-c 79 行注册", "engine_owner==bm-c 80 行注册"),
    ("engine_owner 行 249 注册在册", "engine_owner 行 250 注册在册"),
    # registry scan faces
    ("全二百五十七行注册 N1 带表", "全二百五十八行注册 N1 带表"),
    ("freeze 窗 live derive 257 行单态 owner rows 249", "freeze 窗 live derive 258 行单态 owner rows 250"),
    ("probe leg0 机证 257 行〔", "probe leg0 机证 258 行〔"),
    ("席位窗 probe leg0 实测 257 行〔", "席位窗 probe leg0 实测 258 行〔"),
    # needle heal (W260 canon heal (1) continuation): the true generation leg 零 258 -> 零 259
    ("perpetual_faces.py 零 258 行", "perpetual_faces.py 零 259 行"),
    ("共二百五十七面实测", "共二百五十八面实测"),
    # sec8 placeholder projection-label bump (W262+ face)
    ("§5.5 W261+ 投影承接机证", "§5.5 W262+ 投影承接机证"),
]

VMAP_FLOORS = {
    "569,920 投影": 1, "line_merged@K567,720 **1.1949**": 1,
    "567,720": 7, "561,120": 2,   # 561,120 = b1-HIST W256-finalize leg K, preserved verbatim (position-asserted)
    "994,135": 3, "991,935": 3, "989,735": 2, "987,535": 1, "985,335": 1, "983,135": 1,   # 987,535/985,335/983,135 = b1-HIST historical heads, verbatim (987,535 floor 2->1 heal (5))
    "−0.09273526": 1, "−0.08462": 1, "0.24503750": 1, "实差 0.0081 在带内": 1,
    "（**0.3234** 实测锚）": 1,
    "A-ext seed=587_301..589_300": 1,
    "entry rng seed=**587_301+j**": 1, "entry rng=**587_301+j**": 1,
    "exit rng=**589_301+j**": 1,
    "A base=587301 span=2000 checked=2000 verdict=FREE": 1,
    "B base=589301 span=200 checked=200 verdict=FREE": 1,
    "R261：W260": 1,
    "W260": 33, "W259": 68, "W258": 11, "W257": 9, "W256": 8, "W255": 7, "W254": 7, "W253": 8, "W252": 10, "W251": 9, "W250": 7,
    "W261": 18,   # projection label, NOT in the roll (block-replaced; floor documentation)
    "n1_w260": 4, "n1_w259": 3, "n1_w258": 1, "n1_w257": 1,
    "_w260bmc": 4, "_w259bmc": 2, "_w258bmc": 2, "_w257bmc": 2,
    "_w260bmc_20261017": 3,
    "--wave 260": 2, "波号 260": 1,
    "第 258 枚": 1, "第 250 波": 1, "bm-c 第八十枚自有波": 1,
    "bmc rows 79+候选=第 80 枚 EXACT": 2, "第 80 枚": 2,
    "probe leg0 bmc_rows=79 attempt-continuity face（r1064 窗算法·bm-c own seat+bmc live rows 79 实读）": 1,
    "engine_owner==bm-c 79 行注册": 1, "engine_owner 行 249 注册在册": 1,
    "全二百五十七行注册 N1 带表": 1,
    "freeze 窗 live derive 257 行单态 owner rows 249": 1,
    "probe leg0 机证 257 行〔": 1, "席位窗 probe leg0 实测 257 行〔": 1,
    "perpetual_faces.py 零 258 行": 1,
    "共二百五十七面实测": 1,
    "表尾 W259 行": 2,
    "pre-W260 全二百五十七行注册": 1,
    "§5.5 W261+ 投影承接机证": 1,
    "（bm-c r1064 席·queue-head FREEZE-UNBLOCKED 发布）": 1,
    "（bm-c r1064 席位": 1, "（r1064 席位窗实跑": 1,
    "bm-c r1064 窗 08:5x": 1, "已落账键·08:5x finalize one-pass": 1, "已落账键·08:5x": 1,
    "07:0x": 1,   # 1 = b1-HIST W258-finalize leg (verbatim-preserved via HIST_B1 extract)
    "05:1x": 2,   # 2 = x1 historical W230-leg + b1-HIST W257-finalize leg (verbatim-preserved via HIST_B1 extract)
    "08:5x": 4,   # 4 = compound + 已落账键·compound + b1-HIST W259-finalize leg + 1 more (HIST-anchored, no legs beyond the two specific faces)
    "saturation_engine.py status live-read r1065": 1,
    "本窗 free RAM ~2GB（bm-c 底盘常驻·24G 物理内存机·LLM 态 27b 常驻+引擎队列空转·CPU 车道独立如实注记）": 1,
    "587_300+1": 4, "589_300+1": 2,
    # block-marker stability floors (raw template face; T1 marker = post-roll form asserted in BLOCKS)
    "（**A 面=STAIRCASE-AFFECTS-A": 1,
    "已如实披露非分叉）": 1,
    "法典 §4 W260 行 A=587_301..589_300": 1,
    "法典 §4 W260 行 B=589_301..589_500": 1,
    "披露收敛·ADMIT 回执在场）": 1,
    "非转录 r587·ADMIT 回执在场）": 1,
    "5. **W261+ 投影（probe 机证 leg4": 1,
    "verify at W261 prereg，hop 链逐跳在 probe 回执。": 1,
    "·probe W261+ 投影 A naive 589_301..591_300 CLEAN hops=0": 1,
    "never transcribe r587**）": 1,
    "·W260 冻结窗 2G bm-c 实锚": 1,
    "·W250 冻结窗 RAM 未记录（r1046 死窗": 1,
    "W240 冻结窗 33.2G bm-a 实锚）": 1,
    "selftest W260 face（": 1, "零假设零风险。": 1,
    "+W246=bm-a r1016 prereg derive": 1,
    "——本波上游链=": 1,
    "W261 freezer 承接面）】。": 1,
    "W261 冻结方": 3,
    "W242..W259 leg（18 行）构成 W260 块 parity 118 行": 1,
    "W252/W253/W254/W255/W256/W257/W258/W259/W260=A/B 双 1-hop 形态连续九波": 1,
    "r1061/W257 先例 freeze-prep 同式": 0, "r1063/W259 先例 freeze-prep 同式": 1,
    "n_eff_held_equal 991,935": 1,
    "line_pre_w258 1.1948": 0,
    "键 W259 实测 K-lift **0.0000**": 1,
    "bm-c r1064 W259 §7 范式": 1, "bm-c r1064 W259 §8 范式": 1,
    "W243/W246/W248/W249/W250/W251/W252/W253/W254/W255/W256/W257/W258/W259 低 RAM 实烧先例": 1,
    "第 255 枚": 0, "第 247 波": 0, "bm-c 第七十七枚自有波": 0, "第 77 枚": 0, "第 76 枚": 0, "第 78 枚": 0,
    "585_101..587_100": 2, "587_101..587_300": 5,
    "584_901..586_900": 0, "585_101..585_300": 0,
    "STAIRCASE-AFFECTS-A": 2, "hops=1": 2, "hops=0": 5,
    "第八次连续 A-hop": 0, "第九次连续 A-hop": 3, "第八次连续": 0, "第九次连续": 5,
    "第九次连续 above-own-A": 0, "第十次连续": 7, "第十次连续 A-hop": 3,
    "第十次连续 above-own-A": 3, "第十一次连续": 0, "第十一次连续 A-hop": 0, "第十一次连续 above-own-A": 0,
    "queue-head FREEZE-UNBLOCKED lane": 1, "queue-head FREEZE-UNBLOCKED 承接": 1,
    "本候选=bm-c 自有席自有波": 1, "seed_admit_gate rc0 双带 FREE": 1,
    "zero post-splice heal": 7, "fivekeys 6/6": 7, "（W138..W206+": 1,
    "PERPETUAL-N1-W260": 4, "563,320": 2,
    "bm-c 循环班 r1065 freeze 窗 2026-10-17": 1,
    "37ccebffd": 3, "381d26df7e6d6b7f": 2, "dca9e66660f0c4ac": 2, "824b46d31": 1, "122485949": 1, "cc72046d7": 1, "e166afc6c": 2,
    "16dba0e70": 0, "9fa2c8aed": 3, "MSG-20261017-0910-bmc-w260-seat": 4,
    "sixgate PRE-FINALIZE 21st consecutive": 1,
    "W260p_": 0, "W261 冻结方": 3, "W262 冻结方": 0,
    "W261p_": 2, "W261p_B_lands_inside_W261p_A_naive": 1,
    "A_staircase_hop_past_W258_B": 0, "A_staircase_hop_past_W259_B": 2,
    "A_clean_at_naive_start=false": 2,
    "n1_w260_results.json": 2, "n1_w259_results.json": 3,
    "W259=bm-c r1063 prereg derive": 1, "r1064 finalize one-pass": 1,
    "本波上游链=W1..W259 finalize 全落地": 1,
    "K=567,720": 4,
    # zero-floors (absence assertions on T0)
    "waits-upstream ARMED": 0,
    "（**B 面=CLEAN": 0,
    "996,335": 0, "998,535": 0, "572,120": 0, "569,920 合并池": 0, "567,720 合并池": 3,
    "K=569,920": 0, "K=572,120": 0,
    "0.3292": 0, "0.24503935": 0, "−0.09273073": 0, "−0.09156055": 0, "实差 0.0012 在带内": 0,
    "line_merged@K569,920 **1.195**": 0, "line_pre_w260": 0, "line_pre_w259 1.1949": 1,
    "589_501..591_500": 0, "591_501..591_700": 0, "591_501..593_500": 0, "591_701..591_900": 0,
    "589_500+1": 0, "591_500+1": 0,
    "A base=589501 span=2000 checked=2000 verdict=FREE": 0,
    "B base=591501 span=200 checked=200 verdict=FREE": 0,
    "R262：W261": 0, "n1_w261": 0, "_w261bmc": 0, "--wave 261": 0, "波号 261": 0,
    "第 259 枚": 0, "第 251 波": 0, "bm-c 第八十一枚自有波": 0, "bmc rows 80+候选=第 81 枚 EXACT": 0, "第 81 枚": 0,
    "W262p_B_lands_inside_W262p_A_naive": 0, "W262": 0,
    "MSG-20261017-1225-bmc-w261-seat": 0, "cf23c4553": 0,
    "（bm-c r1065 席": 0, "（r1065 席位窗实跑": 0, "bm-c r1065 W260 §7 范式": 0,
    "键 W260 实测 K-lift": 0,
    "r1065/W260 先例 freeze-prep 同式": 0,
    "engine_owner==bm-c 80 行注册": 0, "engine_owner 行 250 注册在册": 0,
    "全二百五十八行注册 N1 带表": 0, "freeze 窗 live derive 258 行单态 owner rows 250": 0,
    "probe leg0 机证 258 行〔": 0, "席位窗 probe leg0 实测 258 行〔": 0, "perpetual_faces.py 零 259 行": 0, "共二百五十八面实测": 0,
    "§5.5 W262+ 投影承接机证": 0,
    "0f33f9abc": 0, "e8a9d5d67": 0, "63ef15c4f": 0, "9598cf5cb": 0,
    "31d5dc07baee6620": 0, "f40a82c450f32c5a": 0, "87a4c206a35e0584": 0, "b2a353f38": 0,
    "selftest W261 face（": 0, "bm-c 循环班 r1066 freeze 窗": 0,
    "W260=bm-c r1065 prereg derive": 0, "r1065 finalize one-pass": 0,
    "本波上游链=W1..W260 finalize 全落地": 0,
    "n_eff_held_equal 994,135": 0, "n_eff_held_equal 996,335": 0, "n_eff_held_equal 989,735": 0,
}

# floors for POST-chain correction legs (needles exist only in T1 after the pre-chain legs run;
#  pre-authored consumed-label forms per r1059 canon-embed advice -- this generation's consumed label = W254)
VMAP_POST_LEGS = [
    # se_mu narrowing chain: wave roll consumed the W254 label; restore it and append true W260 se 0.000325
    # (W260 key5 = held-flat per fivekeys receipt; chain values re-anchored to true history)
    ("→W249 **0.000332**→W250 **0.000331**→W251 **0.000330**→W252 **0.000330**→W253 **0.000329**→W255 **0.000328**→W256 **0.000328**→W257 **0.000327**→W258 **0.000326**→W259 **0.000326**→W260 **0.000325**】",
     "→W249 **0.000332**→W250 **0.000331**→W251 **0.000330**→W252 **0.000330**→W253 **0.000329**→W254 **0.000328**→W255 **0.000328**→W256 **0.000327**→W257 **0.000326**→W258 **0.000326**→W259 **0.000325**→W260 **0.000325**】", 1),
    # line_pre face: lowercase w-token escapes the uppercase W-roll (r1045 derive precedent);
    # W260 actual line_pre_w260 = 1.195 (n1_w260_results skill_line machine value)
    ("line_pre_w259 1.1949", "line_pre_w260 1.195", 1),
    # NO K-lift leg this generation (needle heal (2): post-roll form already true **0.0000**)
    # sec7/8 backfill paradigm rows (W260 sec.7/8 backfilled by the r1065 closeout window)
    ("bm-c r1064 W260 §7 范式", "bm-c r1065 W260 §7 范式", 1),
    ("bm-c r1064 W260 §8 范式", "bm-c r1065 W260 §8 范式", 1),
    # low-RAM precedent list: rolled T1 form lost the W254 label; restore it
    # (engine self-burn 12/12 r1065 window on this low-RAM machine; chain precedent every-wave append;
    #  pre-authored consumed-label form -- W254 consumed by the chained roll, W260 appended via the roll itself)
    ("W243/W246/W248/W249/W250/W251/W252/W253/W255/W256/W257/W258/W259/W260 低 RAM 实烧先例", "W243/W246/W248/W249/W250/W251/W252/W253/W254/W255/W256/W257/W258/W259/W260 低 RAM 实烧先例", 1),
    # freeze-prep precedent face (W260 prereg derive window = r1065 dead-window B, LANDED 0f33f9abc)
    ("r1063/W260 先例 freeze-prep 同式", "r1065/W260 先例 freeze-prep 同式", 1),
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

# freeze-window live face: regex-extract the r1065 stamp (zero transcription) -> r1066 + runtime FREEZE_T
# (NO date roll this generation: the W261 freeze window is the SAME 2026-10-17 as the W260 freeze window,
#  hours later in the same day -- only the round stamp and time roll)
_fw_pat = re.compile(r"bm-c 循环班 r1065 freeze 窗 2026-10-17 \d{2}:\dx")
_fw_hits = _fw_pat.findall(T1)
assert len(_fw_hits) == 1, "freeze-window stamp count=%d (expect 1): %r" % (len(_fw_hits), _fw_hits)
T1 = T1.replace(_fw_hits[0], "bm-c 循环班 r1066 freeze 窗 2026-10-17 " + FREEZE_T)

# post-chain correction legs: needles exist only in T1 (post chained rolls); floors checked on T1
for o, n, f in VMAP_POST_LEGS:
    if T1.count(o) < f:
        raise SystemExit("VMAP POST FLOOR FAIL: %r count=%d floor=%d" % (o, T1.count(o), f))
    T1 = T1.replace(o, n)

# ---------------- block replacements (needles marker-extracted from T1; NEW = final) ----------------
NEW = {}

WL = "（W138..W206+" + "+".join("W%d" % n for n in range(211, 261)) + "）"  # 69 estate + W211..W260 = 119 rows

NEW["b_band_ab"] = (
    "（**A 面=STAIRCASE-AFFECTS-A·1-HOP WALK 形态（W239 staircase era 后第十次连续 A-hop）**："
    "A 面算术续带 589_301..591_300（自注册 W260 A 尾 589_300 续）"
    "在席位窗宇宙（post-W260-REGISTERED 终态注册·freeze-UNBLOCKED）起点即 REFUSED"
    "（注册 W260 B 带 589_301..589_500 落 naive A 窗内=staircase re-emergence affects A 承袭·"
    "W260 prereg §5.5 item5 A-CLEAN-at-naive pre-W260-universe projection superseded live r587 如实披露）"
    "→walk 越注册 W260 B 尾 589_500→A first-clean **589_501..591_500**·**hops=1**·"
    "**A 落位 base==注册前波 B 尾+1（589_500+1）机检关系**"
    "（A_hop_chain 1 跳 verbatim leg1 机证〔window 589_301..591_300→jump 589_501·refuser band 589_301..589_500〕"
    "·A_clean_at_naive_start=false·A_staircase_hop_past_W260_B=true"
    "·A base>=registered prior-wave B tail+1 floor relation）"
    "·非转录 r587 前向单调断言在走册）；"
    "**B-ext exit seed=591_501..591_700**（**B 面=1-HOP own-A RESERVATION CASCADE·落位高于本波 A 窗形态（第十一次连续 above-own-A 落位）**："
    "B naive 续带 589_501..589_700（自注册 W260 B 尾 589_500+1 续）"
    "在席位窗宇宙（post-W260-REGISTERED 终态注册·freeze-UNBLOCKED）起点即 REFUSED"
    "（naive B 窗 589_501..589_700 落本波 A first-clean 窗 589_501..591_500 内"
    "=own-A reservation cascade standard leg 强制·probe leg1 B_semantics 机证·B_naive_refused_at_start=true）"
    "——**own-A reservation standard leg 越本波 A 窗 589_501..591_500**（1 hop）"
    "→**1 hop** 落位 **591_501..591_700**·**B 落位 base==本波 A 窗尾+1（591_500+1）EXACT 机检关系**"
    "（B_hop lands-inside-A=false·B_lands_above_own_A=true·B_hop_chain 1 跳 verbatim 在 probe 回执 leg1 机证"
    "·非转录 r587·AB 同窗互斥面 leg2 律在场）；"
    "**W260 prereg §5.5 item5 投影承接面注记兑现+落位分歧如实披露**："
    "投影预言 W261 A naive 589_301..591_300 CLEAN（pre-W260 宇宙零 live refusers）——本窗 live re-derive A 面起点即被注册 W260 B 带拒"
    "（投影 A-CLEAN 未兑现=staircase affects A 承袭·第十次连续 A-hop）"
    "→A first-clean 上移 589_501..591_500→B naive 589_501..589_700 相应落本波 A 窗内→own-A reservation cascade 上移 591_501..591_700"
    "（post-W260 宇宙 live re-derive 必变·W260 prereg §5.5 已披露 live re-derive governs·禁转录投影 r587·"
    "落位高于投影=新拒面如实注记·已如实披露非分叉）"
)

NEW["b3_a_bandface"] = (
    "法典 §4 W261 行 A=589_501..591_500·**STAIRCASE-AFFECTS-A·1-HOP WALK 形态（W239 staircase era 后第十次连续 A-hop）**："
    "A 算术续带 589_301..591_300（自注册 W260 A 尾 589_300 续）"
    "在席位窗宇宙（post-W260-REGISTERED 终态注册·freeze-UNBLOCKED）起点即 REFUSED"
    "（注册 W260 B 带 589_301..589_500 落 naive A 窗内=W260 prereg §5.5 item5 A-CLEAN-at-naive 投影被 live re-derive 超越·r587 superseded 披露）"
    "→walk 越注册 W260 B 尾 589_500→A first-clean 589_501..591_500·**hops=1**·"
    "**A 落位 base==注册前波 B 尾+1（589_500+1）机检关系**"
    "（A_hop_chain 1 跳 verbatim probe leg1 机证·A_clean_at_naive_start=false·A_staircase_hop_past_W260_B=true）"
    "·非转录 r587·ADMIT 回执在场）"
)

NEW["b3_b_bandface"] = (
    "法典 §4 W261 行 B=591_501..591_700·**1-HOP own-A RESERVATION CASCADE·落位高于本波 A 窗形态**："
    "B naive 续带 589_501..589_700（自注册 W260 B 尾 589_500+1 续）"
    "在席位窗宇宙（post-W260-REGISTERED 终态注册）起点即 REFUSED"
    "（naive B 窗落本波 A first-clean 窗 589_501..591_500 内=own-A reservation cascade standard leg·probe leg1 B_semantics 机证）"
    "→own-A reservation 越本波 A 窗 589_501..591_500→1 hop 落位 591_501..591_700·"
    "**B 落位 base==本波 A 窗尾+1（591_500+1）机检关系**"
    "（B_hop lands-inside-A=false·B_lands_above_own_A=true·B_hop_chain 1 跳 verbatim 在 probe 回执"
    "·第十一次连续 above-own-A 落位如实注记）"
    "·非转录 r587·与 W260 prereg §5.5 item5 投影承接面注记兑现+落位上移分歧披露收敛·ADMIT 回执在场）"
)

NEW["b1_chain_tail"] = (
    HIST_B1
    + "+W260=bm-c r1065 prereg derive（machine-SUB from frozen W259 tpl b2a353f38 @ b709bc2cc pre-backfill face per r1052/r1049 law·derive LANDED 0f33f9abc·banned_direction_gate rc0·needle-count pre-flight 244 faces 全 floors 预验·1 disclosed same-window gate-heal〔line-591 prior-label expect 3->0 W259-lineage mirror〕+ derive ALL GATES PASS vmap 61+floors 221+post-legs 6+MUST 129+MUST_NOT 175+8 blocks·bands A 587_301..589_300 NINTH consecutive A-hop / B 589_301..589_500 TENTH consecutive above-own-A·out 47,643B sha256_16 87a4c206a35e0584·sec7/8 placeholders intact）"
    + "+五面冻结 splice（r1065 死窗 LANDED e8a9d5d67〔E63 13th-gen 1 disclosed pre-splice editor heal：editor OUTPUT-GATE w245_a 0!=1=builder wrongly rolled frozen aging-face token w244_a +1 AGAIN〔r1064 healed same defect in W259 editor〕->healed back to w244_a 12 per 5-gen frozen-verbatim canon W255..W259·2nd freeze_edits invocation correctly r609-aborted·DEBT HEALED：n1_w259_results.json missed by r1064 closeout landed there〕·dual-sha16 pf bfd877ee61d6b456→31d5dc07baee6620 / n1 57a139af18df580d→f40a82c450f32c5a·W260 块 parity 118 rows〔estate W138..W206 69 + kept W211..W241 31 + fresh W242..W259 18·kept/dropped split boundary MOVES 241->242 per frozen W260 prereg sec.3 mandate〕·bands A 587_301..589_300 NINTH A-hop / B 589_301..589_500 TENTH above-own-A per ADMIT receipt·W259 anchors ledger 994,135/K=567,720 machine-read·zero post-splice heal·absorb-verified n1 TRIPLE identity worktree==receipt post==LANDED @ e8a9d5d67）"
    + "+引擎自燃 12/12（mtime-watch auto-ignite engine lane·ledger appends 63ef15c4f+9598cf5cb batched 6+6 self-committed）"
    + "+bm-c r1065 finalize one-pass 已落（K=569,920·账本头 996,335 机读·n1_w260_results.json·12:1x·fivekeys 6/6 ALL PASS·sixgate PRE-FINALIZE 22nd consecutive 正相〔triple identity n1 f40a82c450f32c5a / pf 31d5dc07baee6620 @ e8a9d5d67〕·K-lift 0.0000 held-flat）"
    "——本波上游链=W1..W260 finalize 全落地·零在飞上游席·干净前置**；"
    "席位公示=MSG-20261017-1225-bmc-w261-seat 已推 origin cf23c4553 先于本冻结"
    "【r565 律·席位先行·bm-c r1065 窗发布·queue-head FREEZE-UNBLOCKED 承接·W260 own-wave finalize 已落=席位时即解锁】；"
    "下游 W262+ 投影见 §5.5（probe 机证 leg4·W262 freezer 承接面）】。"
)

NEW["b5_projection"] = (
    "5. **W262+ 投影（probe 机证 leg4·下波冻结方复核非转抄 r587 律）**：A naive first-clean 591_501..593_500 **CLEAN**（hops=0·pre-W261 宇宙零 live refusers）——"
    "**post-W261-REGISTERED 预披露：naive W262 A 起点 591_501 将被注册 W261 B 带 591_501..591_700 拒（staircase-affects-A 第十一次连续 A-hop 预期）**；"
    "B naive **591_701..591_900 CLEAN（hops=0）但落投影 A 窗 591_501..593_500 内**（W262p_B_lands_inside_W262p_A_naive=true——"
    "**staircase face 延续**：W261 A 589_501..591_500+B 591_501..591_700 注册后 naive W262 A 窗起点即被注册 W261 B 带拒（staircase affects A 承袭·第十一次连续 A-hop 预期）"
    "→A first-clean 将上移·B own-A reservation cascade 落位相应上移——post-W261 宇宙 live re-derive 必变·禁转录投影）；"
    "**W262 冻结方禁假设 staircase A-base==prior-B-tail+1 或 B-base==own-A-tail+1 恒等·须重读 live trace**"
    "（W251 起 staircase affects A·W252/W253/W254/W255/W256/W257/W258/W259/W260/W261=A/B 双 1-hop 形态连续十波如实注记·seed-gap face 已于 W252 终结=A 首跳如实注记）"
    "——W262 冻结方必须在 post-W261 注册宇宙重 derive 且 derive B 时预留本波 A 窗 589_501..591_500+本波 B 带 591_501..591_700"
    "——leg2 律/E36 卡·W141 先例；verify at W262 prereg，hop 链逐跳在 probe 回执。"
)

NEW["b6_ram"] = "·W261 冻结窗 11G bm-c 实锚" + HIST_B6

NEW["b7_claim_projection"] = (
    "·probe W262+ 投影 A naive 591_501..593_500 CLEAN hops=0（零 live refusers）/ B naive 591_701..591_900 CLEAN hops=0 **但落 naive W262 A 窗内**"
    "→own-A reservation cascade 下 staircase 级联上移 **staircase face 延续 live re-derive governs 预披露**"
    "（投影 A naive 591_501..593_500 CLEAN·hops=0——**post-W261-REGISTERED 预披露：naive W262 A 起点 591_501 将被注册 W261 B 带 591_501..591_700 拒=staircase affects A 第十一次连续 A-hop 预期**；"
    "投影 B naive 591_701..591_900 clean 但落 naive W262 A 窗 591_501..593_500 内——"
    "**above-own-A 承袭 face：W261 B 591_501..591_700 落本波 A 窗之上〔第十一次连续〕·W261 A 面 1-hop=staircase affects A〔第十次连续〕·"
    "W262 冻结方禁假设 staircase A-base==prior-B-tail+1 或 B-base==own-A-tail+1 恒等·须重读 live trace·注册 W261 B 带将拒 naive W262 A 窗仅当重叠"
    "——**W262 freezer 承接面强制注记：须在 post-W261 宇宙重 derive 且 derive B 时预留本波 A 窗·W141 先例·never transcribe r587**）"
)

NEW["b8_selftest"] = (
    "selftest W261 face（A=staircase-hop honest-walk past the registered prior-wave B band 断言"
    "（A_hop_chain 与 probe 回执逐跳恒等·A 第十次连续跳=W239 staircase era 后承袭如实注记·A 落位不落任何已注册带内）"
    "·B=own-A reservation 1-hop lands-above-own-A 断言（B_hop_chain 与 probe 回执逐跳恒等·B 落位不落本波 A 窗内=同窗互斥断言·第十一次连续 above-own-A 如实注记）·W260 行 parity 腿"
    "**estate 提取面注记**：冻结拼接脚本的 parity estate（W138..W206 69 行 full-span·r858 absorb 代）从**本机 W260 块物理字节**提取"
    "（结构已知·提取自证断言 69 行 range 恒等在场）——W260 块的自有 W243..W259 legs（17 行）不入 estate 路径"
    "·提取后新增 W243..W260 leg（18 行）构成 W261 块 parity 119 行" + WL + "·零假设零风险。"
)

# marker pairs: (block, start_marker, end_marker) -- needles matched on T1 (post-roll faces)
BLOCKS = [
    ("b_band_ab", "（**A 面=STAIRCASE-AFFECTS-A", "已如实披露非分叉）"),
    ("b3_a_bandface", "法典 §4 W261 行 A=587_301..589_300", "非转录 r587·ADMIT 回执在场）"),
    ("b3_b_bandface", "法典 §4 W261 行 B=589_301..589_500", "披露收敛·ADMIT 回执在场）"),
    ("b5_projection", "5. **W261+ 投影（probe 机证 leg4", "verify at W261 prereg，hop 链逐跳在 probe 回执。"),
    ("b7_claim_projection", "·probe W261+ 投影 A naive 589_301..591_300 CLEAN hops=0", "never transcribe r587**）"),
    ("b6_ram", "·W261 冻结窗 2G bm-c 实锚", "W240 冻结窗 33.2G bm-a 实锚）"),
    ("b8_selftest", "selftest W261 face（", "零假设零风险。"),
    ("b1_chain_tail", "+W246=bm-a r1016 prereg derive", "W261 freezer 承接面）】。"),
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
    "PERPETUAL-N1-W261", "research/PERPETUAL_N1_W261_PREREG.md",
    "589_501..591_500", "591_501..591_700", "996,335", "569,920", "572,120",
    "n1_w261_results.json", "MSG-20261017-1225-bmc-w261-seat", "cf23c4553",
    "第 259 枚", "第八十一枚", "第 251 波", "第 81 枚",
    "STAIRCASE-AFFECTS-A", "第十次连续 A-hop", "第十一次连续 above-own-A",
    "_w261bmc_20261017", "--wave 261", "波号 261",
    "W260=bm-c r1065 prereg derive", "r1065 finalize one-pass",
    "n_eff_held_equal 994,135", "−0.09273073", "0.24503935", "−0.09156055",
    "（**0.3292** 实测锚）", "bm-c 循环班 r1066 freeze 窗", "本窗 free RAM ~11GB",
    "→W249 **0.000332**→W250 **0.000331**→W251 **0.000330**→W252 **0.000330**→W253 **0.000329**→W254 **0.000328**→W255 **0.000328**→W256 **0.000327**→W257 **0.000326**→W258 **0.000326**→W259 **0.000325**→W260 **0.000325**】",
    "queue-head FREEZE-UNBLOCKED lane", "seed_admit_gate rc0 双带 FREE",
    "A base=589501", "B base=591501",
    "bm-c r1065 W260 §7 范式", "bm-c r1065 W260 §8 范式",
    "W262 freezer 承接面", "verify at W262 prereg",
    "selftest W261 face", "W243..W260 leg（18 行）构成 W261 块 parity 119 行",
    "键 W260 实测 K-lift **0.0000**", "line_merged@K569,920 **1.195**", "line_pre_w260 1.195",
    "实差 0.0012 在带内", "已落账键·12:1x", "bm-c r1065 窗 12:1x",
    "r1065/W260 先例 freeze-prep 同式", "258 行单态", "probe leg0 机证 258 行",
    "_w261bmc_freeze_edits", "_w260bmc_freeze_edits", "本波上游链=W1..W260 finalize 全落地",
    "engine_owner==bm-c 80 行注册", "bmc rows 80", "bmc_rows=80",
    "queue-head FREEZE-UNBLOCKED 承接", "A 落位 base==注册前波 B 尾+1（589_500+1）",
    "B 落位 base==本波 A 窗尾+1（591_500+1）",
    "W260 块的自有 W243..W259 legs（17 行）",
    "bm-c r1065 席位", "bm-c r1065 席·queue-head FREEZE-UNBLOCKED 发布",
    "post-W260-REGISTERED 终态注册", "席位窗 probe leg0 实测 258 行",
    "W243/W246/W248/W249/W250/W251/W252/W253/W254/W255/W256/W257/W258/W259/W260 低 RAM 实烧先例", "·W261 冻结窗 11G bm-c 实锚",
    "本候选=bm-c 自有席自有波", "R262：W261 带从未指派",
    "B_hop lands-inside-A=false", "B_lands_above_own_A=true", "A_staircase_hop_past_W260_B=true",
    "§5.5 W262+ 投影承接机证", "exit rng=**591_501+j**", "B-ext exit seed=591_501..591_700",
    "A-ext seed=589_501..591_500",
    "probe leg0 bmc_rows=80 attempt-continuity face（r1065 窗算法·bm-c own seat+bmc live rows 80 实读）",
    "589_301..591_300", "589_501..589_700", "591_501..593_500", "591_701..591_900",
    "A_clean_at_naive_start=false",
    "表尾 W260 行", "pre-W261 全二百五十八行注册 N1 带表", "共二百五十八面实测",
    "engine_owner 行 250 注册在册", "freeze 窗 live derive 258 行单态 owner rows 250",
    "W260 splice 先于席位窗已落地",
    "W260 own-wave finalize 已落=席位时即解锁",
    "n1_w260_results.json",
    "31d5dc07baee6620", "f40a82c450f32c5a", "87a4c206a35e0584", "0f33f9abc", "e8a9d5d67", "63ef15c4f", "9598cf5cb",
    "bfd877ee61d6b456", "57a139af18df580d", "dca9e66660f0c4ac",
    "89aeea31b", "b709bc2cc", "824b46d31", "37ccebffd", "122485949", "cc72046d7",
    "sixgate PRE-FINALIZE 22nd consecutive",
    "（r1065 席位窗实跑", "（bm-c r1065 席",
    "zero post-splice heal", "（W138..W206+",
    "W252/W253/W254/W255/W256/W257/W258/W259/W260/W261=A/B 双 1-hop 形态连续十波",
    "W262p_B_lands_inside_W262p_A_naive",
]
for s in MUST:
    assert s in T2, "MUST-HAVE missing: %r" % s

MUST_NOT = [
    "**A-ext seed=587_301", "571_901", "571_900", "567_501", "567_500", "545_301", "545_300", "545_500", "565_501",
    "FIRST-CLEAN·hops=0", "13-HOP", "13 hops", "A_hop_chain=[] 空集", "A_clean_at_naive_start=true",
    "573_901..574_100", "573_900", "573_901", "574_101..574_300", "576_101..578_100", "576_301..576_500",
    "578_501..578_700", "578_301..580_300",
    "−0.09241377", "0.24503097", "**0.3092**", "实差 0.0003 在带内",
    "−0.09275554", "0.24502959", "−0.10688227", "**0.2973**", "实差 0.0141 在带内",
    "−0.09276683", "0.24503366", "−0.09565814", "**0.3108**", "实差 0.0029 在带内",
    "−0.09273526", "0.24503750", "−0.08462", "**0.3234**", "实差 0.0081 在带内",
    "line_merged@K563,320", "line_merged@K565,520", "line_merged@K567,720", "556,720 合并池", "累计 null 池=556,720",
    "563,320 合并池", "567,720 合并池",
    "cb79242ed", "MSG-20261016-22xx", "bmc-w255-seat", "第 76 枚", "第七十六枚", "第 253 枚", "第 245 波",
    "第 75 枚", "第 77 枚", "第七十七枚", "第 78 枚", "第七十八枚", "第 255 枚", "第 256 枚",
    "第 257 枚", "第 258 枚", "第 249 波", "第 250 波", "第七十九枚", "第 79 枚", "第八十枚自有波", "第 80 枚",
    "engine_owner 行 244", "owner rows 244", "bmc rows 74", "bmc_rows=74", "engine_owner==bm-c 74",
    "engine_owner 行 246", "owner rows 246", "bmc rows 76", "bmc_rows=76", "engine_owner==bm-c 76",
    "engine_owner 行 247", "owner rows 247", "bmc rows 77+候选", "bmc_rows=77", "engine_owner==bm-c 77",
    "engine_owner 行 248 注册在册", "owner rows 248", "bmc rows 78+候选", "bmc_rows=78", "engine_owner==bm-c 78 行注册",
    "engine_owner 行 249 注册在册", "owner rows 249", "bmc rows 79+候选", "bmc_rows=79", "engine_owner==bm-c 79 行注册",
    "probe leg0 bmc_rows=78", "probe leg0 bmc_rows=79",
    "252 行", "二百五十二行注册", "二百五十二面实测", "251 行", "二百五十一行注册", "二百五十一面实测",
    "253 行单态", "机证 253 行", "实测 253 行", "254 行单态", "机证 254 行", "实测 254 行",
    "255 行单态", "机证 255 行", "实测 255 行", "256 行单态", "机证 256 行", "实测 256 行",
    "257 行单态", "机证 257 行", "实测 257 行", "席位窗 probe leg0 实测 257 行",
    "全二百五十六行注册 N1 带表", "共二百五十六面实测", "pre-W259 全二百五十六行注册",
    "全二百五十七行注册 N1 带表", "共二百五十七面实测", "pre-W260 全二百五十七行注册",
    "r1060 窗算法", "（bm-c r1060 席", "（r1060 席位窗实跑", "r1064 窗算法", "（bm-c r1064 席", "（r1064 席位窗实跑",
    "bm-c r1060 窗", "bm-c r1064 窗", "bm-c 循环班 r1063 freeze 窗", "bm-c 循环班 r1065 freeze 窗", "live-read r1063", "live-read r1065", "已落账键·05:1x finalize one-pass",
    "波号 259", "--wave 259", "波号 260", "--wave 260", "R260：W259", "R261：W260",
    "verify at W260 prereg", "verify at W261 prereg", "W260 freezer 承接面", "W261 freezer 承接面", "W260p_", "W261p_", "W260 冻结方", "W261 冻结方",
    "键 W257 实测 K-lift", "键 W253 实测 K-lift", "键 W254 实测 K-lift", "键 W255 实测 K-lift", "键 W256 实测 K-lift", "键 W258 实测 K-lift", "键 W259 实测 K-lift",
    "line_pre_w253", "line_pre_w254", "line_pre_w255", "line_pre_w256", "line_pre_w257", "line_pre_w258", "line_pre_w259 1.1949",
    "（**B 面=CLEAN", "waits-upstream ARMED",
    "（bm-c r1043 席", "第 75 枚",
    "selftest W259 face", "selftest W260 face", "本窗 free RAM ~1.3GB",
    "本窗 free RAM ~2GB（bm-c 底盘常驻·24G 物理内存机·LLM 态 27b 常驻+引擎队列空转·CPU 车道独立如实注记）",
    "第四次连续 A-hop", "第五次连续 A-hop", "第五次连续 above-own-A", "第四次连续 above-own-A",
    "第六次连续 A-hop", "第六次连续 above-own-A", "第七次连续 A-hop", "第七次连续", "第七次连续 above-own-A", "第六次连续",
    "第八次连续 A-hop", "第八次连续 above-own-A", "第八次连续",
    "第九次连续 A-hop", "第九次连续 above-own-A", "第九次连续",
    "第十次连续 above-own-A",
    "571_901..573_900", "573_901..575_900",
    "·W255 冻结窗 2.0G", "·W256 冻结窗 3.3G", "·W257 冻结窗 4G", "·W258 冻结窗 3.5G", "·W259 冻结窗 1.3G", "·W260 冻结窗 2G bm-c 实锚",
    "_w255bmc_20261016", "_w255bmc_20261017", "_w256bmc_20261016", "_w256bmc_20261017", "_w257bmc_20261017", "_w259bmc_20261016", "_w260bmc_20261016",
    "MSG-20261017-0517-bmc-w258-seat", "MSG-20261017-0704-bmc-w259-seat", "MSG-20261017-0910-bmc-w260-seat", "d0d0d04a4", "16dba0e70", "27ee6e95a", "9fa2c8aed",
    "（bm-c r1062 席", "（r1062 席位窗实跑", "bm-c r1062 窗", "r1062 窗算法",
    "998,535",
    "584_901..586_900", "585_101..585_300",
    "582_701..584_700", "582_901..583_100",
    "571_901..573_900",
    "587_101..589_100", "587_301..587_500",
    "W259p_B_lands_inside_W259p_A_naive", "W260p_B_lands_inside_W260p_A_naive", "W261p_B_lands_inside_W261p_A_naive",
]
for s in MUST_NOT:
    assert s not in T2, "MUST-NOT-HAVE present: %r (count=%d)" % (s, T2.count(s))

# pinned positive count gate (r1063 canon continuation): the CORRECT rolled W261 pre-pool faces
assert T2.count("569,920 合并池") == 3, "569,920 合并池 count=%d (expect 3 = §0+§4+§5 rolled pre-pool faces)" % T2.count("569,920 合并池")

# projection-fulfillment count gates
assert T2.count("W261+ 投影") == 0, "W261+ 投影 count=%d (expect 0)" % T2.count("W261+ 投影")
assert T2.count("W262+ 投影") == 4, "W262+ 投影 count=%d (expect 4 = b1 tail + b5 title + b7 claim + sec8 rolled)" % T2.count("W262+ 投影")
assert T2.count("hops=1") == 2, "hops=1 count=%d (expect 2 = 带位 A + §3 A)" % T2.count("hops=1")
assert T2.count("hops=0") == 5, "hops=0 count=%d (expect 5 = b5 x2 + b7 x3)" % T2.count("hops=0")
assert T2.count("第九次连续") == 0, "第九次连续 count=%d (expect 0)" % T2.count("第九次连续")
assert T2.count("第八次连续") == 0, "第八次连续 count=%d (expect 0)" % T2.count("第八次连续")
assert T2.count("第八次连续 A-hop") == 0, "第八次连续 A-hop count=%d (expect 0)" % T2.count("第八次连续 A-hop")
assert T2.count("第九次连续 A-hop") == 0, "第九次连续 A-hop count=%d (expect 0 = block-replaced/rolled)" % T2.count("第九次连续 A-hop")
assert T2.count("第十次连续 A-hop") == 3, "第十次连续 A-hop count=%d (expect 3 = b_band_ab x2 + b3_a x1 own faces)" % T2.count("第十次连续 A-hop")
assert T2.count("第十一次连续 A-hop") == 3, "第十一次连续 A-hop count=%d (expect 3 = b5 pre-registered face x2 + b7 projection face)" % T2.count("第十一次连续 A-hop")
print("DBG-ORDINALS: 第九次连续=%d 第十次连续=%d 第十一次连续=%d 第十次连续A-hop=%d 第十一次连续A-hop=%d 第十次连续above=%d 第十一次连续above=%d 连续十波=%d 连续九波=%d" % (
    T2.count("第九次连续"), T2.count("第十次连续"), T2.count("第十一次连续"),
    T2.count("第十次连续 A-hop"), T2.count("第十一次连续 A-hop"),
    T2.count("第十次连续 above-own-A"), T2.count("第十一次连续 above-own-A"),
    T2.count("连续十波"), T2.count("连续九波")))
assert T2.count("第十次连续") == 5, "第十次连续 count=%d (expect 5 = A-hop x3 + b8 第十次连续跳 x1 + 〔第十次连续〕 x1)" % T2.count("第十次连续")
assert T2.count("第十一次连续") == 7, "第十一次连续 count=%d (expect 7 = A-hop x3 + above-own-A x3 + 〔第十一次连续〕 x1)" % T2.count("第十一次连续")
assert T2.count("第十次连续 above-own-A") == 0, "第十次连续 above-own-A count=%d (expect 0 = block-replaced)" % T2.count("第十次连续 above-own-A")
assert T2.count("第十一次连续 above-own-A") == 3, "第十一次连续 above-own-A count=%d (expect 3 = b_band_ab x1 + b3_b x1 + b7 x1)" % T2.count("第十一次连续 above-own-A")
assert T2.count("连续九波") == 0, "连续九波 count=%d (expect 0 = superseded by 十波)" % T2.count("连续九波")
assert T2.count("连续十波") == 1, "连续十波 count=%d (expect 1 = b5 NEW 10-wave face)" % T2.count("连续十波")
assert T2.count("582_901..583_100") == 0, "582_901..583_100 count=%d (expect 0 = block-replaced)" % T2.count("582_901..583_100")
assert T2.count("582_701..584_700") == 0, "582_701..584_700 count=%d (expect 0 = block-replaced)" % T2.count("582_701..584_700")
assert T2.count("584_901..586_900") == 0, "584_901..586_900 count=%d (expect 0 = block-replaced prior-wave naive A)" % T2.count("584_901..586_900")
assert T2.count("585_101..585_300") == 0, "585_101..585_300 count=%d (expect 0 = block-replaced prior-wave B naive)" % T2.count("585_101..585_300")
assert T2.count("589_301..591_300") == 4, "589_301..591_300 count=%d (expect 4 = b_band_ab x3 [续带 + hop-chain verbatim + 投影兑现 quote] + b3_a x1)" % T2.count("589_301..591_300")
assert T2.count("589_501..589_700") == 4, "589_501..589_700 count=%d (expect 4 = b_band_ab x3 [B naive 续带 + 落 A 窗内 + 投影兑现 tail] + b3_b x1)" % T2.count("589_501..589_700")
assert T2.count("578_501..578_700") == 0, "578_501..578_700 count=%d (expect 0)" % T2.count("578_501..578_700")
assert T2.count("578_301..580_300") == 0, "578_301..580_300 count=%d (expect 0)" % T2.count("578_301..580_300")
assert T2.count("576_101..578_100") == 0, "576_101..578_100 count=%d (expect 0)" % T2.count("576_101..578_100")
assert T2.count("576_301..576_500") == 0, "576_301..576_500 count=%d (expect 0)" % T2.count("576_301..576_500")

# diagnostics (non-fatal; prior-wave band faces legitimately referenced in NEW blocks + HIST_B1)
print("diag counts: 587_301..589_300=%d 589_301..589_500=%d 585_101..587_100=%d 587_101..587_300=%d (prior-wave band refs in NEW blocks + HIST legs)" % (
    T2.count("587_301..589_300"), T2.count("589_301..589_500"), T2.count("585_101..587_100"), T2.count("587_101..587_300")))
print("diag counts: 07:0x=%d 05:1x=%d 08:5x=%d 12:1x=%d (b1-HIST verbatim + current finalize window)" % (
    T2.count("07:0x"), T2.count("05:1x"), T2.count("08:5x"), T2.count("12:1x")))

# residue scan: all X_Y..X_Y windows well-formed
for m in re.finditer(r"(\d{3}_\d{3})\.\.(\d{3}_\d{3})", T2):
    lo = int(m.group(1).replace("_", "")); hi = int(m.group(2).replace("_", ""))
    assert lo <= hi, "malformed window %s" % m.group(0)

io.open(OUT, "w", encoding="utf-8", newline="").write(T2)
print("W261 PREREG DERIVE OK -> %s (%d bytes, %d lines)" % (OUT, len(T2.encode("utf-8")), T2.count("\n") + 1))
print("freeze window face: bm-c 循环班 r1066 freeze 窗 2026-10-17 " + FREEZE_T)
print("blocks replaced: %s" % ", ".join(n for n, _, _ in BLOCKS))
print("vmap legs: %d floors: %d post-legs: %d MUST: %d MUST_NOT: %d" % (len(VMAP), len(VMAP_FLOORS), len(VMAP_POST_LEGS), len(MUST), len(MUST_NOT)))
print("src blob-verified == a7d34500ae5a3b3cd6a983f03c7dd32455598649 @ 0f33f9abc (frozen pre-run face; HEAD post-backfill twin 4c684526 disclosed, NOT used)")
print("out sha256_16: %s" % hashlib.sha256(T2.encode("utf-8")).hexdigest()[:16])
