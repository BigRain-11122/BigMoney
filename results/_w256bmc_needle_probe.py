# -*- coding: utf-8 -*-
# r1058 bm-c: W256 prereg derive NEEDLE-COUNT PRE-FLIGHT PROBE (r1056 precedent law).
# Counts every candidate VMAP/FLOORS needle on the frozen W255 template face
# (results/_w256bmc_w255_frozen_face.txt, blob f353e49f3486957b1b274254f0c0368a51a5c2fc
# @ freeze commit 72d292ea3) so the derive script's floors can be authored from MEASURED
# counts, zero hand-derivation. Also dumps context windows for structural faces not yet
# read in full (带位 tail / vacancy face / §0 认领 / low-RAM line / freeze-window stamp).
import io, os, sys, json, re, hashlib

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(REPO, "results", "_w256bmc_w255_frozen_face.txt")
T0 = io.open(SRC, encoding="utf-8", newline="").read()

print("sha256_16 = %s" % hashlib.sha256(T0.encode("utf-8")).hexdigest()[:16])
print("bytes = %d lines = %d" % (len(T0.encode("utf-8")), T0.count("\n") + 1))

NEEDLES = [
    # ledger / K faces
    "558,920 投影", "line_merged@K556,720 **1.1944**", "556,720", "558,920",
    "983,135", "980,935", "978,735", "976,535", "985,335",
    "n_eff_held_equal 980,935", "n_eff_held_equal 983,135",
    # sec5 measured keys (W254 actuals to be replaced by W255 actuals)
    "−0.09273764", "−0.09241377", "0.24503097", "实差 0.0003 在带内", "（**0.3092** 实测锚）",
    "−0.09270819", "−0.08525445", "0.24503942", "0.3422", "0.0075 在带内",
    # band faces
    "A-ext seed=576_301..578_300", "entry rng seed=**576_301+j**", "entry rng=**576_301+j**",
    "exit rng=**578_301+j**",
    "A base=576301 span=2000 checked=2000 verdict=FREE", "B base=578301 span=200 checked=200 verdict=FREE",
    "A base=578501 span=2000 checked=2000 verdict=FREE", "B base=580501 span=200 checked=200 verdict=FREE",
    "R256：W255", "R257：W256",
    "576_300+1", "578_300+1", "578_500+1", "580_500+1",
    "576_101..578_100", "576_301..576_500", "578_301..580_300", "578_501..578_700",
    "578_501..580_500", "580_501..580_700", "580_501..582_500", "580_701..580_900",
    "578_301..578_500", "576_301..578_300",
    # seat / provenance
    "MSG-20261016-22xx-bmc-w255-seat", "cb79242ed", "fd48643c9",
    "（bm-c r1055 席·queue-head FREEZE-UNBLOCKED 发布）", "（bm-c r1055 席位", "（r1055 席位窗实跑",
    "（bm-c r1057 席", "（r1057 席位窗实跑",
    # finalize window
    "bm-c r1055 窗 21:3x", "21:3x", "已落账键·21:3x", "02:3x",
    # engine live-read + RAM
    "saturation_engine.py status live-read r1056", "saturation_engine.py status live-read r1058",
    "本窗 free RAM ~1.3GB（bm-c 底盘常驻·24G 物理内存机·LLM 态 27b 常驻+引擎队列空转·CPU 车道独立如实注记）",
    # wave tokens
    "W255", "W254", "W253", "W252", "W251", "W250", "W249", "W256", "W257",
    "n1_w255", "n1_w254", "n1_w253", "n1_w256",
    "_w255bmc", "_w254bmc", "_w253bmc", "_w256bmc",
    "--wave 255", "波号 255", "--wave 256", "波号 256",
    # ordinals
    "第 253 枚", "第 254 枚", "第 245 波", "第 246 波", "bm-c 第七十五枚自有波", "bm-c 第七十六枚自有波",
    "bmc rows 74+候选=第 75 枚 EXACT", "第 75 枚", "第 76 枚", "第 74 枚",
    "probe leg0 bmc_rows=74 attempt-continuity face（r1055 窗算法·bm-c own seat+bmc live rows 74 实读）",
    "engine_owner==bm-c 74 行注册", "engine_owner==bm-c 75 行注册",
    "engine_owner 行 244 注册在册", "engine_owner 行 245 注册在册",
    # registry scan faces
    "全二百五十二行注册 N1 带表", "全二百五十三行注册 N1 带表",
    "freeze 窗 live derive 252 行单态 owner rows 244", "freeze 窗 live derive 253 行单态 owner rows 245",
    "probe leg0 机证 252 行〔", "probe leg0 机证 253 行〔",
    "席位窗 probe leg0 实测 252 行〔", "席位窗 probe leg0 实测 253 行〔",
    "perpetual_faces.py 零 253 行", "perpetual_faces.py 零 254 行",
    "共二百五十二面实测", "共二百五十三面实测",
    "pre-W255 全二百五十二行注册 N1 带表", "表尾 W254 行", "表尾 W255 行",
    # §5.5 label
    "§5.5 W256+ 投影承接机证", "§5.5 W257+ 投影承接机证",
    # se_mu chain + line faces
    "→W249 **0.000332**→W250 **0.000331**→W251 **0.000330**→W252 **0.000330**→W253 **0.000329**→W254 **0.000328**】",
    "→W249 **0.000332**→W250 **0.000331**→W252 **0.000330**→W253 **0.000330**→W254 **0.000329**→W255 **0.000328**】",
    "line_pre_w254 1.1945", "line_pre_w255 1.1945", "line_pre_w253",
    "键 W254 实测 K-lift **−0.0001**", "键 W255 实测 K-lift **−0.0001**", "键 W255 实测 K-lift **+0.0001**",
    # §7/8 paradigm + precedent lists
    "bm-c r1055 W254 §7 范式", "bm-c r1055 W254 §8 范式", "bm-c r1055 W255 §7 范式",
    "W243/W246/W248/W249/W250/W251/W252/W253/W254 低 RAM 实烧先例",
    "W243/W246/W248/W249/W250/W252/W253/W254/W255 低 RAM 实烧先例",
    "r1054/W254 先例 freeze-prep 同式", "r1054/W255 先例 freeze-prep 同式", "r1056/W255 先例 freeze-prep 同式",
    # block markers
    "（**A 面=STAIRCASE-AFFECTS-A", "已如实披露非分叉）",
    "法典 §4 W255 行 A=576_301..578_300", "法典 §4 W255 行 B=578_301..578_500",
    "非转录 r587·ADMIT 回执在场）", "披露收敛·ADMIT 回执在场）",
    "5. **W256+ 投影（probe 机证 leg4", "verify at W256 prereg，hop 链逐跳在 probe 回执。",
    "·probe W256+ 投影 A naive 578_301..580_300 CLEAN hops=0", "never transcribe r587**）",
    "·W255 冻结窗 2.0G bm-c 实锚", "W240 冻结窗 33.2G bm-a 实锚）",
    "·W250 冻结窗 RAM 未记录（r1046 死窗",
    "selftest W255 face（", "零假设零风险。",
    "+W246=bm-a r1016 prereg derive", "——本波上游链=", "W256 freezer 承接面）】。",
    # hist-block extraction sanity
    "+W254=bm-c r1054 prereg derive", "+W253=bm-c", "e2c4b543e", "3eb691575", "fa2bc55e5", "c211d1269",
    "72d292ea3", "e166afc6c", "b1414b81a", "f931cf102",
    "924e87b3f02afb72", "d4a9d7164ba9490e", "7b550e65716e0ada", "c6dfb4291c09be1e",
    # zero-floor candidates (must be absent on T0')
    "waits-upstream ARMED", "（**B 面=CLEAN", "第 252 枚", "第 247 波",
    "第六次连续", "571_901..572_100", "561,120", "+0.0001",
    # ordinal faces (block-region stability floors)
    "第四次连续 A-hop", "第五次连续 A-hop", "第五次连续", "第五次连续 above-own-A",
    "第四次连续 above-own-A", "hops=1", "（W138..W206+",
    "W239..W254 leg（16 行）构成 W255 块 parity 113 行",
    "W239..W253 legs（15 行）",
    # freeze-window stamp
    "bm-c 循环班 r1056 freeze 窗 2026-10-17",
    # honesty / other
    "queue-head FREEZE-UNBLOCKED lane", "queue-head FREEZE-UNBLOCKED 承接",
    "本候选=bm-c 自有席自有波", "席位窗 probe leg0 实测",
    "W254 own-wave finalize 已落=席位时即解锁",
    "zero post-splice heal", "（W254 splice 先于席位窗已落地",
    "（W255 splice 先于席位窗已落地",
]

out = {}
for n in NEEDLES:
    c = T0.count(n)
    out[n] = c
    print("COUNT %-100r = %d" % (n, c))

# regex checks
fw = re.findall(r"bm-c 循环班 r1056 freeze 窗 2026-10-17 \d{2}:\dx", T0)
print("FREEZE_WINDOW_REGEX_MATCHES = %d %r" % (len(fw), fw))
win = re.findall(r"(\d{3}_\d{3})\.\.(\d{3}_\d{3})", T0)
bad = [m for m in win if int(m[0].replace("_", "")) > int(m[1].replace("_", ""))]
print("MALFORMED_WINDOWS = %d" % len(bad))

# context dumps for structural faces (segments not yet read in full)
def ctx(needle, before=40, after=420):
    i = T0.find(needle)
    if i < 0:
        return "ABSENT"
    return T0[max(0, i - before):i + after]

print("\n===== CTX 带位 tail (R256 vacancy face) =====")
print(ctx("R256：W255"))
print("\n===== CTX §0 认领 seat-publication line =====")
print(ctx("席位公示=MSG-20261016-22xx-bmc-w255-seat"))
print("\n===== CTX 波号 vacancy four-check =====")
print(ctx("波号 255=注册表"))
print("\n===== CTX low-RAM precedent list head =====")
print(ctx("W243/W246/W248/W249/W250/W251/W252/W253/W254 低 RAM 实烧先例"))
print("\n===== CTX freeze-prep precedent =====")
print(ctx("freeze-prep 束同窗落地"))
print("\n===== CTX §3 disjoint band line =====")
print(ctx("种子带 disjoint 全例"))
print("\n===== CTX b1 tail end =====")
print(ctx("W256 freezer 承接面）】。", before=400, after=10))
print("\n===== CTX pre-W255 registry face =====")
print(ctx("pre-W255"))
print("\n===== CTX title line head =====")
print(T0[:600])
