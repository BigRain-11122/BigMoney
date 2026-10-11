# -*- coding: utf-8 -*-
import json
for w in range(210, 217):
    d = json.load(open(f'results/perpetual_faces/n1_w{w}_results.json'))
    led = d['science_gates']['ledger']
    m = d['null_pool_cumulative']['merged']
    print(f"W{w}: total={led['total']:,} K={m['n_values']:,} mu={m['mu']:.5f}")
