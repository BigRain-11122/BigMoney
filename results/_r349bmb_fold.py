# -*- coding: utf-8 -*-
"""r349 bm-b hot/cold fold (38th batch, O-20260927-0230 <=10KB hard line):
CODELY.md 10,810B > 10,240B after storm direct-concat -> fold 4 flowing lines
(execution-records + yield-ruling addendum, D-20260924-01 flowing type) verbatim
into research/memory-archive/202609.md '三十八批' section; leave ONE meta pointer
line in CODELY. Zero line loss, byte-verbatim archive, parse checks."""
import io, os, re, sys

CODELY = 'CODELY.md'
ARCH = 'research/memory-archive/202609.md'

ct = io.open(CODELY, encoding='utf-8').read()
lines = ct.split('\n')

FOLD_KEYS = [
    ('[2026-09-27 23:1x r362 bm-a] 执行记录', 'r362 执行记录'),
    ('[2026-09-28 00:2x r365 bm-a] 执行记录', 'r365 执行记录'),
    ('[2026-09-28 00:2x r365 bm-a] 勘误追加', 'r365 勘误追加'),
    ('[2026-09-28 00:2x r349 bm-b] 执行记录', 'r349 执行记录'),
]
found = {k: [] for k, _ in FOLD_KEYS}
keep = []
for ln in lines:
    hit = False
    for key, _ in FOLD_KEYS:
        stem = key.split('] ', 1)[0] + '] ' + key.split('] ', 1)[1]
        if ln.startswith('- [') and stem in ln:
            found[key].append(ln)
            hit = True
            break
    if not hit:
        keep.append(ln)

for key, name in FOLD_KEYS:
    n = len(found[key])
    assert n == 1, f'fold key {name}: expected exactly 1 line, found {n}'
folded = [found[key][0] for key, _ in FOLD_KEYS]
total_fold_bytes = sum(len(l.encode('utf-8')) for l in folded)
print(f'folded {len(folded)} lines, {total_fold_bytes}B')

meta = ('- 三十八批外迁（r349 bm-b·2026-09-28·风暴直拼后超线 10,810B>10,240B 当窗整编·行级零丢失·'
        '让号依 in-tree 实况：origin 三十六=r362 bm-a+三十七=r116 bm-c 在位·本批取三十八）：'
        'r362 bm-a 执行记录+r365 bm-a 执行记录+r365 bm-a 勘误追加+r349 bm-b 执行记录 共 4 行流水行 '
        f'verbatim=archive 202609.md『坑律归档 2026-09-28 三十八批』节；保留=User 元律+法行+冷层指针+'
        '活跃律行（r344×2/r359/r360/r346/r113/r347/r116/r365坑/r118/r349坑）+三十六/三十七批 meta。')

# insert meta where the first folded line used to sit: append after last kept law line
# simplest: put meta at the position of the earliest removed line. Rebuild: we walk keep
# and insert meta before the first line that starts with '- [2026-09-27 23:5x r116 bm-c] 坑律'
out = []
inserted = False
for ln in keep:
    if not inserted and ln.startswith('- [2026-09-27 23:5x r116 bm-c] 坑律'):
        out.append(meta)
        out.append('')
        inserted = True
    # collapse triple blank lines created by removals
    if ln == '' and out and out[-1] == '' and len(out) >= 2 and out[-2] == '':
        continue
    out.append(ln)
if not inserted:
    out.append(meta)
new_codely = '\n'.join(out)
if not new_codely.endswith('\n'):
    new_codely += '\n'

arch = io.open(ARCH, encoding='utf-8').read()
section = '\n\n## 坑律归档 2026-09-28 三十八批（r349 bm-b 热冷整编·流水行 4 条 verbatim·行级零丢失）\n\n' + '\n\n'.join(folded) + '\n'
new_arch = arch.rstrip('\n') + section
assert new_arch.count(folded[0]) == 1 and arch.count(folded[0]) == 0, 'archive verbatim uniqueness check'
for f in folded:
    assert f in new_arch, 'zero-loss check: every folded line must appear verbatim in archive'

io.open(CODELY, 'w', encoding='utf-8', newline='').write(new_codely)
io.open(ARCH, 'w', encoding='utf-8', newline='').write(new_arch)

sz = os.path.getsize(CODELY)
print('CODELY.md new size:', sz, '->', 'UNDER-LIMIT' if sz <= 10240 else 'STILL OVER')
print('archive new size:', os.path.getsize(ARCH))
assert sz <= 10240, 'fold failed to bring CODELY under hard line'
print('fold OK, zero-loss verified')
