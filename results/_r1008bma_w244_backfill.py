# r1008 bm-a: W244 prereg sec7/8 finalize backfill (UTF-8 LF preserved, placeholder-line replace)
import json

P = 'research/PERPETUAL_N1_W244_PREREG.md'
c = open(P, 'r', encoding='utf-8', newline='').read()

r = json.load(open('results/_r1008bma_w244_fivekeys.json', encoding='utf-8'))
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
'- \u8d26\u672c\u6052\u7b49\u5f0f\uff1aprev **958,935** + 2,200 = **961,135 EXACT**\uff08voids LOWAMP-P1/P2 \u540c\u6cd5\u5e94\u7528\u00b7append_one_pass\uff09\u3002\n'
'- \u5408\u5e76\u6c60\uff1a**K=534,720 EXACT**\uff08532,520+2,200\uff09\uff1bmerged mu **\u22120.09280**\uff08\u22120.09280471\uff09/ sigma **0.24505**\uff080.2450539\uff09/ **se_mu@K534,720=0.000335**\uff08W243 \u952e 0.000336 \u2192 \u6536\u7a84\u94fe\u7eed\uff09\uff1bW244-only mu \u22120.10390 / sigma 0.24127\u3002\n'
'- \u00a75 \u4e94\u9884\u952e\u673a\u8bc1\u4ef6\uff08results/_r1008bma_w244_fivekeys.json\u00b7ALL PASS\uff09\uff1a\u2460W244-only vs merged mu gap **0.0111**<0.02 \u2713\uff08merged vs W243 \u952e\u5dee 0.0000459 \u2713\uff09\u2461sigma rel **\u22120.0060%**<\u00b110% \u2713 \u2462A \u6863 p95 **0.2952** vs \u952e 0.3193 \u5dee **0.0241**<0.05 \u2713 \u2463K-lift \u7ebf\u79fb **\u22120.0001**\uff08line_pre 1.1935\u2192line_merged 1.1934 @n_eff held 958,935\uff09\u2264\u00b10.02 \u2713 \u2464se_mu **0.000335**\u22640.000336 \u6536\u7a84 \u2713\u3002\n'
'- canon flip \u6001\uff1a**NOT performed**\uff08governance proposal face only\u00b7K2200 \u540c\u6cd5\uff09\u3002\n'
'- \u5f15\u64ce\u70e7\u5f55\uff1aengine self-burn **12/12**\uff08shard 0-11\u00b7\u5f15\u64ce\u8f66\u9053\u00b706:59:12\u219207:11:04\u00b7claim exempt law sec.2\u00b7r1007 \u51bb\u7ed3\u540e\u5f15\u64ce\u6e05\u9053\u91cd\u8dd1\u00b7r1008 \u6536\u53e3\uff09\u3002\n'
'- audit \u6bb5\uff1amachine=bm-a\u00b7finalize_only=true\u00b7shards_consumed 12/12 \u6587\u4ef6\u540d\u5168\u5f55\u3002\n'
'- \u8bda\u5b9e\u62ab\u9732\uff1aline_pre_w244=1.1935 \u4e0e\u8d77\u7a3f\u7a97\u5f15 W243 line_merged@K532,520=1.1934 \u7684 0.0001 held-n \u9762\uff08pre-line \u6309 skill_line_v2 \u5728 n_eff=958,935 \u91cd\u7b97\uff1b\u952e\u2463\u5224\u79fb\u52a8\u91cf\u975e\u7edd\u5bf9\u503c\uff09\uff1bK-lift **\u22120.0001**=W136..W243 \u5148\u4f8b\u94fe\u9996\u89c1\u8d1f\u79fb\uff08\u00b10.0003 \u5148\u4f8b\u5e26\u5185\u00b7\u96f6\u673a\u5236\u542b\u4e49\uff09\uff1bA p95 0.2952 \u8f83 W243 \u952e 0.3193 \u4f4e 0.0241\uff082,000 \u8bd5 A \u5207\u7247\u62bd\u6837\u6ce2\u52a8\u00b7\u6d4b\u91cf\u9762\u975e\u6ce8\u518c\u6536\u76ca\uff09\uff1bW244-only vs merged gap 0.0111\uff08W243 \u5148\u4f8b 0.0041\u00b7\u5e26\u5185\u504f\u5927\u00b7\u96f6\u95e8\u8fdd\u53cd\uff09\u3002'
)

bf8 = (
'- \u00a75.5 W245+ \u6295\u5f71\u627f\u63a5\u673a\u8bc1\uff1a\u51bb\u7ed3\u9762 downstream_seat \u6ce8\u8bb0\u2014\u2014W245 face \u6295\u5f71 **A naive first-clean 555_501..557_500 CLEAN\uff08hops=0\uff09/ B naive first-clean 542_001..542_200\uff08hops=1 \u62d2\u5e26\u9762\u00b7naive 541_901..542_100 \u7a97\u5185\u6d3b\u70b9\u62d2\u2192first-clean \u8bda\u5b9e\u524d\u884c\u00b7B_hop lands-inside-A=false \u817f\u5728\u573a\uff09**\uff1b**W245 \u5e2d\u672a\u53d1\u5e03**\u2014\u2014\u4e0b\u4e00\u4f4d freezer \u5fc5\u987b seat-first publish\uff08O-20261010-2350 \u00a72\uff09+post-W244 universe live re-derive\uff08\u7981\u8f6c\u5f55 r587\uff09+derive B \u65f6\u9884\u7559\u672c\u6ce2 A \u7a97\uff08seed-gap \u627f\u88ad face\uff1aW244 A 553_501..555_500 \u9ad8\u60ac\u4e8e B 541_701..541_900 \u4e4b\u4e0a\u00b7\u7981\u5047\u8bbe staircase A-base==prior-B-tail+1 \u6052\u7b49\uff09\u3002\n'
'- \u5b9d\u85cf\u4e0e\u65b9\u6cd5\u8bba\u6355\u83b7\u95ee\uff1a**\u96f6\u65b0\u65b9\u6cd5**\uff08finalize one-pass=r1003/W243 \u7ba1\u7ebf verbatim \u590d\u7528\u00b7W244 \u51bb\u7ed3\u7f16\u8f91\u5668 gen-bug \u4fee\u590d\u5bf9\u5f52 r1007 \u7a97\u6ce8\u8bb0\uff09\u2192 METHODOLOGY_ASSETS \u96f6 append\uff1b\u5b9d\u85cf\u767b\u8bb0\u96f6\u65b0\u6761\uff08\u65e2\u6709\u94fe\u6cd5\u8986\u76d6\uff09\u3002\n'
'- \u8bda\u5b9e\u62ab\u9732\u9762\uff1a\u672c\u7a97\u6536\u517b\u6b7b 06:15 \u7a97 estate \u94fe\uff08r1007 \u4e09 commit \u95ed\u94fe\uff1a50dfc18e4 estate absorb/71ac3a885 editor \u4fee\u590d+ORD \u6c34\u4f4d\u63a8\u8fdb/10bdb987b \u51bb\u7ed3\u843d\u5730+\u5f15\u64ce\u6062\u590d\u6e05\u9053\u2192\u5f15\u64ce 06:59-07:11 \u81ea\u70e7 12/12\u2192r1008 finalize+\u4e94\u952e+\u672c\u56de\u586b\u6536\u53e3\uff09\uff1b\u8f6e\u5e8f\u8bda\u5b9e=r1007 \u62a5\u544a\u884c\u7f3a\u5931\uff08canonical face=round_reports+git log \u5224\u4f8b r961/r1006\u00b7\u5e8f\u5217\u7eed r1008\uff09\u3002'
)

lines[p7] = bf7
lines[p8] = bf8
c2 = '\n'.join(lines)
assert '\u5360\u4f4d' not in c2.split('\n')[i7], 'sec7 placeholder residue'
assert '\u5360\u4f4d' not in c2.split('\n')[p8], 'sec8 placeholder residue'
open(P, 'w', encoding='utf-8', newline='').write(c2)
print('backfill OK, new len:', len(c2.encode('utf-8')))
