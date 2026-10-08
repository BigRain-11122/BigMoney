import json

d = json.load(open('results/regime5_validation/REGIME5-VALIDATION-2026-09-30.json', encoding='utf-8'))
r = d['result']
mt = r['leg_a_main_window']['states']


def bp(v):
    return 'NA' if v is None else '%+.2f' % (v * 1e4)


print('=== Leg A main window (2020-01-02 -> cutoff), %d days:' % r['leg_a_main_window']['n_days'])
for s in ('BULL', 'BEAR', 'GRIND', 'CHOP', 'SUPPORT'):
    row = mt[s]
    p = r['leg_a_perm_null'][s]
    ci = r['leg_a_block_bootstrap'][s]
    print('%-8s n=%5d d=%s bp t=%7s p=%s CI=[%s,%s]bp' % (
        s, row['n'], bp(row['d']),
        'NA' if row['t'] is None else '%7.2f' % row['t'],
        'NA' if p is None else '%.4f' % p['p_two_sided'],
        bp(ci['ci_lo']) if ci else 'NA', bp(ci['ci_hi']) if ci else 'NA'))
print('main gate BULL:', {k: v for k, v in r['main_gate']['BULL'].items() if 'ok' in k or 'pass' in k})
print('main gate BEAR:', {k: v for k, v in r['main_gate']['BEAR'].items() if 'ok' in k or 'pass' in k})
print('label_face_holds:', r['label_face_holds'])
print('=== Leg B (full history):')
for n, row in sorted(r['leg_b_n_conf_table'].items(), key=lambda kv: int(kv[0])):
    print('N=%s: F=%3d W=%4d C=%s bp O=%s bp L=%s bp net=%s bp' % (
        n, row['flips_F'], row['wrong_days_W'],
        '%.2f' % (row['transition_cost_C'] * 1e4),
        '%.2f' % (row['opportunity_cost_O'] * 1e4),
        '%.2f' % (row['L'] * 1e4), '%+.2f' % (row['net'] * 1e4)))
print('N*:', r['n_conf_star'], '| default3_kept:', r['default3_kept'], '| leg_c_net_pass:', r['leg_c_net_pass'])
print('=== full-history d (Leg B consumption table):')
for s in ('BULL', 'BEAR', 'GRIND', 'CHOP', 'SUPPORT'):
    row = r['leg_a_full_history']['states'][s]
    print('%-8s n=%5d d=%s bp' % (s, row['n'], bp(row['d'])))
print('m1 BULL:', r['m1_t_gate']['BULL'])
print('m1 BEAR:', r['m1_t_gate']['BEAR'])
print('skill_line:', json.dumps(r['skill_line_v2_reading'], ensure_ascii=False)[:200])
print('ledger:', json.dumps(d['trials_ledger']))
print('extremes windows:', [(w['window'], len(w['days'])) for w in r['extreme_day_disclosure']])
