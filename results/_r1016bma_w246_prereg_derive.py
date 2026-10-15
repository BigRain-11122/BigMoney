# -*- coding: utf-8 -*-
# r1016 bm-a: W246 prereg derive (Phase-B count-asserted ordered transform).
# Source = committed frozen W245 prereg (git 6473fb7f8:research/PERPETUAL_N1_W245_PREREG.md,
# 21244 bytes -- the frozen pre-run face; sec7/8 placeholders intact).
# W246 facts (all machine-derived, never transcribed from r587):
#   - pre-seat probe ADMIT receipt results/_w246bma_20261015_probe_receipt.json
#     (A 557_501..559_500 clean hops=0 eighth seed-gap A-continuation /
#      B 542_201..542_400 double-clean hops=0, B base == prior-B-tail+1 EXACT)
#   - upstream W245 finalize landed: ledger 963,335 / K=536,920 / mu -0.09281866 /
#     sigma 0.2450379 / se_mu@K536,920 0.000334 / W245-only mu -0.09621 / A p95 0.3020 /
#     skill_line line_merged 1.1934 / line_pre_w245 1.1935 / n_eff_held 961,135 / K-lift -0.0001
#     (results/perpetual_faces/n1_w245_results.json + results/_r1015bma_w245_fivekeys.json)
#   - seat MSG-20261015-1328-bma-w246-seat @ origin 785936d84 (bm-a r1015 own-seat continuity)
#   - W247+ projection (probe leg4): A naive 559_501..561_500 CLEAN hops=0 /
#     B naive 542_401..542_600 hops=1 refused by registered W239 A band ->
#     first-clean 544_501..544_700 staircase band-hop face (first-disclosed)
import io, os, sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(REPO, "_r1016bma_w245_prereg_frozen.txt")
OUT = os.path.join(REPO, "research", "PERPETUAL_N1_W246_PREREG.md")

T0 = io.open(SRC, encoding="utf-8", newline="").read()

P1, P2, P3 = "\x01W\x01", "\x01N\x01", "\x01B\x01"

VMAP = [
    # pre-shift legs (must run BEFORE the wave-number roll; source faces carry W244)
    # NOTE: pre-shift leg TARGETS carry W244 so the wave-roll (W244->W245) lands them
    # on the final W245 face (targets are placed BEFORE the roll in list order)
    ("bm-a r1008 W244 §7 范式", "bm-a r1015 W244 §7 范式"),   # sec7 placeholder
    ("bm-a r1008 W244 §8 范式", "bm-a r1015 W244 §8 范式"),   # sec8 placeholder
    ("r1005/W244 先例 freeze-prep 同式", "r1015/W244 先例 freeze-prep 同式"),
    # wave-number roll (chained placeholders)
    ("W245", P1), ("W244", "W245"), (P1, "W246"),
    # result-file names (chained)
    ("n1_w245", P2), ("n1_w244", "n1_w245"), (P2, "n1_w246"),
    # probe/freeze script basenames (chained)
    ("_w245bma", P3), ("_w244bma", "_w245bma"), (P3, "_w246bma"),
    # runner CLI wave
    ("--wave 245", "--wave 246"),
    ("波号 245", "波号 246"),
    # band values (A chained: hi -> 559_500, base -> 557_501, prior tail -> 557_500)
    ("557_500", "559_500"), ("555_501", "557_501"), ("555_500", "557_500"),
    # band values (B chained: hi -> 542_400, base -> 542_201, prior tail -> 542_200,
    # naive lo/hi roll with the live-seed-hop face retired)
    ("542_200", "542_400"), ("542_001", "542_201"), ("541_900", "542_200"),
    ("541_901", "542_201"), ("542_100", "542_400"),
    # seed_admit_gate bare-number forms
    ("555501", "557501"), ("542001", "542201"),
    # ledger chain (projection first, then prev, then K)
    ("536,920 投影", "539,120 投影"), ("534,720", "536,920"), ("961,135", "963,335"),
    # sec5 keys -> W245 measured faces
    ("−0.09280471", "−0.09281866"), ("−0.10390359", "−0.09621"),
    ("0.24505388", "0.2450379"), ("实差 0.0111 在带内", "实差 0.0034 在带内"),
    ("（**0.2952** 实测锚）", "（**0.3020** 实测锚）"),
    ("n_eff_held_equal 958,935", "n_eff_held_equal 961,135"),
    ("→W245 **0.000335**】", "→W244 **0.000335**→W245 **0.000334**】"),  # runs POST wave-roll (source face already shifted)
    ("line_pre_w244", "line_pre_w245"),
    ("已落账键·07:4x", "已落账键·13:2x"),
    ("bm-a r1008 窗 07:4x", "bm-a r1015 窗 13:2x"),
    # ordinals
    ("第 243 枚", "第 244 枚"), ("第 127 枚", "第 128 枚"),
    ("第一百二十七枚", "第一百二十八枚"), ("第 235 波", "第 236 波"),
    ("engine_owner 行 234", "engine_owner 行 235"), ("owner rows 234", "owner rows 235"),
    ("242 行单态", "243 行单态"), ("全二百四十二行", "全二百四十三行"),
    ("二百四十二面", "二百四十三面"),
    ("bma rows 126", "bma rows 127"), ("bma_rows=126", "bma_rows=127"),
    ("live rows 126 实读", "live rows 127 实读"),
    ("engine_owner==bm-a 126 行", "engine_owner==bm-a 127 行"),
    ("probe leg0 机证 242 行", "probe leg0 机证 243 行"),
    ("probe leg0 实测 242 行", "probe leg0 实测 243 行"),
    # seed-gap ordinal (probe A_semantics: eighth consecutive seed-gap A-continuation)
    ("连续第六个 seed-gap face", "连续第八个 seed-gap face"),
    # seat / window faces
    ("MSG-20261015-0844", "MSG-20261015-1328"), ("2b0947947", "785936d84"),
    ("GM re-assignment takeover lane", "own-seat continuity lane"),
    ("bm-a r1010 席·GM re-assignment takeover 承接", "bm-a r1015 席·own-seat continuity 承接"),
    ("bm-a r1010 席位", "bm-a r1015 席位"), ("r1010 窗算法", "r1015 窗算法"),
    ("r1010 席位窗实跑", "r1015 席位窗实跑"),
    ("saturation_engine.py status live-read r1010", "saturation_engine.py status live-read r1016"),
    ("bm-a 循环班 r1010 freeze 窗 2026-10-15 09:3x", "bm-a 循环班 r1016 freeze 窗 2026-10-15 14:1x"),
    ("本窗 free RAM ~51.7GB", "本窗 free RAM ~47.1GB"),
]

VMAP_FLOORS = {
    "bm-a r1008 W244 §7 范式": 1, "bm-a r1008 W244 §8 范式": 1, "r1005/W244 先例 freeze-prep 同式": 1,
    "n1_w245": 4, "n1_w244": 3, "_w245bma": 4, "_w244bma": 1,
    "--wave 245": 2, "波号 245": 1,
    "557_500": 8, "555_501": 10, "555_500": 4,
    "542_200": 9, "542_001": 12, "541_900": 2, "541_901": 4, "542_100": 4,
    "555501": 1, "542001": 1,
    "536,920 投影": 1, "534,720": 7, "961,135": 3,
    "−0.09280471": 1, "−0.10390359": 1, "0.24505388": 1, "实差 0.0111 在带内": 1,
    "（**0.2952** 实测锚）": 1, "n_eff_held_equal 958,935": 1,
    "→W244 **0.000335**】": 1, "line_pre_w244": 1,
    "已落账键·07:4x": 1, "bm-a r1008 窗 07:4x": 1,
    "第 243 枚": 1, "第 127 枚": 2, "第一百二十七枚": 1, "第 235 波": 1,
    "engine_owner 行 234": 1, "owner rows 234": 1, "242 行单态": 1,
    "全二百四十二行": 1, "二百四十二面": 1,
    "bma rows 126": 2, "bma_rows=126": 1, "live rows 126 实读": 1,
    "engine_owner==bm-a 126 行": 1, "probe leg0 机证 242 行": 1,
    "probe leg0 实测 242 行": 1,
    "连续第六个 seed-gap face": 2,
    "MSG-20261015-0844": 4, "2b0947947": 3,
    "GM re-assignment takeover lane": 1,
    "bm-a r1010 席·GM re-assignment takeover 承接": 1,
    "bm-a r1010 席位": 1, "r1010 窗算法": 1, "r1010 席位窗实跑": 1,
    "saturation_engine.py status live-read r1010": 1,
    "bm-a 循环班 r1010 freeze 窗 2026-10-15 09:3x": 1,
    "本窗 free RAM ~51.7GB": 1,
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

NEW["b1_chain_tail"] = "+W244=bm-a r1004 席位+r1005 prereg derive（machine-SUB from frozen W243 tpl 70141bc22）+五面冻结 splice（r1007 10bdb987b pushed）+引擎自燃 12/12（07:11:04 done claim-exempt engine lane）+bm-a r1008 finalize one-pass 已落（K=534,720·账本头 961,135 机读·n1_w244_results.json·07:4x）+W245=bm-a r1010 席位（GM re-assignment takeover 承接）+死窗 r1013 prereg derive 收养（r1015 estate-absorb·machine-SUB from frozen W244 tpl 260ffd3f8）+五面冻结 splice（r1015 29d3ab761 pushed·estate-absorb 死窗 12:18-12:52 收口）+引擎自燃 12/12（12:50-13:01 claim-exempt engine lane·工作树字节==提交字节）+bm-a r1015 finalize one-pass 已落（K=536,920·账本头 963,335 机读·n1_w245_results.json·13:2x·fivekeys 6/6 ALL PASS）——本波上游链=W1..W245 finalize 全落地·零在飞上游席·干净前置**；席位公示=MSG-20261015-1328-bma-w246-seat 已推 origin 785936d84 先于本冻结【r565 律·席位先行·bm-a r1015 窗发布·本窗=own-seat continuity 承接】；下游 W247+ 投影见 §5.5（probe 机证 leg4·W247 freezer 承接面）】。"

NEW["b2_band_face"] = "（**B 面=DOUBLE-CLEAN·hops=0 算术续带承袭形态**：B 面 naive 续带 542_201..542_400（自注册 W245 B 尾 542_200 续）在 post-W245 注册宇宙上起点即 CLEAN 零活点拒（W245 席位 leg4 投影兑现·probe leg1 B_semantics 机证·B_double_clean_expected_face=true）且**不落本波 A 窗 557_501..559_500 内**（本波 A 高悬于 B 阶梯之上→**seed-decoupled A/B gap 承袭面**：同窗互斥面 leg2 律·W141 先例·B 无需 own-A reservation jump）→ B 保留 naive 落位 542_201..542_400·**hops=0**·**B base==前波 B 尾+1（542_200+1）EXACT 机检关系**（fc_b==fc_b_naive·B_hop_chain=[] 空集 leg1 机证·B_no_ownA_jump=true·B_semantics double-clean arithmetic continuation 回执在场）；**W245 席位 leg4 投影承接面注记兑现**：投影预言 W246 须在 post-W245 宇宙重 derive 且 A/B 双面 CLEAN hops=0 如投影所期——本窗如实兑现·A 零活点拒=投影所期·B 零活点拒 double-clean=投影所期·已如实披露非分叉）"

NEW["b3_bandface_s3"] = "（法典 §4 W246 行 B=542_201..542_400·**DOUBLE-CLEAN·hops=0 算术续带承袭形态**：B naive 续带 542_201..542_400（自注册 W245 B 尾 542_200 续）在 post-W245 注册宇宙上起点即 CLEAN 零活点拒（W245 席位 leg4 投影兑现·probe leg1 B_semantics 机证·B_double_clean_expected_face=true）且不落本波 A 窗 557_501..559_500 内（本波 A 高悬于 B 阶梯之上→同窗互斥面 leg2 律·W141 先例·B 无需 own-A reservation jump）→保留 naive 落位 542_201..542_400·hops=0·**B base==前波 B 尾+1（542_200+1）EXACT 机检关系**（fc_b==fc_b_naive·B_hop_chain=[] 空集 leg1 机证·B_no_ownA_jump=true·B_semantics double-clean arithmetic continuation 回执在场）·非转录 r587·与 W245 席位 leg4 投影承接面注记兑现收敛·ADMIT 回执在场）"

NEW["b5_projection"] = "5. **W247+ 投影（probe 机证 leg4·下波冻结方复核非转抄 r587 律）**：A naive first-clean 559_501..561_500 **CLEAN**（hops=0·pre-W246 宇宙零活点拒）；B naive **542_401..542_600 hops=1 拒带**（被注册 W239 A 带拒→诚实前行走 first-clean **544_501..544_700**·staircase band-hop face 首披露·**不落投影 A 窗内**——B_hop lands-inside-A=false 腿在场）；**W246 B 带 542_201..542_400 注册后将拒 naive W247 A 窗仅当重叠**（**seed-gap 承袭 face：W246 A/B 仍 decoupled〔A 557_501..559_500 高悬于 B 542_201..542_400 之上〕·W247 冻结方禁假设 staircase A-base==prior-B-tail+1 恒等·须重读 live trace**）——W247 冻结方必须在 post-W246 注册宇宙重 derive 且 derive B 时预留本波 A 窗——leg2 律/E36 卡·W141 先例；verify at W247 prereg，hop 链逐跳在 probe 回执。"

NEW["b6_ram"] = "·W245 冻结窗 RAM 未记录（r1015 estate-absorb 窗·省锚如实注记）·W244 冻结窗 41.9G bm-a 实锚·W243 冻结窗 64.0G bm-a 实锚·W242 冻结窗 17.6G bm-a 实锚·W241 冻结窗 1.8G bm-c 实锚·W240 冻结窗 33.2G bm-a 实锚·W239 冻结窗 1.0G bm-c 实锚）"

NEW["b7_claim_projection"] = "·probe W247+ 投影 A 559_501..561_500 / B 542_401..542_600→first-clean 544_501..544_700 **A CLEAN hops=0+B staircase band-hop hops=1 预披露+seed-gap 承袭注记**（投影 A naive 559_501..561_500 CLEAN 零活点拒·hops=0；投影 B naive 542_401..542_600 被注册 W239 A 带拒→first-clean 544_501..544_700 hops=1 staircase band-hop face 首披露·不落投影 A 窗内——**seed-gap 承袭 face：W246 A/B 仍 decoupled〔A 557_501..559_500 高悬于 B 542_201..542_400 之上〕·W247 冻结方禁假设 staircase A-base==prior-B-tail+1 恒等·须重读 live trace·W246 B 带将拒 naive W247 A 窗仅当重叠——**W247 freezer 承接面强制注记：须在 post-W246 宇宙重 derive 且 derive B 时预留本波 A 窗·W141 先例·never transcribe r587**）"

NEW["b8_selftest"] = "selftest W246 face（A=first-clean A-continuation past prior-wave A tail+live-seeds 恒等·B=double-clean arithmetic continuation past prior-wave B tail 同窗互斥断言·W245 行 parity 腿"

NEW["b9_estate"] = "——W245 块的自有 W235..W244 legs（10 行）不入 estate 路径·提取后新增 W235..W245 leg（11 行）构成 W246 块 parity 104 行（W138..W206+W211+W212+W213+W214+W215+W216+W217+W218+W219+W220+W221+W222+W223+W224+W225+W226+W227+W228+W229+W230+W231+W232+W233+W234+W235+W236+W237+W238+W239+W240+W241+W242+W243+W244+W245）·零假设零风险"

OLD_RAW = {}

OLD_RAW["b1_chain_tail"] = "+W244=bm-a r1004 席位+r1005 prereg derive（machine-SUB from frozen W243 tpl 70141bc22）+五面冻结 splice（r1007 10bdb987b pushed）+引擎自燃 12/12（07:11:04 done claim-exempt engine lane）+bm-a r1008 finalize one-pass 已落（K=534,720·账本头 961,135 机读·n1_w244_results.json·07:4x）——本波上游链=W1..W244 finalize 全落地·零在飞上游席·干净前置**；席位公示=MSG-20261015-0844-bma-w245-seat 已推 origin 2b0947947 先于本冻结【r565 律·席位先行·bm-a r1010 窗发布·本窗=GM re-assignment takeover 承接】；下游 W246+ 投影见 §5.5（probe 机证 leg4·W246 freezer 承接面）】。"

OLD_RAW["b2_band_face"] = "（**B 面=LIVE-SEED-REFUSAL·hops=1 seed-decoupled 形态承袭**：B 面 naive 续带 541_901..542_100（自注册 W244 B 尾 541_900 续）被 SEED_REGISTRY 活点 542_000 拒→诚实前行走 hop 1 first-clean 542_001..542_200 且**不落本波 A 窗 555_501..557_500 内**（本波 A 高悬于 B 阶梯之上→**seed-decoupled A/B gap 承袭面**：同窗互斥面 leg2 律·W141 先例·B 无需 own-A reservation jump）→ B 保留走落 542_001..542_200·**hops=1**·**B base==live-seed hop first-clean 机检关系**（fc_b==fc_b_naive hop 面·B_hop_chain=[naive 541_901..542_100→542_001·refuser 542_000] leg1 机证·B_no_ownA_jump=true·B_semantics seed-driven honest forward hop 回执在场）；**W244 席位 leg4 投影承接面注记兑现**：投影预言 W245 须在 post-W244 宇宙重 derive 且 A CLEAN hops=0+B live-seed hop 拒带面如投影所期——本窗如实兑现·A 零活点拒=投影所期·B live-seed hop 拒带=投影所期·已如实披露非分叉）"

OLD_RAW["b3_bandface_s3"] = "（法典 §4 W245 行 B=542_001..542_200·**LIVE-SEED-REFUSAL·hops=1 seed-decoupled 形态承袭**：B naive 续带 541_901..542_100（自注册 W244 B 尾 541_900 续）被 SEED_REGISTRY 活点 542_000 拒→诚实前行走 hop 1 first-clean 542_001..542_200 且不落本波 A 窗 555_501..557_500 内（本波 A 高悬于 B 阶梯之上→同窗互斥面 leg2 律·W141 先例·B 无需 own-A reservation jump）→保留走落 542_001..542_200·hops=1·**B base==live-seed hop first-clean 机检关系**（fc_b==fc_b_naive hop 面·B_hop_chain=[naive 541_901..542_100→542_001·refuser 542_000] leg1 机证·B_no_ownA_jump=true·B_semantics seed-driven honest forward hop 回执在场）·非转录 r587·与 W244 席位 leg4 投影承接面注记兑现收敛·ADMIT 回执在场）"

OLD_RAW["b5_projection"] = "5. **W246+ 投影（probe 机证 leg4·下波冻结方复核非转抄 r587 律）**：A naive first-clean 557_501..559_500 **CLEAN**（hops=0·pre-W245 宇宙零活点拒）；B naive first-clean **542_201..542_400 CLEAN**（hops=0·**不落投影 A 窗内**——B_hop lands-inside-A=false 腿在场）；**W245 B 带 542_001..542_200 注册后将拒 naive W246 A 窗仅当重叠**（**seed-gap 承袭 face：W245 A/B 仍 decoupled〔A 555_501..557_500 高悬于 B 542_001..542_200 之上〕·W246 冻结方禁假设 staircase A-base==prior-B-tail+1 恒等·须重读 live trace**）——W246 冻结方必须在 post-W245 注册宇宙重 derive 且 derive B 时预留本波 A 窗——leg2 律/E36 卡·W141 先例；verify at W246 prereg，hop 链逐跳在 probe 回执。"

OLD_RAW["b6_ram"] = "·W244 冻结窗 41.9G bm-a 实锚·W243 冻结窗 64.0G bm-a 实锚·W242 冻结窗 17.6G bm-a 实锚·W241 冻结窗 1.8G bm-c 实锚·W240 冻结窗 33.2G bm-a 实锚·W239 冻结窗 1.0G bm-c 实锚·W238 冻结窗 70.1G bm-a 实锚）"

OLD_RAW["b7_claim_projection"] = "·probe W246+ 投影 A 557_501..559_500 / B 542_201..542_400 **双面 CLEAN hops=0 预披露+seed-gap 承袭注记**（投影 A naive 557_501..559_500 CLEAN 零活点拒·hops=0；投影 B naive 542_201..542_400 CLEAN hops=0 不落投影 A 窗内——**seed-gap 承袭 face：W245 A/B 仍 decoupled〔A 555_501..557_500 高悬于 B 542_001..542_200 之上〕·W246 冻结方禁假设 staircase A-base==prior-B-tail+1 恒等·须重读 live trace·W245 B 带将拒 naive W246 A 窗仅当重叠——**W246 freezer 承接面强制注记：须在 post-W245 宇宙重 derive 且 derive B 时预留本波 A 窗·W141 先例·never transcribe r587**）"

OLD_RAW["b8_selftest"] = "selftest W245 face（A=first-clean A-continuation past prior-wave A tail+live-seeds 恒等·B=live-seed-hop first-clean past own-wave A 同窗互斥断言·W244 行 parity 腿"

OLD_RAW["b9_estate"] = "——W244 块的自有 W234..W243 legs（10 行）不入 estate 路径·提取后新增 W234..W244 leg（11 行）构成 W245 块 parity 103 行（W138..W206+W211+W212+W213+W214+W215+W216+W217+W218+W219+W220+W221+W222+W223+W224+W225+W226+W227+W228+W229+W230+W231+W232+W233+W234+W235+W236+W237+W238+W239+W240+W241+W242+W243+W244）·零假设零风险"

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
    "PERPETUAL-N1-W246", "research/PERPETUAL_N1_W246_PREREG.md",
    "557_501..559_500", "542_201..542_400", "963,335", "536,920", "539,120",
    "n1_w246_results.json", "MSG-20261015-1328-bma-w246-seat", "785936d84",
    "第 128 枚", "第一百二十八枚", "第 244 枚", "DOUBLE-CLEAN",
    "B_double_clean_expected_face", "连续第八个 seed-gap face",
    "559_501..561_500", "544_501..544_700", "staircase band-hop face 首披露",
    "_w246bma_20261015_probe_receipt.json", "--wave 246", "波号 246",
    "W245=bm-a r1010 席位", "29d3ab761", "r1015 finalize one-pass",
    "n_eff_held_equal 961,135", "−0.09281866", "0.2450379",
    "（**0.3020** 实测锚）", "bm-a 循环班 r1016 freeze 窗", "本窗 free RAM ~47.1GB",
    "→W245 **0.000334**】", "own-seat continuity lane", "第 236 波",
    "seed_admit_gate rc0 双带 FREE", "A base=557501", "B base=542201",
    "bm-a r1015 W245 §7 范式", "bm-a r1015 W245 §8 范式", "W247 freezer 承接面", "verify at W247 prereg",
    "selftest W246 face", "W235..W245 leg（11 行）构成 W246 块 parity 104 行",
]
for s in MUST:
    assert s in T2, "MUST-HAVE missing: %r" % s

MUST_NOT = [
    "555_501", "555_500", "541_901", "541_900", "LIVE-SEED-REFUSAL",
    "−0.09280471", "0.24505388", "**0.2952**", "2b0947947",
    "MSG-20261015-0844", "GM re-assignment takeover lane",
    "第 127 枚", "第一百二十七枚", "池第 243 枚", "engine_owner 行 234",
    "bma rows 126+候选", "probe receipt _w245bma", "连续第六个 seed-gap face",
    "--wave 245", "534,720+2,200", "0.0111 在带内", "r1010 窗算法",
    "W246 freezer 承接面强制注记", "verify at W246 prereg",
    "refuser 542_000", "n1_w244_results.json·07:4x）——本波上游链=W1..W245",
]
for s in MUST_NOT:
    assert s not in T2, "MUST-NOT-HAVE present: %r (count=%d)" % (s, T2.count(s))

# residue scan: zero frozen-W245 own-face leftovers (W246 face now owns the wave)
import re
for m in re.finditer(r"(\d{3}_\d{3})\.\.(\d{3}_\d{3})", T2):
    lo = int(m.group(1).replace("_", "")); hi = int(m.group(2).replace("_", ""))
    assert lo <= hi, "malformed window %s" % m.group(0)

io.open(OUT, "w", encoding="utf-8", newline="").write(T2)
print("W246 PREREG DERIVE OK -> %s (%d bytes, %d lines)" % (OUT, len(T2), T2.count("\n") + 1))
print("blocks replaced: b1_chain_tail, b2_band_face, b3_bandface_s3, b5_projection, b6_ram, b7_claim_projection, b8_selftest, b9_estate")
