import time

line = (
    time.strftime('%Y-%m-%d %H:%M:%S') + ' | r661 | ' +
    'bm-a 值守轮: S0 churn-absorb merge 净路 (bm-a daemon 7 face absorb + bm-b lane 3 face merge 零冲突); '
    'S0.5 orders 双扫 152/152 零未回执 + D-19 双面 MATCH (decisions eb14b510 / orders 82a0cef9, 实径 git show 原字节复算, K: 缺席 S4U 窗); '
    'S1 smoke 47/47; S6 31 腿全绿 rc0 (dualrun ZERO-DRIFT streak36 / compute_audit CLEAN / probe py_low_board_clear 周末合法 / '
    'CALL ORANGE_COOL sleeves4 activated0 / LIVE-20261004 ORANGE cap50 / REPORT-20261004 faces5 / t35 PASS 0 pending); '
    '生产线盘点: fund trio NULLS bm-b 在飞 (V~10-05 05:03 / Q~10-07, 心跳 05:29 实证禁碰), bm-b r641 已修 VALUE finalize 崩溃 + 预演 ALL-GREEN x3 (r652 refresh), '
    'W14 park=GM 双裁面 (sec-4 self-proof OR GM ruling), post_review 历史 NO 38 条定性 (00:00:03 同秒批) 零当窗新增 X, '
    'W115 bm-c r445 解停点火 12/12; S7 4/4 (loop pin8 no-op / watchdog 重注 / pre-commit+pre-push 双爪重装) + attrition CLEAN; '
    '| verify: state strict json.loads PASS (手术后自证) + 全链 rc0; next=10-05 V-NULLS finalize watch + 10-08 开市窗双跳; '
    '本地未达 origin commit 数=N/A (收尾 push 后 fetch 自证)\n'
)

# append-only, bytes mode, newline='' semantics via 'ab' (no CRLF translation)
with open(r'round_reports-bm-a.md', 'ab') as f:
    f.write(line.encode('utf-8'))
print('appended r661 line,', len(line.encode('utf-8')), 'bytes')
