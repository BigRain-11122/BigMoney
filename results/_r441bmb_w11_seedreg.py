# W11 freeze-step SEED_REGISTRY three-key append (R250 one-step law, same
# commit as the frozen prereg). Retaken berth 20317000/20317500/20318000
# (draft 20316000/20316500 collided with bm-a r445 A12 PREDCOND keys).
p = 'scripts/science_gates.py'
src = open(p, encoding='utf-8').read()
anchor = '''        "t101_v4_a12_predcond_unc": 20316500,
        # T-101-V4-A12-PREDCOND dual-nulls (B=2000 block bootstrap +
        # P=2000 sign-flip, rng([20316500, cell_idx])) W1 semantics -- r445 bm-a
'''
add = anchor + '''        "trial_labor_w11_gen": 20317000,
        # W11 STD-gate (std20_hi/std10_hi high-dispersion confirm) wave:
        # 5,000-draw Sobol generation axis draws (rng([20317000+family_idx,
        # 7919]) integer-axis draw per W1-W10 lineage); draft berth
        # 20316000/20316500 collided with A12 keys -> +500 re-take per draft
        # clause-5 (W9 double-collision precedent) -- r441 bm-b; three-step law
        # verified at freeze (123 int bases zero-collision, first-els
        # 673516273/1869008098/1084768275 mutually distinct vs all bases,
        # null band 20317500..20317699 and unc band 20318000..20318200 clean,
        # rg hits = berth-declaration docs x2 + data volume-column numeric
        # coincidence x3 = t34/batch-69 precedent face; facts =
        # results/_r441bmb_w11_seed_law_facts.json)
        "trial_labor_w11_scrnull": 20317500,
        # s2 screen K=200 same-structure random-signal nulls
        # (rng([20317500, i]), i<200) per BACKTEST_PLAN three-iron-laws
        # (std gate leg merged into same-grid same-param-space draw)
        "trial_labor_w11_unc": 20318000,
        # W11 judge dual-nulls (B=2000 block bootstrap + P=2000 sign-flip)
        # (rng([20318000, cell_idx])) per RANDOM_LARGE_SAMPLE_LAW sec.3
'''
assert src.count(anchor) == 1, f'anchor count {src.count(anchor)}'
src = src.replace(anchor, add)
open(p, 'w', encoding='utf-8', newline='').write(src)
print('SEED_REGISTRY appended ok: trial_labor_w11_gen/scrnull/unc = 20317000/20317500/20318000')
