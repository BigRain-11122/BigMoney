# -*- coding: utf-8 -*-
# r1066 bm-c: W261 prereg derive NEEDLE PROBE (pre-flight count measurement on T0 = frozen W260 face).
# age() machine-needle law: every VMAP floor below is MEASURED on T0 by this probe -- zero hand-estimation.
# T0 = results/_w261bmc_w260_frozen_face.txt (blob a7d34500ae5a3b3cd6a983f03c7dd32455598649 @ 0f33f9abc,
# 47,643 bytes, sha256_16 87a4c206a35e0584 -- the frozen pre-run face; sec7/8 placeholders intact).
# HEAD twin 4c684526295124ab72a51ab99bec377e51278508 = POST-BACKFILL face (r1065 closeout window), NOT used.
# Also SIMULATES the one-generation vmap chain to extract post-roll T1 forms for POST_LEG authoring.
import io, os, re, hashlib

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(REPO, "results", "_w261bmc_w260_frozen_face.txt")
T0 = io.open(SRC, encoding="utf-8", newline="").read()
assert hashlib.sha256(T0.encode("utf-8")).hexdigest()[:16] == "87a4c206a35e0584", "T0 sha mismatch"
print("T0 bytes:", len(T0.encode("utf-8")))

NEEDLES = [
    # projection / line_merged / prior-K / ledger heads
    "569,920 投影", "572,120 投影", "line_merged@K567,720 **1.1949**", "line_merged@K569,920 **1.195**",
    "567,720", "569,920", "567,720 合并池", "569,920 合并池", "565,520",
    "994,135", "991,935", "989,735", "987,535", "985,335", "983,135", "561,120", "563,320", "996,335", "998,535",
    "n_eff_held_equal 989,735", "n_eff_held_equal 991,935", "n_eff_held_equal 994,135", "n_eff_held_equal 996,335",
    # sec5 measured keys (W259 actuals in T0; W260 actuals zero-check)
    "−0.09273526", "−0.08462", "0.24503750", "实差 0.0081 在带内", "（**0.3234** 实测锚）",
    "−0.09273073", "0.24503935", "−0.09156055", "实差 0.0012 在带内", "（**0.3292** 实测锚）",
    "0.3292", "0.000325", "line_pre_w259 1.1949", "line_pre_w260 1.195", "line_pre_w259", "line_pre_w260",
    # band faces
    "A-ext seed=587_301..589_300", "entry rng seed=**587_301+j**", "entry rng=**587_301+j**",
    "exit rng=**589_301+j**", "A base=587301 span=2000 checked=2000 verdict=FREE",
    "B base=589301 span=200 checked=200 verdict=FREE",
    "A base=589501 span=2000 checked=2000 verdict=FREE", "B base=591501 span=200 checked=200 verdict=FREE",
    "R261：W260", "R262：W261",
    "587_300+1", "589_300+1", "589_500+1", "591_500+1",
    "587_301..589_300", "589_301..589_500", "589_301..591_300", "589_501..589_700",
    "589_501..591_500", "591_501..591_700", "591_501..593_500", "591_701..591_900",
    "585_101..587_100", "587_101..587_300", "585_101..585_300", "584_901..586_900",
    # seat / provenance
    "MSG-20261017-0910-bmc-w260-seat", "MSG-20261017-1225-bmc-w261-seat", "9fa2c8aed", "cf23c4553",
    "（bm-c r1064 席·queue-head FREEZE-UNBLOCKED 发布）", "（bm-c r1064 席位", "（r1064 席位窗实跑",
    "（bm-c r1065 席", "（r1065 席位窗实跑",
    # finalize window narrowed legs
    "bm-c r1064 窗 08:5x", "已落账键·08:5x finalize one-pass", "已落账键·08:5x", "05:1x", "07:0x", "08:5x", "12:1x",
    # engine live-read + RAM
    "saturation_engine.py status live-read r1065", "saturation_engine.py status live-read r1066",
    "本窗 free RAM ~2GB（bm-c 底盘常驻·24G 物理内存机·LLM 态 27b 常驻+引擎队列空转·CPU 车道独立如实注记）",
    "本窗 free RAM ~11GB",
    # wave tokens
    "W261", "W260", "W259", "W258", "W257", "W256", "W255", "W254", "W253", "W252", "W251", "W250", "W262",
    # result files
    "n1_w260", "n1_w259", "n1_w258", "n1_w257", "n1_w261",
    # script basenames
    "_w260bmc", "_w259bmc", "_w258bmc", "_w257bmc", "_w261bmc", "_w260bmc_20261017", "_w259bmc_20261017",
    # runner CLI
    "--wave 260", "波号 260", "--wave 261", "波号 261",
    # ordinals
    "第 257 枚", "第 258 枚", "第 259 枚", "第 249 波", "第 250 波", "第 251 波",
    "bm-c 第七十九枚自有波", "bm-c 第八十枚自有波", "bm-c 第八十一枚自有波",
    "bmc rows 78+候选=第 79 枚 EXACT", "bmc rows 79+候选=第 80 枚 EXACT", "bmc rows 80+候选=第 81 枚 EXACT",
    "第 79 枚", "第 80 枚", "第 81 枚",
    "probe leg0 bmc_rows=78", "probe leg0 bmc_rows=79", "probe leg0 bmc_rows=80",
    "engine_owner==bm-c 78 行注册", "engine_owner==bm-c 79 行注册", "engine_owner==bm-c 80 行注册",
    "engine_owner 行 248 注册在册", "engine_owner 行 249 注册在册", "engine_owner 行 250 注册在册",
    # registry scan faces
    "全二百五十六行注册 N1 带表", "全二百五十七行注册 N1 带表", "全二百五十八行注册 N1 带表",
    "freeze 窗 live derive 256 行单态 owner rows 248", "freeze 窗 live derive 257 行单态 owner rows 249",
    "freeze 窗 live derive 258 行单态 owner rows 250",
    "probe leg0 机证 256 行〔", "probe leg0 机证 257 行〔", "probe leg0 机证 258 行〔",
    "席位窗 probe leg0 实测 256 行〔", "席位窗 probe leg0 实测 257 行〔", "席位窗 probe leg0 实测 258 行〔",
    "perpetual_faces.py 零 257 行", "perpetual_faces.py 零 258 行", "perpetual_faces.py 零 259 行",
    "共二百五十六面实测", "共二百五十七面实测", "共二百五十八面实测",
    "pre-W259 全二百五十六行注册", "pre-W260 全二百五十七行注册", "pre-W261 全二百五十八行注册",
    "表尾 W258 行", "表尾 W259 行", "表尾 W260 行",
    # sec8 projection label
    "§5.5 W260+ 投影承接机证", "§5.5 W261+ 投影承接机证", "§5.5 W262+ 投影承接机证",
    # block markers (T0 faces + post-roll T1 faces)
    "（**A 面=STAIRCASE-AFFECTS-A", "已如实披露非分叉）",
    "法典 §4 W260 行 A=587_301..589_300", "法典 §4 W260 行 B=589_301..589_500",
    "法典 §4 W261 行 A=587_301..589_300", "法典 §4 W261 行 B=589_301..589_500",
    "非转录 r587·ADMIT 回执在场）", "披露收敛·ADMIT 回执在场）",
    "5. **W261+ 投影（probe 机证 leg4", "5. **W262+ 投影（probe 机证 leg4",
    "verify at W261 prereg，hop 链逐跳在 probe 回执。", "verify at W262 prereg，hop 链逐跳在 probe 回执。",
    "·probe W261+ 投影 A naive 589_301..591_300 CLEAN hops=0", "never transcribe r587**）",
    "·W260 冻结窗 2G bm-c 实锚", "·W261 冻结窗 2G bm-c 实锚", "W240 冻结窗 33.2G bm-a 实锚）",
    "·W250 冻结窗 RAM 未记录（r1046 死窗",
    "selftest W260 face（", "selftest W261 face（", "零假设零风险。",
    "+W246=bm-a r1016 prereg derive", "——本波上游链=", "W261 freezer 承接面）】。", "W262 freezer 承接面）】。",
    "W242..W259 leg（18 行）构成 W260 块 parity 118 行", "W243..W260 leg（18 行）构成 W261 块 parity 119 行",
    "W241..W258 leg（18 行）构成 W259 块 parity 117 行",
    "W243/W246/W248/W249/W250/W251/W252/W253/W254/W255/W256/W257/W258/W259 低 RAM 实烧先例",
    "W243/W246/W248/W249/W250/W251/W252/W253/W255/W256/W257/W258/W259/W260 低 RAM 实烧先例",
    "第 255 枚", "第 247 波",
    # staircase ordinal faces
    "第八次连续 A-hop", "第九次连续 A-hop", "第十次连续 A-hop", "第十一次连续 A-hop",
    "第九次连续 above-own-A", "第十次连续 above-own-A", "第十一次连续 above-own-A",
    "第七次连续", "第八次连续", "第九次连续", "第十次连续", "第十一次连续",
    "STAIRCASE-AFFECTS-A", "hops=1", "hops=0",
    # se_mu chain (T0 full form + post-roll predicted form)
    "→W249 **0.000332**→W250 **0.000331**→W251 **0.000330**→W252 **0.000330**→W253 **0.000329**→W254 **0.000328**→W255 **0.000328**→W256 **0.000327**→W257 **0.000326**→W258 **0.000326**→W259 **0.000325**】",
    "→W249 **0.000332**→W250 **0.000331**→W251 **0.000330**→W252 **0.000330**→W253 **0.000329**→W255 **0.000328**→W256 **0.000328**→W257 **0.000327**→W258 **0.000326**→W259 **0.000326**→W260 **0.000325**】",
    # post-leg family needles
    "键 W259 实测 K-lift **0.0000**", "键 W260 实测 K-lift", "键 W258 实测 K-lift",
    "bm-c r1064 W259 §7 范式", "bm-c r1064 W259 §8 范式", "bm-c r1065 W260 §7 范式",
    "r1063/W259 先例 freeze-prep 同式", "r1065/W260 先例 freeze-prep 同式",
    "W252/W253/W254/W255/W256/W257/W258/W259/W260=A/B 双 1-hop 形态连续九波",
    "W252/W253/W254/W255/W256/W257/W258/W259/W260/W261=A/B 双 1-hop 形态连续十波",
    "W251 起 staircase affects A",
    "W260p_B_lands_inside_W260p_A_naive", "W261p_B_lands_inside_W261p_A_naive", "W262p_B_lands_inside_W262p_A_naive",
    "queue-head FREEZE-UNBLOCKED lane", "queue-head FREEZE-UNBLOCKED 承接",
    "本候选=bm-c 自有席自有波", "seed_admit_gate rc0 双带 FREE",
    "zero post-splice heal", "fivekeys 6/6", "（W138..W206+",
    "PERPETUAL-N1-W260", "PERPETUAL-N1-W261",
    "bm-c 循环班 r1065 freeze 窗 2026-10-17", "bm-c 循环班 r1066 freeze 窗",
    # W260 chain commit faces (T0 b1 tail content)
    "0f33f9abc", "e8a9d5d67", "63ef15c4f", "9598cf5cb", "bfd877ee61d6b456", "31d5dc07baee6620",
    "57a139af18df580d", "f40a82c450f32c5a", "87a4c206a35e0584",
    "b709bc2cc", "89aeea31b", "b2a353f38", "9fa2c8aed", "cf23c4553",
    "sixgate PRE-FINALIZE 21st consecutive", "sixgate PRE-FINALIZE 22nd consecutive",
    "waits-upstream ARMED", "（**B 面=CLEAN",
    "W260 冻结方", "W262 冻结方", "W261p_", "W262p_",
    "A_staircase_hop_past_W259_B", "A_staircase_hop_past_W260_B",
    "A_clean_at_naive_start=true", "A_clean_at_naive_start=false",
    "已落账键·05:1x", "n1_w259_results.json", "n1_w260_results.json", "n1_w261_results.json",
    "W259=bm-c r1063 prereg derive", "W260=bm-c r1065 prereg derive",
    "r1064 finalize one-pass", "r1065 finalize one-pass",
    "本波上游链=W1..W259 finalize 全落地", "本波上游链=W1..W260 finalize 全落地",
    "K=567,720", "K=569,920", "K=572,120",
    "996,335", "572,120",
    "第 260 枚", "第 261 枚",
]
counts = {}
for n in NEEDLES:
    counts[n] = T0.count(n)
for n in sorted(counts, key=lambda x: (-counts[x], x)):
    print("%d\t%r" % (counts[n], n))

# ---- simulate the W261 vmap chain to extract post-roll T1 forms for POST_LEG authoring ----
P1, P2, P3 = "\x01W\x01", "\x01N\x01", "\x01B\x01"
VMAP = [
    ("569,920 投影", "572,120 投影"),
    ("line_merged@K567,720 **1.1949**", "line_merged@K569,920 **1.195**"),
    ("567,720", "569,920"),
    ("994,135", "996,335"),
    ("991,935", "994,135"),
    ("−0.09273526", "−0.09273073"),
    ("−0.08462", "−0.09156055"),
    ("0.24503750", "0.24503935"),
    ("实差 0.0081 在带内", "实差 0.0012 在带内"),
    ("（**0.3234** 实测锚）", "（**0.3292** 实测锚）"),
    ("A-ext seed=587_301..589_300", "A-ext seed=589_501..591_500"),
    ("entry rng seed=**587_301+j**", "entry rng seed=**589_501+j**"),
    ("entry rng=**587_301+j**", "entry rng=**589_501+j**"),
    ("exit rng=**589_301+j**", "exit rng=**591_501+j**"),
    ("A base=587301 span=2000 checked=2000 verdict=FREE", "A base=589501 span=2000 checked=2000 verdict=FREE"),
    ("B base=589301 span=200 checked=200 verdict=FREE", "B base=591501 span=200 checked=200 verdict=FREE"),
    ("R261：W260", "R262：W261"),
    ("587_300+1", "589_500+1"),
    ("589_300+1", "591_500+1"),
    ("MSG-20261017-0910-bmc-w260-seat", "MSG-20261017-1225-bmc-w261-seat"),
    ("9fa2c8aed", "cf23c4553"),
    ("（bm-c r1064 席·queue-head FREEZE-UNBLOCKED 发布）", "（bm-c r1065 席·queue-head FREEZE-UNBLOCKED 发布）"),
    ("（bm-c r1064 席位", "（bm-c r1065 席位"),
    ("（r1064 席位窗实跑", "（r1065 席位窗实跑"),
    ("bm-c r1064 窗 08:5x", "bm-c r1065 窗 12:1x"),
    ("已落账键·08:5x finalize one-pass", "已落账键·12:1x finalize one-pass"),
    ("已落账键·08:5x", "已落账键·12:1x"),
    ("saturation_engine.py status live-read r1065", "saturation_engine.py status live-read r1066"),
    ("本窗 free RAM ~2GB（bm-c 底盘常驻·24G 物理内存机·LLM 态 27b 常驻+引擎队列空转·CPU 车道独立如实注记）",
     "本窗 free RAM ~RAMFACEGB（bm-c 底盘常驻·24G 物理内存机·LLM 态已退役 gen 专用车道·引擎队列空转·CPU 车道独立如实注记）"),
    ("W260", P1), ("W259", "W260"), ("W258", "W259"), ("W257", "W258"), ("W256", "W257"), ("W255", "W256"), ("W254", "W255"), (P1, "W261"),
    ("n1_w260", P2), ("n1_w259", "n1_w260"), ("n1_w258", "n1_w259"), (P2, "n1_w261"),
    ("_w260bmc", P3), ("_w259bmc", "_w260bmc"), ("_w258bmc", "_w259bmc"), (P3, "_w261bmc"),
    ("--wave 260", "--wave 261"),
    ("波号 260", "波号 261"),
    ("第 258 枚", "第 259 枚"),
    ("第 250 波", "第 251 波"),
    ("bm-c 第八十枚自有波", "bm-c 第八十一枚自有波"),
    ("bmc rows 79+候选=第 80 枚 EXACT", "bmc rows 80+候选=第 81 枚 EXACT"),
    ("第 80 枚", "第 81 枚"),
    ("probe leg0 bmc_rows=79 attempt-continuity face（r1064 窗算法·bm-c own seat+bmc live rows 79 实读）",
     "probe leg0 bmc_rows=80 attempt-continuity face（r1065 窗算法·bm-c own seat+bmc live rows 80 实读）"),
    ("engine_owner==bm-c 79 行注册", "engine_owner==bm-c 80 行注册"),
    ("engine_owner 行 249 注册在册", "engine_owner 行 250 注册在册"),
    ("全二百五十七行注册 N1 带表", "全二百五十八行注册 N1 带表"),
    ("freeze 窗 live derive 257 行单态 owner rows 249", "freeze 窗 live derive 258 行单态 owner rows 250"),
    ("probe leg0 机证 257 行〔", "probe leg0 机证 258 行〔"),
    ("席位窗 probe leg0 实测 257 行〔", "席位窗 probe leg0 实测 258 行〔"),
    ("perpetual_faces.py 零 258 行", "perpetual_faces.py 零 259 行"),
    ("共二百五十七面实测", "共二百五十八面实测"),
    ("§5.5 W261+ 投影承接机证", "§5.5 W262+ 投影承接机证"),
]
T1 = T0
for o, n in VMAP:
    T1 = T1.replace(o, n)
print("\n==== SIMULATED T1 post-roll forms for POST_LEG authoring ====")
m = re.search(r"→W249 \*\*0\.000332\*\*[^】]*】", T1)
print("se_mu chain post-roll:", m.group(0) if m else "NOT FOUND")
m2 = re.search(r"W243/W246/W248/W249/W250/W251/W252/[^低]*?低 RAM 实烧先例", T1)
print("low-RAM list post-roll:", m2.group(0) if m2 else "NOT FOUND")
m3 = re.search(r"键 W\d+ 实测 K-lift \*\*[^*]*\*\*", T1)
print("K-lift face post-roll:", m3.group(0) if m3 else "NOT FOUND")
m4 = re.findall(r"line_pre_w\d+ [0-9.]+", T1)
print("line_pre faces post-roll:", m4)
m5 = re.findall(r"bm-c r\d+ W\d+ §[78] 范式", T1)
print("sec7/8 paradigm faces post-roll:", m5)
m6 = re.findall(r"r\d+/W\d+ 先例 freeze-prep 同式", T1)
print("freeze-prep faces post-roll:", m6)
m7 = re.findall(r"bm-c 循环班 r\d+ freeze 窗 2026-10-1\d \d{2}:\dx", T1)
print("freeze-window stamps post-roll:", m7)
for mk in ["法典 §4 W261 行 A=587_301..589_300", "法典 §4 W261 行 B=589_301..589_500",
           "（**A 面=STAIRCASE-AFFECTS-A", "已如实披露非分叉）", "5. **W262+ 投影（probe 机证 leg4",
           "verify at W262 prereg，hop 链逐跳在 probe 回执。", "selftest W261 face（", "零假设零风险。",
           "+W246=bm-a r1016 prereg derive", "W262 freezer 承接面）】。",
           "·probe W262+ 投影 A naive 591_501..593_500 CLEAN hops=0", "never transcribe r587**）",
           "·W261 冻结窗 2G bm-c 实锚", "W240 冻结窗 33.2G bm-a 实锚）",
           "W242..W260 leg（18 行）构成 W261 块 parity 119 行",
           "·W250 冻结窗 RAM 未记录（r1046 死窗"]:
    print("marker %r -> %d" % (mk, T1.count(mk)))
for f in ["第十次连续 A-hop", "第十一次连续 A-hop", "第十次连续 above-own-A", "第十一次连续 above-own-A",
          "第九次连续", "第十次连续", "第十一次连续",
          "W252/W253/W254/W255/W256/W257/W258/W259/W260=A/B 双 1-hop 形态连续九波",
          "n_eff_held_equal 994,135", "n_eff_held_equal 996,335",
          "W262p_B_lands_inside_W262p_A_naive", "W261p_B_lands_inside_W261p_A_naive",
          "569,920 合并池", "996,335", "572,120", "569,920 投影", "572,120 投影",
          "（**B 面=CLEAN", "waits-upstream ARMED"]:
    print("post-roll face %r -> %d" % (f, T1.count(f)))
print("\nSIMULATION DONE (T1 not written to disk - authoring aid only)")
