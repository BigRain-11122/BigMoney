# -*- coding: utf-8 -*-
"""r819 bm-a W171 prereg sec7/sec8 mechanical backfill (finalize window
missed at r816 one-pass -> this r819 settle window; W169 r812-finalize +
r813-settle precedent law, W159/W168 same-line). Zero-judgment-change
backfill: every displayed value machine-derived from
results/perpetual_faces/n1_w171_results.json (+ n1_w170_results.json for
the prior keys). r587 never-transcribe law; r773 malformed-window scan
after edit; CRLF on-disk convention preserved (r370 law)."""
import io
import json
import re

sys_enc = "utf-8"
P = r"research\PERPETUAL_N1_W171_PREREG.md"
res = json.load(open(r"results/perpetual_faces/n1_w171_results.json", encoding="utf-8"))
w170 = json.load(open(r"results/perpetual_faces/n1_w170_results.json", encoding="utf-8"))
npc = res["null_pool_cumulative"]
pre, wonly, merged = npc["pre_w171_cumulative"], npc["w171_only"], npc["merged"]
led = res["science_gates"]["ledger"]
kl = res["skill_line_v2_k_lift"]
fam = res["families"]["A_random_engine_exit"]

# --- machine-derive every displayed face (r587) -------------------------------
assert pre["n_values"] == 371920 and wonly["n_values"] == 2200 \
    and merged["n_values"] == 374120, (pre["n_values"], wonly["n_values"], merged["n_values"])
assert led["prev_total"] == 779412 and led["batch_trials"] == 2200 and led["total"] == 781612, led
assert led["voids_applied"] == ["LOWAMP-P1", "LOWAMP-P2"], led
assert kl["line_merged_374120"] == 1.1841 and kl["line_pre_w171"] == 1.1841 \
    and kl["line_delta_k_lift"] == 0.0 and kl["n_eff_held_equal"] == 779412, kl
assert kl["canon_flip"].startswith("NOT performed"), kl
assert npc["se_mu_at_k374120"] == 0.000401, npc
assert fam["n"] == 2000 and fam["full_sharpe_p95"] == 0.3177 \
    and fam["full_sharpe_p99"] == 0.4489 and fam["full_sharpe_mu"] == -0.082494, fam
assert res["audit"] == {"machine": "bm-a", "finalize_only": True}, res["audit"]
assert len(res["shards_consumed"]) == 12, res["shards_consumed"]
assert res["evidence_cutoff"] == "2026-09-22", res["evidence_cutoff"]
PREMU6 = f"{pre['mu']:.6f}"          # -0.092848
PRESIG6 = f"{pre['sigma']:.6f}"      # 0.245153
WMU6 = f"{wonly['mu']:.6f}"          # -0.088691
WSIG6 = f"{wonly['sigma']:.6f}"      # 0.244442
MMU6 = f"{merged['mu']:.6f}"         # -0.092823
MSIG6 = f"{merged['sigma']:.6f}"    # 0.245148
assert PREMU6 == "-0.092848" and PRESIG6 == "0.245153", (PREMU6, PRESIG6)
assert WMU6 == "-0.088691" and WSIG6 == "0.244442", (WMU6, WSIG6)
assert MMU6 == "-0.092823" and MSIG6 == "0.245148", (MMU6, MSIG6)
# sec5 four pre-keys (machine-judged)
d1 = abs(wonly["mu"] - merged["mu"])
d2 = (merged["sigma"] - pre["sigma"]) / pre["sigma"] * 100
d3 = fam["full_sharpe_p95"] - w170["families"]["A_random_engine_exit"]["full_sharpe_p95"]
d4 = kl["line_delta_k_lift"]
assert d1 < 0.02 and abs(d2) < 10 and abs(d3) < 0.05 and abs(d4) <= 0.02, (d1, d2, d3, d4)
D1 = f"{d1:.4f}"
D2 = f"{d2:+.4f}%"
D3 = f"{d3:+.4f}"
D4 = f"{d4:+.4f}"
assert D1 == "0.0041" and D2 == "-0.0018%" and D3 == "+0.0246" and D4 == "+0.0000", (D1, D2, D3, D4)
# wave-drift key (W170 sec7 precedent face; machine-computed cross-file)
d5 = wonly["mu"] - w170["null_pool_cumulative"]["w170_only"]["mu"]
D5 = f"{d5:+.6f}"
assert D5 == "+0.003976", D5
# se_mu chain values machine-anchored
SE = f"{npc['se_mu_at_k374120']:.6f}"
assert SE == "0.000401", SE

S7_NEW = (
    "## \u00a77 \u8dd1\u540e\u5b9e\u8bc1\u3002\u3010finalize \u6536\u53e3\u673a\u68b0\u56de\u586b\u00b7bm-a r816 one-pass rc0\u00b712/12 \u5206\u7247\u6d88\u8d39\u2014\u2014\u56de\u586b\u5185\u5bb9=n1_w171_results.json \u51bb\u7ed3\u5b9e\u6d4b\u952e\u96f6\u6539\u5224\u636e\uff1b\u56de\u586b\u7a97\u6ce8\u8bb0\uff1ar816 finalize one-pass \u7a97\u672a\u542b\u672c\u56de\u586b\u00b7\u672c\u56de\u586b=r819 \u8865\u8d26\u7a97\u6536\u53e3\uff08W159/W168/W169 \u62d6\u5ef6\u7a97\u5148\u4f8b\u540c\u5f8b\u00b7\u5982\u5b9e\u6ce8\u8bb0\uff09\u3011\r\n"
    f"- **\u5408\u5e76\u6c60**\uff1apre-W171 K=371,920\uff08mu={PREMU6}\u00b7sigma={PRESIG6}\uff09\u2192 W171-only K=2,200\uff08mu={WMU6}\u00b7sigma={WSIG6}\uff09\u2192 **merged K=374,120\uff08mu={MMU6}\u00b7sigma={MSIG6}\uff09**\uff1b\u8d26\u672c prev=**779,412**+2,200=**781,612**\uff08voids_applied=LOWAMP-P1/P2\u00b7file=results/perpetual_faces/n1_w171_results.json\u00b7evidence_cutoff=2026-09-22\uff09\u3002\r\n"
    f"- **skill_line_v2 K-lift**\uff08n_eff \u6052\u7b49 779,412\uff09\uff1a1.1841 \u2192 **1.1841**\uff08\u0394=**+0.0000**\u00b7\u8bda\u5b9e\u5b9e\u6d4b\u6f02\u79fb vs \u00a75 \u63cf\u8ff0\u6027\u6295\u5f71\u9762\u00b7nulls-deepening \u7ebf\u96f6\u663e\u8457\u8d28\u53d8\uff09\uff1bse_mu \u6536\u7a84\u962f W169 0.000403 \u2192 W170 0.000402 \u2192 **{SE}**\uff08\u03c3{MSIG6}/\u221a374,120\u00b7results \u952e se_mu_at_k374120\uff09\u3002\r\n"
    f"- **A \u6863 full_sharpe_p95=0.3177**\uff082,000 runs\u00b7W170 \u952e 0.2931\u3010n1_w170_results.json \u673a\u8bfb\u3011\u2192\u5dee **{D3}**\u00b7<0.05 \u95e8\u8fc7\u00b7\u62bd\u6837\u6ce2\u52a8\u9762\u5982\u5b9e\u62ab\u9732\uff09\uff1bA p99=0.4489\u00b7A mu=-0.082494\u3002\r\n"
    f"- **\u00a75 \u56db\u9884\u952e\u5168\u8fc7\uff08\u673a\u8bc1\uff09**\uff1a\u2460|W171-only mu \u2212 merged mu|={D1}<0.02 \u2713\u2461sigma \u76f8\u5bf9\u53d8\u5316 {D2}<\u00b110% \u2713\u2462A p95 \u5dee {D3}<0.05 \u2713\u2463K-lift {D4}\u2264\u00b102 \u2713\u3002\r\n"
    "- **canon flip\uff1aNOT performed**\uff08K2,200 \u540c\u4f8b\u6cd5\u00b7\u6cbb\u7406\u63d0\u951a\u9762 only\u00b7\u7ed3\u679c\u5982\u5b9e\u6ce8\u8bb0\uff09\u3002\r\n"
    f"- \u5ba1\u8ba1\uff1a12 shards \u96f6\u91cd\u53e0\u8fde\u7eed\u8986\u76d6 A[0,2000)/B[0,200)\u00b7n_backtests \u5408\u8ba1 2,200\u00b7machine=bm-a\u00b7audit.finalize_only=true\u00b7\u6279\u5185\u6ce2\u95f4\u6f02\u79fb\u952e mu_delta_w171_vs_w170ext=**{D5}**\u3002\r\n"
)
S8_NEW = (
    "## \u00a78 \u6279\u540e\u590d\u76d8\u3002\u3010finalize \u540c\u7a97\u56de\u586b\u00b7bm-a r819 \u8865\u8d26\u7a97\u3011\r\n"
    "- **\u00a75.5 W172+ \u6295\u5f71\u627f\u63a5\uff08r818 probe \u673a\u8bc1\u00b7\u4e0b\u6ce2\u51bb\u7ed3\u65b9\u590d\u6838\u975e\u8f6c\u6284 r587 \u5f8b\uff09**\uff1aA first-clean **395_204..397_203**\uff08probe \u9884 hops=0\u2014\u2014**W172 B \u5e26 395_204..395_403 \u6ce8\u518c\u540e\u62d2\u7edd naive W173 A \u7a97**\u00b7W173 \u51bb\u7ed3\u65b9\u5fc5\u987b post-W172 \u6ce8\u518c\u5b87\u5b99\u91cd derive\u00b7\u9636\u68af A-hops-prior-B \u7ee7\u627f\u7b2c\u4e09\u5341\u4e8c\u4f8b\u5f85 W173 \u673a\u8bc1\uff09\uff1bB first-clean **395_404..395_603**\uff08naive B \u843d naive A \u7a97\u5185\u00b7\u540c\u7a97\u4e92\u65a5 leg2 \u5f8b=W173 \u51bb\u7ed3\u65b9 derive B \u65f6\u9884\u7559\u672c\u6ce2 A \u7a97\uff09\u3002W173 \u5e2d\u4f4d=\u4e0b\u8f6e seat \u94fe\uff08probe\u2192seat MSG\u2192\u51bb\u7ed3\u7a97\uff09\u3002\r\n"
    "- \u5b9d\u85cf/\u65b9\u6cd5\u8bba\u6355\u83b7\u95ee\uff08O-20261003-2030/O-20261002-2100 \u6536\u53e3\u6b65\uff09\uff1a\u672c\u6279=\u6d4b\u91cf\u52a0\u6df1\u9762\u00b7**\u96f6\u65b0\u65b9\u6cd5\u96f6\u65b0\u5b9d\u85cf**\uff08nulls-deepening \u4f8b\u6ce2\u00b7\u8bbe\u8ba1 verbatim \u590d\u7528\uff09\u00b7\u5982\u5b9e\u6ce8\u8bb0\u3002\r\n"
    "- \u8bda\u5b9e\u62ab\u9732\u9762\uff1ar816 finalize one-pass \u7a97\u672a\u542b \u00a77/\u00a78 \u673a\u68b0\u56de\u586b\uff08W171 finalize \u6536\u53e3\u7a97\u9057\u6f0f\uff09\u00b7\u672c \u00a77/\u00a78 \u56de\u586b=r819 \u8865\u8d26\u7a97\u6267\u884c\uff08W169 r812 finalize+r813 \u8865\u8d26\u5148\u4f8b\u540c\u5f8b\uff09\uff1b\u70e7\u5f55=\u5f15\u64ce tick \u81ea\u71c3\uff08\u51bb\u7ed3 commit 456f3affc 2026-10-07 09:29:05 \u540e tick \u81ea\u70b9\u706b\u00b7finalize d3e6c0ea0 09:41:03 one-pass \u6536\u53e3\u00b712 \u5206\u7247 12 \u5206\u949f\u7a97\u70e7\u5b8c\u00b7SATURATION_ENGINE \u5e38\u9a7b\u5f8b\u5b9e\u8bc1\uff09\u3002\r\n"
)

S7_OLD = (
    "## \u00a77 \u8dd1\u540e\u5b9e\u8bc1\u3002\u3010finalize \u6536\u53e3\u673a\u68b0\u56de\u586b\u00b7\u5f85 W171 finalize \u7a97\u3011\r\n"
    "- \uff08\u5360\u4f4d\u00b7finalize one-pass \u540e\u673a\u68b0\u56de\u586b\uff1a\u8d26\u672c\u6052\u7b49\u5f0f+\u5408\u5e76\u6c60 K+merged mu/w-only mu/mu_delta+sigma+se_mu+skill_line_v2 K-lift+A \u6863 p95+\u00a75 \u56db\u9884\u952e\u673a\u8bc1+canon flip \u6001+audit.finalize_only+voids_applied\u3002\uff09\r\n"
)
S8_OLD = (
    "## \u00a78 \u6279\u540e\u590d\u76d8\u3002\u3010finalize \u540c\u7a97\u56de\u586b\u00b7\u5f85 W171 finalize \u7a97\u3011\r\n"
    "- \uff08\u5360\u4f4d\u00b7\u00a75.5 W172+ \u6295\u5f71\u627f\u63a5+\u5b9d\u85cf/\u65b9\u6cd5\u8bba\u6355\u83b7\u95ee+\u8bda\u5b9e\u62ab\u9732\u9762\u00b7finalize \u6536\u53e3\u7a97\u673a\u68b0\u56de\u586b\u3002\uff09\r\n"
)

src = io.open(P, encoding="utf-8", newline="").read()
assert src.count("\r\n") >= 60, "on-disk CRLF convention expected"
for tag, old in (("sec7", S7_OLD), ("sec8", S8_OLD)):
    n = src.count(old)
    assert n == 1, f"{tag} placeholder count={n} expect=1"
out = src.replace(S7_OLD, S7_NEW).replace(S8_OLD, S8_NEW)
# post-edit integrity: placeholders gone, fresh faces present, no LF-mix
assert "占位·finalize one-pass" not in out and "占位·§5.5 W172+" not in out
assert "待 W171 finalize 窗" not in out, "stale pending-window face remains"
assert S7_NEW in out and S8_NEW in out
assert "n1_w171_results.json 冻结实测键零改判据" in out
assert "mu_delta_w171_vs_w170ext=**+0.003976**" in out
assert "781,612" in out and "374,120" in out and "0.000401" in out
bad = [mm.group() for mm in re.finditer(r"(\d{3})_(\d{3})\.\.(\d{3})_(\d{3})", out)
       if int(mm.group(3)) < int(mm.group(1))]
assert not bad, f"malformed windows: {bad[:4]}"
io.open(P, "w", encoding="utf-8", newline="").write(out)
chk = io.open(P, encoding="utf-8", newline="").read()
assert chk == out, "write roundtrip drift"
print(f"W171 sec7/sec8 backfill landed: {P} bytes={len(chk.encode('utf-8'))} "
      f"crlf={chk.count(chr(13)+chr(10))}")
print("sec5 four keys machine-judged: d1=%s d2=%s d3=%s d4=%s" % (D1, D2, D3, D4))
