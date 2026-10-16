# -*- coding: utf-8 -*-
# r1052 bm-c: W253 prereg derive (count-asserted ordered transform + marker-extracted block replaces).
# Source = committed frozen W252 prereg AT THE FREEZE COMMIT 472cc8386 (git 472cc8386:research/PERPETUAL_N1_W252_PREREG.md,
# 37,564 bytes -- the frozen pre-run face; sec7/8 placeholders intact). Extracted to
# results/_w253bmc_w252_frozen_face.txt (dead-window prep 13:00:25) and byte-verified IN-SCRIPT via git hash-object
# == blob c2c7076ac969a78551539ce216d0eaca71e63e58 (freeze-commit face), AND cross-checked against
# git show 472cc8386:research/PERPETUAL_N1_W252_PREREG.md directly (same blob).
# TEMPLATE-FACE DISCLOSURE (needle-face divergence, honest): next_pointer/r1051-facts named tpl blob b79b055f
# = the CURRENT HEAD face (41,648 bytes) = the POST-CYCLE face with sec.7/8 BACKFILLED by r1050 (W252 actual results).
# Deriving from the backfilled face would fabricate W253 sec.7/8 "跑后实证" from W252's measured numbers -- the
# r1049 precedent (derive always from the PRIOR wave's FREEZE-COMMIT face, "frozen pre-run face; sec7/8 placeholders
# intact") and the prereg semantics (frozen PRE-RUN, placeholders for its own cycle) both require c2c7076a.
# Both faces measured this window (rev-parse 472cc8386:=c2c7076a / HEAD:=b79b055f); divergence disclosed in header
# + closeout; b79b055f recorded as the post-backfill twin, NOT used as template.
# W253 facts (all machine-derived, never transcribed):
#   - seat probe ADMIT receipt results/_w253bmc_20261016_probe_receipt.json (r1050 window, seat pushed origin
#     f6433ee61, MSG-20261016-12xx-bmc-w253-seat, file landed in fleet/inbox/processed/ 12:04:21). STAIRCASE
#     CONTINUES: A naive 571_701..573_700 REFUSED at start (registered W252 B band 571_701..571_900 sits INSIDE the
#     naive A window) -> A first-clean 571_901..573_900 hops=1 (SECOND consecutive A-hop, W252 prereg sec.5 item5
#     A-CLEAN-at-naive pre-W252-universe projection superseded live r587, divergence disclosed) / B naive
#     571_901..572_100 REFUSED at start (lands INSIDE the own-wave W253 A first-clean window) -> own-A reservation
#     cascade hop past 573_900 -> 573_901..574_100 hops=1 (THIRD consecutive above-own-A landing);
#     seed_admit FREE x2 (A base=571901 span=2000 / B base=573901 span=200);
#     leg0 rows=250 owner_rows=242 bmc_rows=72 bmc_ordinal=73 ordinal=243;
#     leg4 W254+ projection: A naive 573_901..575_900 clean hops=0 / B naive 574_101..574_300 clean hops=0 but lands
#     INSIDE W254p_A naive (staircase face continues; live re-derive governs).
#   - upstream W252 finalize landed (bm-c r1050 absorb-continuation, ledger 976,535+2,200=978,735 EXACT):
#     merged K=552,320 / merged mu -0.09273968315469293 / sigma 0.24504788580090198 / se_mu@K552,320 0.000330 /
#     W252-only mu -0.09017509090909091 / A p95 0.3199 / K-lift +0.0001 (second consecutive nonzero in-band) /
#     n_eff_held_equal 976,535 / line_pre_w252 1.1942 / line_merged_552320 1.1943 / W252-only vs merged gap 0.002565
#     (prereg face basis: own-slice vs pre-wave merged = 0.0026)
#     (results/perpetual_faces/n1_w252_results.json + results/_r1050bmc_w252_fivekeys.json)
#   - W252 chain: prereg derive r1049 freeze LANDED 472cc8386 + five-face freeze splice r1050 dead-window estate
#     11:33-11:34 LANDED e63561df3 (zero post-splice heal; post-splice sha16 pf b3eed1c579e7f22f / n1 7252c90bad52de99)
#     + engine self-burn 12/12 (ledger appends cbf6411bf+b3d563f4f batched 6+6 self-committed) + r1050 continuation
#     finalize one-pass (sixgate PRE-FINALIZE ALL PASS first-run 14th consecutive correct-phase) + sec.7/8 backfilled
# Disclosed same-window needle heals: none new expected (all rolls count-asserted; POST legs repair wave-roll
# collateral only: se_mu chain tail append + line_pre_w252 value face + sec7/8 paradigm row + low-RAM list append +
# freeze-prep precedent window label + sec8 projection label bump).
import io, os, sys, datetime, subprocess, hashlib, re

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(REPO, "results", "_w253bmc_w252_frozen_face.txt")
OUT = os.path.join(REPO, "research", "PERPETUAL_N1_W253_PREREG.md")

# --- source byte-identity gates ---
_blob_expect = "c2c7076ac969a78551539ce216d0eaca71e63e58"   # freeze-commit face @ 472cc8386
_ho = subprocess.run(["git", "hash-object", SRC], capture_output=True, text=True, cwd=REPO).stdout.strip()
assert _ho == _blob_expect, "SRC blob mismatch: got %s expect %s" % (_ho, _blob_expect)
_fc = subprocess.run(["git", "rev-parse", "472cc8386:research/PERPETUAL_N1_W252_PREREG.md"],
                     capture_output=True, text=True, cwd=REPO).stdout.strip()
assert _fc == _blob_expect, "freeze-commit blob mismatch: got %s expect %s" % (_fc, _blob_expect)
_hb = subprocess.run(["git", "rev-parse", "HEAD:research/PERPETUAL_N1_W252_PREREG.md"],
                     capture_output=True, text=True, cwd=REPO).stdout.strip()
assert _hb == "b79b055fd92e92540f6c62dc8fae7cc87c93b6bf", "HEAD tpl twin face drifted: %s" % _hb

T0 = io.open(SRC, encoding="utf-8", newline="").read()
assert hashlib.sha256(T0.encode("utf-8")).hexdigest()[:16] == "9439feeaa3b914e3", "SRC sha mismatch"

P1, P2, P3 = "\x01W\x01", "\x01N\x01", "\x01B\x01"

now = datetime.datetime.now()
FREEZE_T = "%02d:%dx" % (now.hour, now.minute // 10)

# machine-extracted historical spans (from T0 PRE-roll bytes: zero transcription for carried content)
_i_b1 = T0.index("+W246=bm-a r1016 prereg derive")
_j_b1 = T0.index("——本波上游链=")
HIST_B1 = T0[_i_b1:_j_b1]  # W246..W251 chain legs verbatim (frozen template bytes)
_i_b6 = T0.index("·W250 冻结窗 RAM 未记录（r1046 死窗")
_b6_end = "W240 冻结窗 33.2G bm-a 实锚）"
_j_b6 = T0.index(_b6_end) + len(_b6_end)
HIST_B6 = T0[_i_b6:_j_b6]  # W250..W240 freeze-window RAM ledger verbatim

VMAP = [
    # projection first, then line_merged face, then prior-K bare, then ledger heads (order-critical)
    ("552,320 投影", "554,520 投影"),
    ("line_merged@K550,120 **1.1941**", "line_merged@K552,320 **1.1943**"),
    ("550,120", "552,320"),
    ("976,535", "978,735"),
    ("974,335", "976,535"),
    # sec5 measured keys -> W252 measured faces (n1_w252_results.json machine values)
    ("−0.09274994", "−0.09273968"),
    ("−0.08776", "−0.09018"),
    ("0.2450362", "0.2450479"),
    ("实差 0.0050 在带内", "实差 0.0026 在带内"),
    ("（**0.3153** 实测锚）", "（**0.3199** 实测锚）"),
    # band values outside block regions (staircase-2nd-hop + own-A reservation cascade faces)
    ("A-ext seed=569_701..571_700", "A-ext seed=571_901..573_900"),
    ("entry rng seed=**569_701+j**", "entry rng seed=**571_901+j**"),
    ("entry rng=**569_701+j**", "entry rng=**571_901+j**"),
    ("exit rng=**571_701+j**", "exit rng=**573_901+j**"),
    ("A base=569701 span=2000 checked=2000 verdict=FREE", "A base=571901 span=2000 checked=2000 verdict=FREE"),
    ("B base=571701 span=200 checked=200 verdict=FREE", "B base=573901 span=200 checked=200 verdict=FREE"),
    ("R253：W252", "R254：W253"),
    # seat / provenance faces (W253 seat published r1050 closeout, origin f6433ee61)
    ("MSG-20261016-10xx-bmc-w252-seat", "MSG-20261016-12xx-bmc-w253-seat"),
    ("f9441de67", "f6433ee61"),
    ("（bm-c r1048 席·queue-head FREEZE-UNBLOCKED 发布）", "（bm-c r1050 席·queue-head FREEZE-UNBLOCKED 发布）"),
    ("（bm-c r1048 席位", "（bm-c r1050 席位"),
    ("（r1048 席位窗实跑", "（r1050 席位窗实跑"),
    # finalize window faces (specific first, then catch-all)
    ("bm-c r1048 窗 10:0x", "bm-c r1050 窗 11:5x"),
    ("10:0x", "11:5x"),
    # engine live-read + RAM head (bm-c current window honest: ~1.8G free of 23.9G,
    # jayredo i2v lane burning GPU+RAM legal per MV protected lane, CPU lane independent)
    ("saturation_engine.py status live-read r1049", "saturation_engine.py status live-read r1052"),
    ("本窗 free RAM ~7.0GB（", "本窗 free RAM ~1.8GB（"),
    # wave-number roll (chained placeholders)
    ("W252", P1), ("W251", "W252"), ("W250", "W251"), (P1, "W253"),
    # result-file names (chained)
    ("n1_w252", P2), ("n1_w251", "n1_w252"), (P2, "n1_w253"),
    # probe/freeze script basenames (chained; current face _w253bmc <- template _w252bmc)
    ("_w252bmc", P3), ("_w251bmc", "_w252bmc"), (P3, "_w253bmc"),
    # runner CLI wave
    ("--wave 252", "--wave 253"),
    ("波号 252", "波号 253"),
    # pool/engine ordinals
    ("第 250 枚", "第 251 枚"),
    ("第 242 波", "第 243 波"),
    ("bm-c 第七十二枚自有波", "bm-c 第七十三枚自有波"),
    # subsumption-order fix: compound needle contains 第 72 枚 -> MUST run before any bare roll
    ("bmc rows 71+候选=第 72 枚 EXACT", "bmc rows 72+候选=第 73 枚 EXACT"),
    ("probe leg0 bmc_rows=71 attempt-continuity face（r1048 窗算法·bm-c own seat+bmc live rows 71 实读）",
     "probe leg0 bmc_rows=72 attempt-continuity face（r1050 窗算法·bm-c own seat+bmc live rows 72 实读）"),
    ("engine_owner==bm-c 71 行注册", "engine_owner==bm-c 72 行注册"),
    ("engine_owner 行 241 注册在册", "engine_owner 行 242 注册在册"),
    # registry scan faces
    ("全二百四十九行注册 N1 带表", "全二百五十行注册 N1 带表"),
    ("freeze 窗 live derive 249 行单态 owner rows 241", "freeze 窗 live derive 250 行单态 owner rows 242"),
    ("probe leg0 机证 249 行〔", "probe leg0 机证 250 行〔"),
    ("席位窗 probe leg0 实测 249 行〔", "席位窗 probe leg0 实测 250 行〔"),
    ("perpetual_faces.py 零 250 行", "perpetual_faces.py 零 251 行"),
    ("共二百四十九面实测", "共二百五十面实测"),
    # sec8 placeholder projection-label bump (W253+ -> W254+ face)
    ("§5.5 W253+ 投影承接机证", "§5.5 W254+ 投影承接机证"),
]

VMAP_FLOORS = {
    "552,320 投影": 1, "line_merged@K550,120 **1.1941**": 1,
    "550,120": 7, "976,535": 3, "974,335": 2,
    "−0.09274994": 1, "−0.08776": 1, "0.2450362": 1, "实差 0.0050 在带内": 1,
    "（**0.3153** 实测锚）": 1,
    "A-ext seed=569_701..571_700": 1,
    "entry rng seed=**569_701+j**": 1, "entry rng=**569_701+j**": 1,
    "exit rng=**571_701+j**": 1,
    "A base=569701 span=2000 checked=2000 verdict=FREE": 1,
    "B base=571701 span=200 checked=200 verdict=FREE": 1,
    "R253：W252": 1,
    "W252": 30, "W251": 68, "W250": 8,
    "n1_w252": 4, "n1_w251": 3, "_w252bmc": 4, "_w251bmc": 1,
    "--wave 252": 2, "波号 252": 1,
    "第 250 枚": 1, "第 242 波": 1, "bm-c 第七十二枚自有波": 1,
    "bmc rows 71+候选=第 72 枚 EXACT": 2, "第 72 枚": 2,
    "probe leg0 bmc_rows=71 attempt-continuity face（r1048 窗算法·bm-c own seat+bmc live rows 71 实读）": 1,
    "engine_owner==bm-c 71 行注册": 1, "engine_owner 行 241 注册在册": 1,
    "全二百四十九行注册 N1 带表": 1,
    "freeze 窗 live derive 249 行单态 owner rows 241": 1,
    "probe leg0 机证 249 行〔": 1, "席位窗 probe leg0 实测 249 行〔": 1,
    "perpetual_faces.py 零 250 行": 1,
    "共二百四十九面实测": 1,
    "MSG-20261016-10xx-bmc-w252-seat": 4, "f9441de67": 3,
    "（bm-c r1048 席·queue-head FREEZE-UNBLOCKED 发布）": 1,
    "（bm-c r1048 席位": 1, "（r1048 席位窗实跑": 1,
    "bm-c r1048 窗 10:0x": 1, "10:0x": 3, "已落账键·10:0x": 1,
    "saturation_engine.py status live-read r1049": 1,
    "本窗 free RAM ~7.0GB（": 1,
    "§5.5 W253+ 投影承接机证": 1,
    # block-marker stability floors (raw template face; T1 marker = post-roll form asserted below)
    "（**A 面=STAIRCASE-AFFECTS-A": 1,
    "已如实披露非分叉）": 1,
    "法典 §4 W252 行 A=569_701..571_700": 1,
    "法典 §4 W252 行 B=571_701..571_900": 1,
    "披露收敛·ADMIT 回执在场）": 1,
    "非转录 r587·ADMIT 回执在场）": 1,
    "5. **W253+ 投影（probe 机证 leg4": 1,
    "verify at W253 prereg，hop 链逐跳在 probe 回执。": 1,
    "·probe W253+ 投影 A naive 571_701..573_700 CLEAN hops=0": 1,
    "never transcribe r587**）": 1,
    "·W251 冻结窗 6.7G bm-c 实锚": 1, "·W250 冻结窗 RAM 未记录（r1046 死窗": 1,
    "W240 冻结窗 33.2G bm-a 实锚）": 1,
    "selftest W252 face（": 1, "零假设零风险。": 1,
    "+W246=bm-a r1016 prereg derive": 1,
    "——本波上游链=": 1,
    "W253 freezer 承接面）】。": 1,
    "W243/W246/W248/W249/W250/W251 低 RAM 实烧先例": 1,
    "r1047/W251 先例 freeze-prep 同式": 1,
    "→W249 **0.000332**→W250 **0.000331**→W251 **0.000330**】": 1,
    "line_pre_w251 1.194": 1,
    "bm-c r1048 W251 §7 范式": 1, "bm-c r1048 W251 §8 范式": 1,
    "键 W251 实测 K-lift **0.0001**": 1,
    "n_eff_held_equal 974,335": 1,
    "queue-head FREEZE-UNBLOCKED lane": 1,
    "本候选=bm-c 自有席自有波": 1,
    "表尾 W251 行": 1,
    "pre-W252 全二百四十九行注册 N1 带表": 1,
    # zero-floors (absence assertions on T0)
    "waits-upstream ARMED": 0,
    "（**B 面=CLEAN": 0,
    "978,735": 0, "0.3235": 0, "567_501": 0, "569_501..569_700": 3,
    "552,320": 1,  # only the 投影 compound; bare face absent (baseline rolls supply it)
    "R254：W253": 0, "574_101": 0, "573_901..575_900": 0,
}

# floors for POST-chain correction legs (needles exist only in T1 after the pre-chain legs run)
VMAP_POST_LEGS = [
    # se_mu narrowing chain: wave roll consumed the W250 label; restore it and append true W252 se 0.000330
    ("→W249 **0.000332**→W251 **0.000331**→W252 **0.000330**】",
     "→W249 **0.000332**→W250 **0.000331**→W251 **0.000330**→W252 **0.000330**】", 1),
    # line_pre face: lowercase w-token escapes the uppercase W-roll (r1045 derive precedent);
    # W252 actual line_pre_w252 = 1.1942 (n1_w252_results.json skill_line machine value)
    ("line_pre_w251 1.194", "line_pre_w252 1.1942", 1),
    # sec7/8 backfill paradigm rows (W252 sec.7/8 backfilled by r1050)
    ("bm-c r1048 W252 §7 范式", "bm-c r1050 W252 §7 范式", 1),
    ("bm-c r1048 W252 §8 范式", "bm-c r1050 W252 §8 范式", 1),
    # low-RAM precedent list: rolled T1 form lost the W250 label; restore it and append W252
    # (engine self-burn 12/12 r1050 window on this low-RAM machine; chain precedent every-wave append)
    ("W243/W246/W248/W249/W251/W252 低 RAM 实烧先例", "W243/W246/W248/W249/W250/W251/W252 低 RAM 实烧先例", 1),
    # freeze-prep precedent face (W252 prereg derive window = r1049)
    ("r1047/W252 先例 freeze-prep 同式", "r1049/W252 先例 freeze-prep 同式", 1),
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

# freeze-window live face: regex-extract the r1049 stamp (zero transcription) -> r1052 + runtime FREEZE_T
_fw_pat = re.compile(r"bm-c 循环班 r1049 freeze 窗 2026-10-16 \d{2}:\dx")
_fw_hits = _fw_pat.findall(T1)
assert len(_fw_hits) == 1, "freeze-window stamp count=%d (expect 1): %r" % (len(_fw_hits), _fw_hits)
T1 = T1.replace(_fw_hits[0], "bm-c 循环班 r1052 freeze 窗 2026-10-16 " + FREEZE_T)

# post-chain correction legs: needles exist only in T1 (post chained rolls); floors checked on T1
for o, n, f in VMAP_POST_LEGS:
    if T1.count(o) < f:
        raise SystemExit("VMAP POST FLOOR FAIL: %r count=%d floor=%d" % (o, T1.count(o), f))
    T1 = T1.replace(o, n)

# ---------------- block replacements (needles marker-extracted from T1; NEW = final) ----------------
NEW = {}

WL = "（W138..W206+" + "+".join("W%d" % n for n in range(211, 253)) + "）"  # 69 estate + W211..W252 = 111 rows

NEW["b_band_ab"] = (
    "（**A 面=STAIRCASE-AFFECTS-A·1-HOP WALK 形态（W239 staircase era 后第二次连续 A-hop）**："
    "A 面算术续带 571_701..573_700（自注册 W252 A 尾 571_700 续）"
    "在席位窗宇宙（post-W252-REGISTERED 终态注册·freeze-UNBLOCKED）起点即 REFUSED"
    "（注册 W252 B 带 571_701..571_900 落 naive A 窗内=staircase re-emergence affects A 承袭·"
    "W252 prereg §5.5 item5 A-CLEAN-at-naive 投影=pre-W252 宇宙 face·被 live re-derive 超越 r587 superseded 如实披露）"
    "→walk 越注册 W252 B 尾 571_900→A first-clean **571_901..573_900**·**hops=1**·"
    "**A 落位 base==注册前波 B 尾+1（571_900+1）机检关系**"
    "（A_hop_chain 1 跳 verbatim leg1 机证〔window 571_701..573_700→jump 571_901·refuser band 571_701..571_900〕"
    "·A_clean_at_naive_start=false·A_staircase_hop_past_W252_B=true"
    "·A base>=registered prior-wave B tail+1 floor relation）"
    "·非转录 r587 前向单调断言在走册）；"
    "**B-ext exit seed=573_901..574_100**（**B 面=1-HOP own-A RESERVATION CASCADE·落位高于本波 A 窗形态（第三次连续 above-own-A 落位）**："
    "B naive 续带 571_901..572_100（自注册 W252 B 尾 571_900+1 续）"
    "在席位窗宇宙（post-W252-REGISTERED 终态注册·freeze-UNBLOCKED）起点即 REFUSED"
    "（naive B 窗 571_901..572_100 落本波 A first-clean 窗 571_901..573_900 内"
    "=own-A reservation cascade standard leg 强制·probe leg1 B_semantics 机证·B_naive_refused_at_start=true）"
    "——**own-A reservation standard leg 越本波 A 窗 571_901..573_900**（1 hop）"
    "→**1 hop** 落位 **573_901..574_100**·**B 落位 base==本波 A 窗尾+1（573_900+1）EXACT 机检关系**"
    "（B_hop lands-inside-A=false·B_lands_above_own_A=true·B_hop_chain 1 跳 verbatim 在 probe 回执 leg1 机证"
    "·非转录 r587·AB 同窗互斥面 leg2 律在场）；"
    "**W252 prereg §5.5 item5 投影承接面注记兑现+落位分歧如实披露**："
    "投影预言 W253 A naive 571_701..573_700 CLEAN（pre-W252 宇宙零 live refusers）——本窗 live re-derive A 面起点即被注册 W252 B 带拒"
    "（投影 A-CLEAN 未兑现=staircase affects A 承袭·第二次连续 A-hop）"
    "→A first-clean 上移 571_901..573_900→B naive 571_901..572_100 相应落本波 A 窗内→own-A reservation cascade 上移 573_901..574_100"
    "（post-W252 宇宙 live re-derive 必变·W252 prereg §5.5 已披露 live re-derive governs·禁转录投影 r587·"
    "落位高于投影=新拒面如实注记·已如实披露非分叉）"
)

NEW["b3_a_bandface"] = (
    "法典 §4 W253 行 A=571_901..573_900·**STAIRCASE-AFFECTS-A·1-HOP WALK 形态（W239 staircase era 后第二次连续 A-hop）**："
    "A 算术续带 571_701..573_700（自注册 W252 A 尾 571_700 续）"
    "在席位窗宇宙（post-W252-REGISTERED 终态注册·freeze-UNBLOCKED）起点即 REFUSED"
    "（注册 W252 B 带 571_701..571_900 落 naive A 窗内=W252 prereg §5.5 item5 A-CLEAN-at-naive 投影被 live re-derive 超越·r587 superseded 披露）"
    "→walk 越注册 W252 B 尾 571_900→A first-clean 571_901..573_900·**hops=1**·"
    "**A 落位 base==注册前波 B 尾+1（571_900+1）机检关系**"
    "（A_hop_chain 1 跳 verbatim probe leg1 机证·A_clean_at_naive_start=false·A_staircase_hop_past_W252_B=true）"
    "·非转录 r587·ADMIT 回执在场）"
)

NEW["b3_b_bandface"] = (
    "法典 §4 W253 行 B=573_901..574_100·**1-HOP own-A RESERVATION CASCADE·落位高于本波 A 窗形态**："
    "B naive 续带 571_901..572_100（自注册 W252 B 尾 571_900+1 续）"
    "在席位窗宇宙（post-W252-REGISTERED 终态注册）起点即 REFUSED"
    "（naive B 窗落本波 A first-clean 窗 571_901..573_900 内=own-A reservation cascade standard leg·probe leg1 B_semantics 机证）"
    "→own-A reservation 越本波 A 窗 571_901..573_900→1 hop 落位 573_901..574_100·"
    "**B 落位 base==本波 A 窗尾+1（573_900+1）机检关系**"
    "（B_hop lands-inside-A=false·B_lands_above_own_A=true·B_hop_chain 1 跳 verbatim 在 probe 回执"
    "·第三次连续 above-own-A 落位如实注记）"
    "·非转录 r587·与 W252 prereg §5.5 item5 投影承接面注记兑现+落位上移分歧披露收敛·ADMIT 回执在场）"
)

NEW["b1_chain_tail"] = (
    HIST_B1
    + "+W252=bm-c r1049 prereg derive（machine-SUB from frozen W251 tpl 9f5f106d6·freeze LANDED 472cc8386·banned_direction_gate rc0·同窗缺陷抓修 pre-freeze〔MSG seat-leg split form '-bmc-w251-seat' suffix x3 → full-form leg·r1047 needle 先例〕）"
    + "+五面冻结 splice（r1050 死窗 estate 11:33-11:34 LANDED e63561df3〔zero post-splice heal——splice commit=worktree bytes directly〕·dual-sha16 pf b3eed1c579e7f22f / n1 7252c90bad52de99·W252 块 parity 110 rows）"
    + "+引擎自燃 12/12（mtime-watch auto-ignite claim-exempt engine lane·ledger appends cbf6411bf+b3d563f4f batched 6+6 self-committed）"
    + "+bm-c r1050 finalize one-pass 已落（K=552,320·账本头 978,735 机读·n1_w252_results.json·11:5x·fivekeys ALL PASS·sixgate PRE-FINALIZE 14th consecutive 正相〔triple identity n1 7252c90bad52de99 / pf b3eed1c579e7f22f 零漂移·zero re-anchor face〕·K-lift +0.0001 in-band second consecutive nonzero micro-move）"
    "——本波上游链=W1..W252 finalize 全落地·零在飞上游席·干净前置**；"
    "席位公示=MSG-20261016-12xx-bmc-w253-seat 已推 origin f6433ee61 先于本冻结"
    "【r565 律·席位先行·bm-c r1050 窗发布·queue-head FREEZE-UNBLOCKED 承接·W252 own-wave finalize 已落=席位时即解锁】；"
    "下游 W254+ 投影见 §5.5（probe 机证 leg4·W254 freezer 承接面）】。"
)

NEW["b5_projection"] = (
    "5. **W254+ 投影（probe 机证 leg4·下波冻结方复核非转抄 r587 律）**：A naive first-clean 573_901..575_900 **CLEAN**（hops=0·pre-W253 宇宙零 live refusers）；"
    "B naive **574_101..574_300 CLEAN（hops=0）但落投影 A 窗 573_901..575_900 内**（W254p_B_lands_inside_W254p_A_naive=true——"
    "**staircase face 延续**：W253 A 571_901..573_900+B 573_901..574_100 注册后 naive W254 A 窗起点即被注册 W253 B 带拒（staircase affects A 承袭·第三次连续 A-hop 预期）"
    "→A first-clean 将上移·B own-A reservation cascade 落位相应上移——post-W253 宇宙 live re-derive 必变·禁转录投影）；"
    "**W254 冻结方禁假设 staircase A-base==prior-B-tail+1 或 B-base==own-A-tail+1 恒等·须重读 live trace**"
    "（W251 起 staircase affects A·W252/W253=A/B 双 1-hop 形态连续两波如实注记·seed-gap face 已于 W252 终结=A 首跳如实注记）"
    "——W254 冻结方必须在 post-W253 注册宇宙重 derive 且 derive B 时预留本波 A 窗 571_901..573_900+本波 B 带 573_901..574_100"
    "——leg2 律/E36 卡·W141 先例；verify at W254 prereg，hop 链逐跳在 probe 回执。"
)

NEW["b6_ram"] = "·W252 冻结窗 7.0G bm-c 实锚" + HIST_B6

NEW["b7_claim_projection"] = (
    "·probe W254+ 投影 A naive 573_901..575_900 CLEAN hops=0（零 live refusers）/ B naive 574_101..574_300 CLEAN hops=0 **但落 naive W254 A 窗内**"
    "→own-A reservation cascade 下 staircase 级联上移 **staircase face 延续 live re-derive governs 预披露**"
    "（投影 A naive 573_901..575_900 CLEAN·hops=0；投影 B naive 574_101..574_300 clean 但落 naive W254 A 窗 573_901..575_900 内——"
    "**above-own-A 承袭 face：W253 B 573_901..574_100 落本波 A 窗之上〔第三次连续〕·W253 A 面 1-hop=staircase affects A〔第二次连续〕·"
    "W254 冻结方禁假设 staircase A-base==prior-B-tail+1 或 B-base==own-A-tail+1 恒等·须重读 live trace·注册 W253 B 带将拒 naive W254 A 窗仅当重叠"
    "——**W254 freezer 承接面强制注记：须在 post-W253 宇宙重 derive 且 derive B 时预留本波 A 窗·W141 先例·never transcribe r587**）"
)

NEW["b8_selftest"] = (
    "selftest W253 face（A=staircase-hop honest-walk past the registered prior-wave B band 断言"
    "（A_hop_chain 与 probe 回执逐跳恒等·A 第二次连续跳=W239 staircase era 后承袭如实注记·A 落位不落任何已注册带内）"
    "·B=own-A reservation 1-hop lands-above-own-A 断言（B_hop_chain 与 probe 回执逐跳恒等·B 落位不落本波 A 窗内=同窗互斥断言·第三次连续 above-own-A 如实注记）·W252 行 parity 腿"
    "**estate 提取面注记**：冻结拼接脚本的 parity estate（W138..W206 69 行 full-span·r858 absorb 代）从**本机 W252 块物理字节**提取"
    "（结构已知·提取自证断言 69 行 range 恒等在场）——W252 块的自有 W239..W251 legs（13 行）不入 estate 路径"
    "·提取后新增 W239..W252 leg（14 行）构成 W253 块 parity 111 行" + WL + "·零假设零风险。"
)

# marker pairs: (block, start_marker, end_marker) -- needles matched on T1 (post-roll faces)
BLOCKS = [
    ("b_band_ab", "（**A 面=STAIRCASE-AFFECTS-A", "已如实披露非分叉）"),
    ("b3_a_bandface", "法典 §4 W253 行 A=569_701..571_700", "非转录 r587·ADMIT 回执在场）"),
    ("b3_b_bandface", "法典 §4 W253 行 B=571_701..571_900", "披露收敛·ADMIT 回执在场）"),
    ("b5_projection", "5. **W253+ 投影（probe 机证 leg4", "verify at W253 prereg，hop 链逐跳在 probe 回执。"),
    ("b7_claim_projection", "·probe W253+ 投影 A naive 571_701..573_700 CLEAN hops=0", "never transcribe r587**）"),
    ("b6_ram", "·W252 冻结窗 6.7G bm-c 实锚", "W240 冻结窗 33.2G bm-a 实锚）"),
    ("b8_selftest", "selftest W253 face（", "零假设零风险。"),
    ("b1_chain_tail", "+W246=bm-a r1016 prereg derive", "W253 freezer 承接面）】。"),
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
    "PERPETUAL-N1-W253", "research/PERPETUAL_N1_W253_PREREG.md",
    "571_901..573_900", "573_901..574_100", "978,735", "552,320", "554,520",
    "n1_w253_results.json", "MSG-20261016-12xx-bmc-w253-seat", "f6433ee61",
    "第 251 枚", "第七十三枚", "第 243 波", "第 73 枚",
    "STAIRCASE-AFFECTS-A", "第二次连续 A-hop", "第三次连续 above-own-A",
    "_w253bmc_20261016", "--wave 253", "波号 253",
    "W252=bm-c r1049 prereg derive", "r1050 finalize one-pass",
    "n_eff_held_equal 976,535", "−0.09273968", "0.2450479", "−0.09018",
    "（**0.3199** 实测锚）", "bm-c 循环班 r1052 freeze 窗", "本窗 free RAM ~1.8GB",
    "→W249 **0.000332**→W250 **0.000331**→W251 **0.000330**→W252 **0.000330**】",
    "queue-head FREEZE-UNBLOCKED lane", "seed_admit_gate rc0 双带 FREE",
    "A base=571901", "B base=573901",
    "bm-c r1050 W252 §7 范式", "bm-c r1050 W252 §8 范式",
    "W254 freezer 承接面", "verify at W254 prereg",
    "selftest W253 face", "W239..W252 leg（14 行）构成 W253 块 parity 111 行",
    "键 W252 实测 K-lift **0.0001**", "line_merged@K552,320 **1.1943**", "line_pre_w252 1.1942",
    "实差 0.0026 在带内", "已落账键·11:5x", "bm-c r1050 窗 11:5x",
    "r1049/W252 先例 freeze-prep 同式", "250 行单态", "probe leg0 机证 250 行",
    "_w253bmc_freeze_edits", "_w252bmc_freeze_edits", "本波上游链=W1..W252 finalize 全落地",
    "engine_owner==bm-c 72 行注册", "bmc rows 72", "bmc_rows=72",
    "queue-head FREEZE-UNBLOCKED 承接", "A 落位 base==注册前波 B 尾+1（571_900+1）",
    "B 落位 base==本波 A 窗尾+1（573_900+1）",
    "W252 块的自有 W239..W251 legs（13 行）",
    "bm-c r1050 席位", "bm-c r1050 席·queue-head FREEZE-UNBLOCKED 发布",
    "post-W252-REGISTERED 终态注册", "席位窗 probe leg0 实测 250 行",
    "W243/W246/W248/W249/W250/W251/W252 低 RAM 实烧先例", "·W252 冻结窗 7.0G bm-c 实锚",
    "本候选=bm-c 自有席自有波", "R254：W253 带从未指派",
    "B_hop lands-inside-A=false", "B_lands_above_own_A=true", "A_staircase_hop_past_W252_B=true",
    "§5.5 W254+ 投影承接机证", "exit rng=**573_901+j**", "B-ext exit seed=573_901..574_100",
    "A-ext seed=571_901..573_900",
    "probe leg0 bmc_rows=72 attempt-continuity face（r1050 窗算法·bm-c own seat+bmc live rows 72 实读）",
    "571_701..573_700", "571_901..572_100", "574_101..574_300", "573_901..575_900",
    "A_clean_at_naive_start=false",
    "表尾 W252 行", "pre-W253 全二百五十行注册 N1 带表",
    "engine_owner 行 242 注册在册", "freeze 窗 live derive 250 行单态 owner rows 242",
    "zero post-splice heal", "e63561df3", "472cc8386", "cbf6411bf", "b3d563f4f",
    "（r1050 席位窗实跑", "（bm-c r1050 席位",
    "W252 own-wave finalize 已落=席位时即解锁",
]
for s in MUST:
    assert s in T2, "MUST-HAVE missing: %r" % s

MUST_NOT = [
    "**A-ext seed=569_701", "567_501", "567_500", "545_301", "545_300", "545_500", "565_501",
    "FIRST-CLEAN·hops=0", "13-HOP", "13 hops", "A_hop_chain=[] 空集", "A_clean_at_naive_start=true",
    "连续第十四个",
    "−0.09274994", "0.2450362", "−0.08776", "**0.3153**", "实差 0.0050 在带内",
    "line_merged@K550,120", "547,920 合并池", "累计 null 池=547,920",
    "f9441de67", "MSG-20261016-10xx", "bmc-w252-seat", "第 72 枚", "第七十二枚", "第 249 枚", "第 242 波",
    "engine_owner 行 241", "owner rows 241", "bmc rows 71", "bmc_rows=71", "engine_owner==bm-c 71",
    "249 行", "二百四十九", "r1048 窗算法", "（bm-c r1048 席", "（r1048 席位窗实跑",
    "bm-c r1048 窗 10:0x", "bm-c 循环班 r1049", "live-read r1049", "已落账键·10:0x",
    "波号 252", "--wave 252", "R253：W252",
    "verify at W253 prereg", "W253 freezer 承接面", "W253p_", "W253 冻结方", "W253+ 投影",
    "键 W250 实测 K-lift", "line_pre_w249", "键 W251 实测 K-lift **0.0001**", "line_pre_w251 1.194",
    "（**B 面=CLEAN", "waits-upstream ARMED",
    "（bm-c r1043 席", "第 70 枚", "engine_owner 行 239",
    "·W250 冻结窗 RAM 未记录（r1042",
    "W239..W251 leg（13 行）构成 W252 块 parity 110 行",
    "selftest W252 face", "本窗 free RAM ~7.0GB",
    "首次 A-hop", "第二次连续 above-own-A",
]
for s in MUST_NOT:
    assert s not in T2, "MUST-NOT-HAVE present: %r (count=%d)" % (s, T2.count(s))

# projection-fulfillment count gates
assert T2.count("W253+ 投影") == 0, "W253+ 投影 count=%d (expect 0)" % T2.count("W253+ 投影")
assert T2.count("W254+ 投影") == 4, "W254+ 投影 count=%d (expect 4 = b1 tail + b5 title + b7 claim + sec8 rolled)" % T2.count("W254+ 投影")
assert T2.count("hops=1") == 2, "hops=1 count=%d (expect 2 = 带位 A + §3 A)" % T2.count("hops=1")

# residue scan: all X_Y..X_Y windows well-formed
for m in re.finditer(r"(\d{3}_\d{3})\.\.(\d{3}_\d{3})", T2):
    lo = int(m.group(1).replace("_", "")); hi = int(m.group(2).replace("_", ""))
    assert lo <= hi, "malformed window %s" % m.group(0)

io.open(OUT, "w", encoding="utf-8", newline="").write(T2)
print("W253 PREREG DERIVE OK -> %s (%d bytes, %d lines)" % (OUT, len(T2.encode("utf-8")), T2.count("\n") + 1))
print("freeze window face: bm-c 循环班 r1052 freeze 窗 2026-10-16 %s" % FREEZE_T)
print("blocks replaced: %s" % ", ".join(n for n, _, _ in BLOCKS))
print("vmap legs: %d floors: %d post-legs: %d MUST: %d MUST_NOT: %d" % (len(VMAP), len(VMAP_FLOORS), len(VMAP_POST_LEGS), len(MUST), len(MUST_NOT)))
print("src blob-verified == c2c7076ac969a78551539ce216d0eaca71e63e58 @ 472cc8386 (frozen pre-run face; HEAD post-backfill twin b79b055f disclosed, NOT used)")
