# -*- coding: utf-8 -*-
# r1019 bm-a (successor): W247 prereg derive (Phase-B count-asserted ordered transform).
# Source = committed frozen W246 prereg (git 4a001a96d:research/PERPETUAL_N1_W246_PREREG.md,
# 31995 bytes -- the frozen pre-run face; sec7/8 placeholders intact).
# W247 facts (all machine-derived, never transcribed from r587):
#   - pre-seat probe ADMIT receipt results/_w247bma_20261015_probe_receipt.json
#     (A 559_501..561_500 clean hops=0 ninth seed-gap A-continuation /
#      B 544_501..544_700 staircase band-hop hops=1: naive 542_401..542_600 refused by
#      registered W239 A band 542_501..544_500, B base == refuser end 544_500+1 EXACT)
#   - upstream W246 finalize landed: ledger 965,535 / K=539,120 / merged mu -0.09281716 /
#     sigma 0.2450498 / se_mu@K539,120 0.000334 / W246-only mu -0.09245 / A p95 0.3072 /
#     line_pre_w246 1.1935 / line_merged@K539,120 1.1935 / K-lift +0.0000 / n_eff_held 963,335
#     (results/perpetual_faces/n1_w246_results.json + results/_r1017bma_w246_fivekeys.json)
#   - W246 chain: prereg derive r1016 (tpl 6473fb7f8) + five-face freeze splice r1017
#     650953086 + engine self-burn 12/12 15:44 + finalize one-pass r1018 (e06f4ee2a)
#   - seat MSG-20261015-1608-bma-w247-seat @ origin e06f4ee2a (bm-a r1018 own-seat continuity)
#   - W248+ projection (probe leg4): A naive 561_501..563_500 CLEAN hops=0 /
#     B naive 544_701..544_900 CLEAN hops=0 (B base == prior-B-tail+1 544_700+1 EXACT)
import io, os, sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(REPO, "_r1019bma_w246_frozen_face.txt")
OUT = os.path.join(REPO, "research", "PERPETUAL_N1_W247_PREREG.md")

T0 = io.open(SRC, encoding="utf-8", newline="").read()

P1, P2, P3 = "\x01W\x01", "\x01N\x01", "\x01B\x01"

VMAP = [
    # pre-shift legs (targets carry W245 so the wave-roll lands them on the final W246 face)
    ("bm-a r1015 W245 §7 范式", "bm-a r1018 W245 §7 范式"),
    ("bm-a r1015 W245 §8 范式", "bm-a r1018 W245 §8 范式"),
    ("r1015/W245 先例 freeze-prep 同式", "r1017/W245 先例 freeze-prep 同式"),
    # wave-number roll (chained placeholders)
    ("W246", P1), ("W245", "W246"), (P1, "W247"),
    # result-file names (chained)
    ("n1_w246", P2), ("n1_w245", "n1_w246"), (P2, "n1_w247"),
    # probe/freeze script basenames (chained)
    ("_w246bma", P3), ("_w245bma", "_w246bma"), (P3, "_w247bma"),
    # runner CLI wave
    ("--wave 246", "--wave 247"),
    ("波号 246", "波号 247"),
    # band values (A chained: hi 559_500 -> 561_500, base 557_501 -> 559_501, prior tail 557_500 -> 559_500)
    ("559_500", "561_500"), ("557_501", "559_501"), ("557_500", "559_500"),
    # band values (B chained: hi 542_400 -> 544_700, base 542_201 -> 544_501, prior tail 542_200 -> 542_400)
    ("542_400", "544_700"), ("542_201", "544_501"), ("542_200", "542_400"),
    # seed_admit_gate bare-number forms
    ("557501", "559501"), ("542201", "544501"),
    # ledger chain (projection first, then prior K, then prior ledger)
    ("539,120 投影", "541,320 投影"), ("536,920", "539,120"), ("963,335", "965,535"),
    # sec5 keys -> W246 measured faces
    ("−0.09281866", "−0.09281716"), ("−0.09621", "−0.09245"),
    ("0.2450379", "0.2450498"), ("实差 0.0034 在带内", "实差 0.0004 在带内"),
    ("（**0.3020** 实测锚）", "（**0.3072** 实测锚）"),
    ("n_eff_held_equal 961,135", "n_eff_held_equal 963,335"),
    ("→W244 **0.000335**→W246 **0.000334**】", "→W244 **0.000335**→W245 **0.000334**→W246 **0.000334**】"),  # POST wave-roll face
    ("line_pre_w245", "line_pre_w246"),
    ("line_merged@K539,120 **1.1934**", "line_merged@K539,120 **1.1935**"),  # POST ledger-roll face (K rolled by the 536,920 leg)
    ("W246 实测 K-lift **−0.0001**", "W246 实测 K-lift **+0.0000**"),  # POST wave-roll face (W245 rolled to W246)
    ("已落账键·13:2x", "已落账键·16:0x"),
    ("bm-a r1015 窗 13:2x", "bm-a r1018 窗 16:0x"),
    # ordinals
    ("第 244 枚", "第 245 枚"), ("第 128 枚", "第 129 枚"),
    ("第一百二十八枚", "第一百二十九枚"), ("第 236 波", "第 237 波"),
    ("engine_owner 行 235", "engine_owner 行 236"), ("owner rows 235", "owner rows 236"),
    ("243 行单态", "244 行单态"), ("全二百四十三行", "全二百四十四行"),
    ("二百四十三面", "二百四十四面"),
    ("bma rows 127", "bma rows 128"), ("bma_rows=127", "bma_rows=128"),
    ("live rows 127 实读", "live rows 128 实读"),
    ("engine_owner==bm-a 127 行", "engine_owner==bm-a 128 行"),
    ("probe leg0 机证 243 行", "probe leg0 机证 244 行"),
    ("probe leg0 实测 243 行", "probe leg0 实测 244 行"),
    # seed-gap ordinal (probe A_semantics: ninth consecutive seed-gap A-continuation)
    ("连续第八个 seed-gap face", "连续第九个 seed-gap face"),
    # seat / window faces (full-name legs BEFORE the number-only leg; heal the inherited
    # w245-seat frankenname from the r1016 number-only roll -> real W247 seat file name)
    ("MSG-20261015-1328-bma-w245-seat", "MSG-20261015-1608-bma-w247-seat"),
    ("MSG-20261015-1328-bma-w246-seat", "MSG-20261015-1608-bma-w247-seat"),
    ("MSG-20261015-1328", "MSG-20261015-1608"), ("785936d84", "e06f4ee2a"),
    ("bm-a r1015 席·own-seat continuity 承接", "bm-a r1018 席·own-seat continuity 承接"),
    ("bm-a r1015 席位", "bm-a r1018 席位"), ("r1015 窗算法", "r1018 窗算法"),
    ("r1015 席位窗实跑", "r1018 席位窗实跑"),
    ("saturation_engine.py status live-read r1016", "saturation_engine.py status live-read r1019"),
    ("bm-a 循环班 r1016 freeze 窗 2026-10-15 14:1x", "bm-a 循环班 r1019 freeze 窗 2026-10-15 17:3x"),
    ("本窗 free RAM ~47.1GB", "本窗 free RAM ~60.8GB"),
]

VMAP_FLOORS = {
    "bm-a r1015 W245 §7 范式": 1, "bm-a r1015 W245 §8 范式": 1, "r1015/W245 先例 freeze-prep 同式": 1,
    "n1_w246": 4, "n1_w245": 3, "_w246bma": 4, "_w245bma": 1,
    "--wave 246": 2, "波号 246": 1,
    "559_500": 8, "557_501": 10, "557_500": 4,
    "542_400": 9, "542_201": 10, "542_200": 4,
    "557501": 1, "542201": 1,
    "539,120 投影": 1, "536,920": 7, "963,335": 3,
    "−0.09281866": 1, "−0.09621": 1, "0.2450379": 1, "实差 0.0034 在带内": 1,
    "（**0.3020** 实测锚）": 1, "n_eff_held_equal 961,135": 1,
    "→W244 **0.000335**→W245 **0.000334**】": 1, "line_pre_w245": 1,
    "W245 实测 K-lift **−0.0001**": 1,
    "line_merged@K536,920 **1.1934**": 1,
    "已落账键·13:2x": 1, "bm-a r1015 窗 13:2x": 1,
    "第 244 枚": 1, "第 128 枚": 2, "第一百二十八枚": 1, "第 236 波": 1,
    "engine_owner 行 235": 1, "owner rows 235": 1, "243 行单态": 1,
    "全二百四十三行": 1, "二百四十三面": 1,
    "bma rows 127": 2, "bma_rows=127": 1, "live rows 127 实读": 1,
    "engine_owner==bm-a 127 行": 1, "probe leg0 机证 243 行": 1,
    "probe leg0 实测 243 行": 1,
    "连续第八个 seed-gap face": 2,
    "MSG-20261015-1328-bma-w245-seat": 3, "MSG-20261015-1328-bma-w246-seat": 1,
    "MSG-20261015-1328": 4, "785936d84": 3,
    "bm-a r1015 席·own-seat continuity 承接": 1,
    "bm-a r1015 席位": 1, "r1015 窗算法": 1, "r1015 席位窗实跑": 1,
    "saturation_engine.py status live-read r1016": 1,
    "bm-a 循环班 r1016 freeze 窗 2026-10-15 14:1x": 1,
    "本窗 free RAM ~47.1GB": 1,
}

def xf(t):
    for o, n in VMAP:
        t = t.replace(o, n)
    return t

for o, f in VMAP_FLOORS.items():
    if T0.count(o) < f:
        raise SystemExit("VMAP FLOOR FAIL: %r count=%d floor=%d" % (o, T0.count(o), f))

T1 = xf(T0)

# ---------------- block replacements (OLD' = xf(source bytes); NEW = final) ----------------
NEW = {}

NEW["b1_chain_tail"] = "+W244=bm-a r1004 席位+r1005 prereg derive（machine-SUB from frozen W243 tpl 70141bc22）+五面冻结 splice（r1007 10bdb987b pushed）+引擎自燃 12/12（07:11:04 done claim-exempt engine lane）+bm-a r1008 finalize one-pass 已落（K=534,720·账本头 961,135 机读·n1_w244_results.json·07:4x）+W245=bm-a r1010 席位（GM re-assignment takeover 承接）+死窗 r1013 prereg derive 收养（r1015 estate-absorb·machine-SUB from frozen W244 tpl 260ffd3f8）+五面冻结 splice（r1015 29d3ab761 pushed·estate-absorb 死窗 12:18-12:52 收口）+引擎自燃 12/12（12:50-13:01 claim-exempt engine lane·工作树字节==提交字节）+bm-a r1015 finalize one-pass 已落（K=536,920·账本头 963,335 机读·n1_w245_results.json·13:2x·fivekeys 6/6 ALL PASS）+W246=bm-a r1016 prereg derive（machine-SUB from frozen W245 tpl 6473fb7f8）+五面冻结 splice（r1017 650953086 pushed·editor gen a2-closer 修复×2 收口）+引擎自燃 12/12（15:44 done claim-exempt engine lane）+bm-a r1018 finalize one-pass 已落（K=539,120·账本头 965,535 机读·n1_w246_results.json·16:0x·fivekeys 6/6 ALL PASS）——本波上游链=W1..W246 finalize 全落地·零在飞上游席·干净前置**；席位公示=MSG-20261015-1608-bma-w247-seat 已推 origin e06f4ee2a 先于本冻结【r565 律·席位先行·bm-a r1018 窗发布·本窗=own-seat continuity 承接】；下游 W248+ 投影见 §5.5（probe 机证 leg4·W248 freezer 承接面）】。"

NEW["b2_band_face"] = "（**B 面=REGISTERED-REFUSAL·hops=1 staircase band-hop 形态首实现**：B 面 naive 续带 542_401..542_600（自注册 W246 B 尾 542_400 续）在 post-W246 注册宇宙上被注册 W239 A 带 542_501..544_500 拒→诚实前行走 hop 1 first-clean 544_501..544_700 且**不落本波 A 窗 559_501..561_500 内**（本波 A 高悬于 B 阶梯之上→**seed-decoupled A/B gap 承袭面**：同窗互斥面 leg2 律·W141 先例·B 无需 own-A reservation jump）→ B 保留走落 544_501..544_700·**hops=1**·**B base==拒带尾+1（544_500+1）EXACT 机检关系**（fc_b==fc_b_naive hop 面·B_hop_chain=[naive 542_401..542_600→544_501·refuser_pts 542_500·refuser 注册 W239 A 带 542_501..544_500] leg1 机证·B_no_ownA_jump=true·B_semantics staircase band-hop honest forward hop 回执在场）；**W246 席位 leg4 投影承接面注记兑现**：投影预言 W247 须在 post-W246 宇宙重 derive 且 A CLEAN hops=0+B staircase band-hop 拒带面如投影所期——本窗如实兑现·A 零活点拒=投影所期·B staircase band-hop 拒带=投影所期·staircase band-hop face FIRST-MATERIALIZED·已如实披露非分叉）"

NEW["b3_bandface_s3"] = "（法典 §4 W247 行 B=544_501..544_700·**REGISTERED-REFUSAL·hops=1 staircase band-hop 形态**：B naive 续带 542_401..542_600（自注册 W246 B 尾 542_400 续）被注册 W239 A 带 542_501..544_500 拒→诚实前行走 hop 1 first-clean 544_501..544_700 且不落本波 A 窗 559_501..561_500 内（本波 A 高悬于 B 阶梯之上→同窗互斥面 leg2 律·W141 先例·B 无需 own-A reservation jump）→保留走落 544_501..544_700·hops=1·**B base==拒带尾+1（544_500+1）EXACT 机检关系**（B_hop_chain=[naive 542_401..542_600→544_501·refuser 注册 W239 A 带 542_501..544_500] leg1 机证·B_no_ownA_jump=true·B_semantics staircase band-hop honest forward hop 回执在场）·非转录 r587·与 W246 席位 leg4 投影承接面注记兑现收敛·ADMIT 回执在场）"

NEW["b5_projection"] = "5. **W248+ 投影（probe 机证 leg4·下波冻结方复核非转抄 r587 律）**：A naive first-clean 561_501..563_500 **CLEAN**（hops=0·pre-W247 宇宙零活点拒）；B naive **544_701..544_900 CLEAN**（hops=0·B base==前波 B 尾+1（544_700+1）EXACT·**不落投影 A 窗内**——B_hop lands-inside-A=false 腿在场）；**W247 B 带 544_501..544_700 注册后将拒 naive W248 A 窗仅当重叠**（**seed-gap 承袭 face：W247 A/B 仍 decoupled〔A 559_501..561_500 高悬于 B 544_501..544_700 之上〕·W248 冻结方禁假设 staircase A-base==prior-B-tail+1 恒等·须重读 live trace**）——W248 冻结方必须在 post-W247 注册宇宙重 derive 且 derive B 时预留本波 A 窗——leg2 律/E36 卡·W141 先例；verify at W248 prereg，hop 链逐跳在 probe 回执。"

NEW["b6_ram"] = "·W246 冻结窗 RAM 未记录（r1017 死窗 estate 收口·省锚如实注记）·W245 冻结窗 RAM 未记录（r1015 estate-absorb 窗·省锚如实注记）·W244 冻结窗 41.9G bm-a 实锚·W243 冻结窗 64.0G bm-a 实锚·W242 冻结窗 17.6G bm-a 实锚·W241 冻结窗 1.8G bm-c 实锚·W240 冻结窗 33.2G bm-a 实锚·W239 冻结窗 1.0G bm-c 实锚）"

NEW["b7_claim_projection"] = "·probe W248+ 投影 A 561_501..563_500 / B 544_701..544_900 **双面 CLEAN hops=0 预披露+seed-gap 承袭注记**（投影 A naive 561_501..563_500 CLEAN 零活点拒·hops=0；投影 B naive 544_701..544_900 CLEAN hops=0 不落投影 A 窗内——**seed-gap 承袭 face：W247 A/B 仍 decoupled〔A 559_501..561_500 高悬于 B 544_501..544_700 之上〕·W248 冻结方禁假设 staircase A-base==prior-B-tail+1 恒等·须重读 live trace·W247 B 带将拒 naive W248 A 窗仅当重叠——**W248 freezer 承接面强制注记：须在 post-W247 宇宙重 derive 且 derive B 时预留本波 A 窗·W141 先例·never transcribe r587**）"

NEW["b8_selftest"] = "selftest W247 face（A=first-clean A-continuation past prior-wave A tail+live-seeds 恒等·B=registered-refusal staircase band-hop first-clean past own-wave A 同窗互斥断言·W246 行 parity 腿"

NEW["b9_estate"] = "——W246 块的自有 W235..W245 legs（11 行）不入 estate 路径·提取后新增 W235..W246 leg（12 行）构成 W247 块 parity 105 行（W138..W206+W211+W212+W213+W214+W215+W216+W217+W218+W219+W220+W221+W222+W223+W224+W225+W226+W227+W228+W229+W230+W231+W232+W233+W234+W235+W236+W237+W238+W239+W240+W241+W242+W243+W244+W245+W246）·零假设零风险。"

OLD_RAW = {}

OLD_RAW["b1_chain_tail"] = "+W244=bm-a r1004 席位+r1005 prereg derive（machine-SUB from frozen W243 tpl 70141bc22）+五面冻结 splice（r1007 10bdb987b pushed）+引擎自燃 12/12（07:11:04 done claim-exempt engine lane）+bm-a r1008 finalize one-pass 已落（K=534,720·账本头 961,135 机读·n1_w244_results.json·07:4x）+W245=bm-a r1010 席位（GM re-assignment takeover 承接）+死窗 r1013 prereg derive 收养（r1015 estate-absorb·machine-SUB from frozen W244 tpl 260ffd3f8）+五面冻结 splice（r1015 29d3ab761 pushed·estate-absorb 死窗 12:18-12:52 收口）+引擎自燃 12/12（12:50-13:01 claim-exempt engine lane·工作树字节==提交字节）+bm-a r1015 finalize one-pass 已落（K=536,920·账本头 963,335 机读·n1_w245_results.json·13:2x·fivekeys 6/6 ALL PASS）——本波上游链=W1..W245 finalize 全落地·零在飞上游席·干净前置**；席位公示=MSG-20261015-1328-bma-w246-seat 已推 origin 785936d84 先于本冻结【r565 律·席位先行·bm-a r1015 窗发布·本窗=own-seat continuity 承接】；下游 W247+ 投影见 §5.5（probe 机证 leg4·W247 freezer 承接面）】。"

OLD_RAW["b2_band_face"] = "（**B 面=DOUBLE-CLEAN·hops=0 算术续带承袭形态**：B 面 naive 续带 542_201..542_400（自注册 W245 B 尾 542_200 续）在 post-W245 注册宇宙上起点即 CLEAN 零活点拒（W245 席位 leg4 投影兑现·probe leg1 B_semantics 机证·B_double_clean_expected_face=true）且**不落本波 A 窗 557_501..559_500 内**（本波 A 高悬于 B 阶梯之上→**seed-decoupled A/B gap 承袭面**：同窗互斥面 leg2 律·W141 先例·B 无需 own-A reservation jump）→ B 保留 naive 落位 542_201..542_400·**hops=0**·**B base==前波 B 尾+1（542_200+1）EXACT 机检关系**（fc_b==fc_b_naive·B_hop_chain=[] 空集 leg1 机证·B_no_ownA_jump=true·B_semantics double-clean arithmetic continuation 回执在场）；**W245 席位 leg4 投影承接面注记兑现**：投影预言 W246 须在 post-W245 宇宙重 derive 且 A/B 双面 CLEAN hops=0 如投影所期——本窗如实兑现·A 零活点拒=投影所期·B 零活点拒 double-clean=投影所期·已如实披露非分叉）"

OLD_RAW["b3_bandface_s3"] = "（法典 §4 W246 行 B=542_201..542_400·**DOUBLE-CLEAN·hops=0 算术续带承袭形态**：B naive 续带 542_201..542_400（自注册 W245 B 尾 542_200 续）在 post-W245 注册宇宙上起点即 CLEAN 零活点拒（W245 席位 leg4 投影兑现·probe leg1 B_semantics 机证·B_double_clean_expected_face=true）且不落本波 A 窗 557_501..559_500 内（本波 A 高悬于 B 阶梯之上→同窗互斥面 leg2 律·W141 先例·B 无需 own-A reservation jump）→保留 naive 落位 542_201..542_400·hops=0·**B base==前波 B 尾+1（542_200+1）EXACT 机检关系**（fc_b==fc_b_naive·B_hop_chain=[] 空集 leg1 机证·B_no_ownA_jump=true·B_semantics double-clean arithmetic continuation 回执在场）·非转录 r587·与 W245 席位 leg4 投影承接面注记兑现收敛·ADMIT 回执在场）"

OLD_RAW["b5_projection"] = "5. **W247+ 投影（probe 机证 leg4·下波冻结方复核非转抄 r587 律）**：A naive first-clean 559_501..561_500 **CLEAN**（hops=0·pre-W246 宇宙零活点拒）；B naive **542_401..542_600 hops=1 拒带**（被注册 W239 A 带拒→诚实前行走 first-clean **544_501..544_700**·staircase band-hop face 首披露·**不落投影 A 窗内**——B_hop lands-inside-A=false 腿在场）；**W246 B 带 542_201..542_400 注册后将拒 naive W247 A 窗仅当重叠**（**seed-gap 承袭 face：W246 A/B 仍 decoupled〔A 557_501..559_500 高悬于 B 542_201..542_400 之上〕·W247 冻结方禁假设 staircase A-base==prior-B-tail+1 恒等·须重读 live trace**）——W247 冻结方必须在 post-W246 注册宇宙重 derive 且 derive B 时预留本波 A 窗——leg2 律/E36 卡·W141 先例；verify at W247 prereg，hop 链逐跳在 probe 回执。"

OLD_RAW["b6_ram"] = "·W245 冻结窗 RAM 未记录（r1015 estate-absorb 窗·省锚如实注记）·W244 冻结窗 41.9G bm-a 实锚·W243 冻结窗 64.0G bm-a 实锚·W242 冻结窗 17.6G bm-a 实锚·W241 冻结窗 1.8G bm-c 实锚·W240 冻结窗 33.2G bm-a 实锚·W239 冻结窗 1.0G bm-c 实锚）"

OLD_RAW["b7_claim_projection"] = "·probe W247+ 投影 A 559_501..561_500 / B 542_401..542_600→first-clean 544_501..544_700 **A CLEAN hops=0+B staircase band-hop hops=1 预披露+seed-gap 承袭注记**（投影 A naive 559_501..561_500 CLEAN 零活点拒·hops=0；投影 B naive 542_401..542_600 被注册 W239 A 带拒→first-clean 544_501..544_700 hops=1 staircase band-hop face 首披露·不落投影 A 窗内——**seed-gap 承袭 face：W246 A/B 仍 decoupled〔A 557_501..559_500 高悬于 B 542_201..542_400 之上〕·W247 冻结方禁假设 staircase A-base==prior-B-tail+1 恒等·须重读 live trace·W246 B 带将拒 naive W247 A 窗仅当重叠——**W247 freezer 承接面强制注记：须在 post-W246 宇宙重 derive 且 derive B 时预留本波 A 窗·W141 先例·never transcribe r587**）"

OLD_RAW["b8_selftest"] = "selftest W246 face（A=first-clean A-continuation past prior-wave A tail+live-seeds 恒等·B=double-clean arithmetic continuation past prior-wave B tail 同窗互斥断言·W245 行 parity 腿"

OLD_RAW["b9_estate"] = "——W245 块的自有 W235..W244 legs（10 行）不入 estate 路径·提取后新增 W235..W245 leg（11 行）构成 W246 块 parity 104 行（W138..W206+W211+W212+W213+W214+W215+W216+W217+W218+W219+W220+W221+W222+W223+W224+W225+W226+W227+W228+W229+W230+W231+W232+W233+W234+W235+W236+W237+W238+W239+W240+W241+W242+W243+W244+W245）·零假设零风险。"

T2 = T1
for name in ["b1_chain_tail", "b2_band_face", "b3_bandface_s3", "b5_projection",
             "b6_ram", "b7_claim_projection", "b8_selftest", "b9_estate"]:
    ob = xf(OLD_RAW[name])
    c = T2.count(ob)
    assert c == 1, "BLOCK %s count=%d (expect 1)" % (name, c)
    T2 = T2.replace(ob, NEW[name], 1)
    assert NEW[name] in T2, "BLOCK %s NEW not inserted" % name

# ---------------- post gates ----------------
MUST = [
    "PERPETUAL-N1-W247", "research/PERPETUAL_N1_W247_PREREG.md",
    "559_501..561_500", "544_501..544_700", "965,535", "539,120", "541,320",
    "n1_w247_results.json", "MSG-20261015-1608-bma-w247-seat", "e06f4ee2a",
    "第 129 枚", "第一百二十九枚", "第 245 枚", "REGISTERED-REFUSAL",
    "staircase band-hop face FIRST-MATERIALIZED", "连续第九个 seed-gap face",
    "561_501..563_500", "544_701..544_900", "542_501..544_500", "542_401..542_600",
    "_w247bma_20261015_probe_receipt.json", "--wave 247", "波号 247",
    "W246=bm-a r1016 prereg derive", "650953086", "r1018 finalize one-pass",
    "n_eff_held_equal 963,335", "−0.09281716", "0.2450498", "−0.09245",
    "（**0.3072** 实测锚）", "bm-a 循环班 r1019 freeze 窗", "本窗 free RAM ~60.8GB",
    "→W244 **0.000335**→W245 **0.000334**→W246 **0.000334**】", "own-seat continuity lane",
    "第 237 波", "seed_admit_gate rc0 双带 FREE", "A base=559501", "B base=544501",
    "bm-a r1018 W246 §7 范式", "bm-a r1018 W246 §8 范式", "W248 freezer 承接面", "verify at W248 prereg",
    "selftest W247 face", "W235..W246 leg（12 行）构成 W247 块 parity 105 行",
    "W246 实测 K-lift **+0.0000**", "line_merged@K539,120 **1.1935**", "line_pre_w246",
    "实差 0.0004 在带内", "已落账键·16:0x", "bm-a r1018 窗 16:0x",
    "r1017/W246 先例 freeze-prep 同式", "244 行单态", "probe leg0 机证 244 行",
    "_w246bma_freeze_edits", "本波上游链=W1..W246 finalize 全落地",
]
for s in MUST:
    assert s in T2, "MUST-HAVE missing: %r" % s

MUST_NOT = [
    "557_501", "557_500", "555_501", "555_500", "542_201", "542_200",
    "DOUBLE-CLEAN", "B_double_clean_expected_face",
    "−0.09621", "0.2450379", "**0.3020**", "785936d84",
    "MSG-20261015-1328", "第 128 枚", "第一百二十八枚", "池第 244 枚",
    "engine_owner 行 235", "bma rows 127", "probe leg0 机证 243 行",
    "连续第八个 seed-gap face", "--wave 246", "536,920+2,200", "W1..W245 已落账 536,920", "0.0034 在带内",
    "r1015 窗算法", "W247 freezer 承接面强制注记", "verify at W247 prereg",
    "staircase band-hop face 首披露", "W246 实测 K-lift **−0.0001**",
    "line_merged@K536,920 **1.1934**", "已落账键·13:2x", "n_eff_held_equal 961,135",
    "naive W247", "W247 冻结方",
    "本波上游链=W1..W245 finalize 全落地",
]
for s in MUST_NOT:
    assert s not in T2, "MUST-NOT-HAVE present: %r (count=%d)" % (s, T2.count(s))

# projection-fulfillment count gate: exactly one "W247+ 投影" = the §8 placeholder
# 承接机证 face (W248-projection faces live in §5.5/b7/b1 as "W248+ 投影")
assert T2.count("W247+ 投影") == 1, "W247+ 投影 count=%d (expect 1 = sec8 placeholder)" % T2.count("W247+ 投影")
assert T2.count("W248+ 投影") == 3, "W248+ 投影 count=%d (expect 3 = b1 tail + b5 title + b7 claim)" % T2.count("W248+ 投影")

# residue scan: all X_Y..X_Y windows well-formed
import re
for m in re.finditer(r"(\d{3}_\d{3})\.\.(\d{3}_\d{3})", T2):
    lo = int(m.group(1).replace("_", "")); hi = int(m.group(2).replace("_", ""))
    assert lo <= hi, "malformed window %s" % m.group(0)

io.open(OUT, "w", encoding="utf-8", newline="").write(T2)
print("W247 PREREG DERIVE OK -> %s (%d bytes, %d lines)" % (OUT, len(T2.encode('utf-8')), T2.count("\n") + 1))
print("blocks replaced: b1_chain_tail, b2_band_face, b3_bandface_s3, b5_projection, b6_ram, b7_claim_projection, b8_selftest, b9_estate")
print("vmap legs:", len(VMAP), "floors:", len(VMAP_FLOORS), "MUST:", len(MUST), "MUST_NOT:", len(MUST_NOT))
