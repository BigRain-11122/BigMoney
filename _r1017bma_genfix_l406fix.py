# -*- coding: utf-8 -*-
# r1017 bm-a scratch: byte-exact fix of the NEW a9 last line in the gen file.
# Target parsed value (OUT physical line):
#   "        assert _entry_shard_of(0, 12) == (\"PERPETUAL-N1-W246-SHARD-0\",
# Gen triple-quote encoding doubles every backslash.
import io

gen = 'results/_r1017bma_w246_gen.py'
t = io.open(gen, encoding='utf-8', newline='').read()
lines = t.split('\n')
hits = [n for n, ln in enumerate(lines)
        if '_entry_shard_of(0, 12)' in ln and 'OLD[' not in ln and 'span(' not in ln]
print('candidate lines:', hits)
for n in hits:
    print('L%d: %r' % (n + 1, lines[n]))

target_parsed = '"        assert _entry_shard_of(0, 12) == (\\"PERPETUAL-N1-W246-SHARD-0\","'
enc = target_parsed.replace('\\', '\\\\')
new_line = enc + "'''"  # last line of the NEW a9 block: content then block close
print('new L bytes: %r' % new_line)

# fix the LAST candidate (the NEW a9 tail line); keep span()/OLD lines untouched
n = hits[-1]
before = lines[n]
if before.rstrip('\r') != new_line:
    lines[n] = new_line
    io.open(gen, 'w', encoding='utf-8', newline='').write('\n'.join(lines))
    print('FIXED L%d' % (n + 1))
    print('  before: %r' % before)
    print('  after : %r' % lines[n])
else:
    print('already correct')
