import json, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

fails = []
def check(name, got, want, tol=1e-9):
    ok = (abs(got - want) <= tol) if isinstance(want, (int, float)) and isinstance(got, (int, float)) else (got == want)
    print('%s %s: got=%s want=%s' % ('PASS' if ok else 'FAIL', name, got, want))
    if not ok: fails.append(name)

waves = {}
for w in ['w2', 'w3', 'w4', 'w5']:
    j = json.load(open(r'results\trial_labor_%s\%s_judge.json' % (w, w), encoding='utf-8'))
    s = json.load(open(r'results\trial_labor_%s\%s_screen.json' % (w, w), encoding='utf-8'))
    waves[w] = {
        'n_distinct': s['n_distinct'],
        'survivors': s['n_survivors'],
        'judged': j['n_judged_cells'],
        'g1': sum(1 for c in j['cells'] if c.get('g1_pass')),
        'g2': j['n_eligible_g2'],
        'ledger_prev': j['trials_ledger']['prev_total'],
        'ledger_total': j['trials_ledger']['total'],
        'p95': s['null_family']['p95_line'],
        'batch_cells': s['batch_cells'],
    }

# per-wave table numbers
check('W2 candidates', waves['w2']['n_distinct'], 2924)
check('W2 survivors', waves['w2']['survivors'], 404)
check('W2 judged', waves['w2']['judged'], 404)
check('W2 g1', waves['w2']['g1'], 11)
check('W2 g2', waves['w2']['g2'], 0)
check('W2 ledger', waves['w2']['ledger_total'], 311214)
check('W2 ledger linear', waves['w2']['ledger_prev'] + waves['w2']['judged'], waves['w2']['ledger_total'])
check('W2 p95', round(waves['w2']['p95'], 4), 0.5116)
check('W2 survival %', round(100*404/2924, 1), 13.8)
check('W2 E[FP]', 0.05*404, 20.2)

check('W3 candidates', waves['w3']['n_distinct'], 3552)
check('W3 survivors', waves['w3']['survivors'], 513)
check('W3 judged', waves['w3']['judged'], 513)
check('W3 g1', waves['w3']['g1'], 2)
check('W3 g2', waves['w3']['g2'], 0)
check('W3 ledger', waves['w3']['ledger_total'], 311876)
check('W3 ledger linear', waves['w3']['ledger_prev'] + waves['w3']['judged'], waves['w3']['ledger_total'])
check('W3 survival %', round(100*513/3552, 1), 14.4)
check('W3 E[FP]', 0.05*513, 25.65)

check('W4 candidates', waves['w4']['n_distinct'], 3810)
check('W4 survivors', waves['w4']['survivors'], 461)
check('W4 judged', waves['w4']['judged'], 461)
check('W4 g1', waves['w4']['g1'], 0)
check('W4 g2', waves['w4']['g2'], 0)
check('W4 ledger', waves['w4']['ledger_total'], 317859)
check('W4 ledger linear', waves['w4']['ledger_prev'] + waves['w4']['judged'], waves['w4']['ledger_total'])
check('W4 survival %', round(100*461/3810, 1), 12.1)
check('W4 E[FP]', 0.05*461, 23.05)
check('W4 p95', round(waves['w4']['p95'], 4), 0.5164)

check('W5 candidates', waves['w5']['n_distinct'], 3926)
check('W5 survivors', waves['w5']['survivors'], 372)
check('W5 judged', waves['w5']['judged'], 372)
check('W5 g1', waves['w5']['g1'], 1)
check('W5 g2', waves['w5']['g2'], 0)
check('W5 ledger', waves['w5']['ledger_total'], 328987)
check('W5 ledger linear', waves['w5']['ledger_prev'] + waves['w5']['judged'], waves['w5']['ledger_total'])
check('W5 survival %', round(100*372/3926, 1), 9.5)
check('W5 E[FP]', 0.05*372, 18.6)
check('W5 p95', round(waves['w5']['p95'], 4), 0.5164)

# combined
cand = sum(waves[w]['n_distinct'] for w in waves)
surv = sum(waves[w]['survivors'] for w in waves)
g1 = sum(waves[w]['g1'] for w in waves)
check('W2-5 candidates', cand, 14212)
check('W2-5 survivors', surv, 1750)
check('W2-5 g1', g1, 14)
check('W2-5 survival %', round(100*surv/cand, 1), 12.3)
efp = sum(0.05*waves[w]['judged'] for w in waves)
check('W2-5 E[FP] sum', round(efp, 2), 87.5)

# six-wave totals (W1a 975/166, W1b 858/149 from WAVE1 report)
check('six-wave candidates', cand + 975 + 858, 16045)
check('six-wave judged', surv + 166 + 149, 2065)
check('six-wave survival %', round(100*(surv+315)/(cand+1833), 1), 12.9)
check('six-wave E[FP]', round(efp + 8.3 + 7.45, 2), 103.25)

# screen batch cells
check('W2 screen cells', waves['w2']['batch_cells'], 3124)
check('W3 screen cells', waves['w3']['batch_cells'], 3752)
check('W4 screen cells', waves['w4']['batch_cells'], 4010)
check('W5 screen cells', waves['w5']['batch_cells'], 4126)

# G1 passer module census
mods = {}
for w in ['w2', 'w3', 'w4', 'w5']:
    j = json.load(open(r'results\trial_labor_%s\%s_judge.json' % (w, w), encoding='utf-8'))
    for c in j['cells']:
        if c.get('g1_pass'):
            mods[c['fn']] = mods.get(c['fn'], 0) + 1
check('low_vol_long passers', mods.get('low_vol_long'), 7)
check('top_n_rotation passers', mods.get('top_n_rotation'), 5)
check('box_breakout passers', mods.get('box_breakout'), 2)
check('total passers', sum(mods.values()), 14)

# W5 yang/gate/vol segmented survivals quoted in report
s5 = json.load(open(r'results\trial_labor_w5\w5_screen.json', encoding='utf-8'))
check('W5 yang none surv%', round(100*s5['yang_segmented_survival']['none']['survival_rate'], 1), 12.2)
check('W5 yang first surv%', round(100*s5['yang_segmented_survival']['first_yang']['survival_rate'], 1), 6.6)
check('W5 gxv bear|wild|none', round(100*s5['gate_vol_yang_interaction_survival']['bear|wild|none']['survival_rate'], 1), 36.8)
check('W5 gxv bear|calm|fy', round(100*s5['gate_vol_yang_interaction_survival']['bear|calm|first_yang']['survival_rate'], 1), 0.9)
s4 = json.load(open(r'results\trial_labor_w4\w4_screen.json', encoding='utf-8'))
check('W4 vol wild surv%', round(100*s4['vol_segmented_survival']['wild']['survival_rate'], 1), 20.4)
check('W4 vol none surv%', round(100*s4['vol_segmented_survival']['none']['survival_rate'], 1), 10.7)
check('W4 vol calm surv%', round(100*s4['vol_segmented_survival']['calm']['survival_rate'], 1), 5.0)
check('W4 gatevol bear|wild', round(100*s4['gate_vol_interaction_survival']['bear|wild']['survival_rate'], 1), 35.9)
s3 = json.load(open(r'results\trial_labor_w3\w3_screen.json', encoding='utf-8'))
check('W3 gate bear surv%', round(100*s3['gate_segmented_survival']['bear']['survival_rate'], 1), 19.0)
check('W3 gate none surv%', round(100*s3['gate_segmented_survival']['none']['survival_rate'], 1), 13.4)
check('W3 gate bull surv%', round(100*s3['gate_segmented_survival']['bull']['survival_rate'], 1), 11.2)

# ledger chain order (six judge rows by value)
rows = [(311214, 'W2'), (311363, 'W1b'), (311876, 'W3'), (312042, 'W1a'), (317859, 'W4'), (328987, 'W5')]
check('ledger monotone', all(rows[i][0] < rows[i+1][0] for i in range(len(rows)-1)), True)

print()
if fails:
    print('RESULT: %d FAIL -> %s' % (len(fails), fails)); sys.exit(1)
print('RESULT: ALL CHECKS PASS')
