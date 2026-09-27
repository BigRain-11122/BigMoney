# -*- coding: utf-8 -*-
"""r325 bm-b 5x HANDOVER check: line-4 cascade refresh (prepend r325, demote r320, prune r280) + end-of-file increment window row append.
Byte-faithful CRLF mode (read newline='' per r325 pitfall: universal-newline read flattens CRLF -> full-file rewrite).
Zero-loss assertions per r319 canon. Strict UTF-8 io per r320/r323 GBK lesson."""
import io

P = 'research/HANDOVER.md'
raw = io.open(P, encoding='utf-8', newline='').read()
n0_lines = raw.splitlines(True)
n0 = len(n0_lines)
n0_crlf = sum(1 for l in n0_lines if l.endswith('\r\n'))

NEW_HEAD = ('最近核对=bm-b round 325（2026-09-27 13:2x·对账增量=文末 round 325 bm-b 增量窗行〔bm-b r321-325 窗：'
 '**维护与坑律连营·统一链 286,541 实读平持=本窗零批 finalize（_r295bmb_ledger_scan 复跑 79 件 INTERNAL_BALANCE_FAIL=0·DUP_BATCH_CONFLICTS=0）**——'
 'r321 收讫 bm-a T-90-V1 判据路径 typo 修正（复审器重 derive YES 10/10）+S0 autofill stage-union 55 零损失；'
 'r322 轮首 p1d_gates 第三写手面 stash 三步舞保 unstaged 设计态+orders 96/96 双扫；'
 'r323=r320 GBK 污染残留根修（生产者 54 件面全量 strict UTF-8 扫+round_reports r320 行 strict gbk 无损转码·坑律=污染修复扫描面=生产者写入面全量）+CODELY 十二批热冷整编 9609→7805B multiset 零丢失；'
 'r324 S6 29/29 rc=0+post_review 现行红面=0（每 id 最新行口径 45 YES+5 WAIT）+state/心跳轮号三面对齐（322/323/320→324）+S7 16-UU 三机同窗撞车典解（union 零丢失+take-new probed ts·resolver _r324bmb_resolve.py 16/16）；'
 'r325=本核对轮：轮首 p1d_gates 定向提交（r120 律）FF pull+S6 29/29 rc=0（周日 cutoff 09-24 no-new-bar 法定形态·三条件腿依法跳·audit 旗=pool_starvation 供给缺口白名单〔sina 深面板重拉在飞〕·水位 insufficient_history 窗重积中=前 3 连 py_low_board_clear）'
 '+sina-construct prereg 门维持关（bm-a sina 深面板重拉在飞·complete+N≥250 门开后本机起草·三线三判律）〕）')

OLD_HEAD_ANCHOR = '最近核对=bm-a round 320（2026-09-27 12:1x·对账增量=本窗 bm-a R316-320 行'
PRUNE_TAIL = ('；上一次最近核对=bm-a round 280（2026-09-27 00:5x·对账增量=文末 round 280 bm-a 行〔bm-a R279-280 增量'
 '（R276-278 已并读于 round 280 bm-b 行）：**REV_OSC d6 崩-发双发射根因修（工程修零判定产物窗）'
 '+CN_TREND_ETF_P1 prereg 冻结（T-87 s2 队列#1 趋势跟踪批）+S0 autofill_state 双撞车 union 解**；'
 '统一链 187,845 平持=本窗零批 finalize（prereg 冻结面不计账·revosc 修后待 tick 重发）〕）')

assert raw.count(OLD_HEAD_ANCHOR) == 1, 'head anchor not unique/found'
assert raw.count(PRUNE_TAIL) == 1, 'prune tail not unique/found'

raw2 = raw.replace(OLD_HEAD_ANCHOR, NEW_HEAD + '；上一次最近核对=bm-a round 320（2026-09-27 12:1x·对账增量=本窗 bm-a R316-320 行', 1)
raw2 = raw2.replace(PRUNE_TAIL, '', 1)

# cascade sanity on line-4 after edit
l4 = raw2.splitlines(True)[3]
assert '最近核对=bm-b round 325' in l4 and '上一次最近核对=bm-a round 320' in l4
assert 'round 280 bm-a' not in l4, 'prune failed'
assert l4.count('最近核对=') == 10, 'cascade count unexpected'

ROW = ('- 开发队列增量窗（接续版）**round 325 bm-b（5x 核对本轮），2026-09-27 13:2x 补核；对账区间=增量 bm-b r321-325 并读 bm-a R321-323（基线=round 320 bm-b 行·round 80 bm-c 行已收讫窗），'
 '统一链 286,541 实读平持（_r295bmb_ledger_scan 复跑 79 件〔int-total 78〕INTERNAL_BALANCE_FAIL=0·DUP_BATCH_CONFLICTS=0·链尾全连续 HEAD=DECISION_CHAIN_E2E_P1；'
 '本窗零批 finalize：bm-b 维护与坑律窗零跑批·bm-c T19-PHANTOM stage-2c=测量批零 ledger trials per prereg §4·MF_IC_P1 待 sina 面板 legal park）**：'
 '①**bm-b r321-324=维护与坑律四连窗**——r321 S0 autostash FF（bm-a r320 T-90 criteria-path-fix 窗）+autofill_state stage-union 55 零损失+inbox MSG-20260927-1215 收讫'
 '（bm-a 按 r223/r270 判例修正本机 r319 注册 T-90-V1 判据路径 typo·复审器重 derive YES 10/10·全表 YES=44 NO=0·本机零双写）；'
 'r322 S0 FF pull（bm-a autofill tick 窗 4 件）+轮首 p1d_gates 第三写手面=显式 stash 三步舞保 unstaged 设计态（r317 正典）+orders 96/96 双扫；'
 'r323=r320 GBK 污染残留根修（r320 bm-a 只修冲突集件漏扫同窗生产者非冲突件·strict 读者轮首实撞 UnicodeDecodeError→正典=生产者两提交 54 件面全量 strict UTF-8 扫+坏区 strict gbk 无损转码+全文件重验+邻行断言·指针 results/_r323bmb_gbk_sweep.py）'
 '+CODELY 十二批热冷整编（9609→7805B·2736B verbatim multiset 零丢失·指针 results/_r323bmb_codely_archive.py）；'
 'r324 S6 维护链 29/29 rc=0（r323 法定形态）+post_review 现行红面=0（每 id 最新行口径·45 YES+5 WAIT 皆有 documented waiting_on·13 raw NO=append-only 历史翻面旧行）'
 '+state/心跳轮号三面对齐+S7 16-UU 三机同窗撞车典解（union 零丢失+take-new probed ts·resolver _r324bmb_resolve.py 16/16）；'
 '②观测（非本机车道）：bm-a R321-323=D-20260927-09 skill 双副本同步面修复（Tools 正典×.codely-cli 运行时副本 fc /b 双对一致+selftest 19/19 双绿·坑律=单侧更新=同步断链静默漂移）'
 '+r322 S0 主重落实弹（三机同窗 S6 镜像三撞 28-UU：compute_audit 撞键 200 个 content-diff=0 恒等验证→union·25 测量面 take-origin ts 深扫+3 账本 union 零丢失断言·主重落范式 push 拒→backup 分支→下轮 S0 rebase 重落 零 abort 零强推）'
 '+r323 backup 分支 fold 验证正典（git cherry patch-id 打头阵+内容锚点核·禁 merge-base --is-ancestor）+四条陈旧分支 GC；'
 'bm-c r80 T19-PHANTOM stage-2c 收割已收讫（G-REPRO 6/6+G-SET v2 构造不变量层·ΔSharpe 三员·d0_gap 归因主导·GM 裁决 stage-2a HOLD 维持）；'
 '③窗口维护面：S6 链逐轮全绿（周日/中秋休市 cutoff 09-24 合法 no-op 族）、smoke 25/25 逐轮、orders 96/96 双扫零未回执、板 0 open、池 77/77 done 零可认领、'
 '水位 py_low_board_clear 三连→13:15 insufficient_history 窗重积中（probe 节奏边·诚实态）、audit pool_starvation=供给缺口白名单（SUPPLY-NO-BREAK 照办·禁造数凑烧）、'
 '迁移 v2.2 armed editor-gated（Tuanjie 编辑器三进程 4736/12588/27660 拦+journal 分钟心跳健康·E:\\Minigame 在·E:\\Fluxgroup 空壳·窗至 09-29 12:00·勿双 arm）；'
 '④指针：**09-28 周一开市窗=新 bar 全链接力**（update_daily→live.paper REGIME_GUARD v3〔10-01 日期门前 shadow〕→t35v→t24×2→aggr 20 账→grid 5 账首拍 marks→alloc→export→scorecard→daily_report）'
 '+**T-91 s3 自动点火 09:15 首队列入场（SIG/BARS-2026-09-28 到位即确定性 replay）**+**T-87 astock 首次日续拉 15:30 后实弹**'
 '+**sina-construct prereg 起草=sina 深面板 complete+N≥250 门开后**（bm-a 三件套判定窗后 bm-b 开工·三线三判律）'
 '+10-01 月度三件套（science_audit/monthly_briefing/self_review）+REGIME_GUARD v3 日期门生效（三重门·勿手改）'
 '+T-70 中期判读 10-09+10-31 六员首检 all-HOLD+T-34 半档梯 11-01+迁移窗 09-29 12:00；R330 下次 5x 核对。\r\n')

raw2 += ROW
io.open(P, 'w', encoding='utf-8', newline='').write(raw2)

# post-write verification (byte-faithful strict re-parse)
v = io.open(P, encoding='utf-8', newline='').read()
vl = v.splitlines(True)
assert len(vl) == n0 + 1, ('line count', len(vl), n0)
assert sum(1 for l in vl if l.endswith('\r\n')) == n0_crlf + 1, 'CRLF count mismatch'
assert vl[3].startswith('> 本文件由循环每 5 轮核对更新一次（mandate 已写明）。最近核对=bm-b round 325')
assert '上一次最近核对=bm-a round 320' in vl[3]
assert '上一次最近核对=bm-a round 280' not in vl[3]
assert 'round 280 bm-a（5x 核对本轮）' in v, 'end-of-file r280 row lost'
assert 'round 325 bm-b 增量窗行' in vl[3]
assert vl[-1].startswith('- 开发队列增量窗（接续版）**round 325 bm-b')
assert vl[-1].endswith('R330 下次 5x 核对。\r\n')
print('HANDOVER 5x update PASS: cascade r325-prepended/r320-demoted/r280-pruned(EOF row intact), increment row appended; lines', n0, '->', len(vl), '| CRLF', n0_crlf, '->', n0_crlf+1)
