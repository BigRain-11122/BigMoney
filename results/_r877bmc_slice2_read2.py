import json
d = json.load(open(r'results\regime_style_matrix\P0-SLICE2-DIPREBOUND-THEME-20261011.json', encoding='utf-8'))
f2 = d['dip_rebound']['faces']['x2']
for c in ('CHOP', 'BEAR'):
    st = f2['by_regime'][c]
    r12 = st.get('roll12'); tv = st.get('three_verdicts')
    print('x2', c, 'med12=%s' % (r12['median'] if r12 else None),
          'pos=%s' % (r12['pos_share'] if r12 else None),
          'gate_off=%s' % (tv['gate_off_advice'] if tv else None),
          'floor_beat=%s' % (tv['floor_beat_median'] if tv else None))
t2s = d['theme_wave']['batches']['TJ2']['strata']['TJ2-SOLO']['x1']
for c in ('BULL', 'CHOP'):
    st = t2s['by_regime'][c]
    print('TJ2-SOLO x1', c, 'n=%s' % st.get('n_episodes'),
          'med=%s' % st.get('median_sys_net'),
          'beat_bh=%s' % st.get('beat_bh_share'))
