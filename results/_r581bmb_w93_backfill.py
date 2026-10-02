# -*- coding: utf-8 -*-
# r581 bm-b: W93 finalize archive + prereg sec7/8 mechanical backfill
import json

STDOUT_ARCHIVE = """pre-W93  mu=-0.0927 sigma=0.2448 (K=200320)
w93      mu=-0.0969 sigma=0.2428 (K=2200)
merged  mu=-0.0927 sigma=0.2448 (K=202520)
skill_line_v2 @n_eff=566948: 1.1675 -> 1.1673 (K-lift delta -0.0002)
ledger: {'prev_total': 566948, 'batch_trials': 2200, 'total': 569148, 'batch': 'PERPETUAL-N1-W93', 'voids_applied': ['LOWAMP-P1', 'LOWAMP-P2'], 'file': 'perpetual_faces/n1_w93_results.json', 'note': 'perpetual N1 nulls-deepening wave 93 (law PERPETUAL_FACES v1.0 sec.4): 2,200 new-seed null trials, frozen v1 design, window 2026-09-22', 'evidence_cutoff': '2026-09-22'}
saved: C:\\Fluxgroup\\FluxGroup\\quant\\bigmoney\\results\\perpetual_faces\\n1_w93_results.json
"""
with open('results/_r581bmb_w93_finalize_stdout.txt', 'wb') as f:
    f.write(STDOUT_ARCHIVE.replace('\n', '\r\n').encode('utf-8'))

d = json.load(open('results/perpetual_faces/n1_w93_results.json', encoding='utf-8'))
npc = d['null_pool_cumulative']
w93o = npc['w93_only']
merged = npc['merged']
a_p95 = d['families']['A_random_engine_exit']['full_sharpe_p95']
sl = d['skill_line_v2_k_lift']
se = npc.get('se_mu_at_k202520')
delta_key = [k for k in npc if 'mu_delta' in k]
print('w93_only:', {k: w93o[k] for k in ('n_values', 'mu', 'sigma')})
print('merged:', {k: merged[k] for k in ('n_values', 'mu', 'sigma')})
print('mu_delta key:', delta_key, [npc[k] for k in delta_key])
print('A p95:', a_p95, '| k_lift:', sl['line_delta_k_lift'], '| se_mu:', se)

SEC7_NEW = (
    "## §7 跑后实证。【r579 冻结占位·r581 finalize 收口机械回填】\n"
    "\n"
    "- 12/12 分片 bm-b 引擎烧毕（r579 冻结 commit 后 tick 架构自燃免重启·r535 律·r580 窗 12/12 烧毕·r581 origin ls-tree 产物在场 12/12=r310 完备性门先行实核）；finalize one-pass（r538 律·首跑禁重跑·本地无未 commit 自产波件前置核验·r581）。\n"
    "- ledger：prev_total 566,948（W92 bm-c r372 落账解锁·链序 W88 558,148 bm-c→W89 560,348 bm-b→W90 562,548 bm-a→W91 564,748 bm-b→W92 566,948 bm-c）+ batch_trials 2,200 = **569,148**；voids_applied=LOWAMP-P1/P2。\n"
    "- w93-only：n=2,200·mu=−0.0969452·sigma=0.2428347；merged：n=202,520·mu=−0.0927304·sigma=0.2447890（§0「W92 落账后 K=200,320+本波」投影逐位吻合）；mu_delta_w93_vs_w92ext=−0.006933（本波批较 W92 批更深·仍浅于存量池——合并后 mu 漂 −0.000046·门内）。\n"
    "- skill_line_v2 @n_eff_held 566,948：1.1675→**1.1673**（K-lift delta −0.0002≤0.02 门内·正负交替如实报负〔W89 −0.0004→W90 −0.0002→W91 +0.0003→W92 +0.0004→W93 −0.0002〕）；se_mu @K202,520=0.000544（收窄链延续：W87 0.000563→W89 0.000556→W91 0.000550→W92 0.000547→W93 0.000544）；canon_flip 未执行（治理提案面·K2200 同法）。\n"
    "- §5 预测四门全过：|Δmu|=0.0042<0.02（锚=W91 merged −0.0927138）；σ 变化 −2.3%<±10%（锚 W91-only 0.2485487·本波 0.2428）；A 桶 p95 差 0.0274<0.05（锚 0.3275·本波 0.3001）；K-lift −0.0002≤0.02。finalize stdout 留档=results/_r581bmb_w93_finalize_stdout.txt；产物 `results/perpetual_faces/n1_w93_results.json`（顶层 evidence_cutoff=2026-09-22·cutoff_meta·audit.machine=bm-b·shards_consumed 12）。\n"
)
SEC8_NEW = (
    "## §8 批后复盘。【r581 补全】\n"
    "\n"
    "- 链序实况：冻结窗（r579）在飞上游席已全部落账（W88 bm-c→W89 bm-b→W90 bm-a→W91 bm-b→W92 bm-c r372）——本波 finalize one-pass 收口，r307 两态律跑时复核通过（pre-W93 K=200,320/mu/sigma 与 W92 merged 逐位吻合=链连续性实证）、零改判据。\n"
    "- 供给面：本波 finalize 解锁 W94 bm-a finalize 链序（12/12 产品已 bm-a r582 交付 origin）；同窗 W95 bm-b 12/12 烧毕 finalize-pending（链序候 W94）+W96 bm-a 烧录中+W97 bm-b r581 冻结在案——供给线连续；bm-b 下一 finalize=W95（候 W94 落账）。\n"
)

p = 'research/PERPETUAL_N1_W93_PREREG.md'
data = open(p, 'rb').read().decode('utf-8')
i7 = data.find('## §7')
i8 = data.find('## §8')
itail = data.find('- **跑前冻结=本件 commit**')
assert 0 < i7 < i8 < itail, 'section anchors missing'
old7 = data[i7:i8]
old8 = data[i8:itail]
assert '占位' in old7 and '占位' in old8, 'placeholder drift'
new = data[:i7] + SEC7_NEW + '\n' + SEC8_NEW + '\n' + data[itail:]
open(p, 'wb').write(new.encode('utf-8'))
print('prereg sec7/8 backfilled, +%d bytes' % (len(new) - len(data)))
