# -*- coding: utf-8 -*-
"""r322 bm-a CODELY.md water-mark in-window archival (12th batch) + new pitlaw append.
Laws: D-20260924-01 (line-level zero-loss archival), O-20260927-0230-bm-a (<=10KB hard line),
memory-entrance 4-question gate for the new entry.
"""
import io, sys

ROOT = r'C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney'
CL = ROOT + r'\CODELY.md'
AR = ROOT + r'\research\memory-archive\202609.md'

cl_text = open(CL, encoding='utf-8').read()
ar_text = open(AR, encoding='utf-8').read()

# 4 flowing entries to archive (exact full lines, matched by prefix)
prefixes = [
    '- [2026-09-27 11:3x r317 bm-b]',
    '- [2026-09-27 11:4x r318 bm-b]',
    '- [2026-09-27 12:0x r319 bm-b]',
    '- [2026-09-27 12:1x r79 bm-c]',
]
cl_lines = cl_text.splitlines()
migrate = []
for pref in prefixes:
    hits = [l for l in cl_lines if l.startswith(pref)]
    assert len(hits) == 1, f'prefix {pref}: {len(hits)} hits'
    migrate.append(hits[0])

# append to archive under 12th-batch header (verbatim, zero-loss)
header = '\n\n## 十二批外迁（r322 bm-a·2026-09-27 水位律当窗整编·行级零丢失）\n'
assert header.strip() not in ar_text, '12th batch header already present'
ar_new = ar_text + header + '\n'.join(migrate) + '\n'
open(AR, 'w', encoding='utf-8', newline='').write(ar_new)

# remove from CODELY.md (exact-line removal)
for line in migrate:
    assert cl_text.count(line + '\n') == 1, f'line not unique: {line[:40]}'
    cl_text = cl_text.replace(line + '\n', '', 1)
# also drop the now-dangling blank leftover if the Project block empties oddly -- no, keep structure.

# insert 12th-batch index line after the 11th-batch line in Reference
idx11 = '十一批外迁（r319 bm-b·水位律当窗整编）：'
pos = cl_text.find(idx11)
assert pos != -1, 'index anchor (11th batch) not found'
line_end = cl_text.find('\n', pos)
idx12 = '十二批外迁（r322 bm-a·水位律当窗整编）：r317 autostash 手切禁律/r318 方案A git 转移通道双暗变面/r319 union 键实存/r79 bm-c 反事实恒等门构造不变量=归档十二批节·行级零丢失。'
cl_text = cl_text[:line_end] + '\n' + idx12 + cl_text[line_end:]

# new pitlaw entry into Project section (before '### Reference')
new_entry = ('- [2026-09-27 12:4x r322 bm-a] 坑律：**union 撞键须内容恒等验证——同 key 双侧 content-diff>0=单键不足换复合键（r319 补面）**'
             '——r322 S0 主重落实弹（三机同窗 S6 镜像三撞：bm-b r322 12:34:29/bm-a r321 12:34:56/bm-c r80 12:37:21→28 UU）：'
             'compute_audit history union 202+205 撞键 200 个，ts 单键 HEAD 取侧若遇同秒异机样本=静默吞一侧测量记录；'
             '验证法=撞键集逐对 content 比较（本例 content-diff=0=共同祖先面恒等合法）；content-diff>0 ⇒ 升复合键（如 (ts,machine)）再 union。'
             '同轮实证=28 件全可既有配方解（25 测量面 take-origin ts 深扫+3 账本 union 零丢失断言），'
             '主重落范式（push 拒→backup 分支→next-round S0 rebase 重落）全链零 abort 零强推。'
             '指针=results/_r322bma_probe.py+_r322bma_resolve.py+commit r322。')
anchor = '\n### Reference\n'
assert cl_text.count(anchor) == 1
cl_text = cl_text.replace(anchor, '\n' + new_entry + '\n' + anchor, 1)

open(CL, 'w', encoding='utf-8', newline='').write(cl_text)

# ---- zero-loss verification ----
ar_check = open(AR, encoding='utf-8').read()
for line in migrate:
    assert line in ar_check, f'archived line missing: {line[:40]}'
cl_check = open(CL, encoding='utf-8').read()
for line in migrate:
    assert line not in cl_check, f'line still in CODELY: {line[:40]}'
assert new_entry in cl_check and idx12 in cl_check
open(CL, encoding='utf-8').read()          # strict utf-8 re-verify
open(AR, encoding='utf-8').read()
print('CODELY.md bytes:', len(cl_check.encode('utf-8')))
print('archive bytes:', len(ar_check.encode('utf-8')))
print('migrated lines:', len(migrate), '| zero-loss verified | 12th-batch indexed | new pitlaw in')
assert len(cl_check.encode('utf-8')) <= 10240, 'HARD LINE VIOLATION'
print('<=10KB hard line OK')
