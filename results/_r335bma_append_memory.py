# -*- coding: utf-8 -*-
# r335 bm-a: append one pitfall entry to root CODELY.md (S4 memory step, one-line law)
import io, os

p = 'CODELY.md'
s = io.open(p, encoding='utf-8').read()
if 'ConvertFrom-Json' in s:
    print('already appended, skip (idempotent)')
else:
    entry = (
        '\n- [2026-09-27 16:2x r335 bm-a] 坑律：**PowerShell ConvertFrom-Json 会对合法 JSON 件假报 parse 失败'
        '——板面/多件扫描的权威解析一律用 python**（r335 实弹：fleet/tasks 板扫描 PS 5.1 对 '
        'T-2026-09-26-83-P1.json（11032B 合法件）报 ":\' or \'}\' expected (10641)"，同字符位 python 实读'
        '=纯 ASCII 文本无异常；python json.loads 全 93 任务件零失败=权威核验面）。How to apply：'
        '认领前板扫描/JSON 对账用 python 做，PowerShell 结果只作初筛；禁据 PS 假红开修复单或当板面缺陷上报。'
        '指针=round_reports r335+本条。'
    )
    io.open(p, 'w', encoding='utf-8', newline='').write(s + entry)
t = io.open(p, encoding='utf-8').read()
print('bytes now:', os.path.getsize(p))
print('round-trip ok:', 'ConvertFrom-Json' in t)
print('over 10KB hard line:', os.path.getsize(p) > 10240)
