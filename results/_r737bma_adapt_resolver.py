# -*- coding: utf-8 -*-
import io

src = io.open('results/_r736bma_merge_resolve.py', encoding='utf-8').read()
s = src.replace("'round': 'r736 bm-a", "'round': 'r737 bm-a")
s = s.replace('_r736bma_merge_resolve.json', '_r737bma_merge_resolve.json')
s = s.replace('# r736 bm-a merge resolver', '# r737 bm-a merge resolver')

old = "# ---- 5) CODELY.md append-only tail block-union (r506/r706 law: keep both sides' tail entries verbatim)\np = 'CODELY.md'\nraw = open(os.path.join(ROOT, p), 'rb').read().decode('utf-8')\nlines = raw.splitlines(keepends=True)\nidx_open = [i for i, ln in enumerate(lines) if ln.startswith('<<<<<<< ')]"
new = ("# ---- 5) CODELY.md append-only tail block-union (r506/r706 law: keep both sides' tail entries verbatim)\n"
       "p = 'CODELY.md'\n"
       "raw = open(os.path.join(ROOT, p), 'rb').read().decode('utf-8')\n"
       "lines = raw.splitlines(keepends=True)\n"
       "idx_open = [i for i, ln in enumerate(lines) if ln.startswith('<<<<<<< ')]\n"
       "if not idx_open:\n"
       "    decisions[p] = ('no-conflict', 'CODELY.md not a UU face this window (r737 adaptation)')\n"
       "    receipt['faces'][p] = {'action': 'no-conflict'}\n"
       "    _skip = True\n"
       "else:\n"
       "    _skip = False\n"
       "if not _skip:")
assert s.count(old) == 1, 'codely head anchor'
s = s.replace(old, new)

# indent the remaining original CODELY body (from idx_mid to receipt line) by 4 spaces
tail_anchor = "idx_mid = [i for i, ln in enumerate(lines) if ln.rstrip('\\r\\n') == '=======']"
i = s.find(tail_anchor)
assert i > 0, 'idx_mid anchor'
head = s[:i]
body = s[i:]
# find the end of the CODELY block = the receipt['faces'][p] = {'action': 'block-union'...} line
end_marker = "receipt['faces'][p] = {'action': 'block-union'"
j = body.find(end_marker)
assert j > 0, 'block-union receipt anchor'
# find the end of that line
k = body.find('\n', j)
mid = body[:k]
rest = body[k:]
indented = '\n'.join(('    ' + ln if ln.strip() else ln) for ln in mid.splitlines())
s = head + indented + rest
io.open('results/_r737bma_merge_resolve.py', 'w', encoding='utf-8').write(s)
import py_compile
py_compile.compile('results/_r737bma_merge_resolve.py', doraise=True)
print('r737 resolver written+compiled OK, bytes:', len(s))
