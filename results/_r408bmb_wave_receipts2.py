import json, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

def brief(o, depth=0, maxstr=200):
    if isinstance(o, dict):
        for k, v in o.items():
            if isinstance(v, (dict, list)):
                print('  '*depth + str(k) + ':')
                brief(v, depth+1, maxstr)
            else:
                s = str(v)
                print('  '*depth + '%s: %s' % (k, s[:maxstr]))
    elif isinstance(o, list):
        print('  '*depth + '[list n=%d]' % len(o))

for w in ['w2', 'w3', 'w4', 'w5']:
    p = r'results\trial_labor_%s\%s_judge.json' % (w, w)
    j = json.load(open(p, encoding='utf-8'))
    print('=====', w.upper(), 'descriptive_summary =====')
    brief(j.get('descriptive_summary', {}))
    s = json.load(open(r'results\trial_labor_%s\%s_screen.json' % (w, w), encoding='utf-8'))
    print('---', w.upper(), 'screen summary ---')
    brief(s if not isinstance(s, dict) else {k: v for k, v in s.items() if not isinstance(v, list)})
    print()
