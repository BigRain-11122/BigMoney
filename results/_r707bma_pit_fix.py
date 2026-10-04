import io
p = 'research/pit-engine.md'
b = io.open(p, 'rb').read()
old_sep = b'\r\n\r\n\r\n- [2026-10-05 02:1x r707 bm-a]'
new_sep = b'\r\n\r\n- [2026-10-05 02:1x r707 bm-a]'
assert b.count(old_sep) == 1, 'separator not unique/found'
nb = b.replace(old_sep, new_sep)
assert not nb.endswith(b'\n')
nb = nb + b'\r\n\r\n'
io.open(p, 'wb').write(nb)
back = io.open(p, 'rb').read()
assert back == nb
print('size', len(b), '->', len(nb))
print('tail:', repr(back[-60:]))
