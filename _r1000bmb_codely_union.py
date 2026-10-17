# r1000 stash CODELY union audit (ASCII only per encoding law)
import os, sys, io

TMP = os.environ['TEMP']
s1_path = os.path.join(TMP, 's1_codely.md')
cur_path = 'CODELY.md'
out_path = os.path.join(TMP, 'r1000_codely_union_report.txt')

def sniff(p):
    b = open(p, 'rb').read(4)
    if b[:2] in (b'\xff\xfe', b'\xfe\xff'):
        return 'utf-16'
    if b[:3] == b'\xef\xbb\xbf':
        return 'utf-8-sig'
    return 'utf-8'

def rd(p):
    enc = sniff(p)
    if enc == 'utf-16':
        t = open(p, 'r', encoding='utf-16', errors='replace').read()
    else:
        t = open(p, 'r', encoding=enc, errors='replace').read()
    return t.splitlines()

s1 = rd(s1_path)
cur = rd(cur_path)
lines = []
lines.append('s1 encoding=%s lines=%d chars=%d' % (sniff(s1_path), len(s1), sum(len(l) for l in s1)))
lines.append('cur encoding=%s lines=%d chars=%d' % (sniff(cur_path), len(cur), sum(len(l) for l in cur)))

set1 = {l.strip() for l in s1 if l.strip()}
setc = {l.strip() for l in cur if l.strip()}
only1 = [l for l in s1 if l.strip() and l.strip() not in setc]
onlyc = [l for l in cur if l.strip() and l.strip() not in set1]
lines.append('')
lines.append('=== lines ONLY in s1 (stash reorg content, %d) ===' % len(only1))
for l in only1:
    lines.append('S1+ ' + l[:400])
lines.append('')
lines.append('=== lines ONLY in cur (current face, %d) ===' % len(onlyc))
for l in onlyc:
    lines.append('CUR+ ' + l[:400])
lines.append('')
# header lines for context
lines.append('=== s1 first 6 lines ===')
for l in s1[:6]:
    lines.append('H1 ' + l[:200])
lines.append('=== cur first 6 lines ===')
for l in cur[:6]:
    lines.append('HC ' + l[:200])

with open(out_path, 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines))
print('report written:', out_path)
print('only_in_s1=%d only_in_cur=%d' % (len(only1), len(onlyc)))
