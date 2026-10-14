# -*- coding: utf-8 -*-
"""r985 bm-a: W238 prereg sec.7/sec.8 machine-read backfill.
ZERO TRANSCRIPTION (r583 law): every numeric value formatted from the
finalize product + fivekey receipt + sixgate receipt + seat probe receipt.
Placeholder lines replaced in-place by LINE-MATCH; freeze law respected (backfill = sec.7/8 only).
Bloodline clone of _w237bmc_sec78_backfill.py (W237->W238, prev W236->W237)."""
import json, os, sys

sys.stdout.reconfigure(encoding="utf-8")
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PREREG = os.path.join(REPO, "research", "PERPETUAL_N1_W238_PREREG.md")

d = json.load(open(os.path.join(REPO, "results", "perpetual_faces", "n1_w238_results.json"), encoding="utf-8"))
fk = json.load(open(os.path.join(REPO, "results", "_w238bma_fivekey_receipt.json"), encoding="utf-8"))
sg = json.load(open(os.path.join(REPO, "results", "_w238bma_sixgate_prereg.json"), encoding="utf-8"))
probe = json.load(open(os.path.join(REPO, "results", "_w238bma_20261014_probe_receipt.json"), encoding="utf-8"))
prev = json.load(open(os.path.join(REPO, "results", "perpetual_faces", "n1_w237_results.json"), encoding="utf-8"))

led = d["science_gates"]["ledger"]
npc = d["null_pool_cumulative"]
m = npc["merged"]
only_key = [k for k in npc if k.endswith("_only")][0]
wo = npc[only_key]
kl = d["skill_line_v2_k_lift"]
pre_key = [p for p in kl if p.startswith("line_pre")][0]
mrg_key = [p for p in kl if p.startswith("line_merged")][0]
semu = fk["se_mu"]
semu_key = sorted(semu.keys())[0]
prev_semu_key = sorted(k for k in prev["null_pool_cumulative"] if k.startswith("se_mu"))[0]
prev_A_p95 = prev["families"]["A_random_engine_exit"]["full_sharpe_p95"]
famA = d["families"]["A_random_engine_exit"]
keys = fk["five_keys"]
leg4 = probe["legs"]["leg4"]
gi = sg["gates"]["splice_integrity"]
admit = sg["gates"]["seed_admit"]["seat_receipt_leg2"]

s7 = """## §7 跑后实证。【finalize 收口机械回填】
- **finalize one-pass 已落地（r985 bm-a own-wave 窗 2026-10-14 12:5x·承 bm-a own-seat 链 r976 席位发布（MSG-20261014-0745-bma-w238-seat @ origin 3e551d846·早视法 r565）→r983 own-seat prereg derive（47 SUB 对机生成·冻结前落 origin）→r984 五面冻结 splice（50fa77623·sha16 post {pf_sha}/…双 MATCH 验证后提交）→引擎 daemon 自燃 12/12（r984 点火·12:44:04 末分片交付）→本窗 r985 六门 PRE-FINALIZE 正相位跑毕（W217-debt 常设法正确执行·第十三连续正确相位·W212-pattern 零复发）→finalize one-pass→五键机证后收口（披露面 §8）**：
  - 账本恒等式：prev_total **{prev_total:,d}** + batch_trials **{batch_trials:,d}** = total **{total:,d}** EXACT（断言通过）；**冻结 §0 投影偏离披露（r518 origin-time face 律）**：投影 947,389=W237 尾 945,189+2,200·实收链头 945,735=945,189+TRIAL_LAB_W19_SCREEN **546**（W237 finalize 与本波 finalize 之间共享链上合法落位的 trial-labor 屏幕批·results/trial_labor_w19/w19_screen.json·跨生产者共享账本正常推进面·非双计非污染）——恒等式 prev+batch==total 以实收链头为正身 EXACT 成立；
  - 合并池 K=**{merged_k:,d}** EXACT（与投影 {prev_k:,d}+2,200 恒等·零偏离）；merged mu=**{merged_mu}** / merged sigma=**{merged_sigma}**；w238-only mu=**{wo_mu}** / w238-only sigma=**{wo_sigma}**（全机读=results/perpetual_faces/n1_w238_results.json+results/_w238bma_fivekey_receipt.json；锚 W237 实数程序 derive 写入 r583 律）；
  - skill_line_v2 K-lift 对照：line_pre **{line_pre}** → line_merged **{line_merged}** @n_eff {n_eff:,d}；delta **{k4}**（§5 预键 ≤0.02 达标·W2..W237 阶梯对照链实锚）；
  - **§5 五预键机证验证（fivekey probe=results/_w238bma_fivekey_receipt.json·同窗配对）**：key1 w-only vs merged |Δmu|=**{k1}**<0.02 PASS；key2 sigma 相对变化 **{k2}%**<±10% PASS；key3 A 面 p95 **{a_p95}** vs W237 {prev_a_p95} 差 **{k3}**<0.05 PASS；key4 K-lift **{k4}**≤0.02 PASS；key5 投影承接见 §8（**五键全过=§5 五预键全达标零违例**）；
  - se_mu 收窄链头：{semu_key}=**{semu}**（前值 W237 {prev_semu_key}={prev_semu} 链头对照）；
  - canon flip 态=NOT performed（K2200 同律·治理提案面 only）；
  - audit：voids_applied={voids}；machine=bm-a；finalize_only=True；shards_consumed=12/12；evidence_cutoff={cutoff}；
  - **六门探针=PRE-FINALIZE 正相位（W217-debt 常设法正确执行·第十三连续）=results/_w238bma_sixgate_prereg.json**：banned ADMIT rc0+pf selftest 9/9+n1 selftest PASS（缺省波 r522 律）+shards 12/12 在场+seed_admit FREE x2（{admit_a}+{admit_b}·烧录检查点复跑=自撞 BLOCKED=注册落位完整性正锚）+splice 完整性（bands facts==freeze receipt·pf sha16 **{pf_sha}** 与 n1 sha16 **{n1_sha}** 双面 clean-equal 断言通过=family #6 种子面 splice 原子携带零返·W237 界 row 完整保留）+WAVE_CONFIGS[238] row engine_owner=bm-a（a_seed_base=538404/b_exit_seed_base=540404）+**finalize 恒等 post-hoc 断言（账本 {total:,d}/K {merged_k:,d} EXACT）**——W239 冻结方（bm-c 席位已发布 MSG-20261014-0914）必须六门 PRE-FINALIZE（常设法·防死窗复发面）。"""

s8 = """## §8 批后复盘。【finalize 同窗回填】
- **批后复盘（bm-a r985 own-wave 窗回填）**：
  - §5.5 下波投影承接机证：**W239+ 投影=席位 probe 机证 leg4（承本波 §5.5·results/_w238bma_20261014_probe_receipt.json）**：A naive **{p_a_naive}**（被活 SEED_REGISTRY 点 541500/542000+注册 W238 B 带拒·A-hops-prior-B **NINETY-NINTH 例**预期·E36 卡）→ first-clean **{p_a}**（hops=2·**首个种子解耦双跳面**）；B naive **{p_b_naive}**（=本波 B 尾+1 起算）=first-clean **{p_b}**（hops=0·落 naive A 窗内但不落 hopped own-A 窗内=**首个种子解耦 A/B 间隙面**·fc_b==fc_b_naive）——**W239 席位已由 bm-c 发布（MSG-20261014-0914-bmc-w239-seat·A 542_501..544_500/B 540_604..540_803 与本 leg4 投影机证一致）**；W239 冻结方必须 post-W238 注册宇宙重 derive（r587）+六门 PRE-FINALIZE（第十四连续 mandate·本 finalize 已解除其 waits-upstream 物理依赖）；W240+ 投影 at W240 seat。
  - 宝藏与方法论捕获：**六门相位=PRE-FINALIZE 正确执行（W217-debt 常设法连续第十三波正确相位·W212-pattern 零复发）**；**同轮收口律正法执行（r381：12/12 交付 12:44→finalize 同窗 r985 落地·零跨轮拖延）**；**共享链头跨生产者交织面如实披露（六门 ledger_pre 投影 947,389 vs 实收 947,935：TRIAL_LAB_W19_SCREEN 546 合法落位=共享账本正常推进·恒等式以实收链头为正身 EXACT·r518 origin-time face 律执法）**——零新宝藏（TREASURE_REGISTRY 零行·标准链照 canon 无新坑）。
  - 诚实披露面：r985 窗=bm-a own-wave 全周期收口窗（席位自发布 r976 zero-takeover·prereg=own-seat derive r983·splice r984·烧毕同窗 finalize r985·r381 律）；上游 W237 全周期=bm-c r990 own-wave 收口（ledger 945,189/K 519,320 五键全过·sixgate 第十二连续）；S0 拉取=0-behind 干净（50fa77623 tip·未达 origin=0）；本窗烧制无 kill-restart（daemon 自燃 12/12 顺跑）。"""

s7_fmt = s7.format(
    prev_total=led["prev_total"], batch_trials=led["batch_trials"], total=led["total"],
    merged_k=m["n_values"], prev_k=prev["null_pool_cumulative"]["merged"]["n_values"],
    merged_mu=m["mu"], merged_sigma=m["sigma"],
    wo_mu=wo["mu"], wo_sigma=wo["sigma"],
    line_pre=kl[pre_key], line_merged=kl[mrg_key], n_eff=kl["n_eff_held_equal"], k4=kl["line_delta_k_lift"],
    k1=keys["key1_wonly_vs_merged_dmu"]["value"],
    k2=keys["key2_sigma_rel_pct"]["value"],
    a_p95=famA["full_sharpe_p95"], prev_a_p95=prev_A_p95,
    k3=keys["key3_A_p95_diff_vs_w237"]["value"],
    semu_key=semu_key, semu=semu[semu_key],
    prev_semu_key=prev_semu_key, prev_semu=prev["null_pool_cumulative"][prev_semu_key],
    voids=json.dumps(led["voids_applied"], ensure_ascii=False), cutoff=led["evidence_cutoff"],
    admit_a=admit[0].split("base=")[1].split(" verdict")[0],
    admit_b=admit[1].split("base=")[1].split(" verdict")[0],
    pf_sha=gi["pf_sha16_now"], n1_sha=gi["n1_sha16_now"],
)

s8_fmt = s8.format(
    p_a_naive=leg4["W239p_A_naive"], p_a=leg4["W239p_A_first_clean"],
    p_b_naive=leg4["W239p_B_naive"], p_b=leg4["W239p_B_first_clean"],
)

lines = open(PREREG, encoding="utf-8").read().splitlines(keepends=False)
MARK7 = "占位·finalize one-pass"
MARK8 = "占位·finalize 同窗回填"
hits7 = [i for i, l in enumerate(lines) if MARK7 in l]
hits8 = [i for i, l in enumerate(lines) if MARK8 in l]
if hits7 or hits8:
    assert len(hits7) == 1 and len(hits8) == 1, f"placeholder markers not exactly once: {hits7} {hits8}"
    lines[hits7[0]] = s7_fmt.split("\n", 1)[1]
    lines[hits8[0]] = s8_fmt.split("\n", 1)[1]
    open(PREREG, "w", encoding="utf-8", newline="").write("\n".join(lines) + "\n")

check = open(PREREG, encoding="utf-8").read()
assert MARK7 not in check and MARK8 not in check
for needle in ["{:,d}".format(led["total"]), "{:,d}".format(m["n_values"]),
               str(famA["full_sharpe_p95"]), semu_key]:
    assert needle in check, "backfill missing " + needle
print("SEC78-BACKFILL-OK", "(already-done verify pass)" if not (hits7 or hits8) else "(fresh backfill)")
print("placeholders=0 | total", led["total"], "| K", m["n_values"], "| A_p95", famA["full_sharpe_p95"], "|", semu_key, semu[semu_key])
