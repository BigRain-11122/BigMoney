# -*- coding: utf-8 -*-
src = open(r"scripts\perpetual_faces.py", encoding="utf-8", newline="").read()
i = src.find("    # W157 (bm-a r772 freeze")
j = src.find('"engine_owner": "bm-a"},', src.find('157: {"a":', i))
print("comment start", i, "row tail", j)
block = src[i:j + len('"engine_owner": "bm-a"},')]
print("block len", len(block))
print(block)
