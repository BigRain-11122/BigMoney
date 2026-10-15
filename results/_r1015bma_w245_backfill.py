# r1015 bm-a: W245 prereg sec7/8 finalize backfill (UTF-8 LF preserved, placeholder-line replace)
# Clone lineage: _r1008bma_w244_backfill.py (W244 precedent)
import json

P = 'research/PERPETUAL_N1_W245_PREREG.md'
c = open(P, 'r', encoding='utf-8', newline='').read()

r = json.load(open('results/_r1015bma_w245_fivekeys.json', encoding='utf-8'))
assert r['all_pass'] is True, 'five-key receipt not all-pass; refuse backfill'
assert r['ledger_identity']['exact'] is True, 'ledger identity not exact; refuse backfill'

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
assert p7 > i7 and p7 < i8, 'sec7 placeholder not found'
assert p8 > i8, 'sec8 placeholder not found'

bf7 = (
'- 账本恒等式：prev **961,135** + 2,200 = **963,335 EXACT**（voids LOWAMP-P1/P2 同法应用·append_one_pass）。\n'
'- 合并池：**K=536,920 EXACT**（534,720+2,200）；merged mu **−0.09282**（−0.09281866）/ sigma **0.24504**（0.2450379）/ **se_mu@K536,920=0.000334**（W244 键 0.000335 → 收窄链续）；W245-only mu −0.09621 / sigma 0.24114。\n'
'- §5 五预键机证件（results/_r1015bma_w245_fivekeys.json·ALL PASS）：①W245-only vs merged mu gap **0.0034**<0.02 ✓（merged vs W244 键差 0.0000140 ✓）②sigma rel **−0.0065%**<±10% ✓ ③A 档 p95 **0.3020** vs 键 0.2952 差 **+0.0068**<0.05 ✓ ④K-lift 线移 **−0.0001**（line_pre 1.1935→line_merged 1.1934 @n_eff held 961,135）≤±0.02 ✓ ⑤se_mu **0.000334**≤0.000335 收窄 ✓。\n'
'- canon flip 态：**NOT performed**（governance proposal face only·K2200 同法）。\n'
'- 引擎烧录：engine self-burn **12/12**（shard 0-11·引擎车道·12:50:57→13:01:51·claim exempt law sec.2·冻结编辑 12:51-12:52 落工作树后引擎 mtime-watch 自见点火·r1015 estate-absorb 窗 freeze commit 29d3ab761 落地=引擎所读工作树字节恒等·r1015 收口）。\n'
'- audit 段：machine=bm-a·finalize_only=true·shards_consumed 12/12 文件名全录。\n'
'- 诚实披露：line_pre_w245=1.1935 与起草窗引 W244 line_merged@K534,720=1.1934 的 0.0001 held-n 面（pre-line 按 skill_line_v2 在 n_eff=961,135 重算；键④判移动量非绝对值）；K-lift **−0.0001**=W136..W244 先例链第二次连续负移（W244 首负·±0.0003 先例带内·零机制含义）；A p95 0.3020 较 W244 键 0.2952 高 0.0068（2,000 试 A 切片抽样波动·测量面非注册收益）；W245-only vs merged gap 0.0034（W244 先例 0.0111 之内的偏小值·带内）。'
)

bf8 = (
'- §5.5 W246+ 投影承接机证：冻结面 downstream_seat 注记——**W246 席未发布**——下一位 freezer 必须 seat-first publish（O-20261010-2350 §2）+post-W245 universe live re-derive（禁转录 r587）+derive B 时预留本波 A 窗（W245 face：A naive 557_501..559_500 预投影 CLEAN（hops=0）/ B naive 542_201..542_400 预投影 CLEAN（hops=0·W245 A 555_501..557_500 高悬于 B 542_001..542_200 之上·禁假设 staircase A-base==prior-B-tail+1 恒等——seed-gap face 连续第八波·B=live-seed-hop refuser 542_000+1 形态）。\n'
'- 宝藏与方法论捕获问：**零新方法**（finalize one-pass=r1008/W244 管线 verbatim 复用·fivekeys/backfill 脚本克隆血统注明）→ METHODOLOGY_ASSETS 零 append；宝藏登记零新条（既有链法覆盖）。\n'
'- 诚实披露面：本窗收养死 12:18-12:52 窗 estate 链（freeze edits 12:51:51+receipt 12:52:07 落地后窗死于 commit 前→r1015 estate absorb：freeze commit 29d3ab761 推送 844da61ef..29d3ab761+引擎 12:50-13:01 自烧 12/12（工作树字节=提交字节零偏差）+r1015 finalize one-pass+五键 ALL PASS+本回填收口）；序列诚实=r1014 estate-absorb 后死窗·canonical face=round_reports+git log 判例 r961/r1006·序列续 r1015。'
)

lines[p7] = bf7
lines[p8] = bf8
c2 = '\n'.join(lines)
assert '\u5360\u4f4d' not in c2.split('\n')[i7], 'sec7 placeholder residue'
assert '\u5360\u4f4d' not in c2.split('\n')[p8], 'sec8 placeholder residue'
open(P, 'w', encoding='utf-8', newline='').write(c2)
print('backfill OK, new len:', len(c2.encode('utf-8')))
