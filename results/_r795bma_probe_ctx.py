# -*- coding: utf-8 -*-
"""r795 bm-a final probe: every r794 occurrence in the landed faces with
+-60 char context, to classify freeze(r795) vs pre-seat/gate(r793) vs
tool-filename (keep) attribution. Read-only."""
import io

targets = [
    ("PF", "scripts/perpetual_faces.py"),
    ("N1", "scripts/perpetual_faces_n1.py"),
    ("PRE", "research/PERPETUAL_N1_W165_PREREG.md"),
]
out = io.open("results/_r795bma_r794_contexts.txt", "w", encoding="utf-8")
for tag, path in targets:
    src = io.open(path, encoding="utf-8", newline="").read()
    out.write(f"########## {tag} ##########\n")
    n = 0
    i = 0
    while True:
        i = src.find("r794", i)
        if i < 0:
            break
        n += 1
        ctx = src[max(0, i - 60):i + 64].replace("\n", "\\n").replace("\r", "\\r")
        out.write(f"[{n}] @{i}: ...{ctx}...\n")
        i += 4
    out.write(f"total r794 in {tag}: {n}\n\n")
out.close()
print("dumped results/_r795bma_r794_contexts.txt")
