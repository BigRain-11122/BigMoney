# -*- coding: utf-8 -*-
# r1037 bm-c: W249 prereg derive (count-asserted ordered transform + marker-extracted block replaces).
# Source = committed frozen W248 prereg (git b9abac706:research/PERPETUAL_N1_W248_PREREG.md, 33097 bytes
# -- the frozen pre-run face; sec7/8 placeholders intact).
# W249 facts (all machine-derived, never transcribed):
#   - seat probe ADMIT receipt results/_w249bmc_20261015_probe_receipt.json
#     (A 563_501..565_500 CLEAN hops=0 twelfth consecutive seed-gap A-continuation /
#      B 544_901..545_100 CLEAN hops=0 past the W239 staircase landing,
#      B base == W248-registered B tail 544_900+1 EXACT; seed_admit FREE x2;
#      queue-head FREEZE-UNBLOCKED seat published 8949e0aef, MSG-20261015-225x-bmc-w249-seat;
#      leg0 rows=246 w248_splice_landed=true owner_rows=238 bmc_rows=68 ordinal=239 bmc_ordinal=69)
#   - upstream W248 finalize landed (bm-c r1036 absorb, commit be82e2af1): ledger 969,935 EXACT
#     (967,735+2,200) / K=543,520 (541,320+2,200) / merged mu -0.09279163 / sigma 0.2450393 /
#     se_mu 0.000332 / W248-only mu -0.09134 / key1 gap 0.0015 in-band / A p95 0.3154 /
#     K-lift -0.0001 in-band micro-move / line_pre_w248 1.1938 / line_merged@K543,520 1.1937 /
#     n_eff_held 967,735 (results/perpetual_faces/n1_w248_results.json + results/_r1036bmc_w248_fivekeys.json)
#   - W248 chain: prereg derive r1035 b9abac706 (tpl @ 4c403cb16) + dead-window five-face freeze
#     splice 21:36 (sixgate splice-integrity ALL PASS, dual-sha16 pf fd8b95810b45c48c / n1
#     72e95889017708ba) + engine self-burn 12/12 21:36-21:44 + r1036 absorb finalize one-pass 22:1x
#   - W250+ projection (probe leg4, pre-W249 universe): A 565_501..567_500 / B 545_101..545_300 both CLEAN hops=0
import io, os, sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(REPO, "results", "_w249bmc_w248_frozen_face.txt")
OUT = os.path.join(REPO, "research", "PERPETUAL_N1_W249_PREREG.md")

T0 = io.open(SRC, encoding="utf-8", newline="").read()

P1, P2, P3 = "\x01W\x01", "\x01N\x01", "\x01B\x01"

VMAP = [
    # projection first, then prior-K bare, then ledger heads (order-critical)
    ("543,520 投影", "545,720 投影"),
    ("541,320", "543,520"),
    ("967,735", "969,935"),
    ("965,535", "967,735"),
    # sec5 measured keys -> W248 measured faces
    ("−0.09279753", "−0.09279163"),
    ("−0.08799", "−0.09134"),
    ("0.2450508", "0.2450393"),
    ("实差 0.0048 在带内", "实差 0.0015 在带内"),
    ("（**0.3292** 实测锚）", "（**0.3154** 实测锚）"),
    # band values (A chained: hi 563_500 -> 565_500, base 561_501 -> 563_501, prior tail 561_500 -> 563_500)
    ("563_500", "565_500"),
    ("561_501", "563_501"),
    ("561_500", "563_500"),
    # band values (B chained: hi 544_900 -> 545_100, base 544_701 -> 544_901, prior tail 544_700 -> 544_900)
    ("544_900", "545_100"),
    ("544_701", "544_901"),
    ("544_700", "544_900"),
    # seed_admit_gate bare-number forms
    ("A base=561501 span=2000 checked=2000 verdict=FREE", "A base=563501 span=2000 checked=2000 verdict=FREE"),
    ("B base=544701 span=200 checked=200 verdict=FREE", "B base=544901 span=200 checked=200 verdict=FREE"),
    # wave-number roll (chained placeholders)
    ("W248", P1), ("W247", "W248"), (P1, "W249"),
    # result-file names (chained)
    ("n1_w248", P2), ("n1_w247", "n1_w248"), (P2, "n1_w249"),
    # probe/freeze script basenames (chained; current face _w249bmc <- template _w248bmc)
    ("_w248bmc", P3), ("_w247bma", "_w248bmc"), (P3, "_w249bmc"),
    # runner CLI wave
    ("--wave 248", "--wave 249"),
    ("波号 248", "波号 249"),
    # seed-gap ordinal (probe A_semantics: twelfth consecutive)
    ("连续第十个 seed-gap face", "连续第十二个 seed-gap face"),
    # ordinals
    ("第 246 枚", "第 247 枚"),
    ("第 238 波", "第 239 波"),
    ("bm-c 第六十八枚自有波", "bm-c 第六十九枚自有波"),
    # subsumption-order fix (r1040): compound needle contains 第 68 枚 -> MUST run before the bare roll
    ("bmc rows 67+候选=第 68 枚 EXACT", "bmc rows 68+候选=第 69 枚 EXACT"),
    ("第 68 枚", "第 69 枚"),
    ("probe leg0 bmc_rows=67 attempt-continuity face（r1030 窗算法·bm-c own seat+bmc live rows 67 实读）",
     "probe leg0 bmc_rows=68 attempt-continuity face（r1037 窗算法·bm-c own seat+bmc live rows 68 实读）"),
    ("engine_owner==bm-c 67 行注册", "engine_owner==bm-c 68 行注册"),
    ("engine_owner 行 237 注册在册", "engine_owner 行 238 注册在册"),
    # registry scan face
    ("全二百四十五行注册 N1 带表", "全二百四十六行注册 N1 带表"),
    ("freeze 窗 live derive 245 行单态 owner rows 237", "freeze 窗 live derive 246 行单态 owner rows 238"),
    ("共二百四十五面实测", "共二百四十六面实测"),
    ("perpetual_faces.py 零 246 行", "perpetual_faces.py 零 247 行"),
    # seat / provenance faces
    ("MSG-20261015-164x-bmc-w248-seat", "MSG-20261015-225x-bmc-w249-seat"),
    ("86819ad77", "8949e0aef"),
    ("（bm-c r1030 席·waits-upstream ARMED 发布）", "（bm-c r1037 席·queue-head FREEZE-UNBLOCKED 发布）"),
    ("（bm-c r1030 席位", "（bm-c r1037 席位"),
    ("waits-upstream ARMED lane）", "queue-head FREEZE-UNBLOCKED lane）"),
    ("（r1030 席位窗实跑", "（r1037 席位窗实跑"),
    # finalize window faces (pre-chain forms)
    ("bm-a r1022 窗 19:0x", "bm-c r1036 窗 22:1x"),
    ("·19:0x finalize one-pass】", "·22:1x finalize one-pass】"),
    ("r1019/W248 先例 freeze-prep 同式", "r1035/W248 先例 freeze-prep 同式"),
    # freeze window + engine live-read
    ("bm-c 循环班 r1035 freeze 窗 2026-10-15 19:4x", "bm-c 循环班 r1037 freeze 窗 2026-10-16 02:1x"),
    ("saturation_engine.py status live-read r1035", "saturation_engine.py status live-read r1037"),
    # RAM head face (bm-c current window honest)
    ("本窗 free RAM ~1.9GB（bm-c 底盘常驻·24G 物理内存机·MV V4 Jay 化 i2v 批=CEO 令 O-20261015-1040 在飞〔MV 优先级最高·GPU 车〕+CPU 车道独立如实注记）",
     "本窗 free RAM ~1.9GB（bm-c 底盘常驻·24G 物理内存机·MV V4 装配+星晴 T1 海审=bm-a 席在飞〔P0 交接 poke 22:54 已收·bm-c GPU 空窗〕+CPU 车道独立如实注记）"),
]

VMAP_FLOORS = {
    "543,520 投影": 1, "541,320": 5, "967,735": 3, "965,535": 2,
    "−0.09279753": 1, "−0.08799": 1, "0.2450508": 1, "实差 0.0048 在带内": 1,
    "（**0.3292** 实测锚）": 1,
    "563_500": 8, "561_501": 10, "561_500": 4,
    "544_900": 10, "544_701": 10, "544_700": 5,
    "A base=561501 span=2000 checked=2000 verdict=FREE": 1,
    "B base=544701 span=200 checked=200 verdict=FREE": 1,
    "W248": 26, "W247": 62,
    "n1_w248": 4, "n1_w247": 3, "_w248bmc": 4, "_w247bma": 1,
    "--wave 248": 2, "波号 248": 1,
    "连续第十个 seed-gap face": 2,
    "第 246 枚": 1, "第 238 波": 1,
    "bm-c 第六十八枚自有波": 1, "第 68 枚": 2,
    "probe leg0 bmc_rows=67 attempt-continuity face（r1030 窗算法·bm-c own seat+bmc live rows 67 实读）": 1,
    "bmc rows 67+候选=第 68 枚 EXACT": 2,
    "engine_owner==bm-c 67 行注册": 1,
    "engine_owner 行 237 注册在册": 1,
    "全二百四十五行注册 N1 带表": 1,
    "freeze 窗 live derive 245 行单态 owner rows 237": 1,
    "共二百四十五面实测": 1,
    "perpetual_faces.py 零 246 行": 1,
    "MSG-20261015-164x-bmc-w248-seat": 4, "86819ad77": 3,
    "（bm-c r1030 席·waits-upstream ARMED 发布）": 1,
    "（bm-c r1030 席位": 1, "waits-upstream ARMED lane）": 1, "（r1030 席位窗实跑": 1,
    "bm-a r1022 窗 19:0x": 1, "·19:0x finalize one-pass】": 1,
    "r1019/W247 先例 freeze-prep 同式": 1,
    "bm-c 循环班 r1035 freeze 窗 2026-10-15 19:4x": 1,
    "saturation_engine.py status live-read r1035": 1,
    "本窗 free RAM ~1.9GB（bm-c 底盘常驻·24G 物理内存机·MV V4 Jay 化 i2v 批=CEO 令 O-20261015-1040 在飞〔MV 优先级最高·GPU 车〕+CPU 车道独立如实注记）": 1,
}

# floors for POST-chain correction legs (needles exist only in T1 after the pre-chain legs run)
VMAP_POST_LEGS = [
    # universe face: W249 seat ran on the post-W248-REGISTERED (finalized) universe, freeze UNBLOCKED
    ("席位窗宇宙（post-W246 注册+W248 候选保留拒面·waits-upstream ARMED）起点即 CLEAN 零活点拒（W248 席位 leg4 投影兑现",
     "席位窗宇宙（post-W248-REGISTERED 终态注册·freeze-UNBLOCKED）起点即 CLEAN 零活点拒（W248 席位 leg4 投影兑现", 2),
    # probe leg0 registry faces: splice landed BEFORE the seat window (zero +1 owed)
    ("probe leg0 机证 244 行〔W248 splice 后于席位窗落地·+1 如实注记〕",
     "probe leg0 机证 246 行〔W248 splice 先于席位窗已落地·零 +1 如实注记〕", 1),
    ("席位窗 probe leg0 实测 244 行〔W248 splice 后于席位窗落地·+1 如实注记〕",
     "席位窗 probe leg0 实测 246 行〔W248 splice 先于席位窗已落地·零 +1 如实注记〕", 1),
    # se_mu narrowing chain: relabel rolled W248 tail back to W247 and append true W248 se
    ("→W246 **0.000334**→W248 **0.000333**】", "→W246 **0.000334**→W247 **0.000333**→W248 **0.000332**】", 1),
    # K-lift / line faces (source needle is the un-rolled lowercase w247 form; VMAP rolls uppercase only)
    ("键 W248 实测 K-lift **+0.0000**", "键 W248 实测 K-lift **−0.0001**", 1),
    ("line_pre_w247 1.1937", "line_pre_w248 1.1938", 1),
    # sec7/8 backfill paradigm rows
    ("bm-a r1022 W248 §7 范式", "bm-c r1036 W248 §7 范式", 1),
    ("bm-a r1022 W248 §8 范式", "bm-c r1036 W248 §8 范式", 1),
    # low-RAM precedent list gains W248 (engine self-burn 21:36-21:44 on this 1.9G-free machine)
    ("W243/W246 低 RAM 实烧先例", "W243/W246/W248 低 RAM 实烧先例", 1),
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
    "——本波上游链=W1..W248 finalize 全落地·零在飞上游席·干净前置**；"
    "席位公示=MSG-20261015-225x-bmc-w249-seat 已推 origin 8949e0aef 先于本冻结"
    "【r565 律·席位先行·bm-c r1037 窗发布·queue-head FREEZE-UNBLOCKED 承接·W248 own-wave finalize 已落=席位时即解锁】；"
    "下游 W250+ 投影见 §5.5（probe 机证 leg4·W250 freezer 承接面）】。"
)

NEW["b2_band_face"] = (
    "（**B 面=CLEAN·hops=0 算术续带承袭形态**：B 面 naive 续带 544_901..545_100（自注册 W248 B 尾 544_900 续）"
    "在席位窗宇宙（post-W248-REGISTERED 终态注册·freeze-UNBLOCKED）起点即 CLEAN 零活点拒"
    "（W248 席位 leg4 投影兑现·probe leg1 B_semantics 机证·W239 staircase band-hop landing 已过——注册 W239 A 带 542_501..544_500 "
    "与 W247/W248 B 带均低于走带起点）"
    "且**不落本波 A 窗 563_501..565_500 内**（本波 A 高悬于 B 阶梯之上→**seed-decoupled A/B gap 承袭面**：同窗互斥面 leg2 律·W141 先例·B 无需 own-A reservation jump）"
    "→ B 保留 naive 落位 544_901..545_100·**hops=0**·**B base==前波 B 尾+1（544_900+1）EXACT 机检关系**"
    "（fc_b==fc_b_naive·B_hop_chain=[] 空集 leg1 机证·B_no_ownA_jump=true·B_semantics clean arithmetic continuation 回执在场·W248 splice 先于席位窗落地=freeze 窗 post-W248 宇宙重 derive 复核面在场）；"
    "**W248 席位 leg4 投影承接面注记兑现**：投影预言 W249 须在 post-W248 宇宙重 derive 且 A/B 双面 CLEAN hops=0 落位如投影所期"
    "——本窗如实兑现·A 零活点拒=投影所期·B 零活点拒=投影所期·已如实披露非分叉）"
)

NEW["b3_bandface_s3"] = (
    "（法典 §4 W249 行 B=544_901..545_100·**CLEAN·hops=0 算术续带承袭形态**：B naive 续带 544_901..545_100（自注册 W248 B 尾 544_900 续）"
    "在席位窗宇宙（post-W248-REGISTERED 终态注册）起点即 CLEAN 零活点拒（W248 席位 leg4 投影兑现·probe leg1 B_semantics 机证·W239 staircase landing 已过）"
    "且不落本波 A 窗 563_501..565_500 内（本波 A 高悬于 B 阶梯之上→同窗互斥面 leg2 律·W141 先例·B 无需 own-A reservation jump）"
    "→保留 naive 落位 544_901..545_100·hops=0·**B base==前波 B 尾+1（544_900+1）EXACT 机检关系**"
    "（fc_b==fc_b_naive·B_hop_chain=[] 空集 leg1 机证·B_no_ownA_jump=true·B_semantics clean arithmetic continuation 回执在场）"
    "·非转录 r587·与 W248 席位 leg4 投影承接面注记兑现收敛·ADMIT 回执在场）"
)

NEW["b5_projection"] = (
    "5. **W250+ 投影（probe 机证 leg4·下波冻结方复核非转抄 r587 律）**：A naive first-clean 565_501..567_500 **CLEAN**（hops=0·pre-W249 宇宙零活点拒）；"
    "B naive **545_101..545_300 CLEAN**（hops=0·B base==前波 B 尾+1（545_100+1）EXACT·**不落投影 A 窗内**——B_hop lands-inside-A=false 腿在场）；"
    "**W249 B 带 544_901..545_100 注册后将拒 naive W250 A 窗仅当重叠**"
    "（**seed-gap 承袭 face：W249 A/B 仍 decoupled〔A 563_501..565_500 高悬于 B 544_901..545_100 之上〕·W250 冻结方禁假设 staircase A-base==prior-B-tail+1 恒等·须重读 live trace**）"
    "——W250 冻结方必须在 post-W249 注册宇宙重 derive 且 derive B 时预留本波 A 窗——leg2 律/E36 卡·W141 先例；verify at W250 prereg，hop 链逐跳在 probe 回执。"
)

NEW["b6_ram"] = (
    "·W248 冻结窗 RAM 未记录（r1036 死窗 estate 收口·省锚如实注记）"
    "·W247 冻结窗 60.8G bm-a 实锚·W246 冻结窗 RAM 未记录（r1017 死窗 estate 收口·省锚如实注记）"
    "·W245 冻结窗 RAM 未记录（r1015 estate-absorb 窗·省锚如实注记）"
    "·W244 冻结窗 41.9G bm-a 实锚·W243 冻结窗 64.0G bm-a 实锚·W242 冻结窗 17.6G bm-a 实锚"
    "·W241 冻结窗 1.8G bm-c 实锚·W240 冻结窗 33.2G bm-a 实锚·W239 冻结窗 1.0G bm-c 实锚）"
)

NEW["b7_claim_projection"] = (
    "·probe W250+ 投影 A 565_501..567_500 / B 545_101..545_300 **双面 CLEAN hops=0 预披露+seed-gap 承袭注记**"
    "（投影 A naive 565_501..567_500 CLEAN 零活点拒·hops=0；投影 B naive 545_101..545_300 CLEAN hops=0 不落投影 A 窗内"
    "——**seed-gap 承袭 face：W249 A/B 仍 decoupled〔A 563_501..565_500 高悬于 B 544_901..545_100 之上〕·"
    "W250 冻结方禁假设 staircase A-base==prior-B-tail+1 恒等·须重读 live trace·W249 B 带将拒 naive W250 A 窗仅当重叠"
    "——**W250 freezer 承接面强制注记：须在 post-W249 宇宙重 derive 且 derive B 时预留本波 A 窗·W141 先例·never transcribe r587**）"
)

NEW["b8_selftest"] = (
    "selftest W249 face（A=first-clean A-continuation past prior-wave A tail+live-seeds 恒等"
    "·B=clean arithmetic continuation past prior-wave B tail+own-A 同窗互斥断言·W248 行 parity 腿"
    "**estate 提取面注记**：冻结拼接脚本的 parity estate（W138..W206 69 行 full-span·r858 absorb 代）从**本机 W248 块物理字节**提取"
    "（结构已知·提取自证断言 69 行 range 恒等在场）——W248 块的自有 W237..W247 legs（11 行）不入 estate 路径·提取后新增 W237..W248 leg（12 行）构成 W249 块 parity 107 行"
    "（W138..W206+W211+W212+W213+W214+W215+W216+W217+W218+W219+W220+W221+W222+W223+W224+W225+W226+W227+W228+W229"
    "+W230+W231+W232+W233+W234+W235+W236+W237+W238+W239+W240+W241+W242+W243+W244+W245+W246+W247+W248）·零假设零风险。"
)

# marker pairs: (block, start_marker, end_marker) -- needles extracted from T1 at runtime (zero transcription)
BLOCKS = [
    ("b1_chain_tail", "+W246=bm-a r1016 prereg derive", "W249 freezer 承接面）】。"),
    ("b2_band_face", "（**B 面=CLEAN·hops=0 算术续带承袭形态**", "已如实披露非分叉）"),
    ("b3_bandface_s3", "（法典 §4 W249 行 B=544_901..545_100·**CLEAN·hops=0 算术续带承袭形态**", "兑现收敛·ADMIT 回执在场）"),
    ("b5_projection", "5. **W249+ 投影（probe 机证 leg4", "verify at W249 prereg，hop 链逐跳在 probe 回执。"),
    ("b6_ram", "·W248 冻结窗 60.8G bm-a 实锚", "W239 冻结窗 1.0G bm-c 实锚）"),
    ("b7_claim_projection", "·probe W249+ 投影 A 563_501..565_500 / B 544_901..545_100 **双面 CLEAN hops=0 预披露", "never transcribe r587**）"),
    ("b8_selftest", "selftest W249 face（A=first-clean A-continuation past prior-wave A tail+live-seeds 恒等·B=clean arithmetic continuation past prior-wave B tail+own-A 同窗互斥断言·W248 行 parity 腿", "零假设零风险。"),
]

T2 = T1
for name, sm, em in BLOCKS:
    c = T2.count(sm)
    assert c == 1, "BLOCK %s start-marker count=%d (expect 1)" % (name, c)
    i = T2.index(sm)
    j = T2.find(em, i)
    assert j > i, "BLOCK %s end-marker not found after start" % name
    j += len(em)
    needle = T2[i:j]
    T2 = T2[:i] + NEW[name] + T2[j:]
    assert NEW[name] in T2, "BLOCK %s NEW not inserted" % name

# ---------------- post gates ----------------
MUST = [
    "PERPETUAL-N1-W249", "research/PERPETUAL_N1_W249_PREREG.md",
    "563_501..565_500", "544_901..545_100", "969,935", "543,520", "545,720",
    "n1_w249_results.json", "MSG-20261015-225x-bmc-w249-seat", "8949e0aef",
    "第 69 枚", "第六十九枚", "第 247 枚", "CLEAN·hops=0",
    "连续第十二个 seed-gap face", "565_501..567_500", "545_101..545_300",
    "_w249bmc_20261015_probe_receipt.json", "--wave 249", "波号 249",
    "W248=bm-c r1035 prereg derive", "r1036 finalize one-pass",
    "n_eff_held_equal 967,735", "−0.09279163", "0.2450393", "−0.09134",
    "（**0.3154** 实测锚）", "bm-c 循环班 r1037 freeze 窗", "本窗 free RAM ~1.9GB",
    "→W246 **0.000334**→W247 **0.000333**→W248 **0.000332**】", "queue-head FREEZE-UNBLOCKED lane",
    "第 239 波", "seed_admit_gate rc0 双带 FREE", "A base=563501", "B base=544901",
    "bm-c r1036 W248 §7 范式", "bm-c r1036 W248 §8 范式",
    "W250 freezer 承接面", "verify at W250 prereg",
    "selftest W249 face", "W237..W248 leg（12 行）构成 W249 块 parity 107 行",
    "W248 实测 K-lift **−0.0001**", "line_merged@K543,520 **1.1937**", "line_pre_w248 1.1938",
    "实差 0.0015 在带内", "已落账键·22:1x", "bm-c r1036 窗 22:1x",
    "r1035/W248 先例 freeze-prep 同式", "246 行单态", "probe leg0 机证 246 行",
    "_w248bmc_freeze_edits", "本波上游链=W1..W248 finalize 全落地",
    "engine_owner==bm-c 68 行注册", "bmc rows 68", "bmc_rows=68",
    "queue-head FREEZE-UNBLOCKED 承接", "A base==前波 A 尾+1（563_500+1）",
    "B base==前波 B 尾+1（544_900+1）",
    "W248 块的自有 W237..W247 legs（11 行）",
    "bm-c r1037 席位", "queue-head FREEZE-UNBLOCKED 发布",
    "post-W248-REGISTERED 终态注册", "席位窗 probe leg0 实测 246 行",
    "W243/W246/W248 低 RAM 实烧先例", "·W248 冻结窗 RAM 未记录（r1036 死窗",
]
for s in MUST:
    assert s in T2, "MUST-HAVE missing: %r" % s

MUST_NOT = [
    "561_501", "561_500", "544_701", "544_700",
    "−0.09279753", "0.2450508", "−0.08799", "**0.3292**", "86819ad77",
    "MSG-20261015-164x", "第 68 枚", "第六十八枚", "第 246 枚",
    "engine_owner 行 237", "owner rows 237", "bmc rows 67", "bmc_rows=67",
    "engine_owner==bm-c 67", "连续第十个 seed-gap", "--wave 248", "波号 248",
    "实差 0.0048 在带内", "r1030 窗算法", "第 238 波",
    "waits-upstream ARMED", "verify at W249 prereg", "W249 freezer 承接面",
    "543,520 投影", "已落账键·19:0x", "bm-a r1022 窗 19:0x",
    "本波上游链=W1..W247 finalize 全落地", "A base=561501", "B base=544701",
    "（bm-c r1030 席", "·19:0x finalize one-pass】", "bm-a r1022 W248 §7 范式",
    "r1019/W248 先例", "probe leg0 机证 244 行", "W247 行 parity 腿",
    "（**0.3292**", "键 W248 实测 K-lift **+0.0000**", "line_pre_w248 1.1937",
    "freeze 窗 live derive 245 行", "零 246 行",
    # r1040 needle fix: stale-head detector is the ROLLED T1 form (·W248 冻结窗 60.8G...), not the pre-roll W247 face
    "·W248 冻结窗 60.8G bm-a 实锚·W246",
]
for s in MUST_NOT:
    assert s not in T2, "MUST-NOT-HAVE present: %r (count=%d)" % (s, T2.count(s))

# projection-fulfillment count gates
assert T2.count("W249+ 投影") == 1, "W249+ 投影 count=%d (expect 1 = sec8 placeholder)" % T2.count("W249+ 投影")
assert T2.count("W250+ 投影") == 3, "W250+ 投影 count=%d (expect 3 = b1 tail + b5 title + b7 claim)" % T2.count("W250+ 投影")

# residue scan: all X_Y..X_Y windows well-formed
import re
for m in re.finditer(r"(\d{3}_\d{3})\.\.(\d{3}_\d{3})", T2):
    lo = int(m.group(1).replace("_", "")); hi = int(m.group(2).replace("_", ""))
    assert lo <= hi, "malformed window %s" % m.group(0)

io.open(OUT, "w", encoding="utf-8", newline="").write(T2)
print("W249 PREREG DERIVE OK -> %s (%d bytes, %d lines)" % (OUT, len(T2.encode("utf-8")), T2.count("\n") + 1))
print("blocks replaced: %s" % ", ".join(n for n, _, _ in BLOCKS))
print("vmap legs: %d floors: %d MUST: %d MUST_NOT: %d" % (len(VMAP), len(VMAP_FLOORS), len(MUST), len(MUST_NOT)))
