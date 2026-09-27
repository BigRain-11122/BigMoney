# -*- coding: utf-8 -*-
# r335 bm-a: 19th-batch heat/cold archival (CODELY.md 10185B > 10,000B decimal hard line -> 当窗即办 per O-20260927-0230)
# Move 4 full-text pitlaw entries verbatim (line-level zero-loss) to research/memory-archive/202609.md,
# leave compact pointer lines. D-20260924-01 范式. User-section meta-law NOT archived (元律不随批归档).
import io, os

cp, ap = 'CODELY.md', 'research/memory-archive/202609.md'
cs = io.open(cp, encoding='utf-8').read()
as_ = io.open(ap, encoding='utf-8').read()
cbytes0, abytes0 = len(cs.encode('utf-8')), len(as_.encode('utf-8'))

# the 4 full-text entries to archive: unique line prefixes
MARKS = [
    '- [2026-09-27 15:5x r332 bm-a] 坑律：**实弹测试 commit 演练禁在脏工作树做',
    '- [2026-09-27 15:5x r331 bm-b] 坑律：**autofill tick 自提交与轮会话 git 操作有竞态窗',
    '- [2026-09-27 16:0x r334 bm-a] 坑律：**resolver 取侧 ts 探针的',
    '- [2026-09-27 16:2x r335 bm-a] 坑律：**resolver 两坑',
]
# pointer replacements (one-line, kept in CODELY)
PTRS = [
    '- [2026-09-27 15:5x r332 bm-a] 坑律（十九批外迁·指针）：实弹测试 commit 演练禁在脏工作树——staged 空即 commit 失败后照跑 soft/hard HEAD~1 会回退真 commit/抹掉在飞改动；正典=演练前 status --porcelain 必空+回退用显式 pre-test sha。全文 verbatim=research/memory-archive/202609.md『坑律归档 2026-09-27 十九批』节。',
    '- [2026-09-27 15:5x r331 bm-b] 坑律（十九批外迁·指针）：autofill tick 自提交与轮会话 git 集成窗竞态——tick add 会把 rebase UU 静默解掉+孤儿提交+abort；轮 git 集成窗避 :X0:02±1min+撞后 reflog 定谳+salvage-union。全文 verbatim=archive 202609.md 十九批节。',
    '- [2026-09-27 16:0x r334 bm-a] 坑律（十九批外迁·指针）：blanket max-ts 取侧会被载荷未来日期字段毒化（dashboard next-fire 2026-09-28 压过真生成 ts→假 tie 取旧侧）；正典=已知生产者探针路径优先+未来哨卫+pair/twin 断言防杂交不防双错侧。全文 verbatim=archive 202609.md 十九批节。',
    '- [2026-09-27 16:2x r335 bm-a] 坑律（十九批外迁·指针）：resolver 两坑——①未来哨卫比较先归一位 10 分隔符（T 0x54>空格 0x20，原串直比把 T 形 ts 全误判未来剔除）；②resolver 路径串与 ls-files 输出逐字节核对禁按规格记忆转写（daily_report 真路径=带连字符 REPORT-2026-09-27）。全文 verbatim=archive 202609.md 十九批节。',
]

lines = cs.split('\n')
moved = []
out_lines = []
for ln in lines:
    hit = -1
    for i, m in enumerate(MARKS):
        if ln.startswith(m):
            assert hit == -1, 'multiple marker match -- escalate'
            hit = i
    if hit >= 0:
        moved.append((hit, ln))
        out_lines.append(PTRS[hit])
    else:
        out_lines.append(ln)
assert len(moved) == 4, f'expected to move 4 entries, found {len(moved)}: {[m[0] for m in moved]}'

new_c = '\n'.join(out_lines)
moved_bytes = sum(len(l.encode('utf-8')) for _, l in moved)
ptr_bytes = sum(len(p.encode('utf-8')) for p in PTRS)
assert len(cs.encode('utf-8')) - moved_bytes + ptr_bytes == len(new_c.encode('utf-8')), 'byte account mismatch'

header = '## 坑律归档 2026-09-27 十九批（r335 bm-a·CODELY 10185B>10,000B 硬线触发当窗·行级零丢失）\n\n'
body = '\n'.join(l for _, l in moved) + '\n'
new_a = as_ + ('\n' if not as_.endswith('\n') else '') + header + body

# zero-loss verification: every moved line exists VERBATIM in new archive
for _, l in moved:
    assert l in new_a, 'moved line not found verbatim in archive -- abort'
# write
io.open(cp, 'w', encoding='utf-8', newline='').write(new_c)
io.open(ap, 'w', encoding='utf-8', newline='').write(new_a)
# post-write verify
c1 = io.open(cp, encoding='utf-8').read()
a1 = io.open(ap, encoding='utf-8').read()
print('CODELY: %dB -> %dB (over 10KB: %s)' % (cbytes0, len(c1.encode('utf-8')), len(c1.encode('utf-8')) > 10000))
print('archive: %dB -> %dB (+%dB moved verbatim)' % (abytes0, len(a1.encode('utf-8')), moved_bytes))
for _, l in moved:
    assert l in a1
    assert l not in c1 or l in PTRS  # full text gone from CODELY (pointers remain)
print('4 entries verbatim-verified in archive, pointers in place; zero line loss')
