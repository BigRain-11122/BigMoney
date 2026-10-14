import json, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 1. pool structure
p = json.load(open('results/runnable_pool.json', encoding='utf-8'))
print('POOL TYPE:', type(p).__name__)
if isinstance(p, dict):
    print('POOL KEYS:', list(p)[:10])
    def walk(o, path=''):
        if isinstance(o, dict):
            if o.get('id') == 'TRIAL-LABOR-W19-JUDGE':
                print('FOUND at', path)
                print(json.dumps(o, ensure_ascii=False, indent=1))
                return True
            for k, v in o.items():
                if walk(v, path + '/' + str(k)):
                    return True
        elif isinstance(o, list):
            for i, v in enumerate(o):
                if walk(v, path + '[' + str(i) + ']'):
                    return True
        return False
    walk(p)
elif isinstance(p, list):
    for e in p:
        if isinstance(e, dict) and 'W19-JUDGE' in str(e.get('id', '')):
            print(json.dumps(e, ensure_ascii=False, indent=1))

# 2. prereg finalize section
t = open('research/TRIAL_LABOR_W19_PREREG.md', encoding='utf-8').read()
i = t.find('finalize')
print('\n=== PREREG finalize section ===')
print(t[max(0, i - 200):i + 2000])
