# -*- coding: utf-8 -*-
# r1017 bm-a scratch: byte-exact fix v3 -- full alignment with the W245 template
# line: element literal + separator comma. OUT physical target:
#   "        assert _entry_shard_of(0, 12) == (\"PERPETUAL-N1-W246-SHARD-0",
# ending bytes: backslash, quote, comma, quote, comma  (\:"",) -- closing quote
# then list separator comma, exactly like the W245 physical line.
import io

BS = chr(92)
gen = 'results/_r1017bma_w246_gen.py'
t = io.open(gen, encoding='utf-8', newline='').read()
lines = t.split('\n')
hits = [n for n, ln in enumerate(lines)
        if '_entry_shard_of(0, 12)' in ln and 'span(' not in ln]
n = hits[-1]
print('current L%d: %r' % (n + 1, lines[n]))

tgt = ('"        assert _entry_shard_of(0, 12) == (' + BS + '"PERPETUAL-N1-W246-SHARD-0'
       + BS + '",' + '"' + ',')
enc = tgt.replace(BS, BS * 2)
new_line = enc + "'''"
print('target parsed: %r' % tgt)
print('new gen line : %r' % new_line)

# sanity: parsed form of new_line must equal tgt
import ast
parsed = ast.literal_eval("'''" + new_line + "'''")
assert parsed == tgt, 'roundtrip mismatch'
print('roundtrip OK')
if lines[n].rstrip('\r') != new_line:
    lines[n] = new_line
    io.open(gen, 'w', encoding='utf-8', newline='').write('\n'.join(lines))
    print('FIXED L%d' % (n + 1))
else:
    print('already correct')
