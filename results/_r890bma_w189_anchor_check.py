# -*- coding: utf-8 -*-
"""r890 bm-a W189 anchor-shape verification (read-only) before rolling the
face probe. Confirms the W188 physical faces in pf.py / n1.py for the W189
freeze pre-TOK inventory."""
import io
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
pf = io.open(r"scripts/perpetual_faces.py", encoding="utf-8", newline="").read()
n1 = io.open(r"scripts/perpetual_faces_n1.py", encoding="utf-8", newline="").read()
print("pf W188 comment block:", pf.count("    # W188 (bm-a r888 freeze"))
print("pf W188 row:", pf.count('188: {"a": (428_404'))
print("n1 188 entry:", n1.count('188: {"batch"'))
print("n1 W188 materializer:", n1.count("# --- W188 materializer face"))
print("n1 W188 claim:", n1.count('"+ W188 materializer face'))
print("n1 claim session marker r888:", n1.count('"r888 bm-a] "'))
i2 = pf.find("    # W188 (bm-a r888 freeze")
print("pf W188 block head:", repr(pf[i2:i2 + 90]))
cs = n1.find('"+ W188 materializer face')
print("claim head:", repr(n1[cs:cs + 120]))
