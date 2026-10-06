# -*- coding: utf-8 -*-
"""r779 bm-a W159 pre-TOK probe leg-5: closing forms after the W158 faces."""
import io

s = io.open(r"scripts/perpetual_faces.py", encoding="utf-8", newline="").read()
i = s.find('158: {"a": (362_404, 364_403)')
print("pf after row:", repr(s[i+80:i+135]))

n = io.open(r"scripts/perpetual_faces_n1.py", encoding="utf-8", newline="").read()
k = n.find('158: {"batch"')
m = n.find('"engine_owner": "bm-a"},', k) + len('"engine_owner": "bm-a"},')
print("n1 after entry:", repr(n[m:m+70]))
w = n.find("# --- W158 materializer face")
t2 = n.find("# --- T-141 s2 lane face", w)
print("after materializer block:", repr(n[t2-40:t2+60]))
cs = n.find('"+ W158 materializer face')
ce = n.find('"r773 bm-a] "', cs)
print("after claim:", repr(n[ce:ce+80]))
