raw = open("results/runnable_pool.json", encoding="utf-8", newline="").read()
eol = "\r\n" if "\r\n" in raw[:2000] else "\n"
print("eol:", repr(eol))
kline = ' "key": "generate-0of1"'
i = raw.find(kline)
print("i:", i)
obj_start = raw.rfind("{", 0, i)
j = raw.find("}", i)
print("obj_start:", obj_start, "j:", j)
line_start = raw.rfind(eol, 0, obj_start) + len(eol)
line_end = raw.find(eol, j) + len(eol)
block = raw[line_start:line_end]
print("BLOCK len:", len(block))
print(repr(block[:300]))
print("...tail:", repr(block[-120:]))
new_raw = raw[:line_start] + raw[line_end:]
import json
try:
    d2 = json.loads(new_raw)
    g2 = [x for x in d2["entries"] if x["id"] == "PERPETUAL-N2-W15-GENERATE"][0]
    print("reparse OK, shards:", [s["key"] for s in g2["shards"]])
except Exception as e:
    print("reparse FAIL:", str(e)[:200])
# show the seam region around the removal point
print("SEAM:", repr(new_raw[line_start - 80:line_start + 40]))
