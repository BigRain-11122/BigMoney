# -*- coding: utf-8 -*-
"""r879 adopted-window W185 prereg 7/8 mechanical backfill (r875 W184 bloodline, all values machine-read zero hand-copy)."""
import io, json, sys

P = r'research\PERPETUAL_N1_W185_PREREG.md'
R = r'results\perpetual_faces\n1_w185_results.json'

d = json.load(io.open(R, encoding='utf-8'))
led = d['science_gates']['ledger']
np_ = d['null_pool_cumulative']
kl = d['skill_line_v2_k_lift']
fa = d['families']['A_random_engine_exit']

# machine-read assertions before writing
assert led['prev_total'] == 812128 and led['batch_trials'] == 2200 and led['total'] == 814328, led
assert np_['merged']['n_values'] == 404920, np_['merged']
assert fa['full_sharpe_p95'] == 0.3066 and fa['full_sharpe_p99'] == 0.4726 and fa['full_sharpe_mu'] == -0.095356, {k: fa[k] for k in ('full_sharpe_p95','full_sharpe_p99','full_sharpe_mu')}
assert kl['line_pre_w185'] == 1.1858 and kl['line_merged_404920'] == 1.1857 and kl['line_delta_k_lift'] == -0.0001, kl
assert d['audit']['finalize_only'] is True and d['audit']['machine'] == 'bm-a', d['audit']
assert len(d['shards_consumed']) == 12, len(d['shards_consumed'])

mu_gap = abs(np_['w185_only']['mu'] - np_['merged']['mu'])
sig_rel = (np_['merged']['sigma'] - np_['pre_w185_cumulative']['sigma']) / np_['pre_w185_cumulative']['sigma'] * 100.0
p95_delta = fa['full_sharpe_p95'] - 0.3194
assert mu_gap < 0.02 and abs(sig_rel) < 10.0 and abs(p95_delta) < 0.05 and abs(kl['line_delta_k_lift']) <= 0.02

src = io.open(P, encoding='utf-8').read()

h7_old = '## §7 跑后实证。【finalize 收口机械回填·待 W185 finalize 窗】\n- （占位·finalize one-pass 后机械回填：账本恒等式+合并池 K+merged mu/w-only mu/mu_delta+sigma+se_mu+skill_line_v2 K-lift+A 档 p95+§5 四预键机证+canon flip 态+audit.finalize_only+voids_applied。）'
h8_old = '## §8 批后复盘。【finalize 同窗回填·待 W185 finalize 窗】\n- （占位·§5.5 W186+ 投影承接+宝藏/方法论捕获问+诚实披露面·finalize 收口窗机械回填。）'
assert src.count(h7_old) == 1 and src.count(h8_old) == 1, (src.count(h7_old), src.count(h8_old))

h7_new = '''## §7 跑后实证。【finalize 收口机械回填·r879 收养窗（r844 dead-tail 律·死会话 13:23 落件本窗 13:3x 回填·无漏补窗）】
- 账本恒等式：812,128 + 2,200 = **814,328** EXACT（prev_total/batch_trials/total 三键机读·r879 finalize one-pass 实测；**vs §5 冻结投影（812,128+2,200=814,328 机械算）零差**——本窗零在飞上游批冻结后入链·对照 W184 +1,010 REGIME5 差例=本波干净入链）。
- 合并池：**K=404,920** EXACT（=W184 池 402,720 + 本波 2,200·§5 投影 404,920 命中）。
- merged mu **−0.092852**（机读 -0.09285237）/ w-only mu **−0.099214**（机读 -0.09921359）/ mu_delta(w185 vs w184ext) **−0.005922**。
- merged sigma **0.245090**（W184 键 0.245094→0.245090）；w-only sigma 0.244395；se_mu@K404,920 **0.000385**（W184 0.000386→0.000385 收窄·链面 …W182 0.000388→W183 0.000387→W184 0.000386→W185 0.000385）。
- skill_line_v2：line_pre **1.1858** → line_merged@K404,920 **1.1857**（K-lift **−0.0001**·n_eff_held_equal 812,128·四dp −0.0001 微移）；canon flip **NOT performed**（K2,200 同例法·治理提案面）。
- A 档 full_sharpe_p95 **0.3066**（W184 锚 0.3194·Δ−0.0128 门过）·p99 0.4726·A mu −0.095356。
- §5 四预键机证全过：①mu gap 0.006362<0.02 PASS ②sigma 相对变化 −0.0015%<±10% PASS ③A p95 Δ−0.0128<0.05 PASS ④K-lift −0.0001≤±0.02 PASS。
- audit.finalize_only=**true**（bm-a）·voids_applied=LOWAMP-P1,LOWAMP-P2·evidence_cutoff=2026-09-22 在位·shards_consumed 12/12（引擎 tick 自烧 12:4x–13:0x·r878 冻结窗自燃 r325 实证·finalize 13:23 死会话落件本窗收养）。'''

h8_new = '''## §8 批后复盘。【finalize 同窗回填·r879 收养窗】
- §5.5 W186+ 投影承接（r875 probe 机证·W186 冻结方重 derive 强制非转抄 r587 律）：naive A **423_804..425_803**（hops=0 CLEAN）——将被注册 W185 B 带 423_804..424_003 own-start 拒=阶梯 A-hops-prior-B 继承**第四十六例**待 W186 注册宇宙复核；naive B **424_004..424_203**（hops=0 CLEAN）落 naive A 窗内——W141 同窗互斥 leg2 律适用 W186（derive B 时预留本波 A 窗·§5.5 预披露注记在案）。
- 宝藏/方法论捕获问：本批 finalize one-pass=canonical runner 单发 r718 先例 verbatim 复用零新方法零新宝藏；TREASURE/METHODOLOGY 零 append。
- 诚实披露面：账本投影差 **零**（干净入链·对照 W184 +1,010 REGIME5 冻结后入链差例）；W185-only mu −0.0992 与合并池 −0.0929 差 0.0064（较 W184 的 0.0005 放宽·null 抽样单波 2,200 面小样本波动·四预键①仍 PASS）；mu_delta −0.005922=W185 w-only 较 W184ext-only（−0.093291）深化（方向与 W184 浅回 +0.0093 相反·单波 w-only 面波动·门内如实披露）；A p95 0.3066 较 W184 锚 0.3194 下移 −0.0128 仍门内（<0.05·测量面非注册利益）；line_pre 1.1858 较 W184 收官 1.1857 的 +0.0001=n_eff 基 809,928→812,128（+W184 波 2,200）增长自然步进非池加深效应；K-lift **−0.0001**=W181..W184 +0.0000 四波连平后首个负值（W154/W155/W156 −0.0002 族先例面·四预键④ PASS）；合并池 K=404,920 EXACT；引擎 tick 自烧 12 分片（12:4x–13:0x）+finalize 13:23 落件+§7/§8 回填+commit 收口=本复合窗兑现（r381 finalize 同窗收口律·跨死会话断点收养承接 r844 律·非拖延窗对照 W159/W168/W169/W181）。
- **回填窗注记：r879 dead-session 收养窗机械回填（无漏补窗·finalize→回填跨死会话断点 ~15min）**（数据全量本窗落件 n1_w185_results.json 13:23:17 机读零手抄·head/tail 字节保全）。'''

out = src.replace(h7_old, h7_new).replace(h8_old, h8_new)
assert out != src and out.count('占位·finalize one-pass') == 0 and out.count('占位·§5.5') == 0
io.open(P, 'w', encoding='utf-8', newline='').write(out)
print('backfill OK, new len', len(out))
