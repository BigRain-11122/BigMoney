import json

b = open('logs/iteration-loop/state.json', 'rb').read()
d = json.loads(b.decode('utf-8'))
for k in ('did', 'verdict', 'next', 'last_round_ts', 'last_result', 'ts', 'updated_at', 'last_seen', 'updated', 'last_round_at'):
    print(k, '=', str(d.get(k))[:180])
