# -*- coding: utf-8 -*-
"""R210 hot-cold memory archival (D-20260924-01 pattern, D-20260925-01(4) proactive window).

Move all 2026-09-25-dated entry lines from root CODELY.md to
research/memory-archive/202609.md. Byte-exact binary processing:
- moved lines keep original bytes (incl. CRLF/LF as-is, R164 law)
- kept lines byte-identical
- zero-loss verification: line counts + UTF-8 byte accounting + membership re-check
"""
import io, re, sys

SRC = 'CODELY.md'
DST = 'research/memory-archive/202609.md'
PAT = re.compile(rb'^\s*(?:- )?\[2026-09-25')

raw = io.open(SRC, 'rb').read()
lines = raw.splitlines(keepends=True)
moved_flags = [bool(PAT.match(l)) for l in lines]
moved = [l for l, f in zip(lines, moved_flags) if f]
kept = [l for l, f in zip(lines, moved_flags) if not f]
assert len(moved) == 41, 'expected 41 moved lines, got %d' % len(moved)
# ensure every moved line ends with newline (only last line of file could lack it)
fixed_moved = [l if l.endswith(b'\n') else l + b'\n' for l in moved]
extra_nl = sum(1 for a, b in zip(moved, fixed_moved) if a != b)

moved_bytes = sum(len(l) for l in moved)
src_before = len(raw)

note = ('> [2026-09-26 03:2x] 迁移注（bm-a R210 热冷整编·D-20260925-01④ 逼近线主动窗·49757B=99.5%线）：'
        '迁移时窗 2026-09-25 16:1x-23:5x 条目 41 行（Project 立法到达注 1+Reference 坑律/面律 40，'
        '含 3 行无横杠漂移形 17:37/17:5x/18:3x），原条目内容不变字节恒等；'
        '水位 49757B→%dB（迁移体 %dB），中零丢失（行级校验+UTF-8 字节核算·R164 CRLF/LF 双态一致）；'
        '热层保留=09-26 窗 13 条目+User 节元律（09-24·R156 律不随批归档）+冷层指针；').encode('utf-8')
# fill the two %d later after computing; placeholder replaced below

dst_raw = io.open(DST, 'rb').read()
dst_before = len(dst_raw)

new_src = b''.join(kept)
note_final = note.replace(b'%dB', str(len(new_src)).encode() + b'B').replace(b'%dB', str(moved_bytes).encode() + b'B')
appendix = note_final + b'\n' + b''.join(fixed_moved)
new_dst = dst_raw + (b'' if dst_raw.endswith(b'\n') else b'\n') + appendix

io.open(SRC, 'wb').write(new_src)
io.open(DST, 'wb').write(new_dst)

# ---- zero-loss verification ----
chk_src = io.open(SRC, 'rb').read()
chk_dst = io.open(DST, 'rb').read()
errs = []
# 1) membership: every moved line present in dst tail, absent from src
dst_tail = chk_dst[len(dst_raw):]
for l in fixed_moved:
    if l not in dst_tail: errs.append('missing in dst: %r' % l[:40])
    if l in chk_src: errs.append('still in src: %r' % l[:40])
# 2) byte accounting (tolerate the at-most-one newline fix)
if len(chk_src) != src_before - moved_bytes - extra_nl:
    errs.append('src size mismatch: %d != %d - %d - %d' % (len(chk_src), src_before, moved_bytes, extra_nl))
if len(chk_dst) != dst_before + len(appendix):
    errs.append('dst size mismatch')
# 3) no 09-25 entry-start lines remain in src
if PAT.search(chk_src.replace(b'\r\n', b'\n').replace(b'\n\n', b'\n')) and any(PAT.match(x) for x in chk_src.splitlines()):
    errs.append('09-25 entry still in src')
# 4) 09-26 entries + User entry + pointer survived
for probe in [b'2026-09-26 03:2x', b'2026-09-24 16:07:32', u'冷层指针'.encode('utf-8')]:
    if probe not in chk_src: errs.append('survival probe missing: %r' % probe[:24])

n_src_lines_before = len(lines)
n_src_lines_after = len(chk_src.splitlines())
n_dst_lines_after = len(chk_dst.splitlines())
if n_src_lines_after != n_src_lines_before - 41: errs.append('src line count mismatch')

print('moved lines:', len(moved), '| moved bytes:', moved_bytes, '| extra_nl:', extra_nl)
print('src: %dB -> %dB | dst: %dB -> %dB' % (src_before, len(chk_src), dst_before, len(chk_dst)))
print('src lines: %d -> %d | dst lines: %d -> %d' % (n_src_lines_before, n_src_lines_after, len(dst_raw.splitlines()), n_dst_lines_after))
if errs:
    print('VERIFY FAIL:')
    for e in errs: print(' -', e)
    sys.exit(2)
print('ZERO-LOSS VERIFICATION PASS')
