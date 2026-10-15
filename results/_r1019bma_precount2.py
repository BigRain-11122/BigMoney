# -*- coding: utf-8 -*-
# r1019 bm-a: vmap pre-count on the FROZEN W246 tpl face (git 4a001a96d raw dump)
import sys
sys.stdout.reconfigure(encoding="utf-8")
t = open("_r1019bma_w246_frozen_face.txt", encoding="utf-8").read()
print("bytes", len(t.encode('utf-8')), "chars", len(t))
pats = [
 # pre-shift legs (targets carry W245 so roll lands W246)
 "bm-a r1015 W245 §7 范式", "bm-a r1015 W245 §8 范式", "r1015/W245 先例 freeze-prep 同式",
 # wave / files / basenames
 "W246", "W245", "W247", "W248", "n1_w246", "n1_w245", "_w246bma", "_w245bma",
 "--wave 246", "波号 246", "--wave 245",
 # A band faces
 "559_500", "557_501", "555_500", "555_501", "557_500", "559_501", "561_500",
 # B band faces
 "542_400", "542_201", "542_200", "542_001", "541_900", "542_401", "542_600",
 "544_501", "544_700", "542_501", "544_500", "544_701", "544_900", "561_501", "563_500",
 "542401", "542600", "542501", "544500", "544501", "544700",
 # seed_admit bare
 "557501", "542201",
 # ledger chain
 "539,120 投影", "536,920", "963,335", "961,135", "965,535", "541,320", "534,720",
 # sec5 anchors
 "−0.09281866", "−0.09621", "0.2450379", "实差 0.0034 在带内", "（**0.3020** 实测锚）",
 "n_eff_held_equal 961,135", "→W244 **0.000335**→W245 **0.000334**】", "line_pre_w245",
 "line_merged@K536,920 **1.1934**", "K-lift", "W245 实测 K-lift **−0.0001**",
 "已落账键·13:2x", "bm-a r1015 窗 13:2x",
 # ordinals
 "第 244 枚", "第 128 枚", "第一百二十八枚", "第 236 波", "engine_owner 行 235",
 "owner rows 235", "243 行单态", "全二百四十三行", "二百四十三面", "bma rows 127",
 "bma_rows=127", "live rows 127 实读", "engine_owner==bm-a 127 行",
 "probe leg0 机证 243 行", "probe leg0 实测 243 行", "第 129 枚", "第 245 枚", "第二百四十",
 "TWO HUNDRED AND FORTY", "128th", "129th", "engine_owner==bm-a rows 127",
 # seed-gap
 "连续第八个 seed-gap face", "连续第九个",
 # seat / window
 "MSG-20261015-1328", "785936d84", "own-seat continuity lane", "own-seat continuity 承接",
 "bm-a r1015 席·own-seat continuity 承接", "bm-a r1015 席位", "r1015 窗算法",
 "r1015 席位窗实跑", "saturation_engine.py status live-read r1016",
 "bm-a 循环班 r1016 freeze 窗 2026-10-15 14:1x", "本窗 free RAM ~47.1GB",
 "r1018", "r1017", "e06f4ee2a", "650953086", "MSG-20261015-1608",
 # blocks
 "DOUBLE-CLEAN", "B_double_clean_expected_face", "staircase band-hop face 首披露",
 "LIVE-SEED-REFUSAL",
 # freeze-prep same-form line full face
 "r1015/W245",
 # fivekeys file name
 "_r1017bma_w246_fivekeys", "_w246bma_20261015_probe_receipt",
 # parity block tails
 "W235..W245 leg（11 行）构成 W246 块 parity 104 行", "W138..W206+W211",
]
for p in pats:
    print(t.count(p), "|", p)
