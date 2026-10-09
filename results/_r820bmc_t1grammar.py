src = open('scripts/trial_labor_w1.py', encoding='utf-8').read()
import re
for m in re.finditer(r'^GRAMMAR[^\n]*', src, re.M):
    print('MODULE DEFAULT:', m.group(0)[:200])
# context around it
i = src.find('GRANMAR')
i = src.find('\nGRAMMAR')
print(src[max(0, i-300):i+300])
