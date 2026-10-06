# -*- coding: utf-8 -*-
"""r779 bm-a W159 pre-TOK probe leg-4: post tail + claim full text."""
import io

post = io.open(r"results/_r779bma_w159_mat_post.txt", encoding="utf-8", newline="").read()
print(post[2600:])
print("=====CLAIM=====")
n = io.open(r"scripts/perpetual_faces_n1.py", encoding="utf-8", newline="").read()
cs = n.find('"+ W158 materializer face')
ce = n.find('"r773 bm-a] "', cs) + len('"r773 bm-a] "')
claim = n[cs:ce]
io.open(r"results/_r779bma_w159_claim158.txt", "w", encoding="utf-8", newline="").write(claim)
print(claim)
