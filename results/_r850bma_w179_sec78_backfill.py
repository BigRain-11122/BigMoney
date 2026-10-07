# -*- coding: utf-8 -*-
"""r850 bm-a W179 prereg sec7/sec8 mechanical backfill (finalize one-pass this window).
Zero-judgment-change backfill: every displayed value machine-derived from
results/perpetual_faces/n1_w179_results.json (+ n1_w178_results.json for prior anchors).
r587 never-transcribe law; r773 malformed-window scan after edit; CRLF on-disk
convention preserved (r370 law). Bloodline: _r846bma_w178_sec78_backfill.py."""
import io, json

P = r"research\PERPETUAL_N1_W179_PREREG.md"
res = json.load(open(r"results/perpetual_faces/n1_w179_results.json", encoding="utf-8"))
w178 = json.load(open(r"results/perpetual_faces/n1_w178_results.json", encoding="utf-8"))
npc = res["null_pool_cumulative"]
pre, wonly, merged = npc["pre_w179_cumulative"], npc["w179_only"], npc["merged"]
led = res["science_gates"]["ledger"]
kl = res["skill_line_v2_k_lift"]
fam = res["families"]["A_random_engine_exit"]

# --- machine-derive every displayed face (r587) -------------------------------
assert pre["n_values"] == 389520 and wonly["n_values"] == 2200 \
    and merged["n_values"] == 391720, (pre["n_values"], wonly["n_values"], merged["n_values"])
assert led["prev_total"] == 797505 and led["batch_trials"] == 2200 and led["total"] == 799705, led
assert led["voids_applied"] == ["LOWAMP-P1", "LOWAMP-P2"], led
assert kl["line_pre_w179"] == 1.1851 and kl["line_merged_391720"] == 1.185 \
    and kl["line_delta_k_lift"] == -0.0001 and kl["n_eff_held_equal"] == 797505, kl
assert kl["canon_flip"].startswith("NOT performed"), kl
assert abs(npc["se_mu_at_k391720"] - 0.000392) < 5e-9, npc["se_mu_at_k391720"]
assert abs(npc["mu_delta_w179_vs_w178ext"] - (-0.000971)) < 5e-8, npc["mu_delta_w179_vs_w178ext"]
assert fam["n"] == 2000 and fam["full_sharpe_p95"] == 0.3265 \
    and fam["full_sharpe_p99"] == 0.4552, fam
assert abs(fam["full_sharpe_mu"] - (-0.087915)) < 1e-9, fam
assert res["audit"] == {"machine": "bm-a", "finalize_only": True}, res["audit"]
assert len(res["shards_consumed"]) == 12, res["shards_consumed"]
assert res["evidence_cutoff"] == "2026-09-22", res["evidence_cutoff"]
w178fam = w178["families"]["A_random_engine_exit"]
assert w178fam["full_sharpe_p95"] == 0.3275, w178fam
w178npc = w178["null_pool_cumulative"]["merged"]
assert w178npc["n_values"] == 389520 and round(w178npc["sigma"], 6) == 0.245104, w178npc

PREMU6 = f"{pre['mu']:.6f}"          # -0.092730
PRESIG6 = f"{pre['sigma']:.6f}"      # 0.245104
WMU6 = f"{wonly['mu']:.6f}"          # -0.093224
WSIG6 = f"{wonly['sigma']:.6f}"      # 0.241922
MMU6 = f"{merged['mu']:.6f}"         # -0.092733
MSIG6 = f"{merged['sigma']:.6f}"     # 0.245086
assert PREMU6 == "-0.092730" and PRESIG6 == "0.245104", (PREMU6, PRESIG6)
assert WMU6 == "-0.093224" and WSIG6 == "0.241922", (WMU6, WSIG6)
assert MMU6 == "-0.092733" and MSIG6 == "0.245086", (MMU6, MSIG6)

# --- sec5 four pred keys machine-verdict ---------------------------------------
d1 = abs(wonly["mu"] - merged["mu"])                       # mu gap
d2 = (merged["sigma"] - w178npc["sigma"]) / w178npc["sigma"]
d3 = fam["full_sharpe_p95"] - w178fam["full_sharpe_p95"]   # A p95 delta vs W178 anchor
d4 = kl["line_delta_k_lift"]
assert d1 < 0.02, d1
assert abs(d2) < 0.10, d2
assert abs(d3) < 0.05, d3
assert abs(d4) <= 0.02, d4

raw = open(P, encoding="utf-8", newline="").read()
crlf = raw.count("\r\n")
src = raw.replace("\r\n", "\n")  # match on LF-normalized view (r370 CRLF law: write back CRLF)

old7 = "## §7 跑后实证。【finalize 收口机械回填·待 W179 finalize 窗】\n- （占位·finalize one-pass 后机械回填：账本恒等式+合并池 K+merged mu/w-only mu/mu_delta+sigma+se_mu+skill_line_v2 K-lift+A 档 p95+§5 四预键机证+canon flip 态+audit.finalize_only+voids_applied。）"
new7 = """## §7 跑后实证。【finalize 收口机械回填·r850 窗机证】
- 账本恒等式：797,505 + 2,200 = **799,705** EXACT（§5 投影精确命中·prev_total/batch_trials/total 三键机读）。
- 合并池：**K=391,720** EXACT（=W178 池 389,520 + 本波 2,200·§5 投影命中）。
- merged mu **−0.092733**（6 位机读 -0.092733）/ w-only mu **−0.093224** / mu_delta(w179 vs w178ext) **−0.000971**。
- merged sigma **0.245086**（W178 键 0.245104→0.245086）；w-only sigma 0.241922；se_mu@K391,720 **0.000392**（W178 0.000393→0.000392 收窄）。
- skill_line_v2：line_pre **1.1851** → line_merged@K391,720 **1.1850**（K-lift **−0.0001**·n_eff_held_equal 797,505）；canon flip **NOT performed**（K2,200 同例法·治理提案面）。
- A 档 full_sharpe_p95 **0.3265**（W178 锚 0.3275·Δ−0.0010<0.05 门过）·p99 0.4552·A mu −0.087915。
- §5 四预键机证全过：①mu gap |−0.093224−(−0.092733)|=0.000491<0.02 PASS ②sigma 相对变化 −0.0073%<±10% PASS ③A p95 Δ−0.0010<0.05 PASS ④K-lift −0.0001≤±0.02 PASS。
- audit.finalize_only=**true**（bm-a）·voids_applied=LOWAMP-P1/P2·evidence_cutoff=2026-09-22 在位·shards_consumed 12/12。"""

old8 = "## §8 批后复盘。【finalize 同窗回填·待 W179 finalize 窗】\n- （占位·§5.5 W180+ 投影承接+宝藏/方法论捕获问+诚实披露面·finalize 收口窗机械回填。）"
new8 = """## §8 批后复盘。【finalize 同窗回填·r850 窗】
- §5.5 W180+ 投影承接（r848 seat probe 回执机证·W180 冻结方重 derive 强制非转抄 r587 律）：naive A **410_604..412_603**（将被注册 W179 B 带 410_604..410_803 于 own start 拒=阶梯 A-hops-prior-B 第四十例预期）/ naive B **410_804..411_003**（落 naive A 窗内·W141 同窗互斥 leg2 律→B 保留走须越过本波 A 尾）——W180 冻结窗须在 post-W179 注册宇宙重 derive。
- 宝藏/方法论捕获问：本批无新方法零新宝藏（finalize one-pass+半开区间 preflight=r839/r846 血统既有律 verbatim 复用·preflight 脚本 W178→W179 带值适配=构造性参数替换非新方法论）；TREASURE/METHODOLOGY 零 append。
- 诚实披露面：r849 会话死尾 staged 收养+本窗 17-UU rebase 停窗正典解（merge_lane_views resolve×6+twins 深扫 ts×6+CODELY origin+r849 追加+snapshot 取新×4）零丢失；W179-only mu −0.0932 比合并池 −0.0927 略深=null 抽样正常波动非异常；K-lift **−0.0001**（W177/W178 两连 +0.0001 后首负·线 1.1851→1.1850）如实在册。"""

assert old7 in src, "SS7 PLACEHOLDER NOT FOUND"
assert old8 in src, "SS8 PLACEHOLDER NOT FOUND"
out = src.replace(old7, new7).replace(old8, new8).replace("\n", "\r\n")
with io.open(P, "w", encoding="utf-8", newline="") as f:
    f.write(out)

# --- r773 malformed-window scan: no leftover placeholder spans ----------------
after = open(P, encoding="utf-8", newline="").read().replace("\r\n", "\n")
assert "占位·finalize one-pass 后机械回填" not in after, "SS7 residue"
assert "占位·§5.5 W180+ 投影承接" not in after, "SS8 residue"
assert after.count("§7 跑后实证") == 1 and after.count("§8 批后复盘") == 1
raw_after = open(P, encoding="utf-8", newline="").read()
print("BACKFILL OK; CRLF before=%d after=%d; four pred keys d1=%.6f d2=%.5f%% d3=%.4f d4=%+.4f" % (
    crlf, raw_after.count("\r\n"), d1, d2 * 100, d3, d4))
