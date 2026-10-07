import io
n1 = io.open(r"scripts/perpetual_faces_n1.py", encoding="utf-8", newline="").read()
pf = io.open(r"scripts/perpetual_faces.py", encoding="utf-8", newline="").read()

k = n1.find('172: {"batch"')
ls = n1.rfind("\n", 0, k) + 1
print("ENTRY LINE PREFIX:", repr(n1[ls:k]))
eo = n1.find('"engine_owner": "bm-a"},', k)
after = n1[eo:eo+120]
print("AFTER ENTRY EO:", repr(after[:80]))
# dict closing
c = n1.find("}\r\n", eo)
print("CLOSING SEG:", repr(n1[eo:c+4]))

# pf insertion point
r = pf.find('172: {"a": (393_204')
e2 = pf.find('"engine_owner": "bm-a"},', r)
c2 = pf.find("}\r\n", e2)
print("PF AFTER ROW:", repr(pf[e2:c2+4]))

# mat insert anchor
m = n1.find("    # --- T-141 s2 lane face")
print("T141 ANCHOR:", repr(n1[m-2:m+60]))

# claim anchor area
cs = n1.find('"r819 bm-a] "')
print("CLAIM AREA:", repr(n1[cs-30:cs+80]))
