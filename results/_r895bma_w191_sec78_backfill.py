# r895 bm-a: W191 prereg sec7/sec8 finalize backfill (machine-derived, UTF-8 no BOM).
# Numbers read directly from results/perpetual_faces/n1_w191_results.json (materialized
# finalize face, engine materializer 02:02 12/12 completion) -- zero hand transcription.
import json

P = 'research/PERPETUAL_N1_W191_PREREG.md'
d = json.loads(open('results/perpetual_faces/n1_w191_results.json', encoding='utf-8').read())
nc = d['null_pool_cumulative']
led = d['science_gates']['ledger']
sl = d['skill_line_v2_k_lift']
A = d['families']['A_random_engine_exit']
aud = d['audit']

assert led['prev_total'] == 831336 and led['batch_trials'] == 2200 and led['total'] == 833536
assert aud['finalize_only'] is True and aud['machine'] == 'bm-a'
assert nc['merged']['n_values'] == 418120
assert sl['line_merged_418120'] and abs(sl['line_delta_k_lift'] - 0.0001) < 5e-5
assert len(d['shards_consumed']) == 12
assert d['evidence_cutoff'] == '2026-09-22'
wmu, mmu = nc['w191_only']['mu'], nc['merged']['mu']
gap = abs(wmu - mmu)
sig_old, sig_new = 0.245150, nc['merged']['sigma']
sig_rel = (sig_new - sig_old) / sig_old * 100
p95_d = A['full_sharpe_p95'] - 0.3068
assert gap < 0.02 and abs(sig_rel) < 10 and abs(p95_d) < 0.05 and abs(sl['line_delta_k_lift']) <= 0.02

sec7 = """## §7 跑后实证。【finalize 收口机械回填·r895 回填窗（materializer 02:02 引擎自动 finalize 落件·§7/§8 同窗回填）】
- 账本恒等式：831,336 + 2,200 = **833,536** EXACT（prev_total/batch_trials/total 三键机读·引擎 materializer 02:02 落件；**vs §5 冻结窗投影（825,328+2,200=827,528）差 +6,008**=本波冻结（r893 ea42ee94a）后 bm-b r807 fund_trio 账本分叉追加式重锚（825,328→831,336·pit-protocol-judge r807 律）入链——r518 活链头消费律（prev=finalize 时点活头非冻结窗锚）·偏离=本条披露非改判据）。
- 合并池：**K=418,120** EXACT（=W190 池 415,920 + 本波 2,200·§5 投影 418,120 命中）。
- merged mu **-0.092867**（机读 -0.09286652）/ w-only mu **-0.089832**（机读 -0.08983173）/ mu_delta(w191 vs w190ext) **+0.008767**。
- merged sigma **0.245166**（W190 键 0.245150→0.245166 第六位面微升·相对变化 +0.0065%）；w-only sigma 0.248260；se_mu@K418,120 **0.000379**（W190 0.000380→W191 0.000379 收窄·链面 …W188 0.000382→W189 0.000381→W190 0.000380→W191 0.000379）。
- skill_line_v2：line_pre **1.1871** → line_merged@K418,120 **1.1872**（K-lift **+0.0001**·n_eff_held_equal 831,336）；canon flip **NOT performed**（K2,200 同例法·治理提案面）。
- A 档 full_sharpe_p95 **0.3049**（W190 键 0.3068·Δ-0.0019 门内）·p99 0.4528。
- §5 四预键机证全过：①mu gap 0.0030<0.02 PASS（w-only 高于合并池·方向与 W190 −0.0057 相反·门内如实披露）②sigma 相对变化 +0.0065%<±10% PASS ③A p95 Δ-0.0019<0.05 PASS ④K-lift +0.0001≤±0.02 PASS。
- audit.finalize_only=**true**（bm-a）·voids_applied=LOWAMP-P1,LOWAMP-P2·evidence_cutoff=2026-09-22 在位·shards_consumed 12/12（引擎 tick 自烧 r894 点火 n1w191-1of12 起 12 分片·死会话窗 r895 S0 收编 shard-10/11 verbatim 恢复+01:39 引擎活面吸收·**02:02 materializer 12/12 自动合成落账=W191 materializer 首次实弹自燃 finalize**——r894 五面冻结自带 materializer face（n1 selftest 已验）·session 侧 finalize 零调用·pit-95 落地守卫+finalize_already_landed r459 嵌套面读核确认拒再 append）。
"""

sec8 = """## §8 批后复盘。【finalize 同窗回填·r895 回填窗】
- §5.5 W192+ 投影承接（bm-c 预席 probe 机证·W192 席位已发布=MSG-20261008-2351-bmc·r587 never-transcribe 律）：naive A **437_004..439_003**（hops=0 CLEAN）——被注册 W191 B 带 437_004..437_203 own-start 拒=阶梯 A-hops-prior-B 继承**第五十二例**（§5.5 预披露兑现）——bm-c probe 实证 **A 437_204..439_203，hops=1**；naive B **437_204..437_403**（hops=0 CLEAN）落本波 A 窗内——W141 同窗互斥 leg2 律适用 W192（derive B 时预留本波 A 窗·bm-c probe 实证 **B 439_204..439_403，hops=1**）；W193+ 投影（bm-c 席 MSG leg4 机证：naive A 439_204..441_203 / naive B 439_404..439_603·B 落 A 窗内）——W193 冻结方必须在 post-W192 注册宇宙重 derive（r587·E36 卡·never transcribe·阶梯**第五十三例**预告=W192-B-refuses-W193-A）。
- 宝藏/方法论捕获问：本批 finalize=引擎 materializer 自动合成（r894 冻结窗已设计+n1 selftest 已验机制的首次实弹·非本批新方法）；TREASURE/METHODOLOGY 零 append。
- 诚实披露面：账本投影差 **+6,008**（bm-b r807 fund_trio 追加式重锚于本波冻结后入链·活链头消费律 r518·干净入链零科学损失）；line_pre 1.1871 较 W190 收官 line_merged 1.1866 的 +0.0005=n_eff 基 823,128→831,336 增长自然步进非池加深效应；K-lift **+0.0001**=W190 −0.0001 后回升（正面对照族 W139/W141/W143/W150-153/W157/W159-160）；mu_delta +0.008767=W191 w-only（−0.0898）较 W190ext-only（−0.0986）回升转正（W190 −0.010831 回落后单波 w-only 面波动·门内如实披露）；w-only mu 高于合并池（方向与 W190 相反·四预键①仍 PASS）；A p95 0.3049 较 W190 键 0.3068 微降 −0.0019 仍门内；合并池 K=418,120 EXACT；引擎 tick 自烧 12 分片（r894 点火 n1w191-1of12·死会话窗 12/12 落位）+materializer 02:02 自动 finalize 落件（首次实弹·pit-95 守卫在场=r459 嵌套面读核确认）+§7/§8 本窗（r895）同窗回填+commit 收口。
"""

src = open(P, encoding='utf-8').read()
ph7 = "## §7 跑后实证。【finalize 收口机械回填·待 W191 finalize 窗】\n- （占位·finalize one-pass 后机械回填：账本恒等式+合并池 K+merged mu/w-only mu/mu_delta+sigma+se_mu+skill_line_v2 K-lift+A 档 p95+§5 四预键机证+canon flip 态+audit.finalize_only+voids_applied。）\n"
ph8 = "## §8 批后复盘。【finalize 同窗回填·待 W191 finalize 窗】\n- （占位·§5.5 W192+ 投影承接+宝藏/方法论捕获问+诚实披露面·finalize 收口窗机械回填。）\n"
assert ph7 in src, 'sec7 placeholder not found'
assert ph8 in src, 'sec8 placeholder not found'
src = src.replace(ph7, sec7).replace(ph8, sec8)
with open(P, 'w', encoding='utf-8', newline='') as f:
    f.write(src)
print('backfill OK: sec7+sec8 landed')
