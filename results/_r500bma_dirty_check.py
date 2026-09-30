import json, subprocess
out = subprocess.check_output(['git', 'status', '--porcelain'], text=True).splitlines()
bad = []
for line in out:
    p = line[3:].strip().strip('"')
    if p.endswith('.json') or p.endswith('.jsonl'):
        try:
            if p.endswith('.jsonl'):
                for l in open(p, encoding='utf-8'):
                    if l.strip():
                        json.loads(l)
            else:
                json.load(open(p, encoding='utf-8'))
        except Exception as e:
            bad.append((p, str(e)[:80]))
print('PARSE-FAIL:', bad if bad else 'none')
print('total dirty:', len(out))
for line in out:
    print(line)
