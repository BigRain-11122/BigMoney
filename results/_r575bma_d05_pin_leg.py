# -*- coding: utf-8 -*-
"""D-20261002-05 pin leg: mid-hit skip-semantics positive/negative assertions
into perpetual_faces_n1.py selftest (inserted after the W84 leg, before the
T-141 lane face). Positive = past-hit-restart reading equals the registered
W68-B band; negative = window-step-chain reading must NOT equal it."""
import sys, os
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FP = os.path.join(REPO, 'scripts', 'perpetual_faces_n1.py')
b = open(FP, 'rb').read()
t = b.decode('utf-8')
eol = '\r\n' if t.count('\r\n') * 2 > t.count('\n') else '\n'
if 'D-20261002-05 mid-hit pin leg' in t:
    print('pin leg already landed (idempotent skip)')
    sys.exit(0)

LEG = '''
    # --- D-20261002-05 mid-hit pin leg (group ruling 10-02 12:00): the
    #     mid-band-hit family (arithmetic window hit at a NON-edge point,
    #     where the two readings -- past-hit restart vs window-step
    #     chain -- DIVERGE) is pinned to PAST-HIT RESTART. Positive:
    #     the past-hit reading reproduces the registered W68-B band
    #     (in-table primary face, zero disturbance); negative: the
    #     window-step-chain reading must NOT equal the registered band.
    mid_hit = 50_500                      # SEED_REGISTRY cta_p2_noau (W68-B history)
    arith_lo, arith_hi = 50_401, 50_600   # W67-B tail + 1 arithmetic window
    assert arith_lo <= mid_hit <= arith_hi, \\
        "pin fixture drift: the mid hit must fall inside the arithmetic window"
    past_hit = (mid_hit + 1, mid_hit + 1 + 199)        # positive reading
    win_step = (arith_hi + 1, arith_hi + 1 + 199)       # negative reading
    assert past_hit == (50_501, 50_700) == \\
        pf.N1_BANDS[68]["b_exit"], \\
        "D-20261002-05 pin (positive): past-hit restart must equal the " \\
        "registered W68-B band 50_501..50_700 (in-table primary face)"
    assert win_step != pf.N1_BANDS[68]["b_exit"], \\
        "D-20261002-05 pin (negative): the window-step-chain reading " \\
        "50_601..50_800 must NOT equal the registered band (divergent " \\
        "reading rejected per the 3:1 precedent density W26/W67/W68)"
'''
A3 = '\n    # --- T-141 s2 lane face'
oldX = A3.replace('\n', eol)
assert t.count(oldX) == 1, f'anchor not unique: {t.count(oldX)}'
t = t.replace(oldX, LEG.replace('\n', eol) + oldX)
open(FP, 'wb').write(t.encode('utf-8'))
print('pin leg landed (before T-141 lane face)')
