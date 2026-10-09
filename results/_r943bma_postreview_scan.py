import json, glob
for f in glob.glob('results/post_review*.json'):
    try:
        d = json.load(open(f, encoding='utf-8'))
    except Exception:
        print(f, 'ERR')
        continue
    s = json.dumps(d, ensure_ascii=False)
    bad = s.count('\u2717')
    print(f, '| fail-marks:', bad, '| size:', len(s))
    if bad:
        # show the failing rows
        def walk(o, path=''):
            if isinstance(o, dict):
                for k, v in o.items():
                    walk(v, path + '/' + str(k))
            elif isinstance(o, list):
                for i, v in enumerate(o):
                    walk(v, path + '[' + str(i) + ']')
            elif isinstance(o, str) and '\u2717' in o:
                print('   FAIL ROW at', path, ':', o[:160])
        walk(d)
