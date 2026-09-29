# -*- coding: utf-8 -*-
"""r438 bm-b: CODELY.md hot-cold re-arch (water-line 10,216B > 10KB hard
line -> in-window per D-20260925-01(4)). Migrates 3 verdict/pit entries
verbatim to research/memory-archive/202609.md, leaves a cold pointer in
place, verifies line-level zero loss both sides."""
src = open('CODELY.md', encoding='utf-8').read()
lines = src.split('\n')
pref = {
 'r442': '- [2026-09-29 19:3x r442 bm-a] A10',
 'r234': '- [2026-09-29 19:4x r234 bm-c] VSTD20_q20',
 'r233': '- [2026-09-29 19:2x r233 bm-c]',
}
idx = {}
for i, l in enumerate(lines):
    for k, p in pref.items():
        if l.startswith(p):
            idx[k] = i
assert len(idx) == 3, idx
move_idx = sorted(idx.values())
moved = [lines[i] for i in move_idx]
pointer = ('- 冷层指针：坑律/流水三件（r442 bm-a A10 组合臂判负+判据线 NaN 静默退化双坑律·'
           'r234 bm-c VSTD20_q20 W11 甄别判负·r233 bm-c 阶梯目录消耗态盲区+既有件覆盖拦截）'
           '全文 verbatim=archive 202609.md『热冷整编 2026-09-29 r438 bm-b 窗批』节'
           '（水位 10,216B 超 ≤10KB 硬线当窗即办·行级零丢失校验）。')
out = []
for i, l in enumerate(lines):
    if i in move_idx:
        if i == move_idx[0]:
            out.append(pointer)
        continue
    out.append(l)
new_src = '\n'.join(out)
open('CODELY.md', 'w', encoding='utf-8', newline='').write(new_src)
sec = ['', '## 热冷整编 2026-09-29 r438 bm-b 窗批（CODELY.md 10,216B 超 ≤10KB 硬线当窗即办·行级零丢失迁移）', '']
sec += moved
sec += ['', '（r438 bm-b 窗行级零丢失校验：3 条 verbatim 迁移，源条目删除后仅指针替换零改动）', '']
with open('research/memory-archive/202609.md', 'a', encoding='utf-8') as f:
    f.write('\n'.join(sec))
arc = open('research/memory-archive/202609.md', encoding='utf-8').read()
ok = all(m in arc for m in moved)
gone = all(m not in new_src for m in moved)
print('verbatim-in-archive:', ok, '| removed-from-source:', gone,
      '| new CODELY size:', len(new_src.encode('utf-8')), 'B')
