import io

CODELY = 'CODELY.md'
ARCH = 'research/memory-archive/202609.md'

codely = io.open(CODELY, encoding='utf-8').read()
arch = io.open(ARCH, encoding='utf-8').read()

prefixes = [
    '- 冷层指针：r240 tick 15min 时限强杀',
    '- 冷层指针：r443 jsonl 追加写吞换行腐败坑',
    '- 冷层指针：r455 S5 轮报告路径孤儿坑',
    '- 冷层指针：r433 同门换用法反向证伪律',
]

lines = codely.split('\n')
moved = []
kept = []
for ln in lines:
    hit = None
    for p in prefixes:
        if ln.startswith(p):
            hit = p
            break
    if hit:
        moved.append(ln)
    else:
        kept.append(ln)

assert len(moved) == 4, 'expected 4 moved lines, got %d: %r' % (len(moved), moved)
for p in prefixes:
    assert sum(1 for m in moved if m.startswith(p)) == 1, 'dup or missing: ' + p
    assert arch.count(next(m for m in moved if m.startswith(p))) == 0, 'already in archive: ' + p

section = '\n\n## 热冷整编 2026-09-30 r448 bm-b 窗批\n\n（r448 bm-b 收尾窗热冷整编·CODELY 10,601B>10,240B 硬线当窗即办·指针合并归档 moved 4 (r240 时限杀律指针 + r443 jsonl 追加写坑指针 + r455 S5 路径孤儿坑指针 + r433/431/443/438/233 五条复合指针)/lost 0·行级零丢失校验=四行逐字节在档。本窗新增热条=族选防重 rg 键面补律（r448 bm-b·W8 泊位实弹）留热层在位。）\n\n' + '\n\n'.join(moved) + '\n'

arch_new = arch.rstrip('\n') + section
codely_new = '\n'.join(kept)

# zero-loss verify
for m in moved:
    assert arch_new.count(m) == 1, 'moved line not exactly once in archive'
    assert codely_new.count(m) == 0, 'moved line still in CODELY'

io.open(ARCH, 'w', encoding='utf-8', newline='\n').write(arch_new)
io.open(CODELY, 'w', encoding='utf-8', newline='\n').write(codely_new)

import os
print('CODELY.md now:', os.path.getsize(CODELY), 'bytes (line 10,240)')
print('archive now:', os.path.getsize(ARCH), 'bytes')
print('moved:', len(moved), '| zero-loss verified')
