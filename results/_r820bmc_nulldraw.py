lines = open('scripts/trial_labor_w17.py', encoding='utf-8').read().splitlines()
start = None
for n, l in enumerate(lines, 1):
    if l.startswith('def _null_axis_draw_w17'):
        start = n
        break
end = start + 1
for k in range(start + 1, start + 60):
    if lines[k - 1].startswith('def '):
        end = k
        break
for k in range(start, end):
    print(k, ':', lines[k - 1])
