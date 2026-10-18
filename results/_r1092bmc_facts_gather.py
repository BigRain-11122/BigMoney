# -*- coding: utf-8 -*-
# r1092 bm-c: W269 prereg derive -- Phase-1 facts gather (zero-transcription evidence base).
# Extracts the frozen W268 prereg face @ freeze commit f1ec8231c7 (pre-backfill, r1052/r1049 law),
# machine-reads the W268 finalize anchors (fivekeys + results json), chain commit timestamps,
# W269 seat receipt asserts, live RAM/engine faces, and raw token counts on T0 for the
# needle floors (MEASURED, r1077 law). Read-only except the extraction target file.
import subprocess, hashlib, json, os, sys, re

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GIT = "C:/Program Files/Git/cmd/git.exe"
FREEZE_SHA = "f1ec8231c7"
SRC_PATH = "research/PERPETUAL_N1_W268_PREREG.md"
OUT = os.path.join(REPO, "results", "_w269bmc_w268_frozen_face.txt")

def git_bytes(args):
    r = subprocess.run([GIT] + args, capture_output=True, cwd=REPO)
    if r.returncode != 0:
        raise SystemExit("git fail %r: %s" % (args, r.stderr.decode("utf-8", "replace")))
    return r.stdout

def git_out(args):
    return git_bytes(args).decode("utf-8", "replace").strip()

# --- 1. extract frozen face (binary-safe) ---
blob = git_bytes(["show", "%s:%s" % (FREEZE_SHA, SRC_PATH)])
with open(OUT, "wb") as f:
    f.write(blob)
T0 = blob.decode("utf-8")
size = len(blob)
sha1 = git_out(["hash-object", OUT])
rev_blob = git_out(["rev-parse", "%s:%s" % (FREEZE_SHA, SRC_PATH)])
head_twin = git_out(["rev-parse", "HEAD:%s" % SRC_PATH])
sha256_16 = hashlib.sha256(blob).hexdigest()[:16]
print("FROZEN FACE: %d bytes | sha1 %s | sha256_16 %s" % (size, sha1, sha256_16))
print("  rev-parse @freeze: %s (expect == disk sha1)" % rev_blob)
print("  HEAD twin (post-backfill, DISCLOSED not used): %s" % head_twin)
assert sha1 == rev_blob, "disk extraction != freeze-commit blob"

# --- 2. chain commit timestamps ---
for sha in (FREEZE_SHA, "8bc7ac759e", "d630d043b9", "8d0e7bdb1", "78af85566", "be60d5e075"):
    ts = git_out(["show", "-s", "--format=%h %ci", sha])
    print("COMMIT: %s" % ts)
fin_land = git_out(["log", "-1", "--format=%h", "--", "results/perpetual_faces/n1_w268_results.json"])
print("FINALIZE PRODUCT landed by: %s" % fin_land)
seat_land = git_out(["log", "-1", "--format=%h %ci", "--", "fleet/inbox/MSG-20261018-1407-bmc-w269-seat.md"])
print("W269 SEAT MSG landed by: %s" % seat_land)

# --- 3. W268 finalize anchors (fivekeys receipt, machine-read) ---
with open(os.path.join(REPO, "results", "_r1091bmc_w268_fivekeys.json"), encoding="utf-8") as f:
    fk = json.load(f)
print("FIVEKEYS all_pass: %r" % fk.get("all_pass"))
print("  merged: mu=%.8f sigma=%.8f k=%s" % (fk["merged"]["mu"], fk["merged"]["sigma"], fk["merged"]["k"]))
print("  se_mu_k587520: %r" % fk["merged"].get("se_mu_k587520"))
print("  w268_only.mu: %.8f" % fk["w268_only"]["mu"])
print("  a_band.full_sharpe_p95: %r" % fk["a_band"]["full_sharpe_p95"])
print("  skill_line: k_lift_delta=%r n_eff_held=%s line_pre_w268=%r line_merged_587520=%r" % (
    fk["skill_line"]["k_lift_delta"], fk["skill_line"]["n_eff_held"],
    fk["skill_line"].get("line_pre_w268"), fk["skill_line"].get("line_merged_587520")))
print("  ledger_identity: %r exact=%r" % (fk["ledger_identity"]["total"], fk["ledger_identity"]["exact"]))
for c in fk["checks"]:
    print("  check %-44s value=%-14r pass=%r" % (c["name"], c["value"], c["pass"]))
print("  merged-vs-w268only diff @8dp: %.8f" % (fk["merged"]["mu"] - fk["w268_only"]["mu"]))

with open(os.path.join(REPO, "results", "perpetual_faces", "n1_w268_results.json"), encoding="utf-8") as f:
    res = json.load(f)
print("RESULTS n1_w268: n_eff_held_equal=%s line_pre_w268=%r line_merged_587520=%r se_mu_at_k587520=%r" % (
    res["skill_line_v2_k_lift"]["n_eff_held_equal"],
    res["skill_line_v2_k_lift"].get("line_pre_w268"),
    res["skill_line_v2_k_lift"].get("line_merged_587520"),
    res["null_pool_cumulative"].get("se_mu_at_k587520")))
with open(os.path.join(REPO, "results", "perpetual_faces", "n1_w267_results.json"), encoding="utf-8") as f:
    res7 = json.load(f)
print("RESULTS n1_w267 chain verify: se_mu_at_k585320=%r" % res7["null_pool_cumulative"].get("se_mu_at_k585320"))

# --- 4. W269 seat probe receipt asserts (machine-read) ---
with open(os.path.join(REPO, "results", "_w269bmc_20261018_probe_receipt.json"), encoding="utf-8") as f:
    pr = json.load(f)
print("W269 PROBE: verdict=%s bands A=%s B=%s" % (pr["verdict"], pr["bands"]["A"], pr["bands"]["B"]))
print("  leg0: rows=%s owner=%s bmc=%s ordinal=%s" % (
    pr["legs"]["leg0"]["rows"], pr["legs"]["leg0"]["owner_rows"],
    pr["legs"]["leg0"]["bmc_rows"], pr["legs"]["leg0"]["ordinal"]))
print("  leg0 w268_finalize_anchors: %r" % pr["legs"]["leg0"]["w268_finalize_anchors"])
print("  leg1 hops A=%s B=%s | A_chain=%r | B_chain=%r" % (
    pr["legs"]["leg1"]["hops_A"], pr["legs"]["leg1"]["hops_B"],
    pr["legs"]["leg1"]["A_hop_chain"], pr["legs"]["leg1"]["B_hop_chain"]))
print("  leg2 conflicts=%s leg3 vacancy=%r" % (pr["legs"]["leg2"]["conflicts"], pr["legs"]["leg3"]["origin_vacancy"]))
print("  leg4: %r" % {k: pr["legs"]["leg4"][k] for k in
      ("W270p_A_naive", "W270p_B_naive", "hops_A", "hops_B", "W270p_B_lands_inside_W270p_A_naive")})

# --- 5. live faces ---
try:
    import psutil
    ram = psutil.virtual_memory().available / (1024 ** 3)
    print("LIVE RAM available: %.2f GB" % ram)
except Exception as e:
    print("LIVE RAM probe FAIL: %r" % e)
r = subprocess.run([sys.executable, os.path.join(REPO, "Tools", "saturation_engine.py"), "status"],
                   capture_output=True, text=True, encoding="utf-8", errors="replace", cwd=REPO)
try:
    eng = json.loads(r.stdout)
    print("ENGINE: machine=%s alive=%r burns=%r queue=%r" % (
        eng.get("machine_id"), eng.get("alive_flag"), eng.get("burns_active"), eng.get("queue_next")))
except Exception:
    print("ENGINE raw rc=%d: %s" % (r.returncode, r.stdout[:300]))

# --- 6. raw token counts on T0 (floors evidence) ---
toks = ["W269", "W268", "W267", "W266", "W265", "W264", "W263", "W262", "W261", "W260",
        "W259", "W258", "W257", "W256", "W255", "W254", "W251", "W244", "W270",
        "n1_w269", "n1_w268", "n1_w267", "n1_w266", "_w269bmc", "_w268bmc", "_w267bmc", "_w266bmc",
        "波号 268", "波号 269", "零 268 行", "零 269 行",
        "零 skip-ahead W269/W270 席位声明", "零 skip-ahead W270/W271 席位声明",
        "池第 266 枚", "池第 267 枚", "第 258 波", "第 259 波",
        "bm-c 第八十七枚自有波", "bm-c 第八十八枚自有波",
        "engine_owner==bm-c 86 行注册", "engine_owner==bm-c 87 行注册",
        "engine_owner 行 257 注册在册（表尾", "engine_owner 行 258 注册在册（表尾",
        "bmc_rows=86", "bmc_rows=87",
        "第十七次连续 A-hop", "第十八次连续 A-hop", "第十八次连续 above-own-A", "第十九次连续 above-own-A",
        "连续十七波", "连续十八波", "共二百六十六面", "共二百六十七面", "共二百六十五面",
        "MSG-20261018-1229-bmc-w268-seat", "MSG-20261018-1407-bmc-w269-seat",
        "b9ad2f1119", "d630d043b9", "f1ec8231c7", "8bc7ac759e", "8d0e7bdb1", "78af85566",
        "12:2x", "10:2x", "14:0x", "13:5x",
        "587,520", "1,013,935", "1,011,735", "585,320", "589,720",
        "604_901..606_900", "606_901..607_100", "607_101..609_100", "609_101..609_300",
        "606_901..608_900", "607_101..607_300", "606_701..608_700", "604_701..606_700",
        "604_901..605_100", "607_101..607_300",
        "−0.09273843", "0.24505587", "−0.09269745", "0.3058", "0.3120",
        "W269+ 投影", "W268+ 投影", "W270+ 投影",
        "hops=1", "hops=0",
        "A-ext seed=604_901..606_900", "B-ext exit seed=606_901..607_100",
        "entry rng=**604_901+j**", "exit rng=**606_901+j**",
        "n_eff_held_equal 996,335",
        "（W267 注册+烧录+finalize 全落地）", "（W268 注册+烧录+finalize 全落地）",
        "席位时即解锁", "（占位·finalize one-pass 后回填", "（占位·finalize 同窗回填",
        "W206/W211..W267 低 RAM 实烧先例",
        "本窗 free RAM ~0.1GB", "MV PACK-A i2v wave-1 在飞",
        "W269p_", "W268p_", "W270p_",
        "verify at W269 prereg", "verify at W270 prereg",
        "--wave 268/finalize --wave 268", "--wave 269/finalize --wave 269",
        "§5.5 W269+ 投影承接机证", "§5.5 W270+ 投影承接机证",
        "saturation_engine.py status live-read r1090", "saturation_engine.py status live-read r1092",
        "本机 bm-c 实例·heartbeat 新鲜实读 r1090 窗", "本机 bm-c 实例·heartbeat 新鲜实读 r1092 窗",
        "引擎实况注记（本机 bm-c 实例 heartbeat 新鲜 r1090 窗实读",
        "引擎实况注记（本机 bm-c 实例 heartbeat 新鲜 r1092 窗实读",
        "r1089 席位窗实跑", "r1091 席位窗实跑",
        "probe leg0 bmc_rows=86 attempt-continuity face", "probe leg0 bmc_rows=87 attempt-continuity face",
        "（**A 面=STAIRCASE-AFFECTS-A", "（见 §5 item5）。",
        "5. **W269+ 投影（probe 机证 leg4", "5. **W270+ 投影（probe 机证 leg4",
        "prev=**届时空窗活链头 derive 禁手抄**",
        "（机械算·投影面仅披露·finalize 运行时按 registry 键 derive 免疫）。",
        "本件=席位窗后首窗冻结件；五面冻结拼接脚本",
        "（gate0.5 绿·编辑器 loud abort 兜底）**。",
        "owner per chain-order law）**】】）",
        "entry rng seed=**602_701+j**", "entry rng seed=**604_901+j**",
        "exit rng=**604_701+j**", "exit rng=**606_901+j**",
        "probe W269+ 投影 A naive 606_901..608_900 CLEAN hops=0",
        "probe W270+ 投影 A naive 609_101..611_100 CLEAN hops=0",
        "席位公示=MSG-20261018-1229-bmc-w268-seat 已推 origin b9ad2f1119",
        "席位公示 MSG-20261018-1229-bmc-w268-seat 先推 origin b9ad2f1119",
        "W1..W267 已落账 585,320 实测", "W1..W268 已落账 587,520 实测",
        "键 W267 实测 K-lift", "键 W268 实测 K-lift",
        "→W264 **0.000322**→W265 **0.000321**→W266 **0.000321**→W267 **0.000320**→W268 投影 0.000320】",
        "·W244 冻结窗 41.9G bm-a 实锚·W263 冻结窗 26G bm-a 实锚·W264 冻结窗 7G bm-c 实锚·W265 冻结窗 3G bm-c 实锚·W266 冻结窗 ~5G bm-c 实锚·W267 冻结窗 ~0.1G bm-c 实锚）",
        "W268=bm-c own-wave window per chain-order law",
        "W269=bm-c own-wave window per chain-order law",
        "R269：W268 带", "R270：W269 带",
        "（W267 实测键 **−0.09273843**·K=585,320 合并池·W267-only 实测 **−0.09269745**）",
        "（W268 实测键 **−0.09273843**·K=585,320 合并池·W268-only 实测 **−0.09269745**）",
        "W267-only vs merged 实差 0.0000 在带内", "W268-only vs merged 实差 0.0000 在带内",
        "键 **0.24505587**=W267 合并池实测", "键 **0.24505587**=W268 合并池实测",
        "与 W267 A 档 p95（**0.3058** 实测锚）", "与 W268 A 档 p95（**0.3058** 实测锚）",
        "W2..W267 共二百六十六面实测 mu 稳定先例", "W2..W268 共二百六十六面实测 mu 稳定先例",
        "604_900+1", "606_900+1", "609_100+1",
        "seed_admit_gate rc0 双带 FREE",
        "A_staircase_hop_past_W267_B=true", "A_staircase_hop_past_W268_B=true",
        "B_lands_above_own_A=true",
        "waits-upstream ARMED", "GATED on", "finalize PENDING",
        "队列空转 idle",
        "df55e3fab9", "99166404f2", "eb5c74dbf7", "7b9e9377",
        "bm-c r1089 W267 §7 范式", "bm-c r1089 W267 §8 范式",
        "bm-c r1091 W268 §7 范式", "bm-c r1091 W268 §8 范式",
        "W268 冻结窗 ~0.1G bm-c 实锚", "W267 冻结窗 ~0.1G bm-c 实锚",
        ]
counts = {}
for t in toks:
    counts[t] = T0.count(t)
print("\n=== T0 RAW COUNTS ===")
for t in toks:
    print("%6d  %r" % (counts[t], t))
print("\nT0 lines: %d" % (T0.count("\n") + 1))
