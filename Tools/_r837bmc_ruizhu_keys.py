import re

src = open(r"K:\Fluxgroup\FluxGroup\软著申请材料\generate_copyright.py", encoding="gbk", errors="replace").read()
start = src.find("PROJECTS = {")
seg = src[start:start + 50000]
keys = re.findall(r'^\s*"([^"]+)":\s*\{', seg, re.M)
print("KEYS:", keys)
for k in keys:
    j = seg.find('"%s"' % k)
    line = seg[j:j + 300].replace("\n", " | ")
    print("---", k, "---", line[:280])
