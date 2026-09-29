# r426 bm-b hot-cold re-edit: CODELY.md >10KB hard line (10,279B > 10,240B) -> same-window integration
# Move 7 old cold-layer pointer lines verbatim to archive『指针合并归档 2026-09-29 r426 bm-b 窗批』
# + insert ONE merged pointer (r173 pattern) + append pit batch 106. Line-level zero-loss.
import io, sys

CODELY = 'CODELY.md'
ARCH = 'research/memory-archive/202609.md'

raw = open(CODELY, 'rb').read().decode('utf-8')
lines = raw.split('\n')
size_before = len(raw.encode('utf-8'))

MOVE_MARKERS = [
    '冷层指针：坑律正典 2026-09-29 一百批（r424 bm-a',
    '冷层指针：坑律正典 2026-09-29 一百零一批（r425 bm-a',
    '冷层指针：坑律正典 2026-09-29 九十八/九十九批（r207/r208 bm-c）',
    '冷层指针：坑律正典 2026-09-29 r407 bm-b 八十一批（收割回执路径源码常量解析律）',
    '冷层指针：坑律归档 2026-09-28 各窗老批指针合并行（r419 bm-a',
    '冷层指针（09-29 r407 bm-a/r403 bm-b/r406 bm-b/r193 bm-c 四窗批合并行',
    '冷层指针（09-29 r426 bm-a 水位整编·r173 范式合并行·八行 verbatim 迁',
]
moved, kept = [], []
for l in lines:
    if any(l.startswith(m) for m in MOVE_MARKERS):
        moved.append(l)
    else:
        kept.append(l)
assert len(moved) == 7, f'expected 7 pointer lines to move, got {len(moved)}'

MERGED = ('冷层指针（09-29 r426 bm-b 水位整编·r173 范式合并行·七行 verbatim 迁 archive 202609.md'
          '『指针合并归档 2026-09-29 r426 bm-b 窗批』节·零删改）：坑律正典 2026-09-28 各窗老批'
          '（二十五~五十七/五十八/晚窗/补/六十~六十九等）+2026-09-29 七十~一百零一批全段'
          '+四窗批合并行（r407/r403/r406/r193）+八十一~九十六批全段各指针行全文 verbatim=archive'
          ' 对应『坑律归档 2026-09-28 <各节>』『坑律归档 2026-09-29 <窗批>』节（本轮 CODELY.md '
          '10,279B 超 ≤10KB 硬线触发当窗即办·行级零丢失校验）。')
PIT106 = ('- [2026-09-29 13:3x r426 bm-b] 坑律一百零六批（rebase --continue 非冲突脏树拒绝面误导态'
          '+机尾 resolver 命名碰撞+marker 探针行锚定三联）：①rebase 停止态下任何 tracked 件未暂存改动'
          '（哪怕与冲突集无关·后台池工人写车道件即触）都令 git rebase --continue 报「You must edit all '
          'merge conflicts」——ls-files -u 空+报冲突语=本坑指纹（实因=unstaged 拒续·措辞误导）；处置='
          '还名/提交/还 stash 脏件后 continue 即通。②新写共享目录件前必查占位名——write_file 直写既有'
          '_r<N>_resolve*.py=静默覆盖他机正史件（实弹：覆盖 bm-a _r426_resolve.py·幸未 add+restore 零污染）；'
          '机尾后缀（bma/bmb/bmc）是防碰撞设计。③marker 探针必行锚定（^<<<<<<< ）——archive 正史 '
          'verbatim 引文可含块中 marker 串（实弹 pos 54259）·子串检查=假阳性。How to apply：continue 报'
          '冲突语先 git ls-files -u 定谳；写 results/ 新件先查占位；marker 校验一律 (?m)^ 锚。')

# insert merged pointer where the first moved line was; append pit106 at end
first_move_idx = next(i for i, l in enumerate(lines) if any(l.startswith(m) for m in MOVE_MARKERS))
out = []
inserted = False
for l in kept:
    if not inserted and l == '### Reference':
        out.append(l)
        out.append(MERGED)
        inserted = True
    else:
        out.append(l)
assert inserted
# pit106: append into Project section, after the r429 bm-a entry (before ### Reference)
ref_idx = out.index('### Reference')
out.insert(ref_idx, PIT106)

new_raw = '\n'.join(out)
size_after = len(new_raw.encode('utf-8'))
open(CODELY, 'wb').write(new_raw.encode('utf-8'))

# archive: append moved lines verbatim under new section
asec = ('\n\n## 指针合并归档 2026-09-29 r426 bm-b 窗批\n\n' + '\n\n'.join(moved) + '\n')
with open(ARCH, 'a', encoding='utf-8', newline='') as f:
    f.write(asec)

# line-level zero-loss check: all 7 moved lines present verbatim in archive
arch_raw = open(ARCH, encoding='utf-8').read()
for l in moved:
    assert l in arch_raw, f'zero-loss FAIL: {l[:40]}'
print(f'CODELY.md: {size_before}B -> {size_after}B (hard line 10,240B, {"OK" if size_after <= 10240 else "STILL OVER"})')
print(f'moved 7 pointer lines verbatim -> archive section 指针合并归档 2026-09-29 r426 bm-b 窗批; zero-loss 7/7 OK')
sys.exit(0 if size_after <= 10240 else 2)
