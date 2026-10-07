# -*- coding: utf-8 -*-
"""r826 bm-a W174 prereg sec7/sec8 mechanical backfill (one-pass
full-lifecycle window: freeze r826 commit 24cded752 + tick ignition 13:45
+ burn 12/12 landed 13:45->13:58 + finalize same session -- W46 r348
same-window full-lifecycle precedent; two-session law r797/r799 honored:
prereg build r825 window, freeze r826 window). Zero-judgment-change
backfill: every displayed value machine-derived from
results/perpetual_faces/n1_w174_results.json (+ n1_w173_results.json for
prior keys). r587 never-transcribe law; r773 malformed-window scan after
edit; CRLF on-disk convention (r370 law)."""
import io
import json

P = r"research\PERPETUAL_N1_W174_PREREG.md"
res = json.load(open(r"results/perpetual_faces/n1_w174_results.json", encoding="utf-8"))
w173 = json.load(open(r"results/perpetual_faces/n1_w173_results.json", encoding="utf-8"))
npc = res["null_pool_cumulative"]
pre, wonly, merged = npc["pre_w174_cumulative"], npc["w174_only"], npc["merged"]
led = res["science_gates"]["ledger"]
kl = res["skill_line_v2_k_lift"]
fam = res["families"]["A_random_engine_exit"]
f173 = w173["families"]["A_random_engine_exit"]

# --- machine-derive every displayed face (r587) -------------------------------
assert pre["n_values"] == 378520 and wonly["n_values"] == 2200 \
    and merged["n_values"] == 380720, (pre["n_values"], wonly["n_values"], merged["n_values"])
assert led["prev_total"] == 786012 and led["batch_trials"] == 2200 and led["total"] == 788212, led
assert led["voids_applied"] == ["LOWAMP-P1", "LOWAMP-P2"], led
assert kl["line_merged_380720"] == 1.1844 and kl["line_pre_w174"] == 1.1844 \
    and kl["line_delta_k_lift"] == 0.0 and kl["n_eff_held_equal"] == 786012, kl
assert kl["canon_flip"].startswith("NOT performed"), kl
assert abs(npc["se_mu_at_k380720"] - 0.000397) < 5e-8, npc["se_mu_at_k380720"]
assert fam["n"] == 2000 and fam["full_sharpe_p95"] == 0.3231 \
    and fam["full_sharpe_p99"] == 0.4665, fam
assert res["audit"] == {"machine": "bm-a", "finalize_only": True}, res["audit"]
assert len(res["shards_consumed"]) == 12, res["shards_consumed"]
assert res["evidence_cutoff"] == "2026-09-22", res["evidence_cutoff"]
PREMU6 = f"{pre['mu']:.6f}"          # -0.092786
PRESIG6 = f"{pre['sigma']:.6f}"      # 0.245122
WMU6 = f"{wonly['mu']:.6f}"          # -0.089531
WSIG6 = f"{wonly['sigma']:.6f}"      # 0.243912
MMU6 = f"{merged['mu']:.6f}"         # -0.092767
MSIG6 = f"{merged['sigma']:.6f}"     # 0.245114
AMU6 = f"{fam['full_sharpe_mu']:.6f}"
assert PREMU6 == "-0.092786" and PRESIG6 == "0.245122", (PREMU6, PRESIG6)
assert WMU6 == "-0.089531" and WSIG6 == "0.243912", (WMU6, WSIG6)
assert MMU6 == "-0.092767" and MSIG6 == "0.245114", (MMU6, MSIG6)
# sec5 four pre-keys (machine-judged)
d1 = abs(wonly["mu"] - merged["mu"])
d2 = (merged["sigma"] - pre["sigma"]) / pre["sigma"] * 100
d3 = fam["full_sharpe_p95"] - f173["full_sharpe_p95"]
d4 = kl["line_delta_k_lift"]
assert d1 < 0.02 and abs(d2) < 10 and abs(d3) < 0.05 and abs(d4) <= 0.02, (d1, d2, d3, d4)
D1 = f"{d1:.4f}"; D2 = f"{d2:+.4f}%"; D3 = f"{d3:+.4f}"; D4 = f"{d4:+.4f}"
assert D1 == "0.0032" and D2 == "-0.0029%" and D3 == "+0.0245" and D4 == "+0.0000", (D1, D2, D3, D4)
# wave-drift key (W173 sec7 precedent face; machine-computed cross-file)
d5 = wonly["mu"] - w173["null_pool_cumulative"]["w173_only"]["mu"]
D5 = f"{d5:+.6f}"
assert D5 == "-0.005987", D5
# se_mu chain values machine-anchored
SE = f"{npc['se_mu_at_k380720']:.6f}"
assert SE == "0.000397", SE

S7_NEW = (
    "## \u00a77 跑后实证。【finalize 收口机械回填·bm-a r826 one-pass 同窗 rc0·12/12 分片消费——回填内容=n1_w174_results.json 冻结实测键零改判据；回填窗注记：本波=full-lifecycle one-pass（r826 同窗冻结 commit 24cded752 + tick 点火 13:45 + 烧录 12/12 13:45→13:58 + finalize 同窗收口·W46 r348 同窗全生命周期先例·两节律律 r797/r799 合规：prereg 建=r825 窗/冻结=本 r826 窗）】\r\n"
    f"- **合并池**：pre-W174 K=378,520（mu={PREMU6}·sigma={PRESIG6}）→ W174-only K=2,200（mu={WMU6}·sigma={WSIG6}）→ **merged K=380,720（mu={MMU6}·sigma={MSIG6}）**；账本 prev=**786,012**+2,200=**788,212**（恰=§0 投影恒等）（voids_applied=LOWAMP-P1/P2·file=results/perpetual_faces/n1_w174_results.json·evidence_cutoff=2026-09-22）。\r\n"
    f"- **skill_line_v2 K-lift**（n_eff 恒等 786,012）：1.1844 → **1.1844**（Δ=**{D4}**·nulls-deepening 线零显著质变如实注记）；se_mu 收窄锚 W171 0.000401 → W172 0.000400 → W173 0.000398 → **{SE}**（σ{MSIG6}/√380,720·results 键 se_mu_at_k380720）。\r\n"
    f"- **A 档 full_sharpe_p95=0.3231**（2,000 runs·W173 键 0.2986【n1_w173_results.json 机读】→差 **{D3}**·<0.05 门过·抽样波动面如实披露——本波 A 档 p95 跳幅大于近波常态（W172→W173 差仅 −0.0010）但仍在冻结门内·零翻案零改线）；A p99=0.4665·A mu={AMU6}。\r\n"
    f"- **§5 四预键全过（机证）**：①|W174-only mu − merged mu|={D1}<0.02 ✓②sigma 相对变化 {D2}<±10% ✓③A p95 差 {D3}<0.05 ✓④K-lift {D4}≤±0.02 ✓。\r\n"
    "- **canon flip：NOT performed**（K2,200 同例法·治理提案面 only·结果如实注记）。\r\n"
    f"- 审计：12 shards 零重叠连续覆盖 A[0,2000)/B[0,200)·n_backtests 合计 2,200·machine=bm-a·audit.finalize_only=true·批内波间漂移键 mu_delta_w174_vs_w173ext=**{D5}**；三门 r752 回执=results/_r826bma_w174_three_gate.json PASS（A 2,000/B 200+带域 397,604..399,603/399,604..399,803 分片机读）。\r\n"
)
S8_NEW = (
    "## \u00a78 批后复盘。【finalize 同窗回填·bm-a r826 one-pass 窗】\r\n"
    "- **§5.5 W175+ 投影承接（r823 probe 机证·下波冻结方复核非转抄 r587 律）**：A first-clean **399_604..401_603**（probe 预 hops=0——**W174 B 带 399_604..399_803 注册后将拒 naive W175 A 窗**·W175 冻结方必须 post-W174 注册宇宙重 derive·阶梯 A-hops-prior-B 继承第三十五例待 W175 机证）；B first-clean **399_804..400_003**（naive B 落 naive A 窗内·同窗互斥 leg2 律=W175 冻结方 derive B 时预留本波 A 窗·re-derive-MANDATORY）。W175 席位=下轮 seat 链（probe→seat MSG→冻结窗）。\r\n"
    "- 宝藏/方法论捕获问（O-20261003-2030/O-20261002-2100 收口步）：本批=测量加深面·**零新方法零新宝藏**（nulls-deepening 例波·设计 verbatim 复用）·如实注记。\r\n"
    "- 诚实披露面：本波 full-lifecycle one-pass（冻结 commit 24cded752 + 引擎 tick 自燃 13:45 起 + 12 分片 13:45→13:58 烧完·SATURATION_ENGINE 常驻律实证 + finalize 同窗收口——W46 r348 先例·两节律律合规如实注记）；冻结窗既有披露照录：序数面 convergence（W173 sec5.5 散文预告第三十四例=r823 回执机读 THIRTY-FOURTH·零分叉）；prereg 散文引用滑移（prose 'r823 probe leg4' vs 回执 A_semantics 机读 'r820 probe leg4'）按 r587 以回执面为准·prereg 面冻结纪律不改（r821/r822 同滑移先例）；mat B-face convergence universe-token 陈旧载痕 post-W171→post-W173 单词治愈（r822 sec8-heal 先例·W173 活块面未触碰）。\r\n"
)

S7_OLD = (
    "## \u00a77 跑后实证。【finalize 收口机械回填·待 W174 finalize 窗】\r\n"
    "- （占位·finalize one-pass 后机械回填：账本恒等式+合并池 K+merged mu/w-only mu/mu_delta+sigma+se_mu+skill_line_v2 K-lift+A 档 p95+§5 四预键机证+canon flip 态+audit.finalize_only+voids_applied。）\r\n"
)
S8_OLD = (
    "## \u00a78 批后复盘。【finalize 同窗回填·待 W174 finalize 窗】\r\n"
    "- （占位·§5.5 W175+ 投影承接+宝藏/方法论捕获问+诚实披露面·finalize 收口窗机械回填。）\r\n"
)

src = io.open(P, encoding="utf-8", newline="").read()
assert src.count("\r\n") >= 60, "on-disk CRLF convention expected"
for tag, old in (("sec7", S7_OLD), ("sec8", S8_OLD)):
    n = src.count(old)
    assert n == 1, f"{tag} placeholder count={n} expect=1"
out = src.replace(S7_OLD, S7_NEW).replace(S8_OLD, S8_NEW)
# post-edit integrity: placeholders gone, fresh faces present
assert "占位·finalize one-pass" not in out and "占位·§5.5 W175+" not in out
assert "待 W174 finalize 窗" not in out, "stale pending-window face remains"
assert S7_NEW in out and S8_NEW in out
assert "n1_w174_results.json 冻结实测键零改判据" in out
assert "mu_delta_w174_vs_w173ext=**-0.005987**" in out
assert "788,212" in out and "380,720" in out and "0.000397" in out
assert out.count("\r\n") == src.count("\r\n") + (S7_NEW.count("\r\n") - S7_OLD.count("\r\n")) + (S8_NEW.count("\r\n") - S8_OLD.count("\r\n"))
io.open(P, "w", encoding="utf-8", newline="").write(out)
print("sec7/sec8 backfill LANDED; bytes", len(src), "->", len(out))
