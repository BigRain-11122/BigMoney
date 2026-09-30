import json
rp = json.load(open('results/runnable_pool.json'))
ents = rp.get('entries', [])
for e in ents:
    st = e.get('status')
    if st in ('ready', 'waiting'):
        print('ENTRY', e.get('id', e.get('name')), '| status:', st, '| owner:', e.get('owner'), '| owner_since:', e.get('owner_since'), '| workers:', e.get('workers_plan'), '| desc:', str(e.get('desc', e.get('note', '')))[:100])
        for s in e.get('shards', []):
            if s.get('status') in ('ready', 'waiting', 'claimed'):
                print('   shard', s.get('id', s.get('name')), '| status:', s.get('status'), '| owner:', s.get('owner'), '| since:', s.get('owner_since'))
# autofill cooldown state
af = json.load(open('results/autofill_state.bm-b.json'))
print('\nautofill last_tick:', af['last_tick'])
for k in af:
    if k not in ('launches', 'last_tick', 'lane_machine', 'core_samples_seen'):
        print('autofill key:', k, '->', str(af[k])[:200])
print('\nlast 5 launches:')
for l in af['launches'][-5:]:
    print('  ', l.get('ts'), l.get('verdict'), l.get('entry'), l.get('shard'), '| py_cpu:', l.get('py_cpu_pct'), '| pid:', l.get('pid'), '| target_met:', l.get('target_met'), '| crash:', l.get('crash_counted'), '| auto_parked:', l.get('auto_parked'))
