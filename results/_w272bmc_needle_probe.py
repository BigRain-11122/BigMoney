# -*- coding: utf-8 -*-
# r1099 bm-c: W272 prereg derive NEEDLE FACTS PROBE (r1077 measured-counts law).
# Measures every needle count on T0 (frozen W271 face @ f75b18c862, 23,336B sha256_16
# f8b4a755d81bfbe5) + T1 (post-VMAP roll simulation) + block in/out classification,
# ZERO transformation writes. Evidence receipt -> results/_w272bmc_needle_probe.json.
# Canon-clone of the _w271bmc_needle_probe.py pattern (r1096 lineage) per age()
# machine-needle law, shift-map one generation.
import io, os, re, json, hashlib

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(REPO, "results", "_w272bmc_w271_frozen_face.txt")
T0 = io.open(SRC, encoding="utf-8", newline="").read()
assert len(T0.encode("utf-8")) == 23336
assert hashlib.sha256(T0.encode("utf-8")).hexdigest()[:16] == "f8b4a755d81bfbe5"

P1, P2, P3 = "\x01W\x01", "\x01N\x01", "\x01B\x01"
VMAP = [
    ("A-ext seed=611_501..613_500", "A-ext seed=613_701..615_700"),
    ("B-ext exit seed=613_501..613_700", "B-ext exit seed=615_701..615_900"),
    ("entry rng=**611_501+j**（与 A[j] 同源配对语义逐字", "entry rng=**613_701+j**（与 A[j] 同源配对语义逐字"),
    ("席位公示=MSG-20261018-175x-bmc-w271-seat 已推 origin 87d2697cdc r565 律（bm-c r1095 席·queue-head seat-first lane）",
     "席位公示=MSG-20261018-191x-bmc-w272-seat 已推 origin f608ff1cee r565 律（bm-c r1098 席·queue-head seat-first lane）"),
    ("席位公示 MSG-20261018-175x-bmc-w271-seat 先推 origin 87d2697cdc r565 律",
     "席位公示 MSG-20261018-191x-bmc-w272-seat 先推 origin f608ff1cee r565 律"),
    ("波号 271", "波号 272"),
    ("r1095 席位窗实跑：origin inbox 零 W271 席位外机命中", "r1098 席位窗实跑：origin inbox 零 W272 席位外机命中"),
    ("零 271 行", "零 272 行"),
    ("零 skip-ahead W272/W273 席位声明", "零 skip-ahead W273/W274 席位声明"),
    ("池第 269 枚", "池第 270 枚"),
    ("第 261 波", "第 262 波"),
    ("bm-c 第九十枚自有波", "bm-c 第九十一枚自有波"),
    ("probe leg0 bmc_rows=89 attempt-continuity face（r1095 窗算法·bm-c own seat+bmc live rows 89 实读）——freeze 时 live derive bmc rows 89+候选=第 90 枚 EXACT",
     "probe leg0 bmc_rows=90 attempt-continuity face（r1098 窗算法·bm-c own seat+bmc live rows 90 实读）——freeze 时 live derive bmc rows 90+候选=第 91 枚 EXACT"),
    ("engine_owner==bm-c 89 行注册", "engine_owner==bm-c 90 行注册"),
    ("saturation_engine.py status live-read r1096：burns_active=[] queue_next=[] 实读·heartbeat 新鲜",
     "saturation_engine.py status live-read r1099：burns_active=[] queue_next=[] 实读·heartbeat 新鲜"),
    ("本机 bm-c 实例·heartbeat 新鲜实读 r1096 窗·队列空转 idle",
     "本机 bm-c 实例·heartbeat 新鲜实读 r1099 窗·队列空转 idle"),
    ("引擎实况注记（本机 bm-c 实例 heartbeat 新鲜 r1096 窗实读",
     "引擎实况注记（本机 bm-c 实例 heartbeat 新鲜 r1099 窗实读"),
    ("--wave 271/finalize --wave 271", "--wave 272/finalize --wave 272"),
    ("§5.5 W272+ 投影承接机证", "§5.5 W273+ 投影承接机证"),
    ("n1_w271", P2), ("n1_w270", "n1_w271"), (P2, "n1_w272"),
    ("_w271bmc", P3), ("_w270bmc", "_w271bmc"), (P3, "_w272bmc"),
    ("W271", P1), ("W270", "W271"), ("W269", "W270"), ("W268", "W269"), ("W267", "W268"),
    ("W266", "W267"), ("W265", "W266"), ("W264", "W265"), ("W263", "W264"), ("W262", "W263"),
    ("W261", "W262"), ("W260", "W261"), ("W259", "W260"), ("W258", "W259"), (P1, "W272"),
]
T1 = T0
for o, n in VMAP:
    T1 = T1.replace(o, n)

BLOCKS = [
    ("b_title", "engine_owner 行 260 注册在册（表尾", "owner per chain-order law）**】】）"),
    ("b_prev", "prev=**届时空窗活链头 derive 禁手抄**", "（机械算·投影面仅披露·finalize 运行时按 registry 键 derive 免疫）。"),
    ("b_band", "（**A 面=STAIRCASE-AFFECTS-A", "（见 §5 item5）。"),
    ("b3_a", "entry rng seed=**611_501+j**", "；p=`BASELINE_P"),
    ("b3_b", "exit rng=**613_501+j**", "；p_exit=`P_EXIT=0.05`"),
    ("b_claim_proj", "probe W272+ 投影 A naive 613_501..615_500 CLEAN hops=0", "never transcribe r587**）"),
    ("b5_projection", "5. **W272+ 投影（probe 机证 leg4", "verify at W272 prereg，hop 链逐跳在 probe 回执。"),
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
    "A-ext seed=611_501..613_500", "B-ext exit seed=613_501..613_700",
    "entry rng=**611_501+j**（与 A[j] 同源配对语义逐字",
    "席位公示=MSG-20261018-175x-bmc-w271-seat 已推 origin 87d2697cdc r565 律（bm-c r1095 席·queue-head seat-first lane）",
    "席位公示 MSG-20261018-175x-bmc-w271-seat 先推 origin 87d2697cdc r565 律",
    "波号 271", "r1095 席位窗实跑：origin inbox 零 W271 席位外机命中", "零 271 行",
    "零 skip-ahead W272/W273 席位声明", "池第 269 枚", "第 261 波", "bm-c 第九十枚自有波",
    "probe leg0 bmc_rows=89 attempt-continuity face（r1095 窗算法·bm-c own seat+bmc live rows 89 实读）——freeze 时 live derive bmc rows 89+候选=第 90 枚 EXACT",
    "engine_owner==bm-c 89 行注册",
    "saturation_engine.py status live-read r1096：burns_active=[] queue_next=[] 实读·heartbeat 新鲜",
    "本机 bm-c 实例·heartbeat 新鲜实读 r1096 窗·队列空转 idle",
    "引擎实况注记（本机 bm-c 实例 heartbeat 新鲜 r1096 窗实读",
    "--wave 271/finalize --wave 271", "§5.5 W272+ 投影承接机证",
    # lowercase rolls
    "n1_w271", "n1_w270", "_w271bmc", "_w270bmc", "n1_w269", "_w269bmc",
    # wave rolls (measure deep for roll-depth audit)
    "W271", "W270", "W269", "W268", "W267", "W266", "W265", "W264", "W263", "W262", "W261", "W260",
    "W259", "W258", "W257", "W256", "W255", "W254", "W253", "W252", "W251", "W250", "W249",
    "W248", "W247", "W246", "W245", "W244", "W239", "W272", "W273",
    # block markers + structural stability needles
    "engine_owner 行 260 注册在册（表尾", "prev=**届时空窗活链头 derive 禁手抄**",
    "（**A 面=STAIRCASE-AFFECTS-A", "entry rng seed=**611_501+j**", "exit rng=**613_501+j**",
    "probe W272+ 投影 A naive 613_501..615_500 CLEAN hops=0",
    "5. **W272+ 投影（probe 机证 leg4", "本件=席位窗后首窗冻结件；五面冻结拼接脚本",
    "（gate0.5 绿·编辑器 loud abort 兜底）**。", "owner per chain-order law）**】】）",
    "（见 §5 item5）。", "seed_admit_gate rc0 双带 FREE", "n_eff_held_equal 1,016,135",
    "注册+烧录+finalize 全落地", "席位时即解锁", "（占位·finalize one-pass 后回填", "（占位·finalize 同窗回填",
    "17:2x", "17:0x", "16:0x", "15:4x", "15:2x", "18:3x", "18:4x", "19:1x",
    # band faces (current + old generations)
    "611_501..613_500", "613_501..613_700", "611_301..611_500", "611_101..611_300",
    "611_101..613_100", "611_501..611_500", "609_301..611_300", "609_101..609_300",
    "609_101..611_100", "609_301..609_500", "607_101..609_100", "607_101..607_300",
    "606_901..608_900", "606_901..607_100", "604_901..606_900",
    "613_501..615_500", "613_701..613_900", "613_701..615_700", "615_701..615_900",
    "615_701..617_700", "615_901..616_100",
    "W273p_", "W272p_", "W272p_B_lands_inside_W272p_A_naive",
    # ordinals
    "第二十次连续 A-hop", "第二十一次连续 above-own-A", "第二十一次连续 A-hop", "连续二十波",
    "第十九次连续 A-hop", "第二十次连续 above-own-A", "连续十九波", "第二十二次连续 A-hop",
    "第二十二次连续 above-own-A", "连续二十一波",
    "hops=1", "hops=0", "611_500+1", "613_500+1", "613_700+1", "615_700+1",
    # live numeric/commit faces
    "−0.09272692", "0.24507005", "−0.09170727", "0.3268", "键 W270 实测 K-lift",
    "line_pre_w270", "实差 0.0010", "共二百六十九面", "W2..W270", "W1..W270", "W136..W270",
    "bm-c r1095 W270 §7 范式", "本窗 free RAM ~3.3GB", "W263 冻结窗 26G bm-a 实锚",
    "（上游 W270 席位已闭链", "（W270 注册+烧录+finalize 全落地）",
    "1,016,135", "591,920", "1,018,335", "609_300+1", "611_300+1",
    "line_merged@K591,920", "K=591,920", "r1095 W270 §7 范式", "MSG-20261018-175x",
    "bmc rows 89+候选", "第 90 枚", "第 261 波", "第九十枚", "**594,120 投影**",
    "W264 冻结窗 26G", "W265 冻结窗 7G", "W266 冻结窗 3G", "12:2x", "23:5x", "23:1x",
    # zero-floor candidates (next-gen faces; expect 0 on T0)
    "waits-upstream ARMED", "GATED on", "finalize PENDING", "queue_depth",
    "_w272bmc", "n1_w272", "第 91 枚", "第 262 波", "第九十一枚", "池第 270 枚", "波号 272", "零 272 行",
    "engine_owner==bm-c 90 行注册", "bmc_rows=90", "bmc rows 90+候选",
    "共二百七十面", "1,020,535", "596,320", "594,120",
    "−0.09276412", "0.24509040", "−0.10277223", "0.3042",
    "实差 0.0100 在带内", "line_pre_w271 1.1963", "line_merged@K594,120", "K=594,120",
    "r1097 W271 §7 范式", "（W271 注册+烧录+finalize 全落地）",
    "MSG-20261018-191x", "键 W271 实测 K-lift",
    "f75b18c862", "7dd091eef1", "a035552321", "037445477b", "e0a21b817d", "f608ff1cee",
    "本窗 free RAM ~1.4GB",
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
    "semu_chain": grab("→W267", 30, 220),
    "sec4_k": grab("已落账", 30, 40),
    "paradigm7": grab("§7 范式", 40, 10),
    "paradigm8": grab("§8 范式", 40, 10),
    "ram_face": grab("本窗 free RAM", 0, 320),
    "ram_ledger": grab("冻结窗 41.9G", 10, 360),
    "mu_stability": grab("共二百六十九面", 30, 30),
    "stamp_172x_ctx": [T1[m.start()-60:m.start()+30].replace("\n", "\\n")
                       for m in re.finditer(re.escape("17:2x"), T1)],
    "stamp_170x_ctx": [T1[m.start()-60:m.start()+30].replace("\n", "\\n")
                       for m in re.finditer(re.escape("17:0x"), T1)],
}

# band classification on T1 (in/out of blocks)
report["t1_band_classification"] = {}
for band in ["611_501..613_500", "613_501..613_700", "611_301..611_500", "611_101..611_300",
             "611_101..613_100", "611_501..611_500", "609_301..611_300", "609_101..609_300",
             "609_101..611_100", "609_301..609_500", "607_101..609_100", "607_101..607_300",
             "606_901..608_900", "606_901..607_100", "604_901..606_900",
             "613_501..615_500", "613_701..613_900"]:
    report["t1_band_classification"][band] = classify(band, T1)

# roll-depth audit: W-numbers below the roll floor that survive OUTSIDE blocks on T1
report["t1_low_w_survivors_outside"] = {}
for w in ["W257", "W256", "W255", "W254", "W253", "W252", "W251", "W250", "W249",
          "W248", "W247", "W246", "W245", "W244", "W239", "W272", "W273"]:
    cls = classify(w, T1)
    if cls["outside"]:
        report["t1_low_w_survivors_outside"][w] = cls

# lowercase context locations on T0
for tok in ["n1_w271", "n1_w270", "_w271bmc", "_w270bmc"]:
    report["t0_%s_contexts" % tok.replace("=", "")] = [
        T0[m.start()-30:m.start()+60].replace("\n", "\\n")
        for m in re.finditer(re.escape(tok), T0)]

out = os.path.join(REPO, "results", "_w272bmc_needle_probe.json")
with open(out, "w", encoding="utf-8") as f:
    json.dump(report, f, ensure_ascii=False, indent=1)
print("NEEDLE PROBE OK -> %s" % out)
print("placeholders left: %r" % report["t1_placeholders_left"])
print("blocks: %r" % [(b["name"], b["marker_count"], b["span_ok"]) for b in report["blocks"]])
print("low-W/W272/W273 survivors outside blocks on T1: %r" % report["t1_low_w_survivors_outside"])
print("t1 band classification:")
for k, v in report["t1_band_classification"].items():
    print("  %s total=%d inside=%d outside=%d" % (k, v["total"], v["inside_blocks"], v["outside"]))
print("key t0 counts: W271=%d W270=%d n1_w271=%d n1_w270=%d _w271bmc=%d _w270bmc=%d 17:2x=%d 17:0x=%d" % (
    t0_counts["W271"], t0_counts["W270"], t0_counts["n1_w271"], t0_counts["n1_w270"],
    t0_counts["_w271bmc"], t0_counts["_w270bmc"], t0_counts["17:2x"], t0_counts["17:0x"]))
