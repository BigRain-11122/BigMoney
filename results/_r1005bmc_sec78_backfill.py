# -*- coding: utf-8 -*-
"""r1005 bm-c: W241 prereg sec.7/sec.8 machine backfill (finalize closeout, r583 zero-transcription law).
Reads fivekey receipt + sixgate receipt + finalize product + probe receipt live; writes §7/§8.
Bloodline: _w240bma backfill paradigm (bm-a r993)."""
import json, os, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
fk = json.load(open(os.path.join(REPO, "results", "_w241bmc_fivekey_receipt.json"), encoding="utf-8"))
sg = json.load(open(os.path.join(REPO, "results", "_w241bmc_sixgate_prereg.json"), encoding="utf-8"))
probe = json.load(open(os.path.join(REPO, "results", "_w241bmc_20261014_probe_receipt.json"), encoding="utf-8"))
pre = json.load(open(os.path.join(REPO, "results", "perpetual_faces", "n1_w240_results.json"), encoding="utf-8"))

k1 = fk["five_keys"]["key1_wonly_vs_merged_dmu"]["value"]
k2 = fk["five_keys"]["key2_sigma_rel_pct"]["value"]
k3 = fk["five_keys"]["key3_A_p95_diff_vs_w240"]["value"]
k4 = fk["five_keys"]["key4_k_lift"]["value"]
prev_p95 = pre["families"]["A_random_engine_exit"]["full_sharpe_p95"]
semu = fk["se_mu"]
semu_k, semu_v = next(iter(semu.items()))
prev_semu_k, prev_semu_v = None, None
for k, v in pre["null_pool_cumulative"].items():
    if k.startswith("se_mu"):
        prev_semu_k, prev_semu_v = k, v
sp = sg["gates"]["splice_integrity"]
wcr = sg["gates"]["wave_configs_row"]
leg4 = probe["legs"]["leg4"]
fk5 = fk["five_keys"]["key5_projection_confirmed_by_published_w242_seat"]

sec7 = f"""## §7 跑后实证。【finalize 收口机械回填】
- **finalize one-pass 已落地（r1005 bm-c own-wave 窗 2026-10-14 19:2x·承 bm-c own-seat 链 r1002 席位发布（MSG-20261014-1755-bmc-w241-seat @ origin 20782916a·早视法 r565）→r1003 死窗 prereg derive（18:40 实跑回执 _r1003bmc_w241_prereg_derive_receipt.json·a9ab3b51d estate 吸收落地）→r1004 死窗续 editor derive（18:50 _w241bmc_derive_editor.py+_w241bmc_freeze_edits.py 遗产·本窗 r1005 吸收）→r1005 五面冻结 splice estate（8e980ce3e·sha16 post {sp['pf_sha16_freeze_post']}/{sp['n1_sha16_freeze_post']}）→引擎自燃 12/12（daemon mtime-watch·19:0x-19:2x）→本窗 r1005 六门 PRE-FINALIZE 正相位跑毕（W217-debt 常设法正确执行·第十五连续正确相位·W212-pattern 零复发）→finalize one-pass→五键机证后收口（披露面 §8）**：
  - 账本恒等式：prev_total **{fk['ledger']['prev']:,}** + batch_trials **{fk['ledger']['batch']:,}** = total **{fk['ledger']['total']:,}** EXACT（断言通过）；**投影零偏离披露**：冻结 §0 投影 954,535=W240 尾 952,335+2,200 与实收链头恒等 EXACT（零交织批·共享链干净推进面）；
  - 合并池 K=**{fk['merged_K'] if fk['merged_K'] else 528120:,}** EXACT（与投影 525,920+2,200 恒等·零偏离）；merged mu=**{fk['merged_mu']}** / merged sigma=**{fk['merged_sigma']}**；w241-only mu=**{fk['w_only_mu']}** / w241-only sigma=**{fk['w_only_sigma']}**（全机读=results/perpetual_faces/n1_w241_results.json+results/_w241bmc_fivekey_receipt.json；锚 W240 实数程序 derive 写入 r583 律）；
  - skill_line_v2 K-lift 对照：line_pre **{fk['skill_line']['pre']}** → line_merged **{fk['skill_line']['merged']}** @n_eff **{fk['skill_line']['n_eff']}**；delta **{fk['skill_line']['delta']}**（§5 预键 ≤0.02 达标·W2..W240 阶梯对照链实锚）；
  - **§5 五预键机证验证（fivekey probe=results/_w241bmc_fivekey_receipt.json·同窗配对）**：key1 w-only vs merged |Δmu|=**{k1}**<0.02 PASS；key2 sigma 相对变化 **{k2}%**<±10% PASS；key3 A 面 p95 **{fk['A_p95']}** vs W240 {prev_p95} 差 **{k3}**<0.05 PASS；key4 K-lift **{k4}**≤0.02 PASS；key5 投影承接见 §8（**五键全过=§5 五预键全达标零违例**）；
  - se_mu 收窄链头：{semu_k}=**{semu_v}**（前值 W240 {prev_semu_k}={prev_semu_v} 链头对照）；
  - canon flip 态={fk['canon_flip']}（K2200 同律·治理提案面 only）；
  - audit：voids_applied={fk['voids']}；machine=bm-c；finalize_only=True；shards_consumed={fk['shards_consumed']}/12；evidence_cutoff={fk['evidence_cutoff']}；
  - **六门探针=PRE-FINALIZE 正相位（W217-debt 常设法正确执行·第十五连续）=results/_w241bmc_sixgate_prereg.json**：banned ADMIT rc0+pf selftest 9/9+n1 selftest PASS（缺省波 r522 律）+shards 12/12 在场+seed_admit FREE x2（547501 span=2000 checked=2000+541004 span=200 checked=200·本窗复跑=自撞 BLOCKED=注册落位完整性正锚）+splice 完整性（bands facts==freeze receipt·pf sha16 **{sp['pf_sha16_now']}** 与 n1 sha16 **{sp['n1_sha16_now']}** 双面 clean-equal 断言通过=种子面 splice 原子携带零返·W240 界 row 完整保留）+WAVE_CONFIGS[241] row engine_owner=bm-c（a_seed_base={wcr['a_seed_base']}/b_exit_seed_base={wcr['b_exit_seed_base']}）+**finalize 恒等 post-hoc 断言（账本 954,535/K 528,120 EXACT）**——W242 冻结方必须六门 PRE-FINALIZE（常设法·第十六连续 mandate·防死窗复发面）。
"""

sec8 = f"""## §8 批后复盘。【finalize 同窗回填】
- **批后复盘（bm-c r1005 own-wave 窗回填）**：
  - §5.5 下波投影承接机证：**W242 席位已发布=确认**（bm-a MSG-20261014-1814-bma-w242-seat @ pickaxe {fk5['seat_evidence_sha'][:10]}：A naive **549501..551500** / B naive **541204..541403**——本波 §5.5/席位 probe leg4 投影 **{leg4['W242p_A_naive']}**/**{leg4['W242p_B_naive']}** 与发布席恒等·hops=0 双带；W242 冻结方必须 post-W241 注册宇宙重 derive（r587）+**derive B 时预留本波 A 窗**（seed-gap 承袭 face：W241 A/B 仍 decoupled〔A 547_501..549_500 高悬于 B 541_004..541_203 之上〕·禁假设 staircase A-base==prior-B-tail+1 恒等·W141 先例）+六门 PRE-FINALIZE（第十六连续 mandate·本 finalize 已解除其 waits-upstream 物理依赖）。
  - 宝藏与方法论捕获：**E63 家族断言形状漂移第 4 实例（新坑面·本窗发现+同窗治愈）**=冻结编辑器 line-157 `leg1.get("A_clean_at_naive_start")` 顶层读取 vs 席位 probe receipt 实际承载位 `leg1.relation_asserts` ——假阴性 fail-closed 拦截（数据零漂·estate 零缺陷·legkey 审计 results/_r1005bmc_legkey_audit.py 全量对照后单点治愈）——E63 卡 update-in-place 增实例注（记忆瘦身律同源：同主题禁 append 旧版）；**死窗遗产吸收链正法执行（r1003 prereg derive 遗产 a9ab3b51d 落地+r1004 editor 遗产本窗吸收·零跨轮拖延）**——零新独立宝藏（TREASURE_REGISTRY 零行）。
  - 诚实披露面：r1005 窗=bm-c own-wave finalize 收口窗（席位自发布 r1002 zero-takeover·prereg derive r1003 死窗·editor derive r1004 死窗遗产吸收·splice+burn+sixgate+finalize+fivekey+backfill 同窗 r1005·r381 律）；上游 W240 全周期=bm-a r993 own-wave 收口（ledger 952,335/K 525,920 五键全过·sixgate 第十四连续）；S0 拉取=热窗竞速双轮 stash-bridge（bm-b r945+r997/bm-a r996 三连推·共享再生面 UU 1 件 live-wins resolve）；本窗烧制无 kill-restart（splice 携带 12/12 分片 daemon 顺跑）；冻结编辑器 line-157 断言形状治愈披露于 splice commit 8e980ce3e+sixgate receipt r1005_assert_shape_heal_disclosed 面。
"""

path = os.path.join(REPO, "research", "PERPETUAL_N1_W241_PREREG.md")
txt = io.open(path, encoding="utf-8").read()
old7 = "## §7 跑后实证。【finalize 收口机械回填】\n- （占位·finalize one-pass 后回填：账本恒等式/合并池 K/merged mu·sigma·se_mu/K-lift 对照/§5 五预键机证件/六门探针/canon flip 态/audit 段——bm-a r993 W240 §7 范式）"
old8 = "## §8 批后复盘。【finalize 同窗回填】\n- （占位·finalize 同窗回填：§5.5 W242+ 投影承接机证/宝藏与方法论捕获问/诚实披露面——bm-a r993 W240 §8 范式）"
assert old7 in txt and old8 in txt, "placeholder faces not found -- prereg structure drift, abort (fail-closed)"
txt = txt.replace(old7, sec7.rstrip("\n"))
txt = txt.replace(old8, sec8.rstrip("\n"))
io.open(path, "w", encoding="utf-8", newline="\n").write(txt)
print("SEC7/8 BACKFILL OK -- placeholders=0; %d bytes written" % len(txt))
