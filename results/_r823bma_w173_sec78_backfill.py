# -*- coding: utf-8 -*-
"""r823 bm-a W173 prereg sec7/sec8 mechanical backfill (adoption closeout
window: r822 main session beheaded post-freeze+ignition pre-S7; burn 12/12
landed 12:03:18..12:13:17; finalize one-pass this window -- r799/r819
adoption precedent). Zero-judgment-change backfill: every displayed value
machine-derived from results/perpetual_faces/n1_w173_results.json
(+ n1_w172_results.json for prior keys). r587 never-transcribe law;
r773 malformed-window scan after edit; CRLF on-disk convention (r370 law)."""
import io
import json

P = r"research\PERPETUAL_N1_W173_PREREG.md"
res = json.load(open(r"results/perpetual_faces/n1_w173_results.json", encoding="utf-8"))
w172 = json.load(open(r"results/perpetual_faces/n1_w172_results.json", encoding="utf-8"))
npc = res["null_pool_cumulative"]
pre, wonly, merged = npc["pre_w173_cumulative"], npc["w173_only"], npc["merged"]
led = res["science_gates"]["ledger"]
kl = res["skill_line_v2_k_lift"]
fam = res["families"]["A_random_engine_exit"]
f172 = w172["families"]["A_random_engine_exit"]

# --- machine-derive every displayed face (r587) -------------------------------
assert pre["n_values"] == 376320 and wonly["n_values"] == 2200 \
    and merged["n_values"] == 378520, (pre["n_values"], wonly["n_values"], merged["n_values"])
assert led["prev_total"] == 783812 and led["batch_trials"] == 2200 and led["total"] == 786012, led
assert led["voids_applied"] == ["LOWAMP-P1", "LOWAMP-P2"], led
assert kl["line_merged_378520"] == 1.1843 and kl["line_pre_w173"] == 1.1843 \
    and kl["line_delta_k_lift"] == 0.0 and kl["n_eff_held_equal"] == 783812, kl
assert kl["canon_flip"].startswith("NOT performed"), kl
assert abs(npc["se_mu_at_k378520"] - 0.000398) < 5e-8, npc["se_mu_at_k378520"]
assert fam["n"] == 2000 and fam["full_sharpe_p95"] == 0.2986 \
    and fam["full_sharpe_p99"] == 0.4463, fam
assert res["audit"] == {"machine": "bm-a", "finalize_only": True}, res["audit"]
assert len(res["shards_consumed"]) == 12, res["shards_consumed"]
assert res["evidence_cutoff"] == "2026-09-22", res["evidence_cutoff"]
PREMU6 = f"{pre['mu']:.6f}"          # -0.092840
PRESIG6 = f"{pre['sigma']:.6f}"      # 0.245136
WMU6 = f"{wonly['mu']:.6f}"          # -0.083544
WSIG6 = f"{wonly['sigma']:.6f}"      # 0.242569
MMU6 = f"{merged['mu']:.6f}"         # -0.092786
MSIG6 = f"{merged['sigma']:.6f}"      # 0.245122
AMU6 = f"{fam['full_sharpe_mu']:.6f}"
assert PREMU6 == "-0.092840" and PRESIG6 == "0.245136", (PREMU6, PRESIG6)
assert WMU6 == "-0.083544" and WSIG6 == "0.242569", (WMU6, WSIG6)
assert MMU6 == "-0.092786" and MSIG6 == "0.245122", (MMU6, MSIG6)
# sec5 four pre-keys (machine-judged)
d1 = abs(wonly["mu"] - merged["mu"])
d2 = (merged["sigma"] - pre["sigma"]) / pre["sigma"] * 100
d3 = fam["full_sharpe_p95"] - f172["full_sharpe_p95"]
d4 = kl["line_delta_k_lift"]
assert d1 < 0.02 and abs(d2) < 10 and abs(d3) < 0.05 and abs(d4) <= 0.02, (d1, d2, d3, d4)
D1 = f"{d1:.4f}"; D2 = f"{d2:+.4f}%"; D3 = f"{d3:+.4f}"; D4 = f"{d4:+.4f}"
assert D1 == "0.0092" and D2 == "-0.0058%" and D3 == "-0.0010" and D4 == "+0.0000", (D1, D2, D3, D4)
# wave-drift key (W172 sec7 precedent face; machine-computed cross-file)
d5 = wonly["mu"] - w172["null_pool_cumulative"]["w172_only"]["mu"]
D5 = f"{d5:+.6f}"
assert D5 == "+0.012103", D5
# se_mu chain values machine-anchored
SE = f"{npc['se_mu_at_k378520']:.6f}"
assert SE == "0.000398", SE

S7_NEW = (
    "## \u00a77 跑后实证。【finalize 收口机械回填·bm-a r823 接管收口窗 one-pass rc0·12/12 分片消费——回填内容=n1_w173_results.json 冻结实测键零改判据；回填窗注记：r822 主体窗冻结 commit 04e95748a + tick 点火后被斩首于 S7 前（r799/r819 收养先例同律）·本回填=接管收口窗执行·如实注记】\r\n"
    f"- **合并池**：pre-W173 K=376,320（mu={PREMU6}·sigma={PRESIG6}）→ W173-only K=2,200（mu={WMU6}·sigma={WSIG6}）→ **merged K=378,520（mu={MMU6}·sigma={MSIG6}）**；账本 prev=**783,812**+2,200=**786,012**（恰=§5 投影恒等）（voids_applied=LOWAMP-P1/P2·file=results/perpetual_faces/n1_w173_results.json·evidence_cutoff=2026-09-22）。\r\n"
    f"- **skill_line_v2 K-lift**（n_eff 恒等 783,812）：1.1843 → **1.1843**（Δ=**{D4}**·nulls-deepening 线零显著质变如实注记）；se_mu 收窄锚 W170 0.000402 → W171 0.000401 → W172 0.000400 → **{SE}**（σ{MSIG6}/√378,520·results 键 se_mu_at_k378520）。\r\n"
    f"- **A 档 full_sharpe_p95=0.2986**（2,000 runs·W172 键 0.2996【n1_w172_results.json 机读】→差 **{D3}**·<0.05 门过·抽样波动面如实披露）；A p99=0.4463·A mu={AMU6}。\r\n"
    f"- **§5 四预键全过（机证）**：①|W173-only mu − merged mu|={D1}<0.02 ✓②sigma 相对变化 {D2}<±10% ✓③A p95 差 {D3}<0.05 ✓④K-lift {D4}≤±0.02 ✓。\r\n"
    "- **canon flip：NOT performed**（K2,200 同例法·治理提案面 only·结果如实注记）。\r\n"
    f"- 审计：12 shards 零重叠连续覆盖 A[0,2000)/B[0,200)·n_backtests 合计 2,200·machine=bm-a·audit.finalize_only=true·批内波间漂移键 mu_delta_w173_vs_w172ext=**{D5}**。\r\n"
)
S8_NEW = (
    "## \u00a78 批后复盘。【finalize 同窗回填·bm-a r823 接管收口窗】\r\n"
    "- **§5.5 W174+ 投影承接（r820 probe 机证·下波冻结方复核非转抄 r587 律）**：A first-clean **397_404..399_403**（probe 预 hops=0——**W173 B 带 397_404..397_603 注册后将拒 naive W174 A 窗**·W174 冻结方必须 post-W173 注册宇宙重 derive·阶梯 A-hops-prior-B 继承第三十四例待 W174 机证）；B first-clean **397_604..397_803**（naive B 落 naive A 窗内·同窗互斥 leg2 律=W174 冻结方 derive B 时预留本波 A 窗·re-derive-MANDATORY）。W174 席位=下轮 seat 链（probe→seat MSG→冻结窗）。\r\n"
    "- 宝藏/方法论捕获问（O-20261003-2030/O-20261002-2100 收口步）：本批=测量加深面·**零新方法零新宝藏**（nulls-deepening 例波·设计 verbatim 复用）·如实注记。\r\n"
    "- 诚实披露面：r822 主体窗冻结 commit 04e95748a（2026-10-07 ~11:4x）+ tick 点火后被斩首于 S7 前（烧录=引擎 tick 自燃·12 分片 12:03:18→12:13:17 窗烧完·SATURATION_ENGINE 常驻律实证·state/心跳/轮报零 closeout=斩首实证）；finalize one-pass + 本回填 = r823 接管收口窗执行。冻结窗既有披露照录：序数面按回执机读 THIRTY-THIRD 承载（r587）；prereg 散文引用滑移（prose 'r820 probe leg4' vs 回执 A_semantics 机读 'r818 probe leg4'）按 r587 以回执面为准·prereg 面冻结纪律不改。\r\n"
)

S7_OLD = (
    "## \u00a77 跑后实证。【finalize 收口机械回填·待 W173 finalize 窗】\r\n"
    "- （占位·finalize one-pass 后机械回填：账本恒等式+合并池 K+merged mu/w-only mu/mu_delta+sigma+se_mu+skill_line_v2 K-lift+A 档 p95+§5 四预键机证+canon flip 态+audit.finalize_only+voids_applied。）\r\n"
)
S8_OLD = (
    "## \u00a78 批后复盘。【finalize 同窗回填·待 W173 finalize 窗】\r\n"
    "- （占位·§5.5 W174+ 投影承接+宝藏/方法论捕获问+诚实披露面·finalize 收口窗机械回填。）\r\n"
)

src = io.open(P, encoding="utf-8", newline="").read()
assert src.count("\r\n") >= 60, "on-disk CRLF convention expected"
for tag, old in (("sec7", S7_OLD), ("sec8", S8_OLD)):
    n = src.count(old)
    assert n == 1, f"{tag} placeholder count={n} expect=1"
out = src.replace(S7_OLD, S7_NEW).replace(S8_OLD, S8_NEW)
# post-edit integrity: placeholders gone, fresh faces present
assert "占位·finalize one-pass" not in out and "占位·§5.5 W174+" not in out
assert "待 W173 finalize 窗" not in out, "stale pending-window face remains"
assert S7_NEW in out and S8_NEW in out
assert "n1_w173_results.json 冻结实测键零改判据" in out
assert "mu_delta_w173_vs_w172ext=**+0.012103**" in out
assert "786,012" in out and "378,520" in out and "0.000398" in out
assert out.count("\r\n") == src.count("\r\n") + (S7_NEW.count("\r\n") - S7_OLD.count("\r\n")) + (S8_NEW.count("\r\n") - S8_OLD.count("\r\n"))
io.open(P, "w", encoding="utf-8", newline="").write(out)
print("sec7/sec8 backfill LANDED; bytes", len(src), "->", len(out))
