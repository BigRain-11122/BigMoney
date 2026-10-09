lines = open('scripts/trial_labor_w17.py', encoding='utf-8').read().splitlines()
start = None
for n, l in enumerate(lines, 1):
    if l.startswith('def cmd_judge('):
        start = n
        break
seg_end = start + 120
for k in range(start + 1, start + 120):
    if lines[k - 1].startswith('def '):
        seg_end = k
        break
for k in range(start, min(seg_end, start + 120)):
    print(k, ':', lines[k - 1])
