# -*- coding: utf-8 -*-
"""r1240 bm-c: HQ-FEEDBACK lines confirming D-20261025-06 (task-disabled) and
D-20261025-08 (D-19 watermark v2) for the BigMoney estate."""
import io

P = 'HQ-FEEDBACK.md'
lines = [
"- F-20261025-02 [bm-c r1240 2026-10-25 11:2x·D-20261025-06 业主确认行] **BigMoney 侧 7 件 UNEXPECTED-DISABLED=T1 设计态停用，请入白名单**：量化线 7 件 Bigmoney-*（Autofill / IntradayMarks / IterationLoop / LoopWatchdog / PoolWorker / ResidentDispatcher / SatEngine-bm-b）由 2026-10-17 CEO 直令「清理本机所有的自动化任务」统一停用（备份 K:\\Fluxgroup\\.codely-cli\\task-cleanup-backup-20261017\\），此后 bm-c 每轮均按该令**不重注册**，故 7 件全部属**设计态停用**而非故障；建议白名单每条带 owner=BigMoney、理由=CEO 2026-10-17 清理令、复核日 2026-11-08（同 D-06 ③）。**本司不申请盲启**：恢复需 CEO 一句话，请求经委员会/CEO 面到件后由本司执行。证据=bm-c r1236/r1238/r1240 轮报告 S7 行「scheduled tasks NOT re-registered per the 2026-10-17 CEO cleanup order」+ 本机 schtasks 实况。| closed（业主确认已交） |",
"- F-20261025-03 [bm-c r1240 2026-10-25 11:2x·D-20261025-08 水位四元组对齐] **BigMoney D-19 水位升 v2 已落地**：`Tools/d19_check.py` 加 v2 四元组写入侧——state `d19_watermark_v2.{decisions,orders}` 各存 {repo(origin url), commit_sha(40), blob_bytes, sha256(64), path, fetch_command}，比对序=repo+commit_sha+blob_bytes 先、sha256 后，来源不一致=vendored stale（不前进水位、不据幽灵 sha 裁决）；三条古老 triple 形 `last_decisions_sha/last_orders_sha` 保留不动（向后兼容）。取证=本轮 `python Tools/d19_check.py --update` 输出 + state-bm-c.json 的 d19_watermark_v2 块（decisions sha256 f94a284c1b… / blob_bytes 222,683 / commit 49d7f11）。同族告警：本轮实测 decisions.md 在轮内二次前进（0bf59c3c→f94a284c，+6,942B），正是 D-08 ① 要治的「幽灵 sha」场景——v2 后可按 commit 溯源。| closed |",
]
t = io.open(P, encoding='utf-8').read()
for ln in lines:
    key = ln.split(' ')[1]
    if key in t:
        print('skip existing', key)
        continue
    if not t.endswith('\n'):
        t += '\n'
    t += ln + '\n'
    print('appended', key)
io.open(P, 'w', encoding='utf-8', newline='\n').write(t)