import json
d = json.load(open('results/aggr_capacity_face/p1_results.json', encoding='utf-8-sig'))
print('evidence_cutoff:', d['evidence_cutoff'], '| ledger_total_after:', d['ledger']['ledger_total_after'])
for name, v in sorted(d['variants'].items()):
    t = v['totals']
    print(f"{name:22s} {v['capacity_label']:13s} entries={t['num_entries']:4d} capped={t['capped_entries']:4d} dropped={t['dropped_zero_adv']:3d} miss={t['missing_adv_executions']:4d} rate={v['capped_rate']}")
    for c in v['constrained_detail'][:3]:
        print('     ', c['tid'], 'scale', round(c['scale_cny']), 'capped', c['capped_entries'], 'of', c['num_entries'], 'entries')
print()
print('audit:', json.dumps(d['audit'], ensure_ascii=False))
