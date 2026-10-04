# -*- coding: utf-8 -*-
import re, io
src = open('firm/org_chart.md', encoding='utf-8').read()
depts = re.findall(r'^#{2,3}\s*(.+)$', src, re.M)
t = open('town.html', encoding='utf-8').read()
# building labels in town.html: look for title/label/name keys and Chinese text blocks
bnames = re.findall(r'(?:title|label|name)\s*[:=]\s*["\u0027]([^"\u0027]{2,24})["\u0027]', t)
lines = ['ORG SECTIONS:'] + depts + ['', 'TOWN KEY NAMES:'] + bnames[:80]
# also grab all CJK string literals (likely building descriptions)
cjk = re.findall(r'["\u0027]([^"\u0027]*[\u4e00-\u9fff][^"\u0027]*)["\u0027]', t)
lines += ['', 'TOWN CJK LITERALS (first 100):'] + cjk[:100]
io.open('results/_r690bma_town_scan.txt', 'w', encoding='utf-8').write('\n'.join(lines))
print('written', len(lines), 'lines')
