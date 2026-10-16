# -*- coding: utf-8 -*-
"""r1055 dbg: clone the W254 editor, run it up to the P5e-pre chunk call,
dump intermediate t + the pre needle, then report the first divergence."""
import io, re

ED = r"results\_w254bmc_derive_editor.py"
DBG = r"results\_r1055bmc_editor_dbg.py"

t_ed = io.open(ED, encoding="utf-8").read()
i1 = t_ed.find('"P5e-pre")')
i0 = t_ed.rfind("chunk('''", 0, i1)
hook = ('io.open(r"results/_r1055bmc_t_dump.txt", "w", encoding="utf-8", newline="").write(t)\n'
        'import sys as _s; _s.stdout.write("DUMPED\\n"); _s.exit(0)\n')
dbg = t_ed[:i0] + hook + t_ed[i0:]
io.open(DBG, "w", encoding="utf-8", newline="").write(dbg)
print("dbg editor written, hook at", i0)
