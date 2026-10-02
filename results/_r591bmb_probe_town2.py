import io, re
t = io.open('town.html', encoding='utf-8', errors='replace').read()
# find building-ish markup: divs with class building/sector/house etc.
for cls in set(re.findall(r'class="([a-z-]+)"', t)):
    n = len(re.findall(r'class="%s"' % cls, t))
    if n and ('build' in cls or 'house' in cls or 'sector' in cls or 'dept' in cls or 'block' in cls or 'lot' in cls):
        print('class:', cls, 'x', n)
# extract visible labels near buildings
labels = re.findall(r'<div class="b-title">(.*?)</div>', t)
print('b-title:', labels[:30])
labels2 = re.findall(r'class="building[^"]*"[^>]*>\s*<[^>]+>([^<]{2,40})<', t)
print('building labels:', labels2[:30])
h2 = re.findall(r'<h2[^>]*>(.*?)</h2>', t)
print('h2:', h2[:20])
spans = re.findall(r'<span class="bl">([^<]+)</span>', t)
print('bl spans:', spans[:40])
strong = re.findall(r'<strong>([^<]{2,30})</strong>', t)
print('strong:', strong[:40])
