import json
c = json.load(open('Tools/fill_ladder_catalog.json', encoding='utf-8'))
cs = c['consumption_state']
print('--- consumption states ---')
for k, v in cs.items():
    state = v['state'] if isinstance(v, dict) else str(v)
    print(k, '=>', state)
print()
print('--- entries ---')
for e in c['entries']:
    gates = e.get('enqueue_gates')
    runner = str(e.get('runner'))[:46]
    note = str(e.get('note') or e.get('runner_note') or '')[:70]
    print(e.get('id'), '| gates=', gates, '| runner=', runner, '| note=', note)
