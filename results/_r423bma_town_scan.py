import re

t = open('town.html', encoding='utf-8').read()
for m in re.finditer(r'(name|title|label|desc|detail|info)\s*[:=]\s*["\']([^"\']{2,60})["\']', t):
    print(m.group(1), '=', m.group(2))
print('---BUILDINGS array-ish---')
for m in re.finditer(r'\{[^{}]*?(?:楼|部|所|苑|馆|Tower|Hall)[^{}]*?\}', t):
    s = m.group(0)
    if len(s) < 300:
        print(s)
