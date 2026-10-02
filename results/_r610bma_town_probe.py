import re, io, json

t = io.open('town.html', encoding='utf-8').read()
print('town.html bytes:', len(t))
# building/floor name-ish tokens
names = re.findall(r'[\u4e00-\u9fff][\u4e00-\u9fffA-Za-z0-9\-]{1,20}(?:楼|部|办|中心|组|室)', t)
seen = []
for n in names:
    if n not in seen:
        seen.append(n)
print('NAME-TOKENS:', ' | '.join(seen[:80]))
