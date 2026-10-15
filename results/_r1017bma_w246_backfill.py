# -*- coding: utf-8 -*-
# r1017 bm-a: W246 prereg sec7/8 finalize backfill (UTF-8 LF preserved, placeholder-line replace)
# Clone lineage: _r1015bma_w245_backfill.py (W245 precedent). Values machine-read
# from _r1017bma_w246_fivekeys.json + n1_w246_results.json -- zero transcription.
import json

P = 'research/PERPETUAL_N1_W246_PREREG.md'
c = open(P, 'r', encoding='utf-8', newline='').read()

r = json.load(open('results/_r1017bma_w246_fivekeys.json', encoding='utf-8'))
assert r['all_pass'] is True, 'five-key receipt not all-pass; refuse backfill'
assert r['ledger_identity']['exact'] is True, 'ledger identity not exact; refuse backfill'

res = json.load(open('results/perpetual_faces/n1_w246_results.json', encoding='utf-8'))
pool = res['null_pool_cumulative']
sl = res['skill_line_v2_k_lift']
famA = res['families']['A_random_engine_exit']
ck = {x['name']: x for x in r['checks']}


def f(v, n=5):
    return ('%.' + str(n) + 'f') % v


bf7 = (
'- 账本恒等式：prev **963,335** + 2,200 = **965,535 EXACT**（voids LOWAMP-P1/P2 同法应用·append_one_pass）。\n'
'- 合并池：**K=%d EXACT**（536,920+2,200）；merged mu **%s**（%s）/ sigma **%s**（%s）/ **se_mu@K=539,120=%s**（W245 键 0.000334 → 收窄链续）；W246-only mu %s / sigma %s。\n'
'- §5 五预键机证件（results/_r1017bma_w246_fivekeys.json·ALL PASS）：①W246-only vs merged mu gap **%s**<0.02 ✓（merged vs W245 键差 %s ✓）②sigma rel **%s%%**<±10%% ✓ ③A 档 p95 **%s** vs 键 0.3020 差 **%s**<0.05 ✓ ④K-lift 线移 **%s**（line_pre %s→line_merged %s @n_eff held %d）≤±0.02 ✓ ⑤se_mu **%s**≤0.000334 收窄 ✓。\n'
'- canon flip 态：**%s**（governance proposal face only·K2200 同法）。\n'
'- 引擎烧录：engine self-burn **12/12**（shard 0-11·引擎车道·常驻引擎 materializer 自见 auto-ignite·claim exempt law sec.2·冻结编辑 15:5x 落工作树后引擎 mtime-watch 自见点火·freeze commit 650953086 落地=引擎所读工作树字节恒等·r1017 收口）。\n'
'- audit 段：machine=bm-a·finalize_only=true·shards_consumed 12/12 文件名全录。\n'
'- 诚实披露：K-lift **%s**=W136..W245 先例链三次连续负移段（W244 首负·W245 −0.0001·±0.0003 先例带内·零机制含义·nulls-deepening 测量面）；A p95 %s 较 W245 键 0.3020 差 %s（2,000 试 A 切片抽样波动·测量面非注册收益）；W246-only vs merged gap %s（W245 先例 0.0034 同量级·带内）。'
) % (
    r['merged']['k'],
    f(r['merged']['mu']), '%.8f' % r['merged']['mu'],
    f(r['merged']['sigma']), '%.7f' % r['merged']['sigma'],
    '%.6f' % r['merged']['se_mu_k539120'],
    '%.5f' % r['w246_only']['mu'], '%.5f' % r['w246_only']['sigma'],
    '%.4f' % ck['key1_w246_vs_merged_mu_gap']['value'],
    '%.7f' % ck['key1b_merged_vs_w245_key']['value'],
    '%.4f' % (ck['key2_sigma_rel']['value'] * 100),
    '%.4f' % r['a_band']['full_sharpe_p95'], '%+.4f' % ck['key3_a_p95_delta']['value'],
    '%+.4f' % ck['key4_k_lift_move']['value'],
    '%.4f' % r['skill_line']['line_pre_w246'], '%.4f' % r['skill_line']['line_merged_539120'],
    r['skill_line']['n_eff_held'],
    '%.6f' % r['merged']['se_mu_k539120'],
    str(r['canon_flip']).upper(),
    '%+.4f' % ck['key4_k_lift_move']['value'],
    '%.4f' % r['a_band']['full_sharpe_p95'], '%+.4f' % ck['key3_a_p95_delta']['value'],
    '%.4f' % ck['key1_w246_vs_merged_mu_gap']['value'],
)

bf8 = (
'- §5.5 W247+ 投影承接机证：冻结面 downstream_seat 注记——**W247 席未发布**——下一位 freezer 必须 seat-first publish（O-20261010-2350 §2）+post-W246 universe live re-derive（禁转录 r587）+derive B 时预留本波 A 窗（W246 face：A naive 559_501..561_500 预投影 CLEAN（hops=0）/ B naive 542_401..542_600 撞注册 W239 A 带 → first-clean 544_501..544_700 hops=1 staircase band-hop 形态首披露·B_hop_lands_inside_A=false leg 在场；W246 A 557_501..559_500 高悬于 B 542_201..542_400 之上·seed-gap face 连续第八波·禁假设 staircase A-base==prior-B-tail+1 恒等）。\n'
'- 宝藏与方法论捕获问：**零新方法**（finalize one-pass=r1015/W245 管线 verbatim 复用·sixgate/fivekeys/backfill 脚本克隆血统注明）→ METHODOLOGY_ASSETS 零 append；宝藏登记零新条（既有链法覆盖）。\n'
'- 诚实披露面：本窗收养死 14:11-15:13 窗 estate 链（W246 gen 调试至 L406 quote-tail 修复窗死于编辑器运行前→r1017 继承窗：fix4 修复 gen L406 三引号尾+gen a2-closer 缺尾 `)`×2 修复→editor regen 739 行→五面 splice AST 门首跑拦（L61007 tuple 缺闭合）→回滚→修复→重跑 SPLICE OK）；序列诚实=r1016 闭轮后死窗·canonical face=round_reports+git log 判例 r961/r1006/r1008·序列续 r1017。'
)

lines = c.split('\n')
i7 = i8 = -1
for i, ln in enumerate(lines):
    if ln.startswith('## ') and ln[3:5] == '\u00a77':
        i7 = i
    if ln.startswith('## ') and ln[3:5] == '\u00a78':
        i8 = i
        break
assert i7 >= 0 and i8 > i7, 'sec7/sec8 headers not found'

p7 = p8 = -1
for i in range(i7 + 1, len(lines)):
    if lines[i].startswith('- ') and 'finalize' in lines[i] and p7 < 0:
        p7 = i
for i in range(i8 + 1, len(lines)):
    if lines[i].startswith('- ') and 'finalize' in lines[i] and p8 < 0:
        p8 = i
assert i7 < p7 < i8, 'sec7 placeholder not found (p7=%s)' % p7
assert p8 > i8, 'sec8 placeholder not found (p8=%s)' % p8

lines[p7] = bf7
lines[p8] = bf8
c2 = '\n'.join(lines)
assert '\u5360\u4f4d' not in c2.split('\n')[p7], 'sec7 placeholder residue'
assert '\u5360\u4f4d' not in c2.split('\n')[p8], 'sec8 placeholder residue'
open(P, 'w', encoding='utf-8', newline='').write(c2)
print('backfill OK, new len:', len(c2.encode('utf-8')))
