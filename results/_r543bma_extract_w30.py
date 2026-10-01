import re, io
t = io.open('research/PERPETUAL_FACES.md', encoding='utf-8').read()
# find the W30 row and extract the W31+ warning segment
idx = t.find('N1 波30')
seg = t[idx:idx+9000]
out = []
for kw in ['W31+ 警示', 'W31', 'W32']:
    pass
# print from 'W31' occurrences
m = re.search(r'W31\+?\s*警示.{0,1200}', seg, re.S)
if m:
    out.append('[W31+ warning] ' + m.group(0))
else:
    # fallback: last 1500 chars of the W30 row
    out.append('[W30 row tail] ' + seg[-1500:])
# also confirm row count of N1 wave table
rows = re.findall(r'- N1 波(\d+)（', t)
out.append('wave rows found: ' + ','.join(rows))
io.open('results/_r543bma_w30row.txt', 'w', encoding='utf-8').write('\n\n'.join(out))
print('written')
