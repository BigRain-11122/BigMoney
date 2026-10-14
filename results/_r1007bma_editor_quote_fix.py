# -*- coding: utf-8 -*-
# r1007 bm-a: W244 freeze editor pr-list quoting repair (gen bug form #3).
# Elements 618/619 used a double-quoted wrapper, so their CONTENT lost the
# 10-space indent and the embedded double quotes required by the n1 print
# implicit-concat chain -> output lines 64188-89 landed bare (unquoted) ->
# n1 SyntaxError "'(' was never closed" at the enclosing print (59830).
# Correct form mirrors the A-side elements 616-617 (single-quoted wrapper,
# content = indent + "..." fragment). Count-asserted, exact-content swap.
import io, py_compile

P = "results/_w244bma_freeze_edits.py"
s = io.open(P, "r", encoding="utf-8", newline="").read()
nl = "\r\n" if "\r\n" in s[:5000] else "\n"
lines = s.split(nl)

OLD618 = ' "+ B=FIRST-CLEAN arithmetic continuation of the prior-wave B tail (B-continuation face, ",'
NEW618 = ' \'          "+ B=FIRST-CLEAN arithmetic continuation of the prior-wave B tail (B-continuation face, "\','
OLD619 = ' "hops=0, B_hop_chain empty + B_clean_at_naive_start=true, B base == prior-B-tail+1 EXACT, ",'
NEW619 = ' \'          "hops=0, B_hop_chain empty + B_clean_at_naive_start=true, B base == prior-B-tail+1 EXACT, "\','

i618 = [i for i, l in enumerate(lines) if l == OLD618]
i619 = [i for i, l in enumerate(lines) if l == OLD619]
assert len(i618) == 1 and len(i619) == 1, f"anchor counts {len(i618)}/{len(i619)}"
assert i619[0] == i618[0] + 1, "618/619 not adjacent"
lines[i618[0]] = NEW618
lines[i619[0]] = NEW619
io.open(P, "w", encoding="utf-8", newline="").write(nl.join(lines))
py_compile.compile(P, doraise=True)
print("quoting fix applied (618/619 -> single-quoted indent+embedded-quote form); editor compiles OK")

# structural guard: no remaining pr-list element with the bare double-quote
# wrapper form (starts with space+doublequote and content lacks the indent)
import re
bad = [i + 1 for i, l in enumerate(lines)
       if re.match(r'^ "[^"]*"$', l.rstrip("\r"))]
print("residual bare-double-quote elements:", bad)
assert not bad, bad
