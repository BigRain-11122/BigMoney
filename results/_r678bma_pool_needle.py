import re
P = r"results\runnable_pool.json"
raw = open(P, "rb").read().decode("utf-8")
i = raw.find('"THEME-JUDGE-P2"')
j = raw.find('"id"', i + 10)
if j == -1:
    j = len(raw)
seg = raw[i - 60:min(len(raw), i + 1200)]
print("----SEG----")
print(seg)
print("----COUNTS----")
print("theme-judge-p2-burn key count:", raw.count('"theme-judge-p2-burn-0of1"'))
print('THEME-JUDGE-P2 id count:', raw.count('"THEME-JUDGE-P2"'))
