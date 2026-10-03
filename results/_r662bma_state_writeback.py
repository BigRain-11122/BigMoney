# -*- coding: utf-8 -*-
"""r662 bm-a closeout: state round_no 662 write-back (r645 programmatic+selfverify law)."""
import json, time, datetime

p = 'state-bm-a.json'
d = json.load(open(p, encoding='utf-8'))
now = datetime.datetime.now().astimezone().isoformat(timespec='seconds')
epoch = int(time.time())

d['round_no'] = 662
d['did'] = ("r662 值守轮+预演腿: fund-trio finalize 预演随轮重跑 ALL-GREEN x3 (quality 78.5s / value 96.1s / divlowvol 76.0s, "
            "机制就绪面刷新·r652 以来持续绿); S6 全链 rc0 (dualrun ZERO-DRIFT streak37; compute_audit CLEAN flags=[]; "
            "probe py_low_board_clear 金周合法 idle); S0.5 orders 双扫 152/152 零未回执; D-19 双面 MATCH "
            "(decisions eb14b510/orders 82a0cef9 实径 git show 原字节复算·K: 缺席 S4U 窗·桌面实径=C:\\Users\\sjs20\\Desktop\\FluxGroup); "
            "G-SEG 裁决面零新裁定 (MSG-2026-10-03-1720 站立·finalize 窗 10-06..09 前无 GM ruling 则冻结判线诚实 insufficient-sample); "
            "坑捕获: PS 5.1 无 -Encoding 读 UTF-8 CJK JSON ConvertFrom-Json 硬崩 (state 轮首探针实弹·python 复验文件零伤·"
            "pit-encoding 直写 1 条)")
d['verify'] = ("S1 smoke 47/47; 预演 ALL-GREEN x3; S6 31 腿 rc0; attrition CLEAN 4 台账 (healed 4 行注记如实); "
               "S7 4/4 (loop pin8 no-op + watchdog 重注 + 双爪 CR 归一 MATCH 探针 results/_r662bma_hook_parity.py); "
               "heartbeat epoch int 自证+T 钟自证")
d['next'] = ("10-05 V-NULLS 烧完窗-> fund trio finalize watch (预演 ALL-GREEN x3 持续; G1 burns pending w/ r638 fallback); "
             "10-08 开市窗 run-11/run-7 双跳 + 治理日验收窗; W14/CFO 探针=GM 裁决面")
d['last_round_at'] = now
d['current_task'] = "r662: 值守轮+finalize 预演 ALL-GREEN x3; next=V-NULLS finalize watch + 10-08 开市窗双跳"
d['updated'] = now[:19].replace('T', ' ')
d['last_round'] = 661
d['heartbeat_epoch_utc'] = epoch

b = json.dumps(d, ensure_ascii=False, indent=1).encode('utf-8')
open(p, 'wb').write(b)
chk = json.load(open(p, encoding='utf-8'))
assert isinstance(chk['heartbeat_epoch_utc'], int), 'epoch must be int'
assert chk['round_no'] == 662
print('STATE_OK round_no=662 epoch=%d (int self-verified)' % chk['heartbeat_epoch_utc'])
