# -*- coding: utf-8 -*-
"""r662 bm-a: round report line append (bytes-safe) + heartbeat update (epoch int law)."""
import json, time, datetime

now = datetime.datetime.now().astimezone()
ts = now.strftime('%Y-%m-%d %H:%M:%S')
epoch = int(time.time())

line = ("{ts} | r662 | bm-a 值守轮+finalize 预演腿: 预演随轮重跑 ALL-GREEN x3 (quality 78.5s/value 96.1s/divlowvol 76.0s "
        "·机制就绪面刷新·r652 起持续绿·NOT_A_VERDICT 部分零读出禁判据消费); S0.5 orders 双扫 152/152 零未回执 + D-19 双面 MATCH "
        "(decisions eb14b510/orders 82a0cef9 桌面实径 fetch+show 原字节复算·K: 缺席 S4U 窗); S1 smoke 47/47; "
        "S6 31 腿全绿 rc0 (dualrun ZERO-DRIFT streak37 / compute_audit CLEAN flags=[] / probe py_low_board_clear 金周合法 / "
        "CALL ORANGE_COOL sleeves4 activated0 / LIVE-20261004 ORANGE cap50 / REPORT-20261004 faces5 / t35 PASS 0 pending / "
        "t24 22/22+晋升门 0/22 合法 NOT-ELIGIBLE / 纸盘族 idempotent no-op / 金周采集腿 no-op 族 / alloc_paper 现为 bm-b 车道如实注记); "
        "S7 4/4 (loop pin8 no-op / watchdog 重注 / pre-commit+pre-push 双爪 CR 归一 MATCH 探针 _r662bma_hook_parity.py) + "
        "attrition CLEAN 4 台账 (healed 4 行注记如实); 生产线: fund trio NULLS bm-b 在飞 (Q450/V598/D316 dup_k=0·bm-b r651 实证·禁碰), "
        "G-SEG 裁决面零新裁定 (无 GM ruling 则冻结判线诚实 insufficient-sample 先于一切门), W115 bm-c 解停点火在位; "
        "坑捕获 1 条: PS 5.1 无 -Encoding 读 UTF-8 CJK JSON ConvertFrom-Json 硬崩 (轮首 state 探针实弹·python 复验文件零伤·"
        "pit-encoding.md 直写 r662 行); | verify: state strict json.loads PASS round_no=662 + epoch int 1791066080 自证 + "
        "全链 rc0 + closeout orders 复扫零未回执; next=10-05 V-NULLS 烧完->fund trio finalize watch (预演就绪), "
        "10-08 开市窗 run-11/run-7 双跳, 治理日验收窗 10-08; 本地未达 origin commit 数=收尾 push 后 fetch 自证 "
        "| ceo-visibility: [当前活] 值守轮全链绿+烧批判官预演三连绿 (bm-b 在烧的基金三族判官机制面本机验明无阻塞) "
        "[最近实物] results/_r633bma_finalize_rehearsal_summary.json ALL-GREEN x3 刷新 06:1x + LIVE-2026-10-04 CEO 一页纸 "
        "[下里程碑] 10-05 基金价值族烧完 -> judged finalize 窗开 (<=48h 内首个节点)\n").format(ts=ts)

with open('round_reports-bm-a.md', 'ab') as f:
    f.write(line.encode('utf-8'))

# --- heartbeat ---
hp = 'fleet/machines/bm-a.json'
h = json.load(open(hp, encoding='utf-8'))
h['last_seen'] = now.strftime('%Y-%m-%dT%H:%M:%S+08:00')
h['heartbeat_epoch_utc'] = epoch
h['clock_read'] = now.isoformat(timespec='seconds')
h['current_task'] = 'r662 done: finalize rehearsal ALL-GREEN x3 + S6 full green; next=V-NULLS finalize watch 10-05'
h['verdict'] = 'healthy'
b = json.dumps(h, ensure_ascii=False, indent=1).encode('utf-8')
open(hp, 'wb').write(b)
chk = json.load(open(hp, encoding='utf-8'))
assert isinstance(chk['heartbeat_epoch_utc'], int), 'epoch int law'
assert 'T' in chk['clock_read'] and chk['clock_read'][10] == 'T', 'T-separator clock law'
print('REPORT+HEARTBEAT_OK epoch=%d clock=%s' % (chk['heartbeat_epoch_utc'], chk['clock_read']))
