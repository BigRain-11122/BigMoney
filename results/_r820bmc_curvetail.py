import re
src17 = open('scripts/trial_labor_w17.py', encoding='utf-8').read()
# rest of run_candidate_curve_w17 body (lines 367..414)
lines = src17.splitlines()
print('=== curve fn tail 367-414 ===')
for k in range(367, 415):
    print(k, ':', lines[k-1])
