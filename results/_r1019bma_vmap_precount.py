# -*- coding: utf-8 -*-
# r1019 bm-a: vmap pattern pre-count (W247 prereg derive floors)
import sys
sys.stdout.reconfigure(encoding="utf-8")
t = open("_r1019bma_w246_prereg_frozen.txt", encoding="utf-8").read()
pats = [
 "bm-a r1015 W245 §7 范式", "bm-a r1015 W245 §8 范式", "r1015/W245 先例 freeze-prep 同式",
 "1328-bma-w245-seat", "bma-w246-seat",
 "bm-a r1015 席·own-seat continuity 承接", "bm-a r1015 席位", "r1015 窗算法", "r1015 席位窗实跑",
 "saturation_engine.py status live-read r1016", "bm-a 循环班 r1016 freeze 窗 2026-10-15 14:1x",
 "本窗 free RAM ~47.1GB", "已落账键·13:2x", "bm-a r1015 窗 13:2x", "bm-a r1015 窗发布",
 "539,120 投影", "536,920", "963,335", "n_eff_held_equal 961,135",
 "第 244 枚", "第 128 枚", "第一百二十八枚", "第 236 波",
 "engine_owner 行 235", "owner rows 235", "243 行单态", "全二百四十三行", "二百四十三面",
 "bma rows 127", "bma_rows=127", "engine_owner==bm-a 127 行",
 "probe leg0 机证 243 行", "probe leg0 实测 243 行",
 "557501", "542201", "542_201", "542_400", "557_501", "557_500", "559_500",
 "line_pre_w245", "_w245bma", "_w246bma", "n1_w245", "n1_w246",
 "W247+ 投影", "--wave 246", "波号 246", "波号=注册表 W245",
 "键 W245 实测 K-lift **−0.0001**", "line_merged@K536,920 **1.1934**",
 "→W245 **0.000334**】", "实差 0.0034 在带内", "0.2450379", "−0.09281866", "−0.09621",
 "（**0.3020** 实测锚）", "534,720", "W246 B 带", "W246 A/B 仍 decoupled",
 "W247 freezer 承接面强制注记", "verify at W247 prereg", "W247 冻结方",
 "MSG-20261015-1328", "785936d84", "542_401..542_600", "544_501..544_700",
 "559_501..561_500", "561_501..563_500", "544_701..544_900",
 "DOUBLE-CLEAN", "B_double_clean_expected_face", "staircase band-hop face 首披露",
 "selftest W246 face", "W235..W245 leg", "构成 W246 块 parity 104 行",
 "本机 W245 块物理字节", "W235..W244 legs",
 "r1015/W244 先例", "r1005/W244 先例",
]
for p in pats:
    print(t.count(p), "|", p)
