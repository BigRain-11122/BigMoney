# -*- coding: utf-8 -*-
import io
p = r'results\_r980bma_dbg_run.py'
src = io.open(p, encoding='utf-8').read()
old = "io.open(r'results/_r980bma_dbg_out.md'"
new = "import io as _io2\nio.open(r'results/_r980bma_dbg_out.md'"
if 'import io as _io2' not in src:
    src = src.replace(old, new, 1)
io.open(p, 'w', encoding='utf-8', newline='').write(src)
print('fixed')
