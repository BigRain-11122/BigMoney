import re
t = open('scripts/update_daily.py', encoding='utf-8').read()
for m in re.finditer(r'.{80}open\([^\n]{0,120}["\x27]w[^\n]{0,40}', t):
    print(repr(m.group(0)[-170:]))
print('---PATHS---')
m = re.search(r'(?:from|import)[^\n]*paths[^\n]*\n', t)
print(m.group(0) if m else 'no PATHS import line')
j = t.find('PATHS')
if j > 0:
    print(t[max(0, j-220):j+120].replace('\n', ' | '))
# where does it resolve the csv dir
for m in re.finditer(r'(?:def [a-z_]+|csv_dir|daily_dir|panel)[^\n]{0,110}', t):
    print('>>', m.group(0)[:120])
