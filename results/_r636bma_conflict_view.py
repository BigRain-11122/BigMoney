import re

txt = open(r'results\runnable_pool.json', encoding='utf-8', errors='replace').read()
# locate conflict markers around the divlowvol shard
for m in re.finditer(r'<<<<<<<(.*?)>>>>>>>', txt, re.S):
    seg = m.group(0)
    if 'divlowvol-p1-nulls' in seg or 'w2-judge' in seg.lower():
        print('=' * 50)
        print(seg[:1500])
        print('=' * 50)
print('total marker blocks:', len(re.findall(r'<<<<<<<', txt)))
