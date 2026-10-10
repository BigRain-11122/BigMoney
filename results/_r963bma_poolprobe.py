import json, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

def load(p):
    with open(p, encoding='utf-8') as f:
        return json.load(f)

pool = load('results/runnable_pool.json')
for e in pool['entries']:
    print(json.dumps(e, ensure_ascii=False)[:600])
    print('---')
