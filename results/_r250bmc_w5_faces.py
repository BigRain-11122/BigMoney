import json

d = json.load(open('results/innovation_quota/ICU-MA-TIMING-P1.json', encoding='utf-8'))
out = []
for name in ('ICU-N5', 'ICU-N120', 'ICU-N15'):
    g = d['gates'][name]['g1_prime_v2']
    sk = g['skill_line']
    out.append('%s: sharpe=%s line=%s passive_term=%s null_term=%s mu_null=%s sigma_null=%s n_eff=%s line_ok=%s ci=%s' % (
        name, g['sharpe_full'], sk['line'], sk['passive_term'], sk['null_term'], sk['mu_null'],
        sk['sigma_null'], sk['n_eff'], g['line_ok'], json.dumps(g['bootstrap_ci'])))
    out.append('  dsr=%s g2=%s' % (g.get('dsr'), g.get('g2_eligible', g.get('g2_face', '?'))))
out.append('passive: ' + json.dumps(d['passive'], ensure_ascii=False))
out.append('episode_kpi: ' + json.dumps(d['episode_kpi'], ensure_ascii=False)[:900])
out.append('virtual_starts: ' + json.dumps(d['virtual_starts'], ensure_ascii=False)[:900])
out.append('nulls: ' + json.dumps(d['nulls'], ensure_ascii=False)[:800])
out.append('maintain_face: ' + json.dumps(d['maintain_face'], ensure_ascii=False)[:600])
out.append('extreme_day_face: ' + json.dumps(d['extreme_day_face'], ensure_ascii=False)[:600])
out.append('d6: ' + json.dumps(d['d6'], ensure_ascii=False)[:600])
out.append('funnel: ' + json.dumps(d['funnel'], ensure_ascii=False)[:400])
out.append('trials_ledger: ' + json.dumps(d['trials_ledger'], ensure_ascii=False)[:400])
out.append('judgment_note: ' + json.dumps(d['judgment_note'], ensure_ascii=False)[:500])
out.append('splits: ' + json.dumps(d['splits'], ensure_ascii=False)[:400])
out.append('maintain_full: ' + json.dumps(d.get('maintain_face'), ensure_ascii=False))
open('results/_r250bmc_w5_faces.txt', 'w', encoding='utf-8').write('\n'.join(out))
print('written', len(out), 'lines')
