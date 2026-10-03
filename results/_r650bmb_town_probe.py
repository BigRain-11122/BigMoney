import sys, re, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
t = open(r'town.html', encoding='utf-8').read()
print('SIZE:', len(t))
# building blocks: find BUILDINGS-style arrays or name fields
names = re.findall(r'name\s*:\s*["\']([^"\']{1,40})["\']', t)
print('NAMES(%d):' % len(names))
for n in names:
    print(' -', n)
# detail panel headers / titles
titles = re.findall(r'(?:title|desc|detail)\s*[:=]\s*["\']([^"\']{2,60})["\']', t)
print('TITLES(%d):' % len(titles))
for x in titles[:40]:
    print(' *', x)
