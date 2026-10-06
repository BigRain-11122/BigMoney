# -*- coding: utf-8 -*-
"""r812 bm-a W169 finalize probe: discover n1 module subcommands + W168 finalize precedent."""
import re, sys, json, io, os
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

src = io.open("scripts/perpetual_faces_n1.py", encoding="utf-8", errors="replace").read()
print("file chars", len(src), "lines", src.count("\n"))
funcs = re.findall(r"def (\w+)\(", src)
print("funcs:", funcs)
m = re.findall(r"add_parser\(['\"]([\w\-]+)", src)
print("subcommands:", m)
w169 = re.findall(r"\"169\":\s*\{.*?\}", src, re.S)
print("WAVE_CONFIGS[169]:", (w169[0][:400] + "...") if w169 else "NOT FOUND")

# how did W168 finalize happen? find cmd names mentioning finalize/materialize/merge
for kw in ("finalize", "materialize", "merge_shards", "results.json"):
    hits = [(mm.start(), src[max(0, mm.start() - 80): mm.start() + 120].replace("\n", " | "))
            for mm in re.finditer(kw, src)]
    print(f"--- kw={kw} hits={len(hits)}")
    for pos, ctx in hits[:6]:
        print("   ", pos, ctx[:180])
