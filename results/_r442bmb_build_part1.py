"""r442 bm-b: W11 runner builder stage-1 (corrected counts).
Bulk renames with self-computed counts; unique-anchors asserted where
surgical. Writes results/_r442bmb_stage1.py.
"""
SRC = open('scripts/trial_labor_w10.py', encoding='utf-8').read()
fails = []
replaced = {}


def rep(old, new, tag, must=True):
    global SRC
    n = SRC.count(old)
    if n == 0 and must:
        fails.append(f'[{tag}] NOT FOUND: {old[:70]!r}')
        return
    replaced[tag] = n
    SRC = SRC.replace(old, new)


# ---- bulk wave renames (self-counted) ----
rep('TRIAL_LABOR_W10', 'TRIAL_LABOR_W11', 'wave')
rep('TRIAL_LAB_W10', 'TRIAL_LAB_W11', 'batch')
rep('research/TRIAL_LABOR_W10_PREREG.md', 'research/TRIAL_LABOR_W11_PREREG.md',
    'prereg-path')
rep('trial_labor_w10', 'trial_labor_w11', 'module-bulk')  # seeds keys + RES_DIR
rep('w10-mom-gate-extended', 'w11-std-gate-extended', 'gkind')
# result file names (after module-bulk; these are w10_ prefixed)
for p in ('w10_grammar.json', 'w10_candidates.json', 'w10_screen.json',
          'w10_screen_cells.csv', 'w10_judge.json', 'w10_intake.json'):
    rep(p, p.replace('w10_', 'w11_'), 'path:' + p)
# ---- tuple cardinality ----
rep('thirteen-tuple', 'fourteen-tuple', 't13')
rep('Thirteen-tuple', 'Fourteen-tuple', 'T13')
rep('THIRTEEN-tuple', 'FOURTEEN-tuple', 'TT13')
rep('THIRTEEN-gate', 'FOURTEEN-gate', 'TG13')
rep('thirteen axes', 'fourteen axes', 'a13')
rep('thirteen-tuple axis stream', 'fourteen-tuple axis stream', 'streamT')
rep('thirteen =', 'fourteen =', 'v13')
rep('range(13)', 'range(14)', 'r13')
rep('== 13 and', '== 14 and', 'eq13')
rep('twelve, thirteen', 'thirteen, fourteen', 'tw13')
rep('the first twelve axis arrays are the W9-order stream',
    'the first thirteen axis arrays are the W10-order stream', 'stream12')
rep('13-tuple', '14-tuple', 'tup13')
rep('14-tuple return shape', '15-tuple return shape', 'ret14')
rep('twelve axis arrays', 'thirteen axis arrays', 'stream12b')
rep('W10 seeds/counts', 'W11 seeds/counts', 'w10seeds')

# ---- seed comment values (header comments) ----
rep('# 20311000', '# 20317000', 'seedv1')
rep('# 20311500', '# 20317500', 'seedv2')
rep('# 20312000', '# 20318000', 'seedv3')
# grammar seeds derivation text
rep('Sobol(seed=20311000+family_idx, ', 'Sobol(seed=20317000+family_idx, ',
    'seedder1')
rep('default_rng([20311000+family_idx, 7919])',
    'default_rng([20317000+family_idx, 7919])', 'seedder2')
# null-derivation comment
rep('(W10 berth 20311500, distinct from the W9 berth 20310000 -- zero\n'
    'stream overlap by construction)',
    '(W11 berth 20317500, distinct from the W10 berth 20311500 -- zero\n'
    'stream overlap by construction)', 'seednull')

# ---- wave label W10 -> W11 where it means the current wave ----
# careful sites (leave PRIOR_WAVE_SHA16 alone; handled surgically later)
rep('the W10 runner re-derives ZERO amp machinery',
    'the W11 runner re-derives ZERO mom machinery', 'impface-a')
rep('# amp overlay (tl9 import face)', '# mom overlay (tl10 import face)',
    'impface-b')
rep('The FULL amp machinery is imported verbatim from tl9 (W9 frozen\n'
    '# face; import-face law; zero re-implementation) -- the W11 runner only\n'
    '# adds the NEW mom overlay layer on top of it.',
    'The FULL mom machinery is imported verbatim from tl10 (W10 frozen\n'
    '# face; import-face law; zero re-implementation) -- the W11 runner only\n'
    '# adds the NEW std overlay layer on top of it.', 'impface-c', must=False)

print('replaced counts:', {k: v for k, v in replaced.items()})
print('fails:', len(fails))
for f in fails:
    print(' FAIL', f)
open('results/_r442bmb_stage1.py', 'w', encoding='utf-8').write(SRC)
print('stage1 written, lines:', SRC.count(chr(10)) + 1)
