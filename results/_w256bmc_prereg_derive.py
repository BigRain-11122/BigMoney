# -*- coding: utf-8 -*-
# r1058 bm-c: W256 prereg derive (count-asserted ordered transform + marker-extracted block replaces).
# Source = committed frozen W255 prereg AT THE FREEZE COMMIT 72d292ea3 (git 72d292ea3:research/PERPETUAL_N1_W255_PREREG.md,
# 40,964 bytes -- the frozen pre-run face; sec7/8 placeholders intact). Extracted to
# results/_w256bmc_w255_frozen_face.txt THIS window (blob f353e49f3486957b1b274254f0c0368a51a5c2fc, byte-verified
# hash-object == rev-parse @ 72d292ea3; sha256_16 9b67cded6a4d2d38 measured by the pre-flight probe).
# TEMPLATE-FACE DISCLOSURE (needle-face divergence, honest): HEAD twin b2f6e5d2c3daf3140f4d98f24d70292e03e82875 = the
# CURRENT HEAD face = the POST-CYCLE face with sec.7/8 BACKFILLED by the r1057 window (W255 actual results).
# Deriving from the backfilled face would fabricate W256 sec.7/8 "跑后实证" from W255's measured numbers -- the
# r1049/r1052/r1056 precedent (derive always from the PRIOR wave's FREEZE-COMMIT face, "frozen pre-run face;
# sec7/8 placeholders intact") and the prereg semantics both require f353e49f. Both faces measured this window
# (rev-parse 72d292ea3:=f353e49f / HEAD:=b2f6e5d2); divergence disclosed in header + closeout;
# b2f6e5d2 recorded as the post-backfill twin, NOT used as template.
# W256 facts (all machine-derived, never transcribed):
#   - seat probe ADMIT receipt results/_w256bmc_20261017_probe_receipt.json (r1057 window, seat rides origin
#     fd48643c9 per r565 early-visibility law, MSG-20261017-023x-bmc-w256-seat landed in fleet/inbox/). STAIRCASE
#     CONTINUES: A naive 578_301..580_300 REFUSED at start (registered W255 B band 578_301..578_500 sits INSIDE the
#     naive A window) -> A first-clean 578_501..580_500 hops=1 (FIFTH consecutive A-hop, W255 prereg sec.5 item5
#     A-CLEAN-at-naive pre-W255-universe projection superseded live r587, divergence disclosed) / B naive
#     578_501..578_700 REFUSED at start (lands INSIDE the own-wave W256 A first-clean window 578_501..580_500) ->
#     own-A reservation cascade hop past 580_500 -> 580_501..580_700 hops=1 (SIXTH consecutive above-own-A landing);
#     seed_admit FREE x2 (A base=578501 span=2000 / B base=580501 span=200); leg0 rows=253 owner_rows=245
#     bmc_rows=75 bmc_ordinal=75 ordinal=246; leg2 conflicts=0; leg3 origin_vacancy=true;
#     leg4 W257+ projection: A naive 580_501..582_500 CLEAN hops=0 BUT post-W256-REGISTERED the naive W257 A
#     start 580_501 is REFUSED by the registered W256 B band 580_501..580_700 (SIXTH consecutive A-hop expected)
#     AND the W257 B naive 580_701..580_900 lands inside the own-A reservation face.
#   - upstream W255 finalize landed (r1057 window estate machine-verified, ledger 983,135+2,200=985,335 EXACT):
#     merged K=558,920 / merged mu -0.09270819 / sigma 0.24503942 / se_mu@K558,920 0.000328 held-flat / W255-only
#     mu -0.08525445 / A p95 0.3422 / K-lift +0.0001 in-band / n_eff_held 983,135 / line_pre_w255 1.1945 /
#     line_merged_558920 1.1946 / own-slice vs pre-wave merged gap 0.007454 in-band<0.02 chain-max
#     (results/perpetual_faces/n1_w255_results.json + results/_r1057bmc_w255_fivekeys.json, all six keys PASS)
#   - W255 chain: prereg derive r1056 LANDED 72d292ea3 (3 same-window needle heals disclosed) + five-face freeze
#     splice r1057 dead-window LANDED e166afc6c (2 disclosed needle heals + 2 blanket-duplication sub heals caught
#     PRE-splice per commit msg; dual-sha16 pf 924e87b3f02afb72->d4a9d7164ba9490e / n1 7b550e65716e0ada->c6dfb4291c09be1e;
#     W255 block parity 113 rows) + engine self-burn 12/12 (ledger appends b1414b81a+f931cf102 batched 6+6
#     self-committed) + r1057 continuation sixgate PRE-FINALIZE 17th consecutive (triple identity n1 c6dfb4291c09be1e /
#     pf d4a9d7164ba9490e @ e166afc6c) + finalize one-pass 985,335/K=558,920 + fivekeys 6/6 + sec.7/8 backfilled +
#     W256 seat published fd48643c9.
# Needle-count pre-flight evidence: results/_w256bmc_needle_probe.py (THIS window, ALL floors below measured live
# by the probe -- results/_w256bmc_needle_counts.txt; counts match every VMAP_FLOORS entry below).
# Same-window needle heals disclosed: NONE (all floors pre-verified by the probe before authoring; the
# probe-receipt date face _w255bmc_20261016 x3 -> _w256bmc_20261017 is a NEW leg this generation -- the
# r1056 generation's date faces happened to be date-stable 10-16->10-16, this generation rolls 10-16->10-17).
# RAM face: this r1058 freeze window live-measures ~3.3G free (Get-CimInstance at 02:5x; 27b LLM still resident
# per gpu_mem_used 14.7G/16G + engine queue_next=[] both live-read this window -- honest face carried).
import io, os, sys, datetime, subprocess, hashlib, re

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(REPO, "results", "_w256bmc_w255_frozen_face.txt")
OUT = os.path.join(REPO, "research", "PERPETUAL_N1_W256_PREREG.md")
GIT = "C:/Program Files/Git/cmd/git.exe"

# --- source byte-identity gates ---
_blob_expect = "f353e49f3486957b1b274254f0c0368a51a5c2fc"   # freeze-commit face @ 72d292ea3
_ho = subprocess.run([GIT, "hash-object", SRC], capture_output=True, text=True, cwd=REPO).stdout.strip()
assert _ho == _blob_expect, "SRC blob mismatch: got %s expect %s" % (_ho, _blob_expect)
_fc = subprocess.run([GIT, "rev-parse", "72d292ea3:research/PERPETUAL_N1_W255_PREREG.md"],
                     capture_output=True, text=True, cwd=REPO).stdout.strip()
assert _fc == _blob_expect, "freeze-commit blob mismatch: got %s expect %s" % (_fc, _blob_expect)
_hb = subprocess.run([GIT, "rev-parse", "HEAD:research/PERPETUAL_N1_W255_PREREG.md"],
                     capture_output=True, text=True, cwd=REPO).stdout.strip()
assert _hb == "b2f6e5d2c3daf3140f4d98f24d70292e03e82875", "HEAD tpl twin face drifted: %s" % _hb

T0 = io.open(SRC, encoding="utf-8", newline="").read()
assert hashlib.sha256(T0.encode("utf-8")).hexdigest()[:16] == "9b67cded6a4d2d38", "SRC sha mismatch"

P1, P2, P3 = "\x01W\x01", "\x01N\x01", "\x01B\x01"

now = datetime.datetime.now()
FREEZE_T = "%02d:%dx" % (now.hour, now.minute // 10)

# machine-extracted historical spans (from T0 PRE-roll bytes: zero transcription for carried content)
_i_b1 = T0.index("+W246=bm-a r1016 prereg derive")
_j_b1 = T0.index("——本波上游链=")
HIST_B1 = T0[_i_b1:_j_b1]  # W246..W254 chain legs verbatim (frozen template bytes)
_i_b6 = T0.index("·W250 冻结窗 RAM 未记录（r1046 死窗")
_b6_end = "W240 冻结窗 33.2G bm-a 实锚）"
_j_b6 = T0.index(_b6_end) + len(_b6_end)
HIST_B6 = T0[_i_b6:_j_b6]  # W250..W240 freeze-window RAM ledger verbatim

VMAP = [
    # projection first, then line_merged face, then prior-K bare, then ledger heads (order-critical)
    ("558,920 投影", "561,120 投影"),
    ("line_merged@K556,720 **1.1944**", "line_merged@K558,920 **1.1946**"),
    ("556,720", "558,920"),
    ("983,135", "985,335"),
    ("980,935", "983,135"),
    # sec5 measured keys -> W255 measured faces (n1_w255_results.json machine values)
    ("−0.09273764", "−0.09270819"),
    ("−0.09241377", "−0.08525445"),
    ("0.24503097", "0.24503942"),
    ("实差 0.0003 在带内", "实差 0.0075 在带内"),
    ("（**0.3092** 实测锚）", "（**0.3422** 实测锚）"),
    # band values outside block regions (staircase-5th-hop + own-A reservation cascade faces)
    ("A-ext seed=576_301..578_300", "A-ext seed=578_501..580_500"),
    ("entry rng seed=**576_301+j**", "entry rng seed=**578_501+j**"),
    ("entry rng=**576_301+j**", "entry rng=**578_501+j**"),
    ("exit rng=**578_301+j**", "exit rng=**580_501+j**"),
    ("A base=576301 span=2000 checked=2000 verdict=FREE", "A base=578501 span=2000 checked=2000 verdict=FREE"),
    ("B base=578301 span=200 checked=200 verdict=FREE", "B base=580501 span=200 checked=200 verdict=FREE"),
    ("R256：W255", "R257：W256"),
    # base-relation faces (block-external occurrences; block NEW uses the same new faces)
    ("576_300+1", "578_500+1"),
    ("578_300+1", "580_500+1"),
    # seat / provenance faces (W256 seat published r1057 window, rides origin fd48643c9)
    ("MSG-20261016-22xx-bmc-w255-seat", "MSG-20261017-023x-bmc-w256-seat"),
    ("cb79242ed", "fd48643c9"),
    ("（bm-c r1055 席·queue-head FREEZE-UNBLOCKED 发布）", "（bm-c r1057 席·queue-head FREEZE-UNBLOCKED 发布）"),
    ("（bm-c r1055 席位", "（bm-c r1057 席位"),
    ("（r1055 席位窗实跑", "（r1057 席位窗实跑"),
    # finalize window faces (specific first, then catch-all)
    ("bm-c r1055 窗 21:3x", "bm-c r1057 窗 02:3x"),
    ("21:3x", "02:3x"),
    # engine live-read + RAM head (bm-c current window honest: ~3.3G free live-measured THIS r1058 freeze window;
    # 27b LLM resident per O-20261016-2347 GPU dual-mode + engine queue_next=[] both live-read this window)
    ("saturation_engine.py status live-read r1056", "saturation_engine.py status live-read r1058"),
    ("本窗 free RAM ~1.3GB（bm-c 底盘常驻·24G 物理内存机·LLM 态 27b 常驻+引擎队列空转·CPU 车道独立如实注记）",
     "本窗 free RAM ~3.3GB（bm-c 底盘常驻·24G 物理内存机·LLM 态 27b 常驻+引擎队列空转·CPU 车道独立如实注记）"),
    # probe-receipt date face (W256 receipt = _w256bmc_20261017; MUST precede the _w255bmc chained roll below --
    # r1056 generation was date-stable 10-16->10-16, THIS generation rolls 10-16->10-17)
    ("_w255bmc_20261016", "_w255bmc_20261017"),
    # wave-number roll (chained placeholders)
    ("W255", P1), ("W254", "W255"), ("W253", "W254"), ("W252", "W253"), ("W251", "W252"), (P1, "W256"),
    # result-file names (chained)
    ("n1_w255", P2), ("n1_w254", "n1_w255"), ("n1_w253", "n1_w254"), (P2, "n1_w256"),
    # probe/freeze script basenames (chained; current face _w256bmc <- template _w255bmc)
    ("_w255bmc", P3), ("_w254bmc", "_w255bmc"), (P3, "_w256bmc"),
    # runner CLI wave
    ("--wave 255", "--wave 256"),
    ("波号 255", "波号 256"),
    # pool/engine ordinals
    ("第 253 枚", "第 254 枚"),
    ("第 245 波", "第 246 波"),
    ("bm-c 第七十五枚自有波", "bm-c 第七十六枚自有波"),
    # subsumption-order fix: compound needle contains 第 75 枚 -> MUST run before any bare roll
    ("bmc rows 74+候选=第 75 枚 EXACT", "bmc rows 75+候选=第 76 枚 EXACT"),
    ("第 75 枚", "第 76 枚"),
    ("probe leg0 bmc_rows=74 attempt-continuity face（r1055 窗算法·bm-c own seat+bmc live rows 74 实读）",
     "probe leg0 bmc_rows=75 attempt-continuity face（r1057 窗算法·bm-c own seat+bmc live rows 75 实读）"),
    ("engine_owner==bm-c 74 行注册", "engine_owner==bm-c 75 行注册"),
    ("engine_owner 行 244 注册在册", "engine_owner 行 245 注册在册"),
    # registry scan faces
    ("全二百五十二行注册 N1 带表", "全二百五十三行注册 N1 带表"),
    ("freeze 窗 live derive 252 行单态 owner rows 244", "freeze 窗 live derive 253 行单态 owner rows 245"),
    ("probe leg0 机证 252 行〔", "probe leg0 机证 253 行〔"),
    ("席位窗 probe leg0 实测 252 行〔", "席位窗 probe leg0 实测 253 行〔"),
    ("perpetual_faces.py 零 253 行", "perpetual_faces.py 零 254 行"),
    ("共二百五十二面实测", "共二百五十三面实测"),
    # sec8 placeholder projection-label bump (W256+ -> W257+ face)
    ("§5.5 W256+ 投影承接机证", "§5.5 W257+ 投影承接机证"),
]

VMAP_FLOORS = {
    "558,920 投影": 1, "line_merged@K556,720 **1.1944**": 1,
    "556,720": 7, "983,135": 3, "980,935": 2, "978,735": 1, "976,535": 2,   # 978,735/976,535 = HIST-region historical heads, rolls heal via block replace
    "−0.09273764": 1, "−0.09241377": 1, "0.24503097": 1, "实差 0.0003 在带内": 1,
    "（**0.3092** 实测锚）": 1,
    "A-ext seed=576_301..578_300": 1,
    "entry rng seed=**576_301+j**": 1, "entry rng=**576_301+j**": 1,
    "exit rng=**578_301+j**": 1,
    "A base=576301 span=2000 checked=2000 verdict=FREE": 1,
    "B base=578301 span=200 checked=200 verdict=FREE": 1,
    "R256：W255": 1,
    "W255": 33, "W254": 67, "W253": 8, "W252": 9, "W251": 8,
    "n1_w255": 4, "n1_w254": 3, "n1_w253": 1, "_w255bmc": 4, "_w254bmc": 1,
    "_w255bmc_20261016": 3,
    "--wave 255": 2, "波号 255": 1,
    "第 253 枚": 1, "第 245 波": 1, "bm-c 第七十五枚自有波": 1,
    "bmc rows 74+候选=第 75 枚 EXACT": 2, "第 75 枚": 2,
    "probe leg0 bmc_rows=74 attempt-continuity face（r1055 窗算法·bm-c own seat+bmc live rows 74 实读）": 1,
    "engine_owner==bm-c 74 行注册": 1, "engine_owner 行 244 注册在册": 1,
    "全二百五十二行注册 N1 带表": 1,
    "freeze 窗 live derive 252 行单态 owner rows 244": 1,
    "probe leg0 机证 252 行〔": 1, "席位窗 probe leg0 实测 252 行〔": 1,
    "perpetual_faces.py 零 253 行": 1,
    "共二百五十二面实测": 1,
    "MSG-20261016-22xx-bmc-w255-seat": 4, "cb79242ed": 3,
    "（bm-c r1055 席·queue-head FREEZE-UNBLOCKED 发布）": 1,
    "（bm-c r1055 席位": 1, "（r1055 席位窗实跑": 1,
    "bm-c r1055 窗 21:3x": 1, "21:3x": 4, "已落账键·21:3x": 1,
    "saturation_engine.py status live-read r1056": 1,
    "本窗 free RAM ~1.3GB（bm-c 底盘常驻·24G 物理内存机·LLM 态 27b 常驻+引擎队列空转·CPU 车道独立如实注记）": 1,
    "§5.5 W256+ 投影承接机证": 1,
    "576_300+1": 4, "578_300+1": 2,
    # block-marker stability floors (raw template face; T1 marker = post-roll form asserted in BLOCKS)
    "（**A 面=STAIRCASE-AFFECTS-A": 1,
    "已如实披露非分叉）": 1,
    "法典 §4 W255 行 A=576_301..578_300": 1,
    "法典 §4 W255 行 B=578_301..578_500": 1,
    "披露收敛·ADMIT 回执在场）": 1,
    "非转录 r587·ADMIT 回执在场）": 1,
    "5. **W256+ 投影（probe 机证 leg4": 1,
    "verify at W256 prereg，hop 链逐跳在 probe 回执。": 1,
    "·probe W256+ 投影 A naive 578_301..580_300 CLEAN hops=0": 1,
    "never transcribe r587**）": 1,
    "·W255 冻结窗 2.0G bm-c 实锚": 1,
    "W240 冻结窗 33.2G bm-a 实锚）": 1,
    "·W250 冻结窗 RAM 未记录（r1046 死窗": 1,
    "selftest W255 face（": 1, "零假设零风险。": 1,
    "+W246=bm-a r1016 prereg derive": 1,
    "——本波上游链=": 1,
    "W256 freezer 承接面）】。": 1,
    "W243/W246/W248/W249/W250/W251/W252/W253/W254 低 RAM 实烧先例": 1,
    "r1054/W254 先例 freeze-prep 同式": 1,
    "→W249 **0.000332**→W250 **0.000331**→W251 **0.000330**→W252 **0.000330**→W253 **0.000329**→W254 **0.000328**】": 1,
    "line_pre_w254 1.1945": 1,
    "bm-c r1055 W254 §7 范式": 1, "bm-c r1055 W254 §8 范式": 1,
    "键 W254 实测 K-lift **−0.0001**": 1,
    "n_eff_held_equal 980,935": 1,
    "queue-head FREEZE-UNBLOCKED lane": 1,
    "本候选=bm-c 自有席自有波": 1,
    "表尾 W254 行": 2,
    "pre-W255 全二百五十二行注册 N1 带表": 1,
    "bm-c 循环班 r1056 freeze 窗 2026-10-17": 1,
    "第四次连续 A-hop": 3,
    "第五次连续 A-hop": 3, "第五次连续": 7, "第五次连续 above-own-A": 3,
    "hops=1": 2,
    "（W138..W206+": 1,
    "W239..W254 leg（16 行）构成 W255 块 parity 113 行": 1,
    "W239..W253 legs（15 行）": 1,
    "zero post-splice heal": 4,
    "924e87b3f02afb72": 2, "7b550e65716e0ada": 2,
    "+W254=bm-c r1054 prereg derive": 1,
    "e2c4b543e": 1, "3eb691575": 1, "fa2bc55e5": 1, "c211d1269": 1,
    # zero-floors (absence assertions on T0)
    "waits-upstream ARMED": 0,
    "（**B 面=CLEAN": 0,
    "985,335": 0, "0.3422": 0, "561,120": 0,
    "−0.09270819": 0, "−0.08525445": 0, "0.24503942": 0, "0.0075 在带内": 0,
    "578_501..580_500": 0, "580_501..580_700": 0, "580_501..582_500": 0, "580_701..580_900": 0,
    "578_500+1": 0, "580_500+1": 0,
    "A base=578501 span=2000 checked=2000 verdict=FREE": 0,
    "B base=580501 span=200 checked=200 verdict=FREE": 0,
    "558,920": 1,  # only the 投影 compound; bare face absent (baseline rolls supply it)
    "R257：W256": 0, "n1_w256": 0, "_w256bmc": 0, "--wave 256": 0, "波号 256": 0,
    "第 76 枚": 0, "第 254 枚": 0, "第 246 波": 0, "bm-c 第七十六枚自有波": 0,
    "第六次连续": 0, "W257": 0,
    "fd48643c9": 0, "（bm-c r1057 席": 0, "（r1057 席位窗实跑": 0, "02:3x": 0,
    "line_pre_w255": 0, "键 W255 实测 K-lift": 0,
    "engine_owner==bm-c 75 行注册": 0, "engine_owner 行 245 注册在册": 0,
    "全二百五十三行注册 N1 带表": 0, "freeze 窗 live derive 253 行单态 owner rows 245": 0,
    "probe leg0 机证 253 行〔": 0, "席位窗 probe leg0 实测 253 行〔": 0,
    "perpetual_faces.py 零 254 行": 0, "共二百五十三面实测": 0,
    "§5.5 W257+ 投影承接机证": 0,
}

# floors for POST-chain correction legs (needles exist only in T1 after the pre-chain legs run)
VMAP_POST_LEGS = [
    # se_mu narrowing chain: wave roll consumed the W251 label; restore it and append true W255 se 0.000328
    # (W255 key5 = held-flat first non-narrowing in chain, honest note carried in the replacement tail)
    ("→W249 **0.000332**→W250 **0.000331**→W252 **0.000330**→W253 **0.000330**→W254 **0.000329**→W255 **0.000328**】",
     "→W249 **0.000332**→W250 **0.000331**→W251 **0.000330**→W252 **0.000330**→W253 **0.000329**→W254 **0.000328**→W255 **0.000328**】", 1),
    # line_pre face: lowercase w-token escapes the uppercase W-roll (r1045 derive precedent);
    # W255 actual line_pre_w255 = 1.1945 (n1_w255_results.json skill_line machine value)
    ("line_pre_w254 1.1945", "line_pre_w255 1.1945", 1),
    # K-lift value face: wave roll W254->W255 relabeled the anchor; W255 true K-lift = +0.0001 in-band
    ("键 W255 实测 K-lift **−0.0001**", "键 W255 实测 K-lift **+0.0001**", 1),
    # sec7/8 backfill paradigm rows (W255 sec.7/8 backfilled by the r1057 window)
    ("bm-c r1055 W255 §7 范式", "bm-c r1057 W255 §7 范式", 1),
    ("bm-c r1055 W255 §8 范式", "bm-c r1057 W255 §8 范式", 1),
    # low-RAM precedent list: rolled T1 form lost the W251 label; restore it and append W255
    # (engine self-burn 12/12 r1057 window on this low-RAM machine; chain precedent every-wave append)
    ("W243/W246/W248/W249/W250/W252/W253/W254/W255 低 RAM 实烧先例", "W243/W246/W248/W249/W250/W251/W252/W253/W254/W255 低 RAM 实烧先例", 1),
    # freeze-prep precedent face (W255 prereg derive window = r1056)
    ("r1054/W255 先例 freeze-prep 同式", "r1056/W255 先例 freeze-prep 同式", 1),
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

# freeze-window live face: regex-extract the r1056 stamp (zero transcription) -> r1058 + runtime FREEZE_T
# (NO date roll this generation: the W256 freeze window is the SAME 2026-10-17 as the W255 freeze window,
#  hours later in the same night -- only the round stamp and time roll)
_fw_pat = re.compile(r"bm-c 循环班 r1056 freeze 窗 2026-10-17 \d{2}:\dx")
_fw_hits = _fw_pat.findall(T1)
assert len(_fw_hits) == 1, "freeze-window stamp count=%d (expect 1): %r" % (len(_fw_hits), _fw_hits)
T1 = T1.replace(_fw_hits[0], "bm-c 循环班 r1058 freeze 窗 2026-10-17 " + FREEZE_T)

# post-chain correction legs: needles exist only in T1 (post chained rolls); floors checked on T1
for o, n, f in VMAP_POST_LEGS:
    if T1.count(o) < f:
        raise SystemExit("VMAP POST FLOOR FAIL: %r count=%d floor=%d" % (o, T1.count(o), f))
    T1 = T1.replace(o, n)

# ---------------- block replacements (needles marker-extracted from T1; NEW = final) ----------------
NEW = {}

WL = "（W138..W206+" + "+".join("W%d" % n for n in range(211, 256)) + "）"  # 69 estate + W211..W255 = 114 rows

NEW["b_band_ab"] = (
    "（**A 面=STAIRCASE-AFFECTS-A·1-HOP WALK 形态（W239 staircase era 后第五次连续 A-hop）**："
    "A 面算术续带 578_301..580_300（自注册 W255 A 尾 578_300 续）"
    "在席位窗宇宙（post-W255-REGISTERED 终态注册·freeze-UNBLOCKED）起点即 REFUSED"
    "（注册 W255 B 带 578_301..578_500 落 naive A 窗内=staircase re-emergence affects A 承袭·"
    "W255 prereg §5.5 item5 A-CLEAN-at-naive pre-W255-universe projection superseded live r587 如实披露）"
    "→walk 越注册 W255 B 尾 578_500→A first-clean **578_501..580_500**·**hops=1**·"
    "**A 落位 base==注册前波 B 尾+1（578_500+1）机检关系**"
    "（A_hop_chain 1 跳 verbatim leg1 机证〔window 578_301..580_300→jump 578_501·refuser band 578_301..578_500〕"
    "·A_clean_at_naive_start=false·A_staircase_hop_past_W255_B=true"
    "·A base>=registered prior-wave B tail+1 floor relation）"
    "·非转录 r587 前向单调断言在走册）；"
    "**B-ext exit seed=580_501..580_700**（**B 面=1-HOP own-A RESERVATION CASCADE·落位高于本波 A 窗形态（第六次连续 above-own-A 落位）**："
    "B naive 续带 578_501..578_700（自注册 W255 B 尾 578_500+1 续）"
    "在席位窗宇宙（post-W255-REGISTERED 终态注册·freeze-UNBLOCKED）起点即 REFUSED"
    "（naive B 窗 578_501..578_700 落本波 A first-clean 窗 578_501..580_500 内"
    "=own-A reservation cascade standard leg 强制·probe leg1 B_semantics 机证·B_naive_refused_at_start=true）"
    "——**own-A reservation standard leg 越本波 A 窗 578_501..580_500**（1 hop）"
    "→**1 hop** 落位 **580_501..580_700**·**B 落位 base==本波 A 窗尾+1（580_500+1）EXACT 机检关系**"
    "（B_hop lands-inside-A=false·B_lands_above_own_A=true·B_hop_chain 1 跳 verbatim 在 probe 回执 leg1 机证"
    "·非转录 r587·AB 同窗互斥面 leg2 律在场）；"
    "**W255 prereg §5.5 item5 投影承接面注记兑现+落位分歧如实披露**："
    "投影预言 W256 A naive 578_301..580_300 CLEAN（pre-W255 宇宙零 live refusers）——本窗 live re-derive A 面起点即被注册 W255 B 带拒"
    "（投影 A-CLEAN 未兑现=staircase affects A 承袭·第五次连续 A-hop）"
    "→A first-clean 上移 578_501..580_500→B naive 578_501..578_700 相应落本波 A 窗内→own-A reservation cascade 上移 580_501..580_700"
    "（post-W255 宇宙 live re-derive 必变·W255 prereg §5.5 已披露 live re-derive governs·禁转录投影 r587·"
    "落位高于投影=新拒面如实注记·已如实披露非分叉）"
)

NEW["b3_a_bandface"] = (
    "法典 §4 W256 行 A=578_501..580_500·**STAIRCASE-AFFECTS-A·1-HOP WALK 形态（W239 staircase era 后第五次连续 A-hop）**："
    "A 算术续带 578_301..580_300（自注册 W255 A 尾 578_300 续）"
    "在席位窗宇宙（post-W255-REGISTERED 终态注册·freeze-UNBLOCKED）起点即 REFUSED"
    "（注册 W255 B 带 578_301..578_500 落 naive A 窗内=W255 prereg §5.5 item5 A-CLEAN-at-naive 投影被 live re-derive 超越·r587 superseded 披露）"
    "→walk 越注册 W255 B 尾 578_500→A first-clean 578_501..580_500·**hops=1**·"
    "**A 落位 base==注册前波 B 尾+1（578_500+1）机检关系**"
    "（A_hop_chain 1 跳 verbatim probe leg1 机证·A_clean_at_naive_start=false·A_staircase_hop_past_W255_B=true）"
    "·非转录 r587·ADMIT 回执在场）"
)

NEW["b3_b_bandface"] = (
    "法典 §4 W256 行 B=580_501..580_700·**1-HOP own-A RESERVATION CASCADE·落位高于本波 A 窗形态**："
    "B naive 续带 578_501..578_700（自注册 W255 B 尾 578_500+1 续）"
    "在席位窗宇宙（post-W255-REGISTERED 终态注册）起点即 REFUSED"
    "（naive B 窗落本波 A first-clean 窗 578_501..580_500 内=own-A reservation cascade standard leg·probe leg1 B_semantics 机证）"
    "→own-A reservation 越本波 A 窗 578_501..580_500→1 hop 落位 580_501..580_700·"
    "**B 落位 base==本波 A 窗尾+1（580_500+1）机检关系**"
    "（B_hop lands-inside-A=false·B_lands_above_own_A=true·B_hop_chain 1 跳 verbatim 在 probe 回执"
    "·第六次连续 above-own-A 落位如实注记）"
    "·非转录 r587·与 W255 prereg §5.5 item5 投影承接面注记兑现+落位上移分歧披露收敛·ADMIT 回执在场）"
)

NEW["b1_chain_tail"] = (
    HIST_B1
    + "+W255=bm-c r1056 prereg derive（machine-SUB from frozen W254 tpl e2c4b543e·derive LANDED 72d292ea3·banned_direction_gate rc0·needle-count pre-flight 全 floors 预验·3 same-window needle heals 披露〔RAM 1.3G live anchor / MUST_NOT suffix-restore / count-gates 3->4 x2〕）"
    + "+五面冻结 splice（r1057 死窗 02:0x LANDED e166afc6c〔2 disclosed needle heals + 2 blanket-duplication sub heals caught PRE-splice per commit msg〕·dual-sha16 pf 924e87b3f02afb72→d4a9d7164ba9490e / n1 7b550e65716e0ada→c6dfb4291c09be1e·W255 块 parity 113 rows）"
    + "+引擎自燃 12/12（mtime-watch auto-ignite engine lane·ledger appends b1414b81a+f931cf102 batched 6+6 self-committed）"
    + "+bm-c r1057 finalize one-pass 已落（K=558,920·账本头 985,335 机读·n1_w255_results.json·02:3x·fivekeys 6/6 ALL PASS·sixgate PRE-FINALIZE 17th consecutive 正相〔triple identity n1 c6dfb4291c09be1e / pf d4a9d7164ba9490e @ e166afc6c〕·K-lift +0.0001 in-band）"
    "——本波上游链=W1..W255 finalize 全落地·零在飞上游席·干净前置**；"
    "席位公示=MSG-20261017-023x-bmc-w256-seat 已推 origin fd48643c9 先于本冻结"
    "【r565 律·席位先行·bm-c r1057 窗发布·queue-head FREEZE-UNBLOCKED 承接·W255 own-wave finalize 已落=席位时即解锁】；"
    "下游 W257+ 投影见 §5.5（probe 机证 leg4·W257 freezer 承接面）】。"
)

NEW["b5_projection"] = (
    "5. **W257+ 投影（probe 机证 leg4·下波冻结方复核非转抄 r587 律）**：A naive first-clean 580_501..582_500 **CLEAN**（hops=0·pre-W256 宇宙零 live refusers）——"
    "**post-W256-REGISTERED 预披露：naive W257 A 起点 580_501 将被注册 W256 B 带 580_501..580_700 拒（staircase-affects-A 第六次连续 A-hop 预期）**；"
    "B naive **580_701..580_900 CLEAN（hops=0）但落投影 A 窗 580_501..582_500 内**（W257p_B_lands_inside_W257p_A_naive=true——"
    "**staircase face 延续**：W256 A 578_501..580_500+B 580_501..580_700 注册后 naive W257 A 窗起点即被注册 W256 B 带拒（staircase affects A 承袭·第六次连续 A-hop 预期）"
    "→A first-clean 将上移·B own-A reservation cascade 落位相应上移——post-W256 宇宙 live re-derive 必变·禁转录投影）；"
    "**W257 冻结方禁假设 staircase A-base==prior-B-tail+1 或 B-base==own-A-tail+1 恒等·须重读 live trace**"
    "（W251 起 staircase affects A·W252/W253/W254/W255/W256=A/B 双 1-hop 形态连续五波如实注记·seed-gap face 已于 W252 终结=A 首跳如实注记）"
    "——W257 冻结方必须在 post-W256 注册宇宙重 derive 且 derive B 时预留本波 A 窗 578_501..580_500+本波 B 带 580_501..580_700"
    "——leg2 律/E36 卡·W141 先例；verify at W257 prereg，hop 链逐跳在 probe 回执。"
)

NEW["b6_ram"] = "·W256 冻结窗 3.3G bm-c 实锚" + HIST_B6

NEW["b7_claim_projection"] = (
    "·probe W257+ 投影 A naive 580_501..582_500 CLEAN hops=0（零 live refusers）/ B naive 580_701..580_900 CLEAN hops=0 **但落 naive W257 A 窗内**"
    "→own-A reservation cascade 下 staircase 级联上移 **staircase face 延续 live re-derive governs 预披露**"
    "（投影 A naive 580_501..582_500 CLEAN·hops=0——**post-W256-REGISTERED 预披露：naive W257 A 起点 580_501 将被注册 W256 B 带 580_501..580_700 拒=staircase affects A 第六次连续 A-hop 预期**；"
    "投影 B naive 580_701..580_900 clean 但落 naive W257 A 窗 580_501..582_500 内——"
    "**above-own-A 承袭 face：W256 B 580_501..580_700 落本波 A 窗之上〔第六次连续〕·W256 A 面 1-hop=staircase affects A〔第五次连续〕·"
    "W257 冻结方禁假设 staircase A-base==prior-B-tail+1 或 B-base==own-A-tail+1 恒等·须重读 live trace·注册 W256 B 带将拒 naive W257 A 窗仅当重叠"
    "——**W257 freezer 承接面强制注记：须在 post-W256 宇宙重 derive 且 derive B 时预留本波 A 窗·W141 先例·never transcribe r587**）"
)

NEW["b8_selftest"] = (
    "selftest W256 face（A=staircase-hop honest-walk past the registered prior-wave B band 断言"
    "（A_hop_chain 与 probe 回执逐跳恒等·A 第五次连续跳=W239 staircase era 后承袭如实注记·A 落位不落任何已注册带内）"
    "·B=own-A reservation 1-hop lands-above-own-A 断言（B_hop_chain 与 probe 回执逐跳恒等·B 落位不落本波 A 窗内=同窗互斥断言·第六次连续 above-own-A 如实注记）·W255 行 parity 腿"
    "**estate 提取面注记**：冻结拼接脚本的 parity estate（W138..W206 69 行 full-span·r858 absorb 代）从**本机 W255 块物理字节**提取"
    "（结构已知·提取自证断言 69 行 range 恒等在场）——W255 块的自有 W239..W254 legs（16 行）不入 estate 路径"
    "·提取后新增 W239..W255 leg（17 行）构成 W256 块 parity 114 行" + WL + "·零假设零风险。"
)

# marker pairs: (block, start_marker, end_marker) -- needles matched on T1 (post-roll faces)
BLOCKS = [
    ("b_band_ab", "（**A 面=STAIRCASE-AFFECTS-A", "已如实披露非分叉）"),
    ("b3_a_bandface", "法典 §4 W256 行 A=576_301..578_300", "非转录 r587·ADMIT 回执在场）"),
    ("b3_b_bandface", "法典 §4 W256 行 B=578_301..578_500", "披露收敛·ADMIT 回执在场）"),
    ("b5_projection", "5. **W256+ 投影（probe 机证 leg4", "verify at W256 prereg，hop 链逐跳在 probe 回执。"),
    ("b7_claim_projection", "·probe W256+ 投影 A naive 578_301..580_300 CLEAN hops=0", "never transcribe r587**）"),
    ("b6_ram", "·W256 冻结窗 2.0G bm-c 实锚", "W240 冻结窗 33.2G bm-a 实锚）"),
    ("b8_selftest", "selftest W256 face（", "零假设零风险。"),
    ("b1_chain_tail", "+W246=bm-a r1016 prereg derive", "W256 freezer 承接面）】。"),
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
    "PERPETUAL-N1-W256", "research/PERPETUAL_N1_W256_PREREG.md",
    "578_501..580_500", "580_501..580_700", "985,335", "558,920", "561,120",
    "n1_w256_results.json", "MSG-20261017-023x-bmc-w256-seat", "fd48643c9",
    "第 254 枚", "第七十六枚", "第 246 波", "第 76 枚",
    "STAIRCASE-AFFECTS-A", "第五次连续 A-hop", "第六次连续 above-own-A",
    "_w256bmc_20261017", "--wave 256", "波号 256",
    "W255=bm-c r1056 prereg derive", "r1057 finalize one-pass",
    "n_eff_held_equal 983,135", "−0.09270819", "0.24503942", "−0.08525445",
    "（**0.3422** 实测锚）", "bm-c 循环班 r1058 freeze 窗", "本窗 free RAM ~3.3GB",
    "→W249 **0.000332**→W250 **0.000331**→W251 **0.000330**→W252 **0.000330**→W253 **0.000329**→W254 **0.000328**→W255 **0.000328**】",
    "queue-head FREEZE-UNBLOCKED lane", "seed_admit_gate rc0 双带 FREE",
    "A base=578501", "B base=580501",
    "bm-c r1057 W255 §7 范式", "bm-c r1057 W255 §8 范式",
    "W257 freezer 承接面", "verify at W257 prereg",
    "selftest W256 face", "W239..W255 leg（17 行）构成 W256 块 parity 114 行",
    "键 W255 实测 K-lift **+0.0001**", "line_merged@K558,920 **1.1946**", "line_pre_w255 1.1945",
    "实差 0.0075 在带内", "已落账键·02:3x", "bm-c r1057 窗 02:3x",
    "r1056/W255 先例 freeze-prep 同式", "253 行单态", "probe leg0 机证 253 行",
    "_w256bmc_freeze_edits", "_w255bmc_freeze_edits", "本波上游链=W1..W255 finalize 全落地",
    "engine_owner==bm-c 75 行注册", "bmc rows 75", "bmc_rows=75",
    "queue-head FREEZE-UNBLOCKED 承接", "A 落位 base==注册前波 B 尾+1（578_500+1）",
    "B 落位 base==本波 A 窗尾+1（580_500+1）",
    "W255 块的自有 W239..W254 legs（16 行）",
    "bm-c r1057 席位", "bm-c r1057 席·queue-head FREEZE-UNBLOCKED 发布",
    "post-W255-REGISTERED 终态注册", "席位窗 probe leg0 实测 253 行",
    "W243/W246/W248/W249/W250/W251/W252/W253/W254/W255 低 RAM 实烧先例", "·W256 冻结窗 3.3G bm-c 实锚",
    "本候选=bm-c 自有席自有波", "R257：W256 带从未指派",
    "B_hop lands-inside-A=false", "B_lands_above_own_A=true", "A_staircase_hop_past_W255_B=true",
    "§5.5 W257+ 投影承接机证", "exit rng=**580_501+j**", "B-ext exit seed=580_501..580_700",
    "A-ext seed=578_501..580_500",
    "probe leg0 bmc_rows=75 attempt-continuity face（r1057 窗算法·bm-c own seat+bmc live rows 75 实读）",
    "578_301..580_300", "578_501..578_700", "580_501..582_500", "580_701..580_900",
    "A_clean_at_naive_start=false",
    "表尾 W255 行", "pre-W256 全二百五十三行注册 N1 带表", "共二百五十三面实测",
    "engine_owner 行 245 注册在册", "freeze 窗 live derive 253 行单态 owner rows 245",
    "W255 splice 先于席位窗已落地",
    "W255 own-wave finalize 已落=席位时即解锁",
    "n1_w255_results.json",
    "924e87b3f02afb72", "7b550e65716e0ada", "d4a9d7164ba9490e", "c6dfb4291c09be1e",
    "e166afc6c", "b1414b81a", "f931cf102", "72d292ea3",
    "sixgate PRE-FINALIZE 17th consecutive",
    "（r1057 席位窗实跑", "（bm-c r1057 席位",
    "zero post-splice heal", "e2c4b543e", "3eb691575", "fa2bc55e5", "c211d1269",
]
for s in MUST:
    assert s in T2, "MUST-HAVE missing: %r" % s

MUST_NOT = [
    "**A-ext seed=576_301", "571_901", "571_900", "567_501", "567_500", "545_301", "545_300", "545_500", "565_501",
    "FIRST-CLEAN·hops=0", "13-HOP", "13 hops", "A_hop_chain=[] 空集", "A_clean_at_naive_start=true",
    "573_901..574_100", "573_900", "573_901",
    "−0.09273764", "0.24503097", "−0.09241377", "**0.3092**", "实差 0.0003 在带内",
    "line_merged@K556,720", "556,720 合并池", "累计 null 池=556,720",
    "cb79242ed", "MSG-20261016-22xx", "bmc-w255-seat", "第 75 枚", "第七十五枚", "第 253 枚", "第 245 波",
    "engine_owner 行 244", "owner rows 244", "bmc rows 74", "bmc_rows=74", "engine_owner==bm-c 74",
    "252 行", "二百五十二行注册", "二百五十二面实测", "251 行", "二百五十一行注册", "二百五十一面实测",
    "r1055 窗算法", "（bm-c r1055 席", "（r1055 席位窗实跑",
    "bm-c r1055 窗 21:3x", "bm-c 循环班 r1056", "live-read r1056", "已落账键·21:3x",
    "波号 255", "--wave 255", "R256：W255",
    "verify at W256 prereg", "W256 freezer 承接面", "W256p_", "W256 冻结方",
    "键 W252 实测 K-lift", "键 W253 实测 K-lift", "键 W254 实测 K-lift **−0.0001**", "line_pre_w253", "line_pre_w254",
    "（**B 面=CLEAN", "waits-upstream ARMED",
    "（bm-c r1043 席", "第 73 枚",
    "selftest W255 face", "本窗 free RAM ~1.3GB",
    "第四次连续 A-hop", "第五次连续 above-own-A",
    "571_901..573_900", "573_901..575_900", "574_101..574_300",
    "576_101..578_100", "576_301..576_500",
    "·W255 冻结窗 2.0G",
    "_w255bmc_20261016",
]
for s in MUST_NOT:
    assert s not in T2, "MUST-NOT-HAVE present: %r (count=%d)" % (s, T2.count(s))

# projection-fulfillment count gates
assert T2.count("W256+ 投影") == 0, "W256+ 投影 count=%d (expect 0)" % T2.count("W256+ 投影")
assert T2.count("W257+ 投影") == 4, "W257+ 投影 count=%d (expect 4 = b1 tail + b5 title + b7 claim + sec8 rolled)" % T2.count("W257+ 投影")
assert T2.count("hops=1") == 2, "hops=1 count=%d (expect 2 = 带位 A + §3 A)" % T2.count("hops=1")
assert T2.count("第四次连续 A-hop") == 0, "第四次连续 A-hop count=%d (expect 0)" % T2.count("第四次连续 A-hop")
assert T2.count("第五次连续 A-hop") == 3, "第五次连续 A-hop count=%d (expect 3 = b_band_ab x2 + b3_a x1 own faces)" % T2.count("第五次连续 A-hop")
assert T2.count("第六次连续 A-hop") == 3, "第六次连续 A-hop count=%d (expect 3 = b5 pre-registered face x2 + b7 projection face)" % T2.count("第六次连续 A-hop")
assert T2.count("第六次连续") == 7, "第六次连续 count=%d (expect 7 = A-hop x3 + above-own-A x3 + 〔第六次连续〕 x1)" % T2.count("第六次连续")
assert T2.count("第五次连续") == 5, "第五次连续 count=%d (expect 5 = A-hop x3 + 〔第五次连续〕 x1 + b8 连续跳 x1; same-window needle heal: gate authored 4, b8 第五次连续跳 face is the W255-generation 第四次连续跳 structural twin, disclosed)" % T2.count("第五次连续")
assert T2.count("第五次连续 above-own-A") == 0, "第五次连续 above-own-A count=%d (expect 0)" % T2.count("第五次连续 above-own-A")
assert T2.count("第四次连续 above-own-A") == 0, "第四次连续 above-own-A count=%d (expect 0)" % T2.count("第四次连续 above-own-A")
assert T2.count("578_301..580_300") == 4, "578_301..580_300 count=%d (expect 4 = b_band_ab x3 [续带 + hop-chain verbatim + 投影兑现 quote] + b3_a x1 W256 A naive)" % T2.count("578_301..580_300")
assert T2.count("578_501..578_700") == 4, "578_501..578_700 count=%d (expect 4 = b_band_ab x3 [B naive 续带 + naive-B-落 A 窗内 + 投影兑现 tail] + b3_b x1 W256 B naive)" % T2.count("578_501..578_700")
assert T2.count("576_101..578_100") == 0, "576_101..578_100 count=%d (expect 0 = block-replaced)" % T2.count("576_101..578_100")
assert T2.count("576_301..576_500") == 0, "576_301..576_500 count=%d (expect 0 = block-replaced)" % T2.count("576_301..576_500")

# residue scan: all X_Y..X_Y windows well-formed
for m in re.finditer(r"(\d{3}_\d{3})\.\.(\d{3}_\d{3})", T2):
    lo = int(m.group(1).replace("_", "")); hi = int(m.group(2).replace("_", ""))
    assert lo <= hi, "malformed window %s" % m.group(0)

io.open(OUT, "w", encoding="utf-8", newline="").write(T2)
print("W256 PREREG DERIVE OK -> %s (%d bytes, %d lines)" % (OUT, len(T2.encode("utf-8")), T2.count("\n") + 1))
print("freeze window face: bm-c 循环班 r1058 freeze 窗 2026-10-17 %s" % FREEZE_T)
print("blocks replaced: %s" % ", ".join(n for n, _, _ in BLOCKS))
print("vmap legs: %d floors: %d post-legs: %d MUST: %d MUST_NOT: %d" % (len(VMAP), len(VMAP_FLOORS), len(VMAP_POST_LEGS), len(MUST), len(MUST_NOT)))
print("src blob-verified == f353e49f3486957b1b274254f0c0368a51a5c2fc @ 72d292ea3 (frozen pre-run face; HEAD post-backfill twin b2f6e5d2 disclosed, NOT used)")
