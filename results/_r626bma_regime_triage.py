# -*- coding: utf-8 -*-
"""r626 regime_state drift triage: shared vs merged-view per-face diff (D-03 batch gate requires full diff before judgment)."""
import json, subprocess

shared = json.load(open('results/regime_state.json', encoding='utf-8'))
lane_a = json.load(open('results/regime_state.bm-a.json', encoding='utf-8'))

print('shared top keys:', sorted(shared.keys()))
print('lane bm-a top keys:', sorted(lane_a.keys()) if isinstance(lane_a, dict) else type(lane_a))

def kdiff(a, b, path=''):
    out = []
    if isinstance(a, dict) and isinstance(b, dict):
        for k in sorted(set(a) | set(b)):
            if k not in a:
                out.append(('ONLY-IN-MERGED', path + '/' + str(k)))
            elif k not in b:
                out.append(('ONLY-IN-SHARED', path + '/' + str(k)))
            else:
                out.extend(kdiff(a[k], b[k], path + '/' + str(k)))
    elif a != b:
        sa, sb = str(a)[:60], str(b)[:60]
        out.append(('DIFF', path, sa, sb))
    return out

for d in kdiff(shared, lane_a)[:30]:
    print(d)
