# r503 bm-c heal v2: round-line triple-append truncation (r679 law: uncommitted multi-append -> bytes surgery, keep-first drop-rest)
rp = r'K:\Fluxgroup\FluxGroup\quant\bigmoney\round_reports-bm-c.md'
raw = open(rp, 'rb').read()
needle = b' | r503 | dept:'
cnt = raw.count(needle)
print('pre-heal count=%d' % cnt)
assert cnt == 3, 'expected exactly 3 (v2+v3+v4 triple append), got %d -- ABORT' % cnt
out = raw
# keep first, drop every subsequent round-line (each runs from its needle to next \n inclusive)
first = raw.find(needle)
pos = first
tail_start = None
while True:
    pos = raw.find(needle, pos + 1)
    if pos == -1:
        break
    nl = raw.find(b'\n', pos)
    end = len(raw) if nl == -1 else nl + 1
    if tail_start is None or pos < tail_start:
        pass
# simpler: collect segments to delete (they are contiguous tail lines in append order)
dels = []
pos = first
while True:
    pos = raw.find(needle, pos + 1)
    if pos == -1:
        break
    nl = raw.find(b'\n', pos)
    end = len(raw) if nl == -1 else nl + 1
    dels.append((pos, end))
assert len(dels) == cnt - 1, 'segment collection mismatch'
# delete from the end backwards to keep offsets valid
healed = raw
for start, end in reversed(dels):
    healed = healed[:start] + healed[end:]
open(rp, 'wb').write(healed)
raw2 = open(rp, 'rb').read()
cnt2 = raw2.count(needle)
assert cnt2 == 1, 'post-heal count must be 1, got %d' % cnt2
assert raw2.count(b'r503 bm-c') == 0, 'close-line marker unexpectedly present'
assert len(raw2) == len(raw) - sum(e - s for s, e in dels), 'byte accounting mismatch'
print('healed: kept first r503 round line, truncated %d dup lines; bytes %d -> %d' % (len(dels), len(raw), len(raw2)))
