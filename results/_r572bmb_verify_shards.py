import json
for s in (8, 9):
    d = json.load(open('results/p2cal_ext/n1_w74/shard-%d-of-12.json' % s, encoding='utf-8'))
    a = d.get('audit', {})
    print('shard-%d: machine=%s elapsed=%s top_keys=%s' % (s, a.get('machine'), a.get('elapsed_sec'), sorted(d.keys())[:6]))
