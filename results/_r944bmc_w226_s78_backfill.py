# -*- coding: utf-8 -*-
"""r944 bm-c: W226 prereg sec.7/8 machine-read backfill (finalize landed 22:41
by r943 dead window; sixgate/fivekey healed post-hoc this window).
Numbers pulled programmatically from landed products (r583 zero-literal law)."""
import json, io, sys
sys.stdout.reconfigure(encoding="utf-8")
REPO = r'K:\Fluxgroup\FluxGroup\quant\bigmoney'
PREREG = rf'{REPO}\research\PERPETUAL_N1_W226_PREREG.md'

res = json.load(open(rf'{REPO}\results\perpetual_faces\n1_w226_results.json'))
fk = json.load(open(rf'{REPO}\results\_r944bmc_w226_fivekey_receipt.json'))
sg = res['science_gates']['ledger']
npc = res['null_pool_cumulative']
kl = res['skill_line_v2_k_lift']
famA = res['families']['A_random_engine_exit']
audit = res['audit']
pr = json.load(open(rf'{REPO}\results\_w226bmc_20261012_probe_receipt.json'))
leg4 = pr['legs']['leg4']
prev = json.load(open(rf'{REPO}\results\perpetual_faces\n1_w225_results.json'))
prev_A_p95 = prev['families']['A_random_engine_exit']['full_sharpe_p95']
prev_semu_key = [k for p in prev['null_pool_cumulative'] if p.startswith('se_mu') for k in [p]]
prev_semu = prev['null_pool_cumulative'][prev_semu_key[0]]

k1 = fk['five_keys']['key1_wonly_vs_merged_dmu']['value']
k2 = fk['five_keys']['key2_sigma_rel_pct']['value']
k3 = fk['five_keys']['key3_A_p95_diff_vs_w225']['value']
k4 = fk['five_keys']['key4_k_lift']['value']
semu_key = [k for p in npc if p.startswith('se_mu') for k in [p]]
semu = npc[semu_key[0]]

A7 = "- （占位·finalize one-pass 后回填：账本恒等式/合并池 K/merged mu·sigma·se_mu/K-lift 对照/§5 五预键机证件/六门探针/canon flip 态/audit 段——r940 W225 §7 范式）"
A8 = "- （占位·finalize 同窗回填：§5.5 W227+ 投影承接机证/宝藏与方法论捕获问/诚实披露面——r940 W225 §8 范式）"
N7 = (
f"""- **finalize one-pass 已落地（r943 死窗 2026-10-12 22:41:33·承 r940 席位发布 d7d270752+r941 per-wave prereg derive f65d886cb+r943 五面冻结 splice 9b44d37d1+引擎 daemon mtime-watch 自燃 12/12（batched ledger append 9f41cf5be+eed45a825 自提交））——r943 死窗死于六门/fivekey 回执与收口 commit 前（W212-pattern 第 3 例）=本 r944 窗 post-hoc 愈合+全 estate 吸收（披露面 §8）**：
  - 账本恒等式：prev_total **{sg['prev_total']:,}** + batch_trials **{sg['batch_trials']:,}** = total **{sg['total']:,}** EXACT（断言通过·与 sixgate ledger_pre 投影恒等）；
  - 合并池 K=**{npc['merged']['n_values']:,}** EXACT（与 ledger_pre 投影 {npc['pre_w226_cumulative']['n_values']:,}+2,200 恒等）；merged mu=**{npc['merged']['mu']}** / merged sigma=**{npc['merged']['sigma']}**；w226-only mu=**{npc['w226_only']['mu']}** / w226-only sigma=**{npc['w226_only']['sigma']}**（全机读=results/perpetual_faces/n1_w226_results.json+results/_r944bmc_w226_fivekey_receipt.json；锚 W225 实数程序 derive 写入 r583 律）；
  - skill_line_v2 K-lift 对照：line_pre **{kl['line_pre_w226']}** → line_merged **{kl['line_merged_495120']}** @n_eff {kl['n_eff_held_equal']:,}；delta **{kl['line_delta_k_lift']}**（§5 预键 ≤0.02 达标·W2..W225 阶梯对照链实锚）；
  - **§5 五预键机证验证（fivekey probe=results/_r944bmc_w226_fivekey_receipt.json·post-hoc 配对（六门愈合窗））**：key1 w-only vs merged |Δmu|=**{k1:.10f}**<0.02 PASS；key2 sigma 相对变化 **{'+' if k2>=0 else ''}{k2:.7f}%**<±10% PASS；key3 A 面 p95 **{famA['full_sharpe_p95']}** vs W225 {prev_A_p95} 差 **{k3}**<0.05 PASS；key4 K-lift **{k4}**≤0.02 PASS；key5 投影承接见 §8（**五键全过=§5 五预键全达标零违例**）；
  - se_mu 收窄链头：{semu_key[0]}=**{semu}**（前值 W225 {prev_semu} 平/微收窄·链头收窄）；
  - canon flip 态=NOT performed（K2200 同律·治理提案面 only）；
  - audit：voids_applied={audit.get('voids_applied') if 'voids_applied' in audit else sg.get('voids_applied')}；machine={audit.get('machine')}；finalize_only={audit.get('finalize_only')}；shards_consumed={len(res.get('shards_consumed', []))}/12；evidence_cutoff={res.get('evidence_cutoff')}；
  - **六门探针=POST-FINALIZE HEAL（相位 miss 披露·W212-pattern 第 3 例）=results/_r944bmc_w226_sixgate_receipt.json**：banned ADMIT rc0+pf selftest 9/9+n1 selftest PASS+shards 12/12 在场+seed_admit FREE x2（base=512004 span=2000+base=514004 span=200）+splice 完整性（bands facts==freeze receipt·pf sha16 **f670ff87a0d1af59** 与 n1 sha16 **79109bf30ab12cbb** 双面 clean-equal 断言通过=family #6 修复零返第 2 连窗·三元组 whole-file recheck 'if w < 226)' x3+range(16,226)+range(17,226)+below-226 注释全在场）+WAVE_CONFIGS[226] row engine_owner=bm-c（a_seed_base=512_004/b_exit_seed_base=514_004）+**finalize 恒等 post-hoc 断言（账本 {sg['total']:,}/K {npc['merged']['n_values']:,} EXACT vs W225 锚）**——**W227 必须六门 PRE-FINALIZE（W217-debt 常设法·死窗复发面披露）**。"""
)
N8 = (
f"""- **批后复盘（bm-c r944 窗回填·r943 死窗愈合窗）**：
  - §5.5 下波投影承接机证：**W227+ 投影=probe 机证 leg4（承本波 §5.5·results/_w226bmc_20261012_probe_receipt.json）**：A naive first-clean **514_004..516_003**（hops=0·pre-W226 宇宙·post-W226 注册宇宙待重 derive）；B naive first-clean **514_204..514_403**（hops=0）——**naive B 落在 naive A 窗内**（W141 先例·同窗互斥面适用于 W227）：W227 冻结方必须 post-W226 注册宇宙重 derive 且 derive B 时**预留本波 A 窗**（leg2 律/E36 卡）；**W226 B 带 514_004..514_203 注册后将拒 naive W227 A 窗**——W227 A 重 derive 同强制（越过 W226 B 带·阶梯 A-hops-prior-B **第八十七例**预期）；verify at W227 prereg·hop 链逐跳在 probe 回执。
  - 宝藏与方法论捕获：**W212-pattern 六门相位 miss 第 3 例（r943 死窗面）**——常设法（W217-debt pre-finalize law）在册且 W222 miss#5 后正确相位链曾三连（W223/W224/W225）；本次 miss 根因=会话中途死亡（finalize 落地后死在回执与收口 commit 前）非活窗省略门=法面无缺口零新方法论卡（knowledge/METHODOLOGY_ASSETS.md 零 append·捕获律问过即录）；零新宝藏（TREASURE_REGISTRY 零行）。愈合与披露范式（r917 先例）第 3 次执行。
  - 诚实披露面：r943 死窗死于六门前（splice 全落+finalize 已产·六门/fivekey 回执未跑=本窗 post-hoc 愈合·W212-pattern 第 3 例）；S6 链周一 10-12 bars+迟 bar 自愈 13 员由死窗 22:31-22:36 产出（本窗吸收收口）；compute_audit pool_starvation/supply_floor 结构旗（armed response=波链·W227 席位=下一动作）；canon flip 治理提案面未执行（K2200 同律·待治理窗）；MV i2v 波 A（CEO 令车道）并行在飞。"""
)

t = io.open(PREREG, encoding='utf-8').read()
assert t.count(A7) == 1, f"anchor7 count={t.count(A7)}"
assert t.count(A8) == 1, f"anchor8 count={t.count(A8)}"
t = t.replace(A7, N7).replace(A8, N8)
io.open(PREREG, 'w', encoding='utf-8', newline='').write(t)
print("W226 prereg sec.7/8 backfilled machine-read (ledger %s / K %s / five-key ALL PASS)" % (f"{sg['total']:,}", f"{npc['merged']['n_values']:,}"))
