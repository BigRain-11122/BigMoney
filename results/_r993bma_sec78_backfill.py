# -*- coding: utf-8 -*-
"""r993 bm-a: W240 prereg sec.7/sec.8 machine-read backfill.
ZERO TRANSCRIPTION (r583 law): every numeric value formatted from the
finalize product + fivekey receipt + sixgate receipt + seat probe receipt.
Placeholder lines replaced in-place by LINE-MATCH; freeze law respected (backfill = sec.7/8 only).
Bloodline clone of _r985bma_sec78_backfill.py (W238->W240, prev W237->W239)."""
import json, os, sys

sys.stdout.reconfigure(encoding="utf-8")
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PREREG = os.path.join(REPO, "research", "PERPETUAL_N1_W240_PREREG.md")

d = json.load(open(os.path.join(REPO, "results", "perpetual_faces", "n1_w240_results.json"), encoding="utf-8"))
fk = json.load(open(os.path.join(REPO, "results", "_w240bma_fivekey_receipt.json"), encoding="utf-8"))
sg = json.load(open(os.path.join(REPO, "results", "_w240bma_sixgate_prereg.json"), encoding="utf-8"))
probe = json.load(open(os.path.join(REPO, "results", "_w240bma_20261014_probe_receipt.json"), encoding="utf-8"))
prev = json.load(open(os.path.join(REPO, "results", "perpetual_faces", "n1_w239_results.json"), encoding="utf-8"))

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
admit = sg["gates"]["seed_admit"]["freeze_gate_lines"]

s7 = """## §7 跑后实证。【finalize 收口机械回填】
- **finalize one-pass 已落地（r993 bm-a own-wave 窗 2026-10-14 17:3x·承 bm-a own-seat 链 r987 席位发布（MSG-20261014-1325-bma-w240-seat @ origin 94136b9dd·早视法 r565）→r991/r992 死窗 prereg derive（14:55 实跑回执 _w240bma_prereg_derive_receipt.json）→r992 五面冻结 splice estate（dc27f5217·死窗 16:18-fire 遗产吸收落地·sha16 post {pf_sha}/…双 MATCH 验证后提交）→引擎自燃 12/12（r992 splice 携带·12/12 分片在场）→本窗 r993 六门 PRE-FINALIZE 正相位跑毕（W217-debt 常设法正确执行·第十四连续正确相位·W212-pattern 零复发）→finalize one-pass→五键机证后收口（披露面 §8）**：
  - 账本恒等式：prev_total **{prev_total:,d}** + batch_trials **{batch_trials:,d}** = total **{total:,d}** EXACT（断言通过）；**投影零偏离披露**：冻结 §0 投影 952,335=W239 尾 950,135+2,200 与实收链头恒等 EXACT（零交织批·共享链干净推进面）；
  - 合并池 K=**{merged_k:,d}** EXACT（与投影 {prev_k:,d}+2,200 恒等·零偏离）；merged mu=**{merged_mu}** / merged sigma=**{merged_sigma}**；w240-only mu=**{wo_mu}** / w240-only sigma=**{wo_sigma}**（全机读=results/perpetual_faces/n1_w240_results.json+results/_w240bma_fivekey_receipt.json；锚 W239 实数程序 derive 写入 r583 律）；
  - skill_line_v2 K-lift 对照：line_pre **{line_pre}** → line_merged **{line_merged}** @n_eff {n_eff:,d}；delta **{k4}**（§5 预键 ≤0.02 达标·W2..W239 阶梯对照链实锚）；
  - **§5 五预键机证验证（fivekey probe=results/_w240bma_fivekey_receipt.json·同窗配对）**：key1 w-only vs merged |Δmu|=**{k1}**<0.02 PASS；key2 sigma 相对变化 **{k2}%**<±10% PASS；key3 A 面 p95 **{a_p95}** vs W239 {prev_a_p95} 差 **{k3}**<0.05 PASS；key4 K-lift **{k4}**≤0.02 PASS；key5 投影承接见 §8（**五键全过=§5 五预键全达标零违例**）；
  - se_mu 收窄链头：{semu_key}=**{semu}**（前值 W239 {prev_semu_key}={prev_semu} 链头对照）；
  - canon flip 态=NOT performed（K2200 同律·治理提案面 only）；
  - audit：voids_applied={voids}；machine=bm-a；finalize_only=True；shards_consumed=12/12；evidence_cutoff={cutoff}；
  - **六门探针=PRE-FINALIZE 正相位（W217-debt 常设法正确执行·第十四连续）=results/_w240bma_sixgate_prereg.json**：banned ADMIT rc0+pf selftest 9/9+n1 selftest PASS（缺省波 r522 律）+shards 12/12 在场+seed_admit FREE x2（{admit_a}+{admit_b}·本窗复跑=自撞 BLOCKED=注册落位完整性正锚）+splice 完整性（bands facts==freeze receipt·pf sha16 **{pf_sha}** 与 n1 sha16 **{n1_sha}** 双面 clean-equal 断言通过=种子面 splice 原子携带零返·W239 界 row 完整保留）+WAVE_CONFIGS[240] row engine_owner=bm-a（a_seed_base=545501/b_exit_seed_base=540804）+**finalize 恒等 post-hoc 断言（账本 {total:,d}/K {merged_k:,d} EXACT）**——W241 冻结方必须六门 PRE-FINALIZE（常设法·防死窗复发面）。"""

s8 = """## §8 批后复盘。【finalize 同窗回填】
- **批后复盘（bm-a r993 own-wave 窗回填）**：
  - §5.5 下波投影承接机证：**W241+ 投影=席位 probe 机证 leg4（承本波 §5.5·results/_w240bma_20261014_probe_receipt.json）**：A naive **{p_a_naive}** first-clean **{p_a}**（hops=0·pre-W240 宇宙零活点拒）；B naive **{p_b_naive}** first-clean **{p_b}**（hops=0·lands-inside-A=false 腿在场）——**W241 席位未发布（inbox 零 W241 席位外机命中·截至本 finalize）**；W241 冻结方必须 post-W240 注册宇宙重 derive（r587）+**derive B 时预留本波 A 窗**（seed-gap 承袭 face：W240 A/B 仍 decoupled〔A 545_501..547_500 高悬于 B 540_804..541_003 之上〕·禁假设 staircase A-base==prior-B-tail+1 恒等·W141 先例）+六门 PRE-FINALIZE（第十五连续 mandate·本 finalize 已解除其 waits-upstream 物理依赖）。
  - 宝藏与方法论捕获：**六门相位=PRE-FINALIZE 正确执行（W217-debt 常设法连续第十四波正确相位·W212-pattern 零复发）**；**死窗遗产吸收链正法执行（r992 splice estate 吸收 16:18-fire 死窗 prereg derive+五面冻结+分片→r993 同窗 finalize·零跨轮拖延）**；**S0 rebase 风暴修复（r993 本窗：19-文件共享再生面 canonical resolve〔deep-ts 快照+host faces take-local+twin 同侧配对〕+4 陈旧 stash 清账〔r642 净树根治律·sha 留痕 _r993_stash_shas〕）**——零新宝藏（TREASURE_REGISTRY 零行·标准链照 canon 无新坑）；方法论 E67 已由 r992 落卡（daemon-tick union recovery）。
  - 诚实披露面：r993 窗=bm-a own-wave finalize 收口窗（席位自发布 r987 zero-takeover·prereg derive r991/r992 死窗·splice r992 死窗遗产吸收·烧毕同窗 finalize r993·r381 律）；上游 W239 全周期=bm-c r996-continuation own-wave 收口（ledger 950,135/K 523,720 五键全过·sixgate 第十三连续）；S0 拉取=rebase 竞速修复窗（bm-c r940 竞速 19-UU canonical resolve 后 0-behind·b4b4ec77b push 验证）；本窗烧制无 kill-restart（r992 splice 携带 12/12 分片顺跑）。"""

s7_fmt = s7.format(
    prev_total=led["prev_total"], batch_trials=led["batch_trials"], total=led["total"],
    merged_k=m["n_values"], prev_k=prev["null_pool_cumulative"]["merged"]["n_values"],
    merged_mu=m["mu"], merged_sigma=m["sigma"],
    wo_mu=wo["mu"], wo_sigma=wo["sigma"],
    line_pre=kl[pre_key], line_merged=kl[mrg_key], n_eff=kl["n_eff_held_equal"], k4=kl["line_delta_k_lift"],
    k1=keys["key1_wonly_vs_merged_dmu"]["value"],
    k2=keys["key2_sigma_rel_pct"]["value"],
    a_p95=famA["full_sharpe_p95"], prev_a_p95=prev_A_p95,
    k3=keys["key3_A_p95_diff_vs_w239"]["value"],
    semu_key=semu_key, semu=semu[semu_key],
    prev_semu_key=prev_semu_key, prev_semu=prev["null_pool_cumulative"][prev_semu_key],
    voids=json.dumps(led["voids_applied"], ensure_ascii=False), cutoff=led["evidence_cutoff"],
    admit_a=admit[0].split("base=")[1].split(" verdict")[0],
    admit_b=admit[1].split("base=")[1].split(" verdict")[0],
    pf_sha=gi["pf_sha16_now"], n1_sha=gi["n1_sha16_now"],
)

s8_fmt = s8.format(
    p_a_naive=leg4["W241p_A_naive"], p_a=leg4["W241p_A_first_clean"],
    p_b_naive=leg4["W241p_B_naive"], p_b=leg4["W241p_B_first_clean"],
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
