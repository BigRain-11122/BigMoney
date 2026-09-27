"""r82 bm-c: CODELY.md glued-tail fix + 13th-batch hot-cold archival (water-line law, in-window).

Zero-loss discipline per D-20260924-01 / O-20260927-0230:
- moved entries extracted line-level from the live file (no transcription), verbatim into
  research/memory-archive/202609.md '十三批外迁' section;
- strict UTF-8 end-to-end; CRLF preserved per-line (keepends); anchors asserted.
Idempotency: re-run aborts via anchors if already applied.
"""


def read_exact(p):
    with open(p, 'rb') as f:
        return f.read().decode('utf-8')  # strict


def write_exact(p, s):
    with open(p, 'wb') as f:
        f.write(s.encode('utf-8'))


C = 'CODELY.md'
A = 'research/memory-archive/202609.md'

c = read_exact(C)
a = read_exact(A)
c_before = c
a_before = a

# --- 1) fix glued tail: my earlier partial-fragment replace duplicated the r323 bm-b body
#        onto the end of the r82 entry line. Remove it (the legit r323 entry line stays). ---
combo_head = '（D-06~10 补审回执）。——r320 bm-a 修 HANDOVER'
i = c.find(combo_head)
assert i != -1, 'glued combo not found (already fixed?)'
tail_end_anchor = '指针=results/_r323bmb_gbk_sweep.py+round_reports r323 行。'
j = c.find(tail_end_anchor, i)
assert j != -1, 'glued tail end anchor not found'
end = j + len(tail_end_anchor)
c = c[:i] + '（D-06~10 补审回执）。' + c[end:]
assert c.count(tail_end_anchor) == 1, 'legit r323 entry must be the only remaining tail'

# --- 2) line-level move of the two oldest loose pitlaws (r312 bm-a, r320 bm-b PS) ---
clines = c.splitlines(keepends=True)


def find_one(pred, what):
    hits = [k for k, l in enumerate(clines) if pred(l)]
    assert len(hits) == 1, 'expected exactly one %s, got %r' % (what, hits)
    return hits[0]


k1 = find_one(lambda l: l.startswith('- [2026-09-27 10:4x r312 bm-a]'), 'r312 entry line')
k2 = find_one(lambda l: l.startswith('- [2026-09-27 12:1x r320 bm-b]'), 'r320 bm-b entry line')
assert k1 < k2, 'entry order sanity'
e1, e2 = clines[k1], clines[k2]
assert e1.endswith('\r\n') and e2.endswith('\r\n'), 'moved lines must keep their CRLF'
for k in sorted((k1, k2), reverse=True):
    del clines[k]

# --- 3) insert 13th-batch index line right after the 12th-batch index line ---
k12 = find_one(lambda l: l.startswith('十二批外迁（r322 bm-a'), '12th-batch index line')
idx = ('十三批外迁（r82 bm-c·水位律当窗整编）：r312 bm-a 轮内烧片 fetch 洞察对岸翻面'
       '+r320 bm-b PS 批量 lane 嵌套 splat 静默零执行=归档十三批节·行级零丢失。\r\n')
clines.insert(k12 + 1, idx)
c = ''.join(clines)

# --- 4) archive append (verbatim, zero-loss) ---
if not a.endswith('\r\n'):
    a += '\r\n'
a += '十三批外迁（r82 bm-c·2026-09-27 水位律当窗整编·行级零丢失）\r\n' + e1 + e2

# --- 5) verify before write ---
assert a.count(e1) == 1 and a.count(e2) == 1, 'archive must contain each moved line exactly once'
assert e1 not in c and e2 not in c, 'moved lines must be gone from CODELY.md'
assert '十三批外迁' in c, 'index line missing'
assert 'D-06~10 补审回执）。——r320' not in c, 'glue residue'
assert 'r82 bm-c' in c and 'aacae41' in c, 'r82 entry intact'
assert c != c_before and a != a_before
size_c = len(c.encode('utf-8'))
assert size_c <= 10240, 'CODELY.md still over 10KB line: %d' % size_c

write_exact(A, a)
write_exact(C, c)

# --- 6) post-write strict re-verify ---
c2 = read_exact(C)
a2 = read_exact(A)
assert c2 == c and a2 == a, 'write-back mismatch'
assert read_exact(A).count(e1) == 1
print('OK codely=%dB archive=%dB | moved: r312(%dB) r320b(%dB) | idx line inserted'
      % (size_c, len(a2.encode('utf-8')), len(e1.encode('utf-8')), len(e2.encode('utf-8'))))
