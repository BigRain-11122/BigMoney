# -*- coding: utf-8 -*-
# r1059 bm-c: W257 prereg derive (count-asserted ordered transform + marker-extracted block replaces).
# Canon-clone of _w256bmc_prereg_derive.py per age() machine-needle law (shift-map one generation).
# Source = committed frozen W256 prereg AT THE FREEZE COMMIT 5996e2c93 (git 5996e2c93:research/PERPETUAL_N1_W256_PREREG.md,
# 41,952 bytes -- the frozen pre-run face; sec7/8 placeholders intact). Extracted to
# results/_w257bmc_w256_frozen_face.txt THIS window via python subprocess bytes (blob 4503bf5d92d69c2a409dc2074a300140f7bfdcb9,
# byte-verified hash-object == rev-parse @ 5996e2c93; sha256_16 01685277539b98be measured by the pre-flight probe).
# TEMPLATE-FACE DISCLOSURE (needle-face divergence, honest): HEAD twin 2fb6747e43eb3bb1b952b021d33e7be964a708c5 = the
# CURRENT HEAD face = the POST-CYCLE face with sec.7/8 BACKFILLED by the r1058 window (W256 actual results).
# Deriving from the backfilled face would fabricate W257 sec.7/8 "跑后实证" from W256's measured numbers -- the
# r1049/r1052/r1056/r1058 precedent (derive always from the PRIOR wave's FREEZE-COMMIT face, "frozen pre-run face;
# sec7/8 placeholders intact") and the prereg semantics both require 4503bf5d. Both faces measured this window
# (rev-parse 5996e2c93:=4503bf5d / HEAD:=2fb6747e); divergence disclosed in header + closeout;
# 2fb6747e recorded as the post-backfill twin, NOT used as template.
# W257 facts (all machine-derived, never transcribed):
#   - seat probe ADMIT receipt results/_w257bmc_20261017_probe_receipt.json (r1058 continuation window, seat rides
#     origin 27ee6e95a per r565 early-visibility law, MSG-20261017-03xx-bmc-w257-seat landed in fleet/inbox/).
#     STAIRCASE CONTINUES: A naive 580_501..582_500 REFUSED at start (registered W256 B band 580_501..580_700 sits INSIDE
#     the naive A window) -> A first-clean 580_701..582_700 hops=1 (SIXTH consecutive A-hop, W256 prereg sec.5 item5
#     A-CLEAN-at-naive pre-W256-universe projection superseded live r587, divergence disclosed) / B naive
#     580_701..580_900 REFUSED at start (lands INSIDE the own-wave W257 A first-clean window 580_701..582_700) ->
#     own-A reservation cascade hop past 582_700 -> 582_701..582_900 hops=1 (SEVENTH consecutive above-own-A landing);
#     seed_admit FREE x2 (A base=580701 span=2000 / B base=582701 span=200); leg0 rows=254 owner_rows=246
#     bmc_rows=76 bmc_ordinal=77 ordinal=247; leg2 conflicts=0; leg3 origin_vacancy=true;
#     leg4 W258+ projection: A naive 582_701..584_700 CLEAN hops=0 BUT post-W257-REGISTERED the naive W258 A
#     start 582_701 is REFUSED by the registered W257 B band 582_701..582_900 (SEVENTH consecutive A-hop expected)
#     AND the W258 B naive 582_901..583_100 lands inside the own-A reservation face.
#   - upstream W256 finalize landed (r1058 continuation window estate machine-verified, ledger 985,335+2,200=987,535 EXACT):
#     merged K=561,120 / merged mu -0.09270015433418877 / sigma 0.24503834821648132 / se_mu@K561,120 0.000327
#     narrowing-resumed / W256-only mu -0.090659 / A p95 0.3107 / K-lift 0.0000 in-band / n_eff_held 985,335 /
#     line_pre_w256 1.1947 / line_merged@561,120 1.1947 / own-slice vs pre-wave merged gap 0.0020412 in-band<0.02
#     (results/perpetual_faces/n1_w256_results.json + results/_r1058bmc_w256_fivekeys.json, all six keys PASS)
#   - W256 chain: prereg freeze 5996e2c93 LANDED by dead window self-labeled r1058 (49th-gen absorb verified) +
#     five-face freeze splice r1058-dead-window LANDED aa6102e35 (dual-sha16 pf d4a9d7164ba9490e->ad9776287dd52280 /
#     n1 c6dfb4291c09be1e->986e9162b86e0c7f; W256 block parity 114 rows; 3 disclosed needle heals caught PRE-splice) +
#     engine self-burn 12/12 (ledger appends 31c9e4872+1c7112fd9 batched 6+6 self-committed) + r1058 continuation
#     sixgate PRE-FINALIZE 18th consecutive (triple identity n1 986e9162b86e0c7f / pf ad9776287dd52280 @ aa6102e35) +
#     finalize one-pass 987,535/K=561,120 + fivekeys 6/6 + sec.7/8 backfilled + W257 seat published 27ee6e95a.
# Needle-count pre-flight evidence: results/_w257bmc_needle_probe.py (THIS window, ALL floors below measured live
# on T0 by the probe -- results/_w257bmc_needle_counts.txt; counts match every VMAP_FLOORS entry below).
# Same-window needle heals disclosed: NONE so far (all floors pre-verified by the probe before authoring; the
# receipt-date face is date-STABLE this generation 10-17->10-17 -- no date-roll leg needed, chained basename roll
# _w256bmc_20261017 -> _w257bmc_20261017 supplies the actual on-disk receipt filename).
# RAM face: this r1059 freeze window live-measures ~4G free (Win32_OperatingSystem FreePhysicalMemory round 1dp
# at 04:1x; 27b LLM still resident per gpu_mem_used 14.6G/16G + engine queue empty live-read this window
# -- honest face carried).
import io, os, sys, datetime, subprocess, hashlib, re

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(REPO, "results", "_w257bmc_w256_frozen_face.txt")
OUT = os.path.join(REPO, "research", "PERPETUAL_N1_W257_PREREG.md")
GIT = "C:/Program Files/Git/cmd/git.exe"

# --- source byte-identity gates ---
_blob_expect = "4503bf5d92d69c2a409dc2074a300140f7bfdcb9"   # freeze-commit face @ 5996e2c93
_ho = subprocess.run([GIT, "hash-object", SRC], capture_output=True, text=True, cwd=REPO).stdout.strip()
assert _ho == _blob_expect, "SRC blob mismatch: got %s expect %s" % (_ho, _blob_expect)
_fc = subprocess.run([GIT, "rev-parse", "5996e2c93:research/PERPETUAL_N1_W256_PREREG.md"],
                     capture_output=True, text=True, cwd=REPO).stdout.strip()
assert _fc == _blob_expect, "freeze-commit blob mismatch: got %s expect %s" % (_fc, _blob_expect)
_hb = subprocess.run([GIT, "rev-parse", "HEAD:research/PERPETUAL_N1_W256_PREREG.md"],
                     capture_output=True, text=True, cwd=REPO).stdout.strip()
assert _hb == "2fb6747e43eb3bb1b952b021d33e7be964a708c5", "HEAD tpl twin face drifted: %s" % _hb

T0 = io.open(SRC, encoding="utf-8", newline="").read()
assert hashlib.sha256(T0.encode("utf-8")).hexdigest()[:16] == "01685277539b98be", "SRC sha mismatch"

P1, P2, P3 = "\x01W\x01", "\x01N\x01", "\x01B\x01"

now = datetime.datetime.now()
FREEZE_T = "%02d:%dx" % (now.hour, now.minute // 10)

# machine-extracted historical spans (from T0 PRE-roll bytes: zero transcription for carried content)
_i_b1 = T0.index("+W246=bm-a r1016 prereg derive")
_j_b1 = T0.index("——本波上游链=")
HIST_B1 = T0[_i_b1:_j_b1]  # W246..W255 chain legs verbatim (frozen template bytes)
_i_b6 = T0.index("·W250 冻结窗 RAM 未记录（r1046 死窗")
_b6_end = "W240 冻结窗 33.2G bm-a 实锚）"
_j_b6 = T0.index(_b6_end) + len(_b6_end)
HIST_B6 = T0[_i_b6:_j_b6]  # W250..W240 freeze-window RAM ledger verbatim

VMAP = [
    # projection first, then line_merged face, then prior-K bare, then ledger heads (order-critical)
    ("561,120 投影", "563,320 投影"),
    ("line_merged@K558,920 **1.1946**", "line_merged@K561,120 **1.1947**"),
    ("558,920", "561,120"),
    ("985,335", "987,535"),
    ("983,135", "985,335"),
    # sec5 measured keys -> W256 measured faces (n1_w256_results.json machine values)
    ("−0.09270819", "−0.09270015"),
    ("−0.08525445", "−0.090659"),
    ("0.24503942", "0.24503835"),
    ("实差 0.0075 在带内", "实差 0.0020 在带内"),
    ("（**0.3422** 实测锚）", "（**0.3107** 实测锚）"),
    # band values outside block regions (staircase-6th-hop + own-A reservation cascade faces)
    ("A-ext seed=578_501..580_500", "A-ext seed=580_701..582_700"),
    ("entry rng seed=**578_501+j**", "entry rng seed=**580_701+j**"),
    ("entry rng=**578_501+j**", "entry rng=**580_701+j**"),
    ("exit rng=**580_501+j**", "exit rng=**582_701+j**"),
    ("A base=578501 span=2000 checked=2000 verdict=FREE", "A base=580701 span=2000 checked=2000 verdict=FREE"),
    ("B base=580501 span=200 checked=200 verdict=FREE", "B base=582701 span=200 checked=200 verdict=FREE"),
    ("R257：W256", "R258：W257"),
    # base-relation faces (block-external occurrences; block NEW uses the same new faces)
    ("578_500+1", "580_700+1"),
    ("580_500+1", "582_700+1"),
    # seat / provenance faces (W257 seat published r1058 window, rides origin 27ee6e95a)
    ("MSG-20261017-023x-bmc-w256-seat", "MSG-20261017-03xx-bmc-w257-seat"),
    ("fd48643c9", "27ee6e95a"),
    ("（bm-c r1057 席·queue-head FREEZE-UNBLOCKED 发布）", "（bm-c r1058 席·queue-head FREEZE-UNBLOCKED 发布）"),
    ("（bm-c r1057 席位", "（bm-c r1058 席位"),
    ("（r1057 席位窗实跑", "（r1058 席位窗实跑"),
    # finalize window faces (specific first, then catch-all)
    ("bm-c r1057 窗 02:3x", "bm-c r1058 窗 03:5x"),
    ("02:3x", "03:5x"),
    # engine live-read + RAM head (bm-c current window honest: ~4G free live-measured THIS r1059 freeze window;
    # 27b LLM resident per O-20261016-2347 GPU dual-mode + engine queue empty live-read this window)
    ("saturation_engine.py status live-read r1058", "saturation_engine.py status live-read r1059"),
    ("本窗 free RAM ~3.3GB（bm-c 底盘常驻·24G 物理内存机·LLM 态 27b 常驻+引擎队列空转·CPU 车道独立如实注记）",
     "本窗 free RAM ~4GB（bm-c 底盘常驻·24G 物理内存机·LLM 态 27b 常驻+引擎队列空转·CPU 车道独立如实注记）"),
    # wave-number roll (chained placeholders)
    ("W256", P1), ("W255", "W256"), ("W254", "W255"), ("W253", "W254"), ("W252", "W253"), ("W251", "W252"), (P1, "W257"),
    # result-file names (chained)
    ("n1_w256", P2), ("n1_w255", "n1_w256"), ("n1_w254", "n1_w255"), (P2, "n1_w257"),
    # probe/freeze script basenames (chained; current face _w257bmc <- template _w256bmc; date-STABLE 10-17->10-17)
    ("_w256bmc", P3), ("_w255bmc", "_w256bmc"), (P3, "_w257bmc"),
    # runner CLI wave
    ("--wave 256", "--wave 257"),
    ("波号 256", "波号 257"),
    # pool/engine ordinals
    ("第 254 枚", "第 255 枚"),
    ("第 246 波", "第 247 波"),
    ("bm-c 第七十六枚自有波", "bm-c 第七十七枚自有波"),
    # subsumption-order fix: compound needle contains 第 76 枚 -> MUST run before any bare roll
    ("bmc rows 75+候选=第 76 枚 EXACT", "bmc rows 76+候选=第 77 枚 EXACT"),
    ("第 76 枚", "第 77 枚"),
    ("probe leg0 bmc_rows=75 attempt-continuity face（r1057 窗算法·bm-c own seat+bmc live rows 75 实读）",
     "probe leg0 bmc_rows=76 attempt-continuity face（r1058 窗算法·bm-c own seat+bmc live rows 76 实读）"),
    ("engine_owner==bm-c 75 行注册", "engine_owner==bm-c 76 行注册"),
    ("engine_owner 行 245 注册在册", "engine_owner 行 246 注册在册"),
    # registry scan faces
    ("全二百五十三行注册 N1 带表", "全二百五十四行注册 N1 带表"),
    ("freeze 窗 live derive 253 行单态 owner rows 245", "freeze 窗 live derive 254 行单态 owner rows 246"),
    ("probe leg0 机证 253 行〔", "probe leg0 机证 254 行〔"),
    ("席位窗 probe leg0 实测 253 行〔", "席位窗 probe leg0 实测 254 行〔"),
    ("perpetual_faces.py 零 254 行", "perpetual_faces.py 零 255 行"),
    ("共二百五十三面实测", "共二百五十四面实测"),
    # sec8 placeholder projection-label bump (W257+ -> W258+ face)
    ("§5.5 W257+ 投影承接机证", "§5.5 W258+ 投影承接机证"),
]

VMAP_FLOORS = {
    "561,120 投影": 1, "line_merged@K558,920 **1.1946**": 1,
    "558,920": 7, "985,335": 3, "983,135": 2, "980,935": 1,   # 980,935 = b1-HIST-region historical head, preserved verbatim
    "−0.09270819": 1, "−0.08525445": 1, "0.24503942": 1, "实差 0.0075 在带内": 1,
    "（**0.3422** 实测锚）": 1,
    "A-ext seed=578_501..580_500": 1,
    "entry rng seed=**578_501+j**": 1, "entry rng=**578_501+j**": 1,
    "exit rng=**580_501+j**": 1,
    "A base=578501 span=2000 checked=2000 verdict=FREE": 1,
    "B base=580501 span=200 checked=200 verdict=FREE": 1,
    "R257：W256": 1,
    "W256": 33, "W255": 67, "W254": 8, "W253": 7, "W252": 9, "W251": 8, "W257": 18,
    "n1_w256": 4, "n1_w255": 3, "n1_w254": 1, "_w256bmc": 4, "_w255bmc": 1,
    "_w256bmc_20261017": 3,
    "--wave 256": 2, "波号 256": 1,
    "第 254 枚": 1, "第 246 波": 1, "bm-c 第七十六枚自有波": 1,
    "bmc rows 75+候选=第 76 枚 EXACT": 2, "第 76 枚": 2,
    "probe leg0 bmc_rows=75 attempt-continuity face（r1057 窗算法·bm-c own seat+bmc live rows 75 实读）": 1,
    "engine_owner==bm-c 75 行注册": 1, "engine_owner 行 245 注册在册": 1,
    "全二百五十三行注册 N1 带表": 1,
    "freeze 窗 live derive 253 行单态 owner rows 245": 1,
    "probe leg0 机证 253 行〔": 1, "席位窗 probe leg0 实测 253 行〔": 1,
    "perpetual_faces.py 零 254 行": 1,
    "共二百五十三面实测": 1,
    "MSG-20261017-023x-bmc-w256-seat": 4, "fd48643c9": 3,
    "（bm-c r1057 席·queue-head FREEZE-UNBLOCKED 发布）": 1,
    "（bm-c r1057 席位": 1, "（r1057 席位窗实跑": 1,
    "bm-c r1057 窗 02:3x": 1, "02:3x": 4, "已落账键·02:3x": 1,
    "saturation_engine.py status live-read r1058": 1,
    "本窗 free RAM ~3.3GB（bm-c 底盘常驻·24G 物理内存机·LLM 态 27b 常驻+引擎队列空转·CPU 车道独立如实注记）": 1,
    "§5.5 W257+ 投影承接机证": 1,
    "578_500+1": 4, "580_500+1": 2,
    # block-marker stability floors (raw template face; T1 marker = post-roll form asserted in BLOCKS)
    "（**A 面=STAIRCASE-AFFECTS-A": 1,
    "已如实披露非分叉）": 1,
    "法典 §4 W256 行 A=578_501..580_500": 1,
    "法典 §4 W256 行 B=580_501..580_700": 1,
    "披露收敛·ADMIT 回执在场）": 1,
    "非转录 r587·ADMIT 回执在场）": 1,
    "5. **W257+ 投影（probe 机证 leg4": 1,
    "verify at W257 prereg，hop 链逐跳在 probe 回执。": 1,
    "·probe W257+ 投影 A naive 580_501..582_500 CLEAN hops=0": 1,
    "never transcribe r587**）": 1,
    "·W256 冻结窗 3.3G bm-c 实锚": 1,
    "W240 冻结窗 33.2G bm-a 实锚）": 1,
    "·W250 冻结窗 RAM 未记录（r1046 死窗": 1,
    "selftest W256 face（": 1, "零假设零风险。": 1,
    "+W246=bm-a r1016 prereg derive": 1,
    "——本波上游链=": 1,
    "W256 freezer 承接面）】。": 0,
    "W257 freezer 承接面）】。": 1,
    "W243/W246/W248/W249/W250/W251/W252/W253/W254/W255 低 RAM 实烧先例": 1,
    "r1056/W255 先例 freeze-prep 同式": 1,
    "→W249 **0.000332**→W250 **0.000331**→W251 **0.000330**→W252 **0.000330**→W253 **0.000329**→W254 **0.000328**→W255 **0.000328**】": 1,
    "line_pre_w255 1.1945": 1,
    "bm-c r1057 W255 §7 范式": 1, "bm-c r1057 W255 §8 范式": 1,
    "键 W255 实测 K-lift **+0.0001**": 1,
    "n_eff_held_equal 983,135": 1,
    "queue-head FREEZE-UNBLOCKED lane": 1,
    "queue-head FREEZE-UNBLOCKED 承接": 1,
    "本候选=bm-c 自有席自有波": 1,
    "表尾 W255 行": 2,
    "pre-W256 全二百五十三行注册 N1 带表": 1,
    "bm-c 循环班 r1058 freeze 窗 2026-10-17": 1,
    "r1057 窗算法": 1,
    "W257+ 投影": 4, "STAIRCASE-AFFECTS-A": 2, "hops=1": 2, "hops=0": 5,
    "第五次连续 A-hop": 3, "第六次连续 A-hop": 3, "第六次连续": 7,
    "578_301..580_300": 4, "578_501..578_700": 4,
    "580_501..582_500": 5, "580_701..580_900": 3,
    "578_501..580_500": 11, "580_501..580_700": 10,
    "zero post-splice heal": 4,
    "924e87b3f02afb72": 3, "7b550e65716e0ada": 3,
    "d4a9d7164ba9490e": 2, "c6dfb4291c09be1e": 2,
    "e166afc6c": 2, "b1414b81a": 1, "f931cf102": 1, "72d292ea3": 1,
    "e2c4b543e": 2, "3eb691575": 1, "fa2bc55e5": 1, "c211d1269": 1,
    "（W138..W206+": 1,
    "PERPETUAL-N1-W256": 4,
    # zero-floors (absence assertions on T0)
    "waits-upstream ARMED": 0,
    "（**B 面=CLEAN": 0,
    "987,535": 0, "0.3107": 0, "563,320": 0,
    "−0.09270015": 0, "−0.090659": 0, "0.24503835": 0, "0.0020 在带内": 0,
    "580_701..582_700": 0, "582_701..582_900": 0, "582_701..584_700": 0, "582_901..583_100": 0,
    "580_700+1": 0, "582_700+1": 0,
    "A base=580701 span=2000 checked=2000 verdict=FREE": 0,
    "B base=582701 span=200 checked=200 verdict=FREE": 0,
    "R258：W257": 0, "n1_w257": 0, "_w257bmc": 0, "--wave 257": 0, "波号 257": 0,
    "第 77 枚": 0, "第 255 枚": 0, "第 247 波": 0, "bm-c 第七十七枚自有波": 0, "第 75 枚": 0,
    "第七次连续 A-hop": 0, "第七次连续": 0, "W258": 0,
    "27ee6e95a": 0, "（bm-c r1058 席": 0, "（r1058 席位窗实跑": 0, "03:5x": 0,
    "line_pre_w256": 0, "键 W256 实测 K-lift": 0, "bm-c r1058 W256 §7 范式": 0,
    "engine_owner==bm-c 76 行注册": 0, "engine_owner 行 246 注册在册": 0,
    "全二百五十四行注册 N1 带表": 0, "freeze 窗 live derive 254 行单态 owner rows 246": 0,
    "probe leg0 机证 254 行〔": 0, "席位窗 probe leg0 实测 254 行〔": 0,
    "perpetual_faces.py 零 255 行": 0, "共二百五十四面实测": 0,
    "§5.5 W258+ 投影承接机证": 0,
    "MSG-20261017-03xx-bmc-w257-seat": 0,
    "_w255bmc_20261016": 0, "_w255bmc_20261017": 0,
    "561,120": 1,  # only the 投影 compound; bare face absent (baseline rolls supply it)
}

# floors for POST-chain correction legs (needles exist only in T1 after the pre-chain legs run)
VMAP_POST_LEGS = [
    # se_mu narrowing chain: wave roll consumed the W251 label; restore it and append true W256 se 0.000327
    # (W256 key5 = narrowing-resumed after W255 held-flat, honest note carried in the replacement tail)
    # [needle-heal #1 same-window disclosure: T1 actual rolled form measured = W252..W256 with W251 consumed;
    #  first-authored needle assumed the W256-gen terminal shape and failed its floor -- corrected to the live form]
    ("→W249 **0.000332**→W250 **0.000331**→W252 **0.000330**→W253 **0.000330**→W254 **0.000329**→W255 **0.000328**→W256 **0.000328**】",
     "→W249 **0.000332**→W250 **0.000331**→W251 **0.000330**→W252 **0.000330**→W253 **0.000329**→W254 **0.000328**→W255 **0.000328**→W256 **0.000327**】", 1),
    # line_pre face: lowercase w-token escapes the uppercase W-roll (r1045 derive precedent);
    # W256 actual line_pre_w256 = 1.1947 (n1_w256_results.json skill_line machine value)
    ("line_pre_w255 1.1945", "line_pre_w256 1.1947", 1),
    # K-lift value face: wave roll W255->W256 relabeled the anchor; W256 true K-lift = 0.0000 in-band
    ("键 W256 实测 K-lift **+0.0001**", "键 W256 实测 K-lift **0.0000**", 1),
    # sec7/8 backfill paradigm rows (W256 sec.7/8 backfilled by the r1058 window)
    ("bm-c r1057 W256 §7 范式", "bm-c r1058 W256 §7 范式", 1),
    ("bm-c r1057 W256 §8 范式", "bm-c r1058 W256 §8 范式", 1),
    # low-RAM precedent list: rolled T1 form lost the W251 label; restore it and append W256
    # (engine self-burn 12/12 r1058 windows on this low-RAM machine; chain precedent every-wave append)
    # [needle-heal #2 same-window disclosure: chained W-roll consumes the LOWEST in-list label (W251 here),
    #  same family as heal #1 -- live T1 form measured, corrected]
    ("W243/W246/W248/W249/W250/W252/W253/W254/W255/W256 低 RAM 实烧先例", "W243/W246/W248/W249/W250/W251/W252/W253/W254/W255/W256 低 RAM 实烧先例", 1),
    # freeze-prep precedent face (W256 prereg derive window = r1058 dead window, LANDED 5996e2c93)
    ("r1056/W256 先例 freeze-prep 同式", "r1058/W256 先例 freeze-prep 同式", 1),
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

# freeze-window live face: regex-extract the r1058 stamp (zero transcription) -> r1059 + runtime FREEZE_T
# (NO date roll this generation: the W257 freeze window is the SAME 2026-10-17 as the W256 freeze window,
#  hours later in the same night -- only the round stamp and time roll)
_fw_pat = re.compile(r"bm-c 循环班 r1058 freeze 窗 2026-10-17 \d{2}:\dx")
_fw_hits = _fw_pat.findall(T1)
assert len(_fw_hits) == 1, "freeze-window stamp count=%d (expect 1): %r" % (len(_fw_hits), _fw_hits)
T1 = T1.replace(_fw_hits[0], "bm-c 循环班 r1059 freeze 窗 2026-10-17 " + FREEZE_T)

# post-chain correction legs: needles exist only in T1 (post chained rolls); floors checked on T1
for o, n, f in VMAP_POST_LEGS:
    if T1.count(o) < f:
        raise SystemExit("VMAP POST FLOOR FAIL: %r count=%d floor=%d" % (o, T1.count(o), f))
    T1 = T1.replace(o, n)

# ---------------- block replacements (needles marker-extracted from T1; NEW = final) ----------------
NEW = {}

WL = "（W138..W206+" + "+".join("W%d" % n for n in range(211, 257)) + "）"  # 69 estate + W211..W256 = 115 rows

NEW["b_band_ab"] = (
    "（**A 面=STAIRCASE-AFFECTS-A·1-HOP WALK 形态（W239 staircase era 后第六次连续 A-hop）**："
    "A 面算术续带 580_501..582_500（自注册 W256 A 尾 580_500 续）"
    "在席位窗宇宙（post-W256-REGISTERED 终态注册·freeze-UNBLOCKED）起点即 REFUSED"
    "（注册 W256 B 带 580_501..580_700 落 naive A 窗内=staircase re-emergence affects A 承袭·"
    "W256 prereg §5.5 item5 A-CLEAN-at-naive pre-W256-universe projection superseded live r587 如实披露）"
    "→walk 越注册 W256 B 尾 580_700→A first-clean **580_701..582_700**·**hops=1**·"
    "**A 落位 base==注册前波 B 尾+1（580_700+1）机检关系**"
    "（A_hop_chain 1 跳 verbatim leg1 机证〔window 580_501..582_500→jump 580_701·refuser band 580_501..580_700〕"
    "·A_clean_at_naive_start=false·A_staircase_hop_past_W256_B=true"
    "·A base>=registered prior-wave B tail+1 floor relation）"
    "·非转录 r587 前向单调断言在走册）；"
    "**B-ext exit seed=582_701..582_900**（**B 面=1-HOP own-A RESERVATION CASCADE·落位高于本波 A 窗形态（第七次连续 above-own-A 落位）**："
    "B naive 续带 580_701..580_900（自注册 W256 B 尾 580_700+1 续）"
    "在席位窗宇宙（post-W256-REGISTERED 终态注册·freeze-UNBLOCKED）起点即 REFUSED"
    "（naive B 窗 580_701..580_900 落本波 A first-clean 窗 580_701..582_700 内"
    "=own-A reservation cascade standard leg 强制·probe leg1 B_semantics 机证·B_naive_refused_at_start=true）"
    "——**own-A reservation standard leg 越本波 A 窗 580_701..582_700**（1 hop）"
    "→**1 hop** 落位 **582_701..582_900**·**B 落位 base==本波 A 窗尾+1（582_700+1）EXACT 机检关系**"
    "（B_hop lands-inside-A=false·B_lands_above_own_A=true·B_hop_chain 1 跳 verbatim 在 probe 回执 leg1 机证"
    "·非转录 r587·AB 同窗互斥面 leg2 律在场）；"
    "**W256 prereg §5.5 item5 投影承接面注记兑现+落位分歧如实披露**："
    "投影预言 W257 A naive 580_501..582_500 CLEAN（pre-W256 宇宙零 live refusers）——本窗 live re-derive A 面起点即被注册 W256 B 带拒"
    "（投影 A-CLEAN 未兑现=staircase affects A 承袭·第六次连续 A-hop）"
    "→A first-clean 上移 580_701..582_700→B naive 580_701..580_900 相应落本波 A 窗内→own-A reservation cascade 上移 582_701..582_900"
    "（post-W256 宇宙 live re-derive 必变·W256 prereg §5.5 已披露 live re-derive governs·禁转录投影 r587·"
    "落位高于投影=新拒面如实注记·已如实披露非分叉）"
)

NEW["b3_a_bandface"] = (
    "法典 §4 W257 行 A=580_701..582_700·**STAIRCASE-AFFECTS-A·1-HOP WALK 形态（W239 staircase era 后第六次连续 A-hop）**："
    "A 算术续带 580_501..582_500（自注册 W256 A 尾 580_500 续）"
    "在席位窗宇宙（post-W256-REGISTERED 终态注册·freeze-UNBLOCKED）起点即 REFUSED"
    "（注册 W256 B 带 580_501..580_700 落 naive A 窗内=W256 prereg §5.5 item5 A-CLEAN-at-naive 投影被 live re-derive 超越·r587 superseded 披露）"
    "→walk 越注册 W256 B 尾 580_700→A first-clean 580_701..582_700·**hops=1**·"
    "**A 落位 base==注册前波 B 尾+1（580_700+1）机检关系**"
    "（A_hop_chain 1 跳 verbatim probe leg1 机证·A_clean_at_naive_start=false·A_staircase_hop_past_W256_B=true）"
    "·非转录 r587·ADMIT 回执在场）"
)

NEW["b3_b_bandface"] = (
    "法典 §4 W257 行 B=582_701..582_900·**1-HOP own-A RESERVATION CASCADE·落位高于本波 A 窗形态**："
    "B naive 续带 580_701..580_900（自注册 W256 B 尾 580_700+1 续）"
    "在席位窗宇宙（post-W256-REGISTERED 终态注册）起点即 REFUSED"
    "（naive B 窗落本波 A first-clean 窗 580_701..582_700 内=own-A reservation cascade standard leg·probe leg1 B_semantics 机证）"
    "→own-A reservation 越本波 A 窗 580_701..582_700→1 hop 落位 582_701..582_900·"
    "**B 落位 base==本波 A 窗尾+1（582_700+1）机检关系**"
    "（B_hop lands-inside-A=false·B_lands_above_own_A=true·B_hop_chain 1 跳 verbatim 在 probe 回执"
    "·第七次连续 above-own-A 落位如实注记）"
    "·非转录 r587·与 W256 prereg §5.5 item5 投影承接面注记兑现+落位上移分歧披露收敛·ADMIT 回执在场）"
)

NEW["b1_chain_tail"] = (
    HIST_B1
    + "+W256=bm-c r1058 prereg derive（machine-SUB from frozen W255 tpl f353e49f·derive LANDED 5996e2c93·banned_direction_gate rc0·needle-count pre-flight 全 floors 预验·1 disclosed same-window gate-heal〔count-gate 4->5 b8 连续跳 face〕）"
    + "+五面冻结 splice（r1058 死窗 03:0x LANDED aa6102e35〔editor canon-clone age() law + 3 disclosed needle heals caught PRE-splice by count-asserted gates〕·dual-sha16 pf d4a9d7164ba9490e→ad9776287dd52280 / n1 c6dfb4291c09be1e→986e9162b86e0c7f·W256 块 parity 114 rows）"
    + "+引擎自燃 12/12（mtime-watch auto-ignite engine lane·ledger appends 31c9e4872+1c7112fd9 batched 6+6 self-committed）"
    + "+bm-c r1058 finalize one-pass 已落（K=561,120·账本头 987,535 机读·n1_w256_results.json·03:5x·fivekeys 6/6 ALL PASS·sixgate PRE-FINALIZE 18th consecutive 正相〔triple identity n1 986e9162b86e0c7f / pf ad9776287dd52280 @ aa6102e35〕·K-lift 0.0000 in-band）"
    "——本波上游链=W1..W256 finalize 全落地·零在飞上游席·干净前置**；"
    "席位公示=MSG-20261017-03xx-bmc-w257-seat 已推 origin 27ee6e95a 先于本冻结"
    "【r565 律·席位先行·bm-c r1058 窗发布·queue-head FREEZE-UNBLOCKED 承接·W256 own-wave finalize 已落=席位时即解锁】；"
    "下游 W258+ 投影见 §5.5（probe 机证 leg4·W258 freezer 承接面）】。"
)

NEW["b5_projection"] = (
    "5. **W258+ 投影（probe 机证 leg4·下波冻结方复核非转抄 r587 律）**：A naive first-clean 582_701..584_700 **CLEAN**（hops=0·pre-W257 宇宙零 live refusers）——"
    "**post-W257-REGISTERED 预披露：naive W258 A 起点 582_701 将被注册 W257 B 带 582_701..582_900 拒（staircase-affects-A 第七次连续 A-hop 预期）**；"
    "B naive **582_901..583_100 CLEAN（hops=0）但落投影 A 窗 582_701..584_700 内**（W258p_B_lands_inside_W258p_A_naive=true——"
    "**staircase face 延续**：W257 A 580_701..582_700+B 582_701..582_900 注册后 naive W258 A 窗起点即被注册 W257 B 带拒（staircase affects A 承袭·第七次连续 A-hop 预期）"
    "→A first-clean 将上移·B own-A reservation cascade 落位相应上移——post-W257 宇宙 live re-derive 必变·禁转录投影）；"
    "**W258 冻结方禁假设 staircase A-base==prior-B-tail+1 或 B-base==own-A-tail+1 恒等·须重读 live trace**"
    "（W251 起 staircase affects A·W252/W253/W254/W255/W256/W257=A/B 双 1-hop 形态连续六波如实注记·seed-gap face 已于 W252 终结=A 首跳如实注记）"
    "——W258 冻结方必须在 post-W257 注册宇宙重 derive 且 derive B 时预留本波 A 窗 580_701..582_700+本波 B 带 582_701..582_900"
    "——leg2 律/E36 卡·W141 先例；verify at W258 prereg，hop 链逐跳在 probe 回执。"
)

NEW["b6_ram"] = "·W257 冻结窗 4G bm-c 实锚" + HIST_B6

NEW["b7_claim_projection"] = (
    "·probe W258+ 投影 A naive 582_701..584_700 CLEAN hops=0（零 live refusers）/ B naive 582_901..583_100 CLEAN hops=0 **但落 naive W258 A 窗内**"
    "→own-A reservation cascade 下 staircase 级联上移 **staircase face 延续 live re-derive governs 预披露**"
    "（投影 A naive 582_701..584_700 CLEAN·hops=0——**post-W257-REGISTERED 预披露：naive W258 A 起点 582_701 将被注册 W257 B 带 582_701..582_900 拒=staircase affects A 第七次连续 A-hop 预期**；"
    "投影 B naive 582_901..583_100 clean 但落 naive W258 A 窗 582_701..584_700 内——"
    "**above-own-A 承袭 face：W257 B 582_701..582_900 落本波 A 窗之上〔第七次连续〕·W257 A 面 1-hop=staircase affects A〔第六次连续〕·"
    "W258 冻结方禁假设 staircase A-base==prior-B-tail+1 或 B-base==own-A-tail+1 恒等·须重读 live trace·注册 W257 B 带将拒 naive W258 A 窗仅当重叠"
    "——**W258 freezer 承接面强制注记：须在 post-W257 宇宙重 derive 且 derive B 时预留本波 A 窗·W141 先例·never transcribe r587**）"
)

NEW["b8_selftest"] = (
    "selftest W257 face（A=staircase-hop honest-walk past the registered prior-wave B band 断言"
    "（A_hop_chain 与 probe 回执逐跳恒等·A 第六次连续跳=W239 staircase era 后承袭如实注记·A 落位不落任何已注册带内）"
    "·B=own-A reservation 1-hop lands-above-own-A 断言（B_hop_chain 与 probe 回执逐跳恒等·B 落位不落本波 A 窗内=同窗互斥断言·第七次连续 above-own-A 如实注记）·W256 行 parity 腿"
    "**estate 提取面注记**：冻结拼接脚本的 parity estate（W138..W206 69 行 full-span·r858 absorb 代）从**本机 W256 块物理字节**提取"
    "（结构已知·提取自证断言 69 行 range 恒等在场）——W256 块的自有 W239..W255 legs（17 行）不入 estate 路径"
    "·提取后新增 W239..W256 leg（18 行）构成 W257 块 parity 115 行" + WL + "·零假设零风险。"
)

# marker pairs: (block, start_marker, end_marker) -- needles matched on T1 (post-roll faces)
BLOCKS = [
    ("b_band_ab", "（**A 面=STAIRCASE-AFFECTS-A", "已如实披露非分叉）"),
    ("b3_a_bandface", "法典 §4 W257 行 A=578_501..580_500", "非转录 r587·ADMIT 回执在场）"),
    ("b3_b_bandface", "法典 §4 W257 行 B=580_501..580_700", "披露收敛·ADMIT 回执在场）"),
    ("b5_projection", "5. **W257+ 投影（probe 机证 leg4", "verify at W257 prereg，hop 链逐跳在 probe 回执。"),
    ("b7_claim_projection", "·probe W257+ 投影 A naive 580_501..582_500 CLEAN hops=0", "never transcribe r587**）"),
    ("b6_ram", "·W257 冻结窗 3.3G bm-c 实锚", "W240 冻结窗 33.2G bm-a 实锚）"),
    ("b8_selftest", "selftest W257 face（", "零假设零风险。"),
    ("b1_chain_tail", "+W246=bm-a r1016 prereg derive", "W257 freezer 承接面）】。"),
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
    "PERPETUAL-N1-W257", "research/PERPETUAL_N1_W257_PREREG.md",
    "580_701..582_700", "582_701..582_900", "987,535", "561,120", "563,320",
    "n1_w257_results.json", "MSG-20261017-03xx-bmc-w257-seat", "27ee6e95a",
    "第 255 枚", "第七十七枚", "第 247 波", "第 77 枚",
    "STAIRCASE-AFFECTS-A", "第六次连续 A-hop", "第七次连续 above-own-A",
    "_w257bmc_20261017", "--wave 257", "波号 257",
    "W256=bm-c r1058 prereg derive", "r1058 finalize one-pass",
    "n_eff_held_equal 985,335", "−0.09270015", "0.24503835", "−0.090659",
    "（**0.3107** 实测锚）", "bm-c 循环班 r1059 freeze 窗", "本窗 free RAM ~4GB",
    "→W249 **0.000332**→W250 **0.000331**→W251 **0.000330**→W252 **0.000330**→W253 **0.000329**→W254 **0.000328**→W255 **0.000328**→W256 **0.000327**】",
    "queue-head FREEZE-UNBLOCKED lane", "seed_admit_gate rc0 双带 FREE",
    "A base=580701", "B base=582701",
    "bm-c r1058 W256 §7 范式", "bm-c r1058 W256 §8 范式",
    "W258 freezer 承接面", "verify at W258 prereg",
    "selftest W257 face", "W239..W256 leg（18 行）构成 W257 块 parity 115 行",
    "键 W256 实测 K-lift **0.0000**", "line_merged@K561,120 **1.1947**", "line_pre_w256 1.1947",
    "实差 0.0020 在带内", "已落账键·03:5x", "bm-c r1058 窗 03:5x",
    "r1058/W256 先例 freeze-prep 同式", "254 行单态", "probe leg0 机证 254 行",
    "_w257bmc_freeze_edits", "_w256bmc_freeze_edits", "本波上游链=W1..W256 finalize 全落地",
    "engine_owner==bm-c 76 行注册", "bmc rows 76", "bmc_rows=76",
    "queue-head FREEZE-UNBLOCKED 承接", "A 落位 base==注册前波 B 尾+1（580_700+1）",
    "B 落位 base==本波 A 窗尾+1（582_700+1）",
    "W256 块的自有 W239..W255 legs（17 行）",
    "bm-c r1058 席位", "bm-c r1058 席·queue-head FREEZE-UNBLOCKED 发布",
    "post-W256-REGISTERED 终态注册", "席位窗 probe leg0 实测 254 行",
    "W243/W246/W248/W249/W250/W251/W252/W253/W254/W255/W256 低 RAM 实烧先例", "·W257 冻结窗 4G bm-c 实锚",
    "本候选=bm-c 自有席自有波", "R258：W257 带从未指派",
    "B_hop lands-inside-A=false", "B_lands_above_own_A=true", "A_staircase_hop_past_W256_B=true",
    "§5.5 W258+ 投影承接机证", "exit rng=**582_701+j**", "B-ext exit seed=582_701..582_900",
    "A-ext seed=580_701..582_700",
    "probe leg0 bmc_rows=76 attempt-continuity face（r1058 窗算法·bm-c own seat+bmc live rows 76 实读）",
    "580_501..582_500", "580_701..580_900", "582_701..584_700", "582_901..583_100",
    "A_clean_at_naive_start=false",
    "表尾 W256 行", "pre-W257 全二百五十四行注册 N1 带表", "共二百五十四面实测",
    "engine_owner 行 246 注册在册", "freeze 窗 live derive 254 行单态 owner rows 246",
    "W256 splice 先于席位窗已落地",
    "W256 own-wave finalize 已落=席位时即解锁",
    "n1_w256_results.json",
    "924e87b3f02afb72", "7b550e65716e0ada", "d4a9d7164ba9490e", "c6dfb4291c09be1e",
    "e166afc6c", "b1414b81a", "f931cf102", "72d292ea3",
    "aa6102e35", "31c9e4872", "1c7112fd9", "5996e2c93",
    "ad9776287dd52280", "986e9162b86e0c7f",
    "sixgate PRE-FINALIZE 18th consecutive",
    "（r1058 席位窗实跑", "（bm-c r1058 席位",
    "zero post-splice heal", "e2c4b543e", "3eb691575", "fa2bc55e5", "c211d1269",
]
for s in MUST:
    assert s in T2, "MUST-HAVE missing: %r" % s

MUST_NOT = [
    "**A-ext seed=578_501", "571_901", "571_900", "567_501", "567_500", "545_301", "545_300", "545_500", "565_501",
    "FIRST-CLEAN·hops=0", "13-HOP", "13 hops", "A_hop_chain=[] 空集", "A_clean_at_naive_start=true",
    "573_901..574_100", "573_900", "573_901",
    "−0.09273764", "0.24503097", "−0.09241377", "**0.3092**", "实差 0.0003 在带内",
    "line_merged@K556,720", "556,720 合并池", "累计 null 池=556,720",
    "cb79242ed", "MSG-20261016-22xx", "bmc-w255-seat", "第 76 枚", "第七十六枚", "第 253 枚", "第 245 波",
    "engine_owner 行 244", "owner rows 244", "bmc rows 74", "bmc_rows=74", "engine_owner==bm-c 74",
    "252 行", "二百五十二行注册", "二百五十二面实测", "251 行", "二百五十一行注册", "二百五十一面实测",
    "253 行单态", "机证 253 行", "实测 253 行",
    "r1057 窗算法", "（bm-c r1057 席", "（r1057 席位窗实跑",
    "bm-c r1057 窗", "bm-c 循环班 r1058", "live-read r1058", "已落账键·02:3x",
    "波号 256", "--wave 256", "R257：W256",
    "verify at W257 prereg", "W257 freezer 承接面", "W257p_", "W257 冻结方",
    "键 W255 实测 K-lift", "键 W252 实测 K-lift", "键 W253 实测 K-lift", "键 W254 实测 K-lift", "line_pre_w253", "line_pre_w254", "line_pre_w255",
    "（**B 面=CLEAN", "waits-upstream ARMED",
    "（bm-c r1043 席", "第 75 枚",
    "selftest W256 face", "本窗 free RAM ~3.3GB",
    "第四次连续 A-hop", "第五次连续 A-hop", "第五次连续 above-own-A", "第四次连续 above-own-A",
    "571_901..573_900", "573_901..575_900", "574_101..574_300",
    "576_101..578_100", "576_301..576_500",
    "·W255 冻结窗 2.0G",
    "_w255bmc_20261016", "_w255bmc_20261017",
]
for s in MUST_NOT:
    assert s not in T2, "MUST-NOT-HAVE present: %r (count=%d)" % (s, T2.count(s))

# projection-fulfillment count gates
assert T2.count("W257+ 投影") == 0, "W257+ 投影 count=%d (expect 0)" % T2.count("W257+ 投影")
assert T2.count("W258+ 投影") == 4, "W258+ 投影 count=%d (expect 4 = b1 tail + b5 title + b7 claim + sec8 rolled)" % T2.count("W258+ 投影")
assert T2.count("hops=1") == 2, "hops=1 count=%d (expect 2 = 带位 A + §3 A)" % T2.count("hops=1")
assert T2.count("hops=0") == 5, "hops=0 count=%d (expect 5 = b5 x2 + b7 x3)" % T2.count("hops=0")
assert T2.count("第四次连续 A-hop") == 0, "第四次连续 A-hop count=%d (expect 0)" % T2.count("第四次连续 A-hop")
assert T2.count("第五次连续 A-hop") == 0, "第五次连续 A-hop count=%d (expect 0 = block-replaced)" % T2.count("第五次连续 A-hop")
assert T2.count("第六次连续 A-hop") == 3, "第六次连续 A-hop count=%d (expect 3 = b_band_ab x2 + b3_a x1 own faces)" % T2.count("第六次连续 A-hop")
assert T2.count("第七次连续 A-hop") == 3, "第七次连续 A-hop count=%d (expect 3 = b5 pre-registered face x2 + b7 projection face)" % T2.count("第七次连续 A-hop")
assert T2.count("第七次连续") == 7, "第七次连续 count=%d (expect 7 = A-hop x3 + above-own-A x3 + 〔第七次连续〕 x1)" % T2.count("第七次连续")
assert T2.count("第六次连续") == 5, "第六次连续 count=%d (expect 5 = A-hop x3 + 〔第六次连续〕 x1 + b8 连续跳 x1)" % T2.count("第六次连续")
assert T2.count("第六次连续 above-own-A") == 0, "第六次连续 above-own-A count=%d (expect 0 = block-replaced)" % T2.count("第六次连续 above-own-A")
assert T2.count("第五次连续 above-own-A") == 0, "第五次连续 above-own-A count=%d (expect 0)" % T2.count("第五次连续 above-own-A")
assert T2.count("第四次连续 above-own-A") == 0, "第四次连续 above-own-A count=%d (expect 0)" % T2.count("第四次连续 above-own-A")
assert T2.count("578_301..580_300") == 0, "578_301..580_300 count=%d (expect 0 = block-replaced)" % T2.count("578_301..580_300")
assert T2.count("578_501..578_700") == 0, "578_501..578_700 count=%d (expect 0 = block-replaced)" % T2.count("578_501..578_700")
assert T2.count("580_501..582_500") == 4, "580_501..582_500 count=%d (expect 4 = b_band_ab x3 [续带 + hop-chain verbatim + 投影兑现 quote] + b3_a x1)" % T2.count("580_501..582_500")
assert T2.count("580_701..580_900") == 4, "580_701..580_900 count=%d (expect 4 = b_band_ab x3 [B naive 续带 + 落 A 窗内 + 投影兑现 tail] + b3_b x1)" % T2.count("580_701..580_900")
assert T2.count("576_101..578_100") == 0, "576_101..578_100 count=%d (expect 0 = block-replaced)" % T2.count("576_101..578_100")
assert T2.count("576_301..576_500") == 0, "576_301..576_500 count=%d (expect 0 = block-replaced)" % T2.count("576_301..576_500")

# diagnostics (non-fatal; prior-wave band faces legitimately referenced in NEW blocks)
print("diag counts: 578_501..580_500=%d 580_501..580_700=%d (prior-wave band refs in NEW blocks + any outside-block survivors)" % (
    T2.count("578_501..580_500"), T2.count("580_501..580_700")))

# residue scan: all X_Y..X_Y windows well-formed
for m in re.finditer(r"(\d{3}_\d{3})\.\.(\d{3}_\d{3})", T2):
    lo = int(m.group(1).replace("_", "")); hi = int(m.group(2).replace("_", ""))
    assert lo <= hi, "malformed window %s" % m.group(0)

io.open(OUT, "w", encoding="utf-8", newline="").write(T2)
print("W257 PREREG DERIVE OK -> %s (%d bytes, %d lines)" % (OUT, len(T2.encode("utf-8")), T2.count("\n") + 1))
print("freeze window face: bm-c 循环班 r1059 freeze 窗 2026-10-17 " + FREEZE_T)
print("blocks replaced: %s" % ", ".join(n for n, _, _ in BLOCKS))
print("vmap legs: %d floors: %d post-legs: %d MUST: %d MUST_NOT: %d" % (len(VMAP), len(VMAP_FLOORS), len(VMAP_POST_LEGS), len(MUST), len(MUST_NOT)))
print("src blob-verified == 4503bf5d92d69c2a409dc2074a300140f7bfdcb9 @ 5996e2c93 (frozen pre-run face; HEAD post-backfill twin 2fb6747e disclosed, NOT used)")
