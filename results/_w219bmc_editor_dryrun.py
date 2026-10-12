# -*- coding: utf-8 -*-
# DRY RUN of _w219bmc_editor_gen.py: applies masks+blankets, then reports each
# E1 find-count (post-blanket) instead of applying. No output written.
# (Lineage: _w218bmc_editor_dryrun.py; belt-and-braces re-verification per
# the r918/r919 chain convention -- bad=0 required before the gen applies.)
import sys
sys.stdout.reconfigure(encoding="utf-8")
src = open(r"results\_w219bmc_editor_gen.py", encoding="utf-8").read()
marker = "for find, repl, what in E:\n    t = rep1(t, find, repl, what)"
cut = src.index(marker)
head = src[:cut]
DRY = '''
print("=== DRY: E1 find counts (post-blanket) ===")
bad = 0
for find, repl, what in E:
    c = t.count(find)
    flag = "OK " if c == 1 else "!! "
    if c != 1:
        bad += 1
    find_show = find if len(find) <= 90 else find[:87] + "..."
    print(f"{flag}[{what}] count={c}: {find_show!r}")
print(f"=== DRY: bad={bad} of {len(E)} ===")
c2 = t.count("SEVENTY-NINTH instance anticipated")
print(f"[proj-ordinal repn] count={c2} (expect 2)")
'''
open(r"results\_w219bmc_editor_dryrun_core.py", "w", encoding="utf-8").write(head + DRY)
import py_compile
py_compile.compile(r"results\_w219bmc_editor_dryrun_core.py", doraise=True)
print("dry-run core built OK")
