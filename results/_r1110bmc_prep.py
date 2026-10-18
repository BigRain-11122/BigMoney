# -*- coding: utf-8 -*-
# r1110 bm-c: W276 prereg derive PREP (in-window fold of the r1103/r1107-prep precedent).
# Extracts the frozen W275 template face AT THE FREEZE COMMIT 1fcc0bc30f (PRE-backfill per
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

FREEZE = "1fcc0bc30f"
PATH = "research/PERPETUAL_N1_W275_PREREG.md"
raw = subprocess.run([GIT, "show", FREEZE + ":" + PATH], capture_output=True, cwd=REPO).stdout
assert len(raw) == 23551, "frozen face size drift: %d" % len(raw)
assert hashlib.sha256(raw).hexdigest()[:16] == "e4e1ce44f5afd03b", "frozen face sha256_16 mismatch: %s" % hashlib.sha256(raw).hexdigest()[:16]
t0 = raw.decode("utf-8")
out = os.path.join(REPO, "results", "_w276bmc_w275_frozen_face.txt")
io.open(out, "wb").write(raw)
blob_expect = git_out(["rev-parse", FREEZE + ":" + PATH])
head_twin = git_out(["rev-parse", "HEAD:" + PATH])
twin_size = git_out(["cat-file", "-s", "HEAD:" + PATH])
seat_files = git_out(["show", "--name-only", "--format=", "21b51a102"])
fin_log = git_out(["log", "-1", "--format=%h", "--", "results/perpetual_faces/n1_w275_results.json"])
res4 = json.load(io.open(os.path.join(REPO, "results", "perpetual_faces", "n1_w275_results.json"), encoding="utf-8"))
res3 = json.load(io.open(os.path.join(REPO, "results", "perpetual_faces", "n1_w274_results.json"), encoding="utf-8"))
res4_keys = {
    "n_eff_held_equal": res4["skill_line_v2_k_lift"]["n_eff_held_equal"],
    "line_pre_w275": res4["skill_line_v2_k_lift"]["line_pre_w275"],
    "line_merged_602920": res4["skill_line_v2_k_lift"]["line_merged_602920"],
    "se_mu_at_k602920": res4["null_pool_cumulative"]["se_mu_at_k602920"],
}
res3_keys = {"se_mu_at_k600720": res3["null_pool_cumulative"]["se_mu_at_k600720"]}

KEYS = [
 # wave faces
 "W277", "W276", "W275", "W274", "W273", "W272", "W271", "W270", "W269", "W268", "W267", "W266",
 "W265", "W264", "W263", "W262", "W261", "W260",
 # lowercase chains
 "n1_w276", "n1_w275", "n1_w274", "n1_w273", "_w276bmc", "_w275bmc", "_w274bmc", "_w273bmc",
 # ordinals Chinese
 "第 95 枚", "第 94 枚", "第 93 枚", "第九十五枚", "第九十四枚", "第九十三枚",
 "池第 274 枚", "池第 273 枚", "池第 272 枚", "第 266 波", "第 265 波", "第 264 波",
 "波号 276", "波号 275", "波号 274", "零 276 行", "零 275 行", "零 274 行",
 "共二百七十四面", "共二百七十三面", "共二百七十二面",
 "连续二十五波", "连续二十四波", "连续二十三波",
 "第二十六次连续 A-hop", "第二十五次连续 A-hop", "第二十四次连续 A-hop",
 "第二十六次连续 above-own-A", "第二十五次连续 above-own-A", "第二十四次连续 above-own-A",
 "第二十三次连续 A-hop", "第二十三次连续 above-own-A",
 # numbers / bands
 "1,029,335", "1,027,135", "1,024,935", "1029335", "1027135", "1024935",
 "605,120", "602,920", "600,720", "598,520", "605120", "602920", "600720",
 "622_501..624_500", "624_501..624_700", "622_301..622_500", "620_301..622_300",
 "622_301..624_300", "622_501..622_700", "620_101..620_300", "618_101..620_100",
 "620_101..622_100", "620_301..620_500", "617_901..618_100", "617_901..619_900",
 "618_101..618_300", "624_501..626_500", "624_701..624_900",
 "622_500+1", "624_500+1", "620_100+1", "620_300+1", "622_300+1", "617_900+1", "615_900+1", "615_700+1",
 "615_901..617_900", "615_701..617_700", "613_501..615_500", "613_701..615_700", "613_501..613_700",
 "611_501..613_500", "611_301..613_300",
 # stamps
 "03:0x", "03:2x", "03:3x", "05:2x", "05:3x", "05:5x", "00:3x", "00:2x", "01:0x", "20:4x", "20:2x", "12:2x", "13:5x",
 "2026-10-19 00:20:20", "2026-10-19 00:39:01", "2026-10-19 01:03:27", "2026-10-19 03:06:44",
 "2026-10-19 05:22:20", "2026-10-19 05:31:54",
 # shas
 "6f31f6e073", "ec907d164", "b3c8a83c5c", "b4c0271044", "acf37937ec", "bf4bbbde1e",
 "70b21a0264", "839441a547", "04f2127db", "fbb4788c49", "acc7fd02c0", "6659a0e362",
 "1fcc0bc30f", "018782314d", "5089f02250", "e639699d59", "fc01636095", "21b51a102", "c77ee358f5",
 # MSGs
 "MSG-20261019-055x", "MSG-20261019-034x", "MSG-20261019-012x", "MSG-20261018-211x",
 "bmc-w276-seat", "bmc-w275-seat", "bmc-w274-seat", "bmc-w273-seat",
 # measured values
 "−0.09280110", "0.24508947", "−0.09630486", "0.3009", "0.3138", "0.3124",
 "−0.09280541", "0.24507989", "−0.09398255", "0.3088",
 "实差 0.0035 在带内", "实差 0.0012 在带内", "实差 0.0022 在带内",
 "line_pre_w274 1.1968", "line_pre_w275 1.1968",
 "line_merged@K600,720", "line_merged@K602,920",
 "K=600,720", "K=602,920", "K=605,120",
 "0.000316", "0.000317",
 "n_eff_held_equal 1,024,935", "n_eff_held_equal 1,027,135", "n_eff_held_equal 1,029,735",
 "本窗 free RAM ~4.0GB", "本窗 free RAM ~4.4GB", "本窗 free RAM ~0.3GB", "本窗 free RAM ~1.4GB", "本窗 free RAM ~3.3GB",
 "W274 冻结窗", "W273 冻结窗", "W272 冻结窗", "W274 冻结窗 ~4.0G bm-c 实锚", "W273 冻结窗 ~4.4G bm-c 实锚",
 "W206/W211..W274", "W206/W211..W275",
 # structural markers / floors
 "engine_owner 行 264 注册在册（表尾", "engine_owner 行 263 注册在册（表尾",
 "engine_owner==bm-c 93 行注册", "engine_owner==bm-c 94 行注册", "engine_owner==bm-c 92 行注册",
 "bmc_rows=93", "bmc_rows=94", "bmc rows 93+候选", "bmc rows 94+候选",
 "prev=**届时空窗活链头 derive 禁手抄**", "（**A 面=STAIRCASE-AFFECTS-A",
 "entry rng seed=**620_301+j**", "entry rng=**620_301+j**",
 "exit rng=**622_301+j**", "exit rng=**620_101+j**",
 "probe W276+ 投影 A naive 622_301..624_300 CLEAN hops=0",
 "probe W277+ 投影 A naive 624_501..626_500 CLEAN hops=0",
 "5. **W276+ 投影（probe 机证 leg4", "5. **W277+ 投影（probe 机证 leg4",
 "本件=席位窗后首窗冻结件；五面冻结拼接脚本",
 "（gate0.5 绿·编辑器 loud abort 兜底）**。",
 "owner per chain-order law）**】】）", "（见 §5 item5）。",
 "seed_admit_gate rc0 双带 FREE", "注册+烧录+finalize 全落地", "席位时即解锁",
 "（占位·finalize one-pass 后回填", "（占位·finalize 同窗回填",
 "W276p_", "W277p_", "W276+ 投影", "W277+ 投影",
 "hops=1", "hops=0", "verify at W276 prereg", "verify at W277 prereg",
 "waits-upstream ARMED", "GATED on", "finalize PENDING", "queue_depth",
 "bm-c r1105 W274 §7 范式", "bm-c r1108 W275 §7 范式", "bm-c r1105 W274 §8 范式",
 "r1106 席位窗实跑", "r1109 席位窗实跑",
 "R276：W275 带", "R277：W276 带",
 "--wave 275/finalize --wave 275", "--wave 276/finalize --wave 276",
 "_w275bmc_freeze_edits.py", "_w274bmc_freeze_edits.py 模板派生",
 "n1_w275_results.json", "n1_w274_results.json", "n1_w276_results.json",
 "A_staircase_hop_past_W274_B=true", "A_staircase_hop_past_W275_B=true",
 "B_lands_above_own_A=true", "（上游 W274 席位已闭链", "（上游 W275 席位已闭链",
 "（W274 注册+烧录+finalize 全落地）", "（W275 注册+烧录+finalize 全落地）",
 "A-ext seed=620_301..622_300", "A-ext seed=622_501..624_500",
 "B-ext exit seed=622_301..622_500", "B-ext exit seed=624_501..624_700",
 "entry rng=**620_301+j**（与 A[j] 同源配对语义逐字", "entry rng=**622_501+j**（与 A[j] 同源配对语义逐字",
 "W272_W273_W274_bands_respected", "W273_W274_W275_bands_respected",
 "622_301+j", "624_501+j", "620_301+j", "MV PACK-A i2v wave-3 已收官 GPU idle 回释",
 "CEO 填载令", "chain-order law", "第二十四次连续 A-hop 3",
]
measured = {k: t0.count(k) for k in KEYS}

facts = {
 "prep": "r1110 bm-c W276 prereg derive PREP (in-window fold of r1103/r1107-prep precedent)",
 "freeze_commit": FREEZE, "path": PATH,
 "frozen_size": len(raw), "frozen_sha256_16": hashlib.sha256(raw).hexdigest()[:16],
 "blob_expect": blob_expect, "head_twin": head_twin, "twin_size": int(twin_size),
 "seat_commit": "21b51a102", "seat_msg_in_files": "MSG-20261019-055x-bmc-w276-seat.md" in seat_files,
 "w275_finalize_landed_by": fin_log,
 "res4_keys": res4_keys, "res3_keys": res3_keys,
 "t0_lines": t0.count("\n") + 1,
 "measured": measured,
}
io.open(os.path.join(REPO, "results", "_w276bmc_prep_facts.json"), "w", encoding="utf-8").write(
 json.dumps(facts, ensure_ascii=False, indent=1))
print("PREP OK: frozen face %d bytes sha256_16 %s -> %s" % (len(raw), facts["frozen_sha256_16"], out))
print("blob_expect=%s head_twin=%s twin_size=%s" % (blob_expect, head_twin, twin_size))
print("seat_msg_in_files=%s w275_finalize_landed_by=%s" % (facts["seat_msg_in_files"], fin_log))
print("res4_keys=%r" % (res4_keys,))
print("res3_keys=%r" % (res3_keys,))
print("t0 lines=%d" % facts["t0_lines"])
print("MEASURED nonzero:")
for k, v in sorted(measured.items()):
    if v:
        print("  %r = %d" % (k, v))
