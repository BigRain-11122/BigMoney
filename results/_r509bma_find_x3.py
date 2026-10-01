import json

d = json.load(open("results/shortline_p4_folk.json", encoding="utf-8"))
s = json.dumps(d)
i = s.find("needle")
seg = s[i:i + 2500]
j = seg.find("x3")
print("needle-entry x3:", seg[j - 80:j + 400] if j >= 0 else "ABSENT")
# where does 0.4833 appear anywhere in folk/queue/batch1 files?
for p in ("results/shortline_p4_folk.json",
          "results/shortline_p4_queue.json",
          "results/shortline_p4_batch1.json"):
    try:
        t = json.dumps(json.load(open(p, encoding="utf-8")))
    except Exception as e:
        print(p, "ERR", e)
        continue
    k = t.find("0.4833")
    print(p, "0.4833 at", k, t[max(0, k - 120):k + 80] if k >= 0 else "")
