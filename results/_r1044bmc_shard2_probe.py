import re, json, os
src = open(r'scripts\trial_labor_w20.py', encoding='utf-8').read()
args = re.findall(r"add_argument\(['\"]([^'\"]+)", src)
print('RUNNER ARGS:', args)
for kw in ('checkpoint', 'screen', 'shard'):
    print(kw, 'hits:', len(re.findall(kw, src)))
m = re.findall(r"SCREEN_OUT[A-Z_]*\s*=\s*[^\n]+", src)[:5]
print('SCREEN_OUT faces:', m)
m2 = re.findall(r"results[/\\][a-z0-9_/\\.-]*w20[a-z0-9_/\\.-]*", src)[:10]
print('paths:', set(m2))
