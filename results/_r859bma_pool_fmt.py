txt = open(r'results/runnable_pool.json', encoding='utf-8', newline='').read()
pos = txt.find('"id": "TRIAL-LABOR-W14-JUDGE"')
start = txt.rfind('{', 0, pos)
seg = txt[start:start + 700]
print(repr(seg))
