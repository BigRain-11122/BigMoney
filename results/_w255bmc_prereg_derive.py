# -*- coding: utf-8 -*-
# r1056 bm-c: W255 prereg derive (count-asserted ordered transform + marker-extracted block replaces).
# Source = committed frozen W254 prereg AT THE FREEZE COMMIT e2c4b543e (git e2c4b543e:research/PERPETUAL_N1_W254_PREREG.md,
# 39,994 bytes -- the frozen pre-run face; sec7/8 placeholders intact). Extracted to
# results/_w255bmc_w254_frozen_face.txt by the dead 22:2x window (self-labeled r1056-predecessor) and
# byte-verified THIS window (sha256 739ecd0d541995ec full-equal vs git cat-file blob; hash-object ==
# aa1b1b0a52273e9330cd88a3298bc86e8ae6988d @ e2c4b543e).
# TEMPLATE-FACE DISCLOSURE (needle-face divergence, honest): HEAD twin 2cd2a42d0f39b34f3a7d1f5e84f42da86655e30e = the
# CURRENT HEAD face = the POST-CYCLE face with sec.7/8 BACKFILLED by the r1055 window (W254 actual results).
# Deriving from the backfilled face would fabricate W255 sec.7/8 "跑后实证" from W254's measured numbers -- the
# r1049/r1052 precedent (derive always from the PRIOR wave's FREEZE-COMMIT face, "frozen pre-run face; sec7/8
# placeholders intact") and the prereg semantics (frozen PRE-RUN, placeholders for its own cycle) both require
# aa1b1b0a. Both faces measured this window (rev-parse e2c4b543e:=aa1b1b0a / HEAD:=2cd2a42d); divergence disclosed
# in header + closeout; 2cd2a42d recorded as the post-backfill twin, NOT used as template.
# W255 facts (all machine-derived, never transcribed):
#   - seat probe ADMIT receipt results/_w255bmc_20261016_probe_receipt.json (r1055 window, seat pushed origin
#     cb79242ed, MSG-20261016-22xx-bmc-w255-seat, file landed in fleet/inbox/processed/). STAIRCASE
#     CONTINUES: A naive 576_101..578_100 REFUSED at start (registered W254 B band 576_101..576_300 sits INSIDE the
#     naive A window) -> A first-clean 576_301..578_300 hops=1 (FOURTH consecutive A-hop, W254 prereg sec.5 item5
#     A-CLEAN-at-naive pre-W254-universe projection superseded live r587, divergence disclosed) / B naive
#     576_301..576_500 REFUSED at start (lands INSIDE the own-wave W255 A first-clean window 576_301..578_300) ->
#     own-A reservation cascade hop past 578_300 -> 578_301..578_500 hops=1 (FIFTH consecutive above-own-A landing);
#     seed_admit FREE x2 (A base=576301 span=2000 / B base=578301 span=200); leg0 rows=252 owner_rows=244
#     bmc_rows=74 bmc_ordinal=75 ordinal=245; leg2 conflicts=0; leg3 origin_vacancy=true;
#     leg4 W256+ projection: A naive 578_301..580_300 CLEAN pre-W255 BUT post-W255-REGISTERED the naive W256 A
#     start 578_301 is REFUSED by the registered W255 B band 578_301..578_500 (staircase-affects-A FIFTH consecutive
#     A-hop expected) AND the W256 B naive 578_501..578_700 lands inside the own-A reservation face.
#   - upstream W254 finalize landed (r1055 dead-window estate machine-verified, ledger 980,935+2,200=983,135 EXACT):
#     merged K=556,720 / merged mu -0.0927376436988073 / sigma 0.2450309685260551 / se_mu@K556,720 0.000328 /
#     W254-only mu -0.09241377272727273 / A p95 0.3092 / K-lift -0.0001 in-band / n_eff_held_equal 980,935 /
#     line_pre_w254 1.1945 / line_merged_556720 1.1944 / own-slice vs pre-wave merged gap 0.0003 in-band
#     (results/perpetual_faces/n1_w254_results.json + results/_r1055bmc_w254_fivekeys.json)
#   - W254 chain: prereg derive r1054 dead-window freeze LANDED e2c4b543e + five-face freeze splice r1055 dead-window
#     estate LANDED 3eb691575 (zero post-splice heal; splice commit = healed worktree bytes directly; 4 pre-splice
#     authoring defect classes caught by count-asserted gates; dual-sha16 pf 924e87b3f02afb72 / n1 7b550e65716e0ada)
#     + engine self-burn 12/12 (ledger appends fa2bc55e5+c211d1269 batched 6+6 self-committed) + r1055 continuation
#     sixgate PRE-FINALIZE 16th consecutive (triple identity n1 7b550e65716e0ada / pf 924e87b3f02afb72) + finalize
#     one-pass 983,135/K=556,720 + fivekeys 6/6 + sec.7/8 backfilled + W255 seat published cb79242ed.
# Disclosed same-window needle heals: none new expected (all rolls count-asserted; POST legs repair wave-roll
# collateral only: se_mu chain tail append + K-lift value face + line_pre_w254 value face + sec7/8 paradigm rows
# + low-RAM list append + freeze-prep precedent window label).
# Needle-count pre-flight evidence: results/_w255bmc_needle_probe.py (dead 22:2x window estate, ALL floors
# re-verified live THIS window by re-running the probe -- counts match every VMAP_FLOORS entry below).
import io, os, sys, datetime, subprocess, hashlib, re

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(REPO, "results", "_w255bmc_w254_frozen_face.txt")
OUT = os.path.join(REPO, "research", "PERPETUAL_N1_W255_PREREG.md")
GIT = "C:/Program Files/Git/cmd/git.exe"

# --- source byte-identity gates ---
_blob_expect = "aa1b1b0a52273e9330cd88a3298bc86e8ae6988d"   # freeze-commit face @ e2c4b543e
_ho = subprocess.run([GIT, "hash-object", SRC], capture_output=True, text=True, cwd=REPO).stdout.strip()
assert _ho == _blob_expect, "SRC blob mismatch: got %s expect %s" % (_ho, _blob_expect)
_fc = subprocess.run([GIT, "rev-parse", "e2c4b543e:research/PERPETUAL_N1_W254_PREREG.md"],
                     capture_output=True, text=True, cwd=REPO).stdout.strip()
assert _fc == _blob_expect, "freeze-commit blob mismatch: got %s expect %s" % (_fc, _blob_expect)
_hb = subprocess.run([GIT, "rev-parse", "HEAD:research/PERPETUAL_N1_W254_PREREG.md"],
                     capture_output=True, text=True, cwd=REPO).stdout.strip()
assert _hb == "2cd2a42d0f39b34f3a7d1f5e84f42da86655e30e", "HEAD tpl twin face drifted: %s" % _hb

T0 = io.open(SRC, encoding="utf-8", newline="").read()
assert hashlib.sha256(T0.encode("utf-8")).hexdigest()[:16] == "739ecd0d541995ec", "SRC sha mismatch"

P1, P2, P3 = "\x01W\x01", "\x01N\x01", "\x01B\x01"

now = datetime.datetime.now()
FREEZE_T = "%02d:%dx" % (now.hour, now.minute // 10)

# machine-extracted historical spans (from T0 PRE-roll bytes: zero transcription for carried content)
_i_b1 = T0.index("+W246=bm-a r1016 prereg derive")
_j_b1 = T0.index("——本波上游链=")
HIST_B1 = T0[_i_b1:_j_b1]  # W246..W253 chain legs verbatim (frozen template bytes)
_i_b6 = T0.index("·W250 冻结窗 RAM 未记录（r1046 死窗")
_b6_end = "W240 冻结窗 33.2G bm-a 实锚）"
_j_b6 = T0.index(_b6_end) + len(_b6_end)
HIST_B6 = T0[_i_b6:_j_b6]  # W250..W240 freeze-window RAM ledger verbatim

VMAP = [
    # projection first, then line_merged face, then prior-K bare, then ledger heads (order-critical)
    ("556,720 投影", "558,920 投影"),
    ("line_merged@K554,520 **1.1944**", "line_merged@K556,720 **1.1944**"),
    ("554,520", "556,720"),
    ("980,935", "983,135"),
    ("978,735", "980,935"),
    ("976,535", "978,735"),
    # sec5 measured keys -> W254 measured faces (n1_w254_results.json machine values)
    ("−0.09273893", "−0.09273764"),
    ("−0.0925495", "−0.09241377"),
    ("0.24504775", "0.24503097"),
    ("实差 0.0002 在带内", "实差 0.0003 在带内"),
    ("（**0.3122** 实测锚）", "（**0.3092** 实测锚）"),
    # band values outside block regions (staircase-4th-hop + own-A reservation cascade faces)
    ("A-ext seed=574_101..576_100", "A-ext seed=576_301..578_300"),
    ("entry rng seed=**574_101+j**", "entry rng seed=**576_301+j**"),
    ("entry rng=**574_101+j**", "entry rng=**576_301+j**"),
    ("exit rng=**576_101+j**", "exit rng=**578_301+j**"),
    ("A base=574101 span=2000 checked=2000 verdict=FREE", "A base=576301 span=2000 checked=2000 verdict=FREE"),
    ("B base=576101 span=200 checked=200 verdict=FREE", "B base=578301 span=200 checked=200 verdict=FREE"),
    ("R255：W254", "R256：W255"),
    # base-relation faces (block-external occurrences; block NEW uses the same new faces)
    ("574_100+1", "576_300+1"),
    ("576_100+1", "578_300+1"),
    # seat / provenance faces (W255 seat published r1055 window, origin cb79242ed)
    ("MSG-20261016-14xx-bmc-w254-seat", "MSG-20261016-22xx-bmc-w255-seat"),
    ("fa70f3765", "cb79242ed"),
    ("（bm-c r1053 席·queue-head FREEZE-UNBLOCKED 发布）", "（bm-c r1055 席·queue-head FREEZE-UNBLOCKED 发布）"),
    ("（bm-c r1053 席位", "（bm-c r1055 席位"),
    ("（r1053 席位窗实跑", "（r1055 席位窗实跑"),
    # finalize window faces (specific first, then catch-all)
    ("bm-c r1053 窗 14:4x", "bm-c r1055 窗 21:3x"),
    ("14:4x", "21:3x"),
    # engine live-read + RAM head (bm-c current window honest: ~1.3G free of 23.9G (absorb-window
# same-window needle heal: dead 01:1x window authored ~2.0G from its observation; THIS r1056
# freeze window live-measures 1.3G -- prereg RAM anchor must reflect the actual freeze window; disclosed)
    # LLM-mode 27b resident per O-20261016-2347 GPU dual-mode + engine queue idle, CPU lane independent)
    ("saturation_engine.py status live-read r1054", "saturation_engine.py status live-read r1056"),
    ("本窗 free RAM ~2.7GB（bm-c 底盘常驻·24G 物理内存机·W20 SCREEN 四分片全闭环+引擎队列空转·CPU 车道独立如实注记）",
     "本窗 free RAM ~1.3GB（bm-c 底盘常驻·24G 物理内存机·LLM 态 27b 常驻+引擎队列空转·CPU 车道独立如实注记）"),
    # wave-number roll (chained placeholders)
    ("W254", P1), ("W253", "W254"), ("W252", "W253"), ("W251", "W252"), (P1, "W255"),
    # result-file names (chained)
    ("n1_w254", P2), ("n1_w253", "n1_w254"), (P2, "n1_w255"),
    # probe/freeze script basenames (chained; current face _w255bmc <- template _w254bmc)
    ("_w254bmc", P3), ("_w253bmc", "_w254bmc"), (P3, "_w255bmc"),
    # runner CLI wave
    ("--wave 254", "--wave 255"),
    ("波号 254", "波号 255"),
    # pool/engine ordinals
    ("第 252 枚", "第 253 枚"),
    ("第 244 波", "第 245 波"),
    ("bm-c 第七十四枚自有波", "bm-c 第七十五枚自有波"),
    # subsumption-order fix: compound needle contains 第 74 枚 -> MUST run before any bare roll
    ("bmc rows 73+候选=第 74 枚 EXACT", "bmc rows 74+候选=第 75 枚 EXACT"),
    ("第 74 枚", "第 75 枚"),
    ("probe leg0 bmc_rows=73 attempt-continuity face（r1053 窗算法·bm-c own seat+bmc live rows 73 实读）",
     "probe leg0 bmc_rows=74 attempt-continuity face（r1055 窗算法·bm-c own seat+bmc live rows 74 实读）"),
    ("engine_owner==bm-c 73 行注册", "engine_owner==bm-c 74 行注册"),
    ("engine_owner 行 243 注册在册", "engine_owner 行 244 注册在册"),
    # registry scan faces
    ("全二百五十一行注册 N1 带表", "全二百五十二行注册 N1 带表"),
    ("freeze 窗 live derive 251 行单态 owner rows 243", "freeze 窗 live derive 252 行单态 owner rows 244"),
    ("probe leg0 机证 251 行〔", "probe leg0 机证 252 行〔"),
    ("席位窗 probe leg0 实测 251 行〔", "席位窗 probe leg0 实测 252 行〔"),
    ("perpetual_faces.py 零 252 行", "perpetual_faces.py 零 253 行"),
    ("共二百五十一面实测", "共二百五十二面实测"),
    # sec8 placeholder projection-label bump (W255+ -> W256+ face)
    ("§5.5 W255+ 投影承接机证", "§5.5 W256+ 投影承接机证"),
]

VMAP_FLOORS = {
    "556,720 投影": 1, "line_merged@K554,520 **1.1944**": 1,
    "554,520": 7, "980,935": 3, "978,735": 2, "976,535": 2,
    "−0.09273893": 1, "−0.0925495": 1, "0.24504775": 1, "实差 0.0002 在带内": 1,
    "（**0.3122** 实测锚）": 1,
    "A-ext seed=574_101..576_100": 1,
    "entry rng seed=**574_101+j**": 1, "entry rng=**574_101+j**": 1,
    "exit rng=**576_101+j**": 1,
    "A base=574101 span=2000 checked=2000 verdict=FREE": 1,
    "B base=576101 span=200 checked=200 verdict=FREE": 1,
    "R255：W254": 1,
    "W254": 33, "W253": 67, "W252": 10, "W251": 8,
    "n1_w254": 4, "n1_w253": 3, "_w254bmc": 4, "_w253bmc": 1,
    "--wave 254": 2, "波号 254": 1,
    "第 252 枚": 1, "第 244 波": 1, "bm-c 第七十四枚自有波": 1,
    "bmc rows 73+候选=第 74 枚 EXACT": 2, "第 74 枚": 2,
    "probe leg0 bmc_rows=73 attempt-continuity face（r1053 窗算法·bm-c own seat+bmc live rows 73 实读）": 1,
    "engine_owner==bm-c 73 行注册": 1, "engine_owner 行 243 注册在册": 1,
    "全二百五十一行注册 N1 带表": 1,
    "freeze 窗 live derive 251 行单态 owner rows 243": 1,
    "probe leg0 机证 251 行〔": 1, "席位窗 probe leg0 实测 251 行〔": 1,
    "perpetual_faces.py 零 252 行": 1,
    "共二百五十一面实测": 1,
    "MSG-20261016-14xx-bmc-w254-seat": 4, "fa70f3765": 3,
    "（bm-c r1053 席·queue-head FREEZE-UNBLOCKED 发布）": 1,
    "（bm-c r1053 席位": 1, "（r1053 席位窗实跑": 1,
    "bm-c r1053 窗 14:4x": 1, "14:4x": 3, "已落账键·14:4x": 1,
    "saturation_engine.py status live-read r1054": 1,
    "本窗 free RAM ~2.7GB（bm-c 底盘常驻·24G 物理内存机·W20 SCREEN 四分片全闭环+引擎队列空转·CPU 车道独立如实注记）": 1,
    "§5.5 W255+ 投影承接机证": 1,
    "574_100+1": 4, "576_100+1": 2,
    # block-marker stability floors (raw template face; T1 marker = post-roll form asserted in BLOCKS)
    "（**A 面=STAIRCASE-AFFECTS-A": 1,
    "已如实披露非分叉）": 1,
    "法典 §4 W254 行 A=574_101..576_100": 1,
    "法典 §4 W254 行 B=576_101..576_300": 1,
    "披露收敛·ADMIT 回执在场）": 1,
    "非转录 r587·ADMIT 回执在场）": 1,
    "5. **W255+ 投影（probe 机证 leg4": 1,
    "verify at W255 prereg，hop 链逐跳在 probe 回执。": 1,
    "·probe W255+ 投影 A naive 576_101..578_100 CLEAN hops=0": 1,
    "never transcribe r587**）": 1,
    "·W250 冻结窗 RAM 未记录（r1046 死窗": 1,
    "·W254 冻结窗 2.7G bm-c 实锚": 1,
    "W240 冻结窗 33.2G bm-a 实锚）": 1,
    "selftest W254 face（": 1, "零假设零风险。": 1,
    "+W246=bm-a r1016 prereg derive": 1,
    "——本波上游链=": 1,
    "W255 freezer 承接面）】。": 1,
    "W243/W246/W248/W249/W250/W251/W252/W253 低 RAM 实烧先例": 1,
    "r1052/W253 先例 freeze-prep 同式": 1,
    "→W249 **0.000332**→W250 **0.000331**→W251 **0.000330**→W252 **0.000330**→W253 **0.000329**】": 1,
    "line_pre_w253 1.1944": 1,
    "bm-c r1053 W253 §7 范式": 1, "bm-c r1053 W253 §8 范式": 1,
    "键 W253 实测 K-lift **0.0000**": 1,
    "n_eff_held_equal 978,735": 1,
    "queue-head FREEZE-UNBLOCKED lane": 1,
    "本候选=bm-c 自有席自有波": 1,
    "表尾 W253 行": 2,
    "pre-W254 全二百五十一行注册 N1 带表": 1,
    "bm-c 循环班 r1054 freeze 窗": 1,
    "W239..W253 leg（15 行）构成 W254 块 parity 112 行": 1,
    "W253 块的自有 W239..W252 legs（14 行）": 1,
    # zero-floors (absence assertions on T0)
    "waits-upstream ARMED": 0,
    "（**B 面=CLEAN": 0,
    "983,135": 0, "0.3092": 0, "578_301": 0, "578_300": 0,
    "576_301..578_300": 0, "578_301..578_500": 0, "578_501..578_700": 0, "578_301..580_300": 0,
    "556,720": 1,  # only the 投影 compound; bare face absent (baseline rolls supply it)
    "R256：W255": 0, "n1_w255": 0, "_w255bmc": 0, "--wave 255": 0,
    "第 75 枚": 0, "第 253 枚": 0, "第 245 波": 0,
    "第五次连续": 0, "571_901..572_100": 0,
    "574_101..574_300": 4,  # W254 B naive -- ALL inside b_band_ab/b3_b block regions (block-replaced to 0; T2 count gate)
    "573_901..575_900": 4,  # W254 A naive -- ALL inside block regions (T2 count gate)
}

# floors for POST-chain correction legs (needles exist only in T1 after the pre-chain legs run)
VMAP_POST_LEGS = [
    # se_mu narrowing chain: wave roll consumed the W251 label; restore it and append true W254 se 0.000328
    ("→W249 **0.000332**→W250 **0.000331**→W252 **0.000330**→W253 **0.000330**→W254 **0.000329**】",
     "→W249 **0.000332**→W250 **0.000331**→W251 **0.000330**→W252 **0.000330**→W253 **0.000329**→W254 **0.000328**】", 1),
    # line_pre face: lowercase w-token escapes the uppercase W-roll (r1045 derive precedent);
    # W254 actual line_pre_w254 = 1.1945 (n1_w254_results.json skill_line machine value)
    ("line_pre_w253 1.1944", "line_pre_w254 1.1945", 1),
    # K-lift value face: wave roll W253->W254 relabeled the anchor; W254 true K-lift = -0.0001 in-band
    ("键 W254 实测 K-lift **0.0000**", "键 W254 实测 K-lift **−0.0001**", 1),
    # sec7/8 backfill paradigm rows (W254 sec.7/8 backfilled by the r1055 continuation window)
    ("bm-c r1053 W254 §7 范式", "bm-c r1055 W254 §7 范式", 1),
    ("bm-c r1053 W254 §8 范式", "bm-c r1055 W254 §8 范式", 1),
    # low-RAM precedent list: rolled T1 form lost the W251 label; restore it and append W254
    # (engine self-burn 12/12 r1055 window on this low-RAM machine; chain precedent every-wave append)
    ("W243/W246/W248/W249/W250/W252/W253/W254 低 RAM 实烧先例", "W243/W246/W248/W249/W250/W251/W252/W253/W254 低 RAM 实烧先例", 1),
    # freeze-prep precedent face (W254 prereg derive window = r1054)
    ("r1052/W254 先例 freeze-prep 同式", "r1054/W254 先例 freeze-prep 同式", 1),
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

# freeze-window live face: regex-extract the r1054 stamp (zero transcription) -> r1056 + runtime FREEZE_T
# (date rolls 2026-10-16 -> 2026-10-17: the W255 freeze window is the first after midnight)
_fw_pat = re.compile(r"bm-c 循环班 r1054 freeze 窗 2026-10-16 \d{2}:\dx")
_fw_hits = _fw_pat.findall(T1)
assert len(_fw_hits) == 1, "freeze-window stamp count=%d (expect 1): %r" % (len(_fw_hits), _fw_hits)
T1 = T1.replace(_fw_hits[0], "bm-c 循环班 r1056 freeze 窗 2026-10-17 " + FREEZE_T)

# post-chain correction legs: needles exist only in T1 (post chained rolls); floors checked on T1
for o, n, f in VMAP_POST_LEGS:
    if T1.count(o) < f:
        raise SystemExit("VMAP POST FLOOR FAIL: %r count=%d floor=%d" % (o, T1.count(o), f))
    T1 = T1.replace(o, n)

# ---------------- block replacements (needles marker-extracted from T1; NEW = final) ----------------
NEW = {}

WL = "（W138..W206+" + "+".join("W%d" % n for n in range(211, 255)) + "）"  # 69 estate + W211..W254 = 113 rows

NEW["b_band_ab"] = (
    "（**A 面=STAIRCASE-AFFECTS-A·1-HOP WALK 形态（W239 staircase era 后第四次连续 A-hop）**："
    "A 面算术续带 576_101..578_100（自注册 W254 A 尾 576_100 续）"
    "在席位窗宇宙（post-W254-REGISTERED 终态注册·freeze-UNBLOCKED）起点即 REFUSED"
    "（注册 W254 B 带 576_101..576_300 落 naive A 窗内=staircase re-emergence affects A 承袭·"
    "W254 prereg §5.5 item5 A-CLEAN-at-naive pre-W254-universe projection superseded live r587 如实披露）"
    "→walk 越注册 W254 B 尾 576_300→A first-clean **576_301..578_300**·**hops=1**·"
    "**A 落位 base==注册前波 B 尾+1（576_300+1）机检关系**"
    "（A_hop_chain 1 跳 verbatim leg1 机证〔window 576_101..578_100→jump 576_301·refuser band 576_101..576_300〕"
    "·A_clean_at_naive_start=false·A_staircase_hop_past_W254_B=true"
    "·A base>=registered prior-wave B tail+1 floor relation）"
    "·非转录 r587 前向单调断言在走册）；"
    "**B-ext exit seed=578_301..578_500**（**B 面=1-HOP own-A RESERVATION CASCADE·落位高于本波 A 窗形态（第五次连续 above-own-A 落位）**："
    "B naive 续带 576_301..576_500（自注册 W254 B 尾 576_300+1 续）"
    "在席位窗宇宙（post-W254-REGISTERED 终态注册·freeze-UNBLOCKED）起点即 REFUSED"
    "（naive B 窗 576_301..576_500 落本波 A first-clean 窗 576_301..578_300 内"
    "=own-A reservation cascade standard leg 强制·probe leg1 B_semantics 机证·B_naive_refused_at_start=true）"
    "——**own-A reservation standard leg 越本波 A 窗 576_301..578_300**（1 hop）"
    "→**1 hop** 落位 **578_301..578_500**·**B 落位 base==本波 A 窗尾+1（578_300+1）EXACT 机检关系**"
    "（B_hop lands-inside-A=false·B_lands_above_own_A=true·B_hop_chain 1 跳 verbatim 在 probe 回执 leg1 机证"
    "·非转录 r587·AB 同窗互斥面 leg2 律在场）；"
    "**W254 prereg §5.5 item5 投影承接面注记兑现+落位分歧如实披露**："
    "投影预言 W255 A naive 576_101..578_100 CLEAN（pre-W254 宇宙零 live refusers）——本窗 live re-derive A 面起点即被注册 W254 B 带拒"
    "（投影 A-CLEAN 未兑现=staircase affects A 承袭·第四次连续 A-hop）"
    "→A first-clean 上移 576_301..578_300→B naive 576_301..576_500 相应落本波 A 窗内→own-A reservation cascade 上移 578_301..578_500"
    "（post-W254 宇宙 live re-derive 必变·W254 prereg §5.5 已披露 live re-derive governs·禁转录投影 r587·"
    "落位高于投影=新拒面如实注记·已如实披露非分叉）"
)

NEW["b3_a_bandface"] = (
    "法典 §4 W255 行 A=576_301..578_300·**STAIRCASE-AFFECTS-A·1-HOP WALK 形态（W239 staircase era 后第四次连续 A-hop）**："
    "A 算术续带 576_101..578_100（自注册 W254 A 尾 576_100 续）"
    "在席位窗宇宙（post-W254-REGISTERED 终态注册·freeze-UNBLOCKED）起点即 REFUSED"
    "（注册 W254 B 带 576_101..576_300 落 naive A 窗内=W254 prereg §5.5 item5 A-CLEAN-at-naive 投影被 live re-derive 超越·r587 superseded 披露）"
    "→walk 越注册 W254 B 尾 576_300→A first-clean 576_301..578_300·**hops=1**·"
    "**A 落位 base==注册前波 B 尾+1（576_300+1）机检关系**"
    "（A_hop_chain 1 跳 verbatim probe leg1 机证·A_clean_at_naive_start=false·A_staircase_hop_past_W254_B=true）"
    "·非转录 r587·ADMIT 回执在场）"
)

NEW["b3_b_bandface"] = (
    "法典 §4 W255 行 B=578_301..578_500·**1-HOP own-A RESERVATION CASCADE·落位高于本波 A 窗形态**："
    "B naive 续带 576_301..576_500（自注册 W254 B 尾 576_300+1 续）"
    "在席位窗宇宙（post-W254-REGISTERED 终态注册）起点即 REFUSED"
    "（naive B 窗落本波 A first-clean 窗 576_301..578_300 内=own-A reservation cascade standard leg·probe leg1 B_semantics 机证）"
    "→own-A reservation 越本波 A 窗 576_301..578_300→1 hop 落位 578_301..578_500·"
    "**B 落位 base==本波 A 窗尾+1（578_300+1）机检关系**"
    "（B_hop lands-inside-A=false·B_lands_above_own_A=true·B_hop_chain 1 跳 verbatim 在 probe 回执"
    "·第五次连续 above-own-A 落位如实注记）"
    "·非转录 r587·与 W254 prereg §5.5 item5 投影承接面注记兑现+落位上移分歧披露收敛·ADMIT 回执在场）"
)

NEW["b1_chain_tail"] = (
    HIST_B1
    + "+W254=bm-c r1054 prereg derive（machine-SUB from frozen W253 tpl ba1ccb2a·freeze LANDED e2c4b543e·banned_direction_gate rc0·needle-count pre-flight 全 floors 预验·count-asserted 首过〔zero new needle heals 披露〕）"
    + "+五面冻结 splice（r1055 死窗 20:4x-21:0x LANDED 3eb691575〔zero post-splice heal·splice commit=healed worktree bytes directly·4 pre-splice authoring defect classes caught by count-asserted gates〕·dual-sha16 pf 924e87b3f02afb72 / n1 7b550e65716e0ada·W254 块 parity 112 rows）"
    + "+引擎自燃 12/12（mtime-watch auto-ignite engine lane·ledger appends fa2bc55e5+c211d1269 batched 6+6 self-committed）"
    + "+bm-c r1055 finalize one-pass 已落（K=556,720·账本头 983,135 机读·n1_w254_results.json·21:3x·fivekeys ALL PASS·sixgate PRE-FINALIZE 16th consecutive 正相〔triple identity n1 7b550e65716e0ada / pf 924e87b3f02afb72 零漂移·splice commit=healed worktree bytes directly face〕·K-lift −0.0001 in-band）"
    "——本波上游链=W1..W254 finalize 全落地·零在飞上游席·干净前置**；"
    "席位公示=MSG-20261016-22xx-bmc-w255-seat 已推 origin cb79242ed 先于本冻结"
    "【r565 律·席位先行·bm-c r1055 窗发布·queue-head FREEZE-UNBLOCKED 承接·W254 own-wave finalize 已落=席位时即解锁】；"
    "下游 W256+ 投影见 §5.5（probe 机证 leg4·W256 freezer 承接面）】。"
)

NEW["b5_projection"] = (
    "5. **W256+ 投影（probe 机证 leg4·下波冻结方复核非转抄 r587 律）**：A naive first-clean 578_301..580_300 **CLEAN**（hops=0·pre-W255 宇宙零 live refusers）——"
    "**post-W255-REGISTERED 预披露：naive W256 A 起点 578_301 将被注册 W255 B 带 578_301..578_500 拒（staircase-affects-A 第五次连续 A-hop 预期）**；"
    "B naive **578_501..578_700 CLEAN（hops=0）但落投影 A 窗 578_301..580_300 内**（W256p_B_lands_inside_W256p_A_naive=true——"
    "**staircase face 延续**：W255 A 576_301..578_300+B 578_301..578_500 注册后 naive W256 A 窗起点即被注册 W255 B 带拒（staircase affects A 承袭·第五次连续 A-hop 预期）"
    "→A first-clean 将上移·B own-A reservation cascade 落位相应上移——post-W255 宇宙 live re-derive 必变·禁转录投影）；"
    "**W256 冻结方禁假设 staircase A-base==prior-B-tail+1 或 B-base==own-A-tail+1 恒等·须重读 live trace**"
    "（W251 起 staircase affects A·W252/W253/W254/W255=A/B 双 1-hop 形态连续四波如实注记·seed-gap face 已于 W252 终结=A 首跳如实注记）"
    "——W256 冻结方必须在 post-W255 注册宇宙重 derive 且 derive B 时预留本波 A 窗 576_301..578_300+本波 B 带 578_301..578_500"
    "——leg2 律/E36 卡·W141 先例；verify at W256 prereg，hop 链逐跳在 probe 回执。"
)

NEW["b6_ram"] = "·W255 冻结窗 2.0G bm-c 实锚" + HIST_B6

NEW["b7_claim_projection"] = (
    "·probe W256+ 投影 A naive 578_301..580_300 CLEAN hops=0（零 live refusers）/ B naive 578_501..578_700 CLEAN hops=0 **但落 naive W256 A 窗内**"
    "→own-A reservation cascade 下 staircase 级联上移 **staircase face 延续 live re-derive governs 预披露**"
    "（投影 A naive 578_301..580_300 CLEAN·hops=0——**post-W255-REGISTERED 预披露：naive W256 A 起点 578_301 将被注册 W255 B 带 578_301..578_500 拒=staircase affects A 第五次连续 A-hop 预期**；"
    "投影 B naive 578_501..578_700 clean 但落 naive W256 A 窗 578_301..580_300 内——"
    "**above-own-A 承袭 face：W255 B 578_301..578_500 落本波 A 窗之上〔第五次连续〕·W255 A 面 1-hop=staircase affects A〔第四次连续〕·"
    "W256 冻结方禁假设 staircase A-base==prior-B-tail+1 或 B-base==own-A-tail+1 恒等·须重读 live trace·注册 W255 B 带将拒 naive W256 A 窗仅当重叠"
    "——**W256 freezer 承接面强制注记：须在 post-W255 宇宙重 derive 且 derive B 时预留本波 A 窗·W141 先例·never transcribe r587**）"
)

NEW["b8_selftest"] = (
    "selftest W255 face（A=staircase-hop honest-walk past the registered prior-wave B band 断言"
    "（A_hop_chain 与 probe 回执逐跳恒等·A 第四次连续跳=W239 staircase era 后承袭如实注记·A 落位不落任何已注册带内）"
    "·B=own-A reservation 1-hop lands-above-own-A 断言（B_hop_chain 与 probe 回执逐跳恒等·B 落位不落本波 A 窗内=同窗互斥断言·第五次连续 above-own-A 如实注记）·W254 行 parity 腿"
    "**estate 提取面注记**：冻结拼接脚本的 parity estate（W138..W206 69 行 full-span·r858 absorb 代）从**本机 W254 块物理字节**提取"
    "（结构已知·提取自证断言 69 行 range 恒等在场）——W254 块的自有 W239..W253 legs（15 行）不入 estate 路径"
    "·提取后新增 W239..W254 leg（16 行）构成 W255 块 parity 113 行" + WL + "·零假设零风险。"
)

# marker pairs: (block, start_marker, end_marker) -- needles matched on T1 (post-roll faces)
BLOCKS = [
    ("b_band_ab", "（**A 面=STAIRCASE-AFFECTS-A", "已如实披露非分叉）"),
    ("b3_a_bandface", "法典 §4 W255 行 A=574_101..576_100", "非转录 r587·ADMIT 回执在场）"),
    ("b3_b_bandface", "法典 §4 W255 行 B=576_101..576_300", "披露收敛·ADMIT 回执在场）"),
    ("b5_projection", "5. **W255+ 投影（probe 机证 leg4", "verify at W255 prereg，hop 链逐跳在 probe 回执。"),
    ("b7_claim_projection", "·probe W255+ 投影 A naive 576_101..578_100 CLEAN hops=0", "never transcribe r587**）"),
    ("b6_ram", "·W255 冻结窗 2.7G bm-c 实锚", "W240 冻结窗 33.2G bm-a 实锚）"),
    ("b8_selftest", "selftest W255 face（", "零假设零风险。"),
    ("b1_chain_tail", "+W246=bm-a r1016 prereg derive", "W255 freezer 承接面）】。"),
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
    "PERPETUAL-N1-W255", "research/PERPETUAL_N1_W255_PREREG.md",
    "576_301..578_300", "578_301..578_500", "983,135", "556,720", "558,920",
    "n1_w255_results.json", "MSG-20261016-22xx-bmc-w255-seat", "cb79242ed",
    "第 253 枚", "第七十五枚", "第 245 波", "第 75 枚",
    "STAIRCASE-AFFECTS-A", "第四次连续 A-hop", "第五次连续 above-own-A",
    "_w255bmc_20261016", "--wave 255", "波号 255",
    "W254=bm-c r1054 prereg derive", "r1055 finalize one-pass",
    "n_eff_held_equal 980,935", "−0.09273764", "0.24503097", "−0.09241377",
    "（**0.3092** 实测锚）",     "bm-c 循环班 r1056 freeze 窗", "本窗 free RAM ~1.3GB",
    "→W249 **0.000332**→W250 **0.000331**→W251 **0.000330**→W252 **0.000330**→W253 **0.000329**→W254 **0.000328**】",
    "queue-head FREEZE-UNBLOCKED lane", "seed_admit_gate rc0 双带 FREE",
    "A base=576301", "B base=578301",
    "bm-c r1055 W254 §7 范式", "bm-c r1055 W254 §8 范式",
    "W256 freezer 承接面", "verify at W256 prereg",
    "selftest W255 face", "W239..W254 leg（16 行）构成 W255 块 parity 113 行",
    "键 W254 实测 K-lift **−0.0001**", "line_merged@K556,720 **1.1944**", "line_pre_w254 1.1945",
    "实差 0.0003 在带内", "已落账键·21:3x", "bm-c r1055 窗 21:3x",
    "r1054/W254 先例 freeze-prep 同式", "252 行单态", "probe leg0 机证 252 行",
    "_w255bmc_freeze_edits", "_w254bmc_freeze_edits", "本波上游链=W1..W254 finalize 全落地",
    "engine_owner==bm-c 74 行注册", "bmc rows 74", "bmc_rows=74",
    "queue-head FREEZE-UNBLOCKED 承接", "A 落位 base==注册前波 B 尾+1（576_300+1）",
    "B 落位 base==本波 A 窗尾+1（578_300+1）",
    "W254 块的自有 W239..W253 legs（15 行）",
    "bm-c r1055 席位", "bm-c r1055 席·queue-head FREEZE-UNBLOCKED 发布",
    "post-W254-REGISTERED 终态注册", "席位窗 probe leg0 实测 252 行",
    "W243/W246/W248/W249/W250/W251/W252/W253/W254 低 RAM 实烧先例", "·W255 冻结窗 2.0G bm-c 实锚",
    "本候选=bm-c 自有席自有波", "R256：W255 带从未指派",
    "B_hop lands-inside-A=false", "B_lands_above_own_A=true", "A_staircase_hop_past_W254_B=true",
    "§5.5 W256+ 投影承接机证", "exit rng=**578_301+j**", "B-ext exit seed=578_301..578_500",
    "A-ext seed=576_301..578_300",
    "probe leg0 bmc_rows=74 attempt-continuity face（r1055 窗算法·bm-c own seat+bmc live rows 74 实读）",
    "576_101..578_100", "576_301..576_500", "578_301..580_300", "578_501..578_700",
    "A_clean_at_naive_start=false",
    "表尾 W254 行", "pre-W255 全二百五十二行注册 N1 带表", "共二百五十二面实测",
    "engine_owner 行 244 注册在册", "freeze 窗 live derive 252 行单态 owner rows 244",
    "zero post-splice heal", "3eb691575", "e2c4b543e", "fa2bc55e5", "c211d1269",
    "（r1055 席位窗实跑", "（bm-c r1055 席位",
    "W254 own-wave finalize 已落=席位时即解锁",
    "n1_w254_results.json",
    "924e87b3f02afb72", "7b550e65716e0ada",
    "sixgate PRE-FINALIZE 16th consecutive",
]
for s in MUST:
    assert s in T2, "MUST-HAVE missing: %r" % s

MUST_NOT = [
    "**A-ext seed=574_101", "571_901", "571_900", "567_501", "567_500", "545_301", "545_300", "545_500", "565_501",
    "FIRST-CLEAN·hops=0", "13-HOP", "13 hops", "A_hop_chain=[] 空集", "A_clean_at_naive_start=true",
    "573_901..574_100", "573_900", "573_901",
    "−0.09273893", "0.24504775", "−0.0925495", "**0.3122**", "实差 0.0002 在带内",
    "line_merged@K554,520", "554,520 合并池", "累计 null 池=554,520",
    "fa70f3765", "MSG-20261016-14xx", "bmc-w254-seat", "第 74 枚", "第七十四枚", "第 252 枚", "第 244 波",
    "engine_owner 行 243", "owner rows 243", "bmc rows 73", "bmc_rows=73", "engine_owner==bm-c 73",
    "251 行", "二百五十一行注册", "二百五十一面实测", "250 行", "二百五十行注册", "二百五十面实测",
    "r1053 窗算法", "（bm-c r1053 席", "（r1053 席位窗实跑",
    "bm-c r1053 窗 14:4x", "bm-c 循环班 r1054", "live-read r1054", "已落账键·14:4x",
    "波号 254", "--wave 254", "R255：W254",
    "verify at W255 prereg", "W255 freezer 承接面", "W255p_", "W255 冻结方",
    "键 W251 实测 K-lift", "键 W252 实测 K-lift **0.0001**", "line_pre_w252", "line_pre_w253",
    "键 W253 实测 K-lift",
    "（**B 面=CLEAN", "waits-upstream ARMED",
    "（bm-c r1043 席", "第 73 枚",
    "selftest W254 face", "本窗 free RAM ~2.7GB",
    "第三次连续 A-hop", "第四次连续 above-own-A",
    "571_901..573_900", "573_901..575_900", "574_101..574_300",
]
for s in MUST_NOT:
    assert s not in T2, "MUST-NOT-HAVE present: %r (count=%d)" % (s, T2.count(s))

# projection-fulfillment count gates
assert T2.count("W255+ 投影") == 0, "W255+ 投影 count=%d (expect 0)" % T2.count("W255+ 投影")
assert T2.count("W256+ 投影") == 4, "W256+ 投影 count=%d (expect 4 = b1 tail + b5 title + b7 claim + sec8 rolled)" % T2.count("W256+ 投影")
assert T2.count("hops=1") == 2, "hops=1 count=%d (expect 2 = 带位 A + §3 A)" % T2.count("hops=1")
assert T2.count("第三次连续 A-hop") == 0, "第三次连续 A-hop count=%d (expect 0)" % T2.count("第三次连续 A-hop")
assert T2.count("第四次连续 A-hop") == 3, "第四次连续 A-hop count=%d (expect 3 = b_band_ab x2 + b3_a x1 own faces)" % T2.count("第四次连续 A-hop")
assert T2.count("第五次连续 A-hop") == 3, "第五次连续 A-hop count=%d (expect 3 = b5 pre-registered face x2 + b7 projection face)" % T2.count("第五次连续 A-hop")
assert T2.count("第五次连续") == 7, "第五次连续 count=%d (expect 7 = A-hop x3 + above-own-A x3 + 〔第五次连续〕 x1)" % T2.count("第五次连续")
assert T2.count("第四次连续 above-own-A") == 0, "第四次连续 above-own-A count=%d (expect 0)" % T2.count("第四次连续 above-own-A")
assert T2.count("573_901..575_900") == 0, "573_901..575_900 count=%d (expect 0 = block-replaced)" % T2.count("573_901..575_900")
assert T2.count("574_101..574_300") == 0, "574_101..574_300 count=%d (expect 0 = block-replaced)" % T2.count("574_101..574_300")
assert T2.count("576_101..578_100") == 4, "576_101..578_100 count=%d (expect 4 = b_band_ab x3 [续带 + hop-chain verbatim + 投影兑现 quote] + b3_a x1 W255 A naive; dead-window authored 3 miscounting its own NEW block, healed this window)" % T2.count("576_101..578_100")
assert T2.count("576_301..576_500") == 4, "576_301..576_500 count=%d (expect 4 = b_band_ab x3 [B naive 续带 + naive-B-落 A 窗内 + 投影兑现 tail] + b3_b x1 W255 B naive; same dead-window miscount family, healed)" % T2.count("576_301..576_500")

# residue scan: all X_Y..X_Y windows well-formed
for m in re.finditer(r"(\d{3}_\d{3})\.\.(\d{3}_\d{3})", T2):
    lo = int(m.group(1).replace("_", "")); hi = int(m.group(2).replace("_", ""))
    assert lo <= hi, "malformed window %s" % m.group(0)

io.open(OUT, "w", encoding="utf-8", newline="").write(T2)
print("W255 PREREG DERIVE OK -> %s (%d bytes, %d lines)" % (OUT, len(T2.encode("utf-8")), T2.count("\n") + 1))
print("freeze window face: bm-c 循环班 r1056 freeze 窗 2026-10-17 %s" % FREEZE_T)
print("blocks replaced: %s" % ", ".join(n for n, _, _ in BLOCKS))
print("vmap legs: %d floors: %d post-legs: %d MUST: %d MUST_NOT: %d" % (len(VMAP), len(VMAP_FLOORS), len(VMAP_POST_LEGS), len(MUST), len(MUST_NOT)))
print("src blob-verified == aa1b1b0a52273e9330cd88a3298bc86e8ae6988d @ e2c4b543e (frozen pre-run face; HEAD post-backfill twin 2cd2a42d disclosed, NOT used)")
