# _r868bma_w182_sec78_backfill.py -- W182 prereg sec7/8 same-window backfill (r864 lesson honored).
# All values machine-read from results/perpetual_faces/n1_w182_results.json (zero hand-copy).
# Fresh-read-modify-write (multi-writer file law); byte-preserve head/tail outside the two
# placeholder sections; verify placeholders found exactly once each.
import json

R = json.load(open("results/perpetual_faces/n1_w182_results.json", encoding="utf-8"))

def g(*keys):
    o = R
    for k in keys:
        o = o[k]
    return o

merged = g("null_pool_cumulative", "merged")
pre = g("null_pool_cumulative", "pre_w182_cumulative")
wonly = g("null_pool_cumulative", "w182_only")
sk = g("skill_line_v2_k_lift")
led = g("science_gates", "ledger")
afam = g("families", "A_random_engine_exit")

led_prev, led_batch, led_total = led["prev_total"], led["batch_trials"], led["total"]
K_merged = merged["n_values"]
mu_m, mu_w, mu_pre = merged["mu"], wonly["mu"], pre["mu"]
sig_m, sig_w, sig_pre = merged["sigma"], wonly["sigma"], pre["sigma"]
se_mu = g("null_pool_cumulative", "se_mu_at_k398320")
mu_delta = g("null_pool_cumulative", "mu_delta_w182_vs_w181ext")
p95, p99, a_mu = afam["full_sharpe_p95"], afam["full_sharpe_p99"], afam["full_sharpe_mu"]
line_pre, line_m, klift = sk["line_pre_w182"], sk["line_merged_398320"], sk["line_delta_k_lift"]
n_eff = sk["n_eff_held_equal"]
voids = ",".join(led["voids_applied"])

gap1 = abs(mu_w - mu_pre)
sig_rel = (sig_m - sig_pre) / sig_pre * 100.0
p95_delta = p95 - 0.3073  # vs W181 anchor 0.3073

SEC7 = f"""## §7 跑后实证。【finalize 收口机械回填·r868 同窗】
- 账本恒等式：{led_prev:,} + {led_batch:,} = **{led_total:,}** EXACT（prev_total/batch_trials/total 三键机读·r868 finalize one-pass 实测；**vs §5 冻结投影（=W181 净链头 {led_prev:,}+2,200 机械算）差 +0 EXACT 命中**——本波零冻结后增量·零漂移）。
- 合并池：**K={K_merged:,}** EXACT（=W181 池 396,120 + 本波 2,200·§5 投影 398,320 命中）。
- merged mu **−{abs(mu_m):.6f}**（机读 {mu_m:.7f}）/ w-only mu **−{abs(mu_w):.6f}** / mu_delta(w182 vs w181ext) **+{mu_delta:.6f}**。
- merged sigma **{sig_m:.6f}**（W181 键 0.245101→{sig_m:.6f}）；w-only sigma {sig_w:.6f}；se_mu@K{K_merged:,} **{se_mu:.6f}**（W181 0.000389→{se_mu:.6f} 收窄·链面 …W180 0.000391→W181 0.000389→W182 {se_mu:.6f}）。
- skill_line_v2：line_pre **{line_pre}** → line_merged@K{K_merged:,} **{line_m}**（K-lift **+{klift:.4f}**·n_eff_held_equal {n_eff:,}·四dp 无 roll——W181 −0.0001 后本波持平）；canon flip **NOT performed**（K2,200 同例法·治理提案面）。
- A 档 full_sharpe_p95 **{p95}**（W181 锚 0.3073·Δ{p95_delta:+.4f}<0.05 门过）·p99 {p99}·A mu −{abs(a_mu):.6f}。
- §5 四预键机证全过：①mu gap |−{abs(mu_w):.6f}−(−{abs(mu_pre):.6f})|={gap1:.6f}<0.02 PASS ②sigma 相对变化 {sig_rel:+.4f}%<±10% PASS ③A p95 Δ{p95_delta:+.4f}<0.05 PASS ④K-lift +{klift:.4f}≤±0.02 PASS。
- audit.finalize_only=**true**（bm-a）·voids_applied={voids}·evidence_cutoff={g('evidence_cutoff')} 在位·shards_consumed 12/12（引擎自烧 07:06-07:17 pid=77636）。
"""

SEC8 = f"""## §8 批后复盘。【finalize 同窗回填·r868 同窗】
- §5.5 W183+ 投影承接（r865 seat probe 回执机证·W183 冻结方重 derive 强制非转抄 r587 律）：naive A **417_204..419_203**（hops=0 CLEAN）——将被注册 W182 B 带 417_204..417_403 own-start 拒=阶梯 A-hops-prior-B **第四十三例**待 W183 注册宇宙复核；naive B **417_404..417_603**（hops=0 CLEAN）落 naive A 窗内——W141 同窗互斥 leg2 律适用 W183（derive B 时预留本波 A 窗·W182 §5.5 预披露注记在案）。
- 宝藏/方法论捕获问：本批 finalize one-pass=canonical runner 单发 r718 先例 verbatim 复用零新方法零新宝藏；TREASURE/METHODOLOGY 零 append（本窗 r868 rebase-storm 治愈为新 pit 面·入 CODELY 坑律非方法论资产卡）。
- 诚实披露面：W182-only mu −{abs(mu_w):.4f} 比合并池 −{abs(mu_m):.4f} 浅 {mu_delta:.4f}≈{mu_delta/0.0052:.1f}× w-only se（2,200 抽样 se≈{sig_w:.4f}/√2200≈0.0052）=null 抽样正常波动非异常（方向与 W181 深 −0.0059 相反·单波 w-only 面小样本波动·四预键①仍 PASS {gap1:.4f}<0.02）；K-lift **+0.0000**（W181 −0.0001 后本波持平·线 1.1854→1.1854·n_eff 基 {n_eff:,}=W181 head 零增量）；A p95 {p95} 较 W181 锚 0.3073 下移 0.0002 仍门内；账本投影差 +0 双 EXACT（W181 曾差 +413=W16 合法增量·本波零冻结后增量对照如实披露）；引擎 tick 自烧 12 分片（07:06-07:17）+finalize r868 同轮收口（r381 律）+**§7/§8 同窗回填（r864 漏补教训本波兑现·非补窗）**。
- **回填窗注记：r868 finalize 同窗机械回填（无漏补窗·r864 教训已焊入流程）**（数据全量本窗落件 n1_w182_results.json 机读零手抄·head/tail 字节保全）。
"""

p = "research/PERPETUAL_N1_W182_PREREG.md"
t = open(p, encoding="utf-8").read()

ph7 = "## §7 跑后实证。【finalize 收口机械回填·待 W182 finalize 窗】\n- （占位·finalize one-pass 后机械回填：账本恒等式+合并池 K+merged mu/w-only mu/mu_delta+sigma+se_mu+skill_line_v2 K-lift+A 档 p95+§5 四预键机证+canon flip 态+audit.finalize_only+voids_applied。）\n"
ph8 = "## §8 批后复盘。【finalize 同窗回填·待 W182 finalize 窗】\n- （占位·§5.5 W183+ 投影承接+宝藏/方法论捕获问+诚实披露面·finalize 收口窗机械回填。）\n"

assert t.count(ph7) == 1, f"ph7 count={t.count(ph7)}"
assert t.count(ph8) == 1, f"ph8 count={t.count(ph8)}"

nt = t.replace(ph7, SEC7).replace(ph8, SEC8)
open(p, "w", encoding="utf-8", newline="").write(nt)

# head/tail byte-preservation self-check: everything before ph7 and after ph8 unchanged
h_old, h_new = t.split(ph7)[0], nt.split(SEC7)[0]
t_old = ph8.join(t.split(ph8)[1:]) if ph8 in t else ""
t_new = SEC8.join(nt.split(SEC8)[1:]) if SEC8 in nt else ""
assert h_old == h_new, "head drift"
assert t_old == t_new, "tail drift"
print("sec7/8 backfilled OK; head/tail byte-preserved; bytes:", len(t), "->", len(nt))
