# -*- coding: utf-8 -*-
# r1054 bm-c: W254 prereg derive (count-asserted ordered transform + marker-extracted block replaces).
# Source = committed frozen W253 prereg AT THE FREEZE COMMIT 741371846 (git 741371846:research/PERPETUAL_N1_W253_PREREG.md,
# 38,691 bytes -- the frozen pre-run face; sec7/8 placeholders intact). Extracted to
# results/_w254bmc_w253_frozen_face.txt this window and byte-verified IN-SCRIPT via git hash-object
# == blob ba1ccb2a6f4dc317fcd6cd855f74f465c50b7846 (freeze-commit face), AND cross-checked against
# git show 741371846:research/PERPETUAL_N1_W253_PREREG.md directly (same blob).
# TEMPLATE-FACE DISCLOSURE (needle-face divergence, honest): HEAD twin 9d6a934a = the CURRENT HEAD face
# = the POST-CYCLE face with sec.7/8 BACKFILLED by the r1053 continuation (W253 actual results).
# Deriving from the backfilled face would fabricate W254 sec.7/8 "跑后实证" from W253's measured numbers -- the
# r1049/r1052 precedent (derive always from the PRIOR wave's FREEZE-COMMIT face, "frozen pre-run face; sec7/8
# placeholders intact") and the prereg semantics (frozen PRE-RUN, placeholders for its own cycle) both require
# ba1ccb2a. Both faces measured this window (rev-parse 741371846:=ba1ccb2a / HEAD:=9d6a934a); divergence disclosed
# in header + closeout; 9d6a934a recorded as the post-backfill twin, NOT used as template.
# W254 facts (all machine-derived, never transcribed):
#   - seat probe ADMIT receipt results/_w254bmc_20261016_probe_receipt.json (r1053 window, seat pushed origin
#     fa70f3765, MSG-20261016-14xx-bmc-w254-seat, file landed in fleet/inbox/processed/). STAIRCASE
#     CONTINUES: A naive 573_901..575_900 REFUSED at start (registered W253 B band 573_901..574_100 sits INSIDE the
#     naive A window) -> A first-clean 574_101..576_100 hops=1 (THIRD consecutive A-hop, W253 prereg sec.5 item5
#     A-CLEAN-at-naive pre-W253-universe projection superseded live r587, divergence disclosed) / B naive
#     574_101..574_300 REFUSED at start (lands INSIDE the own-wave W254 A first-clean window) -> own-A reservation
#     cascade hop past 576_100 -> 576_101..576_300 hops=1 (FOURTH consecutive above-own-A landing);
#     seed_admit FREE x2 (A base=574101 span=2000 / B base=576101 span=200); leg0 rows=251 owner_rows=243
#     bmc_rows=73 bmc_ordinal=74 ordinal=244; leg2 conflicts=0; leg3 origin_vacancy=true;
#     leg4 W255+ projection: A naive 576_101..578_100 CLEAN pre-W254 BUT post-W254-REGISTERED the naive W255 A
#     start 576_101 is REFUSED by the registered W254 B band 576_101..576_300 (staircase-affects-A FOURTH consecutive
#     A-hop expected) / B naive 576_301..576_500 CLEAN but lands INSIDE the W255p A naive window.
#   - upstream W253 finalize landed (r1053 dead-window estate machine-verified, ledger 978,735+2,200=980,935 EXACT):
#     merged K=554,520 / merged mu -0.09273892862295319 / sigma 0.24504775480421728 / se_mu@K554,520 0.000329 /
#     W253-only mu -0.0925495 / A p95 0.3122 / K-lift 0.0 zero-move in-band / n_eff_held_equal 978,735 /
#     line_pre_w253 1.1944 / line_merged_554520 1.1944 / own-slice vs pre-wave merged gap 0.0002
#     (results/perpetual_faces/n1_w253_results.json + results/_r1053bmc_w253_fivekeys.json)
#   - W253 chain: prereg derive r1052 freeze LANDED 741371846 + five-face freeze splice r1053 dead-window estate
#     LANDED c9b4fd855 (zero post-splice heal; dual-sha16 pf 24fe08e65ef219c8 / n1 c8218b4deb2540b5)
#     + engine self-burn 12/12 (ledger appends b3caaedc1+bec86607a batched 6+6 self-committed) + r1053 continuation
#     sixgate PRE-FINALIZE 15th consecutive + finalize one-pass 980,935/K=554,520 + fivekeys 6/6 + sec.7/8 backfilled
#     + W254 seat published fa70f3765.
# Disclosed same-window needle heals: none new expected (all rolls count-asserted; POST legs repair wave-roll
# collateral only: se_mu chain tail append + K-lift value face + line_pre_w253 value face + sec7/8 paradigm rows
# + low-RAM list append + freeze-prep precedent window label).
# Needle-count pre-flight evidence: results/_w254bmc_needle_probe.py (all floors pre-verified this window).
import io, os, sys, datetime, subprocess, hashlib, re

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(REPO, "results", "_w254bmc_w253_frozen_face.txt")
OUT = os.path.join(REPO, "research", "PERPETUAL_N1_W254_PREREG.md")

# --- source byte-identity gates ---
_blob_expect = "ba1ccb2a6f4dc317fcd6cd855f74f465c50b7846"   # freeze-commit face @ 741371846
_ho = subprocess.run(["git", "hash-object", SRC], capture_output=True, text=True, cwd=REPO).stdout.strip()
assert _ho == _blob_expect, "SRC blob mismatch: got %s expect %s" % (_ho, _blob_expect)
_fc = subprocess.run(["git", "rev-parse", "741371846:research/PERPETUAL_N1_W253_PREREG.md"],
                     capture_output=True, text=True, cwd=REPO).stdout.strip()
assert _fc == _blob_expect, "freeze-commit blob mismatch: got %s expect %s" % (_fc, _blob_expect)
_hb = subprocess.run(["git", "rev-parse", "HEAD:research/PERPETUAL_N1_W253_PREREG.md"],
                     capture_output=True, text=True, cwd=REPO).stdout.strip()
assert _hb == "9d6a934a153208735d0b48164a6ca5167a8e30ea", "HEAD tpl twin face drifted: %s" % _hb

T0 = io.open(SRC, encoding="utf-8", newline="").read()
assert hashlib.sha256(T0.encode("utf-8")).hexdigest()[:16] == "aab6f0b6b4489166", "SRC sha mismatch"

P1, P2, P3 = "\x01W\x01", "\x01N\x01", "\x01B\x01"

now = datetime.datetime.now()
FREEZE_T = "%02d:%dx" % (now.hour, now.minute // 10)

# machine-extracted historical spans (from T0 PRE-roll bytes: zero transcription for carried content)
_i_b1 = T0.index("+W246=bm-a r1016 prereg derive")
_j_b1 = T0.index("——本波上游链=")
HIST_B1 = T0[_i_b1:_j_b1]  # W246..W252 chain legs verbatim (frozen template bytes)
_i_b6 = T0.index("·W250 冻结窗 RAM 未记录（r1046 死窗")
_b6_end = "W240 冻结窗 33.2G bm-a 实锚）"
_j_b6 = T0.index(_b6_end) + len(_b6_end)
HIST_B6 = T0[_i_b6:_j_b6]  # W250..W240 freeze-window RAM ledger verbatim

VMAP = [
    # projection first, then line_merged face, then prior-K bare, then ledger heads (order-critical)
    ("554,520 投影", "556,720 投影"),
    ("line_merged@K552,320 **1.1943**", "line_merged@K554,520 **1.1944**"),
    ("552,320", "554,520"),
    ("978,735", "980,935"),
    ("976,535", "978,735"),
    # sec5 measured keys -> W253 measured faces (n1_w253_results.json machine values)
    ("−0.09273968", "−0.09273893"),
    ("−0.09018", "−0.0925495"),
    ("0.2450479", "0.24504775"),
    ("实差 0.0026 在带内", "实差 0.0002 在带内"),
    ("（**0.3199** 实测锚）", "（**0.3122** 实测锚）"),
    # band values outside block regions (staircase-3rd-hop + own-A reservation cascade faces)
    ("A-ext seed=571_901..573_900", "A-ext seed=574_101..576_100"),
    ("entry rng seed=**571_901+j**", "entry rng seed=**574_101+j**"),
    ("entry rng=**571_901+j**", "entry rng=**574_101+j**"),
    ("exit rng=**573_901+j**", "exit rng=**576_101+j**"),
    ("A base=571901 span=2000 checked=2000 verdict=FREE", "A base=574101 span=2000 checked=2000 verdict=FREE"),
    ("B base=573901 span=200 checked=200 verdict=FREE", "B base=576101 span=200 checked=200 verdict=FREE"),
    ("R254：W253", "R255：W254"),
    # base-relation faces (block-external occurrences; block NEW uses the same new faces)
    ("571_900+1", "574_100+1"),
    ("573_900+1", "576_100+1"),
    # seat / provenance faces (W254 seat published r1053 window, origin fa70f3765)
    ("MSG-20261016-12xx-bmc-w253-seat", "MSG-20261016-14xx-bmc-w254-seat"),
    ("f6433ee61", "fa70f3765"),
    ("（bm-c r1050 席·queue-head FREEZE-UNBLOCKED 发布）", "（bm-c r1053 席·queue-head FREEZE-UNBLOCKED 发布）"),
    ("（bm-c r1050 席位", "（bm-c r1053 席位"),
    ("（r1050 席位窗实跑", "（r1053 席位窗实跑"),
    # finalize window faces (specific first, then catch-all)
    ("bm-c r1050 窗 11:5x", "bm-c r1053 窗 14:4x"),
    ("11:5x", "14:4x"),
    # engine live-read + RAM head (bm-c current window honest: ~2.7G free of 23.9G,
    # v5redo i2v lane burning GPU+RAM legal per MV P0 protected lane, CPU lane independent)
    ("saturation_engine.py status live-read r1052", "saturation_engine.py status live-read r1054"),
    ("本窗 free RAM ~1.8GB（", "本窗 free RAM ~2.7GB（"),
    # wave-number roll (chained placeholders)
    ("W253", P1), ("W252", "W253"), ("W251", "W252"), (P1, "W254"),
    # result-file names (chained)
    ("n1_w253", P2), ("n1_w252", "n1_w253"), (P2, "n1_w254"),
    # probe/freeze script basenames (chained; current face _w254bmc <- template _w253bmc)
    ("_w253bmc", P3), ("_w252bmc", "_w253bmc"), (P3, "_w254bmc"),
    # runner CLI wave
    ("--wave 253", "--wave 254"),
    ("波号 253", "波号 254"),
    # pool/engine ordinals
    ("第 251 枚", "第 252 枚"),
    ("第 243 波", "第 244 波"),
    ("bm-c 第七十三枚自有波", "bm-c 第七十四枚自有波"),
    # subsumption-order fix: compound needle contains 第 73 枚 -> MUST run before any bare roll
    ("bmc rows 72+候选=第 73 枚 EXACT", "bmc rows 73+候选=第 74 枚 EXACT"),
    ("第 73 枚", "第 74 枚"),
    ("probe leg0 bmc_rows=72 attempt-continuity face（r1050 窗算法·bm-c own seat+bmc live rows 72 实读）",
     "probe leg0 bmc_rows=73 attempt-continuity face（r1053 窗算法·bm-c own seat+bmc live rows 73 实读）"),
    ("engine_owner==bm-c 72 行注册", "engine_owner==bm-c 73 行注册"),
    ("engine_owner 行 242 注册在册", "engine_owner 行 243 注册在册"),
    # registry scan faces
    ("全二百五十行注册 N1 带表", "全二百五十一行注册 N1 带表"),
    ("freeze 窗 live derive 250 行单态 owner rows 242", "freeze 窗 live derive 251 行单态 owner rows 243"),
    ("probe leg0 机证 250 行〔", "probe leg0 机证 251 行〔"),
    ("席位窗 probe leg0 实测 250 行〔", "席位窗 probe leg0 实测 251 行〔"),
    ("perpetual_faces.py 零 251 行", "perpetual_faces.py 零 252 行"),
    ("共二百五十面实测", "共二百五十一面实测"),
    # sec8 placeholder projection-label bump (W254+ -> W255+ face)
    ("§5.5 W254+ 投影承接机证", "§5.5 W255+ 投影承接机证"),
]

VMAP_FLOORS = {
    "554,520 投影": 1, "line_merged@K552,320 **1.1943**": 1,
    "552,320": 7, "978,735": 3, "976,535": 2,
    "−0.09273968": 1, "−0.09018": 1, "0.2450479": 1, "实差 0.0026 在带内": 1,
    "（**0.3199** 实测锚）": 1,
    "A-ext seed=571_901..573_900": 1,
    "entry rng seed=**571_901+j**": 1, "entry rng=**571_901+j**": 1,
    "exit rng=**573_901+j**": 1,
    "A base=571901 span=2000 checked=2000 verdict=FREE": 1,
    "B base=573901 span=200 checked=200 verdict=FREE": 1,
    "R254：W253": 1,
    "W253": 28, "W252": 70, "W251": 9,
    "n1_w253": 4, "n1_w252": 3, "_w253bmc": 4, "_w252bmc": 1,
    "--wave 253": 2, "波号 253": 1,
    "第 251 枚": 1, "第 243 波": 1, "bm-c 第七十三枚自有波": 1,
    "bmc rows 72+候选=第 73 枚 EXACT": 2, "第 73 枚": 2,
    "probe leg0 bmc_rows=72 attempt-continuity face（r1050 窗算法·bm-c own seat+bmc live rows 72 实读）": 1,
    "engine_owner==bm-c 72 行注册": 1, "engine_owner 行 242 注册在册": 1,
    "全二百五十行注册 N1 带表": 1,
    "freeze 窗 live derive 250 行单态 owner rows 242": 1,
    "probe leg0 机证 250 行〔": 1, "席位窗 probe leg0 实测 250 行〔": 1,
    "perpetual_faces.py 零 251 行": 1,
    "共二百五十面实测": 1,
    "MSG-20261016-12xx-bmc-w253-seat": 4, "f6433ee61": 3,
    "（bm-c r1050 席·queue-head FREEZE-UNBLOCKED 发布）": 1,
    "（bm-c r1050 席位": 1, "（r1050 席位窗实跑": 1,
    "bm-c r1050 窗 11:5x": 1, "11:5x": 4, "已落账键·11:5x": 1,
    "saturation_engine.py status live-read r1052": 1,
    "本窗 free RAM ~1.8GB（": 1,
    "§5.5 W254+ 投影承接机证": 1,
    "571_900+1": 4, "573_900+1": 2,
    # block-marker stability floors (raw template face; T1 marker = post-roll form asserted in BLOCKS)
    "（**A 面=STAIRCASE-AFFECTS-A": 1,
    "已如实披露非分叉）": 1,
    "法典 §4 W253 行 A=571_901..573_900": 1,
    "法典 §4 W253 行 B=573_901..574_100": 1,
    "披露收敛·ADMIT 回执在场）": 1,
    "非转录 r587·ADMIT 回执在场）": 1,
    "5. **W254+ 投影（probe 机证 leg4": 1,
    "verify at W254 prereg，hop 链逐跳在 probe 回执。": 1,
    "·probe W254+ 投影 A naive 573_901..575_900 CLEAN hops=0": 1,
    "never transcribe r587**）": 1,
    "·W251 冻结窗 6.7G bm-c 实锚": 0,
    "·W252 冻结窗 7.0G bm-c 实锚": 1,
    "·W250 冻结窗 RAM 未记录（r1046 死窗": 1,
    "W240 冻结窗 33.2G bm-a 实锚）": 1,
    "selftest W253 face（": 1, "零假设零风险。": 1,
    "+W246=bm-a r1016 prereg derive": 1,
    "——本波上游链=": 1,
    "W254 freezer 承接面）】。": 1,
    "W243/W246/W248/W249/W250/W251/W252 低 RAM 实烧先例": 1,
    "r1049/W252 先例 freeze-prep 同式": 1,
    "→W249 **0.000332**→W250 **0.000331**→W251 **0.000330**→W252 **0.000330**】": 1,
    "line_pre_w252 1.194": 1,
    "bm-c r1050 W252 §7 范式": 1, "bm-c r1050 W252 §8 范式": 1,
    "键 W252 实测 K-lift **0.0001**": 1,
    "n_eff_held_equal 976,535": 1,
    "queue-head FREEZE-UNBLOCKED lane": 1,
    "本候选=bm-c 自有席自有波": 1,
    "表尾 W252 行": 2,
    "pre-W253 全二百五十行注册 N1 带表": 1,
    "bm-c 循环班 r1052 freeze 窗": 1,
    # zero-floors (absence assertions on T0)
    "waits-upstream ARMED": 0,
    "（**B 面=CLEAN": 0,
    "980,935": 0, "0.3122": 0, "576_101": 0, "576_300": 0,
    "554,520": 1,  # only the 投影 compound; bare face absent (baseline rolls supply it)
    "R255：W254": 0, "576_301": 0, "576_101..578_100": 0,
    "第四次连续": 0, "n1_w254": 0, "--wave 254": 0, "第 252 枚": 0, "第 244 波": 0,
    "571_901..572_100": 4,  # W253 B naive -- ALL inside b_band_ab/b3_b block regions (block-replaced to 0; T2 count gate)
}

# floors for POST-chain correction legs (needles exist only in T1 after the pre-chain legs run)
VMAP_POST_LEGS = [
    # se_mu narrowing chain: wave roll consumed the W251 label; restore it and append true W253 se 0.000329
    ("→W249 **0.000332**→W250 **0.000331**→W252 **0.000330**→W253 **0.000330**】",
     "→W249 **0.000332**→W250 **0.000331**→W251 **0.000330**→W252 **0.000330**→W253 **0.000329**】", 1),
    # line_pre face: lowercase w-token escapes the uppercase W-roll (r1045 derive precedent);
    # W253 actual line_pre_w253 = 1.1944 (n1_w253_results.json skill_line machine value)
    ("line_pre_w252 1.1942", "line_pre_w253 1.1944", 1),
    # K-lift value face: wave roll W252->W253 relabeled the anchor; W253 true K-lift = 0.0000 zero-move in-band
    ("键 W253 实测 K-lift **0.0001**", "键 W253 实测 K-lift **0.0000**", 1),
    # sec7/8 backfill paradigm rows (W253 sec.7/8 backfilled by the r1053 continuation window)
    ("bm-c r1050 W253 §7 范式", "bm-c r1053 W253 §7 范式", 1),
    ("bm-c r1050 W253 §8 范式", "bm-c r1053 W253 §8 范式", 1),
    # low-RAM precedent list: rolled T1 form lost the W251 label; restore it and append W253
    # (engine self-burn 12/12 r1053 window on this low-RAM machine; chain precedent every-wave append)
    ("W243/W246/W248/W249/W250/W252/W253 低 RAM 实烧先例", "W243/W246/W248/W249/W250/W251/W252/W253 低 RAM 实烧先例", 1),
    # freeze-prep precedent face (W253 prereg derive window = r1052)
    ("r1049/W253 先例 freeze-prep 同式", "r1052/W253 先例 freeze-prep 同式", 1),
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

# freeze-window live face: regex-extract the r1052 stamp (zero transcription) -> r1054 + runtime FREEZE_T
_fw_pat = re.compile(r"bm-c 循环班 r1052 freeze 窗 2026-10-16 \d{2}:\dx")
_fw_hits = _fw_pat.findall(T1)
assert len(_fw_hits) == 1, "freeze-window stamp count=%d (expect 1): %r" % (len(_fw_hits), _fw_hits)
T1 = T1.replace(_fw_hits[0], "bm-c 循环班 r1054 freeze 窗 2026-10-16 " + FREEZE_T)

# post-chain correction legs: needles exist only in T1 (post chained rolls); floors checked on T1
for o, n, f in VMAP_POST_LEGS:
    if T1.count(o) < f:
        raise SystemExit("VMAP POST FLOOR FAIL: %r count=%d floor=%d" % (o, T1.count(o), f))
    T1 = T1.replace(o, n)

# ---------------- block replacements (needles marker-extracted from T1; NEW = final) ----------------
NEW = {}

WL = "（W138..W206+" + "+".join("W%d" % n for n in range(211, 254)) + "）"  # 69 estate + W211..W253 = 112 rows

NEW["b_band_ab"] = (
    "（**A 面=STAIRCASE-AFFECTS-A·1-HOP WALK 形态（W239 staircase era 后第三次连续 A-hop）**："
    "A 面算术续带 573_901..575_900（自注册 W253 A 尾 573_900 续）"
    "在席位窗宇宙（post-W253-REGISTERED 终态注册·freeze-UNBLOCKED）起点即 REFUSED"
    "（注册 W253 B 带 573_901..574_100 落 naive A 窗内=staircase re-emergence affects A 承袭·"
    "W253 prereg §5.5 item5 A-CLEAN-at-naive 投影=pre-W253 宇宙 face·被 live re-derive 超越 r587 superseded 如实披露）"
    "→walk 越注册 W253 B 尾 574_100→A first-clean **574_101..576_100**·**hops=1**·"
    "**A 落位 base==注册前波 B 尾+1（574_100+1）机检关系**"
    "（A_hop_chain 1 跳 verbatim leg1 机证〔window 573_901..575_900→jump 574_101·refuser band 573_901..574_100〕"
    "·A_clean_at_naive_start=false·A_staircase_hop_past_W253_B=true"
    "·A base>=registered prior-wave B tail+1 floor relation）"
    "·非转录 r587 前向单调断言在走册）；"
    "**B-ext exit seed=576_101..576_300**（**B 面=1-HOP own-A RESERVATION CASCADE·落位高于本波 A 窗形态（第四次连续 above-own-A 落位）**："
    "B naive 续带 574_101..574_300（自注册 W253 B 尾 574_100+1 续）"
    "在席位窗宇宙（post-W253-REGISTERED 终态注册·freeze-UNBLOCKED）起点即 REFUSED"
    "（naive B 窗 574_101..574_300 落本波 A first-clean 窗 574_101..576_100 内"
    "=own-A reservation cascade standard leg 强制·probe leg1 B_semantics 机证·B_naive_refused_at_start=true）"
    "——**own-A reservation standard leg 越本波 A 窗 574_101..576_100**（1 hop）"
    "→**1 hop** 落位 **576_101..576_300**·**B 落位 base==本波 A 窗尾+1（576_100+1）EXACT 机检关系**"
    "（B_hop lands-inside-A=false·B_lands_above_own_A=true·B_hop_chain 1 跳 verbatim 在 probe 回执 leg1 机证"
    "·非转录 r587·AB 同窗互斥面 leg2 律在场）；"
    "**W253 prereg §5.5 item5 投影承接面注记兑现+落位分歧如实披露**："
    "投影预言 W254 A naive 573_901..575_900 CLEAN（pre-W253 宇宙零 live refusers）——本窗 live re-derive A 面起点即被注册 W253 B 带拒"
    "（投影 A-CLEAN 未兑现=staircase affects A 承袭·第三次连续 A-hop）"
    "→A first-clean 上移 574_101..576_100→B naive 574_101..574_300 相应落本波 A 窗内→own-A reservation cascade 上移 576_101..576_300"
    "（post-W253 宇宙 live re-derive 必变·W253 prereg §5.5 已披露 live re-derive governs·禁转录投影 r587·"
    "落位高于投影=新拒面如实注记·已如实披露非分叉）"
)

NEW["b3_a_bandface"] = (
    "法典 §4 W254 行 A=574_101..576_100·**STAIRCASE-AFFECTS-A·1-HOP WALK 形态（W239 staircase era 后第三次连续 A-hop）**："
    "A 算术续带 573_901..575_900（自注册 W253 A 尾 573_900 续）"
    "在席位窗宇宙（post-W253-REGISTERED 终态注册·freeze-UNBLOCKED）起点即 REFUSED"
    "（注册 W253 B 带 573_901..574_100 落 naive A 窗内=W253 prereg §5.5 item5 A-CLEAN-at-naive 投影被 live re-derive 超越·r587 superseded 披露）"
    "→walk 越注册 W253 B 尾 574_100→A first-clean 574_101..576_100·**hops=1**·"
    "**A 落位 base==注册前波 B 尾+1（574_100+1）机检关系**"
    "（A_hop_chain 1 跳 verbatim probe leg1 机证·A_clean_at_naive_start=false·A_staircase_hop_past_W253_B=true）"
    "·非转录 r587·ADMIT 回执在场）"
)

NEW["b3_b_bandface"] = (
    "法典 §4 W254 行 B=576_101..576_300·**1-HOP own-A RESERVATION CASCADE·落位高于本波 A 窗形态**："
    "B naive 续带 574_101..574_300（自注册 W253 B 尾 574_100+1 续）"
    "在席位窗宇宙（post-W253-REGISTERED 终态注册）起点即 REFUSED"
    "（naive B 窗落本波 A first-clean 窗 574_101..576_100 内=own-A reservation cascade standard leg·probe leg1 B_semantics 机证）"
    "→own-A reservation 越本波 A 窗 574_101..576_100→1 hop 落位 576_101..576_300·"
    "**B 落位 base==本波 A 窗尾+1（576_100+1）机检关系**"
    "（B_hop lands-inside-A=false·B_lands_above_own_A=true·B_hop_chain 1 跳 verbatim 在 probe 回执"
    "·第四次连续 above-own-A 落位如实注记）"
    "·非转录 r587·与 W253 prereg §5.5 item5 投影承接面注记兑现+落位上移分歧披露收敛·ADMIT 回执在场）"
)

NEW["b1_chain_tail"] = (
    HIST_B1
    + "+W253=bm-c r1052 prereg derive（machine-SUB from frozen W252 tpl c2c7076a·freeze LANDED 741371846·banned_direction_gate rc0·同窗缺陷抓修 pre-freeze〔3 needle heals: se_mu bold-close x2 + line_pre lowercase-w unrolled + MUST n_eff self-correct 976,535〕）"
    + "+五面冻结 splice（r1053 死窗 14:3x LANDED c9b4fd855〔zero post-splice heal·4 pre-splice authoring defect classes caught by count-asserted gates〕·dual-sha16 pf 24fe08e65ef219c8 / n1 c8218b4deb2540b5·W253 块 parity 111 rows）"
    + "+引擎自燃 12/12（mtime-watch auto-ignite engine lane·ledger appends b3caaedc1+bec86607a batched 6+6 self-committed）"
    + "+bm-c r1053 finalize one-pass 已落（K=554,520·账本头 980,935 机读·n1_w253_results.json·14:5x·fivekeys ALL PASS·sixgate PRE-FINALIZE 15th consecutive 正相〔triple identity n1 c8218b4deb2540b5 / pf 24fe08e65ef219c8 零漂移·zero re-anchor face〕·K-lift 0.0000 zero-move in-band）"
    "——本波上游链=W1..W253 finalize 全落地·零在飞上游席·干净前置**；"
    "席位公示=MSG-20261016-14xx-bmc-w254-seat 已推 origin fa70f3765 先于本冻结"
    "【r565 律·席位先行·bm-c r1053 窗发布·queue-head FREEZE-UNBLOCKED 承接·W253 own-wave finalize 已落=席位时即解锁】；"
    "下游 W255+ 投影见 §5.5（probe 机证 leg4·W255 freezer 承接面）】。"
)

NEW["b5_projection"] = (
    "5. **W255+ 投影（probe 机证 leg4·下波冻结方复核非转抄 r587 律）**：A naive first-clean 576_101..578_100 **CLEAN**（hops=0·pre-W254 宇宙零 live refusers）——"
    "**post-W254-REGISTERED 预披露：naive W255 A 起点 576_101 将被注册 W254 B 带 576_101..576_300 拒（staircase-affects-A 第四次连续 A-hop 预期）**；"
    "B naive **576_301..576_500 CLEAN（hops=0）但落投影 A 窗 576_101..578_100 内**（W255p_B_lands_inside_W255p_A_naive=true——"
    "**staircase face 延续**：W254 A 574_101..576_100+B 576_101..576_300 注册后 naive W255 A 窗起点即被注册 W254 B 带拒（staircase affects A 承袭·第四次连续 A-hop 预期）"
    "→A first-clean 将上移·B own-A reservation cascade 落位相应上移——post-W254 宇宙 live re-derive 必变·禁转录投影）；"
    "**W255 冻结方禁假设 staircase A-base==prior-B-tail+1 或 B-base==own-A-tail+1 恒等·须重读 live trace**"
    "（W251 起 staircase affects A·W252/W253/W254=A/B 双 1-hop 形态连续三波如实注记·seed-gap face 已于 W252 终结=A 首跳如实注记）"
    "——W255 冻结方必须在 post-W254 注册宇宙重 derive 且 derive B 时预留本波 A 窗 574_101..576_100+本波 B 带 576_101..576_300"
    "——leg2 律/E36 卡·W141 先例；verify at W255 prereg，hop 链逐跳在 probe 回执。"
)

NEW["b6_ram"] = "·W254 冻结窗 2.7G bm-c 实锚" + HIST_B6

NEW["b7_claim_projection"] = (
    "·probe W255+ 投影 A naive 576_101..578_100 CLEAN hops=0（零 live refusers）/ B naive 576_301..576_500 CLEAN hops=0 **但落 naive W255 A 窗内**"
    "→own-A reservation cascade 下 staircase 级联上移 **staircase face 延续 live re-derive governs 预披露**"
    "（投影 A naive 576_101..578_100 CLEAN·hops=0——**post-W254-REGISTERED 预披露：naive W255 A 起点 576_101 将被注册 W254 B 带 576_101..576_300 拒=staircase affects A 第四次连续 A-hop 预期**；"
    "投影 B naive 576_301..576_500 clean 但落 naive W255 A 窗 576_101..578_100 内——"
    "**above-own-A 承袭 face：W254 B 576_101..576_300 落本波 A 窗之上〔第四次连续〕·W254 A 面 1-hop=staircase affects A〔第三次连续〕·"
    "W255 冻结方禁假设 staircase A-base==prior-B-tail+1 或 B-base==own-A-tail+1 恒等·须重读 live trace·注册 W254 B 带将拒 naive W255 A 窗仅当重叠"
    "——**W255 freezer 承接面强制注记：须在 post-W254 宇宙重 derive 且 derive B 时预留本波 A 窗·W141 先例·never transcribe r587**）"
)

NEW["b8_selftest"] = (
    "selftest W254 face（A=staircase-hop honest-walk past the registered prior-wave B band 断言"
    "（A_hop_chain 与 probe 回执逐跳恒等·A 第三次连续跳=W239 staircase era 后承袭如实注记·A 落位不落任何已注册带内）"
    "·B=own-A reservation 1-hop lands-above-own-A 断言（B_hop_chain 与 probe 回执逐跳恒等·B 落位不落本波 A 窗内=同窗互斥断言·第四次连续 above-own-A 如实注记）·W253 行 parity 腿"
    "**estate 提取面注记**：冻结拼接脚本的 parity estate（W138..W206 69 行 full-span·r858 absorb 代）从**本机 W253 块物理字节**提取"
    "（结构已知·提取自证断言 69 行 range 恒等在场）——W253 块的自有 W239..W252 legs（14 行）不入 estate 路径"
    "·提取后新增 W239..W253 leg（15 行）构成 W254 块 parity 112 行" + WL + "·零假设零风险。"
)

# marker pairs: (block, start_marker, end_marker) -- needles matched on T1 (post-roll faces)
BLOCKS = [
    ("b_band_ab", "（**A 面=STAIRCASE-AFFECTS-A", "已如实披露非分叉）"),
    ("b3_a_bandface", "法典 §4 W254 行 A=571_901..573_900", "非转录 r587·ADMIT 回执在场）"),
    ("b3_b_bandface", "法典 §4 W254 行 B=573_901..574_100", "披露收敛·ADMIT 回执在场）"),
    ("b5_projection", "5. **W254+ 投影（probe 机证 leg4", "verify at W254 prereg，hop 链逐跳在 probe 回执。"),
    ("b7_claim_projection", "·probe W254+ 投影 A naive 573_901..575_900 CLEAN hops=0", "never transcribe r587**）"),
    ("b6_ram", "·W253 冻结窗 7.0G bm-c 实锚", "W240 冻结窗 33.2G bm-a 实锚）"),
    ("b8_selftest", "selftest W254 face（", "零假设零风险。"),
    ("b1_chain_tail", "+W246=bm-a r1016 prereg derive", "W254 freezer 承接面）】。"),
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
    "PERPETUAL-N1-W254", "research/PERPETUAL_N1_W254_PREREG.md",
    "574_101..576_100", "576_101..576_300", "980,935", "554,520", "556,720",
    "n1_w254_results.json", "MSG-20261016-14xx-bmc-w254-seat", "fa70f3765",
    "第 252 枚", "第七十四枚", "第 244 波", "第 74 枚",
    "STAIRCASE-AFFECTS-A", "第三次连续 A-hop", "第四次连续 above-own-A",
    "_w254bmc_20261016", "--wave 254", "波号 254",
    "W253=bm-c r1052 prereg derive", "r1053 finalize one-pass",
    "n_eff_held_equal 978,735", "−0.09273893", "0.24504775", "−0.0925495",
    "（**0.3122** 实测锚）", "bm-c 循环班 r1054 freeze 窗", "本窗 free RAM ~2.7GB",
    "→W249 **0.000332**→W250 **0.000331**→W251 **0.000330**→W252 **0.000330**→W253 **0.000329**】",
    "queue-head FREEZE-UNBLOCKED lane", "seed_admit_gate rc0 双带 FREE",
    "A base=574101", "B base=576101",
    "bm-c r1053 W253 §7 范式", "bm-c r1053 W253 §8 范式",
    "W255 freezer 承接面", "verify at W255 prereg",
    "selftest W254 face", "W239..W253 leg（15 行）构成 W254 块 parity 112 行",
    "键 W253 实测 K-lift **0.0000**", "line_merged@K554,520 **1.1944**", "line_pre_w253 1.1944",
    "实差 0.0002 在带内", "已落账键·14:4x", "bm-c r1053 窗 14:4x",
    "r1052/W253 先例 freeze-prep 同式", "251 行单态", "probe leg0 机证 251 行",
    "_w254bmc_freeze_edits", "_w253bmc_freeze_edits", "本波上游链=W1..W253 finalize 全落地",
    "engine_owner==bm-c 73 行注册", "bmc rows 73", "bmc_rows=73",
    "queue-head FREEZE-UNBLOCKED 承接", "A 落位 base==注册前波 B 尾+1（574_100+1）",
    "B 落位 base==本波 A 窗尾+1（576_100+1）",
    "W253 块的自有 W239..W252 legs（14 行）",
    "bm-c r1053 席位", "bm-c r1053 席·queue-head FREEZE-UNBLOCKED 发布",
    "post-W253-REGISTERED 终态注册", "席位窗 probe leg0 实测 251 行",
    "W243/W246/W248/W249/W250/W251/W252/W253 低 RAM 实烧先例", "·W254 冻结窗 2.7G bm-c 实锚",
    "本候选=bm-c 自有席自有波", "R255：W254 带从未指派",
    "B_hop lands-inside-A=false", "B_lands_above_own_A=true", "A_staircase_hop_past_W253_B=true",
    "§5.5 W255+ 投影承接机证", "exit rng=**576_101+j**", "B-ext exit seed=576_101..576_300",
    "A-ext seed=574_101..576_100",
    "probe leg0 bmc_rows=73 attempt-continuity face（r1053 窗算法·bm-c own seat+bmc live rows 73 实读）",
    "573_901..575_900", "574_101..574_300", "576_101..578_100", "576_301..576_500",
    "A_clean_at_naive_start=false",
    "表尾 W253 行", "pre-W254 全二百五十一行注册 N1 带表", "共二百五十一面实测",
    "engine_owner 行 243 注册在册", "freeze 窗 live derive 251 行单态 owner rows 243",
    "zero post-splice heal", "c9b4fd855", "741371846", "b3caaedc1", "bec86607a",
    "（r1053 席位窗实跑", "（bm-c r1053 席位",
    "W253 own-wave finalize 已落=席位时即解锁",
    "n1_w253_results.json",
]
for s in MUST:
    assert s in T2, "MUST-HAVE missing: %r" % s

MUST_NOT = [
    "**A-ext seed=571_901", "567_501", "567_500", "545_301", "545_300", "545_500", "565_501",
    "FIRST-CLEAN·hops=0", "13-HOP", "13 hops", "A_hop_chain=[] 空集", "A_clean_at_naive_start=true",
    "连续第十四个",
    "−0.09273968", "0.2450479", "−0.09018", "**0.3199**", "实差 0.0026 在带内",
    "line_merged@K552,320", "547,920 合并池", "累计 null 池=547,920",
    "f6433ee61", "MSG-20261016-12xx", "bmc-w253-seat", "第 73 枚", "第七十三枚", "第 251 枚", "第 243 波",
    "engine_owner 行 242", "owner rows 242", "bmc rows 72", "bmc_rows=72", "engine_owner==bm-c 72",
    "250 行", "二百五十行注册", "二百五十面实测", "249 行", "二百四十九",
    "r1050 窗算法", "（bm-c r1050 席", "（r1050 席位窗实跑",
    "bm-c r1050 窗 11:5x", "bm-c 循环班 r1052", "live-read r1052", "已落账键·11:5x",
    "波号 253", "--wave 253", "R254：W253",
    "verify at W254 prereg", "W254 freezer 承接面", "W254p_", "W254 冻结方",
    "键 W250 实测 K-lift", "键 W251 实测 K-lift **0.0001**", "line_pre_w249", "line_pre_w251 1.194",
    "键 W252 实测 K-lift",
    "（**B 面=CLEAN", "waits-upstream ARMED",
    "（bm-c r1043 席", "第 70 枚", "engine_owner 行 239",
    "·W250 冻结窗 RAM 未记录（r1042",
    "W239..W251 leg（13 行）构成 W252 块 parity 110 行",
    "selftest W253 face", "本窗 free RAM ~1.8GB",
    "首次 A-hop", "第二次连续 above-own-A", "第三次连续 above-own-A",
    "571_901..573_900", "571_901..572_100", "571_701..573_700",
]
for s in MUST_NOT:
    assert s not in T2, "MUST-NOT-HAVE present: %r (count=%d)" % (s, T2.count(s))

# projection-fulfillment count gates
assert T2.count("W254+ 投影") == 0, "W254+ 投影 count=%d (expect 0)" % T2.count("W254+ 投影")
assert T2.count("W255+ 投影") == 4, "W255+ 投影 count=%d (expect 4 = b1 tail + b5 title + b7 claim + sec8 rolled)" % T2.count("W255+ 投影")
assert T2.count("hops=1") == 2, "hops=1 count=%d (expect 2 = 带位 A + §3 A)" % T2.count("hops=1")
assert T2.count("第二次连续 A-hop") == 0, "第二次连续 A-hop count=%d (expect 0)" % T2.count("第二次连续 A-hop")
assert T2.count("第四次连续 A-hop") == 3, "第四次连续 A-hop count=%d (expect 3 = b5 pre-registered face x2 + b7 projection face)" % T2.count("第四次连续 A-hop")
assert T2.count("571_901..572_100") == 0, "571_901..572_100 count=%d (expect 0 = block-replaced)" % T2.count("571_901..572_100")

# residue scan: all X_Y..X_Y windows well-formed
for m in re.finditer(r"(\d{3}_\d{3})\.\.(\d{3}_\d{3})", T2):
    lo = int(m.group(1).replace("_", "")); hi = int(m.group(2).replace("_", ""))
    assert lo <= hi, "malformed window %s" % m.group(0)

io.open(OUT, "w", encoding="utf-8", newline="").write(T2)
print("W254 PREREG DERIVE OK -> %s (%d bytes, %d lines)" % (OUT, len(T2.encode("utf-8")), T2.count("\n") + 1))
print("freeze window face: bm-c 循环班 r1054 freeze 窗 2026-10-16 %s" % FREEZE_T)
print("blocks replaced: %s" % ", ".join(n for n, _, _ in BLOCKS))
print("vmap legs: %d floors: %d post-legs: %d MUST: %d MUST_NOT: %d" % (len(VMAP), len(VMAP_FLOORS), len(VMAP_POST_LEGS), len(MUST), len(MUST_NOT)))
print("src blob-verified == ba1ccb2a6f4dc317fcd6cd855f74f465c50b7846 @ 741371846 (frozen pre-run face; HEAD post-backfill twin 9d6a934a disclosed, NOT used)")
