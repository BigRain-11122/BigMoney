import io, re, sys
sys.stdout.reconfigure(encoding='utf-8')
c = io.open('town.html', encoding='utf-8').read()
print('town.html bytes:', len(c))
print('SPM mentions:', c.count('SPM'), '| KPI mentions:', c.count('KPI'))
# extract building/department titles as rendered
titles = re.findall(r'class="building-title"[^>]*>([^<]+)<', c)
if not titles:
    titles = re.findall(r'<h3[^>]*>([^<]+)</h3>', c)
print('titles found:', len(titles))
for t in titles[:40]:
    print('  T:', t.strip())
# floors
floors = re.findall(r'class="(?:floor|unit|dept)[^"]*"[^>]*>([^<]{2,40})<', c)
print('floor-ish entries:', len(floors))
for f in floors[:30]:
    print('  F:', f.strip())
