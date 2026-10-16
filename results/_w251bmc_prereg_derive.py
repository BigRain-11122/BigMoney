# -*- coding: utf-8 -*-
# r1047 bm-c: W251 prereg derive (count-asserted ordered transform + marker-extracted block replaces).
# Source = committed frozen W250 prereg (git 4f7a130ff:research/PERPETUAL_N1_W250_PREREG.md, 34465 bytes
# -- the frozen pre-run face; sec7/8 placeholders intact). This window extracted the frozen face to
# results/_w251bmc_w250_frozen_face.txt and byte-verified == git blob 910aa89c15f4363af5216b9146ba7d0c91820b3d.
# W251 facts (all machine-derived, never transcribed):
#   - seat probe ADMIT receipt results/_w251bmc_20261016_probe_receipt.json
#     (A 567_501..569_500 CLEAN hops=0 fourteenth consecutive seed-gap A-continuation /
#      B 569_501..569_700 = 13-hop walk: naive 545_301..545_500 REFUSED at start [SEED_REGISTRY seed
#      545_500 + W240..W249 A-ladder + W250-A + own-A reservation], B lands ABOVE own-A first time
#      since the W239 staircase era; B base == own-A window tail 569_500+1 EXACT;
#      seed_admit FREE x2 [A base=567501 span=2000 / B base=569501 span=200];
#      seat published bc3b2b693, MSG-20261016-085x-bmc-w251-seat;
#      leg0 rows=248 w250_splice_landed=true w250_finalize_landed=true owner_rows=240 bmc_rows=70
#      ordinal=241 bmc_ordinal=71)
#   - upstream W250 finalize landed (bm-c r1046 continuation, ledger 972,135+2,200=974,335 EXACT):
#     merged K=547,920 / merged mu -0.09276995893561103 / sigma 0.24503505666354172 / se_mu 0.000331 /
#     W250-only mu -0.09225881818181819 / key1 gap 0.000511 in-band / A p95 0.3235 /
#     K-lift 0.0000 in-band / line_pre_w250 1.1939 / line_merged@547,920 1.1939 / n_eff_held 972,135
#     (results/perpetual_faces/n1_w250_results.json + results/_r1046bmc_w250_fivekeys.json)
#   - W250 chain: prereg derive r1045 freeze LANDED 4f7a130ff + five-face freeze splice r1046 dead-window
#     estate 08:02-08:04 LANDED 29930f489 (incl disclosed post-splice heal print-face rows 68->69, E63
#     family; dual-sha16 pf 40b0befe37ebbe2c / n1 22a957f851fd3adc post-heal landed blob; E70 gate-1
#     re-anchor face) + engine self-burn 12/12 (ledger appends 486458150+77a4f529a batched 6+6)
#     + r1046 continuation finalize one-pass 08:4x (sixgate PRE-FINALIZE ALL PASS, fivekeys ALL PASS,
#     sec.7/8 backfilled)
#   - W252+ projection (probe leg4, pre-W251 universe): A naive 569_501..571_500 first-clean hops=0
#     (no live refusers) / B naive 569_701..569_900 first-clean hops=0 BUT lands INSIDE the naive W252
#     A window 569_501..571_500 -> staircase re-emergence face for the W252 freezer, live re-derive governs
# Disclosed same-window needle heal (1): frozen template sec.8 placeholder carried the lagging projection
# label "sec.5.5 <prior-wave>+ projection inheritance machine evidence" (r1045-era cosmetic lag); rolled
# form fixed to the current-wave face W252+ via POST_LEG (disclosed here, no gate impact).
import io, os, sys, datetime

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(REPO, "results", "_w251bmc_w250_frozen_face.txt")
OUT = os.path.join(REPO, "research", "PERPETUAL_N1_W251_PREREG.md")

T0 = io.open(SRC, encoding="utf-8", newline="").read()

P1, P2, P3 = "\x01W\x01", "\x01N\x01", "\x01B\x01"

now = datetime.datetime.now()
FREEZE_T = "%02d:%dx" % (now.hour, now.minute // 10)

VMAP = [
    # projection first, then line_merged face, then prior-K bare, then ledger heads (order-critical)
    ("547,920 投影", "550,120 投影"),
    ("line_merged@K545,720 **1.1938**", "line_merged@K547,920 **1.1939**"),
    ("545,720", "547,920"),
    ("972,135", "974,335"),
    ("969,935", "972,135"),
    # sec5 measured keys -> W250 measured faces (fivekeys machine values)
    ("−0.09277202", "−0.09276996"),
    ("−0.08793", "−0.09226"),
    ("0.2450284", "0.2450351"),
    ("实差 0.0048 在带内", "实差 0.0005 在带内"),
    ("（**0.3158** 实测锚）", "（**0.3235** 实测锚）"),
    # band values (A chained: hi 567_500 -> 569_500 first, base 565_501 -> 567_501, prior tail 565_500 -> 567_500)
    ("567_500", "569_500"),
    ("565_501", "567_501"),
    ("565_500", "567_500"),
    # B faces: W251 B = 13-hop walk landing (NOT arithmetic continuation) -> targeted legs only,
    # remaining template B-value occurrences live inside block-replaced regions
    ("B-ext exit seed=545_101..545_300", "B-ext exit seed=569_501..569_700"),
    ("A base=565501 span=2000 checked=2000 verdict=FREE", "A base=567501 span=2000 checked=2000 verdict=FREE"),
    ("B base=545101 span=200 checked=200 verdict=FREE", "B base=569501 span=200 checked=200 verdict=FREE"),
    ("exit rng=**545_101+j**", "exit rng=**569_501+j**"),
    # R-face (pre-roll safe: new W251 token is not re-rolled)
    ("R251：W250", "R252：W251"),
    # wave-number roll (chained placeholders)
    ("W250", P1), ("W249", "W250"), (P1, "W251"),
    # result-file names (chained)
    ("n1_w250", P2), ("n1_w249", "n1_w250"), (P2, "n1_w251"),
    # probe/freeze script basenames (chained; current face _w251bmc <- template _w250bmc)
    ("_w250bmc", P3), ("_w249bmc", "_w250bmc"), (P3, "_w251bmc"),
    # runner CLI wave
    ("--wave 250", "--wave 251"),
    ("波号 250", "波号 251"),
    # seed-gap ordinal (probe A_semantics: fourteenth consecutive)
    ("连续第十三个 seed-gap face", "连续第十四个 seed-gap face"),
    # ordinals
    ("第 248 枚", "第 249 枚"),
    ("第 240 波", "第 241 波"),
    ("bm-c 第七十枚自有波", "bm-c 第七十一枚自有波"),
    # subsumption-order fix (r1040 law): compound needle contains 第 70 枚 -> MUST run before the bare roll
    ("bmc rows 69+候选=第 70 枚 EXACT", "bmc rows 70+候选=第 71 枚 EXACT"),
    ("第 70 枚", "第 71 枚"),
    ("probe leg0 bmc_rows=69 attempt-continuity face（r1043 窗算法·bm-c own seat+bmc live rows 69 实读）",
     "probe leg0 bmc_rows=70 attempt-continuity face（r1046 窗算法·bm-c own seat+bmc live rows 70 实读）"),
    ("engine_owner==bm-c 69 行注册", "engine_owner==bm-c 70 行注册"),
    ("engine_owner 行 239 注册在册", "engine_owner 行 240 注册在册"),
    # registry scan face
    ("全二百四十七行注册 N1 带表", "全二百四十八行注册 N1 带表"),
    ("freeze 窗 live derive 247 行单态 owner rows 239", "freeze 窗 live derive 248 行单态 owner rows 240"),
    ("共二百四十七面实测", "共二百四十八面实测"),
    ("perpetual_faces.py 零 248 行", "perpetual_faces.py 零 249 行"),
    # seat / provenance faces
    ("MSG-20261016-055x-bmc-w250-seat", "MSG-20261016-085x-bmc-w251-seat"),
    ("cc06f1f4a", "bc3b2b693"),
    ("（bm-c r1043 席·queue-head FREEZE-UNBLOCKED 发布）", "（bm-c r1046 席·queue-head FREEZE-UNBLOCKED 发布）"),
    ("（bm-c r1043 席位", "（bm-c r1046 席位"),
    ("（r1043 席位窗实跑", "（r1046 席位窗实跑"),
    # finalize window faces (specific first, then catch-all)
    ("bm-c r1043 窗 05:5x", "bm-c r1046 窗 08:4x"),
    ("05:5x", "08:4x"),
    # freeze window + engine live-read + RAM head (bm-c current window honest: 6.7G free of 23.9G,
    # W20 SCREEN 4/4 closed, engine queue idle, CPU lane independent)
    ("bm-c 循环班 r1045 freeze 窗 2026-10-16 07:2x", "bm-c 循环班 r1047 freeze 窗 2026-10-16 " + FREEZE_T),
    ("saturation_engine.py status live-read r1045", "saturation_engine.py status live-read r1047"),
    ("本窗 free RAM ~3.3GB（bm-c 底盘常驻·24G 物理内存机·W20 SCREEN 四分片全闭环+引擎队列空转·CPU 车道独立如实注记）",
     "本窗 free RAM ~6.7GB（bm-c 底盘常驻·24G 物理内存机·W20 SCREEN 四分片全闭环+引擎队列空转·CPU 车道独立如实注记）"),
]

VMAP_FLOORS = {
    "547,920 投影": 1, "line_merged@K545,720 **1.1938**": 1,
    "545,720": 7, "972,135": 3, "969,935": 2,
    "−0.09277202": 1, "−0.08793": 1, "0.2450284": 1, "实差 0.0048 在带内": 1,
    "（**0.3158** 实测锚）": 1,
    "567_500": 8, "565_501": 13, "565_500": 4,
    "B-ext exit seed=545_101..545_300": 1,
    "A base=565501 span=2000 checked=2000 verdict=FREE": 1,
    "B base=545101 span=200 checked=200 verdict=FREE": 1,
    "exit rng=**545_101+j**": 1,
    "R251：W250": 1,
    "W250": 26, "W249": 66,
    "n1_w250": 4, "n1_w249": 3, "_w250bmc": 4, "_w249bmc": 1,
    "--wave 250": 2, "波号 250": 1,
    "连续第十三个 seed-gap face": 2,
    "第 248 枚": 1, "第 240 波": 1, "bm-c 第七十枚自有波": 1, "第 70 枚": 2,
    "bmc rows 69+候选=第 70 枚 EXACT": 2,
    "probe leg0 bmc_rows=69 attempt-continuity face（r1043 窗算法·bm-c own seat+bmc live rows 69 实读）": 1,
    "engine_owner==bm-c 69 行注册": 1, "engine_owner 行 239 注册在册": 1,
    "全二百四十七行注册 N1 带表": 1,
    "freeze 窗 live derive 247 行单态 owner rows 239": 1,
    "共二百四十七面实测": 1, "perpetual_faces.py 零 248 行": 1,
    "本候选=bm-c 自有席自有波": 1,
    "MSG-20261016-055x-bmc-w250-seat": 4, "cc06f1f4a": 3,
    "（bm-c r1043 席·queue-head FREEZE-UNBLOCKED 发布）": 1,
    "（bm-c r1043 席位": 1, "（r1043 席位窗实跑": 1,
    "bm-c r1043 窗 05:5x": 1, "05:5x": 3, "已落账键·05:5x": 1,
    "bm-c 循环班 r1045 freeze 窗 2026-10-16 07:2x": 1,
    "saturation_engine.py status live-read r1045": 1,
    "本窗 free RAM ~3.3GB（bm-c 底盘常驻·24G 物理内存机·W20 SCREEN 四分片全闭环+引擎队列空转·CPU 车道独立如实注记）": 1,
    "键 W249 实测 K-lift **0.0000**": 1, "line_pre_w249 1.1938": 1,
    "→W246 **0.000334**→W247 **0.000333**→W248 **0.000332**→W249 **0.000332**】": 1,
    "§5.5 W250+ 投影承接机证": 1,
    "bm-c r1043 W249 §7 范式": 1, "bm-c r1043 W249 §8 范式": 1,
    "r1041/W249 先例 freeze-prep 同式": 1,
    "W243/W246/W248/W249 低 RAM 实烧先例": 1,
    "probe leg0 机证 247 行": 1, "席位窗 probe leg0 实测 247 行": 1,
    "（**B 面=CLEAN·hops=0 算术续带承袭形态**": 1,
    "（法典 §4 W250 行 B=545_101..545_300·**CLEAN·hops=0 算术续带承袭形态**": 1,
    "5. **W251+ 投影（probe 机证 leg4": 1,
    "verify at W251 prereg，hop 链逐跳在 probe 回执。": 1,
    "never transcribe r587**）": 1,
    "selftest W250 face（A=first-clean A-continuation past prior-wave A tail+live-seeds 恒等·B=clean arithmetic continuation past prior-wave B tail+own-A 同窗互斥断言·W249 行 parity 腿": 1,
    "零假设零风险。": 1, "W240 冻结窗 33.2G bm-a 实锚）": 1,
    "+W246=bm-a r1016 prereg derive": 1, "W251 freezer 承接面）】。": 1,
    "已如实披露非分叉）": 1, "兑现收敛·ADMIT 回执在场）": 1,
    "·W249 冻结窗 RAM 未记录（r1042 死窗 estate 收口·省锚如实注记）": 1,
    "waits-upstream ARMED": 0,
}

# floors for POST-chain correction legs (needles exist only in T1 after the pre-chain legs run)
VMAP_POST_LEGS = [
    # probe leg0 registry faces: W250 splice landed BEFORE the seat window (zero +1 owed)
    ("probe leg0 机证 247 行〔", "probe leg0 机证 248 行〔", 1),
    ("席位窗 probe leg0 实测 247 行〔", "席位窗 probe leg0 实测 248 行〔", 1),
    # se_mu narrowing chain: relabel rolled W249 tail (rolled to W250) back and append true W250 se 0.000331
    ("→W248 **0.000332**→W250 **0.000332**】",
     "→W248 **0.000332**→W249 **0.000332**→W250 **0.000331**】", 1),
    # line_pre face: lowercase w-token escapes the uppercase W-roll (r1045 derive precedent);
    # W250 actual line_pre_w250 = 1.1939 (fivekeys skill_line)
    ("line_pre_w249 1.1938", "line_pre_w250 1.1939", 1),
    # sec7/8 backfill paradigm rows (W250 sec.7/8 backfilled by r1046)
    ("bm-c r1043 W250 §7 范式", "bm-c r1046 W250 §7 范式", 1),
    ("bm-c r1043 W250 §8 范式", "bm-c r1046 W250 §8 范式", 1),
    # low-RAM precedent list: rolled T1 form lost the W249 label (rolled to W250); restore it and
    # append W250 (engine self-burn 12/12 r1046 window on this 6.7G-free machine)
    ("W243/W246/W248/W250 低 RAM 实烧先例", "W243/W246/W248/W249/W250 低 RAM 实烧先例", 1),
    # freeze-prep precedent face (W250 prereg derive window = r1045)
    ("r1041/W250 先例 freeze-prep 同式", "r1045/W250 先例 freeze-prep 同式", 1),
    # sec.8 placeholder projection-label heal (disclosed): lagging rolled label -> current-wave W252+ face
    ("§5.5 W251+ 投影承接机证", "§5.5 W252+ 投影承接机证", 1),
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

NEW["b1_chain_tail"] = (
    "+W246=bm-a r1016 prereg derive（machine-SUB from frozen W245 tpl 6473fb7f8）"
    "+五面冻结 splice（r1017 650953086 pushed·editor gen a2-closer 修复×2 收口）"
    "+引擎自燃 12/12（15:44 done claim-exempt engine lane）"
    "+bm-a r1018 finalize one-pass 已落（K=539,120·账本头 965,535 机读·n1_w246_results.json·16:0x·fivekeys 6/6 ALL PASS）"
    "+W247=bm-a r1019 prereg derive（machine-SUB from frozen W246 tpl fbfb7b43f @ commit 4a001a96d）"
    "+五面冻结 splice（r1021 2fcca7711 pushed·splice editor compiled+run clean after gen repair x3）"
    "+引擎自燃 12/12（18:40-18:51 auto-ignite claim-exempt engine lane）"
    "+bm-a r1022 finalize one-pass 已落（K=541,320·账本头 967,735 机读·n1_w247_results.json·19:0x·fivekeys ALL PASS·sixgate PRE-FINALIZE 18:5x 正相）"
    "+W248=bm-c r1035 prereg derive（machine-SUB from frozen W247 tpl @ commit 4c403cb16）"
    "+五面冻结 splice（r1036 absorb 收口 21:36 死窗 estate·六门 splice-integrity ALL PASS·dual-sha16 pf fd8b95810b45c48c / n1 72e95889017708ba）"
    "+引擎自燃 12/12（21:36-21:44 auto-ignite claim-exempt engine lane）"
    "+bm-c r1036 finalize one-pass 已落（K=543,520·账本头 969,935 机读·n1_w248_results.json·22:1x·fivekeys ALL PASS·sixgate PRE-FINALIZE 正相·absorb 窗 estate 收口）"
    "+W249=bm-c r1041 prereg derive（machine-SUB from frozen W248 tpl b9abac706·absorb dead r1040 estate authored 04:04:22·freeze LANDED 4103f0d5d）"
    "+五面冻结 splice（r1042 5d4aeec59 pushed·dead-window estate·E63 heal 2nd instance same-window·dual-sha16 pf 487b9fb3d98aa09e / n1 ee694186ffc6ee97·W249 block parity 107 rows）"
    "+引擎自燃 12/12（r1042 窗 auto-ignite claim-exempt engine lane·ledger appends self-committed）"
    "+bm-c r1043 finalize one-pass 已落（K=545,720·账本头 972,135 机读·n1_w249_results.json·05:5x·fivekeys ALL PASS·sixgate PRE-FINALIZE first correct-phase·absorb 37th-gen 窗 estate 收口）"
    "+W250=bm-c r1045 prereg derive（machine-SUB from frozen W249 tpl 4103f0d5d·freeze LANDED 4f7a130ff·banned_direction_gate rc0·三 needle heals 披露：date-roll/line_pre POST_LEG/owner-face E63）"
    "+五面冻结 splice（r1046 死窗 estate 08:02-08:04 LANDED 29930f489〔含 disclosed post-splice heal print-face rows 68→69·E63 家族〕·dual-sha16 pf 40b0befe37ebbe2c / n1 22a957f851fd3adc〔post-heal landed blob·E70 gate-1 re-anchor 面〕·W250 块 parity 108 rows）"
    "+引擎自燃 12/12（mtime-watch auto-ignite claim-exempt engine lane·ledger appends 486458150+77a4f529a batched 6+6 self-committed）"
    "+bm-c r1046 finalize one-pass 已落（K=547,920·账本头 974,335 机读·n1_w250_results.json·08:4x·fivekeys ALL PASS·sixgate PRE-FINALIZE 正相〔gate-1 re-anchored to landed blob·E70〕）"
    "——本波上游链=W1..W250 finalize 全落地·零在飞上游席·干净前置**；"
    "席位公示=MSG-20261016-085x-bmc-w251-seat 已推 origin bc3b2b693 先于本冻结"
    "【r565 律·席位先行·bm-c r1046 窗发布·queue-head FREEZE-UNBLOCKED 承接·W250 own-wave finalize 已落=席位时即解锁】；"
    "下游 W252+ 投影见 §5.5（probe 机证 leg4·W252 freezer 承接面）】。"
)

NEW["b2_band_face"] = (
    "（**B 面=13-HOP WALK·落位高于本波 A 窗形态（W239 staircase era 后首次 above-own-A 落位）**："
    "B naive 续带 545_301..545_500（自注册 W250 B 尾 545_300 续）"
    "在席位窗宇宙（post-W250-REGISTERED 终态注册·freeze-UNBLOCKED）起点即 REFUSED"
    "（SEED_REGISTRY seed 545_500 命中+W240..W249 A-ladder 拒面=W250 席位 leg4 投影兑现·probe leg1 B_semantics 机证·B_naive_refused_at_start=true）"
    "——pre-W250 投影 first-clean 565_501..565_700 现已落入注册 W250 A 带 565_501..567_500 内→post-W250 walk 越之（W250-A 跳）"
    "+**own-A reservation standard leg 越本波 A 窗 567_501..569_500**（seed 首 hop+W240..W249 A-ladder 10 跳+W250-A 跳+own-A 第 13 跳）"
    "→**13 hops** 落位 **569_501..569_700**·**B 落位 base==本波 A 窗尾+1（569_500+1）EXACT 机检关系**"
    "（B_hop lands-inside-A=false·B_lands_above_own_A=true·B_base_above_W250_tail=true·B_hop_chain 13 跳逐跳 verbatim 在 probe 回执 leg1 机证·非转录 r587·AB 同窗互斥面 leg2 律在场）；"
    "**W250 席位 leg4 投影承接面注记兑现**：投影预言 W251 naive B 拒于 545_301..545_500 且 post-W250 walk 上移越过 W250 A 带"
    "——本窗 live re-derive 如实兑现·落位高于 pre-W250 投影（post-W250 宇宙新拒面·W250 prereg §5.5 已披露 live re-derive governs·above-own-A 新形态如实注记）·已如实披露非分叉）"
)

NEW["b3_bandface_s3"] = (
    "（法典 §4 W251 行 B=569_501..569_700·**13-HOP WALK·落位高于本波 A 窗形态**："
    "B naive 续带 545_301..545_500（自注册 W250 B 尾 545_300 续）"
    "在席位窗宇宙（post-W250-REGISTERED 终态注册）起点即 REFUSED"
    "（SEED_REGISTRY seed 545_500 命中+W240..W249 A-ladder=W250 席位 leg4 投影兑现·probe leg1 B_semantics 机证）"
    "——pre-W250 投影窗 565_501..565_700 已被注册 W250 A 带覆盖→walk 越之+own-A reservation 越本波 A 窗 567_501..569_500"
    "→13 hops 落位 569_501..569_700·**B 落位 base==本波 A 窗尾+1（569_500+1）机检关系**"
    "（B_hop lands-inside-A=false·B_lands_above_own_A=true·B_base_above_W250_tail=true·B_hop_chain 13 跳 verbatim 在 probe 回执）"
    "·非转录 r587·与 W250 席位 leg4 投影承接面注记兑现收敛·ADMIT 回执在场）"
)

NEW["b5_projection"] = (
    "5. **W252+ 投影（probe 机证 leg4·下波冻结方复核非转抄 r587 律）**：A naive first-clean 569_501..571_500 **CLEAN**（hops=0·pre-W251 宇宙零 live refusers）；"
    "B naive **569_701..569_900 CLEAN（hops=0）但落投影 A 窗 569_501..571_500 内**（W252p_B_lands_inside_W252p_A_naive=true——"
    "**staircase re-emergence face**：W251 B 569_501..569_700 注册后 W251 B 带首次落入 W251 A 2,000-span ladder 区间·"
    "W252 B derive with own-A reservation 将 hop past 571_500→~571_501..571_700 staircase 面重临——post-W251 宇宙 live re-derive 必变·禁转录投影）；"
    "**W252 冻结方禁假设 staircase A-base==prior-B-tail+1 恒等·须重读 live trace**"
    "（seed-gap face 承袭 W239..W250·W251 起 B 入 A-ladder 区=above-own-A 新形态如实注记）"
    "——W252 冻结方必须在 post-W251 注册宇宙重 derive 且 derive B 时预留本波 A 窗 567_501..569_500+本波 B 带 569_501..569_700"
    "——leg2 律/E36 卡·W141 先例；verify at W252 prereg，hop 链逐跳在 probe 回执。"
)

NEW["b6_ram"] = (
    "·W250 冻结窗 RAM 未记录（r1046 死窗 estate 收口·省锚如实注记）"
    "·W249 冻结窗 RAM 未记录（r1042 死窗 estate 收口·省锚如实注记）"
    "·W248 冻结窗 RAM 未记录（r1036 死窗 estate 收口·省锚如实注记）"
    "·W247 冻结窗 60.8G bm-a 实锚·W246 冻结窗 RAM 未记录（r1017 死窗 estate 收口·省锚如实注记）"
    "·W245 冻结窗 RAM 未记录（r1015 estate-absorb 窗·省锚如实注记）"
    "·W244 冻结窗 41.9G bm-a 实锚·W243 冻结窗 64.0G bm-a 实锚·W242 冻结窗 17.6G bm-a 实锚"
    "·W241 冻结窗 1.8G bm-c 实锚·W240 冻结窗 33.2G bm-a 实锚）"
)

NEW["b7_claim_projection"] = (
    "·probe W252+ 投影 A naive 569_501..571_500 CLEAN hops=0（零 live refusers）/ B naive 569_701..569_900 CLEAN hops=0 **但落 naive W252 A 窗内**"
    "→own-A reservation 下 ~571_501..571_700 **staircase re-emergence face live re-derive governs 预披露**"
    "（投影 A naive 569_501..571_500 CLEAN·hops=0；投影 B naive 569_701..569_900 clean 但落 naive W252 A 窗 569_501..571_500 内——"
    "**above-own-A 承袭 face：W251 B 569_501..569_700 落本波 A 窗之上〔W239 staircase era 后首次〕·"
    "W252 冻结方禁假设 staircase A-base==prior-B-tail+1 恒等·须重读 live trace·W251 B 带将拒 naive W252 A 窗仅当重叠"
    "——**W252 freezer 承接面强制注记：须在 post-W251 宇宙重 derive 且 derive B 时预留本波 A 窗·W141 先例·never transcribe r587**）"
)

NEW["b8_selftest"] = (
    "selftest W251 face（A=first-clean A-continuation past prior-wave A tail+live-seeds 恒等"
    "·B=13-hop honest-walk lands-above-own-A 断言（B_hop_chain 与 probe 回执逐跳恒等·B 落位不落本波 A 窗内=同窗互斥断言）·W250 行 parity 腿"
    "**estate 提取面注记**：冻结拼接脚本的 parity estate（W138..W206 69 行 full-span·r858 absorb 代）从**本机 W250 块物理字节**提取"
    "（结构已知·提取自证断言 69 行 range 恒等在场）——W250 块的自有 W239..W249 legs（11 行）不入 estate 路径·提取后新增 W239..W250 leg（12 行）构成 W251 块 parity 109 行"
    "（W138..W206+W211+W212+W213+W214+W215+W216+W217+W218+W219+W220+W221+W222+W223+W224+W225+W226+W227+W228+W229"
    "+W230+W231+W232+W233+W234+W235+W236+W237+W238+W239+W240+W241+W242+W243+W244+W245+W246+W247+W248+W249+W250）·零假设零风险。"
)

# marker pairs: (block, start_marker, end_marker) -- needles extracted from T1 at runtime (zero transcription)
BLOCKS = [
    ("b1_chain_tail", "+W246=bm-a r1016 prereg derive", "W251 freezer 承接面）】。"),
    ("b2_band_face", "（**B 面=CLEAN·hops=0 算术续带承袭形态**", "已如实披露非分叉）"),
    ("b3_bandface_s3", "（法典 §4 W251 行 B=545_101..545_300·**CLEAN·hops=0 算术续带承袭形态**", "兑现收敛·ADMIT 回执在场）"),
    ("b5_projection", "5. **W251+ 投影（probe 机证 leg4", "verify at W251 prereg，hop 链逐跳在 probe 回执。"),
    ("b6_ram", "·W250 冻结窗 RAM 未记录（r1042 死窗 estate 收口·省锚如实注记）", "W240 冻结窗 33.2G bm-a 实锚）"),
    ("b7_claim_projection", "·probe W251+ 投影 A 567_501..569_500 CLEAN hops=0 / B naive 545_301..545_500 REFUSED", "never transcribe r587**）"),
    ("b8_selftest", "selftest W251 face（A=first-clean A-continuation past prior-wave A tail+live-seeds 恒等·B=clean arithmetic continuation past prior-wave B tail+own-A 同窗互斥断言·W250 行 parity 腿", "零假设零风险。"),
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
    "PERPETUAL-N1-W251", "research/PERPETUAL_N1_W251_PREREG.md",
    "567_501..569_500", "569_501..569_700", "974,335", "547,920", "550,120",
    "n1_w251_results.json", "MSG-20261016-085x-bmc-w251-seat", "bc3b2b693",
    "第 71 枚", "第七十一枚", "第 249 枚", "CLEAN·hops=0",
    "连续第十四个 seed-gap face", "569_501..571_500", "569_701..569_900",
    "_w251bmc_20261016", "--wave 251", "波号 251",
    "W250=bm-c r1045 prereg derive", "r1046 finalize one-pass",
    "n_eff_held_equal 972,135", "−0.09276996", "0.2450351", "−0.09226",
    "（**0.3235** 实测锚）", "bm-c 循环班 r1047 freeze 窗", "本窗 free RAM ~6.7GB",
    "→W246 **0.000334**→W247 **0.000333**→W248 **0.000332**→W249 **0.000332**→W250 **0.000331**】", "queue-head FREEZE-UNBLOCKED lane",
    "第 241 波", "seed_admit_gate rc0 双带 FREE", "A base=567501", "B base=569501",
    "bm-c r1046 W250 §7 范式", "bm-c r1046 W250 §8 范式",
    "W252 freezer 承接面", "verify at W252 prereg",
    "selftest W251 face", "W239..W250 leg（12 行）构成 W251 块 parity 109 行",
    "W250 实测 K-lift **0.0000**", "line_merged@K547,920 **1.1939**", "line_pre_w250 1.1939",
    "实差 0.0005 在带内", "已落账键·08:4x", "bm-c r1046 窗 08:4x",
    "r1045/W250 先例 freeze-prep 同式", "248 行单态", "probe leg0 机证 248 行",
    "_w251bmc_freeze_edits", "_w250bmc_freeze_edits", "本波上游链=W1..W250 finalize 全落地",
    "engine_owner==bm-c 70 行注册", "bmc rows 70", "bmc_rows=70",
    "queue-head FREEZE-UNBLOCKED 承接", "A base==前波 A 尾+1（567_500+1）",
    "B 落位 base==本波 A 窗尾+1（569_500+1）",
    "W250 块的自有 W239..W249 legs（11 行）",
    "bm-c r1046 席位", "queue-head FREEZE-UNBLOCKED 发布",
    "post-W250-REGISTERED 终态注册", "席位窗 probe leg0 实测 248 行",
    "W243/W246/W248/W249/W250 低 RAM 实烧先例", "·W250 冻结窗 RAM 未记录（r1046 死窗",
    "本候选=bm-c 自有席自有波", "R252：W251 带从未指派",
    "13 hops", "B_hop lands-inside-A=false", "B_lands_above_own_A=true",
    "W239 staircase era 后首次", "staircase re-emergence face",
    "§5.5 W252+ 投影承接机证", "exit rng=**569_501+j**", "B-ext exit seed=569_501..569_700",
    "probe leg0 bmc_rows=70 attempt-continuity face（r1046 窗算法·bm-c own seat+bmc live rows 70 实读）",
    "545_301..545_500", "565_501..567_500",
]
for s in MUST:
    assert s in T2, "MUST-HAVE missing: %r" % s

MUST_NOT = [
    "**A-ext seed=565_501", "565_500", "545_101", "545_100",
    "−0.09277202", "0.2450284", "−0.08793", "**0.3158**", "cc06f1f4a",
    "MSG-20261016-055x", "第 70 枚", "第七十枚", "第 248 枚",
    "engine_owner 行 239", "owner rows 239", "bmc rows 69", "bmc_rows=69",
    "engine_owner==bm-c 69", "连续第十三个 seed-gap", "--wave 250", "波号 250",
    "实差 0.0048 在带内", "r1043 窗算法", "第 240 波",
    "waits-upstream ARMED", "verify at W251 prereg", "W251 freezer 承接面",
    "547,920 投影", "已落账键·05:5x",
    "本波上游链=W1..W249 finalize 全落地", "A base=565501", "B base=545101",
    "（bm-c r1043 席", "bm-c r1043 W250 §7 范式", "bm-c r1043 W250 §8 范式",
    "r1041/W250 先例", "probe leg0 机证 247 行", "W238..W249 leg（12 行）构成 W250 块 parity 108 行",
    "键 W249 实测 K-lift", "line_pre_w249",
    "freeze 窗 live derive 247 行", "零 248 行",
    "·W250 冻结窗 RAM 未记录（r1042",
    "本候选=bm-a", "R251：W250",
    "247 行", "二百四十七",
    "W243/W246/W248/W250 低 RAM",
    "→W250 **0.000332**】",
    "§5.5 W251+ 投影承接机证", "W251+ 投影",
    "B 带均低于走带起点", "B_no_ownA_jump=true",
]
for s in MUST_NOT:
    assert s not in T2, "MUST-NOT-HAVE present: %r (count=%d)" % (s, T2.count(s))

# projection-fulfillment count gates
assert T2.count("W251+ 投影") == 0, "W251+ 投影 count=%d (expect 0)" % T2.count("W251+ 投影")
# expect 4 = b1 tail + b5 title + b7 claim + sec8 placeholder (healed label, disclosed needle heal --
# r1045 output carried the lagging prior-wave label in sec.8; this window fixes it to the current face)
assert T2.count("W252+ 投影") == 4, "W252+ 投影 count=%d (expect 4 = b1 tail + b5 title + b7 claim + sec8 healed)" % T2.count("W252+ 投影")

# residue scan: all X_Y..X_Y windows well-formed
import re
for m in re.finditer(r"(\d{3}_\d{3})\.\.(\d{3}_\d{3})", T2):
    lo = int(m.group(1).replace("_", "")); hi = int(m.group(2).replace("_", ""))
    assert lo <= hi, "malformed window %s" % m.group(0)

io.open(OUT, "w", encoding="utf-8", newline="").write(T2)
print("W251 PREREG DERIVE OK -> %s (%d bytes, %d lines)" % (OUT, len(T2.encode("utf-8")), T2.count("\n") + 1))
print("freeze window face: bm-c 循环班 r1047 freeze 窗 2026-10-16 %s" % FREEZE_T)
print("blocks replaced: %s" % ", ".join(n for n, _, _ in BLOCKS))
print("vmap legs: %d floors: %d post-legs: %d MUST: %d MUST_NOT: %d" % (len(VMAP), len(VMAP_FLOORS), len(VMAP_POST_LEGS), len(MUST), len(MUST_NOT)))
