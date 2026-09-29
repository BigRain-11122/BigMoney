# r415 bm-b CODELY.md hot-cold integration (10KB hard line, O-20260927-0230 law)
# Migrate 4 verbose window entries verbatim -> archive 202609.md new section,
# replace with one pointer line. Zero line loss verified byte-level.
import io, os

CODELY = 'CODELY.md'
ARCHIVE = 'research/memory-archive/202609.md'

MIGRATE_PREFIXES = (
    '- [2026-09-29 06:3x r416-cont bm-a]',
    '- [2026-09-29 06:5x r413 bm-b]',
    '- [2026-09-29 07:0x r203 bm-c]',
    '- [2026-09-29 08:2x r415 bm-b]',
)
POINTER = (
    "冷层指针：坑律正典 2026-09-29 九十/八十九批+T-116 flip 回执+九十四批（r416-cont bm-a 池条目 submit 前置产物未入仓=他机撞门无限崩循环·W6-SCREEN 实弹/r413 bm-b 池面 done-flip=会话专属动作·deferral 结构性错律·V3 实弹/r203 bm-c T-116 s3 wave-1 flip 落地回执·读池面前先读回执件/r415 bm-b 收割前任 flip 脚本 receipt assert 按源常量实值形态校验·detach 存续第三例+W6 判决定谳四面 G1 全零 0/293·E[FP]=14.65·账本 333432·48h CEO 钟 2026-10-01 08:14）全文 verbatim=archive 202609.md『坑律归档 2026-09-29 r415 bm-b 窗批』节（r415 bm-b 窗水位律当窗整编·行级零丢失校验）。\n"
)
SECTION = "## 坑律归档 2026-09-29 r415 bm-b 窗批（水位律当窗整编：CODELY 热层越 10KB 硬线·行级零丢失校验）\n"

with io.open(CODELY, encoding='utf-8') as fh:
    lines = fh.readlines()

migrated, kept = [], []
for l in lines:
    if any(l.startswith(p) for p in MIGRATE_PREFIXES):
        migrated.append(l)
    else:
        kept.append(l)
assert len(migrated) == 4, f'expected 4 migrate lines, got {len(migrated)}'

# insert pointer where the first migrated entry lived (keep Project section order)
first_idx = next(i for i, l in enumerate(lines) if any(l.startswith(p) for p in MIGRATE_PREFIXES))
out, placed = [], False
for l in kept:
    # place pointer before the line that now follows the former first migrated entry
    out.append(l)
# simpler: pointer goes right before the last line group; rebuild: find position in kept
# where original first migrated line sat: count lines before it
n_before = first_idx
out = kept[:n_before] + [POINTER] + kept[n_before:]

with io.open(CODELY, 'w', encoding='utf-8', newline='') as fh:
    fh.writelines(out)

with io.open(ARCHIVE, 'a', encoding='utf-8', newline='') as fh:
    fh.write('\n' + SECTION)
    fh.writelines(migrated)

# zero-loss verification: every migrated byte present verbatim in archive tail
with io.open(ARCHIVE, encoding='utf-8') as fh:
    atail = fh.read()
for ml in migrated:
    assert ml in atail, 'migrated line missing verbatim in archive: ' + ml[:50]
with io.open(CODELY, encoding='utf-8') as fh:
    ctail = fh.read()
assert '\ufffd' not in ctail, 'FFFD in CODELY'
assert all(p.split(']')[0] + ']' not in ctail for p in MIGRATE_PREFIXES), 'migrated lines still in CODELY'
sz = os.path.getsize(CODELY)
print('integration OK: migrated 4 lines verbatim (zero-loss verified), CODELY bytes =', sz,
      'PASS<=10KB' if sz <= 10240 else 'FAIL>10KB')
