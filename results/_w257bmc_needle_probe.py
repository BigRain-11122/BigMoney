# -*- coding: utf-8 -*-
# r1059 bm-c: W257 prereg needle-count pre-flight probe (canon-clone of _w256bmc_needle_probe.py per age() machine-needle law).
# Measures EVERY candidate needle on the frozen W256 template face (results/_w257bmc_w256_frozen_face.txt,
# blob 4503bf5d92d69c2a409dc2074a300140f7bfdcb9 @ freeze-commit 5996e2c93, sha256_16 01685277539b98be)
# BEFORE the derive script is authored -- floors built from these measured counts (zero transcription).
# Output: results/_w257bmc_needle_counts.txt
import io, hashlib

SRC = "results/_w257bmc_w256_frozen_face.txt"
T0 = io.open(SRC, encoding="utf-8", newline="").read()
assert hashlib.sha256(T0.encode("utf-8")).hexdigest()[:16] == "01685277539b98be", "SRC face drift"

NEEDLES = [
    # compound value legs + bare faces
    "561,120 投影", "561,120", "563,320",
    "line_merged@K558,920 **1.1946**", "line_merged@K561,120 **1.1947**",
    "558,920", "985,335", "983,135", "987,535", "980,935",
    "−0.09270819", "−0.09270015", "−0.08525445", "−0.090659", "0.24503942", "0.24503835",
    "实差 0.0075 在带内", "实差 0.0020 在带内", "（**0.3422** 实测锚）", "（**0.3107** 实测锚）",
    # band legs
    "A-ext seed=578_501..580_500", "A-ext seed=580_701..582_700",
    "entry rng seed=**578_501+j**", "entry rng=**578_501+j**", "entry rng seed=**580_701+j**",
    "exit rng=**580_501+j**", "exit rng=**582_701+j**",
    "A base=578501 span=2000 checked=2000 verdict=FREE", "A base=580701 span=2000 checked=2000 verdict=FREE",
    "B base=580501 span=200 checked=200 verdict=FREE", "B base=582701 span=200 checked=200 verdict=FREE",
    "R257：W256", "R258：W257",
    "578_500+1", "580_500+1", "580_700+1", "582_700+1",
    # band windows (T0 faces live inside block regions; new-gen faces expect 0)
    "578_301..580_300", "578_501..578_700", "580_501..582_500", "580_701..580_900",
    "578_501..580_500", "580_501..580_700", "582_701..582_900", "580_701..582_700",
    "582_701..584_700", "582_901..583_100",
    # seat / provenance
    "MSG-20261017-023x-bmc-w256-seat", "MSG-20261017-03xx-bmc-w257-seat",
    "fd48643c9", "27ee6e95a", "cb79242ed",
    "（bm-c r1057 席·queue-head FREEZE-UNBLOCKED 发布）", "（bm-c r1058 席·queue-head FREEZE-UNBLOCKED 发布）",
    "（bm-c r1057 席位", "（bm-c r1058 席位", "（r1057 席位窗实跑", "（r1058 席位窗实跑",
    "bm-c r1057 窗 02:3x", "02:3x", "03:5x", "已落账键·02:3x", "已落账键·03:5x",
    # engine live-read + RAM head
    "saturation_engine.py status live-read r1058", "saturation_engine.py status live-read r1059",
    "本窗 free RAM ~3.3GB（bm-c 底盘常驻·24G 物理内存机·LLM 态 27b 常驻+引擎队列空转·CPU 车道独立如实注记）",
    # date faces
    "_w255bmc_20261016", "_w255bmc_20261017", "_w256bmc_20261017",
    # wave tokens
    "W256", "W255", "W254", "W253", "W252", "W251", "W257", "W258",
    # result files
    "n1_w256", "n1_w255", "n1_w254", "n1_w257",
    # script basenames
    "_w256bmc", "_w255bmc", "_w257bmc",
    # runner CLI
    "--wave 256", "波号 256", "--wave 257", "波号 257",
    # ordinals
    "第 254 枚", "第 255 枚", "第 246 波", "第 247 波",
    "bm-c 第七十六枚自有波", "bm-c 第七十七枚自有波",
    "bmc rows 75+候选=第 76 枚 EXACT", "bmc rows 76+候选=第 77 枚 EXACT",
    "第 76 枚", "第 77 枚", "第 75 枚",
    "probe leg0 bmc_rows=75 attempt-continuity face（r1057 窗算法·bm-c own seat+bmc live rows 75 实读）",
    "probe leg0 bmc_rows=76 attempt-continuity face（r1058 窗算法·bm-c own seat+bmc live rows 76 实读）",
    "engine_owner==bm-c 75 行注册", "engine_owner==bm-c 76 行注册",
    "engine_owner 行 245 注册在册", "engine_owner 行 246 注册在册",
    # registry scan faces
    "全二百五十三行注册 N1 带表", "全二百五十四行注册 N1 带表",
    "freeze 窗 live derive 253 行单态 owner rows 245", "freeze 窗 live derive 254 行单态 owner rows 246",
    "probe leg0 机证 253 行〔", "probe leg0 机证 254 行〔",
    "席位窗 probe leg0 实测 253 行〔", "席位窗 probe leg0 实测 254 行〔",
    "perpetual_faces.py 零 254 行", "perpetual_faces.py 零 255 行",
    "共二百五十三面实测", "共二百五十四面实测",
    "§5.5 W257+ 投影承接机证", "§5.5 W258+ 投影承接机证",
    # block markers (raw T0 faces)
    "（**A 面=STAIRCASE-AFFECTS-A", "已如实披露非分叉）",
    "法典 §4 W256 行 A=578_501..580_500", "法典 §4 W256 行 B=580_501..580_700",
    "非转录 r587·ADMIT 回执在场）", "披露收敛·ADMIT 回执在场）",
    "5. **W257+ 投影（probe 机证 leg4", "verify at W257 prereg，hop 链逐跳在 probe 回执。",
    "·probe W257+ 投影 A naive 580_501..582_500 CLEAN hops=0", "never transcribe r587**）",
    "·W256 冻结窗 3.3G bm-c 实锚", "W240 冻结窗 33.2G bm-a 实锚）", "·W250 冻结窗 RAM 未记录（r1046 死窗",
    "selftest W256 face（", "零假设零风险。",
    "+W246=bm-a r1016 prereg derive", "——本波上游链=", "W256 freezer 承接面）】。",
    # stability / HIST faces
    "（W138..W206+", "W239..W255 legs（17 行）构成 W256 块 parity 114 行",
    "bm-c 循环班 r1058 freeze 窗 2026-10-17",
    "W243/W246/W248/W249/W250/W251/W252/W253/W254/W255 低 RAM 实烧先例",
    "r1056/W255 先例 freeze-prep 同式",
    "→W249 **0.000332**→W250 **0.000331**→W251 **0.000330**→W252 **0.000330**→W253 **0.000329**→W254 **0.000328**→W255 **0.000328**】",
    "line_pre_w255 1.1945", "line_pre_w256 1.1945", "line_pre_w256 1.1947",
    "键 W255 实测 K-lift **+0.0001**", "键 W256 实测 K-lift",
    "bm-c r1057 W255 §7 范式", "bm-c r1057 W255 §8 范式", "bm-c r1058 W256 §7 范式",
    "n_eff_held_equal 985,335", "n_eff_held_equal 983,135",
    "queue-head FREEZE-UNBLOCKED lane", "queue-head FREEZE-UNBLOCKED 承接",
    "本候选=bm-c 自有席自有波", "表尾 W255 行", "表尾 W256 行",
    "pre-W256 全二百五十三行注册 N1 带表", "pre-W257 全二百五十四行注册 N1 带表",
    "zero post-splice heal",
    "924e87b3f02afb72", "7b550e65716e0ada", "d4a9d7164ba9490e", "c6dfb4291c09be1e",
    "e166afc6c", "b1414b81a", "f931cf102", "72d292ea3",
    "aa6102e35", "31c9e4872", "1c7112fd9", "5996e2c93",
    "ad9776287dd52280", "986e9162b86e0c7f",
    "hops=1", "hops=0",
    "第五次连续 A-hop", "第六次连续 A-hop", "第七次连续 A-hop",
    "第五次连续", "第六次连续", "第七次连续",
    "第五次连续 above-own-A", "第六次连续 above-own-A", "第七次连续 above-own-A",
    "第四次连续 A-hop", "第四次连续 above-own-A",
    "W257+ 投影", "W258+ 投影",
    "STAIRCASE-AFFECTS-A", "waits-upstream ARMED", "（**B 面=CLEAN",
    "r1057 窗算法", "已落账键·02:3x",
    "e2c4b543e", "3eb691575", "fa2bc55e5", "c211d1269",
    "PERPETUAL-N1-W256",
]

lines = []
for n in NEEDLES:
    lines.append("%d\t%s" % (T0.count(n), n))
io.open("results/_w257bmc_needle_counts.txt", "w", encoding="utf-8", newline="").write("\n".join(lines) + "\n")
print("needle probe done: %d needles measured, T0 bytes=%d" % (len(NEEDLES), len(T0.encode("utf-8"))))
