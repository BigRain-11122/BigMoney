import re
src = open(r'scripts\trial_labor_w17.py', encoding='utf-8').read()
# 1) all starts-gate patterns in w17
for m in re.finditer(r'listed\.iloc\[p\]', src):
    ln = src[:m.start()].count('\n') + 1
    print('L' + str(ln), src.splitlines()[ln - 1].strip()[:120])
# 2) cmd_generate leg-D face
i = src.find('def cmd_generate')
seg = src[i:src.find('def cmd_', i + 10)]
for m in re.finditer(r'MIN_LISTED|leg == "D"|_load_leg\("D"\)|starts', seg):
    off = seg[:m.start()].count('\n')
    print('GEN off', off, ':', seg.splitlines()[off].strip()[:120])
