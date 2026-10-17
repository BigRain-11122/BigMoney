import io
import re

t = io.open(r"results/watermark_red.json", encoding="utf-8", errors="replace").read()
m = re.findall(r"<<<<<<<.*?=======.*?>>>>>>>", t, re.S)
print("conflict_blocks", len(m))
for b in m[:3]:
    print("---BLOCK (300 chars)---")
    print(b[:300])
ours_side = t.split("=======")[0]
theirs_side = t.split("=======")[1] if "=======" in t else ""
print("ours_ts:", re.findall(r'"ts":\s*"([^"]+)"', ours_side)[-3:])
print("theirs_ts:", re.findall(r'"ts":\s*"([^"]+)"', theirs_side)[-3:])
