# r1003 bm-a: W243 prereg sec7/8 finalize backfill (UTF-8 LF preserved, placeholder-line replace)
import json

P = 'research/PERPETUAL_N1_W243_PREREG.md'
c = open(P, 'r', encoding='utf-8', newline='').read()

r = json.load(open('results/_r1003bma_w243_fivekeys.json', encoding='utf-8'))
assert r['all_pass'] is True, 'five-key receipt not all-pass; refuse backfill'

ph7 = '- （占位·finalize one-pass 后回填：账本恒等式/合并池 K/merged mu·sigma·se_mu/K-lift 对照/§5 五预键机证件/六门探针/canon flip 态/audit 段——bm-a r999 W242 §7 范式）'
ph8 = '- （占位·finalize 同窗回填：§5.5 W244+ 投影承接机证/宝藏与方法论捕获问/诚实披露面——bm-a r999 W242 §8 范式）'

bf7 = (
'- 账本恒等式：prev **956,735** + 2,200 = **958,935 EXACT**（voids LOWAMP-P1/P2 同法应用·append_one_pass）。\n'
'- 合并池：**K=532,520 EXACT**（530,320+2,200）；merged mu **−0.09276**（−0.09275885）/ sigma **0.24507**（0.2450686）/ **se_mu@K532,520=0.000336**（W242 键 0.000374 → 收窄链续）；W243-only mu −0.09688 / sigma 0.24942。\n'
'- §5 五预键机证件（results/_r1003bma_w243_fivekeys.json·ALL PASS）：①W243-only vs merged mu gap **0.0041**<0.02 ✓（merged vs W242 键差 0.000017 ✓）②sigma rel **+0.0074%**<±10% ✓ ③A 档 p95 **0.3193** vs 键 0.2991 差 **0.0202**<0.05 ✓ ④K-lift 线移 **+0.0001**（line_pre 1.1933→line_merged 1.1934 @n_eff held 956,735）≤±0.02 ✓ ⑤se_mu **0.000336**≤0.000374 收窄 ✓。\n'
'- canon flip 态：**NOT performed**（governance proposal face only·K2200 同法）。\n'
'- 引擎烧录：engine self-burn **12/12**（shard 0-11·引擎车道·last done 2026-10-15T01:15:04·claim exempt law sec.2·driver 死窗 01:0x 起烧·r1003 收养收口）。\n'
'- audit 段：machine=bm-a·finalize_only=true·shards_consumed 12/12 文件名全录。\n'
'- 诚实披露：line_pre_w243=1.1933 与起稿窗引 W242 line_merged@K530,320=1.1932 的 0.0001 held-n 面（pre-line 按 skill_line_v2 在 n_eff=956,735 重算；键④判移动量非绝对值）；W242 prereg §7/§8 占位未回填（r999 overclaim 注记·W242 数字存 n1_w242_results.json+commit 90db59fc3·零功能影响）。'
)

bf8 = (
'- §5.5 W244+ 投影承接机证：冻结面 downstream_seat 注记——W244p face **A naive 553_501..555_500 CLEAN / B naive 541_701..541_900 CLEAN**（双 hops=0）；**W244 席未发布**——下一位 freezer 必须 seat-first publish（O-20261010-2350 §2）+post-W243 universe live re-derive（禁转录 r587）。\n'
'- 宝藏与方法论捕获问：**零新方法**（finalize one-pass=r999/W242 管线 verbatim 复用）→ METHODOLOGY_ASSETS 零 append；宝藏登记零新条（既有链法覆盖）。\n'
'- 诚实披露面：本窗收养死窗 estate（r1001 死窗 prereg/freeze/burn 链件 + r1002 退避窗零足迹移交——单执行体法下在飞件收养正法·r997 判例）；同窗并完成 D-20261015-02 方向①出库执行（8 件 bm-a daemon tick 面出库+gitignore+消费面切换·r1001 窗中断件收养）。'
)

assert ph7 in c, 'sec7 placeholder not found verbatim'
assert ph8 in c, 'sec8 placeholder not found verbatim'
c = c.replace(ph7, bf7)
c = c.replace(ph8, bf8)
open(P, 'w', encoding='utf-8', newline='').write(c)
print('backfill OK, new len:', len(c.encode("utf-8")))
