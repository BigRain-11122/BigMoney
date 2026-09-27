# r353 bm-a: CODELY.md over 10KB hard line (10426B) -> hot/cold recompile NOW per law
# Migrate oldest full-flow pitlaw rows (r98/r99 bm-c) to archive 202609.md, leave pointer rows.
import os, re

arch_path = 'research/memory-archive/202609.md'
cod_path = 'CODELY.md'

cod = open(cod_path, encoding='utf-8').read()

def extract_row(marker):
    # returns the full line starting with '- [ ... <marker> ...]' and removes it
    global cod
    lines = cod.split('\n')
    hit = [i for i, l in enumerate(lines) if marker in l and l.startswith('- [')]
    assert len(hit) == 1, f'marker {marker}: {len(hit)} hits'
    row = lines[hit[0]]
    del lines[hit[0]]
    cod = '\n'.join(lines)
    return row

r98 = extract_row('r98 bm-c')
r99 = extract_row('r99 bm-c')

pointers = (
    '- [2026-09-27 19:11 r98 bm-c] 坑律：轮首机器身份锚定+本机链脚本自持本机路径——全文 verbatim=archive 202609.md『坑律归档 2026-09-27 二十八批』节（r353 当窗整编外迁）。\n'
    '- [2026-09-27 19:4x r99 bm-c] 坑律：git 数据面双死窗处置三径+PS 展开坑（HEAD^{tree} 必加引号）——全文 verbatim=archive 202609.md『坑律归档 2026-09-27 二十八批』节（r353 当窗整编外迁）。'
)

# insert pointers where r98/r99 used to sit (keep chronological position: right before the r100 row)
lines = cod.split('\n')
idx = [i for i, l in enumerate(lines) if 'r100 bm-c' in l and l.startswith('- [')]
assert len(idx) == 1, f'r100 anchor: {len(idx)} hits'
lines.insert(idx[0], pointers)
cod = '\n'.join(lines)

sec = (
    "\n\n## 坑律归档 2026-09-27 二十八批（r353 bm-a 当窗热冷整编·CODELY.md 超 10KB 硬线触发·行级零丢失）\n\n"
    + r98 + '\n'
    + r99 + '\n'
)
with open(arch_path, 'a', encoding='utf-8') as f:
    f.write(sec)
with open(cod_path, 'w', encoding='utf-8') as f:
    f.write(cod)

size = os.path.getsize(cod_path)
assert r98 in open(arch_path, encoding='utf-8').read(), 'archive migration lost r98 row'
assert r99 in open(arch_path, encoding='utf-8').read(), 'archive migration lost r99 row'
assert '轮首机器身份锚定' in cod and 'git 数据面双死窗' in cod, 'pointer rows missing'
print('migrated r98+r99 full rows -> archive; CODELY.md now:', size, 'bytes')
assert size <= 10240, f'still over 10KB hard line: {size}'
print('under hard line OK')
