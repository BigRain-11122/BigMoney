# -*- coding: utf-8 -*-
import io, re, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
blob = io.open(r'results\_r872bma_w184_prereg_src.txt', encoding='utf-8').read()
print('blob chars:', len(blob))

# key composites that the S82' old sides need (exact byte forms)
pats = [
    '已回填（r86', '预闸（pre-seat probe r8', '【r86', 'probe 回执已注记',
    'probe leg2/leg3 实跑）', '回执序数面=FORTY-', 'FORTY-', '第四十',
    'probe leg4', '冻结件】', 'probe_receipt.json', '-bma-w18', '自有波【r8',
    '**400,520 投影**', '**1.185', 'line_pre 1.18', '**0.307', '0.24509',
    '−0.09', '+0.0000**', '−0.0001**', '806,718', '804,518', '398,320',
    '共 1', '枚', '行注册', '候选', 'engine 17', 'engine_owner==bm-a 9',
    '净账本锚头', '波号 183', 'n1_w18', 'W184+ 投影', '419_404..421_403',
    '419_604..419_803', '417_404..419_403', '419_404..419_603',
    '417_204..417_403', '417_204..419_203', '417_404..417_603',
    '417_403+1', '419_403+1', '417_404+j', '419_404+j',
]
for p in pats:
    n = blob.count(p)
    if n:
        i = blob.find(p)
        seg = blob[max(0,i-30):i+len(p)+30].replace('\n', '⏎')
        print(f'{n:3d} | {p!r} | …{seg}…')
    else:
        print(f'  0 | {p!r} | ABSENT')
