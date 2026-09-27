# r368 bm-a closeout writes: round report line + CODELY pit-law entries (utf-8 file per r119 law)
import datetime, os

now = datetime.datetime.now().astimezone()
ts = now.strftime('%Y-%m-%dT%H:%M:%S+08:00')

line = (ts + ' | R368 bm-a | watermark verdict: 绿 py_low_board_clear legal-idle (py 0.3% board clear pool P1 ready->curve-bearing machine) '
    + '| did: S0 orphan tick-state adopted (r348 zero-loss) + 2-wave pull-rebase UU storm resolved per skill classifier-first '
    + '(wave-1 1-UU vs bm-c r119, wave-2 1-UU vs bm-c r120, both = runnable_pool r312 pool-entry-done-union 81+2swallowed->83 entries restored) '
    + '+ bm-b tick b5be80cd stale-model write-back swallow live-instance diagnosed (2 T-95 s2 entries claimed-in-flight vanished) '
    + 'cross-validated by bm-c r120 same-window independent verbatim recovery (double-source converged 83=83=83) '
    + '+ S3: DECISION-CHAIN-V2-SLEEVE-EXPORT sleeve-0of1 pool done-flip evidence-gated r312/r203 '
    + '(G-REPRO-REV independent reverify PASS: x1/x2 stats bit-equal p1_results.json frozen FY_BG_TP8, entries=trades=4417, sha256 recompute ok, 8792d both faces; '
    + 'artifact 423KB git-able landed per pool workers_plan; runner 00:50:01->00:50:26 atomic) '
    + '| verify: smoke 25/25 + S6 31 legs rc=0 Monday pre-market legal no-op family (2 detached self-heal spawns MF-rank+AH honest) '
    + '+ orders 99/99 double-scan zero-unacked + decisions mtime 00:10:41 no new rows + schtasks 4/4 (loop pin=8 ok, autofill 01:20 slot-miss transient recovered zero-action, IntradayMarks armed Mon 09:25) '
    + '+ claw reinstalled identical + state 368 + heartbeat epoch int verified '
    + '| next: P1 main run autofill-fired on curve-bearing machine (bm-b proven set; bm-a t34 base curves MISSING = honest exit-2 face), '
    + 'tick claim_lost_yield bookkeeping closed by control-plane flip, CODELY +2 pit-laws (rebase-continue unstaged masquerade + cross-machine tick-vs-tick pool swallow)\n')

with open('logs/iteration-loop/round_reports-bm-a.md', 'a', encoding='utf-8', newline='\n') as f:
    f.write(line)

c1 = ('- [2026-09-28 01:2x r368 bm-a] 坑律：git rebase --continue 拒绝报「You must edit all merge conflicts and then mark them as resolved using git add」'
    '但 git ls-files -u 为空、diff --cached --check 零冲突标记时——真实拦截者=任意 unstaged 改动（REBASE_MERGE continue 路径的 '
    'has_unstaged_changes sanity check 文案误导，与冲突面无关）；正典=同窗把全部 unstaged 件 git add（含他写者 tick 态收养=r348 零丢失律）'
    '后再 continue，勿死磕冲突面勿 abort（r220 律）。r368 实弹：tick 01:00:01 写后 continue 连拒 3 次，add autofill_state 后即过。'
    '指针=results/_r368bma_resolve.py。\n')

c2 = ('- [2026-09-28 01:2x r368 bm-a] 坑律：tick 自提交 keepalive（r290 腿）已成池面跨机常设写者——bm-b tick 陈旧模型写回'
    '（b5be80cd 00:52:51）吞了其祖先 8a1f8613 在册的 2 个 T-95 s2 池条目（含 claimed-in-flight 认领行），r348 家族跨机新面'
    '（r349 实例=本机 tick 吞会话编辑；本例=他机 tick 吞本机 tick 的 claim）；防御=认领后对任何后续 keepalive 提交做 claim 存活对账'
    '（git show 池面 diff 计数），吞失=r312 union 收养恢复；双源同谳实证=bm-c r120 verbatim 收养与 bm-a r368 stage2/3 union '
    '同窗独立恢复收敛 83=83=83。指针=results/_r368bma_resolve.py+commit 1e0c5289。\n')

with open('CODELY.md', 'a', encoding='utf-8', newline='\n') as f:
    f.write(c1)
    f.write(c2)

print('report appended; CODELY size:', os.path.getsize('CODELY.md'))
