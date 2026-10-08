# -*- coding: utf-8 -*-
"""r904 bm-a: W193 prereg sec7/sec8 machine backfill (estate cross-window
closeout).  All numbers derived from the results JSONs at run time (r587
zero-transcribe).  Finalize product = r903 dead-session one-pass output
(07:00:46), adopted per r899/r902 estate law; key-order precondition
(W192 landed on origin) machine-checked here.
"""
import io
import json
import subprocess

M = "\u2212"
G = r"C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney"
PREREG = "research/PERPETUAL_N1_W193_PREREG.md"

def git(*a):
    r = subprocess.run(["git", "-C", G] + list(a), capture_output=True)
    return r.stdout

# --- machine facts -------------------------------------------------------
w193 = json.load(open("results/perpetual_faces/n1_w193_results.json",
                      encoding="utf-8"))
w192 = json.loads(git("show",
                      "origin/main:results/perpetual_faces/n1_w192_results.json")
                  .decode("utf-8"))
w191 = json.load(open("results/perpetual_faces/n1_w191_results.json",
                      encoding="utf-8"))
probe = json.load(open("results/_r902bma_w194_probe_receipt.json",
                       encoding="utf-8"))

led, led192, led191 = (w193["science_gates"]["ledger"],
                      w192["science_gates"]["ledger"],
                      w191["science_gates"]["ledger"])
npc, npc192, npc191 = (w193["null_pool_cumulative"],
                       w192["null_pool_cumulative"],
                       w191["null_pool_cumulative"])
kl, kl192, kl191 = (w193["skill_line_v2_k_lift"],
                    w192["skill_line_v2_k_lift"],
                    w191["skill_line_v2_k_lift"])
fam = w193["families"]["A_random_engine_exit"]

# continuity asserts (key-order r307 face + ledger chain)
assert led["prev_total"] == led192["total"] == 836745, "ledger chain break"
assert led["total"] == 836745 + 2200 == 838945, "ledger equation"
assert npc["merged"]["n_values"] == npc192["merged"]["n_values"] + 2200 \
    == 422520, "K chain"
assert w193["audit"] == {"machine": "bm-a", "finalize_only": True}
assert w193["evidence_cutoff"] == "2026-09-22"
assert led["voids_applied"] == ["LOWAMP-P1", "LOWAMP-P2"]
assert len(w193["shards_consumed"]) == 12
leg1 = probe["legs"]["leg1"]
assert "FIFTY-FOURTH" in leg1["A_semantics"], leg1["A_semantics"]
assert leg1["A"] == [441604, 443603] and leg1["B"] == [443604, 443803]
assert leg1["hops_A"] == 1 and leg1["hops_B"] == 1

mu = npc["merged"]["mu"]            # -0.09285383
mu_w = npc["w193_only"]["mu"]       # -0.09282082
mu_w192 = npc192["w192_only"]["mu"] # -0.09047405
sig = npc["merged"]["sigma"]        # 0.24509981
sig_w = npc["w193_only"]["sigma"]
semu = npc["se_mu_at_k422520"]
semu192 = npc192["se_mu_at_k420320"]
semu191 = npc191["se_mu_at_k418120"]
mu4 = ("%.4f" % mu).replace("-", M)
mu6 = "%.6f" % mu
muw6 = "%.6f" % mu_w
sig6 = "%.6f" % sig
sigw6 = "%.6f" % sig_w
delta_w = mu_w - mu_w192
gap = abs(mu_w - mu)
sigkey = npc191["merged"]["sigma"]           # 0.245166 (W191 pred key)
sigrel = (sig - sigkey) / sigkey * 100.0
p95 = fam["full_sharpe_p95"]
p95key = w191["families"]["A_random_engine_exit"]["full_sharpe_p95"]  # .3049
p95d = p95 - p95key
kl_delta = kl["line_delta_k_lift"]
assert kl["n_eff_held_equal"] == 836745
assert kl["line_pre_w193"] == 1.1873
assert kl["line_merged_422520"] == 1.1872
assert abs(kl_delta - (-0.0001)) < 1e-12
# four pred keys (vs W191 keys per sec5 freeze)
assert gap < 0.02, "key1"
assert abs(sigrel) < 10.0, "key2"
assert abs(p95d) < 0.05, "key3"
assert abs(kl_delta) <= 0.02, "key4"
assert led191["total"] == 833536  # W191 anchor head (sec5 key context)

S7_HEADER_OLD = (
    "## \u00a77 \u8dd1\u540e\u5b9e\u8bc1\u3002\u3010finalize \u6536\u53e3"
    "\u673a\u68b0\u56de\u586b\u00b7\u5f85 W193 finalize \u7a97\u3011")
S7_HEADER_NEW = (
    "## \u00a77 \u8dd1\u540e\u5b9e\u8bc1\u3002\u3010finalize \u6536\u53e3"
    "\u673a\u68b0\u56de\u586b\u00b7r904 \u56de\u586b\u7a97\uff08r903 \u4f1a"
    "\u8bdd 07:00:46 one-pass \u843d\u4ef6\u540e\u8be5\u4f1a\u8bdd\u65e0"
    "\u6536\u8f6e\u6d88\u4ea1\u2014\u2014r904 \u7ee7\u627f\u6267\u884c"
    "\u4f53 estate \u5438\u6536\u00b7\u00a77/\u00a78 \u8de8\u7a97\u56de"
    "\u586b\u00b7r864 \u540c\u7a97\u6559\u8bad\u4f8b\u5916\u8def\u5f84"
    "\u5982\u5b9e\u6ce8\u8bb0\uff09\u3011")
S7_BODY_OLD = (
    "- \uff08\u5360\u4f4d\u00b7finalize one-pass \u540e\u673a\u68b0\u56de"
    "\u586b\uff1a\u8d26\u672c\u6052\u7b49\u5f0f+\u5408\u5e76\u6c60 K+merged "
    "mu/w-only mu/mu_delta+sigma+se_mu+skill_line_v2 K-lift+A \u6863 p95"
    "+\u00a75 \u56db\u9884\u952e\u673a\u8bc1+canon flip \u6001+audit."
    "finalize_only+voids_applied\u3002\uff09")
S8_HEADER_OLD = (
    "## \u00a78 \u6279\u540e\u590d\u76d8\u3002\u3010finalize \u540c\u7a97"
    "\u56de\u586b\u00b7\u5f85 W193 finalize \u7a97\u3011")
S8_HEADER_NEW = (
    "## \u00a78 \u6279\u540e\u590d\u76d8\u3002\u3010finalize \u6536\u53e3"
    "\u673a\u68b0\u56de\u586b\u00b7r904 \u56de\u586b\u7a97\uff08estate \u8de8"
    "\u7a97\u6536\u53e3\uff09\u3011")
S8_BODY_OLD = (
    "- \uff08\u5360\u4f4d\u00b7\u00a75.5 W194+ \u6295\u5f71\u627f\u63a5+"
    "\u5b9d\u85cf/\u65b9\u6cd5\u8bba\u6355\u83b7\u95ee+\u8bda\u5b9e\u62ab"
    "\u9732\u9762\u00b7finalize \u6536\u53e3\u7a97\u673a\u68b0\u56de\u586b"
    "\u3002\uff09")

S7_BODY_NEW = "\n".join([
    "- \u8d26\u672c\u6052\u7b49\u5f0f\uff1a836,745 + 2,200 = **838,945** "
    "EXACT\uff08prev_total/batch_trials/total \u4e09\u952e\u673a\u8bfb"
    "\u00b7prev==W192 \u5df2\u843d\u8d26 total \u6052\u7b49\u3010origin "
    "n1_w192_results.json \u673a\u8bc1\u3011\u00b7\u8d26\u672c\u94fe\u96f6"
    "\u5206\u53c9\uff08+6,008 \u578b\u504f\u79bb\u96f6\u53d1\u751f\u2014"
    "\u2014\u5e72\u51c0\u94fe\uff09\u3002",
    "- \u5408\u5e76\u6c60\uff1a**K=422,520** EXACT\uff08=W192 \u6c60 "
    "420,320 + \u672c\u6ce2 2,200\u00b7\u00a70 \u51bb\u7ed3\u7a97\u6295"
    "\u5f71 422,520 \u547d\u4e2d\uff09\u3002",
    "- merged mu **%s%s**\uff08\u673a\u8bfb %s\u00b74dp **%s%s** U+2212 "
    "\u663e\u793a\u4fdd\u6301\u2014\u2014W191 %s%s\u2192W192 %s%s\u2192"
    "W193 %s%s \u8de8\u4e09\u952e\u7eed\u6301\uff09/ w-only mu "
    "**%s%s**\uff08\u673a\u8bfb %s\uff09/ mu_delta(w193 vs w192ext) "
    "**%s%s**\u3002" % (M, mu6[1:], mu, M, mu4[1:], M, "0.0929", M,
                        "0.0929", M, "0.0929", M, muw6[1:], mu_w,
                        ("+" if delta_w >= 0 else M),
                        "%.6f" % abs(delta_w)),
    "- merged sigma **%s**\uff08\u00a75 W191 \u952e 0.245166\u2192%s\u00b7"
    "\u76f8\u5bf9\u53d8\u5316 %s%.4f%%\uff09\uff1bw-only sigma %s\uff1b"
    "se_mu@K422,520 **0.000377**\uff08W191 0.000379\u2192W192 0.000378"
    "\u2192W193 0.000377 \u6536\u7a84\u94fe\u7eed\uff09\u3002"
    % (sig6, sig6, ("+" if sigrel >= 0 else M), abs(sigrel), sigw6),
    "- skill_line_v2\uff1aline_pre **1.1873** \u2192 line_merged@K422,520 "
    "**1.1872**\uff08K-lift **%s0.0001**\u00b7n_eff_held_equal 836,745"
    "\uff09\uff1bcanon flip **NOT performed**\uff08K2,200 \u540c\u4f8b"
    "\u6cd5\u00b7\u6cbb\u7406\u63d0\u6848\u9762\uff09\u3002" % M,
    "- A \u6863 full_sharpe_p95 **%.4f**\uff08\u00a75 W191 \u952e 0.3049"
    "\u00b7\u0394%s%.4f \u95e8\u5185\u00b7W192 \u952e 0.2989 \u5bf9"
    "\u7167\u0394%s%.4f\uff09\u00b7p99 %.4f\u3002"
    % (p95, M, abs(p95d), M, abs(p95 - 0.2989), fam["full_sharpe_p99"]),
    "- \u00a75 \u56db\u9884\u952e\u673a\u8bc1\u5168\u8fc7\uff1a\u2460mu "
    "gap %.6f<0.02 PASS\uff08w193-only %s \u4e0e merged %s \u8de8\u952e"
    "\u5fae\u00b7\u5148\u4f8b\u7eed\uff09\u2461sigma \u76f8\u5bf9\u53d8"
    "\u5316 %s%.4f%%<\u00b110%% PASS\u2462A p95 \u0394%s%.4f<0.05 "
    "PASS\u2463K-lift \u2212 0.0001\u2264\u00b10.02 PASS\uff08W191 \u952e "
    "+0.0001\u00b7W192 \u2212 0.0002 \u540e\u8fde\u7eed\u7b2c\u4e8c\u6ce2"
    "\u8d1f\u503c\u00b7\u8d1f\u503c\u5148\u4f8b\u65cf W138/W154-156/W168 "
    "\u7b49\u95e8\u5185\u5982\u5b9e\u62ab\u9732\uff09\u3002"
    % (gap, muw6, mu6, ("+" if sigrel >= 0 else M), abs(sigrel), M,
       abs(p95d)),
    "- audit.finalize_only=**true**\uff08bm-a\uff09\u00b7voids_applied="
    "LOWAMP-P1,LOWAMP-P2\u00b7evidence_cutoff=2026-09-22 \u5728\u4f4d"
    "\u00b7shards_consumed 12/12\uff08r902 \u70b9\u706b\u5f15\u64ce\u81ea"
    "\u70e7 06:10-06:22 12 \u5206\u7247\u3010r325 \u4ea7\u7269\u589e\u957f"
    "\u9762\u3011\u00b7finalize one-pass=r903 \u4f1a\u8bdd\u7a97 07:00:46 "
    "\u843d\u4ef6\u00b7\u952e\u5e8f\u524d\u7f6e W192 \u843d\u8d26\u6ee1"
    "\u8db3\u3010n1_w192_results.json origin \u5728\u518c\u673a\u8bc1"
    "\u00b7FAIL-CLOSED r307 \u590d\u6838\u8fc7\u3011\uff09\u3002",
])

S8_BODY_NEW = "\n".join([
    "- \u00a75.5 W194+ \u6295\u5f71\u627f\u63a5\uff08r902 pre-seat probe "
    "\u673a\u8bc1\u00b7W194 \u5e2d\u4f4d\u5df2\u53d1\u5e03=MSG-2026-10-09"
    "-0627-bma-w194-seat\u00b7r587 never-transcribe \u5f8b\uff09\uff1a"
    "naive A **441_404..443_403** own-start \u88ab\u6ce8\u518c W193 B \u5e26 "
    "441_404..441_603 \u62d2=\u9636\u68af A-hops-prior-B \u7ee7\u627f"
    "**\u7b2c\u4e94\u5341\u56db\u4f8b**\uff08\u00a75.5 \u9884\u62ab\u9732"
    "\u5151\u73b0\uff09\u2014\u2014r902 probe \u5b9e\u8bc1 **A 441_604.."
    "443_603\uff0chops=1**\uff1bnaive B **441_604..441_803** \u843d\u672c"
    "\u6ce2 A \u7a97\u5185\u2014\u2014W141 \u540c\u7a97\u4e92\u65a5 leg2 "
    "\u5f8b\u9002\u7528 W194\u2014\u2014r902 probe \u5b9e\u8bc1 **B "
    "443_604..443_803\uff0chops=1**\uff08own-A \u4fdd\u7559\uff09\uff1b"
    "W195+ \u6295\u5f71\uff08r902 probe leg4 \u673a\u8bc1\uff1anaive A "
    "443_604..445_603 / naive B 443_804..444_003\u00b7B \u843d A \u7a97"
    "\u5185\uff09\u2014\u2014W195 \u51bb\u7ed3\u65b9\u5fc5\u987b\u5728 "
    "post-W194 \u6ce8\u518c\u5b87\u5b99\u91cd derive\uff08r587\u00b7E36 "
    "\u5361\u00b7never transcribe\u00b7\u9636\u68af**\u7b2c\u4e94\u5341"
    "\u4e94\u4f8b**\u9884\u544a=W194-B-refuses-W195-A\uff09\u3002",
    "- \u5b9d\u85cf/\u65b9\u6cd5\u8bba\u6355\u83b7\u95ee\uff1a\u672c\u6279 "
    "finalize=\u65e2\u6709 one-pass \u8840\u7edf verbatim \u590d\u7528"
    "\uff08r846/r839 \u7cfb\uff09\uff1bestate \u5438\u6536=r899/r902 \u5148"
    "\u4f8b\u590d\u7528\u2014\u2014TREASURE/METHODOLOGY \u96f6 append\u3002",
    "- \u8bda\u5b9e\u62ab\u9732\u9762\uff1afinalize \u6267\u884c\u4f53="
    "r903 \u4f1a\u8bdd\uff0807:00:46 \u843d\u4ef6\u540e\u8be5\u4f1a\u8bdd"
    "\u65e0\u6536\u8f6e\u6d88\u4ea1\u00b7report/state/heartbeat \u4e09"
    "\u5199\u96f6\uff09\u2014\u2014r904 \u7ee7\u627f\u6267\u884c\u4f53"
    "\u6309 estate \u4e09\u9762\u5224\u5b9a\uff08\u8fdb\u7a0b census "
    "\u65e0 r903 \u7ebf+\u5de5\u4f5c\u4ef6 mtime 07:02 \u540e\u96f6\u65b0"
    "\u5199+\u96f6 closeout\uff09\u5438\u6536\u6536\u53e3\u3010r899/r902 "
    "\u5148\u4f8b\u3011\uff1b\u00a77/\u00a78 \u56de\u586b\u7a97=r904="
    "\u8de8\u7a97\u56de\u586b\uff08r864 \u540c\u7a97\u6559\u8bad\u7684"
    "\u4f8b\u5916\u8def\u5f84\u2014\u2014\u6b7b\u4f1a\u8bdd\u4e0d\u53ef"
    "\u81ea\u56de\u586b\u00b7\u5982\u5b9e\u6ce8\u8bb0\u975e\u9ed8\u8ba4"
    "\uff09\uff1b\u8d26\u672c\u94fe\u96f6\u5206\u53c9\uff08prev 836,745"
    "==W192 total \u6052\u7b49\uff09\uff1bK-lift \u8fde\u7eed\u7b2c\u4e8c"
    "\u6ce2\u8d1f\u503c\uff08W192 %s0.0002/W193 %s0.0001\u00b7\u95e8\u5185"
    "\u5148\u4f8b\u65cf\u5982\u5b9e\u62ab\u9732\uff09\uff1bw-only sigma "
    "%s \u663e\u4f4e\u4e8e\u5408\u5e76\u6c60 %s\uff08W191 w-only "
    "0.248260 \u5bf9\u7167\u00b7\u5355\u6ce2 w-only \u9762\u6ce2\u52a8"
    "\u95e8\u5185\u5982\u5b9e\u62ab\u9732\uff09\uff1bA p95 0.2957 \u8f83 "
    "W192 0.2989 \u5fae\u964d %s0.0032 \u4ecd\u95e8\u5185\u3002"
    % (M, M, sigw6, sig6, M),
])

raw = io.open(PREREG, encoding="utf-8", newline="").read()
crlf = raw.count("\r\n")
lf_only = raw.count("\n") - crlf
eol = "\r\n" if crlf > lf_only else "\n"
for old, new in ((S7_HEADER_OLD, S7_HEADER_NEW), (S7_BODY_OLD, S7_BODY_NEW),
                 (S8_HEADER_OLD, S8_HEADER_NEW), (S8_BODY_OLD, S8_BODY_NEW)):
    o = old.replace("\n", eol)
    n = new.replace("\n", eol)
    assert raw.count(o) == 1, "needle not unique: %r" % old[:40]
    raw = raw.replace(o, n)
assert "\u5360\u4f4d" not in raw.split("\u00a77")[-1], "placeholder residue"
assert raw.count("\u5f85 W193 finalize \u7a97") == 0, "header residue"
io.open(PREREG, "w", encoding="utf-8", newline="").write(raw)
chk = io.open(PREREG, encoding="utf-8", newline="").read()
assert chk == raw and chk.count(eol) >= (raw.count(eol)), "write roundtrip"
print("sec7/sec8 backfill LANDED: bytes=%d crlf=%d" % (len(chk.encode("utf-8")),
                                                      chk.count("\r\n")))
print("four pred keys: gap=%.6f sigrel=%.4f%% p95d=%.4f kl=%s"
      % (gap, sigrel, p95d, kl_delta))
