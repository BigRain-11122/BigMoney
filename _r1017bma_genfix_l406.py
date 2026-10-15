# -*- coding: utf-8 -*-
# r1017 bm-a scratch: show raw bytes of gen L406 + the W245 reference line,
# then rewrite L406 to the byte-exact rolled form.
import io

gen = 'results/_r1017bma_w246_gen.py'
t = io.open(gen, encoding='utf-8', newline='').read()
lines = t.split('\n')
idx = None
for n, ln in enumerate(lines):
    if '_entry_shard_of(0, 12)' in ln and 'NEW' not in ln and 'OLD' not in ln and 'assert' in ln:
        idx = n
        break
print('gen L%d raw: %r' % (idx + 1, lines[idx]))

ref = io.open('results/_w245bma_freeze_edits.py', encoding='utf-8', newline='').read()
i = ref.find('_entry_shard_of(0, 12)')
ls = ref.rfind('\n', 0, i) + 1
le = ref.find('\n', i)
w245_line = ref[ls:le]
print('w245 ref raw: %r' % w245_line)
# rolled form: W245->W246 inside the shard name (the only wave literal)
rolled = w245_line.replace('PERPETUAL-N1-W245-SHARD-0', 'PERPETUAL-N1-W246-SHARD-0')
# gen triple-quote encoding of the target physical line:
#   backslash -> \\, quote stays, EXCEPT we must double any backslash and
#   escape any ''' sequence (none present)
enc = rolled.replace('\\', '\\\\')
print('target physical (rolled): %r' % rolled)
print('target encoded for gen triple-quote: %r' % enc)
