# -*- coding: utf-8 -*-
# r877 bm-c: S7 tail-scan order catch -- ack O-20261011-1436-bm-c (lane discipline)
import io
import json
from datetime import datetime, timezone, timedelta

TZ = timezone(timedelta(hours=8))
ISO = datetime.now(TZ).strftime('%Y-%m-%dT%H:%M:%S+08:00')

# 1) heartbeat orders_ack append
p = r'fleet\machines\bm-c.json'
with io.open(p, 'r', encoding='utf-8') as fh:
    d = json.load(fh)
oa = d.setdefault('orders_ack', [])
name = 'O-20261011-1436-bm-c.md'
if name not in oa:
    oa.append(name)
d['orders_ack_last'] = name + ' | r877 tail-scan catch: BigStream MV/自媒体 domain (executor=bm-c interactive window author + bm-a lanes; quant loop non-executor zero action; §2 V1 takeover receipt duty=bm-a 30min window)'
tmp = p + '.tmp'
with io.open(tmp, 'w', encoding='utf-8', newline='') as fh:
    json.dump(d, fh, ensure_ascii=False, indent=1)
with io.open(tmp, 'r', encoding='utf-8') as fh:
    json.load(fh)
import os
os.replace(tmp, p)

# 2) round-report addendum line
LINE = ('\n' + ISO + ' | r877 bm-c addendum | S7 收尾双扫令捕获: O-20261011-1436-bm-c（CEO 令 14:0x MV 并行+自媒体收口）'
        '——§1 星晴/可爱女人分镜+KF=bm-c 交互窗已认领域·§2 V1《慢慢踩》收口接管=bm-c 交互窗自任（2 轮兜底执法·30min 让位窗对 bm-a）'
        '·§3 mv0001 wave1 六镜任务 ID 遗失交代=@bm-a 装配线——本 quant 循环=非执行体零动作（BigStream 内容产线归交互窗/MiniGame lane·'
        'orders_ack 已回执）；O 件 14:36 落盘=交互窗在飞件·本轮不代提交由其自收 | 回执面=本行+心跳 orders_ack | 下轮指针=r878 常规')
with io.open(r'logs\iteration-loop\round_reports-bm-c.md', 'a', encoding='utf-8', newline='') as fh:
    fh.write(LINE + '\n')
print('order ack OK:', ISO)
