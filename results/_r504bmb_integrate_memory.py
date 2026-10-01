"""r504 bm-b 热冷整编窗批（D-20260925-01④ 50KB 触发·r444 范式·行级零丢失校验）：
可迁集定谳=仅 r305（rebase --continue 假拒绝坑——r501 变体①③已含其净路+r507 中段泛化，双条引用）；
流水/回执面已被 r514 bm-a 窗批（12:5x）掏净，残余=在役坑律正典（结构性，禁为字节数归档活律）。
操作：r305 行 verbatim 迁 archive 202610.md 新窗批节 + CODELY.md 留 r444 式指针行。"""
import re, os

REPO = r'C:\Fluxgroup\FluxGroup\quant\bigmoney'
CM = REPO + r'\CODELY.md'
AR = REPO + r'\research\memory-archive\202610.md'

cm_lines = open(CM, encoding='utf-8').read().splitlines()
orig_n = len(cm_lines)

# locate the r305 entry line (full line, starts with '- [2026-10-01 07:4x r305 bm-c]')
idx = [i for i, l in enumerate(cm_lines) if l.startswith('- [2026-10-01 07:4x r305 bm-c]')]
assert len(idx) == 1, 'r305 line not unique: %r' % idx
r305_line = cm_lines[idx[0]]
print('r305 line: len=%d at line %d' % (len(r305_line), idx[0] + 1))

pointer_line = (
    '- 冷层指针（r504 合并·r444 范式）：r305 bm-c rebase --continue 假拒绝坑（净路已全文吸收于 r501 '
    '变体①③+r507 中段泛化，双条引用）——全文 verbatim=archive 202610.md『热冷整编 2026-10-01 r504 '
    'bm-b 窗批』节；水位注记：流水/回执面已由 r514 窗批掏净，残余 ≈50KB=在役坑律正典（结构性·单条 '
    'superseded 迁毕后仍近线），阈值重锚或立法合并窗=集团/GM 裁定面，各机勿为字节数归档在役律。'
)

# replace r305 line with pointer line (in place to preserve ordering context)
cm_lines[idx[0]] = pointer_line

# drop stray consecutive blank runs (>1 blank between entries) -- structural waste only
out, blanks = [], 0
for l in cm_lines:
    if l.strip() == '':
        blanks += 1
        if blanks > 1:
            continue
    else:
        blanks = 0
    out.append(l)
removed_blanks = orig_n - len(out) - 0
new_cm = '\n'.join(out) + '\n'

# append archive section with r305 verbatim
ar_txt = open(AR, encoding='utf-8').read()
section = (
    '\n## 热冷整编 2026-10-01 r504 bm-b 窗批\n\n'
    '（D-20260925-01④ 50KB 水位触发·r444 范式·行级零丢失校验；本窗批可迁集=单条 superseded 坑律 '
    'r305——r501 变体①③已含其净路+r507 中段泛化；流水/回执面已被 r514 bm-a 窗批掏净，残余热层=在役 '
    '坑律正典，禁为字节数归档活律——结构性注记入指针行，阈值重锚=集团/GM 裁定面）\n\n'
    + r305_line + '\n'
)
new_ar = ar_txt.rstrip('\n') + '\n' + section

# ---- 行级零丢失校验：every original line ∈ (new CODELY) ∪ (archive section) ----
lost = []
for l in cm_lines:
    if l.strip() == '':
        continue  # blank-line accounting handled above (structural waste, disclosed)
    if l == pointer_line:
        continue  # replacement pointer (r305 content accounted in archive)
    if l not in new_cm.splitlines():
        lost.append(l[:60])
assert not lost, 'LOST LINES: %r' % lost
assert r305_line in new_ar, 'r305 verbatim missing in archive'
assert r305_line not in new_cm, 'r305 must not remain in hot file'

open(CM, 'w', encoding='utf-8', newline='').write(new_cm)
open(AR, 'w', encoding='utf-8', newline='').write(new_ar)
print('orig_lines=%d new_lines=%d blanks_removed=%d' % (orig_n, len(out), removed_blanks))
print('new CODELY size=%d' % os.path.getsize(CM))
print('archive size=%d' % os.path.getsize(AR))
print('ZERO_LOSS_VERIFY_OK')
