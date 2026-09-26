# -*- coding: utf-8 -*-
"""R241 S4: append new lesson + D-20260925-01(4) hot-cold reorg (>50KB trigger).

Steps:
1. Append R241 dead-resolver adoption lesson (keep-type) to root CODELY.md.
2. Move 6 flow-type lines (execution records / data-face closures / yield
   rulings) to research/memory-archive/202609.md with migration header.
3. Zero-loss verification: moved lines byte-present in archive, absent from
   root, counts reconcile. EOL mirror CRLF both files (r223 law).
"""
import io

ROOT = 'CODELY.md'
ARCH = 'research/memory-archive/202609.md'
NEW = (' - [2026-09-26 11:1x] 坑律（bm-a R241·死轮 rebase 残骸收养·resolver 半程态·'
       'r225 家族补篇·E1 收养前自验）：**收养死轮冲突解残骸先验磁盘内容对 blob 正典并集再动手'
       '——resolver 死在 write 与 git add 之间（13/14 已 add、CODELY.md 已写盘未 add）时，'
       '重derive 磁盘 vs :2/:3 union 恒等=直接补 add 续走，禁整套重解（重解=白干+双解分叉面）**；'
       '连带=三波 push 撞车窗内 machine/<id>-r<N> fallback 落档后、同轮他机轮中段窗（其 S7 push 已过后）'
       '再 rebase 落 main 可成（本轮撞车解三连实弹：rebase1 残骸收养→rebase2→machine 分支→rebase3 '
       '落 main db38b1aa）。指针=results/_r240_resolve2.py（死轮 13/14 态）+_r241bma_resolve{,3}.py')

FLOW_PREFIXES = (
    (' - [2026-09-26 04:2x] 数据面收线（bm-a R216·T-71 sina 四档资金流候选 FRESH', '数据面收线 R216'),
    (' - [2026-09-26 06:2x] 数据面/R118 证据升级（bm-a R224·T-72 prereg open-item 批腿', '数据面 R224'),
    (' - [2026-09-26 06:5x] 数据面（bm-a R225·T-72 prereg open-item wave-2·sina 四档分组官方面', '数据面 R225'),
    (' - [2026-09-26 10:0x] 执行记录（bm-a R239·CEO 三连令同轮执行', '执行记录 R239'),
    (' - [2026-09-26 10:1x] 勘误（bm-a R239 addendum·T-77 撞认领让路', '勘误 R239'),
    (' - [2026-09-26 10:25] 执行记录（bm-b r240·O-20260926-0958 交易管理解锁令回执', '执行记录 r240'),
)

root = io.open(ROOT, encoding='utf-8', newline='').read()
arch = io.open(ARCH, encoding='utf-8', newline='').read()
assert '\r\n' in root and '\r\n' in arch, 'both files must stay CRLF'

rlines = root.split('\r\n')
moved = []
keep = []
for l in rlines:
    ls = l.lstrip()
    hit = None
    for pref, name in FLOW_PREFIXES:
        if ls.startswith(pref.lstrip()):
            hit = (l, name)
            break
    if hit:
        moved.append(hit)
    else:
        keep.append(l)

assert len(moved) == 6, f'expected 6 flow lines, got {len(moved)}: {[m[1] for m in moved]}'

# append new lesson at tail (before trailing empty line if any)
if keep and keep[-1] == '':
    keep.insert(-1, NEW)
else:
    keep.append(NEW)

new_root = '\r\n'.join(keep)
io.open(ROOT, 'w', encoding='utf-8', newline='').write(new_root)

hdr = ('<!-- R241 热冷整编迁入（D-20260924-01 范式·行级零丢失·源=根 CODELY.md '
       'Reference 节·2026-09-26 11:1x·触发=>50KB 水位 D-20260925-01(4) -->')
arch_lines = arch.split('\r\n')
if arch_lines and arch_lines[-1] == '':
    arch_lines.insert(-1, hdr)
    for l, _ in moved:
        arch_lines.insert(-1, l)
else:
    arch_lines.append(hdr)
    for l, _ in moved:
        arch_lines.append(l)
new_arch = '\r\n'.join(arch_lines)
io.open(ARCH, 'w', encoding='utf-8', newline='').write(new_arch)

# zero-loss verification
root2 = io.open(ROOT, encoding='utf-8', newline='').read()
arch2 = io.open(ARCH, encoding='utf-8', newline='').read()
ok = True
for l, name in moved:
    in_arch = l in arch2
    in_root = l in root2
    print(f'{name}: in_archive={in_arch} absent_from_root={not in_root}')
    ok = ok and in_arch and (not in_root)
print('moved lines:', len(moved), '| new lesson present in root:', NEW in root2)
import os
print('root size after:', os.path.getsize(ROOT), 'bytes (was 50797+~590 new-6 moved)')
assert ok, 'ZERO-LOSS VERIFICATION FAILED'
print('ZERO-LOSS OK')
