import re
s = open('town.html', encoding='utf-8').read()
m = re.search(r'<script>(.*)</script>', s, re.S)
open('results/_r414bmb_town_extracted.js', 'w', encoding='utf-8').write(m.group(1))
print('extracted', len(m.group(1)), 'chars')
