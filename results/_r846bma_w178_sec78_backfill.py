# -*- coding: utf-8 -*-
"""r846 bm-a W178 prereg sec7/sec8 mechanical backfill (adoption closeout window:
r845 session landed freeze+ignition 22:08 then died pre-state-write; burn 12/12
landed 22:19; finalize one-pass this window -- r799/r819/r827 adoption precedent).
Zero-judgment-change backfill: every displayed value machine-derived from
results/perpetual_faces/n1_w178_results.json (+ n1_w177_results.json for prior
keys). r587 never-transcribe law; r773 malformed-window scan after edit; CRLF
on-disk convention preserved (r370 law)."""
import io, json, re

P = r"research\PERPETUAL_N1_W178_PREREG.md"
res = json.load(open(r"results/perpetual_faces/n1_w178_results.json", encoding="utf-8"))
w177 = json.load(open(r"results/perpetual_faces/n1_w177_results.json", encoding="utf-8"))
npc = res["null_pool_cumulative"]
pre, wonly, merged = npc["pre_w178_cumulative"], npc["w178_only"], npc["merged"]
led = res["science_gates"]["ledger"]
kl = res["skill_line_v2_k_lift"]
fam = res["families"]["A_random_engine_exit"]

# --- machine-derive every displayed face (r587) -------------------------------
assert pre["n_values"] == 387320 and wonly["n_values"] == 2200 \
    and merged["n_values"] == 389520, (pre["n_values"], wonly["n_values"], merged["n_values"])
assert led["prev_total"] == 795305 and led["batch_trials"] == 2200 and led["total"] == 797505, led
assert led["voids_applied"] == ["LOWAMP-P1", "LOWAMP-P2"], led
assert kl["line_pre_w178"] == 1.1848 and kl["line_merged_389520"] == 1.1849 \
    and kl["line_delta_k_lift"] == 0.0001 and kl["n_eff_held_equal"] == 795305, kl
assert kl["canon_flip"].startswith("NOT performed"), kl
assert abs(npc["se_mu_at_k389520"] - 0.000393) < 5e-8, npc["se_mu_at_k389520"]
assert abs(npc["mu_delta_w178_vs_w177ext"] - 0.001369) < 5e-8, npc["mu_delta_w178_vs_w177ext"]
assert fam["n"] == 2000 and fam["full_sharpe_p95"] == 0.3275 \
    and fam["full_sharpe_p99"] == 0.4674, fam
assert res["audit"] == {"machine": "bm-a", "finalize_only": True}, res["audit"]
assert len(res["shards_consumed"]) == 12, res["shards_consumed"]
assert res["evidence_cutoff"] == "2026-09-22", res["evidence_cutoff"]
w177fam = w177["families"]["A_random_engine_exit"]
assert w177fam["full_sharpe_p95"] == 0.3116, w177fam
w177kl = w177["skill_line_v2_k_lift"]
assert w177kl["line_delta_k_lift"] == 0.0001 and w177kl["line_pre_w177"] == 1.1846, w177kl

PREMU6 = f"{pre['mu']:.6f}"          # -0.092732
PRESIG6 = f"{pre['sigma']:.6f}"      # 0.245080
WMU6 = f"{wonly['mu']:.6f}"          # -0.092253
WSIG6 = f"{wonly['sigma']:.6f}"      # 0.249435
MMU6 = f"{merged['mu']:.6f}"         # -0.092730
MSIG6 = f"{merged['sigma']:.6f}"     # 0.245104
assert PREMU6 == "-0.092732" and PRESIG6 == "0.245080", (PREMU6, PRESIG6)
assert WMU6 == "-0.092253" and WSIG6 == "0.249435", (WMU6, WSIG6)
assert MMU6 == "-0.092730" and MSIG6 == "0.245104", (MMU6, MSIG6)

# --- sec5 four pred keys machine-verdict ---------------------------------------
d1 = abs(wonly["mu"] - merged["mu"])                    # mu gap
d2 = (merged["sigma"] - w177["null_pool_cumulative"]["merged"]["sigma"]) / w177["null_pool_cumulative"]["merged"]["sigma"]
d3 = fam["full_sharpe_p95"] - w177fam["full_sharpe_p95"]  # A p95 delta vs W177 anchor
d4 = kl["line_delta_k_lift"]
assert d1 < 0.02, d1
assert abs(d2) < 0.10, d2
assert abs(d3) < 0.05, d3
assert abs(d4) <= 0.02, d4
assert abs(fam["full_sharpe_mu"] - (-0.08865)) < 1e-9, fam

raw = open(P, encoding="utf-8", newline="").read()
crlf = raw.count("\r\n")
src = raw.replace("\r\n", "\n")  # match on LF-normalized view (r370 CRLF law: write back CRLF)

old7 = "## §7 跑后实证。【finalize 收口机械回填·待 W178 finalize 窗】\n- （占位·finalize one-pass 后机械回填：账本恒等式+合并池 K+merged mu/w-only mu/mu_delta+sigma+se_mu+skill_line_v2 K-lift+A 档 p95+§5 四预键机证+canon flip 态+audit.finalize_only+voids_applied。）"
new7 = """## §7 跑后实证。【finalize 收口机械回填·r846 窗机证】
- 账本恒等式：795,305 + 2,200 = **797,505** EXACT（§5 投影精确命中·prev_total/batch_trials/total 三键机读）。
- 合并池：**K=389,520** EXACT（=W177 池 387,320 + 本波 2,200·§5 投影命中）。
- merged mu **−0.092730**（6 位机读 -0.092730）/ w-only mu **−0.092253** / mu_delta(w178 vs w177ext) **+0.001369**。
- merged sigma **0.245104**（W177 键 0.245080→0.245104）；w-only sigma 0.249435；se_mu@K389,520 **0.000393**（W177 0.000394→0.000393 收窄）。
- skill_line_v2：line_pre **1.1848** → line_merged@K389,520 **1.1849**（K-lift **+0.0001**·n_eff_held_equal 795,305）；canon flip **NOT performed**（K2,200 同例法·治理提案面）。
- A 档 full_sharpe_p95 **0.3275**（W177 锚 0.3116·Δ+0.0159<0.05 门过）·p99 0.4674·A mu −0.08865。
- §5 四预键机证全过：①mu gap |−0.092253−(−0.092730)|=0.000477<0.02 PASS ②sigma 相对变化 +0.01%<±10% PASS ③A p95 Δ+0.0159<0.05 PASS ④K-lift +0.0001≤±0.02 PASS。
- audit.finalize_only=**true**（bm-a）·voids_applied=LOWAMP-P1/P2·evidence_cutoff=2026-09-22 在位·shards_consumed 12/12。"""

old8 = "## §8 批后复盘。【finalize 同窗回填·待 W178 finalize 窗】\n- （占位·§5.5 W179+ 投影承接+宝藏/方法论捕获问+诚实披露面·finalize 收口窗机械回填。）"
new8 = """## §8 批后复盘。【finalize 同窗回填·r846 窗】
- §5.5 W179+ 投影承接（probe 机证·W179 冻结方重 derive 强制非转抄 r587 律）：A first-clean **408_404..410_403**（hops=0）/ B first-clean **408_604..408_803**（hops=0）——naive B 落 naive A 窗内（W141 同窗互斥·leg2 律/E36 卡适用 W179 冻结方）；W178 B 带 408_404..408_603 注册后将拒 naive W179 A 窗=阶梯 A-hops-prior-B 第三十九例继承。
- 宝藏/方法论捕获问：本批无新方法零新宝藏（dead-r845 接管收口窗·finalize 三亽+半开区间 preflight=r839 血统既有律 verbatim 复用·r831 旧脚本含端点读法对半开 shard 生成假红=当场按 r839 半开律治愈·非新方法论）；TREASURE/METHODOLOGY 零 append。
- 诚实披露面：r845 会话 22:08 冻结+点火后斩首未写 state（本窗 r846 接管收口·零重复烧·shards 12/12 全在）；W178-only mu −0.0923 比合并池 −0.0927 略浅=null 抽样正常波动非异常；K-lift 线 1.1848→1.1849 连续 177 波 nulls-deepening 线如实在册。"""

assert old7 in src, "SS7 PLACEHOLDER NOT FOUND"
assert old8 in src, "SS8 PLACEHOLDER NOT FOUND"
out = src.replace(old7, new7).replace(old8, new8).replace("\n", "\r\n")
with io.open(P, "w", encoding="utf-8", newline="") as f:
    f.write(out)

# --- r773 malformed-window scan: no leftover placeholder spans ----------------
after = open(P, encoding="utf-8", newline="").read().replace("\r\n", "\n")
assert "占位·finalize one-pass 后机械回填" not in after, "SS7 residue"
assert "占位·§5.5 W179+ 投影承接" not in after, "SS8 residue"
assert after.count("§7 跑后实证") == 1 and after.count("§8 批后复盘") == 1
raw_after = open(P, encoding="utf-8", newline="").read()
print("BACKFILL OK; CRLF before=%d after=%d; four pred keys d1=%.6f d2=%.5f%% d3=%.4f d4=+0.0001" % (
    crlf, raw_after.count("\r\n"), d1, d2 * 100, d3))
