# -*- coding: utf-8 -*-
# r1056 bm-c: W255 prereg derive needle-count pre-flight probe (floors must be machine-counted
# against the frozen W254 template face results/_w255bmc_w254_frozen_face.txt, zero transcription).
import io, hashlib, re

SRC = r"results\_w255bmc_w254_frozen_face.txt"
T0 = io.open(SRC, encoding="utf-8", newline="").read()
assert hashlib.sha256(T0.encode("utf-8")).hexdigest()[:16] == "739ecd0d541995ec", "SRC sha mismatch"

NEEDLES = [
    # projection / K / ledger faces
    "556,720 投影", "line_merged@K554,520 **1.1944**", "554,520", "556,720",
    "980,935", "978,735", "983,135", "n_eff_held_equal 978,735",
    # measured keys
    "−0.09273893", "−0.0925495", "0.24504775", "实差 0.0002 在带内", "（**0.3122** 实测锚）",
    "键 W253 实测 K-lift **0.0000**", "line_pre_w253 1.1944",
    "→W249 **0.000332**→W250 **0.000331**→W251 **0.000330**→W252 **0.000330**→W253 **0.000329**】",
    # band faces
    "A-ext seed=574_101..576_100", "entry rng seed=**574_101+j**", "entry rng=**574_101+j**",
    "exit rng=**576_101+j**", "A base=574101 span=2000 checked=2000 verdict=FREE",
    "B base=576101 span=200 checked=200 verdict=FREE", "R255：W254",
    "574_100+1", "576_100+1", "574_101..574_300", "573_901..575_900", "571_901..572_100",
    # seat / provenance
    "MSG-20261016-14xx-bmc-w254-seat", "fa70f3765", "cb79242ed",
    "（bm-c r1053 席·queue-head FREEZE-UNBLOCKED 发布）", "（bm-c r1053 席位", "（r1053 席位窗实跑",
    "bm-c r1053 窗 14:4x", "14:4x", "已落账键·14:4x",
    # live/read faces
    "saturation_engine.py status live-read r1054", "本窗 free RAM ~2.7GB（",
    "§5.5 W255+ 投影承接机证", "本波上游链=W1..W253 finalize 全落地",
    # wave rolls
    "W254", "W253", "W252", "W255", "n1_w254", "n1_w253", "n1_w255",
    "_w254bmc", "_w253bmc", "_w255bmc", "--wave 254", "波号 254", "--wave 255",
    # ordinals
    "第 252 枚", "第 244 波", "bm-c 第七十四枚自有波", "bmc rows 73+候选=第 74 枚 EXACT", "第 74 枚", "第 75 枚",
    "probe leg0 bmc_rows=73 attempt-continuity face（r1053 窗算法·bm-c own seat+bmc live rows 73 实读）",
    "engine_owner==bm-c 73 行注册", "engine_owner 行 243 注册在册",
    "全二百五十一行注册 N1 带表", "freeze 窗 live derive 251 行单态 owner rows 243",
    "probe leg0 机证 251 行〔", "席位窗 probe leg0 实测 251 行〔",
    "perpetual_faces.py 零 252 行", "共二百五十一面实测", "第 253 枚", "第 245 波",
    # block markers (W254-template forms)
    "（**A 面=STAIRCASE-AFFECTS-A", "已如实披露非分叉）",
    "法典 §4 W254 行 A=574_101..576_100", "法典 §4 W254 行 B=576_101..576_300",
    "披露收敛·ADMIT 回执在场）", "非转录 r587·ADMIT 回执在场）",
    "5. **W255+ 投影（probe 机证 leg4", "verify at W255 prereg，hop 链逐跳在 probe 回执。",
    "·probe W255+ 投影 A naive 576_101..578_100 CLEAN hops=0", "never transcribe r587**）",
    "·W254 冻结窗 2.7G bm-c 实锚", "·W250 冻结窗 RAM 未记录（r1046 死窗",
    "W240 冻结窗 33.2G bm-a 实锚）",
    "selftest W254 face（", "零假设零风险。",
    "+W246=bm-a r1016 prereg derive", "——本波上游链=", "W255 freezer 承接面）】。",
    "W243/W246/W248/W249/W250/W251/W252/W253 低 RAM 实烧先例",
    "r1052/W253 先例 freeze-prep 同式",
    "bm-c 循环班 r1054 freeze 窗",
    "W239..W253 leg（15 行）构成 W254 块 parity 112 行",
    "bm-c r1053 W253 §7 范式", "bm-c r1053 W253 §8 范式",
    "W253 块的自有 W239..W252 legs（14 行）",
    "第四次连续", "第四次连续 A-hop", "第四次连续 above-own-A", "第五次连续",
    "hops=1", "W254+ 投影", "W255+ 投影",
    # zero-floor candidates (W255's own values must be absent from template)
    "578_301", "578_300", "576_301..578_300", "578_301..578_500",
    "578_501..578_700", "578_301..580_300", "0.3092", "558,920", "985,335",
    "−0.09273764", "−0.09241377", "0.24503097", "0.000328",
    "R256：W255",
]

for n in NEEDLES:
    print("%d\t%s" % (T0.count(n), n))

print("--- RAM ledger lines (冻结窗 occurrences) ---")
for m in re.finditer(r"·W\d+ 冻结窗[^·]*", T0):
    print(repr(m.group(0)[:60]))
print("--- freeze stamp lines ---")
for m in re.finditer(r"bm-c 循环班 r\d+ freeze 窗[^\n]{0,30}", T0):
    print(repr(m.group(0)))
print("--- K-lift phrasing ---")
for m in re.finditer(r"键 W2\d+ 实测 K-lift[^\n]{0,20}", T0):
    print(repr(m.group(0)))
print("--- 实差 phrasing ---")
for m in re.finditer(r"实差[^\n]{0,25}", T0):
    print(repr(m.group(0)))
print("--- b1 tail head/tail markers ---")
i = T0.find("+W246=bm-a r1016 prereg derive")
print("b1 head found at", i)
j = T0.find("——本波上游链=")
print("upstream-chain marker at", j)
k = T0.find("W255 freezer 承接面）】。")
print("b1 end marker at", k)
print("HIST_B1 len would be", j - i)
print("--- in-band phrasing near K-lift ---")
for m in re.finditer(r"K-lift[^\n]{0,40}", T0):
    print(repr(m.group(0)[:70]))
