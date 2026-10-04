# r684 bm-b: verify refreshed contest table (LA rows ranked + determinism)
import io, json, hashlib

FP = r'results/contest_p1/contest_table.json'
d = json.load(io.open(FP, encoding='utf-8'))
la = [r for r in d['table'] if r['source'] == 'LOWAMP_DEEP_EXPLORATION']
for r in la:
    print('LA row:', r['contest_id'], '| rank', r['rank'], '| composite',
          r['composite'], '| ytd', r['ytd_ret'], '| dd', r['max_dd'],
          '| sharpe', r['sharpe_ytd'], '| beat300', r['beat_510300_pp'],
          '| win', r['window']['end'], r['window']['n_days'])
print('census:', json.dumps(d['census']))
print('pending:', len(d['pending_legs']), [p['contest_id'] for p in d['pending_legs']][:3], '...')
b1 = hashlib.sha256(io.open(FP, 'rb').read()).hexdigest()[:16]
print('table sha16 v1:', b1)
