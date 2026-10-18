# -*- coding: utf-8 -*-
# r1096 bm-c: W271 prereg derive NEEDLE FACTS PROBE (r1077 measured-counts law).
# Measures every needle count on T0 (frozen W270 face @ 3bb8b9308e) + T1 (post-VMAP roll
# simulation) + block in/out classification, ZERO transformation writes. Evidence receipt ->
# results/_w271bmc_needle_probe.json. Canon-clone of the _w270bmc_needle_probe.py pattern
# (r1094 lineage) per age() machine-needle law, shift-map one generation.
import io, os, re, json, hashlib

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(REPO, "results", "_w271bmc_w270_frozen_face.txt")
T0 = io.open(SRC, encoding="utf-8", newline="").read()
assert len(T0.encode("utf-8")) == 23259
assert hashlib.sha256(T0.encode("utf-8")).hexdigest()[:16] == "3aa0b98239369608"

P1, P2, P3 = "\x01W\x01", "\x01N\x01", "\x01B\x01"
VMAP = [
    ("A-ext seed=609_301..611_300", "A-ext seed=611_501..613_500"),
    ("B-ext exit seed=611_301..611_500", "B-ext exit seed=613_501..613_700"),
    ("entry rng=**609_301+j**（与 A[j] 同源配对语义逐字", "entry rng=**611_501+j**（与 A[j] 同源配对语义逐字"),
    ("席位公示=MSG-20261018-1605-bmc-w270-seat 已推 origin 9f480646f4 r565 律（bm-c r1094 席·queue-head seat-first lane）",
     "席位公示=MSG-20261018-175x-bmc-w271-seat 已推 origin 87d2697cd r565 律（bm-c r1095 席·queue-head seat-first lane）"),
    ("席位公示 MSG-20261018-1605-bmc-w270-seat 先推 origin 9f480646f4 r565 律",
     "席位公示 MSG-20261018-175x-bmc-w271-seat 先推 origin 87d2697cd r565 律"),
    ("波号 270", "波号 271"),
    ("r1094 席位窗实跑：origin inbox 零 W270 席位外机命中", "r1095 席位窗实跑：origin inbox 零 W271 席位外机命中"),
    ("零 270 行", "零 271 行"),
    ("零 skip-ahead W271/W272 席位声明", "零 skip-ahead W272/W273 席位声明"),
    ("池第 268 枚", "池第 269 枚"),
    ("第 260 波", "第 261 波"),
    ("bm-c 第八十九枚自有波", "bm-c 第九十枚自有波"),
    ("probe leg0 bmc_rows=88 attempt-continuity face（r1094 窗算法·bm-c own seat+bmc live rows 88 实读）——freeze 时 live derive bmc rows 88+候选=第 89 枚 EXACT",
     "probe leg0 bmc_rows=89 attempt-continuity face（r1095 窗算法·bm-c own seat+bmc live rows 89 实读）——freeze 时 live derive bmc rows 89+候选=第 90 枚 EXACT"),
    ("engine_owner==bm-c 88 行注册", "engine_owner==bm-c 89 行注册"),
    ("saturation_engine.py status live-read r1094：burns_active=[] queue_next=[] 实读·heartbeat 新鲜",
     "saturation_engine.py status live-read r1096：burns_active=[] queue_next=[] 实读·heartbeat 新鲜"),
    ("本机 bm-c 实例·heartbeat 新鲜实读 r1094 窗·队列空转 idle",
     "本机 bm-c 实例·heartbeat 新鲜实读 r1096 窗·队列空转 idle"),
    ("引擎实况注记（本机 bm-c 实例 heartbeat 新鲜 r1094 窗实读",
     "引擎实况注记（本机 bm-c 实例 heartbeat 新鲜 r1096 窗实读"),
    ("--wave 270/finalize --wave 270", "--wave 271/finalize --wave 271"),
    ("§5.5 W271+ 投影承接机证", "§5.5 W272+ 投影承接机证"),
    ("n1_w270", P2), ("n1_w269", "n1_w270"), (P2, "n1_w271"),
    ("_w270bmc", P3), ("_w269bmc", "_w270bmc"), (P3, "_w271bmc"),
    ("W270", P1), ("W269", "W270"), ("W268", "W269"), ("W267", "W268"), ("W266", "W267"),
    ("W265", "W266"), ("W264", "W265"), ("W263", "W264"), ("W262", "W263"), ("W261", "W262"),
    ("W260", "W261"), ("W259", "W260"), ("W258", "W259"), ("W257", "W258"), (P1, "W271"),
]
T1 = T0
for o, n in VMAP:
    T1 = T1.replace(o, n)

BLOCKS = [
    ("b_title", "engine_owner 行 259 注册在册（表尾", "owner per chain-order law）**】】）"),
    ("b_prev", "prev=**届时空窗活链头 derive 禁手抄**", "（机械算·投影面仅披露·finalize 运行时按 registry 键 derive 免疫）。"),
    ("b_band", "（**A 面=STAIRCASE-AFFECTS-A", "（见 §5 item5）。"),
    ("b3_a", "entry rng seed=**609_301+j**", "；p=`BASELINE_P"),
    ("b3_b", "exit rng=**611_301+j**", "；p_exit=`P_EXIT=0.05`"),
    ("b_claim_proj", "probe W271+ 投影 A naive 611_301..613_300 CLEAN hops=0", "never transcribe r587**）"),
    ("b5_projection", "5. **W271+ 投影（probe 机证 leg4", "verify at W271 prereg，hop 链逐跳在 probe 回执。"),
    ("b_gated", "本件=席位窗后首窗冻结件；五面冻结拼接脚本", "（gate0.5 绿·编辑器 loud abort 兜底）**。"),
]
spans = []
for name, sm, em in BLOCKS:
    c = T1.count(sm)
    i = T1.find(sm)
    j = T1.find(em, i) + len(em) if i >= 0 else -1
    spans.append((name, c, i, j))
def in_blocks(pos):
    return any(i <= pos < j for _, _, i, j in spans if j > 0)

def classify(needle, txt):
    total = txt.count(needle)
    positions = [m.start() for m in re.finditer(re.escape(needle), txt)]
    inside = sum(1 for p in positions if in_blocks(p))
    return {"total": total, "inside_blocks": inside, "outside": total - inside}

report = {"vmap_legs": len(VMAP), "t0_sha16": hashlib.sha256(T0.encode("utf-8")).hexdigest()[:16],
          "t1_placeholders_left": {k: T1.count(v) for k, v in (("P1", P1), ("P2", P2), ("P3", P3))},
          "blocks": [{"name": n, "marker_count": c, "span_ok": (j > i > -1)} for n, c, i, j in spans]}

# T0 floor measurements (measured, never assumed)
t0_counts = {}
for n in [
    # explicit-leg needles
    "A-ext seed=609_301..611_300", "B-ext exit seed=611_301..611_500",
    "entry rng=**609_301+j**（与 A[j] 同源配对语义逐字",
    "席位公示=MSG-20261018-1605-bmc-w270-seat 已推 origin 9f480646f4 r565 律（bm-c r1094 席·queue-head seat-first lane）",
    "席位公示 MSG-20261018-1605-bmc-w270-seat 先推 origin 9f480646f4 r565 律",
    "波号 270", "r1094 席位窗实跑：origin inbox 零 W270 席位外机命中", "零 270 行",
    "零 skip-ahead W271/W272 席位声明", "池第 268 枚", "第 260 波", "bm-c 第八十九枚自有波",
    "probe leg0 bmc_rows=88 attempt-continuity face（r1094 窗算法·bm-c own seat+bmc live rows 88 实读）——freeze 时 live derive bmc rows 88+候选=第 89 枚 EXACT",
    "engine_owner==bm-c 88 行注册",
    "saturation_engine.py status live-read r1094：burns_active=[] queue_next=[] 实读·heartbeat 新鲜",
    "本机 bm-c 实例·heartbeat 新鲜实读 r1094 窗·队列空转 idle",
    "引擎实况注记（本机 bm-c 实例 heartbeat 新鲜 r1094 窗实读",
    "--wave 270/finalize --wave 270", "§5.5 W271+ 投影承接机证",
    # lowercase rolls
    "n1_w270", "n1_w269", "_w270bmc", "_w269bmc",
    # wave rolls (measure deep for roll-depth audit)
    "W270", "W269", "W268", "W267", "W266", "W265", "W264", "W263", "W262", "W261", "W260",
    "W259", "W258", "W257", "W256", "W255", "W254", "W253", "W252", "W251", "W250", "W249",
    "W248", "W247", "W246", "W245", "W244", "W239",
    # block markers + structural stability needles
    "engine_owner 行 259 注册在册（表尾", "prev=**届时空窗活链头 derive 禁手抄**",
    "（**A 面=STAIRCASE-AFFECTS-A", "entry rng seed=**609_301+j**", "exit rng=**611_301+j**",
    "probe W271+ 投影 A naive 611_301..613_300 CLEAN hops=0",
    "5. **W271+ 投影（probe 机证 leg4", "本件=席位窗后首窗冻结件；五面冻结拼接脚本",
    "（gate0.5 绿·编辑器 loud abort 兜底）**。", "owner per chain-order law）**】】）",
    "（见 §5 item5）。", "seed_admit_gate rc0 双带 FREE", "n_eff_held_equal 996,335",
    "注册+烧录+finalize 全落地", "席位时即解锁", "（占位·finalize one-pass 后回填", "（占位·finalize 同窗回填",
    "15:4x", "15:2x", "16:0x",
    # band faces (current + old generations)
    "609_301..611_300", "611_301..611_500", "609_101..609_300", "609_101..611_100",
    "609_301..609_500", "607_101..609_100", "607_101..607_300", "606_901..608_900",
    "606_901..607_100", "604_901..606_900",
    "W271p_A_naive", "W271p_B_naive", "W271p_B_lands_inside_W271p_A_naive",
    # ordinals
    "第十九次连续 A-hop", "第二十次连续 above-own-A", "第二十次连续 A-hop", "连续十九波",
    "第十八次连续 A-hop", "第十九次连续 above-own-A", "连续十八波",
    "hops=1", "hops=0", "609_100+1", "611_300+1", "611_500+1", "613_500+1",
    # live numeric/commit faces
    "−0.09273072", "0.24506175", "−0.09084568", "0.3158", "键 W269 实测 K-lift",
    "line_pre_w269", "实差 0.0019", "共二百六十八面", "W2..W269", "W1..W269",
    "bm-c r1093 W269 §7 范式", "本窗 free RAM ~2.1GB", "W263 冻结窗 26G bm-a 实锚",
    "（上游 W269 席位已闭链", "（W269 注册+烧录+finalize 全落地）",
    "1,016,135", "591,920", "609_300+1",
    "line_merged@K589,720", "K=589,720", "r1093 W269 §7 范式", "MSG-20261018-1605",
    "bmc rows 88+候选", "第 89 枚", "第 259 波", "第八十八枚",
    "W264 冻结窗 26G", "W265 冻结窗 7G", "W266 冻结窗 3G", "12:2x",
    # zero-floor candidates (next-gen faces; expect 0 on T0)
    "waits-upstream ARMED", "GATED on", "finalize PENDING", "queue_depth",
    "_w271bmc", "n1_w271", "W272p_", "第 90 枚", "第 261 波", "第九十枚", "池第 269 枚",
    "波号 271", "零 271 行", "engine_owner==bm-c 89 行注册", "bmc_rows=89",
    "第二十一次连续 A-hop", "第二十一次连续 above-own-A", "连续二十波", "共二百六十九面",
    "1,018,335", "594,120", "611_501..613_500", "613_501..613_700",
    "613_501..615_500", "613_701..613_900", "17:0x", "17:2x",
    "3bb8b9308e", "1c814343e", "6c1aee751d", "ae98b97a10", "e4b015cbb", "87d2697cd",
    "−0.09272692", "0.24507005", "−0.09170727", "0.3268",
    "实差 0.0010 在带内", "line_pre_w270 1.1962", "line_merged@K591,920", "K=591,920",
    "r1095 W270 §7 范式", "（W270 注册+烧录+finalize 全落地）",
    "MSG-20261018-175x", "bmc rows 89+候选", "键 W270 实测 K-lift",
]:
    t0_counts[n] = T0.count(n)
report["t0_counts"] = t0_counts

# T1 post-roll face extraction (exact needles for POST_LEGS)
def grab(anchor, before=0, after=400):
    i = T1.find(anchor)
    return T1[max(0, i - before): i + after] if i >= 0 else None

report["t1_faces"] = {
    "item1_keys": grab("实测键", 30, 120),
    "diff_face": grab("实差", 30, 60),
    "sigma_face": grab("合并池实测", 40, 40),
    "p95_face": grab("实测锚", 40, 20),
    "klift_face": grab("实测 K-lift", 10, 160),
    "semu_chain": grab("→W267", 30, 200),
    "sec4_k": grab("已落账", 30, 40),
    "paradigm7": grab("§7 范式", 40, 10),
    "paradigm8": grab("§8 范式", 40, 10),
    "ram_face": grab("本窗 free RAM", 0, 320),
    "ram_ledger": grab("冻结窗 41.9G", 10, 340),
    "mu_stability": grab("共二百六十八面", 30, 30),
}

# band classification on T1 (in/out of blocks)
report["t1_band_classification"] = {}
for band in ["609_301..611_300", "611_301..611_500", "609_101..609_300", "609_101..611_100",
             "609_301..609_500", "607_101..609_100", "607_101..607_300", "606_901..608_900",
             "606_901..607_100", "604_901..606_900"]:
    report["t1_band_classification"][band] = classify(band, T1)

# roll-depth audit: W-numbers below the roll floor that survive OUTSIDE blocks on T1
report["t1_low_w_survivors_outside"] = {}
for w in ["W256", "W255", "W254", "W253", "W252", "W251", "W250", "W249", "W248",
          "W247", "W246", "W245", "W244", "W239"]:
    cls = classify(w, T1)
    if cls["outside"]:
        report["t1_low_w_survivors_outside"][w] = cls

# n1_w270/_w270bmc context location on T0 (to identify what the lowercase rolls touch)
report["t0_n1w270_contexts"] = [T0[m.start()-30:m.start()+60].replace("\n", "\\n")
                                for m in re.finditer(re.escape("n1_w270"), T0)]
report["t0_n1w269_contexts"] = [T0[m.start()-30:m.start()+60].replace("\n", "\\n")
                                for m in re.finditer(re.escape("n1_w269"), T0)]
report["t0__w270bmc_contexts"] = [T0[m.start()-30:m.start()+60].replace("\n", "\\n")
                                  for m in re.finditer(re.escape("_w270bmc"), T0)]
report["t0__w269bmc_contexts"] = [T0[m.start()-30:m.start()+60].replace("\n", "\\n")
                                  for m in re.finditer(re.escape("_w269bmc"), T0)]

out = os.path.join(REPO, "results", "_w271bmc_needle_probe.json")
with open(out, "w", encoding="utf-8") as f:
    json.dump(report, f, ensure_ascii=False, indent=1)
print("NEEDLE PROBE OK -> %s" % out)
print("placeholders left: %r" % report["t1_placeholders_left"])
print("blocks: %r" % [(b["name"], b["marker_count"], b["span_ok"]) for b in report["blocks"]])
print("low-W survivors outside blocks on T1: %r" % report["t1_low_w_survivors_outside"])
print("t1 band classification:")
for k, v in report["t1_band_classification"].items():
    print("  %s total=%d inside=%d outside=%d" % (k, v["total"], v["inside_blocks"], v["outside"]))
print("key t0 counts: W270=%d W269=%d n1_w270=%d n1_w269=%d _w270bmc=%d _w269bmc=%d 15:4x=%d" % (
    t0_counts["W270"], t0_counts["W269"], t0_counts["n1_w270"], t0_counts["n1_w269"],
    t0_counts["_w270bmc"], t0_counts["_w269bmc"], t0_counts["15:4x"]))
