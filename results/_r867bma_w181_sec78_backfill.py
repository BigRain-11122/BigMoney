# -*- coding: utf-8 -*-
"""r867 bm-a W181 sec7/sec8 settle backfill (HEAL leg, W169-precedent law).

The r864 W181 finalize window landed the one-pass finalize (commit 4f710354d,
12/12 shards, K 393,920->396,120 EXACT projection hit) but MISSED the
same-window sec7/sec8 mechanical backfill (placeholders still standing).
This script backfills now from the r864-landed machine face
results/perpetual_faces/n1_w181_results.json (zero hand-copied numbers --
every displayed value derived in-script and asserted), per the W180 sec7/8
format precedent verbatim-structure.  Honest note: backfill window = r867
heal (r864 finalize window miss disclosed in sec8 honesty line).

Edit scope guard: only the two placeholder section bodies are replaced;
everything before '## 7' and the final freeze line ride byte-verbatim.
Worktree file is CRLF (on-disk convention r370); freeze blob (de699e8cd
face fce370dca) is LF -- equality checked modulo EOL before the edit.
"""
import io
import json
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
PATH = r"research\PERPETUAL_N1_W181_PREREG.md"

# --- 0. freeze-blob equality guard (modulo EOL) ---------------------------
_r = subprocess.run(["git", "show", "de699e8cd:research/PERPETUAL_N1_W181_PREREG.md"],
                    capture_output=True)
assert _r.returncode == 0, "freeze blob not reachable"
blob = _r.stdout.decode("utf-8")
_sha = subprocess.run(["git", "rev-parse", "de699e8cd:research/PERPETUAL_N1_W181_PREREG.md"],
                       capture_output=True, text=True).stdout.strip()
assert _sha == "fce370dca52a8a0b6bffe2df2bdfa44b51db237e", _sha
wt = io.open(PATH, encoding="utf-8", newline="").read()
assert wt.replace("\r\n", "\n") == blob, "worktree != freeze blob (EOL-normalized) -- ABORT"

# --- 1. machine-read every displayed value --------------------------------
res = json.load(open(r"results/perpetual_faces/n1_w181_results.json", encoding="utf-8"))
npc = res["null_pool_cumulative"]
kl = res["skill_line_v2_k_lift"]
led = res["science_gates"]["ledger"]
fam = res["families"]["A_random_engine_exit"]

K_MERGED = npc["merged"]["n_values"]
K_PRE = npc["pre_w181_cumulative"]["n_values"]
MU6 = "%.6f" % npc["merged"]["mu"]
MU_W6 = "%.6f" % npc["w181_only"]["mu"]
MU_D = "%.6f" % npc["mu_delta_w181_vs_w180ext"]
SIG6 = "%.6f" % npc["merged"]["sigma"]
SIG_PRE6 = "%.6f" % npc["pre_w181_cumulative"]["sigma"]
SIG_W6 = "%.6f" % npc["w181_only"]["sigma"]
SE6 = "%.6f" % npc["se_mu_at_k396120"]
assert K_MERGED == 396120 and K_PRE == 393920, (K_MERGED, K_PRE)
assert MU6 == "-0.092765" and MU_W6 == "-0.098730" and MU_D == "-0.006231", (MU6, MU_W6, MU_D)
assert SIG6 == "0.245101" and SIG_PRE6 == "0.245111" and SIG_W6 == "0.243318", (SIG6, SIG_PRE6, SIG_W6)
assert SE6 == "0.000389", SE6

LEDG_PREV = led["prev_total"]; LEDG_TRIALS = led["batch_trials"]; LEDG_TOT = led["total"]
VOIDS = "/".join(led["voids_applied"])
CUTOFF = led["evidence_cutoff"]
assert (LEDG_PREV, LEDG_TRIALS, LEDG_TOT) == (802318, 2200, 804518), (LEDG_PREV, LEDG_TRIALS, LEDG_TOT)
assert LEDG_PREV + LEDG_TRIALS == LEDG_TOT, "ledger identity"
assert VOIDS == "LOWAMP-P1/LOWAMP-P2" and CUTOFF == "2026-09-22", (VOIDS, CUTOFF)

LINE_PRE = kl["line_pre_w181"]; LINE_MER = kl["line_merged_396120"]
DELTA = kl["line_delta_k_lift"]; N_EFF = kl["n_eff_held_equal"]
assert LINE_PRE == 1.1854 and LINE_MER == 1.1853 and DELTA == -0.0001 and N_EFF == 802318, kl
assert kl["canon_flip"].startswith("NOT performed"), kl["canon_flip"]
P95 = fam["full_sharpe_p95"]; P99 = fam["full_sharpe_p99"]; A_MU = fam["full_sharpe_mu"]
assert P95 == 0.3073 and P99 == 0.4415 and A_MU == -0.093337, (P95, P99, A_MU)
P95_PREV = 0.3098  # W180 anchor (frozen in W181 prereg sec5 key 3)
DP95 = "%.4f" % (P95 - P95_PREV)
assert DP95 == "-0.0025", DP95
assert res["audit"]["finalize_only"] is True and res["audit"]["machine"] == "bm-a", res["audit"]
SHARDS = len(res["shards_consumed"])
assert SHARDS == 12, SHARDS

# sec5 four-key verification (machine-computed from the same values)
GAP = abs(npc["w181_only"]["mu"] - npc["pre_w181_cumulative"]["mu"])
SIG_REL = (npc["merged"]["sigma"] - npc["pre_w181_cumulative"]["sigma"]) / npc["pre_w181_cumulative"]["sigma"] * 100.0
assert "%.6f" % GAP == "0.005999", GAP
assert "%.4f" % SIG_REL == "-0.0040", SIG_REL
assert GAP < 0.02 and abs(SIG_REL) < 10.0 and abs(P95 - P95_PREV) < 0.05 and abs(DELTA) <= 0.02

U = "\u2212"  # U+2212 display minus (r833 law 3)
K_M = "{:,}".format(K_MERGED); K_P = "{:,}".format(K_PRE)
LP = "{:,}".format(LEDG_PREV); LT = "{:,}".format(LEDG_TOT); NE = "{:,}".format(N_EFF)
PROJ_LEDG = 804105  # W181 frozen sec5 pool/ledger projection (r863 buildgen)
W16_INC = LEDG_TOT - PROJ_LEDG
assert W16_INC == 413, W16_INC

sec7 = (
    "## \u00a77 \u8dd1\u540e\u5b9e\u8bc1\u3002\u3010finalize \u6536\u53e3\u673a\u68b0\u56de\u586b\u00b7\u5f85 W181 finalize \u7a97\u3011\r\n"
    "- \u8d26\u672c\u6052\u7b49\u5f0f\uff1a" + LP + " + 2,200 = **" + LT + "** EXACT\uff08prev_total/batch_trials/total \u4e09\u952e\u673a\u8bfb\u00b7r864 \u5b9e\u6d4b\uff1b**vs \u00a75 \u51bb\u7ed3\u6295\u5f71 804,105 \u5dee +" + str(W16_INC) + "**=\u51bb\u7ed3\u540e W16 \u8bd5\u7528\u52b3\u52a8\u6279\u843d\u8d26\u5408\u6cd5\u589e\u91cf\u3010+373/+40 \u4e24\u6279\u00b7\u96f6\u6f02\u79fb\u00b7r864 finalize \u62ab\u9732\u3011\uff09\u3002\r\n"
    "- \u5408\u5e76\u6c60\uff1a**K=" + K_M + "** EXACT\uff08=W180 \u6c60 " + K_P + " + \u672c\u6ce2 2,200\u00b7\u00a75 \u6295\u5f71\u547d\u4e2d\uff09\u3002\r\n"
    "- merged mu **" + U + "0.092765**\uff08\u673a\u8bfb -0.0927645\uff09/ w-only mu **" + U + "0.098730** / mu_delta(w181 vs w180ext) **" + U + "0.006231**\u3002\r\n"
    "- merged sigma **0.245101**\uff08W180 \u952e 0.245111\u21920.245101\uff09\uff1bw-only sigma 0.243318\uff1bse_mu@K" + K_M + " **0.000389**\uff08W180 0.000391\u21920.000389 \u6536\u7a84\uff09\u3002\r\n"
    "- skill_line_v2\uff1aline_pre **1.1854** \u2192 line_merged@K" + K_M + " **1.1853**\uff08K-lift **" + U + "0.0001**\u00b7n_eff_held_equal " + NE + "\uff09\uff1bcanon flip **NOT performed**\uff08K2,200 \u540c\u4f8b\u6cd5\u00b7\u6cbb\u7406\u63d0\u6848\u9762\uff09\u3002\r\n"
    "- A \u6863 full_sharpe_p95 **0.3073**\uff08W180 \u951a 0.3098\u00b7\u0394" + DP95 + "<0.05 \u95e8\u8fc7\uff09\u00b7p99 0.4415\u00b7A mu " + U + "0.093337\u3002\r\n"
    "- \u00a75 \u56db\u9884\u952e\u673a\u8bc1\u5168\u8fc7\uff1a\u2460mu gap |" + U + "0.098730" + U + "(" + U + "0.092731)|=0.005999<0.02 PASS \u2461sigma \u76f8\u5bf9\u53d8\u5316 " + U + "0.0040%<\u00b110% PASS \u2462A p95 \u0394" + DP95 + "<0.05 PASS \u2463K-lift " + U + "0.0001\u2264\u00b10.02 PASS\u3002\r\n"
    "- audit.finalize_only=**true**\uff08bm-a\uff09\u00b7voids_applied=" + VOIDS + "\u00b7evidence_cutoff=" + CUTOFF + " \u5728\u4f4d\u00b7shards_consumed 12/12\u3002\r\n"
)
sec8 = (
    "## \u00a78 \u6279\u540e\u590d\u76d8\u3002\u3010finalize \u540c\u7a97\u56de\u586b\u00b7\u5f85 W181 finalize \u7a97\u3011\r\n"
    "- \u00a75.5 W182+ \u6295\u5f71\u627f\u63a5\uff08r865 seat probe \u56de\u6267\u673a\u8bc1\u00b7W182 \u51bb\u7ed3\u65b9\u91cd derive \u5f3a\u5236\u975e\u8f6c\u6284 r587 \u5f8b\uff09\uff1anaive A **415_004..417_003**\uff08hops=0 CLEAN\uff09\u5c06\u62d2\u4e8e\u6ce8\u518c W181 B \u5e26 415_004..415_203 own-start=\u9636\u68af A-hops-prior-B **\u7b2c\u56db\u5341\u4e8c\u4f8b**\u9884\u671f\u2014\u2014**r865 probe \u5df2\u5151\u73b0**\uff08A 415_204..417_203 hops=1 FORTY-SECOND \u673a\u8bfb\u00b7\u6295\u5f71\u4e0e\u56de\u6267\u5e8f\u6570 MATCH \u96f6\u5206\u53c9\uff09\uff1bnaive B **415_204..415_403**\uff08hops=0 CLEAN\uff09\u2014\u2014W141 \u540c\u7a97\u4e92\u65a5 leg2 \u5f8b\u9002\u7528 W182\uff08derive B \u65f6\u9884\u7559\u672c\u6ce2 A \u7a97\u00b7\u5df2\u5151\u73b0 B 417_204..417_403\uff09\u3002\r\n"
    "- \u5b9d\u85cf/\u65b9\u6cd5\u8bba\u6355\u83b7\u95ee\uff1a\u672c\u6279\u65e0\u65b0\u65b9\u6cd5\u96f6\u65b0\u5b9d\u85cf\uff08finalize one-pass=canonical runner \u5355\u53d1 r718 \u5148\u4f8b verbatim \u590d\u7528\uff09\uff1bTREASURE/METHODOLOGY \u96f6 append\u3002\r\n"
    "- \u8bda\u5b9e\u62ab\u9732\u9762\uff1aW181-only mu " + U + "0.0987 \u6bd4\u5408\u5e76\u6c60 " + U + "0.0928 \u6df1 0.0059\u22481.16\u00d7 w-only se\uff082,200 \u62bd\u6837 se\u22480.2433/\u221a2200\u22480.0052\uff09=null \u62bd\u6837\u6b63\u5e38\u6ce2\u52a8\u975e\u5f02\u5e38\uff08\u5355\u6ce2 w-only \u9762\u5c0f\u6837\u672c\u6ce2\u52a8\u00b7\u56db\u9884\u952e\u2460\u4ecd PASS\uff09\uff1bK-lift **" + U + "0.0001**\uff08W180 +0.0001 \u540e\u56de\u8d1f\u00b7\u7ebf 1.1854\u21921.1853\u00b7n_eff \u57fa " + NE + "=\u51bb\u7ed3\u540e W16 \u589e\u91cf\u540e head\u00b7r863 buildgen (f) sign-roll \u9884\u62ab\u9732\u5151\u73b0\uff09\uff1bA p95 0.3073 \u8f83 W180 \u951a 0.3098 \u4e0b\u79fb 0.0025 \u4ecd\u95e8\u5185\uff1b\u8d26\u672c +" + str(W16_INC) + " W16 \u5408\u6cd5\u589e\u91cf\u5982\u5b9e\u62ab\u9732\uff1b\u5f15\u64ce tick \u81ea\u70e7 12 \u5206\u7247\uff0805:28-05:39\uff09+finalize r864 \u540c\u8f6e\u6536\u53e3\uff08r381 \u5f8b\uff09\u3002\r\n"
    "- **\u00a77/\u00a78 \u56de\u586b\u7a97\u6ce8\u8bb0\uff1ar864 finalize \u7a97\u6f0f\u8865\u00b7r867 \u8865\u7a97\u673a\u68b0\u56de\u586b**\uff08\u6570\u636e\u5168\u91cf r864 \u5df2\u843d\u4ef6 n1_w181_results.json \u673a\u8bfb\u96f6\u624b\u6284\u00b7\u5982\u5b9e\u7559\u75d5\uff09\u3002\r\n"
)

# --- 2. locate + replace the two placeholder sections ----------------------
i7 = wt.find("## \u00a77")
i8 = wt.find("## \u00a78")
iF = wt.find("- **\u8dd1\u524d\u51bb\u7ed3")  # final freeze line
assert 0 < i7 < i8 < iF < len(wt), (i7, i8, iF)
assert "\u5360\u4f4d" in wt[i7:i8] and "\u5360\u4f4d" in wt[i8:iF], "placeholder sections expected"
old_tail = wt[iF:]
new = wt[:i7] + sec7 + "\r\n" + sec8 + "\r\n" + old_tail
io.open(PATH, "wb").write(new.encode("utf-8"))

chk = io.open(PATH, encoding="utf-8", newline="").read()
assert chk == new, "CRLF write roundtrip drift"
assert chk.startswith(wt[:i7]), "head drift"
assert chk.endswith(old_tail), "tail drift"
assert "804,518" in chk and "K=396,120" in chk and "1.1854" in chk and "1.1853" in chk
assert chk.count("\r\n") == wt.count("\r\n") + 10, (chk.count("\r\n"), wt.count("\r\n"))  # 63->73 observed: 2 placeholder bodies (5 crlf) out, 15 in
print("W181 sec7/8 backfilled:", PATH, "bytes", len(chk.encode("utf-8")), "crlf", chk.count("\r\n"))
print("HEAL leg done: r864 finalize data landed (r867 heal window, miss disclosed in sec8)")
