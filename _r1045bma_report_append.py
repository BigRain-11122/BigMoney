# r1045 bm-a: round report line + CODELY pit row appends (fresh read-append, single-writer faces)
import io

rr = 'round_reports-bm-a.md'
line = ('2026-10-18T04:48:15+08:00 | r1045 bm-a (dept:工程·D-19摄入链缺陷根治+回执簿记康复+事故值守) | '
 'WM-VERDICT: 绿(red=false lane=healthy; satengine ALIVE queue0 idle; idle two_read_red consumed via --worked(0)=d19修复产品工) | '
 '当前活=r1045: S0吸收+rebase(watermark_red UU r1028 newer-wins; behind-0 onto 3917a974e 5commits含W265 PREREG FREEZE bm-c) '
 '+ O-20261018-0348-bm-a回执(bm-a-proxy升级令·@bm-b第一动作; MSG-0216仍不在origin=O-0137账号保持开启watch1) '
 '+ D-19 orders增量消费(4行:V5.3-C01交付/O-2110记账/bm-c resume回执/@bm-c BM仓解锁行——零BigMoney新动作; dec 1d4741e4 hold) '
 '+ 水位推进ord=eae5ac55(update --advance读回恒等) '
 '+ D19探针静默rc0缺陷根治: Win/Py3.14宿主吞直传子进程stdout(父print落地子print消失·重定向0字节实证)——cmd_probe依赖直传=循环把静默当hold,r1044漏掉4个集团orders提交01:52-04:3x未消费; 修=capture+relay(_relay_child_streams)·selftest 15->17/17 PASS·live probe现打印orders_changed=true '
 '+ orders_ack清单回归治愈: r1041事故态重建把107->1截断(b9cb641d8),扫描器99假P0债; 从r1040 git face 8812bda52 verbatim重建+3=110条,复扫CLEAN(101 orders 0 unacked 0 stale) '
 '+ S6 42/42 rc0(driver _r1045bma_s6chain.ps1 04:41-04:46)+smoke 49/49+loop pin=8 no-op+watchdog Running(S4U flip拒绝访问=既有carried面C-20261016-04)+claws match x2+orphan face=0(19py faces) '
 '| 最近实物=scripts/d19_watermark.py(探针中继修复+selftest 17/17·04:38) + results/_r1045bma_s6chain_rc.log(42/42 rc0·04:46) '
 '| 下个里程碑=O-0137账号关闭(候bm-b MSG-0216落链+bm-c回执核验)+W265 splice+finalize落地(bm-c下窗第一动作)→W266 owner命名(per W265 sec.7)·窗内48h '
 '| 本地未达origin commit数=0(closeout push后自证)')
with io.open(rr, 'a', encoding='utf-8') as f:
    f.write(line + '\n')
print('round report appended')

cl = 'CODELY.md'
row = ('\n- [2026-10-18 04:5x r1045 bm-a] **直传子进程 stdout 吞噬坑（Win/Py3.14 宿主面·D-19 摄入链实弹）**：'
 '本机 python 父进程 spawn 子进程（subprocess.run 不带 capture）时，子进程的 print 不落父进程继承句柄——'
 '父进程自身 print 正常落地、子进程输出即使重定向到文件也 0 字节（实证：嵌套 subprocess.run spawn print(123) 的 123 消失）。'
 '后果面：scripts/d19_watermark.py cmd_probe 依赖直传=循环把「静默+rc0」读成 zero-delta hold，r1044 实漏 4 个集团 orders 提交（01:52-04:3x 未消费）。'
 '正法=凡需消费子进程输出的工具一律 capture_output=True+父进程 re-print 中继（修复=_relay_child_streams+selftest L16/L17）；rc 契约不变。'
 'How to apply：仓内任何「spawn 子进程并依赖其 stdout 透传」的工具面审计以此坑为准；子进程 verdict 面优先走证据文件（d19 cmd_update 先例=capture+读 PROBE_OUT 本就安全）。')
with io.open(cl, 'a', encoding='utf-8') as f:
    f.write(row + '\n')
print('CODELY pit row appended')
