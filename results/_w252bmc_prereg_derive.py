# -*- coding: utf-8 -*-
# r1049 bm-c: W252 prereg derive (count-asserted ordered transform + marker-extracted block replaces).
# Source = committed frozen W251 prereg (git 9f5f106d6:research/PERPETUAL_N1_W251_PREREG.md, 35,820 bytes
# -- the frozen pre-run face; sec7/8 placeholders intact). Extracted to
# results/_w252bmc_w251_frozen_face.txt and byte-verified IN-SCRIPT via git hash-object
# == blob 60d2b4e9359d68ceb694cc63a343a226bd7662f2 (sha256_16 228eb5385479fff2).
# W252 facts (all machine-derived, never transcribed):
#   - seat probe ADMIT receipt results/_w252bmc_20261016_probe_receipt.json (r1048 window, seat pushed
#     origin f9441de67, MSG-20261016-10xx-bmc-w252-seat). STAIRCASE-AFFECTS-A live face:
#     A naive 569_501..571_500 REFUSED at start (registered W251 B band 569_501..569_700 sits INSIDE the
#     naive A window) -> A first-clean 569_701..571_700 hops=1 (FIRST A-HOP SINCE W239 STAIRCASE ERA;
#     W251 prereg sec.5 item5 A-CLEAN projection was a pre-W251-universe face, superseded live r587,
#     divergence disclosed) / B naive 569_701..569_900 CLEAN at start but lands INSIDE the own-wave W252
#     A first-clean window -> own-A reservation hop past 571_700 -> 571_701..571_900 hops=1
#     (second consecutive above-own-A landing; B base==own-A tail+1 re-emerges);
#     seed_admit FREE x2 (A base=569701 span=2000 / B base=571701 span=200);
#     leg0 rows=249 owner_rows=241 bmc_rows=71 bmc_ordinal=72 ordinal=242;
#     leg4 W253+ projection: A naive 571_701..573_700 clean / B naive 571_901..572_100 clean but lands
#     INSIDE W253p_A naive (staircase face continues; live re-derive governs).
#   - upstream W251 finalize landed (bm-c r1048 continuation, ledger 974,335+2,200=976,535 EXACT):
#     merged K=550,120 / merged mu -0.09274993928597397 / sigma 0.24503622147677206 / se_mu 0.000330 /
#     W251-only mu -0.08776395454545455 / A p95 0.3153 / K-lift +0.0001 in-band first nonzero micro-move /
#     n_eff_held_equal 974,335 / line_pre_w251 1.194 / line_merged_550120 1.1941
#     (results/perpetual_faces/n1_w251_results.json + results/_r1048bmc_w251_fivekeys.json)
#   - W251 chain: prereg derive r1047 freeze LANDED 9f5f106d6 + five-face freeze splice r1048 dead-window
#     estate 09:31-09:32 LANDED c813471cd (zero post-splice heal) + engine self-burn 12/12 (ledger appends
#     c15c32afd+e46094052) + r1048 continuation finalize one-pass (sixgate PRE-FINALIZE ALL PASS first-run
#     triple identity n1 c9de218d7c362499 / pf d88cd951f44dfaf6; fivekeys ALL PASS; sec.7/8 backfilled)
# Disclosed same-window needle heals: none new (all rolls count-asserted; POST legs repair wave-roll
# collateral only: se_mu chain tail restore + K-lift value face 0.0000->0.0001).
import io, os, sys, datetime, subprocess, hashlib

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(REPO, "results", "_w252bmc_w251_frozen_face.txt")
OUT = os.path.join(REPO, "research", "PERPETUAL_N1_W252_PREREG.md")

# --- source byte-identity gate (blob @ 9f5f106d6) ---
_blob_expect = "60d2b4e9359d68ceb694cc63a343a226bd7662f2"
_ho = subprocess.run(["git", "hash-object", SRC], capture_output=True, text=True, cwd=REPO).stdout.strip()
assert _ho == _blob_expect, "SRC blob mismatch: got %s expect %s" % (_ho, _blob_expect)

T0 = io.open(SRC, encoding="utf-8", newline="").read()
assert hashlib.sha256(T0.encode("utf-8")).hexdigest()[:16] == "228eb5385479fff2", "SRC sha mismatch"

P1, P2, P3 = "\x01W\x01", "\x01N\x01", "\x01B\x01"

now = datetime.datetime.now()
FREEZE_T = "%02d:%dx" % (now.hour, now.minute // 10)

# machine-extracted historical spans (from T0 PRE-roll bytes: zero transcription for carried content)
_i_b1 = T0.index("+W246=bm-a r1016 prereg derive")
_j_b1 = T0.index("——本波上游链=")
HIST_B1 = T0[_i_b1:_j_b1]  # W246..W250 chain legs verbatim (frozen template bytes)
_i_b6 = T0.index("·W250 冻结窗 RAM 未记录（r1046 死窗")
_b6_end = "W240 冻结窗 33.2G bm-a 实锚）"
_j_b6 = T0.index(_b6_end) + len(_b6_end)
HIST_B6 = T0[_i_b6:_j_b6]  # W250..W240 freeze-window RAM ledger verbatim

VMAP = [
    # projection first, then line_merged face, then prior-K bare, then ledger heads (order-critical)
    ("550,120 投影", "552,320 投影"),
    ("line_merged@K547,920 **1.1939**", "line_merged@K550,120 **1.1941**"),
    ("547,920", "550,120"),
    ("974,335", "976,535"),
    ("972,135", "974,335"),
    # sec5 measured keys -> W251 measured faces (n1_w251_results.json machine values)
    ("−0.09276996", "−0.09274994"),
    ("−0.09226", "−0.08776"),
    ("0.2450351", "0.2450362"),
    ("实差 0.0005 在带内", "实差 0.0050 在带内"),
    ("（**0.3235** 实测锚）", "（**0.3153** 实测锚）"),
    # band values outside block regions (staircase-affects-A + own-A reservation faces)
    ("A-ext seed=567_501..569_500", "A-ext seed=569_701..571_700"),
    ("entry rng seed=**567_501+j**", "entry rng seed=**569_701+j**"),
    ("entry rng=**567_501+j**", "entry rng=**569_701+j**"),
    ("exit rng=**569_501+j**", "exit rng=**571_701+j**"),
    ("A base=567501 span=2000 checked=2000 verdict=FREE", "A base=569701 span=2000 checked=2000 verdict=FREE"),
    ("B base=569501 span=200 checked=200 verdict=FREE", "B base=571701 span=200 checked=200 verdict=FREE"),
    ("R252：W251", "R253：W252"),
    # seat / provenance faces (W252 seat published r1048 window, origin f9441de67)
    ("MSG-20261016-085x-bmc-w251-seat", "MSG-20261016-10xx-bmc-w252-seat"),
    ("bc3b2b693", "f9441de67"),
    ("（bm-c r1046 席·queue-head FREEZE-UNBLOCKED 发布）", "（bm-c r1048 席·queue-head FREEZE-UNBLOCKED 发布）"),
    ("（bm-c r1046 席位", "（bm-c r1048 席位"),
    ("（r1046 席位窗实跑", "（r1048 席位窗实跑"),
    # finalize window faces (specific first, then catch-all)
    ("bm-c r1046 窗 08:4x", "bm-c r1048 窗 10:0x"),
    ("08:4x", "10:0x"),
    # freeze window + engine live-read + RAM head (bm-c current window honest: ~7.0G free of 23.9G,
    # W20 SCREEN 4/4 closed, engine queue idle, CPU lane independent)
    ("bm-c 循环班 r1047 freeze 窗 2026-10-16 09:0x", "bm-c 循环班 r1049 freeze 窗 2026-10-16 " + FREEZE_T),
    ("saturation_engine.py status live-read r1047", "saturation_engine.py status live-read r1049"),
    ("本窗 free RAM ~6.7GB（", "本窗 free RAM ~7.0GB（"),
    # wave-number roll (chained placeholders)
    ("W251", P1), ("W250", "W251"), (P1, "W252"),
    # result-file names (chained)
    ("n1_w251", P2), ("n1_w250", "n1_w251"), (P2, "n1_w252"),
    # probe/freeze script basenames (chained; current face _w252bmc <- template _w251bmc)
    ("_w251bmc", P3), ("_w250bmc", "_w251bmc"), (P3, "_w252bmc"),
    # runner CLI wave
    ("--wave 251", "--wave 252"),
    ("波号 251", "波号 252"),
    # pool/engine ordinals
    ("第 249 枚", "第 250 枚"),
    ("第 241 波", "第 242 波"),
    ("bm-c 第七十一枚自有波", "bm-c 第七十二枚自有波"),
    # subsumption-order fix: compound needle contains 第 71 枚 -> MUST run before the bare roll
    ("bmc rows 70+候选=第 71 枚 EXACT", "bmc rows 71+候选=第 72 枚 EXACT"),
    ("第 71 枚", "第 72 枚"),
    ("probe leg0 bmc_rows=70 attempt-continuity face（r1046 窗算法·bm-c own seat+bmc live rows 70 实读）",
     "probe leg0 bmc_rows=71 attempt-continuity face（r1048 窗算法·bm-c own seat+bmc live rows 71 实读）"),
    ("engine_owner==bm-c 70 行注册", "engine_owner==bm-c 71 行注册"),
    ("engine_owner 行 240 注册在册", "engine_owner 行 241 注册在册"),
    # registry scan faces
    ("全二百四十八行注册 N1 带表", "全二百四十九行注册 N1 带表"),
    ("freeze 窗 live derive 248 行单态 owner rows 240", "freeze 窗 live derive 249 行单态 owner rows 241"),
    ("perpetual_faces.py 零 249 行", "perpetual_faces.py 零 250 行"),
    ("共二百四十八面实测", "共二百四十九面实测"),
]

VMAP_FLOORS = {
    "550,120 投影": 1, "line_merged@K547,920 **1.1939**": 1,
    "547,920": 7, "974,335": 3, "972,135": 2,
    "−0.09276996": 1, "−0.09226": 1, "0.2450351": 1, "实差 0.0005 在带内": 1,
    "（**0.3235** 实测锚）": 1,
    "A-ext seed=567_501..569_500": 1,
    "entry rng seed=**567_501+j**": 1, "entry rng=**567_501+j**": 1,
    "exit rng=**569_501+j**": 1,
    "A base=567501 span=2000 checked=2000 verdict=FREE": 1,
    "B base=569501 span=200 checked=200 verdict=FREE": 1,
    "R252：W251": 1,
    "W251": 28, "W250": 75,
    "n1_w251": 4, "n1_w250": 3, "_w251bmc": 4, "_w250bmc": 1,
    "--wave 251": 2, "波号 251": 1,
    "第 249 枚": 1, "第 241 波": 1, "bm-c 第七十一枚自有波": 1,
    "bmc rows 70+候选=第 71 枚 EXACT": 2, "第 71 枚": 2,
    "probe leg0 bmc_rows=70 attempt-continuity face（r1046 窗算法·bm-c own seat+bmc live rows 70 实读）": 1,
    "engine_owner==bm-c 70 行注册": 1, "engine_owner 行 240 注册在册": 1,
    "全二百四十八行注册 N1 带表": 1,
    "freeze 窗 live derive 248 行单态 owner rows 240": 1,
    "共二百四十八面实测": 1, "perpetual_faces.py 零 249 行": 1,
    "MSG-20261016-085x-bmc-w251-seat": 4, "bc3b2b693": 3,
    "（bm-c r1046 席·queue-head FREEZE-UNBLOCKED 发布）": 1,
    "（bm-c r1046 席位": 1, "（r1046 席位窗实跑": 1,
    "bm-c r1046 窗 08:4x": 1, "08:4x": 3,
    "bm-c 循环班 r1047 freeze 窗 2026-10-16 09:0x": 1,
    "saturation_engine.py status live-read r1047": 1,
    "本窗 free RAM ~6.7GB（": 1,
    # block-marker stability floors (raw template face)
    "（**A 面=FIRST-CLEAN·hops=0 seed-decoupled A-continuation 形态**": 1,
    "已如实披露非分叉）": 1,
    "法典 §4 W251 行 A=567_501..569_500": 1,
    "法典 §4 W251 行 B=569_501..569_700": 1,
    "兑现收敛·ADMIT 回执在场）": 1,
    "5. **W252+ 投影（probe 机证 leg4": 1,
    "verify at W252 prereg，hop 链逐跳在 probe 回执。": 1,
    "·probe W252+ 投影 A naive 569_501..571_500 CLEAN hops=0": 1,
    "never transcribe r587**）": 1,
    "selftest W251 face（": 1, "零假设零风险。": 1,
    "·W250 冻结窗 RAM 未记录（r1046 死窗": 1, "W240 冻结窗 33.2G bm-a 实锚）": 1,
    "+W246=bm-a r1016 prereg derive": 1,
    "——本波上游链=": 1,
    "W243/W246/W248/W249/W250 低 RAM 实烧先例": 1,
    "bm-c r1046 W250 §7 范式": 1, "bm-c r1046 W250 §8 范式": 1,
    "r1045/W250 先例 freeze-prep 同式": 1,
    "§5.5 W252+ 投影承接机证": 1,
    "键 W250 实测 K-lift **0.0000**": 1,
    "→W249 **0.000332**→W250 **0.000331**】": 1,
    "probe leg0 机证 248 行〔": 1, "席位窗 probe leg0 实测 248 行〔": 1,
    "本候选=bm-c 自有席自有波": 1,
    "queue-head FREEZE-UNBLOCKED lane": 1,
    "waits-upstream ARMED": 0,
    "（**B 面=CLEAN·hops=0 算术续带承袭形态**": 0,
}

# floors for POST-chain correction legs (needles exist only in T1 after the pre-chain legs run)
VMAP_POST_LEGS = [
    # probe leg0 registry faces: W251 splice landed BEFORE the seat window (zero +1 owed)
    ("probe leg0 机证 248 行〔", "probe leg0 机证 249 行〔", 1),
    ("席位窗 probe leg0 实测 248 行〔", "席位窗 probe leg0 实测 249 行〔", 1),
    # se_mu narrowing chain: wave roll consumed the W250 label; restore it and append true W251 se 0.000330
    ("→W249 **0.000332**→W251 **0.000331**】",
     "→W249 **0.000332**→W250 **0.000331**→W251 **0.000330**】", 1),
    # line_pre face: lowercase w-token escapes the uppercase W-roll (r1045 derive precedent);
    # W251 actual line_pre_w251 = 1.194 (n1_w251_results.json skill_line machine value)
    ("line_pre_w250 1.1939", "line_pre_w251 1.194", 1),
    # sec7/8 backfill paradigm rows (W251 sec.7/8 backfilled by r1048)
    ("bm-c r1046 W251 §7 范式", "bm-c r1048 W251 §7 范式", 1),
    ("bm-c r1046 W251 §8 范式", "bm-c r1048 W251 §8 范式", 1),
    # low-RAM precedent list: rolled T1 form lost the W250 label (rolled to W251); restore it and
    # append W251 (engine self-burn 12/12 r1048 window on this 6.7G-free machine)
    ("W243/W246/W248/W249/W251 低 RAM 实烧先例", "W243/W246/W248/W249/W250/W251 低 RAM 实烧先例", 1),
    # freeze-prep precedent face (W251 prereg derive window = r1047)
    ("r1045/W251 先例 freeze-prep 同式", "r1047/W251 先例 freeze-prep 同式", 1),
    # sec.8 placeholder projection-label roll (W252+ -> W253+ face)
    ("§5.5 W252+ 投影承接机证", "§5.5 W253+ 投影承接机证", 1),
    # K-lift value face: wave roll relabeled W250->W251; true W251 K-lift = +0.0001 (machine value)
    ("键 W251 实测 K-lift **0.0000**", "键 W251 实测 K-lift **0.0001**", 1),
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

# post-chain correction legs: needles exist only in T1 (post chained rolls); floors checked on T1
for o, n, f in VMAP_POST_LEGS:
    if T1.count(o) < f:
        raise SystemExit("VMAP POST FLOOR FAIL: %r count=%d floor=%d" % (o, T1.count(o), f))
    T1 = T1.replace(o, n)

# ---------------- block replacements (needles marker-extracted from T1; NEW = final) ----------------
NEW = {}

WL = "（W138..W206+" + "+".join("W%d" % n for n in range(211, 252)) + "）"  # 69 estate + W211..W251 = 110 rows

NEW["b_band_ab"] = (
    "（**A 面=STAIRCASE-AFFECTS-A·1-HOP WALK 形态（W239 staircase era 后首次 A-hop）**："
    "A 面算术续带 569_501..571_500（自注册 W251 A 尾 569_500 续）"
    "在席位窗宇宙（post-W251-REGISTERED 终态注册·freeze-UNBLOCKED）起点即 REFUSED"
    "（注册 W251 B 带 569_501..569_700 落 naive A 窗内=staircase re-emergence affects A·"
    "W251 prereg §5.5 item5 A-CLEAN 投影=pre-W251 宇宙 face·被 live re-derive 超越 r587 superseded 如实披露）"
    "→walk 越注册 W251 B 尾 569_700→A first-clean **569_701..571_700**·**hops=1**·"
    "**A 落位 base==注册前波 B 尾+1（569_700+1）机检关系**"
    "（A_hop_chain 1 跳 verbatim leg1 机证〔window 569_501..571_500→jump 569_701·refuser band 569_501..569_700〕"
    "·A_clean_at_naive_start=false·A_staircase_hop_past_W251_B=true"
    "·A base>=registered prior-wave B tail+1 floor relation）"
    "·非转录 r587 前向单调断言在走册）；"
    "**B-ext exit seed=571_701..571_900**（**B 面=1-HOP own-A RESERVATION·落位高于本波 A 窗形态（第二次连续 above-own-A 落位）**："
    "B naive 续带 569_701..569_900（自注册 W251 B 尾 569_700+1 续）"
    "在席位窗宇宙（post-W251-REGISTERED 终态注册·freeze-UNBLOCKED）起点即 REFUSED"
    "（naive B 窗 569_701..569_900 落本波 A first-clean 窗 569_701..571_700 内"
    "=own-A reservation standard leg 强制·probe leg1 B_semantics 机证·B_naive_refused_at_start=true）"
    "——**own-A reservation standard leg 越本波 A 窗 569_701..571_700**（1 hop）"
    "→**1 hop** 落位 **571_701..571_900**·**B 落位 base==本波 A 窗尾+1（571_700+1）EXACT 机检关系**"
    "（B_hop lands-inside-A=false·B_lands_above_own_A=true·B_hop_chain 1 跳 verbatim 在 probe 回执 leg1 机证"
    "·非转录 r587·AB 同窗互斥面 leg2 律在场）；"
    "**W251 prereg §5.5 item5 投影承接面注记兑现+落位分歧如实披露**："
    "投影预言 W252 B own-A reservation 下 ~571_501..571_700 落位——本窗 live re-derive A 面自身被注册 W251 B 带拒"
    "（投影 A-CLEAN 未兑现=staircase affects A·W239 staircase era 后首次 A-hop）"
    "→A first-clean 上移 569_701..571_700→B 预留落位相应上移 571_701..571_900"
    "（post-W251 宇宙 live re-derive 必变·W251 prereg §5.5 已披露 live re-derive governs·禁转录投影 r587·"
    "落位高于投影=新拒面如实注记·已如实披露非分叉）"
)

NEW["b3_a_bandface"] = (
    "法典 §4 W252 行 A=569_701..571_700·**STAIRCASE-AFFECTS-A·1-HOP WALK 形态（W239 staircase era 后首次 A-hop）**："
    "A 算术续带 569_501..571_500（自注册 W251 A 尾 569_500 续）"
    "在席位窗宇宙（post-W251-REGISTERED 终态注册·freeze-UNBLOCKED）起点即 REFUSED"
    "（注册 W251 B 带 569_501..569_700 落 naive A 窗内=W251 prereg §5.5 item5 A-CLEAN 投影被 live re-derive 超越·r587 superseded 披露）"
    "→walk 越注册 W251 B 尾 569_700→A first-clean 569_701..571_700·**hops=1**·"
    "**A 落位 base==注册前波 B 尾+1（569_700+1）机检关系**"
    "（A_hop_chain 1 跳 verbatim probe leg1 机证·A_clean_at_naive_start=false·A_staircase_hop_past_W251_B=true）"
    "·非转录 r587·ADMIT 回执在场）"
)

NEW["b3_b_bandface"] = (
    "法典 §4 W252 行 B=571_701..571_900·**1-HOP own-A RESERVATION·落位高于本波 A 窗形态**："
    "B naive 续带 569_701..569_900（自注册 W251 B 尾 569_700+1 续）"
    "在席位窗宇宙（post-W251-REGISTERED 终态注册）起点即 REFUSED"
    "（naive B 窗落本波 A first-clean 窗 569_701..571_700 内=own-A reservation standard leg·probe leg1 B_semantics 机证）"
    "→own-A reservation 越本波 A 窗 569_701..571_700→1 hop 落位 571_701..571_900·"
    "**B 落位 base==本波 A 窗尾+1（571_700+1）机检关系**"
    "（B_hop lands-inside-A=false·B_lands_above_own_A=true·B_hop_chain 1 跳 verbatim 在 probe 回执"
    "·第二次连续 above-own-A 落位如实注记）"
    "·非转录 r587·与 W251 prereg §5.5 item5 投影承接面注记兑现+落位上移分歧披露收敛·ADMIT 回执在场）"
)

NEW["b1_chain_tail"] = (
    HIST_B1
    + "+W251=bm-c r1047 prereg derive（machine-SUB from frozen W250 tpl 4f7a130ff·freeze LANDED 9f5f106d6·banned_direction_gate rc0·1 disclosed needle heal〔sec8 projection-label lag W251+→W252+〕）"
    + "+五面冻结 splice（r1048 死窗 estate 09:31-09:32 LANDED c813471cd〔zero post-splice heal——splice commit=worktree bytes directly〕·dual-sha16 pf d88cd951f44dfaf6 / n1 c9de218d7c362499·W251 块 parity 109 rows）"
    + "+引擎自燃 12/12（mtime-watch auto-ignite claim-exempt engine lane·ledger appends c15c32afd+e46094052 batched 6+6 self-committed）"
    + "+bm-c r1048 finalize one-pass 已落（K=550,120·账本头 976,535 机读·n1_w251_results.json·10:0x·fivekeys ALL PASS·sixgate PRE-FINALIZE 13th consecutive 正相〔triple identity worktree==receipt==landed blob·zero re-anchor face〕·K-lift +0.0001 in-band first nonzero micro-move）"
    "——本波上游链=W1..W251 finalize 全落地·零在飞上游席·干净前置**；"
    "席位公示=MSG-20261016-10xx-bmc-w252-seat 已推 origin f9441de67 先于本冻结"
    "【r565 律·席位先行·bm-c r1048 窗发布·queue-head FREEZE-UNBLOCKED 承接·W251 own-wave finalize 已落=席位时即解锁】；"
    "下游 W253+ 投影见 §5.5（probe 机证 leg4·W253 freezer 承接面）】。"
)

NEW["b5_projection"] = (
    "5. **W253+ 投影（probe 机证 leg4·下波冻结方复核非转抄 r587 律）**：A naive first-clean 571_701..573_700 **CLEAN**（hops=0·pre-W252 宇宙零 live refusers）；"
    "B naive **571_901..572_100 CLEAN（hops=0）但落投影 A 窗 571_701..573_700 内**（W253p_B_lands_inside_W253p_A_naive=true——"
    "**staircase face 延续**：W252 A 569_701..571_700+B 571_701..571_900 注册后 naive W253 A 窗起点即被注册 W252 B 带拒（staircase affects A 承袭）"
    "→A first-clean 将上移·B own-A reservation 落位相应上移——post-W252 宇宙 live re-derive 必变·禁转录投影）；"
    "**W253 冻结方禁假设 staircase A-base==prior-B-tail+1 或 B-base==own-A-tail+1 恒等·须重读 live trace**"
    "（W251 起 staircase affects A·W252=A/B 双 1-hop 形态如实注记·seed-gap face 已于 W252 终结=A 首跳如实注记）"
    "——W253 冻结方必须在 post-W252 注册宇宙重 derive 且 derive B 时预留本波 A 窗 569_701..571_700+本波 B 带 571_701..571_900"
    "——leg2 律/E36 卡·W141 先例；verify at W253 prereg，hop 链逐跳在 probe 回执。"
)

NEW["b6_ram"] = "·W251 冻结窗 6.7G bm-c 实锚" + HIST_B6

NEW["b7_claim_projection"] = (
    "·probe W253+ 投影 A naive 571_701..573_700 CLEAN hops=0（零 live refusers）/ B naive 571_901..572_100 CLEAN hops=0 **但落 naive W253 A 窗内**"
    "→own-A reservation 下 staircase 级联上移 **staircase face 延续 live re-derive governs 预披露**"
    "（投影 A naive 571_701..573_700 CLEAN·hops=0；投影 B naive 571_901..572_100 clean 但落 naive W253 A 窗 571_701..573_700 内——"
    "**above-own-A 承袭 face：W252 B 571_701..571_900 落本波 A 窗之上〔第二次连续〕·W252 A 面 1-hop=staircase affects A〔W239 era 后首次〕·"
    "W253 冻结方禁假设 staircase A-base==prior-B-tail+1 或 B-base==own-A-tail+1 恒等·须重读 live trace·注册 W252 B 带将拒 naive W253 A 窗仅当重叠"
    "——**W253 freezer 承接面强制注记：须在 post-W252 宇宙重 derive 且 derive B 时预留本波 A 窗·W141 先例·never transcribe r587**）"
)

NEW["b8_selftest"] = (
    "selftest W252 face（A=staircase-hop honest-walk past the registered prior-wave B band 断言"
    "（A_hop_chain 与 probe 回执逐跳恒等·A 首跳=W239 staircase era 后首次如实注记·A 落位不落任何已注册带内）"
    "·B=own-A reservation 1-hop lands-above-own-A 断言（B_hop_chain 与 probe 回执逐跳恒等·B 落位不落本波 A 窗内=同窗互斥断言·第二次连续 above-own-A 如实注记）·W251 行 parity 腿"
    "**estate 提取面注记**：冻结拼接脚本的 parity estate（W138..W206 69 行 full-span·r858 absorb 代）从**本机 W251 块物理字节**提取"
    "（结构已知·提取自证断言 69 行 range 恒等在场）——W251 块的自有 W239..W250 legs（12 行）不入 estate 路径"
    "·提取后新增 W239..W251 leg（13 行）构成 W252 块 parity 110 行" + WL + "·零假设零风险。"
)

# marker pairs: (block, start_marker, end_marker) -- needles extracted from T1 at runtime (zero transcription)
BLOCKS = [
    ("b_band_ab", "（**A 面=FIRST-CLEAN·hops=0 seed-decoupled A-continuation 形态**", "已如实披露非分叉）"),
    ("b3_a_bandface", "法典 §4 W252 行 A=567_501..569_500", "非转录 r587·ADMIT 回执在场）"),
    ("b3_b_bandface", "法典 §4 W252 行 B=569_501..569_700", "兑现收敛·ADMIT 回执在场）"),
    ("b5_projection", "5. **W252+ 投影（probe 机证 leg4", "verify at W252 prereg，hop 链逐跳在 probe 回执。"),
    ("b7_claim_projection", "·probe W252+ 投影 A naive 569_501..571_500 CLEAN hops=0", "never transcribe r587**）"),
    ("b6_ram", "·W251 冻结窗 RAM 未记录（r1046 死窗", "W240 冻结窗 33.2G bm-a 实锚）"),
    ("b8_selftest", "selftest W252 face（", "零假设零风险。"),
    ("b1_chain_tail", "+W246=bm-a r1016 prereg derive", "W252 freezer 承接面）】。"),
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
    "PERPETUAL-N1-W252", "research/PERPETUAL_N1_W252_PREREG.md",
    "569_701..571_700", "571_701..571_900", "976,535", "550,120", "552,320",
    "n1_w252_results.json", "MSG-20261016-10xx-bmc-w252-seat", "f9441de67",
    "第 72 枚", "第七十二枚", "第 250 枚", "第 242 波",
    "STAIRCASE-AFFECTS-A", "W239 staircase era 后首次 A-hop",
    "_w252bmc_20261016", "--wave 252", "波号 252",
    "W251=bm-c r1047 prereg derive", "r1048 finalize one-pass",
    "n_eff_held_equal 974,335", "−0.09274994", "0.2450362", "−0.08776",
    "（**0.3153** 实测锚）", "bm-c 循环班 r1049 freeze 窗", "本窗 free RAM ~7.0GB",
    "→W249 **0.000332**→W250 **0.000331**→W251 **0.000330**】",
    "queue-head FREEZE-UNBLOCKED lane",
    "seed_admit_gate rc0 双带 FREE", "A base=569701", "B base=571701",
    "bm-c r1048 W251 §7 范式", "bm-c r1048 W251 §8 范式",
    "W253 freezer 承接面", "verify at W253 prereg",
    "selftest W252 face", "W239..W251 leg（13 行）构成 W252 块 parity 110 行",
    "W251 实测 K-lift **0.0001**", "line_merged@K550,120 **1.1941**", "line_pre_w251 1.194",
    "实差 0.0050 在带内", "已落账键·10:0x", "bm-c r1048 窗 10:0x",
    "r1047/W251 先例 freeze-prep 同式", "249 行单态", "probe leg0 机证 249 行",
    "_w252bmc_freeze_edits", "_w251bmc_freeze_edits", "本波上游链=W1..W251 finalize 全落地",
    "engine_owner==bm-c 71 行注册", "bmc rows 71", "bmc_rows=71",
    "queue-head FREEZE-UNBLOCKED 承接", "A 落位 base==注册前波 B 尾+1（569_700+1）",
    "B 落位 base==本波 A 窗尾+1（571_700+1）",
    "W251 块的自有 W239..W250 legs（12 行）",
    "bm-c r1048 席位", "queue-head FREEZE-UNBLOCKED 发布",
    "post-W251-REGISTERED 终态注册", "席位窗 probe leg0 实测 249 行",
    "W243/W246/W248/W249/W250/W251 低 RAM 实烧先例", "·W251 冻结窗 6.7G bm-c 实锚",
    "本候选=bm-c 自有席自有波", "R253：W252 带从未指派",
    "B_hop lands-inside-A=false", "B_lands_above_own_A=true", "A_staircase_hop_past_W251_B=true",
    "§5.5 W253+ 投影承接机证", "exit rng=**571_701+j**", "B-ext exit seed=571_701..571_900",
    "A-ext seed=569_701..571_700",
    "probe leg0 bmc_rows=71 attempt-continuity face（r1048 窗算法·bm-c own seat+bmc live rows 71 实读）",
    "569_501..571_500", "569_701..569_900", "571_901..572_100", "571_701..573_700",
    "A_clean_at_naive_start=false", "第二次连续 above-own-A",
    "表尾 W251 行", "pre-W252 全二百四十九行注册 N1 带表",
    "engine_owner 行 241 注册在册", "freeze 窗 live derive 249 行单态 owner rows 241",
    "zero post-splice heal", "c813471cd", "9f5f106d6",
]
for s in MUST:
    assert s in T2, "MUST-HAVE missing: %r" % s

MUST_NOT = [
    "**A-ext seed=567_501", "567_501", "567_500", "545_301", "545_300", "545_500", "565_501",
    "FIRST-CLEAN·hops=0", "13-HOP", "13 hops", "A_hop_chain=[] 空集", "A_clean_at_naive_start=true",
    "连续第十四个",
    "−0.09276996", "0.2450351", "−0.09226", "**0.3235**", "实差 0.0005 在带内",
    "line_merged@K547,920", "547,920 合并池", "累计 null 池=547,920",
    "bc3b2b693", "MSG-20261016-085x", "bmc-w251-seat", "第 71 枚", "第七十一枚", "第 249 枚", "第 241 波",
    "engine_owner 行 240", "owner rows 240", "bmc rows 70", "bmc_rows=70", "engine_owner==bm-c 70",
    "248 行", "二百四十八", "r1046 窗算法", "（bm-c r1046 席", "（r1046 席位窗实跑",
    "bm-c r1046 窗 08:4x", "bm-c 循环班 r1047", "live-read r1047", "09:0x",
    "波号 251", "--wave 251", "R252：W251",
    "verify at W252 prereg", "W252 freezer 承接面", "W252p_", "W252 冻结方", "W252+ 投影",
    "键 W250 实测 K-lift", "line_pre_w249", "键 W251 实测 K-lift **0.0000**",
    "（**B 面=CLEAN", "waits-upstream ARMED",
    "（bm-c r1043 席", "第 70 枚", "engine_owner 行 239",
    "·W250 冻结窗 RAM 未记录（r1042",
    "W239..W250 leg（12 行）构成 W251 块 parity 109 行",
    "selftest W251 face",
]
for s in MUST_NOT:
    assert s not in T2, "MUST-NOT-HAVE present: %r (count=%d)" % (s, T2.count(s))

# projection-fulfillment count gates
assert T2.count("W252+ 投影") == 0, "W252+ 投影 count=%d (expect 0)" % T2.count("W252+ 投影")
assert T2.count("W253+ 投影") == 4, "W253+ 投影 count=%d (expect 4 = b1 tail + b5 title + b7 claim + sec8 rolled)" % T2.count("W253+ 投影")
assert T2.count("hops=1") == 2, "hops=1 count=%d (expect 2 = 带位 A + §3 A)" % T2.count("hops=1")

# residue scan: all X_Y..X_Y windows well-formed
import re
for m in re.finditer(r"(\d{3}_\d{3})\.\.(\d{3}_\d{3})", T2):
    lo = int(m.group(1).replace("_", "")); hi = int(m.group(2).replace("_", ""))
    assert lo <= hi, "malformed window %s" % m.group(0)

io.open(OUT, "w", encoding="utf-8", newline="").write(T2)
print("W252 PREREG DERIVE OK -> %s (%d bytes, %d lines)" % (OUT, len(T2.encode("utf-8")), T2.count("\n") + 1))
print("freeze window face: bm-c 循环班 r1049 freeze 窗 2026-10-16 %s" % FREEZE_T)
print("blocks replaced: %s" % ", ".join(n for n, _, _ in BLOCKS))
print("vmap legs: %d floors: %d post-legs: %d MUST: %d MUST_NOT: %d" % (len(VMAP), len(VMAP_FLOORS), len(VMAP_POST_LEGS), len(MUST), len(MUST_NOT)))
print("src blob-verified == 60d2b4e9359d68ceb694cc63a343a226bd7662f2 @ 9f5f106d6")
