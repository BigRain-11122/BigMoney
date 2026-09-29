p = 'scripts/science_gates.py'
src = open(p, encoding='utf-8').read()
anchor = '        "trial_labor_w8_unc": 20307500,'
add = anchor + '''
        # T-101-V4-A2-PRESCREEN (r433 bm-a; take-number law: 101-key
        # inventory zero-conflict checked 2026-09-29 15:0x before freeze):
        "t101_v4_a2_scrnull": 20308000,  # same-mask circular-shift nulls K=200/cell'''
assert src.count(anchor) == 1, f'anchor count {src.count(anchor)}'
src = src.replace(anchor, add)
open(p, 'w', encoding='utf-8', newline='').write(src)
print('SEED_REGISTRY appended ok')
