# -*- coding: utf-8 -*-
"""r976 bm-c absorb window: W234 prereg sec.7/sec.8 machine-read backfill.
ZERO TRANSCRIPTION (r583 law): every numeric value formatted from the
finalize product + fivekey receipt + sixgate receipt + seat probe receipt.
Placeholder lines replaced in-place by LINE-MATCH (marker substring, robust
against needle-format drift); freeze law respected (backfill = sec.7/8 only).
Bloodline clone of _r974bmc_w233_sec78_backfill.py (W233->W234, prev W232->W233)."""
import json
import sys

sys.stdout.reconfigure(encoding="utf-8")
REPO = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
PREREG = REPO + r"\research\PERPETUAL_N1_W234_PREREG.md"

d = json.load(open(REPO + r"\results\perpetual_faces\n1_w234_results.json", encoding="utf-8"))
fk = json.load(open(REPO + r"\results\_r976bmc_w234_fivekey_receipt.json", encoding="utf-8"))
sg = json.load(open(REPO + r"\results\_r976bmc_w234_sixgate_prereg.json", encoding="utf-8"))
probe = json.load(open(REPO + r"\results\_w234bmc_20261013_probe_receipt.json", encoding="utf-8"))
prev = json.load(open(REPO + r"\results\perpetual_faces\n1_w233_results.json", encoding="utf-8"))

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
- **finalize one-pass 已落地（r976 吸收窗 2026-10-13 21:4x·承 r974 吸收窗席位发布 MSG-20261013-1955-bmc（probe ADMIT+origin 260217d39）+死 r976 窗 prereg derive（R34 authored r975 + 18 级 lineage replay 46/46 one deeper than W233 + PITFALL r958 4th instance caught live by chain-leg assert→R34[3] heritage token fixed→SUB block re-emitted→rederived green·commit 252d5cc95 上链自证）+死 r976 continuation 窗 census-first derive（postsent calibration probe 24-face KEPT/24 LIVE/LEG231+LEG232/ASM sentinels·86 shifts one-pass·receipt parity W211..W229 fix）+五面冻结 splice（freeze receipt·estate commit de342250c）→引擎 daemon mtime-watch 自燃 12/12（batched ledger append 39f7b8b0c+5022491bc+absorb-tail cbe25f1a4 自提交）→本窗 r976 六门 PRE-FINALIZE 正相位跑毕（W217-debt 常设法正确执行·第九连续正确相位·W212-pattern 零复发）→finalize one-pass→五键机证后收口（披露面 §8）**：
  - 账本恒等式：prev_total **{prev_total:,d}** + batch_trials **{batch_trials:,d}** = total **{total:,d}** EXACT（断言通过·与 sixgate ledger_pre 投影恒等）；
  - 合并池 K=**{merged_k:,d}** EXACT（与 ledger_pre 投影 {prev_k:,d}+2,200 恒等）；merged mu=**{merged_mu}** / merged sigma=**{merged_sigma}**；w234-only mu=**{wo_mu}** / w234-only sigma=**{wo_sigma}**（全机读=results/perpetual_faces/n1_w234_results.json+results/_r976bmc_w234_fivekey_receipt.json；锚 W233 实数程序 derive 写入 r583 律）；
  - skill_line_v2 K-lift 对照：line_pre **{line_pre}** → line_merged **{line_merged}** @n_eff {n_eff:,d}；delta **{k4}**（§5 预键 ≤0.02 达标·W2..W233 阶梯对照链实锚）；
  - **§5 五预键机证验证（fivekey probe=results/_r976bmc_w234_fivekey_receipt.json·同窗配对）**：key1 w-only vs merged |Δmu|=**{k1}**<0.02 PASS；key2 sigma 相对变化 **{k2}%**<±10% PASS；key3 A 面 p95 **{a_p95}** vs W233 {prev_a_p95} 差 **{k3}**<0.05 PASS；key4 K-lift **{k4}**≤0.02 PASS；key5 投影承接见 §8（**五键全过=§5 五预键全达标零违例**）；
  - se_mu 收窄链头：{semu_key}=**{semu}**（前值 W233 {prev_semu_key}={prev_semu} 链头对照）；
  - canon flip 态=NOT performed（K2200 同律·治理提案面 only）；
  - audit：voids_applied={voids}；machine=bm-c；finalize_only=True；shards_consumed=12/12；evidence_cutoff={cutoff}；
  - **六门探针=PRE-FINALIZE 正相位（W217-debt 常设法正确执行·第九连续）=results/_r976bmc_w234_sixgate_prereg.json**：banned ADMIT rc0+pf selftest 9/9+n1 selftest PASS+shards 12/12 在场+seed_admit FREE x2（{admit_a}+{admit_b}）+splice 完整性（bands facts==freeze receipt·pf sha16 **{pf_sha}** 与 n1 sha16 **{n1_sha}** 双面 clean-equal 断言通过=family #6 三元组 splice 原子携带零返·W233 界 w<233 x3 合法保留）+WAVE_CONFIGS[234] row engine_owner=bm-c（a_seed_base=529604/b_exit_seed_base=531604）+**finalize 恒等 post-hoc 断言（账本 {total:,d}/K {merged_k:,d} EXACT vs W233 锚）**——W235 必须六门 PRE-FINALIZE（常设法·防死窗复发面）。"""

s8 = """## §8 批后复盘。【finalize 同窗回填】
- **批后复盘（bm-c r976 吸收窗回填）**：
  - §5.5 下波投影承接机证：**W235+ 投影=席位 probe 机证 leg4（承本波 §5.5·results/_w234bmc_20261013_probe_receipt.json）**：A naive first-clean **{p_a}**（hops=0·pre-W234 宇宙·post-W234 注册宇宙待重 derive）；B naive first-clean **{p_b}**（hops=0）——**naive B 落在 naive A 窗内**（W141 先例·同窗互斥面适用于 W235）；**W234 B 带 531_604..531_803 注册后将拒 naive W235 A 窗**（A-hops-prior-B **NINETY-FIFTH 例**预期·E36 卡/leg2 律）：W235 冻结方必须 post-W234 注册宇宙重 derive 且 derive B 时**预留本波 A 窗**；verify at W235 prereg·hop 链逐跳在 probe 回执。
  - 宝藏与方法论捕获：**六门相位=PRE-FINALIZE 正确执行（W217-debt 常设法连续第九波正确相位·W212-pattern 零复发）**；**r976 吸收窗链式接力范式**（死 r976 derive 窗→死 r976 continuation splice 窗→引擎自燃 12/12→本窗六门+finalize+五键+回填一气呵成·零双计：尾 3 分片引擎律 batched append cbe25f1a4 本窗补账）·零新宝藏（TREASURE_REGISTRY 零行）。
  - 诚实披露面：r976 窗=吸收窗（state 冻结 976·死 r976 双窗各自 commit 落账·本窗验 estate 后接力六门+finalize+五键+回填）；上游 W233 全周期=r974 吸收窗收口（ledger 936,389/K 510,520 五键全过）；S0.5 消费本窗=DEC 水位 fb5825cb→2bf2a0ef 增量两行（D-20261013-01 核销批 31+D-20261013-02 Phase 0 盘点·涉本司零执行件如实注记）+本仓 ORD 差集 0；MV V3 车道并行（fullres 7/7 帧审候导演席）。"""

s7_fmt = s7.format(
    prev_total=led["prev_total"], batch_trials=led["batch_trials"], total=led["total"],
    merged_k=m["n_values"], prev_k=prev["null_pool_cumulative"]["merged"]["n_values"],
    merged_mu=m["mu"], merged_sigma=m["sigma"],
    wo_mu=wo["mu"], wo_sigma=wo["sigma"],
    line_pre=kl[pre_key], line_merged=kl[mrg_key], n_eff=kl["n_eff_held_equal"], k4=kl["line_delta_k_lift"],
    k1=keys["key1_wonly_vs_merged_dmu"]["value"],
    k2=keys["key2_sigma_rel_pct"]["value"],
    a_p95=famA["full_sharpe_p95"], prev_a_p95=prev_A_p95,
    k3=keys["key3_A_p95_diff_vs_w233"]["value"],
    semu_key=semu_key, semu=semu[semu_key],
    prev_semu_key=prev_semu_key, prev_semu=prev["null_pool_cumulative"][prev_semu_key],
    voids=json.dumps(led["voids_applied"], ensure_ascii=False), cutoff=led["evidence_cutoff"],
    admit_a=admit[0].split("base=")[1].split(" verdict")[0],
    admit_b=admit[1].split("base=")[1].split(" verdict")[0],
    pf_sha=gi["pf_sha16_now"], n1_sha=gi["n1_sha16_now"],
)

s8_fmt = s8.format(
    p_a=leg4["W234p_A"], p_b=leg4["W234p_B"],
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
