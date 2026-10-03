# r627 bm-a: inspect fund_value_p1 _G init path for the four-point verify (d) recompute
import re
src = open('scripts/fund_value_p1.py', encoding='utf-8').read()

for m in re.finditer(r'_G\["([a-z_]+)"\]\s*=', src):
    print('set _G[', m.group(1), ']')

i = src.index('AMT20_MIN')
print('--- constants ---')
print(src[i-600:i+500])

# find where _G is populated inside a function
for m in re.finditer(r'def (cmd_run|_init|_load_all|_setup)\(', src):
    j = m.start()
    print('=== fn:', m.group(1), '===')
    print(src[j:j+2200])
