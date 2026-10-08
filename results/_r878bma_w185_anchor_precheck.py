# -*- coding: utf-8 -*-
import io
pf = io.open(r"scripts/perpetual_faces.py", encoding="utf-8", newline="").read()
n1 = io.open(r"scripts/perpetual_faces_n1.py", encoding="utf-8", newline="").read()
print("pf W184 blk:", pf.find("    # W184 (bm-a r874 freeze"))
print("pf W184 row:", pf.find('184: {"a": (419_604'))
print("n1 184 entry:", n1.find('184: {"batch"'))
print("n1 mat W184:", n1.find("# --- W184 materializer"))
print("n1 T141:", n1.find("# --- T-141 s2 lane face"))
print("n1 claim W184:", n1.find('"+ W184 materializer face'))
print("n1 claim tail r874:", n1.find('"r874 bm-a] "'))
print("pf N1_BANDS rows:", pf.count(': {"a": ('))
print("EO face:", n1.count('"engine_owner": "bm-a"},'))
