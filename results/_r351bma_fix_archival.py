p = 'results/_r351bma_codely_archival.py'
raw = open(p, 'rb').read()
bad = b"decode('utf-8').split('" + b"\x5cn" + b'")) if i not in (i96, i99))'
good = b"decode('utf-8').split('" + b"\x5cn" + b"')) if i not in (i96, i99))"
assert bad in raw, 'pattern not found'
raw = raw.replace(bad, good)
open(p, 'wb').write(raw)
import ast
ast.parse(open(p, encoding='utf-8').read())
print('fix applied, AST OK')
