# -*- coding: utf-8 -*-
"""r1055 absorb heal-2: P5e-pr chunk whitespace structure (compact triple-quote
form per the W253 canon -- first content line rides the ''' opener, terminator
rides the last content line; the dead window's clone broke both, disclosed)."""
import io

ED = r"results\_w254bmc_derive_editor.py"
t = io.open(ED, encoding="utf-8", newline="").read()

edits = [
    # src head: join first content line onto the opener (keep leading space)
    ("chunk('''\n '          \"A=1-HOP STAIRCASE-AFFECTS-A walk (hops=1, A_hop_chain verbatim, A_clean_at_naive_start=false, \"',",
     "chunk(''' '          \"A=1-HOP STAIRCASE-AFFECTS-A walk (hops=1, A_hop_chain verbatim, A_clean_at_naive_start=false, \"',",
     "heal2-src-head"),
    # src tail + separator + dst head: terminators ride the content lines
    ("THIRD consecutive above-own-A landing), chain-order splice from the \"\n''',\n'''\n '          \"A=1-HOP STAIRCASE-AFFECTS-A walk (hops=1, A_hop_chain verbatim, A_clean_at_naive_start=false, \"',",
     "THIRD consecutive above-own-A landing), chain-order splice from the \"''',\n''' '          \"A=1-HOP STAIRCASE-AFFECTS-A walk (hops=1, A_hop_chain verbatim, A_clean_at_naive_start=false, \"',",
     "heal2-mid-join"),
    # dst tail: terminator rides the last content line
    ("FOURTH consecutive above-own-A landing), chain-order splice from the \"\n''', \"P5e-pr\")",
     "FOURTH consecutive above-own-A landing), chain-order splice from the \"''', \"P5e-pr\")",
     "heal2-dst-tail"),
]
for old, new, tag in edits:
    n = t.count(old)
    assert n == 1, f"[{tag}] count {n} != 1"
    t = t.replace(old, new)
    print(f"{tag}: applied 1x")

io.open(ED, "w", encoding="utf-8", newline="").write(t)
print("heal-2 done")
