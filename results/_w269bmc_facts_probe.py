# -*- coding: utf-8 -*-
# r1092 bm-c: W269 prereg derive -- needle-count pre-flight evidence (MEASURED, r1077 law).
# T0 = frozen W268 prereg face @ f1ec8231c7 (extracted results/_w269bmc_w268_frozen_face.txt,
# sha1 7b08409b55d872339afd57159fa4332f8944783f / 23,158B / sha256_16 83076bf5b0e4a989).
# Measures: (a) T0 floors for every planned VMAP needle; (b) T1 roll-sim residuals with
# block-span classification (interior=discarded by block replace vs live=needs a leg);
# (c) POST_LEG needle counts on T1; (d) BLOCK marker uniqueness on T1; (e) live RAM/GPU faces.
import io, os, json, hashlib, subprocess, sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(REPO, "results", "_w269bmc_w268_frozen_face.txt")
OUTJ = os.path.join(REPO, "results", "_w269bmc_facts_probe.json")

T0 = io.open(SRC, encoding="utf-8", newline="").read()
assert len(T0.encode("utf-8")) == 23158, "SRC size drift: %d" % len(T0.encode("utf-8"))
assert hashlib.sha256(T0.encode("utf-8")).hexdigest()[:16] == "83076bf5b0e4a989", "SRC sha mismatch"

P1, P2, P3 = "\x01W\x01", "\x01N\x01", "\x01B\x01"

VMAP = [
    ("A-ext seed=604_901..606_900", "A-ext seed=607_101..609_100"),
    ("B-ext exit seed=606_901..607_100", "B-ext exit seed=609_101..609_300"),
    ("entry rng=**604_901+j**（与 A[j] 同源配对语义逐字", "entry rng=**607_101+j**（与 A[j] 同源配对语义逐字"),
    ("席位公示=MSG-20261018-1229-bmc-w268-seat 已推 origin b9ad2f1119 r565 律（bm-c r1089 席·queue-head seat-first lane）",
     "席位公示=MSG-20261018-1407-bmc-w269-seat 已推 origin d630d043b9 r565 律（bm-c r1091 席·queue-head seat-first lane）"),
    ("席位公示 MSG-20261018-1229-bmc-w268-seat 先推 origin b9ad2f1119 r565 律",
     "席位公示 MSG-20261018-1407-bmc-w269-seat 先推 origin d630d043b9 r565 律"),
    ("波号 268", "波号 269"),
    ("r1089 席位窗实跑：origin inbox 零 W268 席位外机命中", "r1091 席位窗实跑：origin inbox 零 W269 席位外机命中"),
    ("零 268 行", "零 269 行"),
    ("零 skip-ahead W269/W270 席位声明", "零 skip-ahead W270/W271 席位声明"),
    ("池第 266 枚", "池第 267 枚"),
    ("第 258 波", "第 259 波"),
    ("bm-c 第八十七枚自有波", "bm-c 第八十八枚自有波"),
    ("probe leg0 bmc_rows=86 attempt-continuity face（r1089 窗算法·bm-c own seat+bmc live rows 86 实读）——freeze 时 live derive bmc rows 86+候选=第 87 枚 EXACT",
     "probe leg0 bmc_rows=87 attempt-continuity face（r1091 窗算法·bm-c own seat+bmc live rows 87 实读）——freeze 时 live derive bmc rows 87+候选=第 88 枚 EXACT"),
    ("engine_owner==bm-c 86 行注册", "engine_owner==bm-c 87 行注册"),
    ("saturation_engine.py status live-read r1090：burns_active=[] queue_next=[] 实读·heartbeat 新鲜",
     "saturation_engine.py status live-read r1092：burns_active=[] queue_next=[] 实读·heartbeat 新鲜"),
    ("本机 bm-c 实例·heartbeat 新鲜实读 r1090 窗·队列空转 idle",
     "本机 bm-c 实例·heartbeat 新鲜实读 r1092 窗·队列空转 idle"),
    ("引擎实况注记（本机 bm-c 实例 heartbeat 新鲜 r1090 窗实读",
     "引擎实况注记（本机 bm-c 实例 heartbeat 新鲜 r1092 窗实读"),
    ("--wave 268/finalize --wave 268", "--wave 269/finalize --wave 269"),
    ("§5.5 W269+ 投影承接机证", "§5.5 W270+ 投影承接机证"),
    ("n1_w268", P2), ("n1_w267", "n1_w268"), (P2, "n1_w269"),
    ("_w268bmc", P3), ("_w267bmc", "_w268bmc"), (P3, "_w269bmc"),
    ("W268", P1), ("W267", "W268"), ("W266", "W267"), ("W265", "W266"), ("W264", "W265"), ("W263", "W264"),
    ("W262", "W263"), ("W261", "W262"), ("W260", "W261"), ("W259", "W260"), ("W258", "W259"), ("W257", "W258"),
    ("W256", "W257"), (P1, "W269"),
]

VMAP_FLOORS = {
    "A-ext seed=604_901..606_900": 1,
    "B-ext exit seed=606_901..607_100": 1,
    "entry rng=**604_901+j**（与 A[j] 同源配对语义逐字": 1,
    "席位公示=MSG-20261018-1229-bmc-w268-seat 已推 origin b9ad2f1119 r565 律（bm-c r1089 席·queue-head seat-first lane）": 1,
    "席位公示 MSG-20261018-1229-bmc-w268-seat 先推 origin b9ad2f1119 r565 律": 1,
    "波号 268": 1,
    "r1089 席位窗实跑：origin inbox 零 W268 席位外机命中": 1,
    "零 268 行": 1,
    "零 skip-ahead W269/W270 席位声明": 1,
    "池第 266 枚": 1,
    "第 258 波": 1,
    "bm-c 第八十七枚自有波": 1,
    "probe leg0 bmc_rows=86 attempt-continuity face（r1089 窗算法·bm-c own seat+bmc live rows 86 实读）——freeze 时 live derive bmc rows 86+候选=第 87 枚 EXACT": 1,
    "engine_owner==bm-c 86 行注册": 1,
    "saturation_engine.py status live-read r1090：burns_active=[] queue_next=[] 实读·heartbeat 新鲜": 1,
    "本机 bm-c 实例·heartbeat 新鲜实读 r1090 窗·队列空转 idle": 1,
    "引擎实况注记（本机 bm-c 实例 heartbeat 新鲜 r1090 窗实读": 1,
    "--wave 268/finalize --wave 268": 1,
    "§5.5 W269+ 投影承接机证": 1,
    "n1_w268": 4, "n1_w267": 6, "_w268bmc": 4, "_w267bmc": 1,
    "W268": 33, "W267": 62, "W266": 4, "W265": 4, "W264": 3, "W263": 2, "W262": 1, "W261": 1, "W260": 1,
    "W259": 1, "W258": 1, "W257": 1, "W256": 1,
    "engine_owner 行 257 注册在册（表尾": 1,
    "prev=**届时空窗活链头 derive 禁手抄**": 1,
    "（**A 面=STAIRCASE-AFFECTS-A": 1,
    "entry rng seed=**604_901+j**": 1,
    "exit rng=**606_901+j**": 1,
    "probe W269+ 投影 A naive 606_901..608_900 CLEAN hops=0": 1,
    "5. **W269+ 投影（probe 机证 leg4": 1,
    "本件=席位窗后首窗冻结件；五面冻结拼接脚本": 1,
    "（gate0.5 绿·编辑器 loud abort 兜底）**。": 1,
    "owner per chain-order law）**】】）": 1,
    "（见 §5 item5）。": 1,
    "seed_admit_gate rc0 双带 FREE": 1,
    "n_eff_held_equal 996,335": 1,
    "注册+烧录+finalize 全落地": 2,
    "席位时即解锁": 2,
    "（占位·finalize one-pass 后回填": 1,
    "（占位·finalize 同窗回填": 1,
}

VMAP_ZEROS = [
    "1,013,935", "589,720", "607_101..609_100", "609_101..609_300", "609_101..611_100", "609_301..609_500",
    "−0.09273778", "0.24505168", "−0.09256686", "0.3120", "0.0002 在带内", "14:0x", "13:5x",
    "MSG-20261018-1407", "d630d043b9", "f1ec8231c7", "8bc7ac759e", "8d0e7bdb1", "78af85566",
    "_w269bmc", "n1_w269", "W270p_", "W270+ 投影",
    "第 88 枚", "第 259 波", "第八十八枚", "池第 267 枚", "波号 269", "零 269 行",
    "engine_owner==bm-c 87 行注册", "bmc_rows=87",
    "第十九次连续 A-hop", "第十九次连续 above-own-A", "连续十八波", "共二百六十七面",
    "键 W268 实测 K-lift", "line_pre_w268 1.1959", "line_merged@K587,520",
    "（W268 注册+烧录+finalize 全落地）",
    "waits-upstream ARMED", "GATED on", "finalize PENDING", "07:0x", "19:2x", "10:2x", "让路态", "queue_depth",
]

def xf(t):
    for o, n in VMAP:
        t = t.replace(o, n)
    return t

report = {"t0_floors": {}, "t0_zeros": {}, "t1_residuals": {}, "post_legs_t1": {}, "blocks_t1": {},
          "classification": {}, "live": {}}
fail = []
for o, f in VMAP_FLOORS.items():
    c = T0.count(o)
    report["t0_floors"][o] = c
    if c < f:
        fail.append("T0 FLOOR %r count=%d floor=%d" % (o, c, f))
for o in VMAP_ZEROS:
    c = T0.count(o)
    report["t0_zeros"][o] = c
    if c:
        fail.append("T0 ZERO %r count=%d (expect 0)" % (o, c))

T1 = xf(T0)
for ph in (P1, P2, P3):
    c = T1.count(ph)
    report["t1_residuals"]["placeholder_" + ph] = c
    if c:
        fail.append("T1 placeholder %r leftover=%d" % (ph, c))

# block spans on T1 (markers identical to the derive BLOCKS)
BLOCKS = [
    ("b_title", "engine_owner 行 257 注册在册（表尾", "owner per chain-order law）**】】）"),
    ("b_prev", "prev=**届时空窗活链头 derive 禁手抄**", "（机械算·投影面仅披露·finalize 运行时按 registry 键 derive 免疫）。"),
    ("b_band", "（**A 面=STAIRCASE-AFFECTS-A", "（见 §5 item5）。"),
    ("b3_a", "entry rng seed=**604_901+j**", "；p=`BASELINE_P"),
    ("b3_b", "exit rng=**606_901+j**", "；p_exit=`P_EXIT=0.05`"),
    ("b_claim_proj", "probe W269+ 投影 A naive 606_901..608_900 CLEAN hops=0", "never transcribe r587**）"),
    ("b5_projection", "5. **W269+ 投影（probe 机证 leg4", "verify at W269 prereg，hop 链逐跳在 probe 回执。"),
    ("b_gated", "本件=席位窗后首窗冻结件；五面冻结拼接脚本", "（gate0.5 绿·编辑器 loud abort 兜底）**。"),
]
spans = []
for name, sm, em in BLOCKS:
    c = T1.count(sm)
    report["blocks_t1"][name + ":start"] = c
    if c != 1:
        fail.append("T1 BLOCK %s start-marker count=%d (expect 1)" % (name, c))
    i = T1.index(sm)
    j = T1.find(em, i)
    report["blocks_t1"][name + ":end_found"] = (j > i)
    if j <= i:
        fail.append("T1 BLOCK %s end-marker missing" % name)
        continue
    spans.append((name, i, j + len(em)))

def classify(tok):
    """returns (total, interior, live) for token occurrences in T1 vs block spans"""
    total = interior = 0
    start = 0
    while True:
        k = T1.find(tok, start)
        if k < 0:
            break
        total += 1
        if any(s <= k < e for _, s, e in spans):
            interior += 1
        start = k + 1
    return total, interior, total - interior

for tok in ["W269", "W270", "R269", "R270", "604_901..606_900", "606_901..607_100",
            "606_901..608_900", "604_701..606_700", "604_901..605_100", "12:2x",
            "第十七次连续 A-hop", "第十八次连续 A-hop", "第十八次连续 above-own-A",
            "连续十七波", "共二百六十六面", "1,011,735", "585,320", "604_900+1", "606_900+1",
            "607_101..607_300", "W269+ 投影", "W269p_", "verify at W269 prereg",
            "n1_w268", "_w268bmc", "MSG-20261018-1229", "b9ad2f1119", "7b9e9377",
            "df55e3fab9", "99166404f2", "eb5c74dbf7", "engine_owner 行 257",
            "r1089", "r1090", "W271", "W272"]:
    t, i_, l = classify(tok)
    report["classification"][tok] = {"total": t, "interior": i_, "live": l}

# POST_LEG needles on T1 (post-roll faces) -- measured
POST_LEGS_CHECK = [
    "12:2x",
    "（W268 实测键 **−0.09273843**·K=585,320 合并池·W268-only 实测 **−0.09269745**）",
    "W2..W268 共二百六十六面实测 mu 稳定先例",
    "W268-only vs merged 实差 0.0000 在带内",
    "键 **0.24505587**=W268 合并池实测",
    "与 W268 A 档 p95（**0.3058** 实测锚）",
    "键 W268 实测 K-lift **−0.0001**·line_merged@K585,320 **1.1958**·line_pre_w267 1.1959·n_eff_held_equal 996,335",
    "→W265 **0.000322**→W266 **0.000321**→W267 **0.000321**→W268 **0.000320**→W269 投影 0.000320】",
    "W1..W268 已落账 585,320 实测",
    "bm-c r1089 W268 §7 范式",
    "bm-c r1089 W268 §8 范式",
    "本窗 free RAM ~0.1GB（bm-c 底盘常驻·24G 物理内存机·CEO 周末用机态·RAM 临界挤占=GPU 道主进程 python 4.5G 实测·GPU=gen-only 车道满载烧批在飞（nvidia-smi 实读 100%·15.6G VRAM 占用·MV PACK-A i2v wave-1 在飞）·LLM 态已退役 gen 专用车道·引擎队列空转·CPU 车道独立如实注记）",
    "·W244 冻结窗 41.9G bm-a 实锚·W264 冻结窗 26G bm-a 实锚·W265 冻结窗 7G bm-c 实锚·W266 冻结窗 3G bm-c 实锚·W267 冻结窗 ~5G bm-c 实锚·W268 冻结窗 ~0.1G bm-c 实锚）",
]
for o in POST_LEGS_CHECK:
    report["post_legs_t1"][o[:60]] = T1.count(o)

# live faces
try:
    import psutil
    ram = psutil.virtual_memory().available / (1024 ** 3)
    report["live"]["ram_available_gb"] = round(ram, 2)
except Exception as e:
    report["live"]["ram_err"] = repr(e)
try:
    r = subprocess.run(["nvidia-smi", "--query-gpu=utilization.gpu,memory.used,memory.total",
                        "--format=csv,noheader,nounits"], capture_output=True, text=True, timeout=20)
    report["live"]["nvidia_smil"] = r.stdout.strip()
except Exception as e:
    report["live"]["nvidia_err"] = repr(e)

report["fail"] = fail
io.open(OUTJ, "w", encoding="utf-8", newline="\n").write(json.dumps(report, ensure_ascii=False, indent=1))
print("PROBE rc=%s | t0_floors=%d zeros=%d | fails=%d" % (
    0 if not fail else 1, len(report["t0_floors"]), len(report["t0_zeros"]), len(fail)))
for f in fail:
    print("FAIL: %s" % f)
print("--- T1 classification (total/interior/live) ---")
for k, v in report["classification"].items():
    print("  %-24s %3d %3d %3d" % (k, v["total"], v["interior"], v["live"]))
print("--- POST_LEG needles on T1 ---")
for k, v in report["post_legs_t1"].items():
    print("  %2d  %s" % (v, k))
print("--- LIVE ---")
print(json.dumps(report["live"], ensure_ascii=False))
