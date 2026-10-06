# -*- coding: utf-8 -*-
"""r787 bm-a W161 frozen-face prose heal (r783-heal precedent class, third
instance): the W161 materializer B-assert prose carries a vmap-leak
"jumps to 368_804, first-clean" -- the W161 B walk's honest jump target is
371_004 per the frozen-window gate receipt (_r785bma_w161_band_gate.json
leg1 B_hop_chain: window [371204,371403] -> jump_to 371204... final B =
[371004, 371203]). 368_804 = the W160 B base (the r781-vmap latent leak
face: the fragment shape "own-wave A window reserved jumps to 368_804,
first-clean " was not tokenized in the W161 freeze TOK, so the W160 value
leaked verbatim into the W161 B assert message). Healed with the
machine-verified gate value 371_004; needle whole-file count==1 (W160 block
has a different physical shape for its own B walk prose -- verified)."""
import ast
import io
import json

N1 = r"scripts/perpetual_faces_n1.py"
CRLF = "\r\n"

OLD = 'own-wave A window reserved jumps to 368_804, first-clean '
NEW = 'own-wave A window reserved jumps to 371_004, first-clean '

gate = json.load(open("results/_r785bma_w161_band_gate.json", encoding="utf-8"))
leg1 = gate["legs"]["leg1"]
assert gate["verdict"] == "ADMIT"
assert leg1["B"] == [371004, 371203], leg1["B"]
# machine-verified: the W161 B walk jumped to 371_004 (own-A tail+1)
assert leg1["B"][0] == 371_004 == leg1["A"][1] + 1, "B base != own-A tail+1"
assert leg1["B_hop_chain"] and leg1["B_hop_chain"][0]["jump_to"] == 371004, \
    "gate hop chain does not carry 371_004 as the jump target"

src = io.open(N1, encoding="utf-8", newline="").read()
n = src.count(OLD)
assert n == 1, f"heal needle count={n} expect=1"
i = src.find("# --- W161 materializer face")
j = src.find("# --- T-141 s2 lane face", i)
assert 0 < i < j and src[i:j].count(OLD) == 1, "needle not inside the W161 block"
src = src.replace(OLD, NEW)
io.open(N1, "w", encoding="utf-8", newline="").write(src)
ast.parse(io.open(N1, encoding="utf-8", newline="").read())
after = io.open(N1, encoding="utf-8", newline="").read()
assert after.count(NEW) == 1 and after.count(OLD) == 0
# r773 pit law leg 3: full-file start>end malformed-window scan
import re
bad = [m.group() for m in re.finditer(r"(\d{3})_(\d{3})\.\.(\d{3})_(\d{3})", after)
       if int(m.group(3)) < int(m.group(1))]
assert not bad, f"malformed windows: {bad[:4]}"
print("W161 B-assert prose heal landed: 368_804 -> 371_004 (gate-receipt "
      "machine value; AST gate PASS; whole-file malformed-window scan CLEAN)")
