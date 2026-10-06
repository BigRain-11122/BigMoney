# -*- coding: utf-8 -*-
"""r773 empirical probe: inventory the live W157-era strings in n1.py + pf.py
that the W158 freeze-edits vmap must cover (band forms, bare seeds, bases,
projection prose, ordinals, shas) — read-only."""
import io
import re

src = io.open("scripts/perpetual_faces_n1.py", encoding="utf-8", newline="").read()
k = src.find('157: {"batch"')
m = src.find('"engine_owner": "bm-a"},', k) + len('"engine_owner": "bm-a"},')
entry = src[k:m]
print("W157 entry len", len(entry))
pats = [r"\d{3}_\d{3}\.\.\d{3}_\d{3}", r"\d{3}_\d{3}, \d{3}_\d{3}",
        r"\d{3}_\d{3}\+\d", r"\d{3}_\d{3} \+ 1", r"a_seed_base=\d+",
        r"b_exit_seed_base=\d+", r"shard_subdir=\w+", r"out_name=\w+",
        r"PERPETUAL-N1-W\d+", r"n1_w\d+", r"MSG-[\d\-]+", r"[0-9a-f]{9,10}",
        r"rows \d+", r"row(s)? 1\d\d", r"[a-z]+-(?:fourteenth|fifteenth|sixteenth|seventeenth)",
        r"ONE HUNDRED-AND-[A-Z-]+"]
for p in pats:
    print(p, "->", sorted(set(re.findall(p, entry))))
i = entry.find("W158+ projection")
print("--- W158+ projection prose ---")
print(entry[i:i + 420])
print("--- arith/jump prose faces ---")
for probe in ("jumps to", "range end", "walk hops", "a_seed_base", "b_exit_seed_base"):
    j = entry.find(probe)
    if j >= 0:
        print(f"[{probe}] ...{entry[max(0,j-60):j+80]}...")
print()
pf = io.open("scripts/perpetual_faces.py", encoding="utf-8", newline="").read()
i1 = pf.find("    # W157 (bm-a r772 freeze")
r157 = pf.find('157: {"a": (360_204, 362_203)', i1)
j1 = pf.find('"engine_owner": "bm-a"},', r157) + len('"engine_owner": "bm-a"},')
blk = pf[i1:j1]
print("=== pf W157 comment+row block len", len(blk))
for p in [r"\d{3}_\d{3}, \d{3}_\d{3}", r"\d{3}_\d{3}\.\.\d{3}_\d{3}", r"r7\d\d bm-a", r"[0-9a-f]{9,10}"]:
    print(p, "->", sorted(set(re.findall(p, blk))))
print(blk[:800])
