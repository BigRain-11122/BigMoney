lines = open('scripts/trial_labor_w17.py', encoding='utf-8').read().splitlines()
# find def boundaries around line 350 (1-based)
for n in range(350, 0, -1):
    if lines[n-1].startswith('def '):
        print('line 350 belongs to:', lines[n-1][:80], '(def at line', n, ')')
        break
# print that def fully
start = n
end = start
for k in range(start, min(start+220, len(lines)+1)):
    if k > start and lines[k-1].startswith('def '):
        end = k
        break
print('=== def body lines', start, '..', end-1, '===')
for k in range(start, min(end+2, start+200)):
    print(k, ':', lines[k-1])
