import re

src = open('scripts/trial_labor_w17.py', encoding='utf-8').read()
i = src.find('def _screen_cell_w17')
j = src.find('\ndef ', i + 10)
seg = src[i:j]
print('cell fn length:', len(seg))
for m in re.finditer(r'(GRAMMAR|grammar)[^\n]{0,90}', seg):
    print(m.start(), ':', m.group(0)[:110])
print()
print('=== W17 exit-face access in cell fn ===')
for m in re.finditer(r'(exit_face|exit_cfg|EXIT|state\[)[^\n]{0,90}', seg):
    t = m.group(0)
    if 'exit' in t.lower():
        print(m.start(), ':', t[:110])
