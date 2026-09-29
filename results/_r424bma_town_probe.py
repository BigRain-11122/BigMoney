import io, re
th = io.open('town.html', encoding='utf-8').read()
print('town.html len:', len(th))
ids = re.findall(r'id="([a-zA-Z0-9_\-]+)"', th)
print('total ids:', len(ids))
names = re.findall(r'(?:title|label|name)\s*[:=]\s*["\']([^"\']{2,24})["\']', th)
seen = []
for n in names:
    if n not in seen:
        seen.append(n)
print('named items (%d):' % len(seen))
for n in seen[:50]:
    print('  -', n)
