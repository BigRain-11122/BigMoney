# -*- coding: utf-8 -*-
"""r325 bm-b CODELY.md hot-cold archival (13th batch, water-level law D-20260925-01④):
append new r325 pit-law, move 3 oldest entries (r312/r320bm-b/r320bm-a) verbatim to
research/memory-archive/202609.md, update Reference batch index. Multiset zero-loss assertions."""
import io
from collections import Counter

C = 'CODELY.md'
A = 'research/memory-archive/202609.md'
c = io.open(C, encoding='utf-8', newline='').read()
a = io.open(A, encoding='utf-8', newline='').read()
assert '\r\n' not in c and '\r\n' not in a, 'unexpected CRLF in LF-canonical files'

NEW = ('- [2026-09-27 13:2x r325 bm-b] 坑律：**python 文本模式 read 的 universal-newlines 静默把 CRLF 件归一成 LF——写回即全文件 LF 化=CRLF 正典件全文件假 diff（同族=PS/cmd 重定向毁字节面 r85/r90/r117 的 python 变体）**——r325 实弹（HANDOVER 5x line4 刷新）：`io.open(p,encoding=\'utf-8\').read()` 默认 newline=None 翻译一切行尾为 \\n，`splitlines(True)` 保不住原 CRLF，`newline=\'\'` 写回落 LF→git diff 232 行全重写（幸行数断言当场拦+git checkout 还原后字节保真重做）；正典=读改 CRLF 正典件一律 `io.open(..., newline=\'\')` 字节保真读+追加行用 \'\\r\\n\' 终结符+CRLF 计数断言（n0_crlf+k）。指针=results/_r325bmb_handover_5x.py（断言版）+round_reports r325 行。\n')

MOVE_KEYS = [
    '- [2026-09-27 10:4x r312 bm-a] 坑律：',
    '- [2026-09-27 12:1x r320 bm-b] 坑律：',
    '- [2026-09-27 12:1x r320 bm-a] 坑律：',
]
clines = c.splitlines(True)
moved = []
for key in MOVE_KEYS:
    hits = [l for l in clines if l.startswith(key)]
    assert len(hits) == 1, ('entry not unique', key, len(hits))
    moved.append(hits[0])
kept = [l for l in clines if not any(l.startswith(k) for k in MOVE_KEYS)]
assert len(kept) == len(clines) - 3, 'kept count mismatch'

IDX_ANCHOR = '十二批外迁（r322 bm-a·水位律当窗整编）：r317 autostash 手切禁律/r318 方案A git 转移通道双暗变面/r319 union 键实存/r79 bm-c 反事实恒等门构造不变量=归档十二批节·行级零丢失。\n'
IDX_NEW = '十三批外迁（r325 bm-b·水位律当窗整编）：r312 轮内烧片前 fetch 洞察/r320 bm-b PS 批量 splat/r320 bm-a GBK 污染修复=归档十三批节·行级零丢失。\n'
assert c.count(IDX_ANCHOR) == 1, 'index anchor not found'
kept_text = ''.join(kept)
kept_text = kept_text.replace(IDX_ANCHOR, IDX_ANCHOR + IDX_NEW, 1)
if not kept_text.endswith('\n'):
    kept_text += '\n'
kept_text += NEW
io.open(C, 'w', encoding='utf-8', newline='').write(kept_text)

ARCH_SEC = '\n## 十三批外迁（r325 bm-b·2026-09-27 水位律当窗整编·行级零丢失）\n' + ''.join(moved)
if not a.endswith('\n'):
    a += '\n'
a2 = a + ARCH_SEC
io.open(A, 'w', encoding='utf-8', newline='').write(a2)

# multiset zero-loss verification (r323 canon) -- content-only keys (splitlines strips terminators)
c2 = io.open(C, encoding='utf-8', newline='').read()
a3 = io.open(A, encoding='utf-8', newline='').read()
cl2 = Counter(c2.splitlines())
al3 = Counter(a3.splitlines())
prev_cl = Counter(c.splitlines())
prev_al = Counter(a.splitlines())
moved_ms = Counter(l[:-1] if l.endswith('\n') else l for l in moved)
new_ms = Counter([NEW[:-1] if NEW.endswith('\n') else NEW])
assert all(al3[k] >= prev_al[k] + moved_ms[k] for k in moved_ms), 'archive side lost lines'
assert all(cl2[k] == 0 for k in moved_ms), 'moved lines still present in CODELY'
assert all(cl2[k] == prev_cl[k] for k in prev_cl if k not in moved_ms and k != IDX_NEW and not k.startswith('- [2026-09-27 13:2x r325 bm-b]')), 'unrelated CODELY lines changed'
assert cl2 == prev_cl - moved_ms + new_ms + Counter([IDX_NEW[:-1] if IDX_NEW.endswith('\n') else IDX_NEW]), 'CODELY multiset equation failed'
arch_hdr = '## 十三批外迁（r325 bm-b·2026-09-27 水位律当窗整编·行级零丢失）'
assert al3 == prev_al + moved_ms + Counter(['', arch_hdr]), 'archive multiset equation failed'
assert '十三批外迁' in c2 and '[2026-09-27 13:2x r325 bm-b]' in c2, 'new entries missing'
sz = len(c2.encode('utf-8'))
print('CODELY 13th-batch archival PASS: moved 3 entries verbatim, new r325 entry in, index line added; CODELY size', sz, 'bytes (<=10KB:', sz <= 10240, ') | archive lines', len(prev_al), '->', len(al3))
