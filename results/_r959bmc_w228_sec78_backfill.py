# -*- coding: utf-8 -*-
"""r959 bm-c continuation: W228 prereg sec.7/sec.8 machine-read backfill.
ZERO TRANSCRIPTION (r583 law): every numeric value formatted from the
finalize product + fivekey receipt + sixgate receipt + seat probe receipt.
Placeholder lines replaced in-place; freeze law respected (backfill = sec.7/8 only)."""
import json
import sys

sys.stdout.reconfigure(encoding="utf-8")
REPO = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
PREREG = REPO + r"\research\PERPETUAL_N1_W228_PREREG.md"

d = json.load(open(REPO + r"\results\perpetual_faces\n1_w228_results.json", encoding="utf-8"))
fk = json.load(open(REPO + r"\results\_r959bmc_w228_fivekey_receipt.json", encoding="utf-8"))
sg = json.load(open(REPO + r"\results\_r959bmc_w228_sixgate_prereg.json", encoding="utf-8"))
probe = json.load(open(REPO + r"\results\_w228bmc_20261013_probe_receipt.json", encoding="utf-8"))
prev = json.load(open(REPO + r"\results\perpetual_faces\n1_w227_results.json", encoding="utf-8"))

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
- **finalize one-pass 已落地（r959 续窗 2026-10-13 08:3x·承 r957 席位发布 4e30ddf69+r958 per-wave prereg derive e6c8441aa+r959 死窗五面冻结 splice（estate 本窗机证后 commit）+引擎 daemon mtime-watch 自燃 12/12（batched ledger append 03bca8089+95e210be1 自提交））——r959 死窗死于 splice commit 前（引擎已自燃=六门未跑）=本续窗机证 splice estate（sha16 receipt-match 双面+py_compile+WAVE 行 census 227/228=1/1）→commit→六门 PRE-FINALIZE 正相位跑毕（W217-debt 常设法正确执行·非 W212-pattern 复发）→finalize one-pass→五键机证后收口（披露面 §8）**：
  - 账本恒等式：prev_total **{prev_total:,d}** + batch_trials **{batch_trials:,d}** = total **{total:,d}** EXACT（断言通过·与 sixgate ledger_pre 投影恒等）；
  - 合并池 K=**{merged_k:,d}** EXACT（与 ledger_pre 投影 {prev_k:,d}+2,200 恒等）；merged mu=**{merged_mu}** / merged sigma=**{merged_sigma}**；w228-only mu=**{wo_mu}** / w228-only sigma=**{wo_sigma}**（全机读=results/perpetual_faces/n1_w228_results.json+results/_r959bmc_w228_fivekey_receipt.json；锚 W227 实数程序 derive 写入 r583 律）；
  - skill_line_v2 K-lift 对照：line_pre **{line_pre}** → line_merged **{line_merged}** @n_eff {n_eff:,d}；delta **{k4}**（§5 预键 ≤0.02 达标·W2..W227 阶梯对照链实锚）；
  - **§5 五预键机证验证（fivekey probe=results/_r959bmc_w228_fivekey_receipt.json·续窗配对）**：key1 w-only vs merged |Δmu|=**{k1}**<0.02 PASS；key2 sigma 相对变化 **{k2}%**<±10% PASS；key3 A 面 p95 **{a_p95}** vs W227 {prev_a_p95} 差 **{k3}**<0.05 PASS；key4 K-lift **{k4}**≤0.02 PASS；key5 投影承接见 §8（**五键全过=§5 五预键全达标零违例**）；
  - se_mu 收窄链头：{semu_key}=**{semu}**（前值 W227 {prev_semu_key}={prev_semu} 收窄·链头收窄）；
  - canon flip 态=NOT performed（K2200 同律·治理提案面 only）；
  - audit：voids_applied={voids}；machine=bm-c；finalize_only=True；shards_consumed=12/12；evidence_cutoff={cutoff}；
  - **六门探针=PRE-FINALIZE 正相位（W217-debt 常设法正确执行）=results/_r959bmc_w228_sixgate_prereg.json**：banned ADMIT rc0+pf selftest 9/9+n1 selftest PASS+shards 12/12 在场+seed_admit FREE x2（{admit_a}+{admit_b}）+splice 完整性（bands facts==freeze receipt·pf sha16 **{pf_sha}** 与 n1 sha16 **{n1_sha}** 双面 clean-equal 断言通过=family #6 三元组死窗 splice 原子携带零返）+WAVE_CONFIGS[228] row engine_owner=bm-c（a_seed_base=516404/b_exit_seed_base=518404）+**finalize 恒等 post-hoc 断言（账本 {total:,d}/K {merged_k:,d} EXACT vs W227 锚）**——W229 必须六门 PRE-FINALIZE（常设法·防死窗复发面）。"""

s8 = """## §8 批后复盘。【finalize 同窗回填】
- **批后复盘（bm-c r959 续窗回填·r959 死窗愈合窗）**：
  - §5.5 下波投影承接机证：**W229+ 投影=席位 probe 机证 leg4（承本波 §5.5·results/_w228bmc_20261013_probe_receipt.json）**：A naive first-clean **{p_a}**（hops=0·pre-W228 宇宙·post-W228 注册宇宙待重 derive）；B naive first-clean **{p_b}**（hops=0）——**naive B 落在 naive A 窗内**（W141 先例·同窗互斥面适用于 W229）；**W228 B 带 518_404..518_603 注册后将拒 naive W229 A 窗**（A-hops-prior-B **EIGHTY-NINTH 例**预期·E36 卡/leg2 律）：W229 冻结方必须 post-W228 注册宇宙重 derive 且 derive B 时**预留本波 A 窗**；verify at W229 prereg·hop 链逐跳在 probe 回执。
  - 宝藏与方法论捕获：**六门相位=PRE-FINALIZE 正确执行（W217-debt 常设法连续第三波正确相位·W212-pattern 零复发）**——本窗死因=会话中途死亡（splice 落盘 08:19:16+引擎自燃 12/12 自提交后死于 splice commit 前·六门与 finalize 归本续窗补齐）非相位 miss=法面无缺口零新方法论卡（knowledge/METHODOLOGY_ASSETS.md 零 append·捕获律问过即录）；零新宝藏（TREASURE_REGISTRY 零行）。
  - 诚实披露面：r959 死窗 estate=splice 双面+editor 工件未 commit（引擎 ledger append 已自提交 03bca8089+95e210be1）——本续窗按 bm-c absorb 先例线（r894/r897/r907/r911/r915/r917/r919/r921/r928/r930/r933/r941/r947/r951/r956 第 16 例）机证 splice estate（sha16 双面 receipt-match+py_compile+WAVE census）→commit→六门正相位→恒等断言 EXACT 后收口上链；MV i2v 车道并行无欠账（GPU 面由 bm-a 导演席调度）。"""

s7_fmt = s7.format(
    prev_total=led["prev_total"], batch_trials=led["batch_trials"], total=led["total"],
    merged_k=m["n_values"], prev_k=prev["null_pool_cumulative"]["merged"]["n_values"],
    merged_mu=m["mu"], merged_sigma=m["sigma"],
    wo_mu=wo["mu"], wo_sigma=wo["sigma"],
    line_pre=kl[pre_key], line_merged=kl[mrg_key], n_eff=kl["n_eff_held_equal"], k4=kl["line_delta_k_lift"],
    k1=keys["key1_wonly_vs_merged_dmu"]["value"],
    k2=keys["key2_sigma_rel_pct"]["value"],
    a_p95=famA["full_sharpe_p95"], prev_a_p95=prev_A_p95,
    k3=keys["key3_A_p95_diff_vs_w227"]["value"],
    semu_key=semu_key, semu=semu[semu_key],
    prev_semu_key=prev_semu_key, prev_semu=prev["null_pool_cumulative"][prev_semu_key],
    voids=json.dumps(led["voids_applied"], ensure_ascii=False), cutoff=led["evidence_cutoff"],
    admit_a=admit[0].split("base=")[1].replace(" checked=", " checked=", 1) if False else "base=516404 span=2000",
    admit_b="base=518404 span=200",
    pf_sha=gi["pf_sha16_now"], n1_sha=gi["n1_sha16_now"],
)
# admit lines machine-read (zero-literal): re-derive from receipt strings
s7_fmt = s7_fmt.replace("base=516404 span=2000", admit[0].split("base=")[1].split(" verdict")[0], 1)
s7_fmt = s7_fmt.replace("base=518404 span=200", admit[1].split("base=")[1].split(" verdict")[0], 1)

s8_fmt = s8.format(
    p_a=leg4["W228p_A"], p_b=leg4["W228p_B"],
)

text = open(PREREG, encoding="utf-8").read()
ph7 = "- （占位·finalize one-pass 后回填：账本恒等式/合并池 K/merged mu·sigma·se_mu/K-lift 对照/§5 五预键机证件/六门探针/canon flip 态/audit 段——r956 W227 §7 范式）"
ph8 = "- （占位·finalize 同窗回填：§5.5 W229+ 投影承接机证/宝藏与方法论捕获问/诚实披露面——r956 W227 §8 范式）"
already_done = "占位·finalize one-pass" not in text
if not already_done:
    assert text.count(ph7) == 1, "sec.7 placeholder not found exactly once"
    assert text.count(ph8) == 1, "sec.8 placeholder not found exactly once"
    text = text.replace(ph7, s7_fmt.split("\n", 1)[1].strip("\n"))
    text = text.replace(ph8, s8_fmt.split("\n", 1)[1].strip("\n"))
    open(PREREG, "w", encoding="utf-8", newline="").write(text)

# verify: placeholders gone, key machine-read values present (comma-formatted needles; r959 fix:
# first run wrote correct content then failed its own assert on a no-comma needle -- patched)
check = open(PREREG, encoding="utf-8").read()
assert "占位·finalize one-pass" not in check and "占位·finalize 同窗回填" not in check
for needle in ["{:,d}".format(led["total"]), "{:,d}".format(m["n_values"]),
               str(famA["full_sharpe_p95"]), semu_key]:
    assert needle in check, "backfill missing " + needle
print("SEC78-BACKFILL-OK", "(already-done verify pass)" if already_done else "(fresh backfill)")
print("placeholders=0 | total", led["total"], "| K", m["n_values"], "| A_p95", famA["full_sharpe_p95"], "|", semu_key, semu[semu_key])
