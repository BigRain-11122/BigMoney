import json
import subprocess


def blob_tail(path, n=3):
    b = subprocess.run(['git', 'show', 'HEAD:' + path], capture_output=True).stdout
    return repr(b[-n:])


for p in ['results/runnable_pool.json', 'fleet/tasks/T-2026-09-25-46-P1.json', 'results/gate_attrition.json']:
    print(p, 'HEAD tail:', blob_tail(p))

# 1. pool: CRLF + indent=1
pool = json.load(open('results/runnable_pool.json', encoding='utf-8'))
s = json.dumps(pool, ensure_ascii=False, indent=1)
with open('results/runnable_pool.json', 'w', encoding='utf-8', newline='') as f:
    f.write(s.replace('\n', '\r\n') + '\r\n')
print('pool rewritten CRLF')

# 2. T-46: LF + indent=1
t = json.load(open('fleet/tasks/T-2026-09-25-46-P1.json', encoding='utf-8'))
s = json.dumps(t, ensure_ascii=False, indent=1)
with open('fleet/tasks/T-2026-09-25-46-P1.json', 'w', encoding='utf-8', newline='') as f:
    f.write(s + '\n')
print('T-46 rewritten LF indent=1')

# sanity: reload both
json.load(open('results/runnable_pool.json', encoding='utf-8'))
json.load(open('fleet/tasks/T-2026-09-25-46-P1.json', encoding='utf-8'))
print('reload OK')
