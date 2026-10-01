# -*- coding: utf-8 -*-
import subprocess

b = open("CODELY.md", "rb").read().decode("utf-8", errors="replace")
marks = [i for i in range(len(b)) if b.startswith("<<<<<<<", i)]
print("conflict regions:", len(marks))
for i in marks:
    seg = b[i:i + 1500]
    print("=== region at", i, "===")
    print(seg[:1200])
    print()
