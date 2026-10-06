# -*- coding: utf-8 -*-
"""r783 bm-a W160 freeze FZT fragment heal (r776 fragment-needle law
enforcement; the @FZT@ composite 'bm-a r773 freeze aed41df3e' was
fragment-broken in the source W159 entry -- 'bm-a r773 freeze ' ends one
python string fragment, 'aed41df3e,' starts the next -- so the contiguous
TOK needle silently missed and the bare @PRW@ produced 'bm-a r779 freeze'
+ 'aed41df3e' in the new W160 entry. Same latent defect class as the
r781 @FZ@ zero-match that produced the W159 entry's own drift face).

Heal = surgical fragment-level replace in the NEW W160 entry only
(the historical W159 entry keeps its frozen face, git history intact):
  fragment 1: 'REGISTERED W159 row bm-a r779 freeze '  ->  '... bm-a r781 freeze '
  fragment 2: 'aed41df3e, SINGLE STATE zero seat gap W2..W159 all '
              ->  '6ee1207bb, SINGLE STATE zero seat gap W2..W159 all '
Machine-verified fact (gate leg0 W159 row check + git history):
W159 row = bm-a r781 freeze 6ee1207bb."""
import ast
import io

N1 = r"scripts/perpetual_faces_n1.py"
src = io.open(N1, encoding="utf-8", newline="").read()

# isolate the W160 entry segment to guarantee we heal the NEW entry only
k = src.find('160: {"batch"')
assert k > 0, "W160 entry not found"
m_end = src.find('"engine_owner": "bm-a"},', k) + len('"engine_owner": "bm-a"},')
seg = src[k:m_end]

OLD1 = '"number law after the REGISTERED W159 row bm-a r779 freeze "'
NEW1 = '"number law after the REGISTERED W159 row bm-a r781 freeze "'
OLD2 = '"aed41df3e, SINGLE STATE zero seat gap W2..W159 all "'
NEW2 = '"6ee1207bb, SINGLE STATE zero seat gap W2..W159 all "'
assert seg.count(OLD1) == 1, ("frag1", seg.count(OLD1))
assert seg.count(OLD2) == 1, ("frag2", seg.count(OLD2))
# the historical W159 entry keeps its own (frozen) face untouched
assert src.count(OLD1) == 1, "frag1 must be unique to the W160 entry"
assert src.count(OLD2) == 1, "frag2 must be unique to the W160 entry"

healed = seg.replace(OLD1, NEW1).replace(OLD2, NEW2)
assert healed.count("bm-a r781 freeze ") == 1 and healed.count("6ee1207bb") == 1
assert "aed41df3e" not in healed and "bm-a r779 freeze" not in healed

out = src[:k] + healed + src[m_end:]
io.open(N1, "w", encoding="utf-8", newline="").write(out)
ast.parse(io.open(N1, encoding="utf-8", newline="").read())
print("FZT fragment heal landed: W160 entry cites the machine-verified "
      "fact 'bm-a r781 freeze 6ee1207bb' (fragment shapes, AST gate PASS)")
