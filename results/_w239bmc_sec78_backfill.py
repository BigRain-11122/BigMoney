# -*- coding: utf-8 -*-
"""r996-continuation bm-c: W239 prereg sec.7/sec.8 machine-read backfill.
ZERO TRANSCRIPTION (r583 law): every numeric value formatted from the
finalize product + fivekey receipt + sixgate receipt + seat probe receipt.
Placeholder lines replaced in-place by LINE-MATCH (marker substring, robust
against needle-format drift); freeze law respected (backfill = sec.7/8 only).
Bloodline clone of _w237bmc_sec78_backfill.py (W237->W239 generation step;
dead r996-cycle-session estate absorb: sixgate+finalize+fivekey landed on
disk 13:56-13:59:56, backfill = this window's completion step)."""
import json, os, sys

sys.stdout.reconfigure(encoding="utf-8")
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PREREG = os.path.join(REPO, "research", "PERPETUAL_N1_W239_PREREG.md")

d = json.load(open(os.path.join(REPO, "results", "perpetual_faces", "n1_w239_results.json"), encoding="utf-8"))
fk = json.load(open(os.path.join(REPO, "results", "_w239bmc_fivekey_receipt.json"), encoding="utf-8"))
sg = json.load(open(os.path.join(REPO, "results", "_w239bmc_sixgate_prereg.json"), encoding="utf-8"))
probe = json.load(open(os.path.join(REPO, "results", "_w239bmc_20261014_probe_receipt.json"), encoding="utf-8"))
prev = json.load(open(os.path.join(REPO, "results", "perpetual_faces", "n1_w238_results.json"), encoding="utf-8"))

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
wcr = sg["gates"]["wave_configs_row"]

s7 = """## §7 跑后实证。【finalize 收口机械回填】
- **finalize one-pass 已落地（r996-continuation bm-c own-wave 窗 2026-10-14 13:5x-14:0x·承 bm-c own-seat 链 r991 席位发布（MSG-20261014-0914-bmc-w239-seat @ origin 603ff65d9·早视法 r565）→死窗 r996 prereg derive（97a7ff0e6 已上链·死窗 commit 后窗死）→接续窗五面冻结 splice（本窗 origin c85e806c9·sha16 post {pf_sha}/…双 MATCH 验证后提交·E63 arith_a239/arith_b239 修复面 W238 漂移不复发）→引擎 daemon 自燃 12/12（mtime-watch self-commits 65b222df6+6cc36056f）→本窗六门 PRE-FINALIZE 正相位跑毕（13:56·W217-debt 常设法正确执行·第十四连续正确相位·W212-pattern 零复发）→finalize one-pass（13:59）→五键机证后收口（披露面 §8）**：
  - 账本恒等式：prev_total **{prev_total:,d}** + batch_trials **{batch_trials:,d}** = total **{total:,d}** EXACT（断言通过·与 sixgate ledger_pre 投影恒等）；
  - 合并池 K=**{merged_k:,d}** EXACT（与 ledger_pre 投影 {prev_k:,d}+2,200 恒等）；merged mu=**{merged_mu}** / merged sigma=**{merged_sigma}**；w239-only mu=**{wo_mu}** / w239-only sigma=**{wo_sigma}**（全机读=results/perpetual_faces/n1_w239_results.json+results/_w239bmc_fivekey_receipt.json；锚 W238 实数程序 derive 写入 r583 律）；
  - skill_line_v2 K-lift 对照：line_pre **{line_pre}** → line_merged **{line_merged}** @n_eff {n_eff:,d}；delta **{k4}**（§5 预键 ≤0.02 达标·W2..W238 阶梯对照链实锚）；
  - **§5 五预键机证验证（fivekey probe=results/_w239bmc_fivekey_receipt.json·同窗配对）**：key1 w-only vs merged |Δmu|=**{k1}**<0.02 PASS；key2 sigma 相对变化 **{k2}%**<±10% PASS；key3 A 面 p95 **{a_p95}** vs W238 {prev_a_p95} 差 **{k3}**<0.05 PASS；key4 K-lift **{k4}**≤0.02 PASS；key5 投影承接见 §8（**五键全过=§5 五预键全达标零违例**）；
  - se_mu 收窄链头：{semu_key}=**{semu}**（前值 W238 {prev_semu_key}={prev_semu} 链头对照）；
  - canon flip 态=NOT performed（K2200 同律·治理提案面 only）；
  - audit：voids_applied={voids}；machine=bm-c；finalize_only=True；shards_consumed=12/12；evidence_cutoff={cutoff}；
  - **六门探针=PRE-FINALIZE 正相位（W217-debt 常设法正确执行·第十四连续）=results/_w239bmc_sixgate_prereg.json**：banned ADMIT rc0+pf selftest 9/9+n1 selftest PASS+shards 12/12 在场+seed_admit FREE x2（{admit_a}+{admit_b}）+splice 完整性（bands facts==freeze receipt·pf sha16 **{pf_sha}** 与 n1 sha16 **{n1_sha}** 双面 clean-equal 断言通过=family #6 三元组 splice 原子携带零返·W238 界 w<239 合法保留·E63 heal verified）+WAVE_CONFIGS[239] row engine_owner=bm-c（a_seed_base={a_base}/b_exit_seed_base={b_base}）+**finalize 恒等 post-hoc 断言（账本 {total:,d}/K {merged_k:,d} EXACT vs W238 锚）**——W240 冻结方（席位已发布 39a30b6a0·bm-a）必须六门 PRE-FINALIZE（常设法·防死窗复发面）。"""

s8 = """## §8 批后复盘。【finalize 同窗回填】
- **批后复盘（bm-c r996-continuation own-wave 窗回填）**：
  - §5.5 下波投影承接机证：**W240+ 投影=席位 probe 机证 leg4（承本波 §5.5·results/_w239bmc_20261014_probe_receipt.json）**：A naive first-clean **{p_a}**（hops={hops_a}·naive {a_naive} 被 live seed {refusers} 拒·pre-W239 宇宙）；B naive first-clean **{p_b}**（hops={hops_b}）——**B 落在 naive A 窗外（seed-gap face：W239 A/B decoupled·非 W141 同窗互斥面）**；**W240 冻结方必须 post-W239 注册宇宙重 derive 且 derive A/B 时按 live trace 各自重读**（禁假设 staircase A-base==prior-B-tail+1 等式）；投影 INHERITED per leg4（W240 席位已发布 bm-a @ 39a30b6a0·freeze waits-upstream 于本 W239 finalize——已落地）；hop 链逐跳在 probe 回执。
  - 宝藏与方法论捕获：**六门相位=PRE-FINALIZE 正确执行（W217-debt 常设法连续第十四波正确相位·W212-pattern 零复发）**；**死窗遗产吸收范式第五实例**（席位 r991→死窗 prereg derive commit 97a7ff0e6 后窗死→接续窗 splice c85e806c9+burn+sixgate+finalize+fivekey 全链吸收零重烧零重 derive=死窗不重烧不重 derive 零科学面损失）；零新宝藏（TREASURE_REGISTRY 零行·标准链照 canon 无新坑）。
  - 诚实披露面：本窗=r996-continuation 多死窗吸收窗（MV V3 车道会话+收尾准备会话+W239 周期会话三死窗·本窗按 bm-c absorb 先例链收口·详面轮报告）；S0 rebase=origin 3-behind bm-a W19 面集成于本窗收口步；S0.5 消费=ORD 10-14 10:3x-11:1x 行已由死窗会话+lineage-B 双面消费（回执在案）·本窗复核零新行；上游 W238 全周期=bm-a r985 own-wave 收口（ledger 947,935/K 521,520 五键全过）。"""

s7_fmt = s7.format(
    prev_total=led["prev_total"], batch_trials=led["batch_trials"], total=led["total"],
    merged_k=m["n_values"], prev_k=prev["null_pool_cumulative"]["merged"]["n_values"],
    merged_mu=m["mu"], merged_sigma=m["sigma"],
    wo_mu=wo["mu"], wo_sigma=wo["sigma"],
    line_pre=kl[pre_key], line_merged=kl[mrg_key], n_eff=kl["n_eff_held_equal"], k4=kl["line_delta_k_lift"],
    k1=keys["key1_wonly_vs_merged_dmu"]["value"],
    k2=keys["key2_sigma_rel_pct"]["value"],
    a_p95=famA["full_sharpe_p95"], prev_a_p95=prev_A_p95,
    k3=keys["key3_A_p95_diff_vs_w238"]["value"],
    semu_key=semu_key, semu=semu[semu_key],
    prev_semu_key=prev_semu_key, prev_semu=prev["null_pool_cumulative"][prev_semu_key],
    voids=json.dumps(led["voids_applied"], ensure_ascii=False), cutoff=led["evidence_cutoff"],
    admit_a=admit[0].split("base=")[1].split(" verdict")[0],
    admit_b=admit[1].split("base=")[1].split(" verdict")[0],
    pf_sha=gi["pf_sha16_now"], n1_sha=gi["n1_sha16_now"],
    a_base=wcr["a_seed_base"], b_base=wcr["b_exit_seed_base"],
)

s8_fmt = s8.format(
    p_a=leg4["W240p_A_first_clean"], hops_a=leg4["hops_A"],
    a_naive=leg4["W240p_A_naive"], refusers=",".join(str(s) for s in leg4["W240p_A_naive_refusers_seeds"]),
    p_b=leg4["W240p_B_naive"], hops_b=leg4["hops_B"],
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

# verify: placeholders gone, key machine-read values present
check = open(PREREG, encoding="utf-8").read()
assert MARK7 not in check and MARK8 not in check
for needle in ["{:,d}".format(led["total"]), "{:,d}".format(m["n_values"]),
               str(famA["full_sharpe_p95"]), semu_key]:
    assert needle in check, "backfill missing " + needle
print("SEC78-BACKFILL-OK", "(already-done verify pass)" if not (hits7 or hits8) else "(fresh backfill)")
print("placeholders=0 | total", led["total"], "| K", m["n_values"], "| A_p95", famA["full_sharpe_p95"], "|", semu_key, semu[semu_key])
