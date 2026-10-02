import io, re
t = io.open('town.html', encoding='utf-8', errors='replace').read()
blds = re.findall(r'<h3>(.*?)</h3>', t)
print('town h3:', [b.strip()[:26] for b in blds])
o = io.open('firm/org_chart.md', encoding='utf-8', errors='replace').read()
i = o.find('部门')
print('org_chart len:', len(o))
print(o[max(0,i-200):i+1100])
