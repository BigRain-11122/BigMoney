# -*- coding: utf-8 -*-
"""r783 bm-a W160 freeze FOPT fragment heal (r776 fragment-needle law;
sister of _r783bma_w160_fzt_heal.py). The @FOPT@ composite
'W158 finalize one-pass bm-a r779' was fragment-broken in the source
W159 entry ('...ALL LANDED (W158 "' ends one python string fragment,
'finalize one-pass bm-a r779, net chain head 753,012, "' starts the
next) so the contiguous TOK needle silently missed and the bare
@RW@ (r779->r783) produced the wrong session in the new W160 entry
tail. Machine-verified fact: W159 finalize one-pass = bm-a r782
(fc92cbf53 'r782 bm-a ... W159 finalize one-pass ... ledger 753,012 ->
755,212 +2,200, K=347,720'); ledger head after = 755,212."""
import ast
import io

N1 = r"scripts/perpetual_faces_n1.py"
src = io.open(N1, encoding="utf-8", newline="").read()

k = src.find('160: {"batch"')
assert k > 0, "W160 entry not found"
m_end = src.find('"engine_owner": "bm-a"},', k) + len('"engine_owner": "bm-a"},')
seg = src[k:m_end]

OLD = '"finalize one-pass bm-a r783, net chain head 755,212, "'
NEW = '"finalize one-pass bm-a r782, net chain head 755,212, "'
assert seg.count(OLD) == 1, ("frag", seg.count(OLD))
assert src.count(OLD) == 1, "frag must be unique to the W160 entry"
# the historical W159 entry keeps its own frozen (r779-drift) face
i159 = src.find('159: {"batch"')
seg159 = src[i159:src.find('"engine_owner": "bm-a"},', i159)]
assert "finalize one-pass bm-a r779, net chain head 753,012" in seg159, \
    "W159 entry frozen tail face must stay untouched"

healed = seg.replace(OLD, NEW)
assert "finalize one-pass bm-a r783" not in healed
out = src[:k] + healed + src[m_end:]
io.open(N1, "w", encoding="utf-8", newline="").write(out)
ast.parse(io.open(N1, encoding="utf-8", newline="").read())
print("FOPT fragment heal landed: W160 entry tail cites 'finalize "
      "one-pass bm-a r782, net chain head 755,212' (AST gate PASS)")
