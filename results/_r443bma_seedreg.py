p = 'scripts/science_gates.py'
src = open(p, encoding='utf-8').read()
anchor = '''        "t101_v4_a10_combo_unc": 20314500,
        # T-101-V4-A10-REGIMECOMBO dual-nulls (B=2000 block bootstrap +
        # P=2000 sign-flip, rng([20314500, cell_idx])) W1 semantics -- r442 bm-a
'''
add = anchor + '''        "t101_v4_a11_xsel_scrnull": 20315000,
        # T-101-V4-A11-XSELECT random-topk-selection nulls K=200/cell
        # (rng([20315000, cell_idx]) per cell) -- r443 bm-a; three-step law
        # verified pre-freeze (119 int bases zero-collision, band 20315xxx
        # rg-empty, first-el distinctness check, rg hits = Money0923 volume
        # column numeric coincidence = t34/batch-69 precedent face)
        "t101_v4_a11_xsel_unc": 20315500,
        # T-101-V4-A11-XSELECT dual-nulls (B=2000 block bootstrap +
        # P=2000 sign-flip, rng([20315500, cell_idx])) W1 semantics -- r443 bm-a
'''
assert src.count(anchor) == 1, f'anchor count {src.count(anchor)}'
src = src.replace(anchor, add)
open(p, 'w', encoding='utf-8', newline='').write(src)
print('SEED_REGISTRY appended ok: 20315000/20315500')
