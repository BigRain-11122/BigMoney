# -*- coding: utf-8 -*-
# r1210 bm-c: W316 seat publication (machine-read from the ADMIT receipt, r587).
import io
import json
from datetime import datetime, timezone, timedelta

TZ = timezone(timedelta(hours=8))
now = datetime.now(TZ)
rec = json.load(io.open('results/_w316bmc_20261024_probe_receipt.json', encoding='utf-8'))
do = json.load(io.open('results/perpetual_faces/n1_w315_results.json', encoding='utf-8'))
A, B = rec['bands']['A'], rec['bands']['B']
leg1, leg2 = rec['legs']['leg1'], rec['legs']['leg2']
leg4 = rec['legs']['leg4']
ordn = rec['ordinals']
led = do['science_gates']['ledger']
pool = do['null_pool_cumulative']
chA = leg1['A_hop_chain'][0]
chB = leg1['B_hop_chain'][0]

body = f"""# MSG-{now:%Y%m%d-%H%M}-bmc-w316-seat - W316 seat ADMIT (bm-c)

- ts: {now.isoformat(timespec='minutes')}
- from: bm-c (compute-node)
- lane: PERPETUAL-N1 / own-wave rotation (W316 = bm-c own turn per chain order)
- tool: `python Tools/n1_seat_probe.py --wave 316 --a-hop-ordinal {ordn['a_hop']} --above-ordinal {ordn['above_own_a']}`
- receipt: `results/_w316bmc_20261024_probe_receipt.json`
- verdict: **{rec['verdict']}**

## Bands

| band | range | semantics |
|------|-------|-----------|
| A | {A[0]:,} .. {A[1]:,} (2,000) | {ordn['a_hop_word']} consecutive A-hop; base == prior-B tail {chA['refuser_bands'][0][1]:,} + 1 EXACT |
| B | {B[0]:,} .. {B[1]:,} (200)   | {ordn['above_own_a_word']} above-own-A (own-A reservation cascade); base == own-A tail {A[1]:,} + 1 EXACT |

- hops_A = {leg1['hops_A']}, hops_B = {leg1['hops_B']}; AB point-wise mutual exclusion asserted (leg2).
- leg3 bands_clear = {rec['legs']['leg3']['bands_clear']} on the {rec['legs']['leg3']['universe']} face.
- seed_admit_gate: FREE x2 (base {A[0]} span 2000 / base {B[0]} span 200).

## Universe / anchors (live-derived, r587)

- owner_rows {rec['legs']['leg0']['owner_rows']} (bm-a {rec['legs']['leg0']['bma_rows']} / bm-b {rec['legs']['leg0']['bmb_rows']} / bm-c {rec['legs']['leg0']['bmc_rows']}), ordinal {rec['legs']['leg0']['ordinal']}
- anchors: ledger_total {led['total']:,} / merged_n {pool['merged']['n_values']:,} (read from n1_w315_results.json, W315 finalize anchors)

## Refuser chains (machine-trace, not transcribed)

- A arithmetic continuation {chA['window'][0]:,}..{chA['window'][1]:,} refused at start by the registered
  prior-wave B band {chA['refuser_bands'][0][0]:,}..{chA['refuser_bands'][0][1]:,} (staircase-affects-A; sample point
  {chA['refuser_pts_sample'][0]:,}) -> jump to {chA['jump_to']:,} -> first clean {A[0]:,}..{A[1]:,}.
- B arithmetic continuation {chB['window'][0]:,}..{chB['window'][1]:,} lands inside this wave's own A window
  {A[0]:,}..{A[1]:,} -> own-A reservation cascade -> {B[0]:,}..{B[1]:,} (base == own-A tail + 1 EXACT).

## Projection for W317 (disclosed, not transcribed - freezer must live re-derive)

- A naive {leg4['W317p_A_naive']} - clean, hops {leg4['hops_A']}
- B naive {leg4['W317p_B_naive']} - clean, hops {leg4['hops_B']}, but lands inside projected W317 A window

## Note on ordering

Published in the r1210 window AFTER the W315 cycle close and BEFORE the W316 prereg freeze,
satisfying r565 early-visibility and O-20261010-2350 sec.2 seat-first law.
"""
p = 'fleet/inbox/MSG-%s-bmc-w316-seat.md' % (now.strftime('%Y%m%d-%H%M'))
io.open(p, 'w', encoding='utf-8', newline='\n').write(body)
print('WROTE', p, len(body))