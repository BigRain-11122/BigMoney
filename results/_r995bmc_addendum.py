# -*- coding: utf-8 -*-
"""r995 附产 line: push saga disclosure + JSON integrity check of rebase-resolved faces at HEAD."""
import json, subprocess, datetime, sys

ROOT = r'K:\Fluxgroup\FluxGroup\quant\bigmoney'
G = r'C:\Program Files\Git\cmd\git.exe'

# 1) integrity: rebase-resolved/merged faces at HEAD must parse
faces = ['results/token_usage.json', 'results/compute_audit.json',
         'results/_attrition_guard_scan.json', 'results/fundamental_b_layer_filter.json',
         'fleet/machines/bm-c.json', 'state-bm-c.json']
for f in faces:
    r = subprocess.run([G, '-C', ROOT, 'show', 'HEAD:' + f], capture_output=True)
    json.loads(r.stdout.decode('utf-8'))
print('JSON integrity at HEAD: %d/%d OK' % (len(faces), len(faces)))

now = datetime.datetime.now().astimezone().isoformat(timespec='seconds')
line = ("{0} | r995 附产 | bm-c | closeout push saga 披露（诚实面·r992 附产先例）：首轮 push 撞 bm-b autofill 竞速（origin 10:4x 三连推）non-FF -> "
        "rebase --autostash origin/main 撞 4 共享再生面 UU（_attrition_guard_scan/compute_audit/fundamental_b_layer_filter 三面 ts 双查 "
        "live-wins 取我侧 10:4x>bm-b 10:2x-10:39；token_usage.json=per-machine 子键 union-merge〔machines 键集双側恒等·scalars newer-wins "
        "10:40:42·_r995bmc_tu_merge.py 落盘〕）-> rebase --continue 幻影拒=r990 已录坑（daemon unstaged churn 真因）-> 原子 add-A+-c "
        "core.editor=true continue 收束 9e54cb836 -> 二轮 push 再撞 claw+non-FF -> autostash pop 冲突 3 daemon 滚动面 "
        "（machine-health/satengine face+state=daemon 每 tick 整写再生件）checkout --ours 清树+stash@{{0}} 留置（r959/r918 先例·零 treasure "
        "损失）-> 原子 fetch+rebase+push 链终落 8d58630a1（1a68320b1..8d58630a1）·送达自证 rev-list=0 + state blob origin==HEAD · "
        "全程零 --no-verify（claw 两过）·JSON 完整性 6/6 | counter 维持 996（同窗）").format(now)

with open(ROOT + r'\round_reports-bm-c.md', 'a', encoding='utf-8') as f:
    f.write(line + '\n')
print('APPENDED r995 附产 line')
