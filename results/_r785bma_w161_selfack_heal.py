# -*- coding: utf-8 -*-
"""r785 bm-a W161 self-ack honesty-face heal (surgical fragment-level replace,
r783 heal precedent): during the W161 freeze window bm-b r779 (a2d002357)
read-only-observer-processed the W161 seat MSG (inbox -> processed/, W159
bm-c-r625 precedent class) -- the landed W161 block prose cited "bm-a r784
finalize window" (the W160 seat's mover) as the W161 seat's mover, which is
the wrong attribution. Heal both faces (pf.py + n1.py mat) with the
machine-verified fact: mover = bm-b r779, commit a2d002357."""
import ast
import io
import subprocess

PF = r"scripts/perpetual_faces.py"
N1 = r"scripts/perpetual_faces_n1.py"
CRLF = "\r\n"

# machine-verify the fact before healing (never transcribe)
out = subprocess.check_output(["git", "show", "--stat", "--oneline", "a2d002357",
                               "--", "fleet/inbox/", "fleet/inbox/processed/"],
                              encoding="utf-8")
assert "round 779" in out and "via bm-b" in out, out[:80]
# seat rename evidence: R100 rename inbox -> processed in the r779 commit
r = subprocess.run(["git", "diff", "--name-status", "a2d002357^", "a2d002357",
                   "--", "fleet/inbox/MSG-2026-10-06-165x-bma-w161-seat.md",
                   "fleet/inbox/processed/MSG-2026-10-06-165x-bma-w161-seat.md"],
                  capture_output=True, encoding="utf-8")
assert "R100" in r.stdout and "fleet/inbox/processed/MSG-2026-10-06-165x-bma-w161-seat.md" in r.stdout, r.stdout

pfsrc = io.open(PF, encoding="utf-8", newline="").read()
n1src = io.open(N1, encoding="utf-8", newline="").read()

old_pf = ("move landed (bm-a r784 finalize window; seat in" + CRLF +
          "    # fleet/inbox/processed/);")
new_pf = "move landed (bm-b r779 read-only-observer processed, a2d002357);"
assert pfsrc.count(old_pf) == 1, pfsrc.count(old_pf)

old_n1 = ("self-ack inbox->processed move landed (bm-a" + CRLF +
          "    #     r784 finalize window; seat in fleet/inbox/processed/).")
new_n1 = ("self-ack inbox->processed move landed (bm-b" + CRLF +
          "    #     r779 read-only-observer processed, a2d002357).")
assert n1src.count(old_n1) == 1, n1src.count(old_n1)

pfsrc = pfsrc.replace(old_pf, new_pf)
io.open(PF, "w", encoding="utf-8", newline="").write(pfsrc)
n1src = n1src.replace(old_n1, new_n1)
io.open(N1, "w", encoding="utf-8", newline="").write(n1src)

ast.parse(io.open(PF, encoding="utf-8", newline="").read())
ast.parse(io.open(N1, encoding="utf-8", newline="").read())
# r776 fragment-needle law: the n1 face is two physical lines -- assert the
# within-fragment shapes, never a needle spanning CRLF
assert "bm-b r779 read-only-observer processed, a2d002357" in pfsrc
assert "self-ack inbox->processed move landed (bm-b" in n1src
assert "r779 read-only-observer processed, a2d002357)." in n1src
assert "bm-a r784 finalize window" not in pfsrc and "bm-a r784 finalize window" not in n1src
print("W161 self-ack honesty heal landed (mover = bm-b r779 a2d002357, W159 r625 precedent class), AST gates PASS")
