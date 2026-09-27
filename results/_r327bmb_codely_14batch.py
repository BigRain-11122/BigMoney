# -*- coding: utf-8 -*-
"""r327 bm-b 14th-batch hot-cold archival: CODELY.md append pushed size to 10210B (at 10KB hard line) -> move two oldest in-file entries (r322 bm-a / r323 bm-a) verbatim to research/memory-archive/202609.md + in-file index line. Zero-loss multiset assertions."""
import io

CODELY = 'CODELY.md'
ARCH = 'research/memory-archive/202609.md'

raw = io.open(CODELY, 'rb').read()
text = raw.decode('utf-8')
lines = text.split('\n')

# locate the two entries by unique prefixes
pfx = ['- [2026-09-27 12:4x r322 bm-a]', '- [2026-09-27 12:5x r323 bm-a]']
hits = {p: [i for i, l in enumerate(lines) if l.startswith(p)] for p in pfx}
for p, idx in hits.items():
    assert len(idx) == 1, 'prefix must match exactly one line: %r -> %r' % (p, idx)
move_idx = sorted(hits[p][0] for p in pfx)
entries = [lines[i] for i in move_idx]

# zero-dup guard: neither entry may already exist in archive
arch_text = io.open(ARCH, 'r', encoding='utf-8', newline='').read()
for e in entries:
    assert e not in arch_text, 'entry already archived (x-dup guard): %s...' % e[:60]

# 1) append verbatim to archive with 14th-batch header
with io.open(ARCH, 'a', encoding='utf-8', newline='') as f:
    if not arch_text.endswith('\n'):
        f.write('\n')
    f.write('\n## 十四批外迁（r327 bm-b·2026-09-27 水位律当窗整编·行级零丢失）\n')
    for e in entries:
        f.write(e + '\n')

# 2) remove the two lines from CODELY.md
kept = [l for i, l in enumerate(lines) if i not in set(move_idx)]
assert len(kept) == len(lines) - 2

# 3) insert 14th-batch index line after the r325-bm-b 13th-batch index line
idx_anchor = '十三批外迁（r325 bm-b·水位律当窗整编）'
pos = [i for i, l in enumerate(kept) if l.startswith(idx_anchor)]
assert len(pos) == 1, 'index anchor not unique: %r' % pos
new_idx = '十四批外迁（r327 bm-b·水位律当窗整编）：r322 union 撞键内容恒等验证/r323 rebase 重落 backup 分支禁 reachability 验 fold（bm-a 两例）=归档十四批节·行级零丢失。'
kept.insert(pos[0] + 1, new_idx)

with io.open(CODELY, 'w', encoding='utf-8', newline='') as f:
    f.write('\n'.join(kept))

# ---------- assertions ----------
new_raw = io.open(CODELY, 'rb').read()
new_text = new_raw.decode('utf-8')  # strict re-parse
arch_new = io.open(ARCH, 'r', encoding='utf-8', newline='').read()
for e in entries:
    assert e in arch_new, 'archive lost entry: %s...' % e[:60]
    assert e not in new_text, 'CODELY still contains moved entry'
assert '## 十四批外迁（r327 bm-b' in arch_new
assert new_idx in new_text
print('moved 2 entries verbatim; CODELY %d -> %d bytes (headroom %d B under 10240)' % (len(raw), len(new_raw), 10240 - len(new_raw)))
print('ARCHIVE_14TH_BATCH_OK')
