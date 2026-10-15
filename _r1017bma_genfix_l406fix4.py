# -*- coding: utf-8 -*-
# r1017 bm-a scratch: byte-exact fix v4 (fix3 had a triple-quote double-append
# bug in its own roundtrip check and never wrote). GEN L406 tail must encode
# the W245-template-rolled element; OUT physical line value must equal the
# rolled template element VALUE byte-exactly (leading space deviation from the
# dead window's sibling NEW lines is cosmetic-only, list elements).
import ast
import io

BS = chr(92)
gen = 'results/_r1017bma_w246_gen.py'
t = io.open(gen, encoding='utf-8', newline='').read()
lines = t.split('\n')
hits = [n for n, ln in enumerate(lines)
        if '_entry_shard_of(0, 12)' in ln and "'''" in ln]
assert len(hits) == 1, 'expect exactly 1 triple-quote entry_shard line, got %d' % len(hits)
n = hits[0]
print('current L%d: %r' % (n + 1, lines[n]))

# target GEN physical line: '''-content == OUT physical line:
#   "        assert _entry_shard_of(0, 12) == (\"PERPETUAL-N1-W246-SHARD-0\",",
out_line = ('"        assert _entry_shard_of(0, 12) == (' + BS + '"PERPETUAL-N1-W246-SHARD-0'
            + BS + '",')
out_line += '"' + ','
gen_line = out_line.replace(BS, BS * 2) + "'''"
print('target OUT line : %r' % out_line)
print('new gen L%d     : %r' % (n + 1, gen_line))

# sanity 1: gen line closes a ''' block whose content == out_line
parsed = ast.literal_eval("'''\n" + gen_line)
assert parsed.strip('\n') == out_line, 'roundtrip mismatch: %r' % parsed
# sanity 2: out_line is a valid string-literal element; its VALUE must equal
# the W245 template element value rolled W245->W246 byte-exactly
mod = ast.parse(out_line + '\n')
elem = mod.body[0].value
if isinstance(elem, ast.Tuple):  # trailing separator comma -> 1-elt tuple expr
    assert len(elem.elts) == 1, 'expect 1-elt tuple, got %d' % len(elem.elts)
    elem = elem.elts[0]
assert isinstance(elem, ast.Constant), 'not a plain literal'
ref = io.open('results/_w245bma_freeze_edits.py', encoding='utf-8', newline='').read()
i = ref.find('_entry_shard_of(0, 12)')
ls = ref.rfind('\n', 0, i) + 1
le = ref.find('\n', i)
w245_line = ref[ls:le].rstrip('\r')
def _elem(src_line):
    e = ast.parse(src_line.lstrip(' ') + '\n').body[0].value
    if isinstance(e, ast.Tuple):  # trailing separator comma -> 1-elt tuple expr
        assert len(e.elts) == 1, 'expect 1-elt tuple, got %d' % len(e.elts)
        e = e.elts[0]
    assert isinstance(e, ast.Constant), 'not a plain literal: %r' % e
    return e.value


ref = io.open('results/_w245bma_freeze_edits.py', encoding='utf-8', newline='').read()
i = ref.find('_entry_shard_of(0, 12)')
ls = ref.rfind('\n', 0, i) + 1
le = ref.find('\n', i)
w245_line = ref[ls:le].rstrip('\r')
rolled_value = _elem(w245_line).replace('W245', 'W246')
my_value = _elem(out_line)
assert my_value == rolled_value, 'VALUE drift vs template: %r vs %r' % (
    my_value, rolled_value)
print('roundtrip OK + element-VALUE template-exact OK')

if lines[n].rstrip('\r') != gen_line:
    lines[n] = gen_line
    io.open(gen, 'w', encoding='utf-8', newline='').write('\n'.join(lines))
    print('FIXED L%d' % (n + 1))
else:
    print('already correct')
ast.parse(io.open(gen, encoding='utf-8', newline='').read())
print('gen parses OK')
