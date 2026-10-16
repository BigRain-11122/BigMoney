# -*- coding: utf-8 -*-
# r1062 bm-c: one-shot fixer for the sect() anchor-duplication bug in the builder.
import io
p = "results/_r1062bmc_build_editor.py"
t = io.open(p, encoding="utf-8", newline="").read()
fixes = [
 ('sect(t.split("\\n", 1)[0], "import io, os, subprocess, sys", NEW_HEADER + "import io, os, subprocess, sys", "hdr")',
  'sect(t.split("\\n", 1)[0], "import io, os, subprocess, sys", NEW_HEADER, "hdr")'),
 ('NEW_ERAS + "def rep(old, new, expect=None, tag=", "eras")',
  'NEW_ERAS, "eras")'),
 ('NEW_P1_P4X + "# ============ P5a: numeric/anchor", "P1-P4x")',
  'NEW_P1_P4X, "P1-P4x")'),
 ('NEW_P5A + "# ============ P5b: extraction count faces", "P5a")',
  'NEW_P5A, "P5a")'),
 ('NEW_P5B + "_PARFULL_W255 = ", "P5b-direct")',
  'NEW_P5B, "P5b-direct")'),
 ("NEW_P5B_LATE + '# receipt note (single big face: counts + generation stamp)', \"P5b-late\")",
  'NEW_P5B_LATE, "P5b-late")'),
 ('NEW_P5C + "# ============ P5d: ordinal/leg0", "P5c")',
  'NEW_P5C, "P5c")'),
 ('NEW_P5D + "# ============ P5e: A/B face structural", "P5d")',
  'NEW_P5D, "P5d")'),
 ('NEW_P5F + "# ============ structural output gates", "P5f")',
  'NEW_P5F, "P5f")'),
 ('NEW_GATES + \'io.open(DST, "w", encoding="utf-8", newline="").write(t)\', "gates")',
  'NEW_GATES, "gates")'),
]
for old, new in fixes:
    n = t.count(old)
    assert n == 1, "count %d for: %r" % (n, old[:70])
    t = t.replace(old, new)
io.open(p, "w", encoding="utf-8", newline="").write(t)
print("10 sect fixes applied")
