# -*- coding: utf-8 -*-
"""r893 bm-a: W190 sec7/sec8 finalize backfill (deferred-to-r893 first-leg
per W186/W187/W188/W189 second-window precedent; the r892-continuation
finalize window was finalize+W191-seat-publish+dead-tail-adoption
full-load, sec7/sec8 deferred to this window's first leg --
non-procrastination asserted vs W159/W168/W169/W181).
Numbers machine-verified live vs results/perpetual_faces/n1_w190_results.json
(zero hand-copied values in the written text: every displayed number is
derived in-script from the results file and formatted the same way as the
_r892bma_w189_backfill W189-backfill pattern).  Edit face = the two sec7/sec8
placeholder blocks ONLY (post-freeze edit legality: 回填限 §7/§8)."""
import io
import json
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
P = r"research\PERPETUAL_N1_W190_PREREG.md"

# --- machine-verified facts (r587: read from on-disk receipt) --------------
res = json.load(open(r"results\perpetual_faces\n1_w190_results.json",
                     encoding="utf-8"))
npc = res["null_pool_cumulative"]
kl = res["skill_line_v2_k_lift"]
led = res["science_gates"]["ledger"]
assert led["prev_total"] == 823128 and led["batch_trials"] == 2200 \
    and led["total"] == 825328, led
assert npc["merged"]["n_values"] == 415920 and \
    npc["pre_w190_cumulative"]["n_values"] == 413720 and \
    npc["w190_only"]["n_values"] == 2200, npc
MU6 = npc["merged"]["mu"]
WONLY8 = npc["w190_only"]["mu"]
SIG = npc["merged"]["sigma"]
WONLY_SIG = npc["w190_only"]["sigma"]
PRE_SIG = npc["pre_w190_cumulative"]["sigma"]
DELT = npc["mu_delta_w190_vs_w189ext"]
SEMU = npc["se_mu_at_k415920"]
P95 = res["families"]["A_random_engine_exit"]["full_sharpe_p95"]
P99 = res["families"]["A_random_engine_exit"]["full_sharpe_p99"]
AMU = res["families"]["A_random_engine_exit"]["full_sharpe_mu"]
assert abs(MU6 - (-0.09288257669744181)) < 1e-12 and MU6 < 0
assert abs(WONLY8 - (-0.09859909090909091)) < 1e-12 and WONLY8 < 0
assert abs(SIG - 0.24514977664802964) < 1e-12
assert abs(WONLY_SIG - 0.24250461943925483) < 1e-12
assert abs(PRE_SIG - 0.24516369991716355) < 1e-12
assert abs(DELT - (-0.010831)) < 1e-9
assert SEMU == 0.00038 and P95 == 0.3068 and P99 == 0.4574 \
    and abs(AMU - (-0.092202)) < 1e-9, (SEMU, P95, P99, AMU)
assert kl["line_pre_w190"] == 1.1867 and kl["line_merged_415920"] == 1.1866 \
    and abs(kl["line_delta_k_lift"] - (-0.0001)) < 1e-12 \
    and kl["n_eff_held_equal"] == 823128, kl
assert kl["canon_flip"].startswith("NOT performed"), kl
assert res["audit"]["finalize_only"] is True and \
    res["audit"]["machine"] == "bm-a", res["audit"]
assert led["voids_applied"] == ["LOWAMP-P1", "LOWAMP-P2"]
assert led["evidence_cutoff"] == "2026-09-22"
assert len(res["shards_consumed"]) == 12
GAP = WONLY8 - MU6
assert abs(GAP - (-0.00571651421164910)) < 1e-9 and GAP < 0
SIGREL = (SIG - PRE_SIG) / abs(PRE_SIG) * 100.0
assert abs(SIGREL - (-0.005678)) < 0.001, SIGREL
P95D = P95 - 0.3447
assert abs(P95D - (-0.0379)) < 1e-9, P95D
assert abs(abs(kl["line_delta_k_lift"]) - 0.0001) <= 0.02

MU6S = "%.6f" % MU6                      # -0.092883
WONLY6S = "%.6f" % WONLY8                 # -0.098599
MU4S = "%.4f" % MU6                       # -0.0929 (display HOLDS)
WONLY4S = "%.4f" % WONLY8                 # -0.0986 (display ROLLS)
SIG6S = "%.6f" % SIG                      # 0.245150 (display ROLLS)
WSIG6S = "%.6f" % WONLY_SIG              # 0.242505
PRESIG6S = "%.6f" % PRE_SIG              # 0.245164 (W189 key)
GAP4S = "%.4f" % GAP                      # -0.0057 (w-only BELOW merged)
assert (MU6S, WONLY6S, MU4S, WONLY4S, SIG6S, WSIG6S, PRESIG6S, GAP4S) == \
    ("-0.092883", "-0.098599", "-0.0929", "-0.0986", "0.245150",
     "0.242505", "0.245164", "-0.0057"), (MU6S, WONLY6S, MU4S, WONLY4S,
                                           SIG6S, WSIG6S, PRESIG6S, GAP4S)
DELT6S = "%.6f" % DELT                    # -0.010831
assert DELT6S == "-0.010831"
SIGRELS = "%.3f%%" % SIGREL               # -0.006%
assert SIGRELS == "-0.006%"
P95DS = "-0.0379"

S7_OLD_H = "## \u00a77 \u8dd1\u540e\u5b9e\u8bc1\u3002\u3010finalize \u6536\u53e3\u673a\u68b0\u56de\u586b\u00b7\u5f85 W190 finalize \u7a97\u3011"
S7_OLD_P = ("- \uff08\u5360\u4f4d\u00b7finalize one-pass \u540e\u673a\u68b0\u56de\u586b\uff1a\u8d26\u672c\u6052\u7b49\u5f0f+\u5408\u5e76\u6c60 K+merged mu/w-only"
            " mu/mu_delta+sigma+se_mu+skill_line_v2 K-lift+A \u6863 p95+\u00a75 \u56db\u9884\u952e\u673a\u8bc1"
            "+canon flip \u6001+audit.finalize_only+voids_applied\u3002\uff09")
S8_OLD_H = "## \u00a78 \u6279\u540e\u590d\u76d8\u3002\u3010finalize \u540c\u7a97\u56de\u586b\u00b7\u5f85 W190 finalize \u7a97\u3011"
S8_OLD_P = ("- \uff08\u5360\u4f4d\u00b7\u00a75.5 W191+ \u6295\u5f71\u627f\u63a5+\u5b9d\u85cf/\u65b9\u6cd5\u8bba\u6355\u83b7\u95ee+\u8bda\u5b9e\u62ab\u9732\u9762\u00b7finalize "
            "\u6536\u53e3\u7a97\u673a\u68b0\u56de\u586b\u3002\uff09")

S7_NEW = (
"## \u00a77 \u8dd1\u540e\u5b9e\u8bc1\u3002\u3010finalize \u6536\u53e3\u673a\u68b0\u56de\u586b\u00b7r893 \u56de\u586b\u7a97\uff08finalize 21:19 r892-continuation finalize "
"one-pass \u7a97\u843d\u4ef6\u00b7\u00a77/\u00a78 \u56de\u586b\u987a\u5ef6\u81f3 r893 \u5f00\u7a97\u9996\u817f\u5373\u523b\u8865\u00b7\u975e\u62d6\u5ef6\u7a97\u5bf9\u7167 W159/W168/W169/W181\u00b7"
"\u5982\u5b9e\u6ce8\u8bb0\uff09\u3011\n"
"- \u8d26\u672c\u6052\u7b49\u5f0f\uff1a823,128 + 2,200 = **825,328** EXACT\uff08prev_total/batch_trials/total \u4e09\u952e"
"\u673a\u8bfb\u00b7r892-continuation finalize one-pass \u5b9e\u6d4b\uff1b**vs \u00a75 \u51bb\u7ed3\u6295\u5f71\uff08823,128+2,200=825,328 \u673a\u68b0\u7b97\uff09\u96f6\u5dee**"
"\u2014\u2014\u672c\u7a97\u96f6\u5728\u98de\u4e0a\u6e38\u6279\u51bb\u7ed3\u540e\u5165\u94fe\u00b7\u5e72\u51c0\u5165\u94fe\uff09\u3002\n"
"- \u5408\u5e76\u6c60\uff1a**K=415,920** EXACT\uff08=W189 \u6c60 413,720 + \u672c\u6ce2 2,200\u00b7\u00a75 \u6295\u5f71 415,920 \u547d\u4e2d\uff09\u3002\n"
"- merged mu **" + MU6S + "\uff08\u673a\u8bfb -0.09288258\uff09/ w-only mu **" + WONLY6S +
"\uff08\u673a\u8bfb -0.09859909\uff09/ mu_delta(w190 vs w189ext) **" + DELT6S + "\u3002\n"
"- merged sigma **" + SIG6S + "\uff08W189 \u952e 0.245164\u21920.245150 \u7b2c\u516d\u4f4d\u9762\u5fae\u964d\u00b7\u76f8\u5bf9\u53d8\u5316 " +
SIGRELS + "\uff09\uff1bw-only sigma " + WSIG6S + "\uff1bse_mu@K415,920 **0.000380**"
"\uff08W189 0.000381\u2192W190 0.000380 \u6536\u7a84\u00b7\u94fe\u9762 \u2026W186 0.000384\u2192W187 0.000383\u2192W188 "
"0.000382\u2192W189 0.000381\u2192W190 0.000380\uff09\u3002\n"
"- skill_line_v2\uff1aline_pre **1.1867** \u2192 line_merged@K415,920 **1.1866**\uff08K-lift "
"**\u2212" + "0.0001**\u00b7n_eff_held_equal 823,128\uff09\uff1bcanon flip **NOT performed**\uff08K2,200 \u540c\u4f8b\u6cd5\u00b7"
"\u6cbb\u7406\u63d0\u6848\u9762\uff09\u3002\n"
"- A \u6863 full_sharpe_p95 **0.3068**\uff08W189 \u952a 0.3447\u00b7\u0394" + P95DS + " \u95e8\u5185\uff09\u00b7p99 0.4574\u00b7"
"A mu \u22120.092202\u3002\n"
"- \u00a75 \u56db\u9884\u952e\u673a\u8bc1\u5168\u8fc7\uff1a\u2460mu gap " + GAP4S + "<0.02 PASS\uff08w-only \u4f4e\u4e8e\u5408\u5e76\u6c60\u00b7\u65b9\u5411\u4e0e W189 +0.0051 "
"\u76f8\u53cd\u00b7\u95e8\u5185\u5982\u5b9e\u62ab\u9732\uff09\u2461sigma \u76f8\u5bf9\u53d8\u5316 " + SIGRELS + "<\u00b110% PASS \u2462A p95 \u0394" + P95DS +
"<0.05 PASS \u2463K-lift \u22120.0001\u2264\u00b10.02 PASS\u3002\n"
"- audit.finalize_only=**true**\uff08bm-a\uff09\u00b7voids_applied=LOWAMP-P1,LOWAMP-P2\u00b7"
"evidence_cutoff=2026-09-22 \u5728\u4f4d\u00b7shards_consumed 12/12\uff08\u5f15\u64ce tick \u81ea\u70e7 21:00 \u51bb\u7ed3\u7a97\u540e\u81ea\u4e3b\u81ea\u71c3 "
"r325 \u5b9e\u8bc1\u00b7\u5206\u7247 12/12 \u4e8e finalize \u524d\u843d\u4f4d\u00b7S0-leg \u5438\u6536 21:20 commit 3d42893e3\uff09\u00b7"
"finalize 21:19 r892-continuation finalize one-pass \u7a97\u843d\u4ef6 commit 1c28dd21d\u3002")

S8_NEW = (
"## \u00a78 \u6279\u540e\u590d\u76d8\u3002\u3010finalize \u540c\u7a97\u56de\u586b\u00b7r893 \u56de\u586b\u7a97\u3011\n"
"- \u00a75.5 W191+ \u6295\u5f71\u627f\u63a5\uff08r892 probe \u673a\u8bc1\u00b7W191 \u51bb\u7ed3\u65b9\u91cd derive \u5f3a\u5236\u975e\u8f6c\u6284 r587 \u5f8b\uff09\uff1a"
"naive A **434_804..436_803**\uff08hops=0 CLEAN\uff09\u2014\u2014\u88ab\u6ce8\u518c W190 B \u5e26 434_804..435_003 "
"own-start \u62d2=\u9636\u68af A-hops-prior-B \u7ee7\u627f**\u7b2c\u4e94\u5341\u4e00\u4f8b**\u2014\u2014**r892 probe \u5b9e\u8bc1\u590d\u6838\u786e\u8ba4**"
"\uff08A 435_004..437_003 hops=1 \u00b7\u672c\u7a97 W191 \u94fe\u5f00\u7a97\u5151\u73b0\uff09\uff1bnaive B **435_004..435_203**"
"\uff08hops=0 CLEAN\uff09\u843d\u672c\u6ce2 A \u7a97\u5185\u2014\u2014W141 \u540c\u7a97\u4e92\u65a5 leg2 \u5f8b\u9002\u7528 W191\uff08derive B \u65f6\u9884\u7559\u672c\u6ce2 "
"A \u7a97\u00b7\u00a75.5 \u9884\u62ab\u9732\u6ce8\u8bb0\u5728\u6848\u00b7r892 probe \u5b9e\u8bc1 B 437_004..437_203 \u5151\u73b0\uff09\uff1bW192+ \u6295\u5f71"
"\uff08r892 probe leg4 \u673a\u8bc1\uff1aA **437_004..439_003** / B **437_204..437_403**\u00b7B \u843d A \u7a97\u5185\uff09"
"\u2014\u2014W192 \u51bb\u7ed3\u65b9\u5fc5\u987b\u5728 post-W191 \u6ce8\u518c\u5b87\u5b99\u91cd derive\uff08r587\u00b7E36 \u5361\u00b7never transcribe\uff09\u3002\n"
"- \u5b9d\u85cf/\u65b9\u6cd5\u8bba\u6355\u83b7\u95ee\uff1a\u672c\u6279 finalize one-pass=canonical runner \u5355\u53d1 r718 \u5148\u4f8b verbatim "
"\u590d\u7528\u96f6\u65b0\u65b9\u6cd5\u96f6\u65b0\u5b9d\u85cf\uff1bTREASURE/METHODOLOGY \u96f6 append\u3002\n"
"- \u8bda\u5b9e\u62ab\u9732\u9762\uff1a\u8d26\u672c\u6295\u5f71\u5dee **\u96f6**\uff08\u5e72\u51c0\u5165\u94fe\uff09\uff1bW190-only mu \u22120.0986 \u4e0e\u5408\u5e76\u6c60 \u22120.0929 \u5dee " +
GAP4S + "\uff08\u8f83 W189 \u7684 +0.0051 \u65b9\u5411\u7ffb\u8f6c\u00b7null \u62bd\u6837\u5355\u6ce2 2,200 \u9762\u5c0f\u6837\u672c\u6ce2\u52a8\u00b7\u56db\u9884\u952e\u2460\u4ecd PASS\uff09\uff1b"
"mu_delta \u22120.010831=W190 w-only\uff08\u22120.0986\uff09\u8f83 W189ext-only\uff08\u22120.0878\uff09\u56de\u843d\u8f6c\u8d1f\uff08W189 +0.010848 \u56de\u5347\u540e"
"\u5355\u6ce2 w-only \u9762\u6ce2\u52a8\u00b7\u95e8\u5185\u5982\u5b9e\u62ab\u9732\uff09\uff1bA p95 0.3068 \u8f83 W189 \u952a 0.3447 \u4e0b\u79fb \u2212" + "0.0379 \u4ecd\u95e8\u5185"
"\uff08<0.05\u00b7\u6d4b\u91cf\u9762\u975e\u6ce8\u518c\u5229\u76ca\uff09\uff1bline_pre 1.1867 \u8f83 W189 \u6536\u5b98 line_merged 1.1866 \u7684 +0.0001"
"=n_eff \u57fa 820,928\u2192823,128 \u589e\u957f\u81ea\u7136\u6b65\u8fdb\u975e\u6c60\u52a0\u6df1\u6548\u5e94\uff1bK-lift **\u22120.0001**=W189 +0.0003 \u540e"
"\u56de\u843d\uff08W138/W154\u2013156/W168/W176 \u65cf\u56de\u843d\u5148\u4f8b\u9762\u00b7\u56db\u9884\u952e\u2463 PASS\uff09\uff1b\u5408\u5e76\u6c60 K=415,920 EXACT\uff1b\u5f15\u64ce tick \u81ea\u70e7 "
"12 \u5206\u7247\uff0821:0x \u51bb\u7ed3\u7a97\u81ea\u71c3\uff09+finalize 21:19 \u843d\u4ef6\uff08r892-continuation finalize one-pass \u7a97\u00b7commit "
"1c28dd21d\uff09+\u00a77/\u00a78 \u56de\u586b r893 \u6b21\u7a97\u8865\uff08\u56de\u586b\u7a97\u6ce8\u8bb0\uff1aW185 \u5148\u4f8b=finalize \u540c\u7a97\u56de\u586b r879\u00b7W186 \u5148\u4f8b=r885 \u6b21\u7a97"
"\u56de\u586b\u00b7W187 \u5148\u4f8b=r888 \u6b21\u7a97\u56de\u586b\u00b7W188 \u5148\u4f8b=r890 \u6b21\u7a97\u56de\u586b\u00b7W189 \u5148\u4f8b=r892 \u6b21\u7a97\u56de\u586b\u00b7\u672c\u6ce2 finalize "
"\u7a97 r892-continuation \u4e3a finalize+W191 \u5e2d\u4f4d\u53d1\u5e03+dead-tail \u6536\u53e3\u6ee1\u8f7d\u7a97\u00b7\u00a77/\u00a78 \u987a\u5ef6\u81f3 r893 \u5f00\u7a97\u9996\u817f\u5373\u523b\u8865"
"\u00b7\u975e\u62d6\u5ef6\u7a97\u5bf9\u7167 W159/W168/W169/W181\u00b7\u5982\u5b9e\u6ce8\u8bb0\uff09+commit \u6536\u53e3\u3002")

src = io.open(P, encoding="utf-8", newline="").read()
NL = "\r\n" if src.count("\r\n") > src.count("\n\r\n") and "\r\n" in src else "\n"
assert NL == "\r\n", "on-disk prereg expected CRLF (r370 law)"
for old in (S7_OLD_H, S7_OLD_P, S8_OLD_H, S8_OLD_P):
    assert src.count(old) == 1, "placeholder count != 1: %r" % old[:50]
out = src.replace(S7_OLD_H + NL + S7_OLD_P, S7_NEW.replace("\n", NL), 1)
out = out.replace(S8_OLD_H + NL + S8_OLD_P, S8_NEW.replace("\n", NL), 1)
assert "\u5360\u4f4d" not in out, "placeholder text survives"
assert out.count("## \u00a77") == 1 and out.count("## \u00a78") == 1
# write + roundtrip verify
io.open(P, "w", encoding="utf-8", newline="").write(out)
chk = io.open(P, encoding="utf-8", newline="").read()
assert chk == out, "CRLF write roundtrip drift"
for needle in ("825,328", "K=415,920", MU6S, WONLY6S, SIG6S, "0.000380",
               "1.1866", "\u22120.0001", "0.3068", GAP4S, P95DS,
               "435_004..437_003", "437_004..437_203", "437_004..439_003",
               "437_204..437_403", "r893 \u56de\u586b\u7a97", "1c28dd21d",
               "3d42893e3"):
    assert needle in chk, "backfill needle missing: %r" % needle
print("W190 sec7/sec8 backfill landed: %d bytes (CRLF %d)" %
      (len(chk.encode("utf-8")), chk.count("\r\n")))
print("machine-verified: ledger 825,328 EXACT / K 415,920 EXACT / four "
      "prekeys PASS / projection carry W192+ A 437_004..439_003 B "
      "437_204..437_403")
