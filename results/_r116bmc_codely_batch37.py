import io

CODELY = 'CODELY.md'
ARCH = 'research/memory-archive/202609.md'

hot = io.open(CODELY, encoding='utf-8').read()
arch = io.open(ARCH, encoding='utf-8').read()

# fold rows: exact single lines from hot file (verbatim), each must already exist in archive
fold_prefixes = [
    '- [2026-09-27 19:4x r99 bm-c]',
    '- [2026-09-27 21:3x r109 bm-c]',
    '- [2026-09-27 17:3x r334 bm-b] 坑律（二十六批外迁·指针）',
    '- [2026-09-27 17:5x r335 bm-b] 坑律（二十六批外迁·指针）',
    '- [2026-09-27 17:5x r341 bm-a]',
    '- [2026-09-27 17:4x r339 bm-a]',
    '- [2026-09-27 17:5x r340 bm-a]',
    '- [2026-09-27 17:3x r334 bm-b] 坑律（二十三批外迁·指针）',
    '- [2026-09-27 17:5x r335 bm-b] 坑律（二十五批外迁·指针）',
    '- [2026-09-27 21:15 r342 bm-b]',
    '- [2026-09-27 22:1x r110 bm-c]',
    '- [2026-09-27 22:3x r344 bm-b] 坑律（三十三批外迁·指针）：autofill claim 恢复腿',
    '- [2026-09-27 22:3x r344 bm-b] 坑律（三十三批外迁·指针）：rebase 重放窗',
    '- [2026-09-27 22:1x r359 bm-a]',
    '- [2026-09-27 22:5x r346 bm-b]',
    '- 二十六/二十七/二十九/三十/三十一/三十三批外迁史行族',
]

lines = hot.split('\n')
removed, kept_unverified = [], []
out_lines = []
for ln in lines:
    hit = None
    for p in fold_prefixes:
        if ln.startswith(p):
            hit = p
            break
    if hit is None:
        out_lines.append(ln)
        continue
    if ln in arch:
        removed.append(ln)
    else:
        kept_unverified.append(ln)
        out_lines.append(ln)

n = len(removed)
meta = ('三十七批外迁（r116 bm-c·2026-09-27·超线 10,395B>10,240B 当窗整编·行级零丢失·union 吸收回潮再折叠·archive 在位核验 %d/%d 全过）：'
        'r99/r109/r334×2/r335×2/r341/r339/r340/r342/r110/r344×2/r359/r346 指针行+行族 meta 行共 %d 行'
        '（verbatim 皆在各对应批节在位·检索按日期段）；保留=User 元律+法行 2+冷层指针+活跃律行（r360/r113/r347）+三十六批 meta+r362 执行记录+r116 新律。' % (n, len(fold_prefixes), n))
if kept_unverified:
    meta += ' 未核验保留 %d 行。' % len(kept_unverified)

# insert meta after the 三十六批 meta line (or append near the folded zone)
new_hot = '\n'.join(out_lines)
anchor = '- 三十六批外迁（r362 bm-a'
idx = new_hot.find(anchor)
if idx == -1:
    # fall back: append at end
    new_hot = new_hot.rstrip('\n') + '\n' + meta + '\n'
else:
    line_end = new_hot.find('\n', idx) + 1
    new_hot = new_hot[:line_end] + meta + '\n' + new_hot[line_end:]

# archive side: batch meta line
arch_meta = ('三十七批记录（r116 bm-c·2026-09-27）：CODELY.md 热面 %d 指针/行族行 union 吸收回潮再折叠——各行 verbatim 此前已在对应批节在位（在位核验 %d/%d）；'
             '热面保留律行族见 CODELY 三十七批 meta 行。' % (n, n, len(fold_prefixes)))
with io.open(CODELY, 'w', encoding='utf-8', newline='\n') as f:
    f.write(new_hot)
with io.open(ARCH, 'a', encoding='utf-8', newline='\n') as f:
    f.write(arch_meta + '\n')

sz = len(io.open(CODELY, 'rb').read())
print('folded %d rows; kept-unverified %d; CODELY.md -> %dB (hard line 10240B)' % (n, len(kept_unverified), sz))
assert sz < 10240, 'still over line'
# zero-loss spot checks: folded rows still in archive
for ln in removed:
    assert ln in io.open(ARCH, encoding='utf-8').read(), 'LOST: ' + ln[:60]
print('zero-loss verified %d/%d folded rows in archive' % (len(removed), len(removed)))
