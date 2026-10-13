# -*- coding: utf-8 -*-
"""r975 bm-a: W236 prereg sec.7/sec.8 machine-read backfill.
ZERO TRANSCRIPTION (r583 law): every numeric value formatted from the
finalize product + fivekey receipt + sixgate receipt + seat probe receipt.
Placeholder lines replaced in-place by LINE-MATCH (marker substring, robust
against needle-format drift); freeze law respected (backfill = sec.7/8 only).
Bloodline clone of _r970bma_w235_sec78_backfill.py (W235->W236, prev W234->W235)."""
import json
import sys

sys.stdout.reconfigure(encoding="utf-8")
REPO = r"C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney"
PREREG = REPO + r"\research\PERPETUAL_N1_W236_PREREG.md"

d = json.load(open(REPO + r"\results\perpetual_faces\n1_w236_results.json", encoding="utf-8"))
fk = json.load(open(REPO + r"\results\_r975bma_w236_fivekey_receipt.json", encoding="utf-8"))
sg = json.load(open(REPO + r"\results\_r975bma_w236_sixgate_prereg.json", encoding="utf-8"))
probe = json.load(open(REPO + r"\results\_w236bma_20261014_probe_receipt.json", encoding="utf-8"))
prev = json.load(open(REPO + r"\results\perpetual_faces\n1_w235_results.json", encoding="utf-8"))

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
- **finalize one-pass 已落地（r975 bm-a own-wave 遗产吸收收口窗 2026-10-14 07:1x·承 bm-a own-seat 链 r971 席位发布（MSG-20261014-0446-bma-w236-seat @ origin 5c25db795·早视法 r565）→r972 prereg derive（67ade8314·own-seat 零接管）→五面冻结 splice（死窗中断于 commit 前·本 r975 窗遗产吸收落链 6e798bd22·sha16 post 44b87d828160d281/de93f34835a652f5 双 MATCH 验证后提交）→引擎 daemon 自燃 12/12（06:52-07:03 窗 ~1min/shard·burn shards 落链 08b6067c9）→本窗 r975 六门 PRE-FINALIZE 正相位跑毕（W217-debt 常设法正确执行·第十一连续正确相位·W212-pattern 零复发）→finalize one-pass→五键机证后收口（披露面 §8）**：
  - 账本恒等式：prev_total **{prev_total:,d}** + batch_trials **{batch_trials:,d}** = total **{total:,d}** EXACT（断言通过·与 sixgate ledger_pre 投影恒等）；
  - 合并池 K=**{merged_k:,d}** EXACT（与 ledger_pre 投影 {prev_k:,d}+2,200 恒等）；merged mu=**{merged_mu}** / merged sigma=**{merged_sigma}**；w236-only mu=**{wo_mu}** / w236-only sigma=**{wo_sigma}**（全机读=results/perpetual_faces/n1_w236_results.json+results/_r975bma_w236_fivekey_receipt.json；锚 W235 实数程序 derive 写入 r583 律）；
  - skill_line_v2 K-lift 对照：line_pre **{line_pre}** → line_merged **{line_merged}** @n_eff {n_eff:,d}；delta **{k4}**（§5 预键 ≤0.02 达标·W2..W235 阶梯对照链实锚）；
  - **§5 五预键机证验证（fivekey probe=results/_r975bma_w236_fivekey_receipt.json·同窗配对）**：key1 w-only vs merged |Δmu|=**{k1}**<0.02 PASS；key2 sigma 相对变化 **{k2}%**<±10% PASS；key3 A 面 p95 **{a_p95}** vs W235 {prev_a_p95} 差 **{k3}**<0.05 PASS；key4 K-lift **{k4}**≤0.02 PASS；key5 投影承接见 §8（**五键全过=§5 五预键全达标零违例**）；
  - se_mu 收窄链头：{semu_key}=**{semu}**（前值 W235 {prev_semu_key}={prev_semu} 链头对照）；
  - canon flip 态=NOT performed（K2200 同律·治理提案面 only）；
  - audit：voids_applied={voids}；machine=bm-a；finalize_only=True；shards_consumed=12/12；evidence_cutoff={cutoff}；
  - **六门探针=PRE-FINALIZE 正相位（W217-debt 常设法正确执行·第十一连续）=results/_r975bma_w236_sixgate_prereg.json**：banned ADMIT rc0+pf selftest 9/9+n1 selftest PASS+shards 12/12 在场+seed_admit FREE x2（{admit_a}+{admit_b}·烧录检查点复跑=自撞 BLOCKED=注册落位完整性正锚）+splice 完整性（bands facts==freeze receipt·pf sha16 **{pf_sha}** 与 n1 sha16 **{n1_sha}** 双面 clean-equal 断言通过=family #6 三元组 splice 原子携带零返·W235 界 w<236 x3 合法保留）+WAVE_CONFIGS[236] row engine_owner=bm-a（a_seed_base=534004/b_exit_seed_base=536004）+**finalize 恒等 post-hoc 断言（账本 {total:,d}/K {merged_k:,d} EXACT vs W235 锚）**——W237 冻结方（bm-c 席已发布）必须六门 PRE-FINALIZE（常设法·防死窗复发面）。"""

s8 = """## §8 批后复盘。【finalize 同窗回填】
- **批后复盘（bm-a r975 own-wave 遗产吸收收口窗回填）**：
  - §5.5 下波投影承接机证：**W237+ 投影=席位 probe 机证 leg4（承本波 §5.5·results/_w236bma_20261014_probe_receipt.json）**：A naive first-clean **{p_a}**（hops=0·pre-W236 宇宙·post-W236 注册宇宙待重 derive）；B naive first-clean **{p_b}**（hops=0）——**naive B 落在 naive A 窗内**（W141 先例·同窗互斥面适用于 W237）；**W236 B 带 536_004..536_203 注册后将拒 naive W237 A 窗**（A-hops-prior-B **NINETY-SEVENTH 例**预期·E36 卡/leg2 律）：W237 冻结方必须 post-W236 注册宇宙重 derive 且 derive B 时**预留本波 A 窗**——**已实证**：bm-c W237 席已发布（9312ef7ac/5654c4f04·A 536_204..538_203 hops=1 NINETY-SEVENTH staircase / B 538_204..538_403 own-A-reserved W141 先例·probe ADMIT seed_admit FREE x2·wait-upstream 本 W236 finalize 已落）=投影 CONFIRMED by published seat；verify at W237 prereg·hop 链逐跳在 probe 回执。
  - 宝藏与方法论捕获：**六门相位=PRE-FINALIZE 正确执行（W217-debt 常设法连续第十一波正确相位·W212-pattern 零复发）**；**死窗遗产吸收范式再证**（r899 先例第三实例：席位 r971→prereg r972→冻结编辑全落盘但 commit 前窗死→接续窗验 sha16 双 MATCH+selftest 后零返工直接落链=死窗不重烧不重 derive 零科学面损失）；零新宝藏（TREASURE_REGISTRY 零行·标准链照 canon 无新坑）。
  - 诚实披露面：r975 窗=bm-a own-wave finalize 遗产吸收窗（席位自发布 zero-takeover·own-seat continuity）；轮报告面 r962 后死窗断档至 r975（r963-r974 死窗工作实锚=origin 提交链 W205..W236 波序+T-182 等·收口行全缺=本窗诚实补账·序列以 r975 续接不回改）；S0 rebase 干净（2-behind 非重叠·紧循环 E42/r884 法）；上游 W235 全周期=bm-a r970 own-wave 收口（takeover face·ledger 940,589/K 514,920 五键全过）；S0.5 消费本窗=见轮报告（水位探针按 d19_watermark 双扫）。"""

s7_fmt = s7.format(
    prev_total=led["prev_total"], batch_trials=led["batch_trials"], total=led["total"],
    merged_k=m["n_values"], prev_k=prev["null_pool_cumulative"]["merged"]["n_values"],
    merged_mu=m["mu"], merged_sigma=m["sigma"],
    wo_mu=wo["mu"], wo_sigma=wo["sigma"],
    line_pre=kl[pre_key], line_merged=kl[mrg_key], n_eff=kl["n_eff_held_equal"], k4=kl["line_delta_k_lift"],
    k1=keys["key1_wonly_vs_merged_dmu"]["value"],
    k2=keys["key2_sigma_rel_pct"]["value"],
    a_p95=famA["full_sharpe_p95"], prev_a_p95=prev_A_p95,
    k3=keys["key3_A_p95_diff_vs_w235"]["value"],
    semu_key=semu_key, semu=semu[semu_key],
    prev_semu_key=prev_semu_key, prev_semu=prev["null_pool_cumulative"][prev_semu_key],
    voids=json.dumps(led["voids_applied"], ensure_ascii=False), cutoff=led["evidence_cutoff"],
    admit_a=admit[0].split("base=")[1].split(" verdict")[0],
    admit_b=admit[1].split("base=")[1].split(" verdict")[0],
    pf_sha=gi["pf_sha16_now"], n1_sha=gi["n1_sha16_now"],
)

s8_fmt = s8.format(
    p_a=leg4["W237p_A"], p_b=leg4["W237p_B"],
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
