lines = open('scripts/trial_labor_w17.py', encoding='utf-8').read().splitlines()
# locate _screen_cell_w17 def and print full body
start = None
for n, l in enumerate(lines, 1):
    if l.startswith('def _screen_cell_w17'):
        start = n
        break
end = start
for k in range(start + 1, min(start + 130, len(lines) + 1)):
    if lines[k - 1].startswith('def '):
        end = k
        break
print('=== _screen_cell_w17 lines', start, '..', end - 1, '===')
for k in range(start, end):
    print(k, ':', lines[k - 1])
