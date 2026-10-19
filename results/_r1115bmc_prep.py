# -*- coding: utf-8 -*-
# r1115 bm-c: W278 prereg derive PREP (in-window fold of the r1103/r1107/r1110/r1113-prep precedent).
# Extracts the frozen W277 template face AT THE FREEZE COMMIT e0bc4a0ddd (PRE-backfill per
# r1052/r1049 law; python subprocess raw bytes per the r1012 PS-redirect law), byte-verifies
# size+sha256_16, then MEASURES every needle floor on T0 (r1077 measured-counts law) and dumps
# the builder facts receipt. Zero transcription of chain values into any product.
# EXTENDED FACTS BLOCK (r1103 facts-gather fold): W278 anchors machine-frozen HERE so the r1116
# builder window consumes them zero-transcription (commit ts / fivekeys / receipt bands / stamps).
import io, os, json, subprocess, hashlib

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GIT = "C:/Program Files/Git/cmd/git.exe"

def git_out(args):
    r = subprocess.run([GIT] + args, capture_output=True, cwd=REPO)
    if r.returncode != 0:
        raise SystemExit("git fail %r: %s" % (args, r.stderr.decode("utf-8", "replace")))
    return r.stdout.decode("utf-8", "replace").strip()

FREEZE = "e0bc4a0ddd"
PATH = "research/PERPETUAL_N1_W277_PREREG.md"
raw = subprocess.run([GIT, "show", FREEZE + ":" + PATH], capture_output=True, cwd=REPO).stdout
assert len(raw) == 23593, "frozen face size drift: %d" % len(raw)
assert hashlib.sha256(raw).hexdigest()[:16] == "45ee1de94c7d36fd", "frozen face sha256_16 mismatch: %s" % hashlib.sha256(raw).hexdigest()[:16]
t0 = raw.decode("utf-8")
out = os.path.join(REPO, "results", "_w278bmc_w277_frozen_face.txt")
io.open(out, "wb").write(raw)
blob_expect = git_out(["rev-parse", FREEZE + ":" + PATH])
head_twin = git_out(["rev-parse", "HEAD:" + PATH])
twin_size = git_out(["cat-file", "-s", "HEAD:" + PATH])
seat_files = git_out(["show", "--name-only", "--format=", "b187aa6214"])
fin_log = git_out(["log", "-1", "--format=%h", "--", "results/perpetual_faces/n1_w277_results.json"])
res4 = json.load(io.open(os.path.join(REPO, "results", "perpetual_faces", "n1_w277_results.json"), encoding="utf-8"))
res3 = json.load(io.open(os.path.join(REPO, "results", "perpetual_faces", "n1_w276_results.json"), encoding="utf-8"))
res4_keys = {
    "n_eff_held_equal": res4["skill_line_v2_k_lift"]["n_eff_held_equal"],
    "line_pre_w277": res4["skill_line_v2_k_lift"]["line_pre_w277"],
    "line_merged_607320": res4["skill_line_v2_k_lift"]["line_merged_607320"],
    "se_mu_at_k607320": res4["null_pool_cumulative"]["se_mu_at_k607320"],
}
res3_keys = {"se_mu_at_k605120": res3["null_pool_cumulative"]["se_mu_at_k605120"]}

KEYS = [
 # wave faces
 "W280", "W279", "W278", "W277", "W276", "W275", "W274", "W273", "W272", "W271", "W270", "W269", "W268",
 "W267", "W266", "W265", "W264", "W263", "W262", "W261",
 # lowercase chains
 "n1_w278", "n1_w277", "n1_w276", "n1_w275", "_w278bmc", "_w277bmc", "_w276bmc", "_w275bmc",
 # ordinals Chinese
 "第 97 枚", "第 96 枚", "第 95 枚", "第九十七枚", "第九十六枚", "第九十五枚",
 "池第 276 枚", "池第 275 枚", "池第 274 枚", "第 268 波", "第 267 波", "第 266 波",
 "波号 278", "波号 277", "波号 276", "零 278 行", "零 277 行", "零 276 行",
 "共二百七十六面", "共二百七十五面", "共二百七十四面",
 "连续二十七波", "连续二十六波", "连续二十五波",
 "第二十八次连续 A-hop", "第二十七次连续 A-hop", "第二十六次连续 A-hop",
 "第二十八次连续 above-own-A", "第二十七次连续 above-own-A", "第二十六次连续 above-own-A",
 "第二十五次连续 A-hop", "第二十五次连续 above-own-A",
 "〔第二十七次连续〕", "〔第二十八次连续〕", "〔第二十六次连续〕",
 # numbers / bands
 "1,033,735", "1,031,535", "1,029,335", "1033735", "1031535", "1029335",
 "609,320", "607,320", "605,120", "602,920", "609320", "607320", "605120", "602920",
 "626_901..628_900", "628_901..629_100", "626_701..626_900", "624_701..626_700",
 "626_901..627_100", "626_701..628_700", "624_501..624_700", "622_501..624_500",
 "624_501..626_500", "624_701..624_900", "622_301..622_500", "620_301..622_300",
 "622_301..624_300", "622_501..622_700", "620_101..620_300",
 "628_901..630_900", "629_101..629_300", "629_901..631_900",
 "626_900+1", "628_700+1", "624_700+1", "626_700+1", "622_500+1", "624_500+1", "622_300+1", "620_100+1", "620_300+1", "617_900+1", "615_900+1", "615_700+1",
 "615_901..617_900", "615_701..617_700", "613_501..615_500", "613_701..615_700", "613_501..613_700",
 "611_501..613_500", "611_301..613_300",
 # stamps
 "03:0x", "03:2x", "03:3x", "05:2x", "05:3x", "05:5x", "05:0x", "07:2x", "07:4x", "08:1x", "09:5x", "10:3x", "09:0x", "00:3x", "00:2x", "01:0x", "20:4x", "20:2x", "12:2x", "13:5x",
 "2026-10-19 07:28:56", "2026-10-19 07:47:43", "2026-10-19 08:13:22",
 "2026-10-19 09:57:42", "2026-10-19 10:35:34", "2026-10-19 09:02:01",
 # shas
 "770a47fa1f", "354a645155", "df7dedfd07", "627c4e10f2", "e781164e41", "c5f8b88f91",
 "e0bc4a0ddd", "9e53371814", "0df07c846b", "644b4f8459", "0502c722ac", "b187aa6214",
 "1fcc0bc30f", "018782314d", "5089f02250", "e639699d59", "fc01636095", "21b51a102",
 "bf4bbbde1e", "70b21a0264", "39e1bb32f1", "87d2697cdc", "f608ff1cee",
 # MSGs
 "MSG-20261019-102x", "MSG-20261019-080x", "MSG-20261019-055x", "MSG-20261019-034x",
 "bmc-w278-seat", "bmc-w277-seat", "bmc-w276-seat", "bmc-w275-seat",
 # measured values
 "−0.09278451", "0.24508562", "−0.08705886", "0.305",
 "−0.09277044", "0.24508694", "−0.08889850", "0.3095", "0.4459",
 "实差 0.0057 在带内", "实差 0.0039 在带内", "实差 0.0012 在带内",
 "line_pre_w276 1.1968", "line_pre_w277 1.197",
 "line_merged@K605,120", "line_merged@K607,320",
 "K=605,120", "K=607,320", "K=609,320",
 "0.000315", "0.000314",
 "n_eff_held_equal 1,029,335", "n_eff_held_equal 1,031,535", "n_eff_held_equal 1,033,735",
 "本窗 free RAM ~5.1GB", "本窗 free RAM ~3.8GB", "本窗 free RAM ~4.4GB", "本窗 free RAM ~4.0GB", "本窗 free RAM ~0.3GB", "本窗 free RAM ~1.4GB",
 "W276 冻结窗", "W277 冻结窗", "W275 冻结窗", "W277 冻结窗 ~5.1G bm-c 实锚", "W276 冻结窗 ~3.8G bm-c 实锚",
 "W206/W211..W276", "W206/W211..W277",
 # structural markers / floors
 "engine_owner 行 267 注册在册（表尾", "engine_owner 行 266 注册在册（表尾",
 "engine_owner==bm-c 96 行注册", "engine_owner==bm-c 95 行注册", "engine_owner==bm-c 94 行注册",
 "bmc_rows=96", "bmc_rows=95", "bmc_rows=94", "bmc rows 96+候选", "bmc rows 95+候选", "bmc rows 94+候选",
 "prev=**届时空窗活链头 derive 禁手抄**", "（**A 面=STAIRCASE-AFFECTS-A",
 "entry rng seed=**624_701+j**", "entry rng=**624_701+j**", "entry rng=**626_901+j**",
 "exit rng=**626_701+j**", "exit rng=**624_501+j**",
 "probe W278+ 投影 A naive 626_701..628_700 CLEAN hops=0",
 "probe W279+ 投影 A naive 628_901..630_900 CLEAN hops=0",
 "5. **W278+ 投影（probe 机证 leg4", "5. **W279+ 投影（probe 机证 leg4",
 "本件=席位窗后首窗冻结件；五面冻结拼接脚本",
 "（gate0.5 绿·编辑器 loud abort 兜底）**。",
 "owner per chain-order law）**】】）", "（见 §5 item5）。",
 "seed_admit_gate rc0 双带 FREE", "注册+烧录+finalize 全落地", "席位时即解锁",
 "（占位·finalize one-pass 后回填", "（占位·finalize 同窗回填",
 "W278p_", "W279p_", "W278+ 投影", "W279+ 投影",
 "hops=1", "hops=0", "verify at W278 prereg", "verify at W279 prereg",
 "waits-upstream ARMED", "GATED on", "finalize PENDING", "queue_depth",
 "bm-c r1111 W276 §7 范式", "bm-c r1114-continuation W277 §7 范式", "bm-c r1111 W276 §8 范式", "bm-c r1114-continuation W277 §8 范式",
 "r1112 席位窗实跑", "r1114-continuation 席位窗实跑", "r1115 席位窗实跑",
 "R278：W277 带", "R279：W278 带",
 "--wave 277/finalize --wave 277", "--wave 278/finalize --wave 278",
 "_w277bmc_freeze_edits.py", "_w276bmc_freeze_edits.py 模板派生",
 "n1_w277_results.json", "n1_w276_results.json", "n1_w278_results.json",
 "A_staircase_hop_past_W276_B=true", "A_staircase_hop_past_W277_B=true",
 "B_base_above_W277_tail", "B_lands_above_own_A=true", "（上游 W276 席位已闭链", "（上游 W277 席位已闭链",
 "（W276 注册+烧录+finalize 全落地）", "（W277 注册+烧录+finalize 全落地）",
 "A-ext seed=624_701..626_700", "A-ext seed=626_901..628_900",
 "B-ext exit seed=626_701..626_900", "B-ext exit seed=628_901..629_100",
 "entry rng=**624_701+j**（与 A[j] 同源配对语义逐字", "entry rng=**626_901+j**（与 A[j] 同源配对语义逐字",
 "W275_W276_W277_bands_respected", "W274_W275_W276_bands_respected",
 "624_701+j", "626_901+j", "626_701+j", "622_501+j", "MV PACK-A i2v wave-3 已收官 GPU idle 回释",
 "CEO 填载令", "chain-order law", "第二十六次连续 A-hop 3",
 "results/p2cal_ext/n1_w277/ 12/12", "results/p2cal_ext/n1_w276/ 12/12",
 "saturation_engine.py status live-read r1113", "saturation_engine.py status live-read r1115",
 "nvidia-smi 实读 4%·2.8G VRAM", "0.0039",
]
measured = {k: t0.count(k) for k in KEYS}

# --- EXTENDED FACTS BLOCK (r1103 facts-gather fold; r1116 builder consumes zero-transcription) ---
ci = lambda sha: git_out(["show", "-s", "--format=%ci", sha])
fk277 = json.load(io.open(os.path.join(REPO, "results", "_r1114bmc_w277_fivekeys.json"), encoding="utf-8"))
rcp278 = json.load(io.open(os.path.join(REPO, "results", "_w278bmc_20261019_probe_receipt.json"), encoding="utf-8"))
ram_live = round(float(subprocess.run(["python", "-c", "import psutil;print(psutil.virtual_memory().available/1024**3)"], capture_output=True).stdout.decode().strip()), 1)
facts = {
 "prep": "r1115 bm-c W278 prereg derive PREP (in-window fold of r1103/r1107/r1110/r1113-prep precedent + extended facts-gather)",
 "freeze_commit": FREEZE, "path": PATH,
 "frozen_size": len(raw), "frozen_sha256_16": hashlib.sha256(raw).hexdigest()[:16],
 "blob_expect": blob_expect, "head_twin": head_twin, "twin_size": int(twin_size),
 "seat_commit": "b187aa6214", "seat_msg_in_files": "MSG-20261019-102x-bmc-w278-seat.md" in seat_files,
 "w277_finalize_landed_by": fin_log,
 "res4_keys": res4_keys, "res3_keys": res3_keys,
 "t0_lines": t0.count("\n") + 1,
 "measured": measured,
 # --- W278 anchors (all machine-read this window; zero transcription into any product) ---
 "w278_anchor_facts": {
  "prereg_freeze": {"commit": "e0bc4a0ddd", "ts": ci("e0bc4a0ddd"), "blob_sha1": blob_expect,
                    "head_twin_sha1": head_twin, "head_twin_size": int(twin_size)},
  "splice": {"commit": "9e53371814", "ts": ci("9e53371814"), "splice_t": "09:5x"},
  "engine_batches": [{"commit": "0df07c846b", "ts": ci("0df07c846b")},
                     {"commit": "644b4f8459", "ts": ci("644b4f8459")}],
  "finalize_estate": {"commit": "0502c722ac", "ts": ci("0502c722ac")},
  "seat": {"commit": "b187aa6214", "ts": ci("b187aa6214"), "msg": "MSG-20261019-102x-bmc-w278-seat.md"},
  "fivekeys_w277": {
   "merged_k": fk277["merged"]["k"], "merged_mu": fk277["merged"]["mu"],
   "merged_sigma": fk277["merged"]["sigma"], "merged_mu_8dp": round(fk277["merged"]["mu"], 8),
   "sigma_8dp": round(fk277["merged"]["sigma"], 8),
   "se_mu_607320": fk277["merged"]["se_mu_k607320"],
   "w277_only_mu": fk277["w277_only"]["mu"], "w277_only_mu_8dp": round(fk277["w277_only"]["mu"], 8),
   "a_p95": fk277["a_band"]["full_sharpe_p95"], "a_p99": fk277["a_band"]["full_sharpe_p99"],
   "k_lift": fk277["skill_line"]["k_lift_delta"],
   "n_eff_held": fk277["skill_line"]["n_eff_held"],
   "line_pre_w277": fk277["skill_line"]["line_pre_w277"],
   "line_merged_607320": fk277["skill_line"]["line_merged_607320"],
   "ledger_total": fk277["ledger_identity"]["total"], "ledger_exact": fk277["ledger_identity"]["exact"],
   "merged_k_exact": fk277["merged_k_identity"]["merged_k"],
   "key1_name": "key1_w277_vs_merged_mu_gap",
   "key1_value": [c for c in fk277["checks"] if c["name"] == "key1_w277_vs_merged_mu_gap"][0]["value"],
   "key1_value_4dp": round([c for c in fk277["checks"] if c["name"] == "key1_w277_vs_merged_mu_gap"][0]["value"], 4),
   "all_pass": fk277["all_pass"],
  },
  "receipt_w278": {
   "verdict": rcp278["verdict"],
   "bands_A": rcp278["bands"]["A"], "bands_B": rcp278["bands"]["B"],
   "seed_admit": rcp278["legs"]["leg2"]["seed_admit_gate"],
   "leg0_rows": rcp278["legs"]["leg0"]["rows"], "leg0_owner_rows": rcp278["legs"]["leg0"]["owner_rows"],
   "leg0_bmc_rows": rcp278["legs"]["leg0"]["bmc_rows"], "leg0_ordinal": rcp278["legs"]["leg0"]["ordinal"],
   "A_hop_chain": rcp278["legs"]["leg1"]["A_hop_chain"], "B_hop_chain": rcp278["legs"]["leg1"]["B_hop_chain"],
   "B_naive": rcp278["legs"]["leg1"]["B_naive"], "B_naive_refused_at_start": rcp278["legs"]["leg1"]["B_naive_refused_at_start"],
   "relation_asserts": rcp278["legs"]["leg1"]["relation_asserts"],
   "leg2_conflicts": rcp278["legs"]["leg2"]["conflicts"], "leg3_origin_vacancy": rcp278["legs"]["leg3"]["origin_vacancy"],
   "W279p_A_naive": rcp278["legs"]["leg4"]["W279p_A_naive"], "W279p_B_naive": rcp278["legs"]["leg4"]["W279p_B_naive"],
   "W279p_B_lands_inside_W279p_A_naive": rcp278["legs"]["leg4"]["W279p_B_lands_inside_W279p_A_naive"],
  },
  "k_projection_w278": 607320 + 2200,
  "ledger_projection_w278": fk277["ledger_identity"]["total"] + 2200,
  "n_eff_held_projection_w278": fk277["ledger_identity"]["total"],
  "ram_live_gb": ram_live,
  "stamp_faces_t0": {"07:4x": t0.count("07:4x"), "07:2x": t0.count("07:2x"), "08:1x": t0.count("08:1x"),
                     "09:5x": t0.count("09:5x"), "10:3x": t0.count("10:3x")},
 },
}
io.open(os.path.join(REPO, "results", "_w278bmc_prep_facts.json"), "w", encoding="utf-8").write(
 json.dumps(facts, ensure_ascii=False, indent=1))
print("PREP OK: frozen face %d bytes sha256_16 %s -> %s" % (len(raw), facts["frozen_sha256_16"], out))
print("blob_expect=%s head_twin=%s twin_size=%s" % (blob_expect, head_twin, twin_size))
print("seat_msg_in_files=%s w277_finalize_landed_by=%s" % (facts["seat_msg_in_files"], fin_log))
print("res4_keys=%r" % (res4_keys,))
print("res3_keys=%r" % (res3_keys,))
print("t0 lines=%d" % facts["t0_lines"])
print("MEASURED nonzero:")
for k, v in sorted(measured.items()):
    if v:
        print("  %r = %d" % (k, v))
