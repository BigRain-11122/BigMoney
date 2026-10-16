# -*- coding: utf-8 -*-
# r1061 bm-c: W258 prereg needle-count pre-flight probe (canon-clone of _w257bmc_needle_probe.py per age() machine-needle law).
# Measures every candidate needle face on T0 = the FROZEN W257 prereg face (blob 88ae1c8ea564994a90ede6e3709d43223c8caba5
# @ freeze commit c7fbc443c, sha256_16 545373a72ba4d46c, 42,904 bytes / 64 lines -- PRE-BACKFILL face; the sec.7/8-backfilled
# HEAD twin d0734421d5b517c980c1e2e3104ddf2fc363bb96 disclosed, NOT used per r1052/r1049 precedent law).
# Output: results/_w258bmc_needle_counts.txt (one "count<TAB>needle" per line). ALL VMAP_FLOORS entries in the derive
# script must equal these measured counts (zero-floors asserted ==0). Zero transcription.
import io

SRC = "results/_w258bmc_w257_frozen_face.txt"
OUT = "results/_w258bmc_needle_counts.txt"
T0 = io.open(SRC, encoding="utf-8", newline="").read()

NEEDLES = [
    # ---- pre-chain VMAP needles ----
    "563,320 投影", "line_merged@K561,120 **1.1947**", "561,120", "563,320",
    "987,535", "985,335", "983,135", "989,735",
    "−0.09270015", "−0.090659", "0.24503835", "实差 0.0020 在带内", "（**0.3107** 实测锚）",
    "−0.09275554", "−0.10688227", "0.24502959", "0.0141 在带内", "0.2973", "565,520",
    "A-ext seed=580_701..582_700", "entry rng seed=**580_701+j**", "entry rng=**580_701+j**",
    "exit rng=**582_701+j**",
    "A base=580701 span=2000 checked=2000 verdict=FREE", "B base=582701 span=200 checked=200 verdict=FREE",
    "A base=582901 span=2000 checked=2000 verdict=FREE", "B base=584901 span=200 checked=200 verdict=FREE",
    "R258：W257", "R259：W258",
    "580_700+1", "582_700+1", "582_900+1", "584_900+1",
    "MSG-20261017-03xx-bmc-w257-seat", "MSG-20261017-0517-bmc-w258-seat", "27ee6e95a", "d0d0d04a4",
    "（bm-c r1058 席·queue-head FREEZE-UNBLOCKED 发布）", "（bm-c r1058 席位", "（r1058 席位窗实跑",
    "（bm-c r1060 席", "（r1060 席位窗实跑",
    "bm-c r1058 窗 03:5x", "03:5x", "已落账键·03:5x", "05:1x",
    "saturation_engine.py status live-read r1059", "saturation_engine.py status live-read r1061",
    "本窗 free RAM ~4GB（bm-c 底盘常驻·24G 物理内存机·LLM 态 27b 常驻+引擎队列空转·CPU 车道独立如实注记）",
    # ---- roll labels ----
    "W258", "W257", "W256", "W255", "W254", "W253", "W252", "W251", "W259",
    # ---- result-file basenames ----
    "n1_w257", "n1_w256", "n1_w255", "n1_w258",
    # ---- script basenames ----
    "_w257bmc", "_w256bmc", "_w258bmc", "_w257bmc_20261017", "_w256bmc_20261017", "_w256bmc_20261016",
    # ---- runner CLI ----
    "--wave 257", "波号 257", "--wave 258", "波号 258",
    # ---- ordinals ----
    "第 255 枚", "第 247 波", "bm-c 第七十七枚自有波", "bm-c 第七十八枚自有波",
    "bmc rows 76+候选=第 77 枚 EXACT", "bmc rows 77+候选=第 78 枚 EXACT",
    "第 77 枚", "第 76 枚", "第 78 枚", "第 256 枚", "第 248 波",
    "probe leg0 bmc_rows=76 attempt-continuity face（r1058 窗算法·bm-c own seat+bmc live rows 76 实读）",
    "probe leg0 bmc_rows=77 attempt-continuity face（r1060 窗算法·bm-c own seat+bmc live rows 77 实读）",
    "engine_owner==bm-c 76 行注册", "engine_owner==bm-c 77 行注册",
    "engine_owner 行 246 注册在册", "engine_owner 行 247 注册在册",
    # ---- registry scan faces ----
    "全二百五十四行注册 N1 带表", "全二百五十五行注册 N1 带表",
    "freeze 窗 live derive 254 行单态 owner rows 246", "freeze 窗 live derive 255 行单态 owner rows 247",
    "probe leg0 机证 254 行〔", "probe leg0 机证 255 行〔",
    "席位窗 probe leg0 实测 254 行〔", "席位窗 probe leg0 实测 255 行〔",
    "perpetual_faces.py 零 255 行", "perpetual_faces.py 零 256 行",
    "共二百五十四面实测", "共二百五十五面实测",
    "表尾 W256 行", "表尾 W257 行",
    "pre-W257 全二百五十四行注册 N1 带表", "pre-W258 全二百五十五行注册 N1 带表",
    # ---- §5.5 title ----
    "§5.5 W258+ 投影承接机证", "§5.5 W259+ 投影承接机证",
    # ---- post-leg needles (T0 true forms) ----
    "→W249 **0.000332**→W250 **0.000331**→W251 **0.000330**→W252 **0.000330**→W253 **0.000329**→W254 **0.000328**→W255 **0.000328**→W256 **0.000327**】",
    "→W249 **0.000332**→W250 **0.000331**→W251 **0.000330**→W253 **0.000330**→W254 **0.000329**→W255 **0.000328**→W256 **0.000328**→W257 **0.000327**】",
    "line_pre_w256 1.1947", "line_pre_w257", "键 W256 实测 K-lift **0.0000**", "键 W257 实测 K-lift",
    "bm-c r1058 W256 §7 范式", "bm-c r1058 W256 §8 范式", "bm-c r1060 W257 §7 范式",
    "W243/W246/W248/W249/W250/W251/W252/W253/W254/W255/W256 低 RAM 实烧先例",
    "W243/W246/W248/W249/W250/W251/W253/W254/W255/W256/W257 低 RAM 实烧先例",
    "r1058/W256 先例 freeze-prep 同式", "r1059/W257 先例 freeze-prep 同式",
    "n_eff_held_equal 985,335", "n_eff_held_equal 987,535",
    # ---- block markers (T0 forms) ----
    "（**A 面=STAIRCASE-AFFECTS-A", "已如实披露非分叉）",
    "法典 §4 W257 行 A=580_701..582_700", "法典 §4 W257 行 B=582_701..582_900",
    "披露收敛·ADMIT 回执在场）", "非转录 r587·ADMIT 回执在场）",
    "5. **W258+ 投影（probe 机证 leg4", "verify at W258 prereg，hop 链逐跳在 probe 回执。",
    "·probe W258+ 投影 A naive 582_701..584_700 CLEAN hops=0", "never transcribe r587**）",
    "·W257 冻结窗 4G bm-c 实锚", "·W258 冻结窗 3.5G bm-c 实锚",
    "·W250 冻结窗 RAM 未记录（r1046 死窗", "W240 冻结窗 33.2G bm-a 实锚）",
    "selftest W257 face（", "零假设零风险。",
    "+W246=bm-a r1016 prereg derive", "——本波上游链=",
    "W258 freezer 承接面）】。", "W257 freezer 承接面）】。",
    "本波上游链=W1..W256 finalize 全落地", "本波上游链=W1..W257 finalize 全落地",
    # ---- band windows ----
    "580_701..582_700", "582_701..582_900", "580_501..582_500", "580_701..580_900",
    "578_501..580_500", "580_501..580_700", "582_701..584_700", "582_901..583_100",
    "582_901..584_900", "584_901..585_100", "584_901..586_900", "585_101..585_300",
    "578_501..578_700", "578_301..580_300", "576_301..576_500", "576_101..578_100",
    "A-ext seed=582_901..584_900", "B-ext exit seed=584_901..585_100", "B-ext exit seed=582_701..582_900",
    # ---- hop-ordinal phrases ----
    "第七次连续 A-hop", "第八次连续 A-hop", "第七次连续", "第八次连续",
    "第六次连续 A-hop", "第六次连续", "第七次连续 above-own-A", "第六次连续 above-own-A",
    "STAIRCASE-AFFECTS-A", "hops=1", "hops=0",
    "W252/W253/W254/W255/W256/W257=A/B 双 1-hop 形态连续六波",
    # ---- zero-floor faces (new-gen, expect 0) ----
    "waits-upstream ARMED", "（**B 面=CLEAN",
    "A_clean_at_naive_start=true", "A_staircase_hop_past_W257_B",
    # ---- chain sha16 receipts ----
    "924e87b3f02afb72", "7b550e65716e0ada", "d4a9d7164ba9490e", "c6dfb4291c09be1e",
    "e166afc6c", "b1414b81a", "f931cf102", "72d292ea3",
    "e2c4b543e", "3eb691575", "fa2bc55e5", "c211d1269",
    "aa6102e35", "31c9e4872", "1c7112fd9", "5996e2c93",
    "d93e644b38fae882", "38da334ef0a033d2", "e37b483340aa67ba",
    "550293d3f", "9b848c2e0", "370d6c81", "c7fbc443c", "5e88b3067",
    # ---- misc faces ----
    "（W138..W206+", "PERPETUAL-N1-W257", "PERPETUAL-N1-W258",
    "zero post-splice heal", "queue-head FREEZE-UNBLOCKED lane", "queue-head FREEZE-UNBLOCKED 承接",
    "本候选=bm-c 自有席自有波", "·W255 冻结窗 2.0G", "·W256 冻结窗 3.3G",
    "bm-c 循环班 r1059 freeze 窗 2026-10-17", "bm-c 循环班 r1061 freeze 窗",
    "W243/W246/W248/W249/W250/W251/W252/W253/W254/W255/W256/W257 低 RAM 实烧先例",
    "1. **W258 A naive**", "W258p_B_lands_inside_W258p_A_naive",
    "W259p_B_lands_inside_W259p_A_naive", "W259 freezer", "W258 冻结方",
    "594,935", "991,935",
]

rows = []
for n in NEEDLES:
    rows.append("%d\t%s" % (T0.count(n), n))
io.open(OUT, "w", encoding="utf-8", newline="").write("\n".join(rows) + "\n")
print("needle probe: counted %d faces -> %s" % (len(NEEDLES), OUT))
