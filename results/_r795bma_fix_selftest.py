# -*- coding: utf-8 -*-
"""r795 bm-a surgical fix 2 (final): n1 selftest W165-leg step-up misses.
Dual-era count evidence (cur vs f7d34e5a7): every affected functional
index appears in the W164-era leg as its CORRECT W164 form (w<164 /
range(17,164) / range(16,164) / below-164 / [164] keys), and the r794
generator advanced the leg's VALUES+prose to W165 but left these indexes
unstepped -- so the W165 leg now under-scans by one wave (misses W164 in
collision/dep/set faces) and asserts the wrong WAVE_CONFIGS key.
Fix = step each to its W165 form (W164 precedent arithmetic +1)."""
import ast
import io

N1 = "scripts/perpetual_faces_n1.py"
EDITS = [
    ('assert WAVE_CONFIGS[164]["a_seed_base"] == 377_804 == 377_803 + 1, (',
     'assert WAVE_CONFIGS[165]["a_seed_base"] == 377_804 == 377_803 + 1, (', 1),
    ('assert WAVE_CONFIGS[164]["b_exit_seed_base"] == 379_804 == 379_803 + 1, (',
     'assert WAVE_CONFIGS[165]["b_exit_seed_base"] == 379_804 == 379_803 + 1, (', 1),
    ('for wprev in sorted(w for w in WAVE_CONFIGS if w < 164):',
     'for wprev in sorted(w for w in WAVE_CONFIGS if w < 165):', 2),
    ('for _depw in range(17, 164):',
     'for _depw in range(17, 165):', 1),
    ('assert sorted(w for w in WAVE_CONFIGS if w < 164) == ',
     'assert sorted(w for w in WAVE_CONFIGS if w < 165) == ', 1),
    ('[w for w in range(16, 164)]',
     '[w for w in range(16, 165)]', 1),
    ('# registered wave below 164 composes; wave 15 excluded by',
     '# registered wave below 165 composes; wave 15 excluded by', 1),
]
src = io.open(N1, encoding="utf-8", newline="").read()
for i, (old, new, cnt) in enumerate(EDITS):
    n = src.count(old)
    assert n == cnt, f"edit {i}: count {n} != {cnt}: {old[:60]!r}"
    src = src.replace(old, new)
io.open(N1, "w", encoding="utf-8", newline="").write(src)
ast.parse(src)
print(f"all {len(EDITS)} step-up fixes landed (wprev x2); AST PASS; bytes", len(src))
