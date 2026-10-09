import re

src = open('scripts/trial_labor_w17.py', encoding='utf-8').read()
for m in re.finditer(r"\bfaces?\b[^\n]{0,90}", src):
    print(m.start(), ':', m.group(0)[:110])

print('=== screen jobs construction ===')
i = src.find('def cmd_screen(')
seg = src[i:i+12000]
j = seg.find('jobs')
while j != -1 and j < len(seg):
    line_start = seg.rfind('\n', 0, j)
    print(seg[line_start+1:j+220].replace('\n', ' | ')[:260])
    print('---')
    j = seg.find('jobs', j+1)
    if j > 6000:
        break
