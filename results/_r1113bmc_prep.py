# -*- coding: utf-8 -*-
# r1113 bm-c: W277 prereg derive PREP (in-window fold of the r1103/r1107/r1110-prep precedent).
# Extracts the frozen W276 template face AT THE FREEZE COMMIT 770a47fa1f (PRE-backfill per
# r1052/r1049 law; python subprocess raw bytes per the r1012 PS-redirect law), byte-verifies
# size+sha256_16, then MEASURES every needle floor on T0 (r1077 measured-counts law) and dumps
# the builder facts receipt. Zero transcription of chain values into any product.
import io, os, json, subprocess, hashlib

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GIT = "C:/Program Files/Git/cmd/git.exe"

def git_out(args):
    r = subprocess.run([GIT] + args, capture_output=True, cwd=REPO)
    if r.returncode != 0:
        raise SystemExit("git fail %r: %s" % (args, r.stderr.decode("utf-8", "replace")))
    return r.stdout.decode("utf-8", "replace").strip()

FREEZE = "770a47fa1f"
PATH = "research/PERPETUAL_N1_W276_PREREG.md"
raw = subprocess.run([GIT, "show", FREEZE + ":" + PATH], capture_output=True, cwd=REPO).stdout
assert len(raw) == 23554, "frozen face size drift: %d" % len(raw)
assert hashlib.sha256(raw).hexdigest()[:16] == "5352c7cf343fc5e5", "frozen face sha256_16 mismatch: %s" % hashlib.sha256(raw).hexdigest()[:16]
t0 = raw.decode("utf-8")
out = os.path.join(REPO, "results", "_w277bmc_w276_frozen_face.txt")
io.open(out, "wb").write(raw)
blob_expect = git_out(["rev-parse", FREEZE + ":" + PATH])
head_twin = git_out(["rev-parse", "HEAD:" + PATH])
twin_size = git_out(["cat-file", "-s", "HEAD:" + PATH])
seat_files = git_out(["show", "--name-only", "--format=", "c5f8b88f91"])
fin_log = git_out(["log", "-1", "--format=%h", "--", "results/perpetual_faces/n1_w276_results.json"])
res4 = json.load(io.open(os.path.join(REPO, "results", "perpetual_faces", "n1_w276_results.json"), encoding="utf-8"))
res3 = json.load(io.open(os.path.join(REPO, "results", "perpetual_faces", "n1_w275_results.json"), encoding="utf-8"))
res4_keys = {
    "n_eff_held_equal": res4["skill_line_v2_k_lift"]["n_eff_held_equal"],
    "line_pre_w276": res4["skill_line_v2_k_lift"]["line_pre_w276"],
    "line_merged_605120": res4["skill_line_v2_k_lift"]["line_merged_605120"],
    "se_mu_at_k605120": res4["null_pool_cumulative"]["se_mu_at_k605120"],
}
res3_keys = {"se_mu_at_k602920": res3["null_pool_cumulative"]["se_mu_at_k602920"]}

KEYS = [
 # wave faces
 "W278", "W277", "W276", "W275", "W274", "W273", "W272", "W271", "W270", "W269", "W268", "W267", "W266",
 "W265", "W264", "W263", "W262", "W261", "W260",
 # lowercase chains
 "n1_w277", "n1_w276", "n1_w275", "n1_w274", "_w277bmc", "_w276bmc", "_w275bmc", "_w274bmc",
 # ordinals Chinese
 "第 96 枚", "第 95 枚", "第 94 枚", "第九十六枚", "第九十五枚", "第九十四枚",
 "池第 275 枚", "池第 274 枚", "池第 273 枚", "第 267 波", "第 266 波", "第 265 波",
 "波号 277", "波号 276", "波号 275", "零 277 行", "零 276 行", "零 275 行",
 "共二百七十五面", "共二百七十四面", "共二百七十三面",
 "连续二十六波", "连续二十五波", "连续二十四波",
 "第二十七次连续 A-hop", "第二十六次连续 A-hop", "第二十五次连续 A-hop",
 "第二十七次连续 above-own-A", "第二十六次连续 above-own-A", "第二十五次连续 above-own-A",
 "第二十四次连续 A-hop", "第二十四次连续 above-own-A",
 "〔第二十六次连续〕", "〔第二十七次连续〕", "〔第二十五次连续〕",
 # numbers / bands
 "1,031,535", "1,029,335", "1,027,135", "1031535", "1029335", "1027135",
 "607,320", "605,120", "602,920", "600,720", "607320", "605120", "602920", "600720",
 "624_701..626_700", "626_701..626_900", "624_501..624_700", "622_501..624_500",
 "624_501..626_500", "624_701..624_900", "622_301..622_500", "620_301..622_300",
 "622_301..624_300", "622_501..622_700", "620_101..620_300", "618_101..620_100",
 "620_101..622_100", "620_301..620_500", "617_901..618_100", "617_901..619_900",
 "618_101..618_300", "626_701..628_700", "626_901..627_100",
 "624_700+1", "626_700+1", "622_500+1", "624_500+1", "622_300+1", "620_100+1", "620_300+1", "617_900+1", "615_900+1", "615_700+1",
 "615_901..617_900", "615_701..617_700", "613_501..615_500", "613_701..615_700", "613_501..613_700",
 "611_501..613_500", "611_301..613_300",
 # stamps
 "03:0x", "03:2x", "03:3x", "05:2x", "05:3x", "05:5x", "05:0x", "07:2x", "07:4x", "08:1x", "00:3x", "00:2x", "01:0x", "20:4x", "20:2x", "12:2x", "13:5x",
 "2026-10-19 05:22:20", "2026-10-19 05:31:54", "2026-10-19 05:55:17",
 "2026-10-19 07:28:56", "2026-10-19 07:47:43", "2026-10-19 08:13:22",
 # shas
 "1fcc0bc30f", "018782314d", "5089f02250", "e639699d59", "fc01636095", "21b51a102",
 "770a47fa1f", "354a645155", "df7dedfd07", "627c4e10f2", "e781164e41", "c5f8b88f91",
 "6f31f6e073", "ec907d164", "b3c8a83c5c", "b4c0271044", "acf37937ec", "6659a0e362",
 "bf4bbbde1e", "70b21a0264", "39e1bb32f1", "87d2697cdc", "f608ff1cee",
 # MSGs
 "MSG-20261019-080x", "MSG-20261019-055x", "MSG-20261019-034x", "MSG-20261019-012x",
 "bmc-w277-seat", "bmc-w276-seat", "bmc-w275-seat", "bmc-w274-seat",
 # measured values
 "−0.09280541", "0.24507989", "−0.09398255", "0.3088",
 "−0.09278451", "0.24508562", "−0.08705886", "0.305", "0.4459",
 "实差 0.0012 在带内", "实差 0.0057 在带内", "实差 0.0035 在带内",
 "line_pre_w275 1.1968", "line_pre_w276 1.1968",
 "line_merged@K602,920", "line_merged@K605,120",
 "K=602,920", "K=605,120", "K=607,320",
 "0.000316", "0.000315",
 "n_eff_held_equal 1,027,135", "n_eff_held_equal 1,029,335", "n_eff_held_equal 1,031,535",
 "本窗 free RAM ~3.8GB", "本窗 free RAM ~4.4GB", "本窗 free RAM ~4.0GB", "本窗 free RAM ~0.3GB", "本窗 free RAM ~1.4GB", "本窗 free RAM ~3.3GB", "本窗 free RAM ~5.9GB",
 "W275 冻结窗", "W274 冻结窗", "W273 冻结窗", "W275 冻结窗 ~3.8G bm-c 实锚", "W274 冻结窗 ~4.0G bm-c 实锚",
 "W206/W211..W275", "W206/W211..W276",
 # structural markers / floors
 "engine_owner 行 265 注册在册（表尾", "engine_owner 行 264 注册在册（表尾",
 "engine_owner==bm-c 94 行注册", "engine_owner==bm-c 95 行注册", "engine_owner==bm-c 93 行注册",
 "bmc_rows=94", "bmc_rows=95", "bmc_rows=93", "bmc rows 94+候选", "bmc rows 95+候选", "bmc rows 93+候选",
 "prev=**届时空窗活链头 derive 禁手抄**", "（**A 面=STAIRCASE-AFFECTS-A",
 "entry rng seed=**622_501+j**", "entry rng=**622_501+j**",
 "exit rng=**624_501+j**", "exit rng=**622_301+j**",
 "probe W277+ 投影 A naive 624_501..626_500 CLEAN hops=0",
 "probe W278+ 投影 A naive 626_701..628_700 CLEAN hops=0",
 "5. **W277+ 投影（probe 机证 leg4", "5. **W278+ 投影（probe 机证 leg4",
 "本件=席位窗后首窗冻结件；五面冻结拼接脚本",
 "（gate0.5 绿·编辑器 loud abort 兜底）**。",
 "owner per chain-order law）**】】）", "（见 §5 item5）。",
 "seed_admit_gate rc0 双带 FREE", "注册+烧录+finalize 全落地", "席位时即解锁",
 "（占位·finalize one-pass 后回填", "（占位·finalize 同窗回填",
 "W277p_", "W278p_", "W277+ 投影", "W278+ 投影",
 "hops=1", "hops=0", "verify at W277 prereg", "verify at W278 prereg",
 "waits-upstream ARMED", "GATED on", "finalize PENDING", "queue_depth",
 "bm-c r1108 W275 §7 范式", "bm-c r1111 W276 §7 范式", "bm-c r1108 W275 §8 范式", "bm-c r1111 W276 §8 范式",
 "r1109 席位窗实跑", "r1112 席位窗实跑",
 "R277：W276 带", "R278：W277 带",
 "--wave 276/finalize --wave 276", "--wave 277/finalize --wave 277",
 "_w276bmc_freeze_edits.py", "_w275bmc_freeze_edits.py 模板派生",
 "n1_w276_results.json", "n1_w275_results.json", "n1_w277_results.json",
 "A_staircase_hop_past_W275_B=true", "A_staircase_hop_past_W276_B=true",
 "B_lands_above_own_A=true", "（上游 W275 席位已闭链", "（上游 W276 席位已闭链",
 "（W275 注册+烧录+finalize 全落地）", "（W276 注册+烧录+finalize 全落地）",
 "A-ext seed=622_501..624_500", "A-ext seed=624_701..626_700",
 "B-ext exit seed=624_501..624_700", "B-ext exit seed=626_701..626_900",
 "entry rng=**622_501+j**（与 A[j] 同源配对语义逐字", "entry rng=**624_701+j**（与 A[j] 同源配对语义逐字",
 "W274_W275_W276_bands_respected", "W273_W274_W275_bands_respected",
 "624_501+j", "626_701+j", "622_501+j", "MV PACK-A i2v wave-3 已收官 GPU idle 回释",
 "CEO 填载令", "chain-order law", "第二十五次连续 A-hop 3",
 "results/p2cal_ext/n1_w276/ 12/12", "results/p2cal_ext/n1_w275/ 12/12",
 "saturation_engine.py status live-read r1110", "saturation_engine.py status live-read r1113",
 "nvidia-smi 实读 4%·2.8G VRAM", "W276 冻结窗", "0.0057",
]
measured = {k: t0.count(k) for k in KEYS}

facts = {
 "prep": "r1113 bm-c W277 prereg derive PREP (in-window fold of r1103/r1107/r1110-prep precedent)",
 "freeze_commit": FREEZE, "path": PATH,
 "frozen_size": len(raw), "frozen_sha256_16": hashlib.sha256(raw).hexdigest()[:16],
 "blob_expect": blob_expect, "head_twin": head_twin, "twin_size": int(twin_size),
 "seat_commit": "c5f8b88f91", "seat_msg_in_files": "MSG-20261019-080x-bmc-w277-seat.md" in seat_files,
 "w276_finalize_landed_by": fin_log,
 "res4_keys": res4_keys, "res3_keys": res3_keys,
 "t0_lines": t0.count("\n") + 1,
 "measured": measured,
}
io.open(os.path.join(REPO, "results", "_w277bmc_prep_facts.json"), "w", encoding="utf-8").write(
 json.dumps(facts, ensure_ascii=False, indent=1))
print("PREP OK: frozen face %d bytes sha256_16 %s -> %s" % (len(raw), facts["frozen_sha256_16"], out))
print("blob_expect=%s head_twin=%s twin_size=%s" % (blob_expect, head_twin, twin_size))
print("seat_msg_in_files=%s w276_finalize_landed_by=%s" % (facts["seat_msg_in_files"], fin_log))
print("res4_keys=%r" % (res4_keys,))
print("res3_keys=%r" % (res3_keys,))
print("t0 lines=%d" % facts["t0_lines"])
print("MEASURED nonzero:")
for k, v in sorted(measured.items()):
    if v:
        print("  %r = %d" % (k, v))
