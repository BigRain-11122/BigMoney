# -*- coding: utf-8 -*-
"""r346 bm-b: CODELY.md 10KB hard-line hot-cold fold -> archive 202609.md 33rd batch.
Line-level zero-loss: full lines extracted programmatically (no retyping),
moved verbatim into archive, pointer lines substituted in CODELY.md.
New pitlaw (psutil liveness) enters this window's fold set per 'new pitlaws
still enter this file first' + same-window reorganize precedent (30th batch).
"""
import os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CODELY = os.path.join(ROOT, 'CODELY.md')
ARCH = os.path.join(ROOT, 'research', 'memory-archive', '202609.md')

raw = open(CODELY, 'rb').read()
txt = raw.decode('utf-8-sig')  # tolerate BOM
had_bom = raw.startswith(b'\xef\xbb\xbf')
nl = '\r\n' if '\r\n' in txt else '\n'
# normalize split preserving content
lines = txt.split(nl)

MARKERS = [
    ('[2026-09-27 22:3x r344 bm-b] \u5751\u5f8b\uff1aautofill claim',
     '[2026-09-27 22:3x r344 bm-b] \u5751\u5f8b\uff08\u4e09\u5341\u4e09\u6279\u5916\u8fc1\u00b7\u6307\u9488\uff09\uff1aautofill claim \u6062\u590d\u817f\u76f2 git rebase --abort \u4f1a\u6740\u4f1a\u8bdd\u5728\u98de rebase\uff08abort \u817f\u65b0\u9762\uff09\uff1b\u6b63\u5178=\u591a\u505c\u70b9 fold \u5355\u8fdb\u7a0b\u539f\u5b50\u9a71\u52a8+tick \u810f\u642d\u8f66\u5f8b+\u5371\u9669\u7a97\u540e reflog \u5b9a\u8c2d\u2014\u2014\u5168\u6587 verbatim=archive 202609.md\u300e\u5751\u5f8b\u5f52\u6863 2026-09-27 \u4e09\u5341\u4e09\u6279\u300f\u8282\u3002\u6307\u9488=results/_r344bmb_fold_drive.py'),
    ('[2026-09-27 22:3x r344 bm-b] \u5751\u5f8b\uff1arebase \u91cd\u653e\u7a97\u5185',
     '[2026-09-27 22:3x r344 bm-b] \u5751\u5f8b\uff08\u4e09\u5341\u4e09\u6279\u5916\u8fc1\u00b7\u6307\u9488\uff09\uff1arebase \u91cd\u653e\u7a97\u5185 runnable_pool take-new(updated_at) \u65f6\u6233\u53d6\u4fa7\u4e22\u8fdc\u7aef\u65b0\u589e\u6761\u76ee\uff1b\u6b63\u5178=pool=\u6761\u76ee\u96c6 carry \u9762\uff0cfold \u540e entries-ID-set \u53cc\u4fa7\u5bf9\u8d26\uff0cresolver \u5bf9 pool \u7981\u88f8 take-new \u65f6\u6233\u9762\u2014\u2014\u5168\u6587 verbatim=archive 202609.md\u300e\u5751\u5f8b\u5f52\u6863 2026-09-27 \u4e09\u5341\u4e09\u6279\u300f\u8282\u3002\u6307\u9488=results/_r344bmb_close.py'),
    ('[2026-09-27 22:3x r360 bm-a] \u5751\u5f8b\uff1arolling-ledger',
     '[2026-09-27 22:3x r360 bm-a] \u5751\u5f8b\uff08\u4e09\u5341\u4e09\u6279\u5916\u8fc1\u00b7\u6307\u9488\uff09\uff1arolling-ledger union \u89e3\u65b9\u7981\u81ea\u9020 cap \u622a\u7559\uff08\u6eda\u52a8\u7a97\u5f52\u751f\u4ea7\u8005\u5199\u56de\u9762\u975e resolver\uff09\u2014\u2014\u5168\u6587 verbatim=archive 202609.md\u300e\u5751\u5f8b\u5f52\u6863 2026-09-27 \u4e09\u5341\u4e09\u6279\u300f\u8282\u3002\u6307\u9488=results/_r360bma_resolve.py'),
]

NEW_FULL = ('- [2026-09-27 22:5x r346 bm-b] \u5751\u5f8b\uff1a\u8fdb\u7a0b\u6d3b\u4f53\u5224\u5b9a\uff08burn \u6b7b\u6d3b/\u770b\u95e8\u72d7\u5047\u6d3b\u4f53\u5acc\u7591\uff09\u5fc5\u4ee5 psutil \u540c\u6e90\u63a2\u9488\u590d\u73b0\u5b9a\u8c2d\uff0c\u7981\u4ee5 PowerShell Get-Process \u8868\u9762\u5b9a\u751f\u6b7b\u2014\u2014r346 \u5b9e\u5f39\uff1aGet-Process \u8f93\u51fa\u88ab PS format-merge \u5403\u6210\u7a7a\u884c\u5047\u8c61=\u300c\u96f6 python \u8fdb\u7a0b\u300d\u8bef\u8bfb\uff0cW2-A burn parent 13148+4 spawn workers \u5168\u6d3b\u6001\u9669\u88ab\u5b9a\u8c2d\u6b7b\u4ea1+\u9669\u89e6\u53d1\u5bf9\u4e0d\u5b58\u5728\u7684\u300cautofill \u5047\u6d3b\u4f53 bug\u300d\u7684\u8865\u6551\uff08\u53cc\u70e7/\u91cd\u542f\u707e\u96be\u9762\uff09\uff1b\u6b63\u5178=psutil process_iter\uff08name+cmdline\uff0c\u4e0e Tools/autofill.py _runner_alive \u540c\u6e90\uff09\u9010 pid \u6253\u5370+\u77ed\u7a97 cpu_delta \u91c7\u6837\uff08~6s\uff0c\u6ee1\u6838\u22485-6s delta\uff09\u53cc\u8bc1\u5b9a\u8c2d\uff0c\u6b7b/\u6d3b\u7ed3\u8bba\u7981\u5355\u4e00 shell \u9762\u5b9a\u6848\u3002\u6307\u9488=logs/iteration-loop/round_reports.md r346 \u884c\u3002')
NEW_PTR = ('- [2026-09-27 22:5x r346 bm-b] \u5751\u5f8b\uff08\u4e09\u5341\u4e09\u6279\u5916\u8fc1\u00b7\u6307\u9488\uff09\uff1a\u8fdb\u7a0b\u6d3b\u4f53\u5224\u5b9a\u5fc5 psutil \u540c\u6e90\u63a2\u9488\u590d\u73b0+cpu_delta \u53cc\u8bc1\u5b9a\u8c2d\uff0c\u7981 Get-Process \u8868\u9762\u5b9a\u751f\u6b7b\uff08r346 \u5b9e\u5f39\uff1aformat-merge \u7a7a\u884c\u5047\u8c61\u9669\u628a\u5168\u6d3b W2-A burn \u5224\u6b7b\u5e76\u89e6\u53d1\u8fdd\u6cd5\u8865\u6551\uff09\u2014\u2014\u5168\u6587 verbatim=archive 202609.md\u300e\u5751\u5f52\u6863 2026-09-27 \u4e09\u5341\u4e09\u6279\u300f\u8282\u3002\u6307\u9488=logs/iteration-loop/round_reports.md r346\u3002')

# locate full lines by marker (must hit exactly 1 each)
hits = {}
for i, ln in enumerate(lines):
    for mk, _ptr in MARKERS:
        if mk in ln and ln.lstrip().startswith('- ['):
            hits.setdefault(mk, []).append(i)
for mk, _ in MARKERS:
    if len(hits.get(mk, [])) != 1:
        print('FATAL: marker hit count != 1 for', mk[:40], hits.get(mk)); sys.exit(1)

# collect verbatim fulls (strip trailing \r if any)
fulls = []
for mk, _ in MARKERS:
    i = hits[mk][0]
    fulls.append(lines[i].rstrip('\r'))

# 1) append archive section (utf-8, preserve per-file newline style)
araw = open(ARCH, 'rb').read()
atxt = araw.decode('utf-8')
anl = '\r\n' if '\r\n' in atxt else '\n'
section_lines = ['', '## \u5751\u5f8b\u5f52\u6863 2026-09-27 \u4e09\u5341\u4e09\u6279\uff08r346 bm-b\u00b7CODELY.md \u8d85 10KB \u786c\u7ebf\u5f53\u7a97\u6574\u7f16\u00b7\u884c\u7ea7\u96f6\u4e22\u5931\uff09']
section_lines += fulls
section_lines.append(NEW_FULL)
section_lines.append('\u4e09\u5341\u4e09\u6279\u8bb0\u5f55\uff1a\u524d\u4e09\u884c=CODELY.md \u539f\u884c verbatim \u5916\u8fc1\uff0c\u672b\u884c=r346 bm-b \u65b0\u5751\u5f8b\u540c\u7a97\u5165\u672c\u6279\uff08\u65b0\u5751\u5f8b\u4ecd\u5148\u5165\u672c\u4ef6+\u5f53\u7a97\u6298\u53e0\u5148\u4f8b\uff09\uff1bCODELY.md \u4fa7\u5404\u7559\u6307\u9488\u884c\u3002')
addition = anl.join(section_lines) + anl
if not (atxt.endswith('\n') or atxt.endswith('\r')):
    addition = anl + addition
with open(ARCH, 'ab') as f:
    f.write(addition.encode('utf-8'))

# 2) substitute pointers in CODELY.md + append new pointer
for mk, ptr in MARKERS:
    i = hits[mk][0]
    lines[i] = ptr
# append new pointer at end (before trailing empty lines if file ends with newline)
while lines and lines[-1] == '':
    lines.pop()
lines.append(NEW_PTR)
out = nl.join(lines)
if txt.endswith(nl):
    out += nl
data = ('\ufeff' + out if had_bom else out).encode('utf-8')
with open(CODELY, 'wb') as f:
    f.write(data)

# 3) verify: zero-loss (each full verbatim in archive), size under line
anow = open(ARCH, encoding='utf-8').read()
for fl in fulls + [NEW_FULL]:
    if fl not in anow:
        print('FATAL: zero-loss check FAILED for', fl[:40]); sys.exit(1)
cnow = open(CODELY, 'rb').read()
print('OK folded:', len(fulls) + 1, 'entries; CODELY.md bytes:', len(cnow), '(was', len(raw), '); archive bytes:', os.path.getsize(ARCH))
print('BOM preserved:', had_bom, '; codely_nl:', repr(nl), '; arch_nl:', repr(anl))
