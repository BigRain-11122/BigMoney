# -*- coding: utf-8 -*-
import subprocess, sys, importlib.util
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
spec = importlib.util.spec_from_file_location('se', 'Tools/saturation_engine.py')
se_mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(se_mod)
r = subprocess.run(['git', 'show', 'a9ab3b51d:research/PERPETUAL_N1_W241_PREREG.md'], capture_output=True)
tpl = r.stdout.decode('utf-8')
print('tpl 238 行 =', tpl.count('238 行'), '| 239 行 =', tpl.count('239 行'))
print('tpl engine_owner 行 =', tpl.count('engine_owner 行'), 'owner rows =', tpl.count('owner rows'))
# find all '238 行' and '239 行' contexts in template
for pat in ['238 行', '239 行']:
    i = 0
    while True:
        j = tpl.find(pat, i)
        if j < 0:
            break
        print(repr(tpl[max(0, j-40):j+40]))
        i = j + 1
