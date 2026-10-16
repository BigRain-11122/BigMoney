# -*- coding: utf-8 -*-
# r1050 bm-c: comprehensive needle repair for the dead-window W252 derive editor.
# Root cause class: hand-written needles drifted from the committed W251 source
# ("W240..W250 A-ladder" vs actual "W240..W249 A-ladder"; P5e-tailcmt needle
# authored in post-blanket form while chunk() re-applies xf()).
# Law: needles rebuilt PROGRAMMATICALLY from the source blob (r962/r1049 lineage).
import io

EP = "results/_w252bmc_derive_editor.py"
SRC = "results/_w251bmc_freeze_edits.py"

ed = io.open(EP, encoding="utf-8").read()
src = io.open(SRC, encoding="utf-8").read()

# ---- Fix 2 first: P5e-tailcmt needle -> verbatim RAW source band-facts block
i = src.find('"        # band facts (law sec.4 W251 row)')
assert i > 0, "band-facts block not found in source"
end_token = "no staircase-equality assumption);\","
j = src.find(end_token, i)
assert j > 0, "band-facts block end not found"
raw_block = src[i:j + len(end_token)]
assert raw_block.count("\n") == 20, f"raw block lines {raw_block.count(chr(10))}"

needle_start = ed.find("chunk('''\"        # band facts")
assert needle_start > 0, "tailcmt needle start not found"
close_marker = "''',\n'''"
k = ed.find(close_marker, needle_start)
assert k > 0, "tailcmt needle close not found"
ed = ed[:needle_start] + "chunk('''" + raw_block + close_marker + ed[k + len(close_marker):]
print("Fix2 tailcmt needle rebuilt from verbatim source (%d chars)" % len(raw_block))

# ---- token fixes (unique suffix contexts)
fixes = [
    # (old, new, unique-suffix context to disambiguate, tag)
    ("hops past the W240..W250 A-ladder + W251-A + own-A reservation; B lands",
     "hops past the W240..W249 A-ladder + W251-A + own-A reservation; B lands",
     "mem-b rep needle (post-blanket)"),
    ("the walk hops past the W240..W250 A-ladder bands + W251-A + the own-wave A window)",
     "the walk hops past the W240..W249 A-ladder bands + W251-A + the own-wave A window)",
     "bassert5 rep needle (post-blanket)"),
    ("hops past the W240..W250 A-ladder + W251-A + own-A reservation, ",
     "hops past the W240..W249 A-ladder + W250-A + own-A reservation, ",
     "pr chunk needle (RAW form: W250-A)"),
    ("SEED_REGISTRY seed 545_500 + the W240..W250 A-ladder bands + W251-A",
     "SEED_REGISTRY seed 545_500 + the W240..W249 A-ladder bands + W251-A",
     "rcpt-semantics-B rep needle (post-blanket)"),
]
for old, new, tag in fixes:
    n = ed.count(old)
    assert n == 1, f"[{tag}] count {n} != 1"
    ed = ed.replace(old, new)
    print(f"fixed [{tag}]")

leftover = ed.count("W240..W250")
assert leftover == 0, f"leftover W240..W250 tokens: {leftover}"
io.open(EP, "w", encoding="utf-8", newline="").write(ed)
print("ALL NEEDLE FIXES LANDED")
