# -*- coding: utf-8 -*-
# R264 (bm-a): T-73 progress_r264 append -- byte-face mirror per R255/R257 law
# probed: no BOM, LF-only, indent=1, no trailing newline, ensure_ascii=False
import json

P = 'fleet/tasks/T-2026-09-26-73-P1.json'
raw = open(P, 'rb').read()
assert raw[:3] != b'\xef\xbb\xbf', 'unexpected BOM'
d = json.loads(raw.decode('utf-8'))
assert 'progress_r264' not in d

d['progress_r264'] = (
    'R264 bm-a: s3 VERDICT CONSOLIDATION LEDGER delivered (O-0926 closing face): '
    'research/CN_COMBO_VERDICTS.md v1.0 + machine-readable matrix '
    'results/_r264bma_cn_verdict_matrix.json (extractor results/_r264bma_cn_verdict_extract.py --write). '
    'Five families x 19 judged cells ALL NEGATIVE (pass_v2 0/19, dsr_ok 0/19): best-vs-line reads '
    'REV60_bare 0.4757/0.6147, W252_bare 0.7371/0.9527 (closest at 77% but buy_hold_512890 alone 0.7039 '
    '=> rotation skill increment +0.033 marginal), v3_base 0.2998/0.5691, SAT40_bare 0.4586/0.5664, '
    'SAT40_DD20 0.4477/0.7686; only 3 cells CI95-lower positive (REV60_bare/REV60_tilt/W252_bare); '
    'PBO gate FAIL on 3 families (POLICY 0.6857 / SAT 0.5571 / DDCTL 0.6143 > 0.25). Root cause: '
    'random-rebalance null line 0.5691-0.9527 dominates -- returns are beta-exposure not rotation alpha, '
    'mutually corroborating T-28 NOT-DEMONSTRATED (J4 0.4854<0.70). Disposition: zero registry entries, '
    'no-reopen per O-1105 negative-line law (new evidence = new prereg); GM-ruling per O-1620: no '
    'forward paper accounts for negative families (paper = forward-evidence generator, AGGR precedent '
    'inapplicable -- different three-lane KPI). Allocation-lane reference reads (x1 face, NOT the frozen '
    'gate, honest disclosure per O-1145 three-lane law): W252_bare ann 10.70% dd -19.60% Calmar 0.546 '
    'pos-year 0.750 BUT oos sharpe 0.2021 with 2026 YTD -1.25% (near-window dividend-lowvol failure). '
    's1/s2/s3 science faces now FULLY CLOSED; remaining legs = CEO briefing (ledger is the carrier) + '
    '10-01 monthly verdict-bench例行引用.'
)

out = json.dumps(d, ensure_ascii=False, indent=1).encode('utf-8')
assert not out.endswith(b'\n')
with open(P, 'wb') as fh:
    fh.write(out)
print('progress_r264 appended, bytes:', len(out))
