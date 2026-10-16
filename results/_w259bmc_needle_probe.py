# -*- coding: utf-8 -*-
# r1063 bm-c: W259 prereg needle-count pre-flight probe (canon-clone of _w258bmc_needle_probe.py per age() machine-needle law).
# Measures every candidate needle face on T0 = the FROZEN W258 prereg face (blob f3dce7a1f073f0c7903f42d31097a07395911f12
# @ freeze commit 824b46d31, sha256_16 f412a772695ec76e, 44,096 bytes -- PRE-BACKFILL face; the sec.7/8-backfilled
# HEAD twin 3eaccd1dada01f4ceff017953fafef15ea0555b4 disclosed, NOT used per r1052/r1049 precedent law).
# Output: results/_w259bmc_needle_counts.txt (one "count<TAB>needle" per line). ALL VMAP_FLOORS entries in the derive
# script must equal these measured counts (zero-floors asserted ==0). Zero transcription.
import io

SRC = "results/_w259bmc_w258_frozen_face.txt"
OUT = "results/_w259bmc_needle_counts.txt"
T0 = io.open(SRC, encoding="utf-8", newline="").read()

NEEDLES = [
    # ---- pre-chain VMAP needles (W258-face forms) ----
    "565,520 投影", "line_merged@K563,320 **1.1947**", "563,320", "561,120", "565,520", "567,720",
    "989,735", "987,535", "985,335", "983,135", "991,935", "994,135",
    "−0.09275554", "−0.10688227", "0.24502959", "实差 0.0141 在带内", "（**0.2973** 实测锚）",
    "−0.09276683", "−0.09565814", "0.24503366", "实差 0.0029 在带内", "（**0.3108** 实测锚）",
    "−0.09270015", "0.24503835", "−0.090659", "**0.3107**", "实差 0.0020 在带内",
    "A-ext seed=582_901..584_900", "entry rng seed=**582_901+j**", "entry rng=**582_901+j**",
    "exit rng=**584_901+j**",
    "A-ext seed=585_101..587_100", "entry rng=**585_101+j**", "exit rng=**587_101+j**",
    "A base=582901 span=2000 checked=2000 verdict=FREE", "B base=584901 span=200 checked=200 verdict=FREE",
    "A base=585101 span=2000 checked=2000 verdict=FREE", "B base=587101 span=200 checked=200 verdict=FREE",
    "R259：W258", "R260：W259", "R258：W257",
    "582_900+1", "584_900+1", "585_100+1", "587_100+1",
    "MSG-20261017-0517-bmc-w258-seat", "MSG-20261017-0704-bmc-w259-seat", "27ee6e95a", "d0d0d04a4", "16dba0e70",
    "（bm-c r1060 席·queue-head FREEZE-UNBLOCKED 发布）", "（bm-c r1060 席位", "（r1060 席位窗实跑",
    "（bm-c r1062 席", "（r1062 席位窗实跑", "（bm-c r1062 席·queue-head FREEZE-UNBLOCKED 发布）",
    "bm-c r1060 窗 05:1x", "03:5x", "05:1x", "已落账键·05:1x", "07:0x", "bm-c r1062 窗 07:0x", "已落账键·07:0x",
    "saturation_engine.py status live-read r1061", "saturation_engine.py status live-read r1059",
    "saturation_engine.py status live-read r1063",
    "本窗 free RAM ~3.5GB（bm-c 底盘常驻·24G 物理内存机·LLM 态 27b 常驻+引擎队列空转·CPU 车道独立如实注记）",
    "本窗 free RAM ~4GB（bm-c 底盘常驻·24G 物理内存机·LLM 态 27b 常驻+引擎队列空转·CPU 车道独立如实注记）",
    # ---- roll labels ----
    "W259", "W258", "W257", "W256", "W255", "W254", "W253", "W252", "W251", "W250", "W260",
    "W243", "W246", "W248", "W249",
    # ---- result-file basenames ----
    "n1_w258", "n1_w257", "n1_w256", "n1_w255", "n1_w259", "n1_w254",
    # ---- script basenames ----
    "_w258bmc", "_w257bmc", "_w256bmc", "_w259bmc", "_w255bmc",
    "_w258bmc_20261017", "_w257bmc_20261017", "_w256bmc_20261017", "_w256bmc_20261016",
    # ---- runner CLI ----
    "--wave 258", "波号 258", "--wave 259", "波号 259", "--wave 257", "波号 257",
    # ---- ordinals ----
    "第 256 枚", "第 255 枚", "第 257 枚", "第 248 波", "第 247 波", "第 249 波",
    "bm-c 第七十八枚自有波", "bm-c 第七十九枚自有波", "bm-c 第七十七枚自有波",
    "bmc rows 77+候选=第 78 枚 EXACT", "bmc rows 78+候选=第 79 枚 EXACT", "bmc rows 76+候选=第 77 枚 EXACT",
    "第 78 枚", "第 77 枚", "第 79 枚", "第 76 枚",
    "probe leg0 bmc_rows=77 attempt-continuity face（r1060 窗算法·bm-c own seat+bmc live rows 77 实读）",
    "probe leg0 bmc_rows=78 attempt-continuity face（r1062 窗算法·bm-c own seat+bmc live rows 78 实读）",
    "probe leg0 bmc_rows=76 attempt-continuity face（r1058 窗算法·bm-c own seat+bmc live rows 76 实读）",
    "engine_owner==bm-c 77 行注册", "engine_owner==bm-c 78 行注册", "engine_owner==bm-c 76 行注册",
    "engine_owner 行 247 注册在册", "engine_owner 行 248 注册在册", "engine_owner 行 246 注册在册",
    # ---- registry scan faces ----
    "全二百五十五行注册 N1 带表", "全二百五十六行注册 N1 带表", "全二百五十四行注册 N1 带表",
    "freeze 窗 live derive 255 行单态 owner rows 247", "freeze 窗 live derive 256 行单态 owner rows 248",
    "freeze 窗 live derive 254 行单态 owner rows 246",
    "probe leg0 机证 255 行〔", "probe leg0 机证 256 行〔", "probe leg0 机证 254 行〔",
    "席位窗 probe leg0 实测 255 行〔", "席位窗 probe leg0 实测 256 行〔", "席位窗 probe leg0 实测 254 行〔",
    "perpetual_faces.py 零 256 行", "perpetual_faces.py 零 257 行", "perpetual_faces.py 零 255 行",
    "共二百五十五面实测", "共二百五十六面实测", "共二百五十四面实测",
    "表尾 W257 行", "表尾 W258 行", "表尾 W256 行",
    "pre-W258 全二百五十五行注册 N1 带表", "pre-W259 全二百五十六行注册 N1 带表",
    "pre-W257 全二百五十四行注册 N1 带表",
    # ---- §5.5 title ----
    "§5.5 W259+ 投影承接机证", "§5.5 W260+ 投影承接机证", "§5.5 W258+ 投影承接机证",
    # ---- post-leg needles (T0 true forms + rolled variants) ----
    "→W249 **0.000332**→W250 **0.000331**→W251 **0.000330**→W252 **0.000330**→W253 **0.000329**→W254 **0.000328**→W255 **0.000328**→W256 **0.000327**→W257 **0.000326】",
    "→W249 **0.000332**→W250 **0.000331**→W251 **0.000330**→W252 **0.000330**→W254 **0.000329**→W255 **0.000328**→W256 **0.000328**→W257 **0.000327】",
    "→W249 **0.000332**→W250 **0.000331**→W251 **0.000330**→W253 **0.000330**→W254 **0.000329**→W255 **0.000328**→W256 **0.000328**→W257 **0.000327】",
    "→W249 **0.000332**→W250 **0.000331**→W251 **0.000330**→W252 **0.000330**→W253 **0.000329**→W254 **0.000328**→W255 **0.000328**→W256 **0.000327】",
    "→W249 **0.000332**→W250 **0.000331**→W251 **0.000330**→W252 **0.000330**→W253 **0.000329**→W254 **0.000328**→W255 **0.000328**→W256 **0.000327**→W257 **0.000326】→W258 **0.000326】",
    "line_pre_w257 1.1948", "line_pre_w256 1.1947", "line_pre_w258 1.1948", "line_pre_w258",
    "键 W257 实测 K-lift **−0.0001**", "键 W256 实测 K-lift **0.0000**", "键 W258 实测 K-lift",
    "bm-c r1060 W257 §7 范式", "bm-c r1060 W257 §8 范式", "bm-c r1062 W258 §7 范式",
    "bm-c r1058 W256 §7 范式", "bm-c r1058 W256 §8 范式",
    "W243/W246/W248/W249/W250/W251/W252/W253/W254/W255/W256/W257 低 RAM 实烧先例",
    "W243/W246/W248/W249/W250/W251/W253/W254/W255/W256/W257 低 RAM 实烧先例",
    "W243/W246/W248/W249/W250/W251/W252/W253/W254/W255/W256/W257/W258 低 RAM 实烧先例",
    "W243/W246/W248/W249/W250/W251/W253/W254/W255/W256/W257/W258 低 RAM 实烧先例",
    "W243/W246/W248/W249/W250/W251/W252/W254/W255/W256/W257/W258 低 RAM 实烧先例",
    "r1059/W257 先例 freeze-prep 同式", "r1061/W258 先例 freeze-prep 同式", "r1058/W256 先例 freeze-prep 同式",
    "n_eff_held_equal 987,535", "n_eff_held_equal 989,735", "n_eff_held_equal 985,335",
    # ---- block markers (T0 forms) ----
    "（**A 面=STAIRCASE-AFFECTS-A", "已如实披露非分叉）",
    "法典 §4 W258 行 A=582_901..584_900", "法典 §4 W258 行 B=584_901..585_100",
    "法典 §4 W257 行 A=580_701..582_700", "法典 §4 W257 行 B=582_701..582_900",
    "披露收敛·ADMIT 回执在场）", "非转录 r587·ADMIT 回执在场）",
    "5. **W259+ 投影（probe 机证 leg4", "verify at W259 prereg，hop 链逐跳在 probe 回执。",
    "5. **W258+ 投影（probe 机证 leg4", "verify at W258 prereg，hop 链逐跳在 probe 回执。",
    "·probe W259+ 投影 A naive 584_901..586_900 CLEAN hops=0", "never transcribe r587**）",
    "·probe W258+ 投影 A naive 582_701..584_700 CLEAN hops=0",
    "·W258 冻结窗 3.5G bm-c 实锚", "·W259 冻结窗 3.5G bm-c 实锚",
    "·W257 冻结窗 4G bm-c 实锚", "·W256 冻结窗 3.3G", "·W255 冻结窗 2.0G",
    "·W250 冻结窗 RAM 未记录（r1046 死窗", "W240 冻结窗 33.2G bm-a 实锚）",
    "selftest W258 face（", "selftest W259 face（", "selftest W257 face（",
    "零假设零风险。", "+W246=bm-a r1016 prereg derive", "——本波上游链=",
    "W259 freezer 承接面）】。", "W258 freezer 承接面）】。", "W260 freezer 承接面）】。",
    "本波上游链=W1..W257 finalize 全落地", "本波上游链=W1..W258 finalize 全落地",
    "本波上游链=W1..W256 finalize 全落地",
    # ---- band windows ----
    "582_901..584_900", "584_901..585_100", "580_701..582_700", "582_701..582_900",
    "584_901..586_900", "585_101..585_300", "585_101..587_100", "587_101..587_300",
    "587_101..589_100", "587_301..587_500",
    "580_501..582_500", "580_701..580_900", "578_501..580_500", "580_501..580_700",
    "582_701..584_700", "582_901..583_100", "578_501..578_700", "578_301..580_300",
    "576_301..576_500", "576_101..578_100",
    "A-ext seed=582_901..584_900", "B-ext exit seed=584_901..585_100", "B-ext exit seed=582_701..582_900",
    "B-ext exit seed=587_101..587_300",
    # ---- hop-ordinal phrases ----
    "第七次连续 A-hop", "第八次连续 A-hop", "第九次连续 A-hop", "第六次连续 A-hop",
    "第七次连续", "第八次连续", "第九次连续", "第六次连续",
    "第七次连续 above-own-A", "第八次连续 above-own-A", "第九次连续 above-own-A", "第六次连续 above-own-A",
    "STAIRCASE-AFFECTS-A", "hops=1", "hops=0",
    "W252/W253/W254/W255/W256/W257=A/B 双 1-hop 形态连续六波",
    "W253/W254/W255/W256/W257/W258=A/B 双 1-hop 形态连续七波",
    "W251/W252/W253/W254/W255/W256=A/B 双 1-hop 形态连续六波",
    # ---- zero-floor faces (new-gen, expect 0) ----
    "waits-upstream ARMED", "（**B 面=CLEAN",
    "A_clean_at_naive_start=true", "A_staircase_hop_past_W257_B", "A_staircase_hop_past_W258_B",
    "W259p_B_lands_inside_W259p_A_naive", "W260p_B_lands_inside_W260p_A_naive", "W258p_B_lands_inside_W258p_A_naive",
    "W259 冻结方", "W260 冻结方", "W258 冻结方",
    "W259p_", "W260p_",
    # ---- chain sha16 receipts (W258-face expected) + new-gen zero candidates ----
    "d93e644b38fae882", "38da334ef0a033d2", "e37b483340aa67ba",
    "ad9776287dd52280", "986e9162b86e0c7f",
    "924e87b3f02afb72", "7b550e65716e0ada", "d4a9d7164ba9490e", "c6dfb4291c09be1e",
    "e166afc6c", "b1414b81a", "f931cf102", "72d292ea3",
    "550293d3f", "9b848c2e0", "370d6c81", "c7fbc443c", "5e88b3067",
    "e2c4b543e", "3eb691575", "fa2bc55e5", "c211d1269",
    "aa6102e35", "31c9e4872", "1c7112fd9", "5996e2c93",
    "dca9e66660f0c4ac", "381d26df7e6d6b7f", "37ccebffd", "122485949", "cc72046d7", "824b46d31",
    # ---- misc faces ----
    "（W138..W206+", "PERPETUAL-N1-W258", "PERPETUAL-N1-W259", "PERPETUAL-N1-W257",
    "zero post-splice heal", "queue-head FREEZE-UNBLOCKED lane", "queue-head FREEZE-UNBLOCKED 承接",
    "本候选=bm-c 自有席自有波",
    "bm-c 循环班 r1061 freeze 窗 2026-10-17", "bm-c 循环班 r1059 freeze 窗",
    "bm-c 循环班 r1063 freeze 窗",
    "W240..W257 leg（18 行）构成 W258 块 parity 116 行", "W240..W256 legs（17 行）",
    "W240..W258 leg（19 行）构成 W259 块 parity 117 行",
    "kept W211..W239 29", "dropped W240..W256 17", "fresh W240..W257 18",
    "kept W211..W240 30", "dropped W241..W257 17", "fresh W241..W258 18",
    "239->240", "240->241", "238->239",
    "n1_w258_results.json", "n1_w259_results.json",
    "queue-head FREEZE-UNBLOCKED lane", "seed_admit_gate rc0 双带 FREE",
    "556,720 合并池", "累计 null 池=556,720", "563,320 合并池", "565,520 合并池",
]

rows = []
for n in NEEDLES:
    rows.append("%d\t%s" % (T0.count(n), n))
io.open(OUT, "w", encoding="utf-8", newline="").write("\n".join(rows) + "\n")
print("needle probe: counted %d faces -> %s" % (len(NEEDLES), OUT))

# context prints for authoring (exact live forms, zero transcription by the derive author)
import re
def ctx(pat, label, maxhits=4):
    hits = [m.start() for m in re.finditer(re.escape(pat), T0)]
    print("[%s] %d hits" % (label, len(hits)))
    for h in hits[:maxhits]:
        seg = T0[max(0, h - 120): h + 260]
        print("  >>> " + seg.replace("\n", "\\n")[:520])
ctx("低 RAM 实烧先例", "low-ram list")
ctx("0.000326】", "se_mu chain tail")
ctx("kept W211", "sec3 split kept")
ctx("dropped ", "sec3 split dropped")
ctx("fresh W", "sec3 split fresh")
ctx("·W258 冻结窗", "ram ledger head")
ctx("bm-c r1061 freeze 窗", "freeze-window stamp")
ctx("W259p_", "W259p face")
ctx("1. **W258 A naive**", "b5 item1")
ctx("W252/W253", "double-1hop family")
