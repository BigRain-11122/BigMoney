# -*- coding: utf-8 -*-
# r1085 bm-c: W266 prereg derive NEEDLE PROBE (E63 age() machine-needle law: measure before authoring).
# T0 = frozen W265 prereg face @ e57215a2c (results/_w266bmc_w265_frozen_face.txt, 22,927B, sha256_16 d36c29cf048d299d).
# Dumps every planned VMAP needle count + verbatim POST-leg faces + block markers + zero-floor candidates
# to results/_w266bmc_needle_counts.txt. Zero mutation of any canon file.
import io, os, sys, re, json, hashlib

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(REPO, "results", "_w266bmc_w265_frozen_face.txt")
OUT = os.path.join(REPO, "results", "_w266bmc_needle_counts.txt")

T0 = io.open(SRC, encoding="utf-8", newline="").read()
assert len(T0.encode("utf-8")) == 22927, "SRC size drift: %d" % len(T0.encode("utf-8"))
assert hashlib.sha256(T0.encode("utf-8")).hexdigest()[:16] == "d36c29cf048d299d", "SRC sha mismatch"

lines = []
A = lines.append

A("=== W266 prereg needle probe (T0 = frozen W265 face @ e57215a2c, r1085 window) ===")
A("T0 bytes=%d sha256_16=%s" % (len(T0.encode("utf-8")), hashlib.sha256(T0.encode("utf-8")).hexdigest()[:16]))
A("")

A("--- explicit VMAP needle counts (planned legs, measured on T0) ---")
EXPLICIT = [
    "A-ext seed=598_301..600_300",
    "B-ext exit seed=600_301..600_500",
    "entry rng=**598_301+j**（与 A[j] 同源配对语义逐字",
    "席位公示=MSG-20261017-2241-bmc-w265-seat 已推 origin 7343e3650 r565 律（bm-c r1077 席·queue-head seat-first lane）",
    "席位公示 MSG-20261017-2241-bmc-w265-seat 先推 origin 7343e3650 r565 律",
    "波号 265",
    "r1077 席位窗实跑：origin inbox 零 W265 席位外机命中",
    "零 265 行",
    "零 skip-ahead W266/W267 席位声明",
    "池第 263 枚",
    "第 255 波",
    "bm-c 第八十四枚自有波",
    "probe leg0 bmc_rows=83 attempt-continuity face（r1077 窗算法·bm-c own seat+bmc live rows 83 实读）——freeze 时 live derive bmc rows 83+候选=第 84 枚 EXACT",
    "engine_owner==bm-c 83 行注册",
    "saturation_engine.py status live-read r1080：burns_active=[] queue_next=[] 实读·heartbeat 新鲜",
    "本机 bm-c 实例·heartbeat 新鲜实读 r1080 窗·队列空转 idle",
    "引擎实况注记（本机 bm-c 实例 heartbeat 新鲜 r1080 窗实读",
    "--wave 265/finalize --wave 265",
    "§5.5 W266+ 投影承接机证",
    "本窗 free RAM ~3GB（bm-c 底盘常驻·24G 物理内存机·CEO 周末用机态·GPU=gen-only 车道空窗（nvidia-smi 实读 3%·3.2G VRAM 常驻·POOL-0016 候件冻结态）·LLM 态已退役 gen 专用车道·引擎队列空转·CPU 车道独立如实注记）",
]
for s in EXPLICIT:
    A("count=%d %r" % (T0.count(s), s))
A("")

A("--- chained roll token counts (T0) ---")
for s in ["n1_w265", "n1_w264", "n1_w263", "_w265bmc", "_w264bmc", "_w263bma",
          "W265", "W264", "W263", "W262", "W261", "W260", "W259", "W258", "W257", "W256", "W255"]:
    A("count=%d %r" % (T0.count(s), s))
A("")

A("--- block-marker counts (T0 raw + post-VMAP simulation) ---")
P1, P2, P3 = "\x01W\x01", "\x01N\x01", "\x01B\x01"
VMAP_SIM = [
    ("A-ext seed=598_301..600_300", "A-ext seed=600_501..602_500"),
    ("B-ext exit seed=600_301..600_500", "B-ext exit seed=602_501..602_700"),
    ("entry rng=**598_301+j**（与 A[j] 同源配对语义逐字", "entry rng=**600_501+j**（与 A[j] 同源配对语义逐字"),
    ("席位公示=MSG-20261017-2241-bmc-w265-seat 已推 origin 7343e3650 r565 律（bm-c r1077 席·queue-head seat-first lane）",
     "席位公示=MSG-20261018-0719-bmc-w266-seat 已推 origin ace19ba85b r565 律（bm-c r1084 席·queue-head seat-first lane）"),
    ("席位公示 MSG-20261017-2241-bmc-w265-seat 先推 origin 7343e3650 r565 律",
     "席位公示 MSG-20261018-0719-bmc-w266-seat 先推 origin ace19ba85b r565 律"),
    ("波号 265", "波号 266"),
    ("r1077 席位窗实跑：origin inbox 零 W265 席位外机命中", "r1084 席位窗实跑：origin inbox 零 W266 席位外机命中"),
    ("零 265 行", "零 266 行"),
    ("零 skip-ahead W266/W267 席位声明", "零 skip-ahead W267/W268 席位声明"),
    ("池第 263 枚", "池第 264 枚"),
    ("第 255 波", "第 256 波"),
    ("bm-c 第八十四枚自有波", "bm-c 第八十五枚自有波"),
    ("probe leg0 bmc_rows=83 attempt-continuity face（r1077 窗算法·bm-c own seat+bmc live rows 83 实读）——freeze 时 live derive bmc rows 83+候选=第 84 枚 EXACT",
     "probe leg0 bmc_rows=84 attempt-continuity face（r1084 窗算法·bm-c own seat+bmc live rows 84 实读）——freeze 时 live derive bmc rows 84+候选=第 85 枚 EXACT"),
    ("engine_owner==bm-c 83 行注册", "engine_owner==bm-c 84 行注册"),
    ("saturation_engine.py status live-read r1080：burns_active=[] queue_next=[] 实读·heartbeat 新鲜",
     "saturation_engine.py status live-read r1085：burns_active=[] queue_next=[] 实读·heartbeat 新鲜"),
    ("本机 bm-c 实例·heartbeat 新鲜实读 r1080 窗·队列空转 idle", "本机 bm-c 实例·heartbeat 新鲜实读 r1085 窗·队列空转 idle"),
    ("引擎实况注记（本机 bm-c 实例 heartbeat 新鲜 r1080 窗实读", "引擎实况注记（本机 bm-c 实例 heartbeat 新鲜 r1085 窗实读"),
    ("--wave 265/finalize --wave 265", "--wave 266/finalize --wave 266"),
    ("§5.5 W266+ 投影承接机证", "§5.5 W267+ 投影承接机证"),
    ("n1_w265", P2), ("n1_w264", "n1_w265"), (P2, "n1_w266"),
    ("_w265bmc", P3), ("_w264bmc", "_w265bmc"), (P3, "_w266bmc"),
    ("W265", P1), ("W264", "W265"), ("W263", "W264"), ("W262", "W263"), ("W261", "W262"), ("W260", "W261"),
    ("W259", "W260"), ("W258", "W259"), ("W257", "W258"), ("W256", "W257"), ("W255", "W256"), (P1, "W266"),
]
T1 = T0
for o, n in VMAP_SIM:
    T1 = T1.replace(o, n)

MARKERS = [
    ("b_title", "engine_owner 行 254 注册在册（表尾", "已名此窗）**】】）"),
    ("b_prev", "prev=**届时空窗活链头 derive 禁手抄**", "（机械算·投影面仅披露·finalize 运行时按 registry 键 derive 免疫）。"),
    ("b_band", "（**A 面=STAIRCASE-AFFECTS-A", "（见 §5 item5）。"),
    ("b3_a", "entry rng seed=**598_301+j**", "；p=`BASELINE_P"),
    ("b3_b", "exit rng=**600_301+j**", "；p_exit=`P_EXIT=0.05`"),
    ("b_claim_proj", "probe W266+ 投影 A naive 600_301..602_300 CLEAN hops=0", "never transcribe r587**）"),
    ("b5_projection", "5. **W266+ 投影（probe 机证 leg4", "verify at W266 prereg，hop 链逐跳在 probe 回执。"),
    ("b_gated", "本件=席位窗后首窗冻结件；五面冻结拼接脚本", "（gate0.5 绿·编辑器 loud abort 兜底）**。"),
]
for name, sm, em in MARKERS:
    A("block=%s start(T0)=%d start(T1)=%d end(T1)=%d" % (name, T0.count(sm), T1.count(sm), T1.count(em)))
A("")

A("--- POST-leg needle candidates (measured on T1 post-VMAP simulation) ---")
POST_CAND = [
    "22:3x", "19:2x", "07:0x",
    "（W265 实测键 **−0.09272766**·K=578,720 合并池·W265-only 实测 **−0.08593818**）",
    "（W264 实测键 **−0.09272766**·K=578,720 合并池·W264-only 实测 **−0.08593818**）",
    "W2..W265 共二百六十三面实测 mu 稳定先例",
    "W265-only vs merged 实差 0.0068 在带内",
    "键 **0.24504297**=W265 合并池实测",
    "与 W265 A 档 p95（**0.3046** 实测锚）",
    "键 W265 实测 K-lift **0.0001**·line_merged@K578,720 **1.1955**·line_pre_w265 1.1954·n_eff_held_equal 996,335",
    "→W262 **0.000324**→W263 **0.000323**→W264 **0.000323**→W265 **0.000322**→W266 投影 0.000322】",
    "→W261 **0.000324**→W262 **0.000323**→W263 **0.000323**→W264 **0.000322**→W265 投影 0.000322】",
    "（起草窗实流 W1..W265 已落账 578,720 实测〔n1_w265_results.json 机读·W265 finalize 已落〕）",
    "bm-c r1077 W265 §7 范式", "bm-c r1077 W265 §8 范式",
    "bm-c r1084 W265 §7 范式",
    "·W244 冻结窗 41.9G bm-a 实锚·W263 冻结窗 26G bm-a 实锚·W264 冻结窗 7G bm-c 实锚）",
    "estate absorb r1077 7343e3650",
    "W265 finalize one-pass bm-c r1077 窗 22:3x",
    "n_eff_held_equal 996,335", "1,005,135", "1,007,335", "578,720", "580,920", "583,120", "1,009,535",
    "共二百六十三面", "共二百六十四面",
    "W206/W211..W265 低 RAM 实烧先例",
    "probe receipt _w265bmc_20261017 机证",
    "W266p_", "W265p_", "W267p_",
    "line_pre_w265 1.1954", "line_pre_w264 1.1954",
    "键 W263 实测 K-lift", "键 W264 实测 K-lift", "键 W265 实测 K-lift",
    "verify at W266 prereg", "verify at W265 prereg", "verify at W267 prereg",
    "W266+ 投影", "W267+ 投影", "W265+ 投影",
    "第十四次连续 A-hop", "第十五次连续 A-hop", "第十六次连续 A-hop",
    "第十五次连续 above-own-A", "第十六次连续 above-own-A",
    "连续十四波", "连续十五波",
    "hops=1", "hops=0",
    "600_301..602_300", "600_501..602_500", "602_501..602_700", "602_501..604_500", "602_701..602_900",
    "席位时即解锁",
    "598_301..600_300", "600_301..600_500",
    "600_300+1", "600_500+1", "602_500+1",
    "A_staircase_hop_past_W265_B=true", "A_staircase_hop_past_W264_B=true",
    "B_lands_above_own_A=true",
    "seed_admit_gate rc0 双带 FREE",
    "waits-upstream ARMED",
    "−0.09272766", "0.24504297", "−0.08593818", "0.3046", "−0.09271568", "0.24504118", "−0.08956582", "0.3149",
    "实差 0.0068 在带内", "实差 0.0031 在带内",
    "MSG-20261017-2241", "MSG-20261018-0719", "MSG-20261017-1950",
    "7343e3650", "ace19ba85b", "dd5fd438e", "f4ffdb34e", "216b578b0", "964148797", "17dd06323",
    "b32f6bf1c", "f499817fa", "355c716b7", "91da16c86", "e57215a2c", "a47517f792", "93298b7e33", "c72805837c", "2e622ee447",
    "bmc_rows=83", "bmc_rows=82", "第 84 枚", "第 85 枚", "第 255 波", "第 256 波", "第八十四枚", "第八十五枚",
    "engine_owner==bm-c 83 行注册", "engine_owner==bm-c 84 行注册", "engine_owner==bm-c 82 行注册",
    "r1077 席", "r1084 席", "本窗 free RAM ~3GB", "本窗 free RAM ~7GB",
    "n1_w264_results.json", "n1_w263_results.json", "n1_w265_results.json", "n1_w266_results.json",
    "W2..W264", "W2..W265", "W136..W264", "W136..W265",
    "queue_depth", "GATED on", "finalize PENDING",
    "R266：W265 带", "R267：W266 带",
    "W266=bm-c own-wave window per chain-order law", "W265=bm-c own-wave window per chain-order law",
    "perpetual_faces/n1_w265/", "p2cal_ext/n1_w265/",
]
for s in POST_CAND:
    A("T0=%d T1=%d %r" % (T0.count(s), T1.count(s), s))
A("")

A("--- verbatim T1 face extracts (POST-leg authoring inputs) ---")
EXTRACTS = [
    ("sec5_item1", "（W265 实测键"),
    ("sec5_mu_stable", "共二百六十三面实测"),
    ("sec5_gap", "vs merged 实差"),
    ("sec5_item2_sigma", "键 **0.24504297**"),
    ("sec5_item3_p95", "A 档 p95（"),
    ("sec5_item4_klift", "键 W265 实测 K-lift"),
    ("se_mu_chain", "→W262 **"),
    ("sec4_pool", "（起草窗实流 W1..W265"),
    ("paradigm7", "§7 范式"),
    ("paradigm8", "§8 范式"),
    ("ram_ledger_tail", "冻结窗 7G bm-c 实锚"),
    ("stamp_faces", "22:3x"),
    ("bgated_timeline", "先例实时间线"),
    ("btitle_finalize", "W265 finalize 已落地"),
    ("bprev_head", "最新已 finalize 锚"),
]
for label, needle in EXTRACTS:
    idx = 0
    hits = 0
    while hits < 3:
        i = T1.find(needle, idx)
        if i < 0:
            break
        A("[%s @%d] ...%s..." % (label, i, T1[max(0, i - 60):i + 260].replace("\n", "\\n")))
        idx = i + len(needle)
        hits += 1
    if hits == 0:
        A("[%s] NOT FOUND in T1: %r" % (label, needle))
A("")

A("--- RAM/engine live faces measured THIS window (r1085) ---")
try:
    import psutil
    vm = psutil.virtual_memory()
    A("psutil free_ram_gb=%.2f avail_gb=%.2f total_gb=%.1f" % (vm.free / 1e9, vm.available / 1e9, vm.total / 1e9))
except Exception as e:
    A("psutil FAIL: %r" % (e,))
try:
    import subprocess
    r = subprocess.run(["nvidia-smi", "--query-gpu=utilization.gpu,memory.used,memory.total", "--format=csv,noheader"], capture_output=True, timeout=20)
    A("nvidia-smi: %s" % r.stdout.decode("utf-8", "replace").strip())
except Exception as e:
    A("nvidia-smi FAIL: %r" % (e,))

io.open(OUT, "w", encoding="utf-8", newline="").write("\n".join(lines) + "\n")
print("NEEDLE PROBE OK -> %s (%d lines)" % (OUT, len(lines)))
print("T0=%dB T1=%dB" % (len(T0.encode("utf-8")), len(T1.encode("utf-8"))))
