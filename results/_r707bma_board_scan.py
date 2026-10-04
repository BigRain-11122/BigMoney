import json
import glob

open_t = []
claimed_by_other_active = []
for p in glob.glob(r'fleet\tasks\*.json'):
    try:
        with open(p, encoding='utf-8') as f:
            t = json.load(f)
    except Exception:
        try:
            with open(p, encoding='gbk') as f:
                t = json.load(f)
        except Exception as e:
            print('PARSE-FAIL:', p)
            continue
    st = t.get('status')
    if st == 'open':
        open_t.append((p, t.get('id'), t.get('immediate'), str(t.get('title'))[:60]))
for row in open_t:
    print('OPEN:', row)
print('open count:', len(open_t))
