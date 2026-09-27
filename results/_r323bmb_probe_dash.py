# -*- coding: utf-8 -*-
import subprocess, json, re
b = subprocess.run(['git', 'show', ':2:results/dashboard_status.json'], capture_output=True).stdout
d = json.loads(b.decode('utf-8'))
print('dash json keys:', list(d.keys()))
def walk(o, pfx='', depth=0):
    if depth > 2:
        return
    if isinstance(o, dict):
        for k, v in o.items():
            if isinstance(v, str) and '2026-09-27' in v and len(v) < 40:
                print(' tslike:', pfx + k, '=', v)
            walk(v, pfx + k + '.', depth + 1)
walk(d)
bjs = subprocess.run(['git', 'show', ':2:results/dashboard_status.js'], capture_output=True).stdout
print('js head:', bjs[:160])
m = re.search(rb'(?:"ts"|"generated"|"updated"|ts=|generated=)[^\d]*([\d]{4}-[\d]{2}-[\d]{2}[ T][\d:.]+)', bjs)
print('js tslike:', m.group(1).decode() if m else None)
