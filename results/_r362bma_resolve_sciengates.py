"""R362 bm-a rebase stop 1: science_gates.py UU resolve.
Same-window blind double seed registration (4th instance of r239-family race):
origin (bm-b r347, 23:06) registered trial_labor_w1_gen/scrnull/unc =
20283500/20284000/20284500; local (bm-a R362, 22:57) registered mass_trial_w1
= 20283000 with a declared 900-slot band 20283000..20283899 that blindly
covered bm-b's 20283500. Resolution = UNION both families verbatim (both are
real: bm-b's = frozen-prereg-not-yet-run design; mine = ALREADY BURNED draws
for the 975-cell screen), amend my comment to disclose the overlap + the
actual used range (families 20283000..20283074 + nulls 20283100..20283119),
derivation protocols disjoint (Sobol scalar seed vs multi-int seed-sequence).
"""
import io

P = 'scripts/science_gates.py'
src = io.open(P, 'r', encoding='utf-8', newline='').read()

i = src.find('<<<<<<<')
m = src.find('=======', i)
j = src.find('>>>>>>>', m)
assert i >= 0 and m > i and j > m, 'conflict markers not found'

head_side = src[i + len('<<<<<<< HEAD\n'):m]
mine_side = src[m + len('=======\n'):j]

# union: origin's three entries (verbatim) + my entry with amended comment
my_entry = ('    "mass_trial_w1": 20283000,  # T-2026-09-27-94 mass candidate '
            'trial wave-1\n'
            '    # (CEO O-2026-09-27-2245). ALREADY-BURNED face (975-cell '
            'stage-1 screen,\n'
            '    # side-branch yielded to bm-b TRIAL_LABOR_W1 lane per sec.4 '
            'commit-time\n'
            '    # 22:49 < 22:57; trials stay counted). Same-window blind '
            'double-reg\n'
            '    # disclosure: originally declared band 20283000..20283899 '
            'covered\n'
            '    # bm-b r347 trial_labor_w1_gen 20283500 (invisible locally at '
            'reg\n'
            '    # time); actual used = Sobol seeds 20283000..20283074 (75 '
            'families)\n'
            '    # + null rngs 20283100..20283119 -- disjoint from bm-b '
            'seeds by\n'
            '    # both range and derivation protocol (scalar Sobol seed vs '
            'multi-int\n'
            '    # seed-sequence), zero stream collision; kept for '
            'reproducibility of\n'
            '    # the counted cells\n')

resolved = head_side + my_entry
out = src[:i] + resolved + src[j + len('>>>>>>> 900e90eb (T-94 claim (bm-a R362, CEO immediate-law claim-and-start) + mass_trial_w1 seed base 20283000 registered (band collision-free, R99 one-step: seed at freeze commit before any run)\n'):]
io.open(P, 'w', encoding='utf-8', newline='').write(out)

import ast
ast.parse(out)
print('science_gates.py resolved: union both seed families, ast.parse OK')
