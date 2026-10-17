import re, io, sys

p = 'results/post_review.jsonl'
raw = io.open(p, 'r', encoding='utf-8', newline='').read()
m = re.search(r'(?ms)^<<<<<<< HEAD\r?\n(.*?)^=======\r?\n(.*?)^>>>>>>> [^\r\n]+\r?\n', raw)
if not m:
    print('NO_CONFLICT_MARKERS')
    sys.exit(1)
head_block, theirs_block = m.group(1), m.group(2)
pre, post = raw[:m.start()], raw[m.end():]
hl = [l for l in head_block.split('\n') if l.strip()]
tl = [l for l in theirs_block.split('\n') if l.strip()]
print('head_new_lines=%d theirs_new_lines=%d' % (len(hl), len(tl)))

def ts_of(line):
    mm = re.search(r'"ts":\s*"([^"]+)"', line)
    return mm.group(1) if mm else '9999'

all_new = hl + tl
all_new.sort(key=ts_of)  # stable: equal ts keeps HEAD-first order
out = pre + '\n'.join(all_new)
if not out.endswith('\n'):
    out += '\n'
out += post
tmp = p + '.tmp1077'
io.open(tmp, 'w', encoding='utf-8', newline='').write(out)
import os
os.replace(tmp, p)
print('MERGED_OK union_sorted total_new=%d' % len(all_new))
