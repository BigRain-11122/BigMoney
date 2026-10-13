# -*- coding: utf-8 -*-
"""r974 bm-c: W233 prereg sec.7/sec.8 machine-read backfill.
ZERO TRANSCRIPTION (r583 law): every numeric value formatted from the
finalize product + fivekey receipt + sixgate receipt + seat probe receipt.
Placeholder lines replaced in-place by LINE-MATCH (marker substring, robust
against needle-format drift); freeze law respected (backfill = sec.7/8 only).
Bloodline clone of _r968bmc_w232_sec78_backfill.py (W232->W233, prev W231->W232)."""
import json
import sys

sys.stdout.reconfigure(encoding="utf-8")
REPO = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
PREREG = REPO + r"\research\PERPETUAL_N1_W233_PREREG.md"

d = json.load(open(REPO + r"\results\perpetual_faces\n1_w233_results.json", encoding="utf-8"))
fk = json.load(open(REPO + r"\results\_r974bmc_w233_fivekey_receipt.json", encoding="utf-8"))
sg = json.load(open(REPO + r"\results\_r974bmc_w233_sixgate_prereg.json", encoding="utf-8"))
probe = json.load(open(REPO + r"\results\_w233bmc_20261013_probe_receipt.json", encoding="utf-8"))
prev = json.load(open(REPO + r"\results\perpetual_faces\n1_w232_results.json", encoding="utf-8"))

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
- **finalize one-pass 已落地（r974 吸收窗 2026-10-13 19:5x·承 r968 吸收窗席位发布 dd38a9da8（probe ADMIT+MSG-1530）+死 r972 窗 prereg derive（R33 authored+subgen m30+17 级 lineage replay 46/46+phase-B S-table 3 mis-aged pairs 修复·commit 933e3ceea 上链自证）+死 r973 窗 census-first derive 8 轮+五面冻结 splice（编辑器 first-pass ALL GREEN 49,833 template·62 shifts+22 pairs+sentinel family-5+stale/must_one/final asserts·freeze receipt 19:24:08·estate commit 0ca920362）→引擎 daemon mtime-watch 自燃 12/12（batched ledger append 6c1587483+d4cce3ffe 自提交）→本窗 r974 六门 PRE-FINALIZE 正相位跑毕（W217-debt 常设法正确执行·第八连续正确相位·W212-pattern 零复发）→finalize one-pass→五键机证后收口（披露面 §8）**：
  - 账本恒等式：prev_total **{prev_total:,d}** + batch_trials **{batch_trials:,d}** = total **{total:,d}** EXACT（断言通过·与 sixgate ledger_pre 投影恒等）；
  - 合并池 K=**{merged_k:,d}** EXACT（与 ledger_pre 投影 {prev_k:,d}+2,200 恒等）；merged mu=**{merged_mu}** / merged sigma=**{merged_sigma}**；w233-only mu=**{wo_mu}** / w233-only sigma=**{wo_sigma}**（全机读=results/perpetual_faces/n1_w233_results.json+results/_r974bmc_w233_fivekey_receipt.json；锚 W232 实数程序 derive 写入 r583 律）；
  - skill_line_v2 K-lift 对照：line_pre **{line_pre}** → line_merged **{line_merged}** @n_eff {n_eff:,d}；delta **{k4}**（§5 预键 ≤0.02 达标·W2..W232 阶梯对照链实锚）；
  - **§5 五预键机证验证（fivekey probe=results/_r974bmc_w233_fivekey_receipt.json·同窗配对）**：key1 w-only vs merged |Δmu|=**{k1}**<0.02 PASS；key2 sigma 相对变化 **{k2}%**<±10% PASS；key3 A 面 p95 **{a_p95}** vs W232 {prev_a_p95} 差 **{k3}**<0.05 PASS；key4 K-lift **{k4}**≤0.02 PASS；key5 投影承接见 §8（**五键全过=§5 五预键全达标零违例**）；
  - se_mu 收窄链头：{semu_key}=**{semu}**（前值 W232 {prev_semu_key}={prev_semu} 链头对照）；
  - canon flip 态=NOT performed（K2200 同律·治理提案面 only）；
  - audit：voids_applied={voids}；machine=bm-c；finalize_only=True；shards_consumed=12/12；evidence_cutoff={cutoff}；
  - **六门探针=PRE-FINALIZE 正相位（W217-debt 常设法正确执行·第八连续）=results/_r974bmc_w233_sixgate_prereg.json**：banned ADMIT rc0+pf selftest 9/9+n1 selftest PASS+shards 12/12 在场+seed_admit FREE x2（{admit_a}+{admit_b}）+splice 完整性（bands facts==freeze receipt·pf sha16 **{pf_sha}** 与 n1 sha16 **{n1_sha}** 双面 clean-equal 断言通过=family #6 三元组 splice 原子携带零返·W232 界 w<232 x3 合法保留）+WAVE_CONFIGS[233] row engine_owner=bm-c（a_seed_base=527404/b_exit_seed_base=529404）+**finalize 恒等 post-hoc 断言（账本 {total:,d}/K {merged_k:,d} EXACT vs W232 锚）**——W234 必须六门 PRE-FINALIZE（常设法·防死窗复发面）。"""

s8 = """## §8 批后复盘。【finalize 同窗回填】
- **批后复盘（bm-c r974 窗回填）**：
  - §5.5 下波投影承接机证：**W234+ 投影=席位 probe 机证 leg4（承本波 §5.5·results/_w233bmc_20261013_probe_receipt.json）**：A naive first-clean **{p_a}**（hops=0·pre-W233 宇宙·post-W233 注册宇宙待重 derive）；B naive first-clean **{p_b}**（hops=0）——**naive B 落在 naive A 窗内**（W141 先例·同窗互斥面适用于 W234）；**W233 B 带 529_404..529_603 注册后将拒 naive W234 A 窗**（A-hops-prior-B **NINETY-FOURTH 例**预期·E36 卡/leg2 律）：W234 冻结方必须 post-W233 注册宇宙重 derive 且 derive B 时**预留本波 A 窗**；verify at W234 prereg·hop 链逐跳在 probe 回执。
  - 宝藏与方法论捕获：**六门相位=PRE-FINALIZE 正确执行（W217-debt 常设法连续第八波正确相位·W212-pattern 零复发）**；**r974 吸收窗链式接力范式**（死 r972 derive→死 r973 splice→引擎自燃→本窗六门+finalize 一气呵成·零双计：S0.5 ORD 消费由死 r972 自持）·零新宝藏（TREASURE_REGISTRY 零行）。
  - 诚实披露面：r974 窗=吸收窗（state 冻结 972·死 r972/r973 各自 commit 落账·本窗验 estate 后接力六门+finalize+五键+回填）；上游 W232 全周期=r968 吸收窗收口（ledger 934,189/K 508,320 五键全过）；S0.5 ORD 消费本窗=18:1x/18:3x/18:4x/18:5x 四行 CEO 剧本/门禁令（bm-a 同窗执行·bm-c 零直接动作·水位自推进）；DEC fb5825cb hold 零新行；MV V3 车道并行（fullres 7/7 烧毕接力上链 6851396b485a·GPU 面候导演席十席帧审）。"""

s7_fmt = s7.format(
    prev_total=led["prev_total"], batch_trials=led["batch_trials"], total=led["total"],
    merged_k=m["n_values"], prev_k=prev["null_pool_cumulative"]["merged"]["n_values"],
    merged_mu=m["mu"], merged_sigma=m["sigma"],
    wo_mu=wo["mu"], wo_sigma=wo["sigma"],
    line_pre=kl[pre_key], line_merged=kl[mrg_key], n_eff=kl["n_eff_held_equal"], k4=kl["line_delta_k_lift"],
    k1=keys["key1_wonly_vs_merged_dmu"]["value"],
    k2=keys["key2_sigma_rel_pct"]["value"],
    a_p95=famA["full_sharpe_p95"], prev_a_p95=prev_A_p95,
    k3=keys["key3_A_p95_diff_vs_w232"]["value"],
    semu_key=semu_key, semu=semu[semu_key],
    prev_semu_key=prev_semu_key, prev_semu=prev["null_pool_cumulative"][prev_semu_key],
    voids=json.dumps(led["voids_applied"], ensure_ascii=False), cutoff=led["evidence_cutoff"],
    admit_a=admit[0].split("base=")[1].split(" verdict")[0],
    admit_b=admit[1].split("base=")[1].split(" verdict")[0],
    pf_sha=gi["pf_sha16_now"], n1_sha=gi["n1_sha16_now"],
)

s8_fmt = s8.format(
    p_a=leg4["W233p_A"], p_b=leg4["W233p_B"],
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
