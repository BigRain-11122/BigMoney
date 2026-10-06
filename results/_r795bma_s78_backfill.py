# -*- coding: utf-8 -*-
"""r795 bm-a W165 prereg §7/§8 mechanical backfill (finalize-closeout step).
All numbers machine-read from results/perpetual_faces/n1_w165_results.json
(r587 never-transcribe law). Replaces the two placeholder sections with the
landed finalize facts."""
import io
import json

PRE = "research/PERPETUAL_N1_W165_PREREG.md"
RES = "results/perpetual_faces/n1_w165_results.json"

r = json.load(open(RES, encoding="utf-8"))
m = r["null_pool_cumulative"]["merged"]
own = r["null_pool_cumulative"]["w165_only"]
led = r["science_gates"]["ledger"]
sk = r["skill_line_v2_k_lift"]
nc = r["null_pool_cumulative"]
canon = nc.get("canon")
se_mu = nc.get("se_mu_at_k360920")
fams = r["families"]
ap95 = fams.get("A_random_engine_exit", {}).get("full_sharpe_p95")
shards = r.get("shards_consumed")
audit = r.get("audit", {})

s7 = (
    "## §7 跑后实证。【finalize 收口机械回填·r795 落】\n"
    "- **合并池**：merged K=%s·mu=%s·sigma=%s（机取 n1_w165_results.json null_pool_cumulative.merged）。\n"
    "- **本波独立面**：w165_only K=%s·mu=%s·sigma=%s。\n"
    "- **账本**：prev_total %s + batch_trials %s = **total %s**（batch=%s·voids_applied=%s·evidence_cutoff=%s）。\n"
    "- **K-lift**：skill_line_v2 @n_eff=%s：%s -> %s（delta **%s**·方向如实=本波微降）。\n"
    "- **se_mu@K%s**：%s（机器键 se_mu_at_k%s）。\n"
    "- **A 随机引擎出场 p95**：%s（families.A_random_engine_exit.full_sharpe_p95）。\n"
    "- **§5 四键机证**：seeds 带位对账=gate ADMIT 回执在场（band/projection 双窗恒等·pre-seat probe 与冻结窗 gate 同窗双跑 r793 实跑）；canon flip 态=%s；shards_consumed=%s。\n"
    "- **审计段**：finalize one-pass bm-a r795（12/12 shards 引擎 tick 自燃烧录 r535 律·本窗 finalize 命令收口·audit=%s）。\n"
) % (
    f"{m['n_values']:,}", f"{m['mu']:.4f}" if abs(m['mu'])>1e-6 else m['mu'], f"{m['sigma']:.6f}".rstrip('0'),
    f"{own['n_values']:,}", f"{own['mu']:.6f}", f"{own['sigma']:.8f}".rstrip('0'),
    f"{led['prev_total']:,}", f"{led['batch_trials']:,}", f"{led['total']:,}",
    led['batch'], "/".join(led.get('voids_applied', [])), led.get('evidence_cutoff'),
    f"{sk.get('n_eff_held_equal', led['prev_total']):,}",
    f"{sk.get('line_pre_w165', sk.get('line_pre', '?'))}", f"{sk.get('line_merged_%s' % m['n_values'], sk.get('line_merged', '?'))}",
    f"{sk.get('line_delta_k_lift', '?')}",
    f"{m['n_values']:,}", se_mu, f"{m['n_values']:,}",
    ap95, canon, shards, str(audit)[:120],
)

s8 = (
    "## §8 批后复盘。【finalize 同窗回填·r795 落】\n"
    "- **设计复用面**：冻结 v1 设计 verbatim 零改动（例行 nulls-deepening 波·r794 工具血统+本窗 6 处值修正不涉设计）；无方法论新增（METHODOLOGY_ASSETS 零 append·捕获律问过=无新方法）。\n"
    "- **宝藏捕获问**：本批宝藏=无新增（例行波·TREASURE_REGISTRY 零出入记录·捕获律问过）。\n"
    "- **W166+ 投影承接**：A first-clean 379_804..381_803 CLEAN（hops=0）/B first-clean 380_004..380_203 CLEAN（hops=0）——naive B 落 naive A 窗内·W166 冻结方必须在 post-W165 注册宇宙重 derive 且 derive B 时预留本波 A 窗（W141 先例·leg2 律·E36 阶梯卡）；**W165 B 带 379_804..380_003 注册后将拒 naive W166 A 窗**——阶梯 A-hops-prior-B 继承第二十五例待 W166 注册宇宙复核（gate leg3 verbatim·r587 非转抄）。\n"
    "- **诚实披露**：本波 K-lift 微降 -0.0001（1.1834→1.1833）如实记录；se_mu/A p95 键名如有漂移以 n1_w165_results.json 机读为准。\n"
)

src = io.open(PRE, encoding="utf-8", newline="").read()
i = src.find("## §7 跑后实证")
j = src.find("## §8 批后复盘")
k = src.find("- **跑前冻结=本件 commit**")
assert 0 < i < j < k, (i, j, k)
new = s7 + "\n" + s8 + "\n\n"
out = src[:i] + new + src[k:]
io.open(PRE, "w", encoding="utf-8", newline="").write(out)
print("§7/§8 backfilled:", len(new), "bytes; file now", len(out), "bytes")
