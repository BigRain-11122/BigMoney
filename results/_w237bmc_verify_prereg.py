# -*- coding: utf-8 -*-
import io, json
s = io.open('research/PERPETUAL_N1_W237_PREREG.md', encoding='utf-8').read()
BN = 'batch_name="PERPETUAL-N1-W237"'
checks = ['PERPETUAL-N1-W237', 'A-ext seed=536_204..538_203', 'B-ext exit seed=538_204..538_403',
          BN, 'n1_w237_results.json', '942,989', 'K=517,120',
          '519,320', 'NINETY-SEVENTH', 'MSG-20261014-0654-bmc-w237-seat',
          'W236 \u6ce8\u518c B \u5e26 536_004..536_203']
for c in checks:
    print(('PASS' if c in s else 'FAIL'), c, s.count(c))
r = json.load(open('results/_w237bmc_prereg_derive_receipt.json', encoding='utf-8'))
print('receipt: sub_pairs=%d out_bytes=%d merged_K=%d ledger=%d bands_A=%s'
      % (r['sub_pairs_applied'], r['out_bytes'], r['facts']['merged_K'],
         r['facts']['ledger_total'], r['facts']['bands']['A']))
