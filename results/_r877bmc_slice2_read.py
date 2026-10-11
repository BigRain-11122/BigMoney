import json
d = json.load(open(r'results\regime_style_matrix\P0-SLICE2-DIPREBOUND-THEME-20261011.json', encoding='utf-8'))
print('== dip_rebound x1 by regime (12m median / pos_share / n_days) ==')
f = d['dip_rebound']['faces']['x1']
for c, st in f['by_regime'].items():
    r12 = st.get('roll12'); tv = st.get('three_verdicts')
    med = r12['median'] if r12 else None
    pos = r12['pos_share'] if r12 else None
    go = tv['gate_off_advice'] if tv else None
    fb = tv['floor_beat_median'] if tv else None
    print(c, 'n=%d' % st['n_days'], 'med12=%s' % med, 'pos=%s' % pos,
          'gate_off=%s' % go, 'floor_beat=%s' % fb)
print('unlabeled:', f['unlabeled_days'], 'labeled:', f['labeled_days'],
      'panic_in:', f['panic_days_in'])
print('x2 unlabeled:', d['dip_rebound']['faces']['x2']['unlabeled_days'])
print()
print('== theme TJ-FULL x1 by regime (n / median_sys / beat_bh) ==')
t = d['theme_wave']['batches']['TJ']['strata']['TJ-FULL']['x1']
print('n_total', t['n_episodes'], 'unlabeled', t['unlabeled_episodes'],
      'panic', t['panic_ignitions'])
for c, st in t['by_regime'].items():
    print(c, 'n=%s' % st.get('n_episodes'), 'med=%s' % st.get('median_sys_net'),
          'beat_bh=%s' % st.get('beat_bh_share'),
          'exc_med=%s' % st.get('median_excess_vs_bh'),
          'pos=%s' % st.get('pos_share'))
print()
print('== theme TJ2-FULL x1 by regime ==')
t2 = d['theme_wave']['batches']['TJ2']['strata']['TJ2-FULL']['x1']
for c, st in t2['by_regime'].items():
    print(c, 'n=%s' % st.get('n_episodes'), 'med=%s' % st.get('median_sys_net'),
          'beat_bh=%s' % st.get('beat_bh_share'))
print()
print('== theme TJ-SOLO x1 BULL/CHOP/BEAR ==')
ts = d['theme_wave']['batches']['TJ']['strata']['TJ-SOLO']['x1']
for c in ('BULL', 'CHOP', 'BEAR'):
    st = ts['by_regime'][c]
    print(c, 'n=%s' % st.get('n_episodes'), 'med=%s' % st.get('median_sys_net'),
          'beat_bh=%s' % st.get('beat_bh_share'), 'pos=%s' % st.get('pos_share'))
