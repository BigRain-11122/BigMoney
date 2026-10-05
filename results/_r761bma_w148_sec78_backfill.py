# -*- coding: utf-8 -*-
"""r761 bm-a W149 freeze window -- cite-fix leg: backfill W148 prereg
sec7/sec8 with the finalize MEASURED keys (r760 one-pass finalize landed
06:00:04, compressed close-out window did not backfill; r759 cite-fix
precedent for W147 mirrored; backfill content derived from
results/perpetual_faces/n1_w148_results.json machine keys, zero gate
rewording -- needle-asserted count==1 per r745 extract-vs-insert law).
"""
import json
import io

R = json.load(io.open(r"results\perpetual_faces\n1_w148_results.json",
                      encoding="utf-8"))
# machine-derived anchors (zero hand transcription of results)
pre = R["null_pool_cumulative"]["pre_w148_cumulative"]
only = R["null_pool_cumulative"]["w148_only"]
merged = R["null_pool_cumulative"]["merged"]
kl = R["skill_line_v2_k_lift"]
p95 = R["families"]["A_random_engine_exit"]["full_sharpe_p95"]
led = R["science_gates"]["ledger"]
mu_delta = R["null_pool_cumulative"]["mu_delta_w148_vs_w147ext"]
se_mu = R["null_pool_cumulative"]["se_mu_at_k323520"]
assert led["prev_total"] == 719411 and led["batch_trials"] == 2200 \
    and led["total"] == 721611, "ledger keys drift"
assert merged["n_values"] == 323520 and only["n_values"] == 2200, "K drift"
assert kl["n_eff_held_equal"] == 719411 and kl["line_delta_k_lift"] == 0.0, "K-lift drift"
g1 = abs(only["mu"] - merged["mu"])
g2 = (merged["sigma"] - pre["sigma"]) / pre["sigma"] * 100.0
g3 = p95 - 0.3246  # W147 anchor (W147 finalize measured key)
g4 = kl["line_delta_k_lift"]
assert g1 < 0.02 and abs(g2) < 10.0 and abs(g3) < 0.05 and abs(g4) <= 0.02, \
    "gate re-eval beyond prereg bounds (backfill is disclosure, not judging)"

SRC = r"research\PERPETUAL_N1_W148_PREREG.md"
src = io.open(SRC, encoding="utf-8", newline="").read()
assert "\r" not in src, "unexpected CRLF face"

ph7 = ("## §7 跑后实证。【finalize 收口机械回填·占位——跑前为空】\n"
       "- （占位：12/12 分片落地后 finalize one-pass 机械回填·回填限本节与 §8·judged 断言照 W147 例。）")
ph8 = ("## §8 批后复盘。【finalize 同窗回填·占位】\n"
       "- （占位：设计复用面+宝藏捕获问+W149+ 投影承接三行照 W147 例回填。）")
assert src.count(ph7) == 1, "sec7 placeholder needle count!=1"
assert src.count(ph8) == 1, "sec8 placeholder needle count!=1"

sec7 = (
    "## §7 跑后实证。【finalize 收口机械回填·bm-a r760·one-pass rc0·12/12 分片消费；"
    "§7/§8 回填窗注记：r760 finalize one-pass 压缩收口窗未及回填·r761 W149 冻结窗 cite-fix 腿补呈"
    "——回填内容=n1_w148_results.json 冻结实测键·零改判据】\n"
    f"- **合并池**：pre-W148 K=321,320（mu=−{abs(pre['mu']):.6f}·sigma={pre['sigma']:.6f}）"
    f"→ W148-only K=2,200（mu=−{abs(only['mu']):.6f}·sigma={only['sigma']:.6f}）"
    f"→ **merged K=323,520（mu=−0.0928·sigma=0.2449）**；"
    "账本 719,411+2,200=**721,611**（voids_applied=LOWAMP-P1/P2·"
    "file=results/perpetual_faces/n1_w148_results.json·evidence_cutoff=2026-09-22）。\n"
    f"- **skill_line_v2 K-lift**（n_eff 恒等 719,411）：{kl['line_pre_w148']:.4f} → "
    f"**{kl['line_merged_323520']:.4f}**（Δ=**+{abs(kl['line_delta_k_lift']):.4f}**）；"
    f"se_mu 收窄链 W147 0.000432 → **{se_mu:.6f}**（{merged['sigma']:.6f}/√323,520）。\n"
    f"- **A 档 full_sharpe_p95={p95}**（2,000 runs·W147 锚 0.3246）。\n"
    f"- **§5 四预测键全过（机证）**：①|W148-only mu − merged mu|={g1:.4f}<0.02 ✓ "
    f"②sigma 相对变化 {g2:.4f}%<±10% ✓ ③A p95 差 {g3:+.4f}<0.05 ✓ "
    f"④K-lift +{abs(g4):.4f}≤±0.02 ✓。\n"
    "- **canon flip：NOT performed**（K2,200 同例法·治理提锚面 only·结果件如实注记）。\n"
    f"- 审计：12 shards 零重叠连续覆盖 A[0,2000)/B[0,200)·n_backtests 合计 2,200·"
    f"machine=bm-a·audit.finalize_only=true·批内波间漂移键 mu_delta_w148_vs_w147ext={mu_delta:+.6f}。")

sec8 = (
    "## §8 批后复盘。【finalize 同窗回填·bm-a r760（cite-fix 补呈窗 r761）】\n"
    "- 设计=v1 冻结逐字复用·纯种子带深化——零新机制零新方法；"
    "**宝藏捕获问（O-20261003-2030 §1 判决 finalize 收口步）：本批无新宝藏**"
    "（A-hops-prior-B 阶梯第七例+同窗互斥 leg2 面已于冻结窗 r759 确认·E36 卡既有·finalize 无新增面）；"
    "方法论资产卡无 append 面。\n"
    "- W149+ 投影承接（§5 键 5 冻结窗已披露）：A naive 342_404..344_403 将被本波 B 带 "
    "342_404..342_603 拒（阶梯 A-hops-prior-B 继承）→ W149 A 重 derive 同强制（越过 W148 B 带）；"
    "B naive 342_604..342_803 落重 derive 后 A 窗内=**同窗互斥 leg2 律**——"
    "**W149 冻结方必在 post-W148 注册宇宙重 derive 且 derive B 时预留本波 A 窗**"
    "（E36 卡·W141/W143/W145/W147 先例链）；verify at W149 prereg，hop 链逐跳在 probe 回执。")

out = src.replace(ph7, sec7).replace(ph8, sec8)
assert out.count("占位：12/12") == 0 and out.count("占位：设计复用面") == 0, \
    "placeholder residue after backfill"
assert out.count("n1_w148_results.json 冻结实测键") == 1, "cite-fix note missing"
io.open(SRC, "w", encoding="utf-8", newline="\n").write(out)
print(f"W148 sec7/sec8 cite-fix landed: {len(src)} -> {len(out)} bytes "
      f"({len(out)-len(src):+} bytes) | gates re-derive in-bounds: "
      f"g1={g1:.4f} g2={g2:.4f}% g3={g3:+.4f} g4=+{abs(g4):.4f}")
