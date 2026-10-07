import io
n1 = io.open(r"scripts/perpetual_faces_n1.py", encoding="utf-8", newline="").read()
pf = io.open(r"scripts/perpetual_faces.py", encoding="utf-8", newline="").read()
EO = '"engine_owner": "bm-a"},'
segs = [
    ("pf ROW+CLOSE", EO + "\r\n}", pf),
    ("n1 ENTRY+CLOSE", EO + "\r\n" + "                       }", n1),
    ("n1 T141 MAT ANCHOR", "    # --- T-141 s2 lane face", n1),
    ("n1 CLAIM ANCHOR", '"r819 bm-a] "\r\n          "+ T-141 s2 "', n1),
]
for name, seg, src in segs:
    print(name, "count=", src.count(seg))
