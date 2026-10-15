# -*- coding: utf-8 -*-
# r1045 bm-c: W250 prereg derive (count-asserted ordered transform + marker-extracted block replaces).
# Source = committed frozen W249 prereg (git 4103f0d5d:research/PERPETUAL_N1_W249_PREREG.md, 33637 bytes
# -- the frozen pre-run face; sec7/8 placeholders intact). Dead r1044 window pre-extracted the frozen
# face to results/_w250bmc_w249_frozen_face.txt and byte-verified == git blob this window (r1045).
# W250 facts (all machine-derived, never transcribed):
#   - seat probe ADMIT receipt results/_w250bmc_20261016_probe_receipt.json
#     (A 565_501..567_500 CLEAN hops=0 thirteenth consecutive seed-gap A-continuation /
#      B 545_101..545_300 CLEAN hops=0 past the W239 staircase landing,
#      B base == W249-registered B tail 545_100+1 EXACT; seed_admit FREE x2;
#      queue-head FREEZE-UNBLOCKED seat published cc06f1f4a, MSG-20261016-055x-bmc-w250-seat;
#      leg0 rows=247 w249_splice_landed=true w249_finalize_landed=true owner_rows=239 bmc_rows=69
#      ordinal=240 bmc_ordinal=70)
#   - upstream W249 finalize landed (bm-c r1043 absorb, commit cc06f1f4a): ledger 972,135 EXACT
#     (969,935+2,200) / K=545,720 (543,520+2,200) / merged mu -0.09277202 / sigma 0.2450284 /
#     se_mu 0.000332 / W249-only mu -0.08793 / key1 gap 0.00485 in-band / A p95 0.3158 /
#     K-lift 0.0000 in-band / line_pre_w249 1.1938 / line_merged@K545,720 1.1938 /
#     n_eff_held 969,935 (results/perpetual_faces/n1_w249_results.json + results/_r1043bmc_w249_fivekeys.json)
#   - W249 chain: prereg derive dead r1040 authored 04:04:22, landed r1041 4103f0d5d + five-face
#     freeze splice r1042 5d4aeec59 (E63 heal 2nd instance: owner face asserted bm-a vs live bm-c,
#     healed in live block) + engine self-burn 12/12 self-commits 2d0b41383/f528ab7ab/dfbb4afa2
#     + r1043 absorb finalize one-pass 05:52:59
#   - W251+ projection (probe leg4, pre-W250 universe): A naive 567_501..569_500 CLEAN hops=0 /
#     B naive 545_301..545_500 REFUSED (SEED_REGISTRY seed 545_500 + W240..W249 A-ladder)
#     -> first-clean 565_501..565_700 hops=11
# Owner-face heal (same-window disclosure): template carried stale "本候选=bm-a 自有席自有波"
# (E63 heal family, r1042 live-block heal precedent); W250 = bm-c own seat own wave -> fixed to bm-c.
import io, os, sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(REPO, "results", "_w250bmc_w249_frozen_face.txt")
OUT = os.path.join(REPO, "research", "PERPETUAL_N1_W250_PREREG.md")

T0 = io.open(SRC, encoding="utf-8", newline="").read()

P1, P2, P3 = "\x01W\x01", "\x01N\x01", "\x01B\x01"

VMAP = [
    # projection first, then prior-K bare, then ledger heads (order-critical)
    ("545,720 投影", "547,920 投影"),
    ("line_merged@K543,520 **1.1937**", "line_merged@K545,720 **1.1938**"),
    ("543,520", "545,720"),
    ("969,935", "972,135"),
    ("967,735", "969,935"),
    # sec5 measured keys -> W249 measured faces
    ("−0.09279163", "−0.09277202"),
    ("−0.09134", "−0.08793"),
    ("0.2450393", "0.2450284"),
    ("实差 0.0015 在带内", "实差 0.0048 在带内"),
    ("（**0.3154** 实测锚）", "（**0.3158** 实测锚）"),
    # band values (A chained: hi 565_500 -> 567_500, base 563_501 -> 565_501, prior tail 563_500 -> 565_500)
    ("565_500", "567_500"),
    ("563_501", "565_501"),
    ("563_500", "565_500"),
    # band values (B chained: hi 545_100 -> 545_300, base 544_901 -> 545_101, prior tail 544_900 -> 545_100)
    ("545_100", "545_300"),
    ("544_901", "545_101"),
    ("544_900", "545_100"),
    # seed_admit_gate bare-number forms
    ("A base=563501 span=2000 checked=2000 verdict=FREE", "A base=565501 span=2000 checked=2000 verdict=FREE"),
    ("B base=544901 span=200 checked=200 verdict=FREE", "B base=545101 span=200 checked=200 verdict=FREE"),
    # R-face (pre-roll safe: new W250 token is not re-rolled)
    ("R250：W249", "R251：W250"),
    # wave-number roll (chained placeholders)
    ("W249", P1), ("W248", "W249"), (P1, "W250"),
    # result-file names (chained)
    ("n1_w249", P2), ("n1_w248", "n1_w249"), (P2, "n1_w250"),
    # probe/freeze script basenames (chained; current face _w250bmc <- template _w249bmc)
    ("_w249bmc", P3), ("_w248bmc", "_w249bmc"), (P3, "_w250bmc"),
    # probe receipt date roll (W249 probe face dated 20261015 -> W250 probe face dated 20261016;
    # W248/W249 shared date 20261015 so the precedent chain had no date leg -- this window needs one)
    ("_20261015", "_20261016"),
    # runner CLI wave
    ("--wave 249", "--wave 250"),
    ("波号 249", "波号 250"),
    # seed-gap ordinal (probe A_semantics: thirteenth consecutive)
    ("连续第十二个 seed-gap face", "连续第十三个 seed-gap face"),
    # ordinals
    ("第 247 枚", "第 248 枚"),
    ("第 239 波", "第 240 波"),
    ("bm-c 第六十九枚自有波", "bm-c 第七十枚自有波"),
    # subsumption-order fix (r1040 law): compound needle contains 第 69 枚 -> MUST run before the bare roll
    ("bmc rows 68+候选=第 69 枚 EXACT", "bmc rows 69+候选=第 70 枚 EXACT"),
    ("第 69 枚", "第 70 枚"),
    ("probe leg0 bmc_rows=68 attempt-continuity face（r1037 窗算法·bm-c own seat+bmc live rows 68 实读）",
     "probe leg0 bmc_rows=69 attempt-continuity face（r1043 窗算法·bm-c own seat+bmc live rows 69 实读）"),
    ("engine_owner==bm-c 68 行注册", "engine_owner==bm-c 69 行注册"),
    ("engine_owner 行 238 注册在册", "engine_owner 行 239 注册在册"),
    # registry scan face
    ("全二百四十六行注册 N1 带表", "全二百四十七行注册 N1 带表"),
    ("freeze 窗 live derive 246 行单态 owner rows 238", "freeze 窗 live derive 247 行单态 owner rows 239"),
    ("共二百四十六面实测", "共二百四十七面实测"),
    ("perpetual_faces.py 零 247 行", "perpetual_faces.py 零 248 行"),
    # owner face heal (E63 family: template carried stale bm-a face; W250 = bm-c own wave)
    ("本候选=bm-a 自有席自有波", "本候选=bm-c 自有席自有波"),
    # seat / provenance faces
    ("MSG-20261015-225x-bmc-w249-seat", "MSG-20261016-055x-bmc-w250-seat"),
    ("8949e0aef", "cc06f1f4a"),
    ("（bm-c r1037 席·queue-head FREEZE-UNBLOCKED 发布）", "（bm-c r1043 席·queue-head FREEZE-UNBLOCKED 发布）"),
    ("（bm-c r1037 席位", "（bm-c r1043 席位"),
    ("（r1037 席位窗实跑", "（r1043 席位窗实跑"),
    # finalize window faces (specific first, then catch-all)
    ("bm-c r1036 窗 22:1x", "bm-c r1043 窗 05:5x"),
    ("22:1x", "05:5x"),
    # freeze window + engine live-read
    ("bm-c 循环班 r1037 freeze 窗 2026-10-16 02:1x", "bm-c 循环班 r1045 freeze 窗 2026-10-16 07:2x"),
    ("saturation_engine.py status live-read r1037", "saturation_engine.py status live-read r1045"),
    # RAM head face (bm-c current window honest: 3.3G free of 23.9G, W20 SCREEN 4/4 closed, engine idle)
    ("本窗 free RAM ~1.9GB（bm-c 底盘常驻·24G 物理内存机·MV V4 装配+星晴 T1 海审=bm-a 席在飞〔P0 交接 poke 22:54 已收·bm-c GPU 空窗〕+CPU 车道独立如实注记）",
     "本窗 free RAM ~3.3GB（bm-c 底盘常驻·24G 物理内存机·W20 SCREEN 四分片全闭环+引擎队列空转·CPU 车道独立如实注记）"),
]

VMAP_FLOORS = {
    "545,720 投影": 1, "line_merged@K543,520 **1.1937**": 1,
    "543,520": 7, "969,935": 3, "967,735": 2,
    "−0.09279163": 1, "−0.09134": 1, "0.2450393": 1, "实差 0.0015 在带内": 1,
    "（**0.3154** 实测锚）": 1,
    "565_500": 8, "563_501": 10, "563_500": 4,
    "545_100": 10, "544_901": 10, "544_900": 4,
    "A base=563501 span=2000 checked=2000 verdict=FREE": 1,
    "B base=544901 span=200 checked=200 verdict=FREE": 1,
    "R250：W249": 1,
    "W249": 26, "W248": 63,
    "n1_w249": 4, "n1_w248": 3, "_w249bmc": 4, "_w248bmc": 1, "_20261015": 3,
    "--wave 249": 2, "波号 249": 1,
    "连续第十二个 seed-gap face": 2,
    "第 247 枚": 1, "第 239 波": 1, "bm-c 第六十九枚自有波": 1, "第 69 枚": 2,
    "bmc rows 68+候选=第 69 枚 EXACT": 2,
    "probe leg0 bmc_rows=68 attempt-continuity face（r1037 窗算法·bm-c own seat+bmc live rows 68 实读）": 1,
    "engine_owner==bm-c 68 行注册": 1, "engine_owner 行 238 注册在册": 1,
    "全二百四十六行注册 N1 带表": 1,
    "freeze 窗 live derive 246 行单态 owner rows 238": 1,
    "共二百四十六面实测": 1, "perpetual_faces.py 零 247 行": 1,
    "本候选=bm-a 自有席自有波": 1,
    "MSG-20261015-225x-bmc-w249-seat": 4, "8949e0aef": 3,
    "（bm-c r1037 席·queue-head FREEZE-UNBLOCKED 发布）": 1,
    "（bm-c r1037 席位": 1, "（r1037 席位窗实跑": 1,
    "bm-c r1036 窗 22:1x": 1, "22:1x": 3, "已落账键·22:1x": 1,
    "bm-c 循环班 r1037 freeze 窗 2026-10-16 02:1x": 1,
    "saturation_engine.py status live-read r1037": 1,
    "本窗 free RAM ~1.9GB（bm-c 底盘常驻·24G 物理内存机·MV V4 装配+星晴 T1 海审=bm-a 席在飞〔P0 交接 poke 22:54 已收·bm-c GPU 空窗〕+CPU 车道独立如实注记）": 1,
}

# floors for POST-chain correction legs (needles exist only in T1 after the pre-chain legs run)
VMAP_POST_LEGS = [
    # probe leg0 registry faces: W249 splice landed BEFORE the seat window (zero +1 owed)
    ("probe leg0 机证 246 行〔W249 splice 先于席位窗已落地·零 +1 如实注记〕",
     "probe leg0 机证 247 行〔W249 splice 先于席位窗已落地·零 +1 如实注记〕", 1),
    ("席位窗 probe leg0 实测 246 行〔W249 splice 先于席位窗已落地·零 +1 如实注记〕",
     "席位窗 probe leg0 实测 247 行〔W249 splice 先于席位窗已落地·零 +1 如实注记〕", 1),
    # se_mu narrowing chain: relabel rolled W249 tail back to W248 and append true W249 se
    ("→W247 **0.000333**→W249 **0.000332**】", "→W247 **0.000333**→W248 **0.000332**→W249 **0.000332**】", 1),
    # K-lift face (source needle is the un-fixed rolled form; VMAP rolls wave tokens only)
    ("键 W249 实测 K-lift **−0.0001**", "键 W249 实测 K-lift **0.0000**", 1),
    # line_pre face: lowercase w-token escapes the uppercase W-roll (W249 derive precedent);
    # W249 actual line_pre_w249 = 1.1938 (value unchanged, label rolls)
    ("line_pre_w248 1.1938", "line_pre_w249 1.1938", 1),
    # sec7/8 backfill paradigm rows
    ("bm-c r1036 W249 §7 范式", "bm-c r1043 W249 §7 范式", 1),
    ("bm-c r1036 W249 §8 范式", "bm-c r1043 W249 §8 范式", 1),
    # low-RAM precedent list gains W249 (engine self-burn 12/12 r1042 window on this 3.3G-free machine)
    ("W243/W246/W249 低 RAM 实烧先例", "W243/W246/W248/W249 低 RAM 实烧先例", 1),
    # freeze-prep precedent face (W249 prereg derive window = r1041)
    ("r1035/W249 先例 freeze-prep 同式", "r1041/W249 先例 freeze-prep 同式", 1),
]

def xf(t):
    for o, n in VMAP:
        t = t.replace(o, n)
    return t

for o, f in VMAP_FLOORS.items():
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
    "——本波上游链=W1..W249 finalize 全落地·零在飞上游席·干净前置**；"
    "席位公示=MSG-20261016-055x-bmc-w250-seat 已推 origin cc06f1f4a 先于本冻结"
    "【r565 律·席位先行·bm-c r1043 窗发布·queue-head FREEZE-UNBLOCKED 承接·W249 own-wave finalize 已落=席位时即解锁】；"
    "下游 W251+ 投影见 §5.5（probe 机证 leg4·W251 freezer 承接面）】。"
)

NEW["b2_band_face"] = (
    "（**B 面=CLEAN·hops=0 算术续带承袭形态**：B 面 naive 续带 545_101..545_300（自注册 W249 B 尾 545_100 续）"
    "在席位窗宇宙（post-W249-REGISTERED 终态注册·freeze-UNBLOCKED）起点即 CLEAN 零活点拒"
    "（W249 席位 leg4 投影兑现·probe leg1 B_semantics 机证·W239 staircase band-hop landing 已过——注册 W239 A 带 542_501..544_500 "
    "与 W247/W248/W249 B 带均低于走带起点）"
    "且**不落本波 A 窗 565_501..567_500 内**（本波 A 高悬于 B 阶梯之上→**seed-decoupled A/B gap 承袭面**：同窗互斥面 leg2 律·W141 先例·B 无需 own-A reservation jump）"
    "→ B 保留 naive 落位 545_101..545_300·**hops=0**·**B base==前波 B 尾+1（545_100+1）EXACT 机检关系**"
    "（fc_b==fc_b_naive·B_hop_chain=[] 空集 leg1 机证·B_no_ownA_jump=true·B_semantics clean arithmetic continuation 回执在场·W249 splice 先于席位窗落地=freeze 窗 post-W249 宇宙重 derive 复核面在场）；"
    "**W249 席位 leg4 投影承接面注记兑现**：投影预言 W250 须在 post-W249 宇宙重 derive 且 A/B 双面 CLEAN hops=0 落位如投影所期"
    "——本窗如实兑现·A 零活点拒=投影所期·B 零活点拒=投影所期·已如实披露非分叉）"
)

NEW["b3_bandface_s3"] = (
    "（法典 §4 W250 行 B=545_101..545_300·**CLEAN·hops=0 算术续带承袭形态**：B naive 续带 545_101..545_300（自注册 W249 B 尾 545_100 续）"
    "在席位窗宇宙（post-W249-REGISTERED 终态注册）起点即 CLEAN 零活点拒（W249 席位 leg4 投影兑现·probe leg1 B_semantics 机证·W239 staircase landing 已过）"
    "且不落本波 A 窗 565_501..567_500 内（本波 A 高悬于 B 阶梯之上→同窗互斥面 leg2 律·W141 先例·B 无需 own-A reservation jump）"
    "→保留 naive 落位 545_101..545_300·hops=0·**B base==前波 B 尾+1（545_100+1）EXACT 机检关系**"
    "（fc_b==fc_b_naive·B_hop_chain=[] 空集 leg1 机证·B_no_ownA_jump=true·B_semantics clean arithmetic continuation 回执在场）"
    "·非转录 r587·与 W249 席位 leg4 投影承接面注记兑现收敛·ADMIT 回执在场）"
)

NEW["b5_projection"] = (
    "5. **W251+ 投影（probe 机证 leg4·下波冻结方复核非转抄 r587 律）**：A naive first-clean 567_501..569_500 **CLEAN**（hops=0·pre-W250 宇宙零活点拒）；"
    "B naive **545_301..545_500 REFUSED**（SEED_REGISTRY seed 545_500 命中+W240..W249 A-ladder 拒面→first-clean **565_501..565_700**·hops=11·"
    "**不落投影 A 窗内**——B_hop lands-inside-A=false 腿在场）；"
    "**W250 B 带 545_101..545_300 注册后将拒 naive W251 A 窗仅当重叠**"
    "（**seed-gap 承袭 face：W250 A/B 仍 decoupled〔A 565_501..567_500 高悬于 B 545_101..545_300 之上〕·W251 冻结方禁假设 staircase A-base==prior-B-tail+1 恒等·须重读 live trace**）"
    "——W251 冻结方必须在 post-W250 注册宇宙重 derive 且 derive B 时预留本波 A 窗——leg2 律/E36 卡·W141 先例；verify at W251 prereg，hop 链逐跳在 probe 回执。"
)

NEW["b6_ram"] = (
    "·W249 冻结窗 RAM 未记录（r1042 死窗 estate 收口·省锚如实注记）"
    "·W248 冻结窗 RAM 未记录（r1036 死窗 estate 收口·省锚如实注记）"
    "·W247 冻结窗 60.8G bm-a 实锚·W246 冻结窗 RAM 未记录（r1017 死窗 estate 收口·省锚如实注记）"
    "·W245 冻结窗 RAM 未记录（r1015 estate-absorb 窗·省锚如实注记）"
    "·W244 冻结窗 41.9G bm-a 实锚·W243 冻结窗 64.0G bm-a 实锚·W242 冻结窗 17.6G bm-a 实锚"
    "·W241 冻结窗 1.8G bm-c 实锚·W240 冻结窗 33.2G bm-a 实锚）"
)

NEW["b7_claim_projection"] = (
    "·probe W251+ 投影 A 567_501..569_500 CLEAN hops=0 / B naive 545_301..545_500 REFUSED→first-clean 565_501..565_700 hops=11 **live re-derive governs 预披露**"
    "（投影 A naive 567_501..569_500 CLEAN 零活点拒·hops=0；投影 B naive 545_301..545_500 拒=SEED_REGISTRY seed 545_500+W240..W249 A-ladder→first-clean 565_501..565_700·hops=11"
    "——**seed-gap 承袭 face：W250 A/B 仍 decoupled〔A 565_501..567_500 高悬于 B 545_101..545_300 之上〕·"
    "W251 冻结方禁假设 staircase A-base==prior-B-tail+1 恒等·须重读 live trace·W250 B 带将拒 naive W251 A 窗仅当重叠"
    "——**W251 freezer 承接面强制注记：须在 post-W250 宇宙重 derive 且 derive B 时预留本波 A 窗·W141 先例·never transcribe r587**）"
)

NEW["b8_selftest"] = (
    "selftest W250 face（A=first-clean A-continuation past prior-wave A tail+live-seeds 恒等"
    "·B=clean arithmetic continuation past prior-wave B tail+own-A 同窗互斥断言·W249 行 parity 腿"
    "**estate 提取面注记**：冻结拼接脚本的 parity estate（W138..W206 69 行 full-span·r858 absorb 代）从**本机 W249 块物理字节**提取"
    "（结构已知·提取自证断言 69 行 range 恒等在场）——W249 块的自有 W238..W248 legs（11 行）不入 estate 路径·提取后新增 W238..W249 leg（12 行）构成 W250 块 parity 108 行"
    "（W138..W206+W211+W212+W213+W214+W215+W216+W217+W218+W219+W220+W221+W222+W223+W224+W225+W226+W227+W228+W229"
    "+W230+W231+W232+W233+W234+W235+W236+W237+W238+W239+W240+W241+W242+W243+W244+W245+W246+W247+W248+W249）·零假设零风险。"
)

# marker pairs: (block, start_marker, end_marker) -- needles extracted from T1 at runtime (zero transcription)
BLOCKS = [
    ("b1_chain_tail", "+W246=bm-a r1016 prereg derive", "W250 freezer 承接面）】。"),
    ("b2_band_face", "（**B 面=CLEAN·hops=0 算术续带承袭形态**", "已如实披露非分叉）"),
    ("b3_bandface_s3", "（法典 §4 W250 行 B=545_101..545_300·**CLEAN·hops=0 算术续带承袭形态**", "兑现收敛·ADMIT 回执在场）"),
    ("b5_projection", "5. **W250+ 投影（probe 机证 leg4", "verify at W250 prereg，hop 链逐跳在 probe 回执。"),
    ("b6_ram", "·W249 冻结窗 RAM 未记录（r1036 死窗 estate 收口·省锚如实注记）", "W239 冻结窗 1.0G bm-c 实锚）"),
    ("b7_claim_projection", "·probe W250+ 投影 A 565_501..567_500 / B 545_101..545_300 **双面 CLEAN hops=0 预披露", "never transcribe r587**）"),
    ("b8_selftest", "selftest W250 face（A=first-clean A-continuation past prior-wave A tail+live-seeds 恒等·B=clean arithmetic continuation past prior-wave B tail+own-A 同窗互斥断言·W249 行 parity 腿", "零假设零风险。"),
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
    "PERPETUAL-N1-W250", "research/PERPETUAL_N1_W250_PREREG.md",
    "565_501..567_500", "545_101..545_300", "972,135", "545,720", "547,920",
    "n1_w250_results.json", "MSG-20261016-055x-bmc-w250-seat", "cc06f1f4a",
    "第 70 枚", "第七十枚", "第 248 枚", "CLEAN·hops=0",
    "连续第十三个 seed-gap face", "567_501..569_500", "545_301..545_500", "565_501..565_700",
    "_w250bmc_20261016", "--wave 250", "波号 250",
    "W249=bm-c r1041 prereg derive", "r1043 finalize one-pass",
    "n_eff_held_equal 969,935", "−0.09277202", "0.2450284", "−0.08793",
    "（**0.3158** 实测锚）", "bm-c 循环班 r1045 freeze 窗", "本窗 free RAM ~3.3GB",
    "→W246 **0.000334**→W247 **0.000333**→W248 **0.000332**→W249 **0.000332**】", "queue-head FREEZE-UNBLOCKED lane",
    "第 240 波", "seed_admit_gate rc0 双带 FREE", "A base=565501", "B base=545101",
    "bm-c r1043 W249 §7 范式", "bm-c r1043 W249 §8 范式",
    "W251 freezer 承接面", "verify at W251 prereg",
    "selftest W250 face", "W238..W249 leg（12 行）构成 W250 块 parity 108 行",
    "W249 实测 K-lift **0.0000**", "line_merged@K545,720 **1.1938**", "line_pre_w249 1.1938",
    "实差 0.0048 在带内", "已落账键·05:5x", "bm-c r1043 窗 05:5x",
    "r1041/W249 先例 freeze-prep 同式", "247 行单态", "probe leg0 机证 247 行",
    "_w249bmc_freeze_edits", "本波上游链=W1..W249 finalize 全落地",
    "engine_owner==bm-c 69 行注册", "bmc rows 69", "bmc_rows=69",
    "queue-head FREEZE-UNBLOCKED 承接", "A base==前波 A 尾+1（565_500+1）",
    "B base==前波 B 尾+1（545_100+1）",
    "W249 块的自有 W238..W248 legs（11 行）",
    "bm-c r1043 席位", "queue-head FREEZE-UNBLOCKED 发布",
    "post-W249-REGISTERED 终态注册", "席位窗 probe leg0 实测 247 行",
    "W243/W246/W248/W249 低 RAM 实烧先例", "·W249 冻结窗 RAM 未记录（r1042 死窗",
    "本候选=bm-c 自有席自有波", "R251：W250 带从未指派",
    "W247/W248/W249 B 带均低于走带起点", "W249 splice 先于席位窗已落地",
    "probe leg0 bmc_rows=69 attempt-continuity face（r1043 窗算法·bm-c own seat+bmc live rows 69 实读）",
]
for s in MUST:
    assert s in T2, "MUST-HAVE missing: %r" % s

MUST_NOT = [
    "563_501", "563_500", "544_901", "544_900",
    "−0.09279163", "0.2450393", "−0.09134", "**0.3154**", "8949e0aef",
    "MSG-20261015-225x", "第 69 枚", "第六十九枚", "第 247 枚",
    "engine_owner 行 238", "owner rows 238", "bmc rows 68", "bmc_rows=68",
    "engine_owner==bm-c 68", "连续第十二个 seed-gap", "--wave 249", "波号 249",
    "实差 0.0015 在带内", "r1037 窗算法", "第 239 波", "r1037",
    "waits-upstream ARMED", "verify at W250 prereg", "W250 freezer 承接面",
    "545,720 投影", "已落账键·22:1x",
    "本波上游链=W1..W248 finalize 全落地", "A base=563501", "B base=544901",
    "（bm-c r1037 席", "bm-c r1036 W249 §7 范式", "bm-c r1036 W249 §8 范式",
    "r1035/W249 先例", "probe leg0 机证 246 行", "W248 行 parity 腿",
    "键 W249 实测 K-lift **−0.0001**", "line_pre_w248",
    "freeze 窗 live derive 246 行", "零 247 行",
    "·W249 冻结窗 RAM 未记录（r1036",
    "本候选=bm-a", "R250：W249",
    "246 行", "二百四十六",
    "W243/W246/W249 低 RAM",
    "→W247 **0.000333**→W249 **0.000332**】",
    "W239 冻结窗 1.0G bm-c 实锚）",
]
for s in MUST_NOT:
    assert s not in T2, "MUST-NOT-HAVE present: %r (count=%d)" % (s, T2.count(s))

# projection-fulfillment count gates
assert T2.count("W250+ 投影") == 1, "W250+ 投影 count=%d (expect 1 = sec8 placeholder)" % T2.count("W250+ 投影")
assert T2.count("W251+ 投影") == 3, "W251+ 投影 count=%d (expect 3 = b1 tail + b5 title + b7 claim)" % T2.count("W251+ 投影")

# residue scan: all X_Y..X_Y windows well-formed
import re
for m in re.finditer(r"(\d{3}_\d{3})\.\.(\d{3}_\d{3})", T2):
    lo = int(m.group(1).replace("_", "")); hi = int(m.group(2).replace("_", ""))
    assert lo <= hi, "malformed window %s" % m.group(0)

io.open(OUT, "w", encoding="utf-8", newline="").write(T2)
print("W250 PREREG DERIVE OK -> %s (%d bytes, %d lines)" % (OUT, len(T2.encode("utf-8")), T2.count("\n") + 1))
print("blocks replaced: %s" % ", ".join(n for n, _, _ in BLOCKS))
print("vmap legs: %d floors: %d post-legs: %d MUST: %d MUST_NOT: %d" % (len(VMAP), len(VMAP_FLOORS), len(VMAP_POST_LEGS), len(MUST), len(MUST_NOT)))
