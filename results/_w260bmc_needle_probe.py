# -*- coding: utf-8 -*-
# r1065 bm-c: W260 prereg derive NEEDLE PROBE (pre-flight count measurement on T0 = frozen W259 face).
# age() machine-needle law: every VMAP floor below is MEASURED on T0 by this probe -- zero hand-estimation.
# T0 = results/_w260bmc_w259_frozen_face.txt (blob b2a353f38 @ b709bc2cc, 45,806B, sha256_16 ca4805af49781954).
# Also SIMULATES the one-generation vmap chain to extract post-roll T1 forms for POST_LEG authoring.
import io, os, re, hashlib

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(REPO, "results", "_w260bmc_w259_frozen_face.txt")
T0 = io.open(SRC, encoding="utf-8", newline="").read()
assert hashlib.sha256(T0.encode("utf-8")).hexdigest()[:16] == "ca4805af49781954", "T0 sha mismatch"
print("T0 bytes:", len(T0.encode("utf-8")))

NEEDLES = [
    # projection / line_merged / prior-K / ledger heads
    "567,720 投影", "line_merged@K565,520 **1.1948**", "565,520", "565,520 合并池",
    "991,935", "989,735", "987,535", "985,335", "983,135", "561,120", "563,320", "567,720", "569,920", "994,135", "996,335",
    # sec5 measured keys (W258 actuals in T0)
    "−0.09276683", "−0.09565814", "0.24503366", "实差 0.0029 在带内", "（**0.3108** 实测锚）",
    "−0.09273526", "0.24503750", "−0.08462", "实差 0.0081 在带内", "（**0.3234** 实测锚）", "0.3234", "0.000325",
    # band faces
    "A-ext seed=585_101..587_100", "entry rng seed=**585_101+j**", "entry rng=**585_101+j**",
    "exit rng=**587_101+j**", "A base=585101 span=2000 checked=2000 verdict=FREE",
    "B base=587101 span=200 checked=200 verdict=FREE",
    "A base=587301 span=2000 checked=2000 verdict=FREE", "B base=589301 span=200 checked=200 verdict=FREE",
    "R260：W259", "R261：W260",
    "585_100+1", "587_100+1", "587_300+1", "589_300+1",
    "587_301..589_300", "589_301..589_500", "587_101..589_100", "587_301..587_500",
    "585_101..587_100", "587_101..587_300", "585_101..585_300", "584_901..586_900",
    "589_301..591_300", "589_501..589_700", "589_301..589_500",
    # seat / provenance
    "MSG-20261017-0704-bmc-w259-seat", "MSG-20261017-0910-bmc-w260-seat", "16dba0e70", "9fa2c8aed",
    "（bm-c r1062 席·queue-head FREEZE-UNBLOCKED 发布）", "（bm-c r1062 席位", "（r1062 席位窗实跑",
    "（bm-c r1064 席", "（r1064 席位窗实跑",
    # finalize window narrowed legs
    "bm-c r1062 窗 07:0x", "已落账键·07:0x finalize one-pass", "已落账键·07:0x", "05:1x", "07:0x", "08:5x",
    # engine live-read + RAM
    "saturation_engine.py status live-read r1063", "saturation_engine.py status live-read r1065",
    "本窗 free RAM ~1.3GB（bm-c 底盘常驻·24G 物理内存机·LLM 态 27b 常驻+引擎队列空转·CPU 车道独立如实注记）",
    "本窗 free RAM ~2GB（bm-c 底盘常驻",
    # wave tokens
    "W259", "W258", "W257", "W256", "W255", "W254", "W253", "W252", "W251", "W250", "W260", "W261",
    # result files
    "n1_w259", "n1_w258", "n1_w257", "n1_w256", "n1_w260",
    # script basenames
    "_w259bmc", "_w258bmc", "_w257bmc", "_w256bmc", "_w260bmc", "_w259bmc_20261017", "_w258bmc_20261017",
    # runner CLI
    "--wave 259", "波号 259", "--wave 260", "波号 260",
    # ordinals
    "第 256 枚", "第 257 枚", "第 258 枚", "第 248 波", "第 249 波", "第 250 波",
    "bm-c 第七十八枚自有波", "bm-c 第七十九枚自有波", "bm-c 第八十枚自有波",
    "bmc rows 77+候选=第 78 枚 EXACT", "bmc rows 78+候选=第 79 枚 EXACT", "bmc rows 79+候选=第 80 枚 EXACT",
    "第 78 枚", "第 79 枚", "第 80 枚", "第 77 枚",
    "probe leg0 bmc_rows=77", "probe leg0 bmc_rows=78", "probe leg0 bmc_rows=79",
    "engine_owner==bm-c 77 行注册", "engine_owner==bm-c 78 行注册", "engine_owner==bm-c 79 行注册",
    "engine_owner 行 247 注册在册", "engine_owner 行 248 注册在册", "engine_owner 行 249 注册在册",
    # registry scan faces
    "全二百五十六行注册 N1 带表", "全二百五十七行注册 N1 带表",
    "freeze 窗 live derive 256 行单态 owner rows 248", "freeze 窗 live derive 257 行单态 owner rows 249",
    "probe leg0 机证 256 行〔", "probe leg0 机证 257 行〔",
    "席位窗 probe leg0 实测 256 行〔", "席位窗 probe leg0 实测 257 行〔",
    "perpetual_faces.py 零 256 行", "perpetual_faces.py 零 257 行",
    "共二百五十六面实测", "共二百五十七面实测",
    "pre-W259 全二百五十六行注册", "pre-W260 全二百五十七行注册",
    "表尾 W258 行", "表尾 W259 行",
    # sec8 projection label
    "§5.5 W260+ 投影承接机证", "§5.5 W261+ 投影承接机证",
    # block markers (T0 faces)
    "（**A 面=STAIRCASE-AFFECTS-A", "已如实披露非分叉）",
    "法典 §4 W259 行 A=585_101..587_100", "法典 §4 W259 行 B=587_101..587_300",
    "法典 §4 W260 行 A=585_101..587_100", "法典 §4 W260 行 B=587_101..587_300",
    "非转录 r587·ADMIT 回执在场）", "披露收敛·ADMIT 回执在场）",
    "5. **W260+ 投影（probe 机证 leg4", "verify at W260 prereg，hop 链逐跳在 probe 回执。",
    "·probe W260+ 投影 A naive 587_101..589_100 CLEAN hops=0", "never transcribe r587**）",
    "·W259 冻结窗 1.3G bm-c 实锚", "W240 冻结窗 33.2G bm-a 实锚）",
    "selftest W259 face（", "零假设零风险。",
    "+W246=bm-a r1016 prereg derive", "——本波上游链=", "W260 freezer 承接面）】。",
    "W241..W258 leg（18 行）构成 W259 块 parity 117 行", "W240..W257 leg（18 行）构成 W258 块 parity 116 行",
    "W243/W246/W248/W249/W250/W251/W252/W253/W254/W255/W256/W257/W258 低 RAM 实烧先例",
    "W243/W246/W248/W249/W250/W251/W252/W253/W255/W256/W257/W258/W259 低 RAM 实烧先例",
    "第 255 枚", "第 247 波",
    # staircase ordinal faces
    "第八次连续 A-hop", "第九次连续 A-hop", "第九次连续 above-own-A", "第八次连续 above-own-A",
    "第十次连续 A-hop", "第十次连续 above-own-A", "第七次连续", "第八次连续", "第九次连续", "第十次连续",
    "STAIRCASE-AFFECTS-A", "hops=1", "hops=0",
    # se_mu chain
    "→W249 **0.000332**→W250 **0.000331**→W251 **0.000330**→W252 **0.000330**→W253 **0.000329**→W254 **0.000328**→W255 **0.000328**→W256 **0.000327**→W257 **0.000326**→W258 **0.000326**】",
    "→W249 **0.000332**→W250 **0.000331**→W251 **0.000330**→W252 **0.000330**→W253 **0.000329**→W255 **0.000328**→W256 **0.000328**→W257 **0.000327**→W258 **0.000326**→W259 **0.000326**】",
    # post-leg family needles
    "line_pre_w258 1.1948", "line_pre_w259 1.1949", "line_pre_w259", "line_pre_w258",
    "键 W258 实测 K-lift **0.0000**", "键 W259 实测 K-lift",
    "bm-c r1062 W258 §7 范式", "bm-c r1062 W258 §8 范式", "bm-c r1064 W259 §7 范式",
    "r1061/W258 先例 freeze-prep 同式", "r1061/W259 先例 freeze-prep 同式", "r1063/W259 先例 freeze-prep 同式",
    "W252/W253/W254/W255/W256/W257/W258/W259=A/B 双 1-hop 形态连续八波",
    "W253/W254/W255/W256/W257/W258/W259/W260=A/B 双 1-hop 形态连续九波",
    "W251 起 staircase affects A", "n_eff_held_equal 989,735", "n_eff_held_equal 991,935",
    "W260p_B_lands_inside_W260p_A_naive", "W261p_B_lands_inside_W261p_A_naive",
    "queue-head FREEZE-UNBLOCKED lane", "queue-head FREEZE-UNBLOCKED 承接",
    "本候选=bm-c 自有席自有波", "seed_admit_gate rc0 双带 FREE",
    "zero post-splice heal", "（W138..W206+",
    "PERPETUAL-N1-W259", "PERPETUAL-N1-W260", "567,720 合并池", "563,320 合并池",
    "bm-c 循环班 r1063 freeze 窗 2026-10-17", "bm-c 循环班 r1064 freeze 窗", "bm-c 循环班 r1065 freeze 窗",
    # W259 chain commit faces (T0 b1 tail content)
    "89aeea31b", "b709bc2cc", "85e44f6a6", "778bd1c04", "ceeb47cda", "e166afc6c",
    "9fa2c8aed", "dca9e66660f0c4ac", "bfd877ee61d6b456", "57a139af18df580d", "381d26df7e6d6b7f",
    "37ccebffd", "122485949", "cc72046d7", "824b46d31", "d0d0d04a4",
    "fivekeys 6/6", "sixgate PRE-FINALIZE 20th consecutive", "sixgate PRE-FINALIZE 21st consecutive",
    "waits-upstream ARMED", "（**B 面=CLEAN",
    "selftest W260 face", "W260 冻结方", "W261p_", "W260p_",
    "A_staircase_hop_past_W258_B", "A_staircase_hop_past_W259_B",
    "A_clean_at_naive_start=true", "A_clean_at_naive_start=false",
    "已落账键·05:1x", "n1_w259_results.json", "n1_w260_results.json",
]
counts = {}
for n in NEEDLES:
    counts[n] = T0.count(n)
for n in sorted(counts, key=lambda x: (-counts[x], x)):
    print("%d\t%r" % (counts[n], n))

# ---- simulate the W260 vmap chain to extract post-roll T1 forms for POST_LEG authoring ----
P1, P2, P3 = "\x01W\x01", "\x01N\x01", "\x01B\x01"
VMAP = [
    ("567,720 投影", "569,920 投影"),
    ("line_merged@K565,520 **1.1948**", "line_merged@K567,720 **1.1949**"),
    ("565,520", "567,720"),
    ("991,935", "994,135"),
    ("989,735", "991,935"),
    ("−0.09276683", "−0.09273526"),
    ("−0.09565814", "−0.08462"),
    ("0.24503366", "0.24503750"),
    ("实差 0.0029 在带内", "实差 0.0081 在带内"),
    ("（**0.3108** 实测锚）", "（**0.3234** 实测锚）"),
    ("A-ext seed=585_101..587_100", "A-ext seed=587_301..589_300"),
    ("entry rng seed=**585_101+j**", "entry rng seed=**587_301+j**"),
    ("entry rng=**585_101+j**", "entry rng=**587_301+j**"),
    ("exit rng=**587_101+j**", "exit rng=**589_301+j**"),
    ("A base=585101 span=2000 checked=2000 verdict=FREE", "A base=587301 span=2000 checked=2000 verdict=FREE"),
    ("B base=587101 span=200 checked=200 verdict=FREE", "B base=589301 span=200 checked=200 verdict=FREE"),
    ("R260：W259", "R261：W260"),
    ("585_100+1", "587_300+1"),
    ("587_100+1", "589_300+1"),
    ("MSG-20261017-0704-bmc-w259-seat", "MSG-20261017-0910-bmc-w260-seat"),
    ("16dba0e70", "9fa2c8aed"),
    ("（bm-c r1062 席·queue-head FREEZE-UNBLOCKED 发布）", "（bm-c r1064 席·queue-head FREEZE-UNBLOCKED 发布）"),
    ("（bm-c r1062 席位", "（bm-c r1064 席位"),
    ("（r1062 席位窗实跑", "（r1064 席位窗实跑"),
    ("bm-c r1062 窗 07:0x", "bm-c r1064 窗 08:5x"),
    ("已落账键·07:0x finalize one-pass", "已落账键·08:5x finalize one-pass"),
    ("已落账键·07:0x", "已落账键·08:5x"),
    ("saturation_engine.py status live-read r1063", "saturation_engine.py status live-read r1065"),
    ("本窗 free RAM ~1.3GB（bm-c 底盘常驻·24G 物理内存机·LLM 态 27b 常驻+引擎队列空转·CPU 车道独立如实注记）",
     "本窗 free RAM ~RAMFACEGB（bm-c 底盘常驻·24G 物理内存机·LLM 态 27b 常驻+引擎队列空转·CPU 车道独立如实注记）"),
    ("W259", P1), ("W258", "W259"), ("W257", "W258"), ("W256", "W257"), ("W255", "W256"), ("W254", "W255"), (P1, "W260"),
    ("n1_w259", P2), ("n1_w258", "n1_w259"), ("n1_w257", "n1_w258"), (P2, "n1_w260"),
    ("_w259bmc", P3), ("_w258bmc", "_w259bmc"), ("_w257bmc", "_w258bmc"), (P3, "_w260bmc"),
    ("--wave 259", "--wave 260"),
    ("波号 259", "波号 260"),
    ("第 257 枚", "第 258 枚"),
    ("第 249 波", "第 250 波"),
    ("bm-c 第七十九枚自有波", "bm-c 第八十枚自有波"),
    ("bmc rows 78+候选=第 79 枚 EXACT", "bmc rows 79+候选=第 80 枚 EXACT"),
    ("第 79 枚", "第 80 枚"),
    ("probe leg0 bmc_rows=78 attempt-continuity face（r1062 窗算法·bm-c own seat+bmc live rows 78 实读）",
     "probe leg0 bmc_rows=79 attempt-continuity face（r1064 窗算法·bm-c own seat+bmc live rows 79 实读）"),
    ("engine_owner==bm-c 78 行注册", "engine_owner==bm-c 79 行注册"),
    ("engine_owner 行 248 注册在册", "engine_owner 行 249 注册在册"),
    ("全二百五十六行注册 N1 带表", "全二百五十七行注册 N1 带表"),
    ("freeze 窗 live derive 256 行单态 owner rows 248", "freeze 窗 live derive 257 行单态 owner rows 249"),
    ("probe leg0 机证 256 行〔", "probe leg0 机证 257 行〔"),
    ("席位窗 probe leg0 实测 256 行〔", "席位窗 probe leg0 实测 257 行〔"),
    ("perpetual_faces.py 零 256 行", "perpetual_faces.py 零 257 行"),
    ("共二百五十六面实测", "共二百五十七面实测"),
    ("§5.5 W260+ 投影承接机证", "§5.5 W261+ 投影承接机证"),
]
T1 = T0
for o, n in VMAP:
    T1 = T1.replace(o, n)
print("\n==== SIMULATED T1 post-roll forms for POST_LEG authoring ====")
# se_mu chain post-roll form
m = re.search(r"→W249 \*\*0\.000332\*\*[^】]*】", T1)
print("se_mu chain post-roll:", m.group(0) if m else "NOT FOUND")
# low-RAM list post-roll
m2 = re.search(r"W243/W246/W248/W249/W250/W251/W252/[^低]*?低 RAM 实烧先例", T1)
print("low-RAM list post-roll:", m2.group(0) if m2 else "NOT FOUND")
# K-lift face post-roll
m3 = re.search(r"键 W\d+ 实测 K-lift \*\*[^*]*\*\*", T1)
print("K-lift face post-roll:", m3.group(0) if m3 else "NOT FOUND")
# line_pre face post-roll
m4 = re.findall(r"line_pre_w\d+ [0-9.]+", T1)
print("line_pre faces post-roll:", m4)
# sec7/8 paradigm rows post-roll
m5 = re.findall(r"bm-c r\d+ W\d+ §[78] 范式", T1)
print("sec7/8 paradigm faces post-roll:", m5)
# freeze-prep precedent post-roll
m6 = re.findall(r"r\d+/W\d+ 先例 freeze-prep 同式", T1)
print("freeze-prep faces post-roll:", m6)
# freeze-window stamp post-roll
m7 = re.findall(r"bm-c 循环班 r\d+ freeze 窗 2026-10-1\d \d{2}:\dx", T1)
print("freeze-window stamps post-roll:", m7)
# block markers post-roll
for mk in ["法典 §4 W260 行 A=585_101..587_100", "法典 §4 W260 行 B=587_101..587_300",
           "（**A 面=STAIRCASE-AFFECTS-A", "已如实披露非分叉）", "5. **W261+ 投影（probe 机证 leg4",
           "verify at W261 prereg，hop 链逐跳在 probe 回执。", "selftest W260 face（", "零假设零风险。",
           "+W246=bm-a r1016 prereg derive", "W261 freezer 承接面）】。",
           "·probe W261+ 投影 A naive 589_301..591_300 CLEAN hops=0", "never transcribe r587**）",
           "·W260 冻结窗 1.3G bm-c 实锚", "W240 冻结窗 33.2G bm-a 实锚）"]:
    print("marker %r -> %d" % (mk, T1.count(mk)))
# ordinal + staircase faces post-roll
for f in ["第九次连续 A-hop", "第十次连续 A-hop", "第十次连续 above-own-A", "第九次连续 above-own-A",
          "W252/W253/W254/W255/W256/W257/W258/W259=A/B 双 1-hop 形态连续八波",
          "W253/W254/W255/W256/W257/W258/W259/W260=A/B 双 1-hop 形态连续九波",
          "n_eff_held_equal 989,735", "n_eff_held_equal 991,935",
          "W261p_B_lands_inside_W261p_A_naive", "W260p_B_lands_inside_W260p_A_naive",
          "567,720 合并池", "994,135", "569,920", "567,720 投影", "569,920 投影"]:
    print("post-roll face %r -> %d" % (f, T1.count(f)))
print("\nSIMULATION DONE (T1 not written to disk - authoring aid only)")
