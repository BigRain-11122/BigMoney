# -*- coding: utf-8 -*-
# r1017 bm-a scratch: byte-exact fix v2 of the NEW a9 last line (chr(92) explicit).
# OUT physical line must be (matching the W245 template line, rolled):
#   "        assert _entry_shard_of(0, 12) == (\"PERPETUAL-N1-W246-SHARD-0",
# i.e. list-element literal whose VALUE ends: ...SHARD-0",   (backslash-escaped
# inner quotes; closing quote; separator comma).
import io

BS = chr(92)  # backslash
gen = 'results/_r1017bma_w246_gen.py'
t = io.open(gen, encoding='utf-8', newline='').read()
lines = t.split('\n')
hits = [n for n, ln in enumerate(lines)
        if '_entry_shard_of(0, 12)' in ln and 'span(' not in ln]
print('candidates:', [n + 1 for n in hits])
for n in hits:
    print('  L%d: %r' % (n + 1, lines[n]))

# target parsed value of the gen triple-quote line (OUT physical bytes):
tgt = ('"        assert _entry_shard_of(0, 12) == (' + BS + '"PERPETUAL-N1-W246-SHARD-0'
       + BS + '",')
# encode for the gen ''' block: double every backslash
enc = tgt.replace(BS, BS * 2)
new_line = enc + "'''"
print('target parsed : %r' % tgt)
print('new gen line  : %r' % new_line)

n = hits[-1]
if lines[n].rstrip('\r') != new_line:
    lines[n] = new_line
    io.open(gen, 'w', encoding='utf-8', newline='').write('\n'.join(lines))
    print('FIXED L%d' % (n + 1))
    print('  after: %r' % lines[n])
else:
    print('already correct')
