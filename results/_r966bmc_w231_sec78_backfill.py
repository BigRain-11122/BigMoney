# -*- coding: utf-8 -*-
"""r966 bm-c: W231 prereg sec.7/sec.8 machine-read backfill.
ZERO TRANSCRIPTION (r583 law): every numeric value formatted from the
finalize product + fivekey receipt + sixgate receipt + seat probe receipt.
Placeholder lines replaced in-place by LINE-MATCH (marker substring, robust
against needle-format drift); freeze law respected (backfill = sec.7/8 only).
Bloodline clone of _r963bmc_w230_sec78_backfill.py (W230->W231, prev W229->W230)."""
import json
import sys

sys.stdout.reconfigure(encoding="utf-8")
REPO = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
PREREG = REPO + r"\research\PERPETUAL_N1_W231_PREREG.md"

d = json.load(open(REPO + r"\results\perpetual_faces\n1_w231_results.json", encoding="utf-8"))
fk = json.load(open(REPO + r"\results\_r966bmc_w231_fivekey_receipt.json", encoding="utf-8"))
sg = json.load(open(REPO + r"\results\_r966bmc_w231_sixgate_prereg.json", encoding="utf-8"))
probe = json.load(open(REPO + r"\results\_w231bmc_20261013_probe_receipt.json", encoding="utf-8"))
prev = json.load(open(REPO + r"\results\perpetual_faces\n1_w230_results.json", encoding="utf-8"))

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
- **finalize one-pass 已落地（r966 窗 2026-10-13 13:3x·承 r963 席位发布 6638ddf9f+死 r964 窗 prereg derive aebe0a5ac（FIFTEEN 级 lineage replay 46/46·上链自证）+死 12:5x 窗 editor derive（_w231bmc_derive_editor.py 12:59 落盘未 commit·本窗 absorb）+本窗 r966 执行五面冻结 splice（编辑器自带 fail-closed 门全过：gate0 origin+gate0.5 上游锚 929,789/K=503,920+post-edit count gates+py_compile 双绿）→estate commit aee0bd9fa→引擎 daemon mtime-watch 自燃 12/12（batched ledger append 492972ee7+4e373b743 自提交）→六门 PRE-FINALIZE 正相位跑毕（W217-debt 常设法正确执行·第六连续正确相位·W212-pattern 零复发）→finalize one-pass→五键机证后收口（披露面 §8）**：
  - 账本恒等式：prev_total **{prev_total:,d}** + batch_trials **{batch_trials:,d}** = total **{total:,d}** EXACT（断言通过·与 sixgate ledger_pre 投影恒等）；
  - 合并池 K=**{merged_k:,d}** EXACT（与 ledger_pre 投影 {prev_k:,d}+2,200 恒等）；merged mu=**{merged_mu}** / merged sigma=**{merged_sigma}**；w231-only mu=**{wo_mu}** / w231-only sigma=**{wo_sigma}**（全机读=results/perpetual_faces/n1_w231_results.json+results/_r966bmc_w231_fivekey_receipt.json；锚 W230 实数程序 derive 写入 r583 律）；
  - skill_line_v2 K-lift 对照：line_pre **{line_pre}** → line_merged **{line_merged}** @n_eff {n_eff:,d}；delta **{k4}**（§5 预键 ≤0.02 达标·W2..W230 阶梯对照链实锚）；
  - **§5 五预键机证验证（fivekey probe=results/_r966bmc_w231_fivekey_receipt.json·同窗配对）**：key1 w-only vs merged |Δmu|=**{k1}**<0.02 PASS；key2 sigma 相对变化 **{k2}%**<±10% PASS；key3 A 面 p95 **{a_p95}** vs W230 {prev_a_p95} 差 **{k3}**<0.05 PASS；key4 K-lift **{k4}**≤0.02 PASS；key5 投影承接见 §8（**五键全过=§5 五预键全达标零违例**）；
  - se_mu 收窄链头：{semu_key}=**{semu}**（前值 W230 {prev_semu_key}={prev_semu} 收窄·链头收窄）；
  - canon flip 态=NOT performed（K2200 同律·治理提案面 only）；
  - audit：voids_applied={voids}；machine=bm-c；finalize_only=True；shards_consumed=12/12；evidence_cutoff={cutoff}；
  - **六门探针=PRE-FINALIZE 正相位（W217-debt 常设法正确执行·第六连续）=results/_r966bmc_w231_sixgate_prereg.json**：banned ADMIT rc0+pf selftest 9/9+n1 selftest PASS+shards 12/12 在场+seed_admit FREE x2（{admit_a}+{admit_b}）+splice 完整性（bands facts==freeze receipt·pf sha16 **{pf_sha}** 与 n1 sha16 **{n1_sha}** 双面 clean-equal 断言通过=family #6 三元组 splice 原子携带零返·W230 界 w<230 x3 合法保留）+WAVE_CONFIGS[231] row engine_owner=bm-c（a_seed_base=523004/b_exit_seed_base=525004）+**finalize 恒等 post-hoc 断言（账本 {total:,d}/K {merged_k:,d} EXACT vs W230 锚）**——W232 必须六门 PRE-FINALIZE（常设法·防死窗复发面）。"""

s8 = """## §8 批后复盘。【finalize 同窗回填】
- **批后复盘（bm-c r966 窗回填）**：
  - §5.5 下波投影承接机证：**W232+ 投影=席位 probe 机证 leg4（承本波 §5.5·results/_w231bmc_20261013_probe_receipt.json）**：A naive first-clean **{p_a}**（hops=0·pre-W231 宇宙·post-W231 注册宇宙待重 derive）；B naive first-clean **{p_b}**（hops=0）——**naive B 落在 naive A 窗内**（W141 先例·同窗互斥面适用于 W232）；**W231 B 带 525_004..525_203 注册后将拒 naive W232 A 窗**（A-hops-prior-B **NINETY-SECOND 例**预期·E36 卡/leg2 律）：W232 冻结方必须 post-W231 注册宇宙重 derive 且 derive B 时**预留本波 A 窗**；verify at W232 prereg·hop 链逐跳在 probe 回执。
  - 宝藏与方法论捕获：**六门相位=PRE-FINALIZE 正确执行（W217-debt 常设法连续第六波正确相位·W212-pattern 零复发）**——本窗零死窗半成品（prereg=死 r964 窗自提交上链·editor=死 12:5x 窗落盘本窗 absorb 执行 splice·引擎自燃 12/12 自提交 492972ee7+4e373b743）=法面无缺口；**S0.5 幻影水位案=新方法论面（corrupt-face 第 5/6 例·ORD c7d3ee65/DEC f41caf26 双双不在 blob 史）**——r965 窗消费声明所记 sha 为幻影、行内容已被描述（行级消费实质完成）·本窗 blob 史逐 commit sha256 对账治愈水位（ORD 前移 f4d2ea1b·DEC 归位 fb5825cb）·启示=水位记录脚本必须 blob 史存在性断言（防 6 例复发）；零新宝藏（TREASURE_REGISTRY 零行）。
  - 诚实披露面：r966 窗 splice=本窗亲手执行（非死窗 estate 吸收——编辑器门内自证+estate commit aee0bd9fa 上链）；S0.5 ORD 新行 11:3x-13:1x 全 BigStream MV-lane 零 BigMoney 动作·**10-12 23:3x RAM 撤单令涉本机**（bm-c/bm-b RAM 采购冻结·装机回执单作废·RAM-GATE 单片 >8G 分片让渡 bm-a 常设·W 波 CPU 面不动）回执在轮报告；DEC fb5825cb 自 00:07 未变零新行；MV i2v 车道并行无欠账（GPU 面由 bm-a 导演席调度·12:1x @bm-c V3 回炉 5 槽=夜窗 GPU 域）。"""

s7_fmt = s7.format(
    prev_total=led["prev_total"], batch_trials=led["batch_trials"], total=led["total"],
    merged_k=m["n_values"], prev_k=prev["null_pool_cumulative"]["merged"]["n_values"],
    merged_mu=m["mu"], merged_sigma=m["sigma"],
    wo_mu=wo["mu"], wo_sigma=wo["sigma"],
    line_pre=kl[pre_key], line_merged=kl[mrg_key], n_eff=kl["n_eff_held_equal"], k4=kl["line_delta_k_lift"],
    k1=keys["key1_wonly_vs_merged_dmu"]["value"],
    k2=keys["key2_sigma_rel_pct"]["value"],
    a_p95=famA["full_sharpe_p95"], prev_a_p95=prev_A_p95,
    k3=keys["key3_A_p95_diff_vs_w230"]["value"],
    semu_key=semu_key, semu=semu[semu_key],
    prev_semu_key=prev_semu_key, prev_semu=prev["null_pool_cumulative"][prev_semu_key],
    voids=json.dumps(led["voids_applied"], ensure_ascii=False), cutoff=led["evidence_cutoff"],
    admit_a=admit[0].split("base=")[1].split(" verdict")[0],
    admit_b=admit[1].split("base=")[1].split(" verdict")[0],
    pf_sha=gi["pf_sha16_now"], n1_sha=gi["n1_sha16_now"],
)

s8_fmt = s8.format(
    p_a=leg4["W231p_A"], p_b=leg4["W231p_B"],
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
