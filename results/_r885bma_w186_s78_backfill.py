# -*- coding: utf-8 -*-
"""r885 bm-a W186 prereg sec7/sec8 mechanical backfill (finalize landed r884
composite closeout window 16:08; backfill legs this r885 window as the
open-window first leg -- honest next-window note vs the W185 same-window
r879 precedent, r864 procrastination-lesson disclosed). All values
machine-read from results/perpetual_faces/n1_w186_results.json (r587
never-transcribe law). Output CRLF (r370 law)."""
import io
import json
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
PF = "research/PERPETUAL_N1_W186_PREREG.md"

res = json.load(open("results/perpetual_faces/n1_w186_results.json",
                     encoding="utf-8"))
sg = res["science_gates"]
led = sg["ledger"]
npc = res["null_pool_cumulative"]
kl = res["skill_line_v2_k_lift"]
fA = res["families"]["A_random_engine_exit"]
assert led["prev_total"] == 814328 and led["batch_trials"] == 2200 \
    and led["total"] == 816528, led
assert led["voids_applied"] == ["LOWAMP-P1", "LOWAMP-P2"], led
assert led["evidence_cutoff"] == "2026-09-22", led
assert res["evidence_cutoff"] == "2026-09-22", "top cutoff drift"
assert npc["merged"]["n_values"] == 407120 and \
    npc["pre_w186_cumulative"]["n_values"] == 404920, npc
assert npc["w186_only"]["n_values"] == 2200, npc
assert kl["line_pre_w186"] == 1.1859 and \
    kl["line_merged_407120"] == 1.1858 and \
    kl["line_delta_k_lift"] == -0.0001 and \
    kl["n_eff_held_equal"] == 814328, kl
assert kl["canon_flip"].startswith("NOT performed"), kl
assert npc["se_mu_at_k407120"] == 0.000384, npc
assert abs(npc["mu_delta_w186_vs_w185ext"] - (-0.003301)) < 1e-9, npc
assert fA["full_sharpe_p95"] == 0.3004 and fA["full_sharpe_p99"] == 0.4316 \
    and abs(fA["full_sharpe_mu"] - (-0.097146)) < 1e-9, fA
assert res["audit"] == {"machine": "bm-a", "finalize_only": True}, res["audit"]
assert len(res["shards_consumed"]) == 12, "shards 12/12 drift"
MU6 = "%.6f" % npc["merged"]["mu"]
WONLY6 = "%.6f" % npc["w186_only"]["mu"]
SIG6 = "%.6f" % npc["merged"]["sigma"]
WSIG6 = "%.6f" % npc["w186_only"]["sigma"]
MU_R = "%.8f" % npc["merged"]["mu"]
WONLY_R = "%.8f" % npc["w186_only"]["mu"]
assert MU6 == "-0.092905" and WONLY6 == "-0.102515" and SIG6 == "0.245086" \
    and WSIG6 == "0.244154", (MU6, WONLY6, SIG6, WSIG6)
assert MU_R == "-0.09290459" and WONLY_R == "-0.10251500", (MU_R, WONLY_R)
GAP = abs(npc["w186_only"]["mu"] - npc["merged"]["mu"])
assert "%.6f" % GAP == "0.009610", GAP
SIGREL = (npc["merged"]["sigma"] - 0.245090) / 0.245090 * 100.0
assert SIGREL < 0 and SIGREL > -0.01, SIGREL
M = "\u2212"  # U+2212 display minus (r833 law 3)

S7_OLD = ("## \u00a77 \u8dd1\u540e\u5b9e\u8bc1\u3002\u3010finalize \u6536\u53e3\u673a\u68b0\u56de\u586b"
          "\u00b7\u5f85 W186 finalize \u7a97\u3011\r\n"
          "- \uff08\u5360\u4f4d\u00b7finalize one-pass \u540e\u673a\u68b0\u56de\u586b\uff1a\u8d26\u672c\u6052\u7b49\u5f0f"
          "+\u5408\u5e76\u6c60 K+merged mu/w-only mu/mu_delta+sigma+se_mu+skill_line_v2 "
          "K-lift+A \u6863 p95+\u00a75 \u56db\u9884\u952e\u673a\u8bc1+canon flip \u6001"
          "+audit.finalize_only+voids_applied\u3002\uff09")
S8_OLD = ("## \u00a78 \u6279\u540e\u590d\u76d8\u3002\u3010finalize \u540c\u7a97\u56de\u586b"
          "\u00b7\u5f85 W186 finalize \u7a97\u3011\r\n"
          "- \uff08\u5360\u4f4d\u00b7\u00a75.5 W187+ \u6295\u5f71\u627f\u63a5+\u5b9d\u85cf/\u65b9\u6cd5\u8bba"
          "\u6355\u83b7\u95ee+\u8bda\u5b9e\u62ab\u9732\u9762\u00b7finalize \u6536\u53e3\u7a97\u673a\u68b0\u56de\u586b\u3002\uff09")

S7_NEW = (
    "## \u00a77 \u8dd1\u540e\u5b9e\u8bc1\u3002\u3010finalize \u6536\u53e3\u673a\u68b0\u56de\u586b"
    "\u00b7r885 \u56de\u586b\u7a97\uff08finalize 16:08 r884 \u4e09\u6b7b\u5c3e\u590d\u5408\u6536\u53e3\u7a97\u843d\u4ef6"
    "\u00b7\u00a77/\u00a78 \u56de\u586b\u987a\u5ef6\u81f3 r885 \u5f00\u7a97\u9996\u817f\u5373\u523b\u8865"
    "\u00b7\u975e\u62d6\u5ef6\u7a97\u5bf9\u7167 W159/W168/W169/W180\u00b7\u5982\u5b9e\u6ce8\u8bb0\uff09\u3011\r\n"
    "- \u8d26\u672c\u6052\u7b49\u5f0f\uff1a814,328 + 2,200 = **816,528** EXACT"
    "\uff08prev_total/batch_trials/total \u4e09\u952e\u673a\u8bfb\u00b7r884 finalize one-pass \u5b9e\u6d4b"
    "\uff1b**vs \u00a75 \u51bb\u7ed3\u6295\u5f71\uff08814,328+2,200=816,528 \u673a\u68b0\u7b97\uff09\u96f6\u5dee**"
    "\u2014\u2014\u672c\u7a97\u96f6\u5728\u98de\u4e0a\u6e38\u6279\u51bb\u7ed3\u540e\u5165\u94fe\u00b7\u5e72\u51c0\u5165\u94fe\uff09\u3002\r\n"
    "- \u5408\u5e76\u6c60\uff1a**K=407,120** EXACT\uff08=W185 \u6c60 404,920 + \u672c\u6ce2 2,200"
    "\u00b7\u00a75 \u6295\u5f71 407,120 \u547d\u4e2d\uff09\u3002\r\n"
    "- merged mu **{mu6}\uff08\u673a\u8bfb {mur}\uff09/ w-only mu **{wonly6}"
    "\uff08\u673a\u8bfb {wonlyr}\uff09/ mu_delta(w186 vs w185ext) **{md}\u3002\r\n"
    "- merged sigma **{sig6}\uff08W185 \u952e 0.245090\u2192{sig6}\uff09\uff1bw-only sigma {wsig6}"
    "\uff1bse_mu@K407,120 **0.000384**\uff08W185 0.000385\u2192W186 0.000384 \u6536\u7a84"
    "\u00b7\u94fe\u9762 \u2026W183 0.000387\u2192W184 0.000386\u2192W185 0.000385\u2192W186 0.000384\uff09\u3002\r\n"
    "- skill_line_v2\uff1aline_pre **1.1859** \u2192 line_merged@K407,120 **1.1858**"
    "\uff08K-lift **{m}0.0001**\u00b7n_eff_held_equal 814,328\uff09\uff1bcanon flip **NOT performed**"
    "\uff08K2,200 \u540c\u4f8b\u6cd5\u00b7\u6cbb\u7406\u63d0\u6848\u9762\uff09\u3002\r\n"
    "- A \u6863 full_sharpe_p95 **0.3004**\uff08W185 \u952a 0.3066\u00b7\u0394{m}0.0062 \u95e8\u8fc7\uff09"
    "\u00b7p99 0.4316\u00b7A mu {m}0.097146\u3002\r\n"
    "- \u00a75 \u56db\u9884\u952e\u673a\u8bc1\u5168\u8fc7\uff1a\u2460mu gap 0.009610<0.02 PASS "
    "\u2461sigma \u76f8\u5bf9\u53d8\u5316 {m}0.0016%<\u00b110% PASS \u2462A p95 \u0394{m}0.0062<0.05 PASS "
    "\u2463K-lift {m}0.0001\u2264\u00b10.02 PASS\u3002\r\n"
    "- audit.finalize_only=**true**\uff08bm-a\uff09\u00b7voids_applied=LOWAMP-P1,LOWAMP-P2"
    "\u00b7evidence_cutoff=2026-09-22 \u5728\u4f4d\u00b7shards_consumed 12/12"
    "\uff08\u5f15\u64ce tick \u81ea\u70e7 15:4x\u201316:0x\u00b7r882 \u51bb\u7ed3\u7a97\u81ea\u71c3 r325 \u5b9e\u8bc1"
    "\u00b7finalize 16:08 r884 \u4e09\u6b7b\u5c3e\u590d\u5408\u6536\u53e3\u7a97\u843d\u4ef6\uff09\u3002"
).format(mu6=MU6, mur=MU_R, wonly6=WONLY6, wonlyr=WONLY_R,
         md=M + "0.003301", sig6=SIG6, wsig6=WSIG6, m=M)

S8_NEW = (
    "## \u00a78 \u6279\u540e\u590d\u76d8\u3002\u3010finalize \u540c\u7a97\u56de\u586b"
    "\u00b7r885 \u56de\u586b\u7a97\u3011\r\n"
    "- \u00a75.5 W187+ \u6295\u5f71\u627f\u63a5\uff08r880 probe \u673a\u8bc1\u00b7W187 \u51bb\u7ed3\u65b9\u91cd derive "
    "\u5f3a\u5236\u975e\u8f6c\u6284 r587 \u5f8b\uff09\uff1anaive A **426_004..428_003**\uff08hops=0 CLEAN\uff09"
    "\u2014\u2014\u88ab\u6ce8\u518c W186 B \u5e26 426_004..426_203 own-start \u62d2=\u9636\u68af "
    "A-hops-prior-B \u7ee7\u627f**\u7b2c\u56db\u5341\u4e03\u4f8b**\u2014\u2014**r885 probe \u5b9e\u8bc1\u590d\u6838"
    "\u786e\u8ba4**\uff08A 426_204..428_203 hops=1 \u00b7\u672c\u7a97 W187 \u94fe\u5f00\u7a97\u5151\u73b0\uff09"
    "\uff1bnaive B **426_204..426_403**\uff08hops=0 CLEAN\uff09\u843d naive A \u7a97\u5185"
    "\u2014\u2014W141 \u540c\u7a97\u4e92\u65a7 leg2 \u5f8b\u9002\u7528 W187\uff08derive B \u65f6\u9884\u7559\u672c\u6ce2 "
    "A \u7a97\u00b7\u00a75.5 \u9884\u62ab\u9732\u6ce8\u8bb0\u5728\u6848\u00b7r885 probe \u5b9e\u8bc1 B 428_204..428_403 "
    "\u5151\u73b0\uff09\u3002\r\n"
    "- \u5b9d\u85cf/\u65b9\u6cd5\u8bba\u6355\u83b7\u95ee\uff1a\u672c\u6279 finalize one-pass=canonical "
    "runner \u5355\u53d1 r718 \u5148\u4f8b verbatim \u590d\u7528\u96f6\u65b0\u65b9\u6cd5\u96f6\u65b0\u5b9d\u85cf"
    "\uff1bTREASURE/METHODOLOGY \u96f6 append\u3002\r\n"
    "- \u8bda\u5b9e\u62ab\u9732\u9762\uff1a\u8d26\u672c\u6295\u5f71\u5dee **\u96f6**\uff08\u5e72\u51c0\u5165\u94fe\uff09"
    "\uff1bW186-only mu {m}0.1025 \u4e0e\u5408\u5e76\u6c60 {m}0.0929 \u5dee 0.0096\uff08\u8f83 W185 \u7684 "
    "0.0064 \u653e\u5bbd\u00b7null \u62bd\u6837\u5355\u6ce2 2,200 \u9762\u5c0f\u6837\u672c\u6ce2\u52a8"
    "\u00b7\u56db\u9884\u952e\u2460\u4ecd PASS\uff09\uff1bmu_delta {m}0.003301=W186 w-only \u8f83 "
    "W185ext-only\uff08{m}0.0992\uff09\u540c\u5411\u6df1\u5316\uff08\u5355\u6ce2 w-only \u9762\u6ce2\u52a8"
    "\u00b7\u95e8\u5185\u5982\u5b9e\u62ab\u9732\uff09\uff1bA p95 0.3004 \u8f83 W185 \u952a 0.3066 \u4e0b\u79fb "
    "{m}0.0062 \u4ecd\u95e8\u5185\uff08<0.05\u00b7\u6d4b\u91cf\u9762\u975e\u6ce8\u518c\u5229\u76ca\uff09"
    "\uff1bline_pre 1.1859 \u8f83 W185 \u6536\u5b98 1.1857 \u7684 +0.0002=n_eff \u57fa "
    "812,128\u2192814,328 \u589e\u957f\u81ea\u7136\u6b65\u8fdb\u975e\u6c60\u52a0\u6df1\u6548\u5e94"
    "\uff1bK-lift **{m}0.0001**=W185 {m}0.0001 \u8fde\u7eed\u7b2c\u4e8c\u6ce2\u8d1f\u503c"
    "\uff08W154/W155/W156 {m}0.0002 \u65cf\u5148\u4f8b\u9762\u00b7\u56db\u9884\u952e\u2463 PASS\uff09"
    "\uff1b\u5408\u5e76\u6c60 K=407,120 EXACT\uff1b\u5f15\u64ce tick \u81ea\u70e7 12 \u5206\u7247"
    "\uff0815:4x\u201316:0x\uff09+finalize 16:08 \u843d\u4ef6\uff08r884 \u4e09\u6b7b\u5c3e\u590d\u5408\u6536\u53e3\u7a97"
    "\u00b7r844 dead-tail \u6536\u517b\uff09+\u00a77/\u00a78 \u56de\u586b r885 \u6b21\u7a97\u8865"
    "\uff08\u56de\u586b\u7a97\u6ce8\u8bb0\uff1aW185 \u5148\u4f8b=finalize \u540c\u7a97\u56de\u586b r879"
    "\u00b7\u672c\u6ce2 finalize \u7a97 r884 \u4e3a\u4e09\u6b7b\u5c3e\u590d\u5408\u6536\u53e3\u7a97\u6ee1\u8f7d"
    "\u00b7\u00a77/\u00a78 \u987a\u5ef6\u81f3 r885 \u5f00\u7a97\u9996\u817f\u5373\u523b\u8865"
    "\u00b7\u975e\u62d6\u5ef6\u7a97\u5bf9\u7167 W159/W168/W169/W180\u00b7\u5982\u5b9e\u6ce8\u8bb0\uff09"
    "+commit \u6536\u53e3\u3002"
).format(m=M)

src = io.open(PF, encoding="utf-8", newline="").read()
assert src.count("\r\n") >= 60, "CRLF convention drift"
assert src.count(S7_OLD) == 1, "sec7 placeholder not unique/found"
assert src.count(S8_OLD) == 1, "sec8 placeholder not unique/found"
out = src.replace(S7_OLD, S7_NEW).replace(S8_OLD, S8_NEW)
assert out != src and out.count("\u5360\u4f4d") == 0, "placeholder residue"
assert "W187 finalize \u7a97" not in out, "stale placeholder wave face"
assert out.count("\r\n") >= 60 and "\r\r" not in out, "EOL drift"
io.open(PF, "w", encoding="utf-8", newline="").write(out)
chk = io.open(PF, encoding="utf-8", newline="").read()
assert chk == out, "roundtrip drift"
print("W186 sec7/sec8 backfill rc0: bytes %d -> %d, crlf=%d" %
      (len(src.encode("utf-8")), len(chk.encode("utf-8")), chk.count("\r\n")))
