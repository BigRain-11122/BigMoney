# -*- coding: utf-8 -*-
"""r545 bm-a: add the W35 materializer leg to the runner selftest summary
string (claims-vs-reality consistency law -- the leg code landed and PASSED,
the prose summary must carry it)."""
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
p = "scripts/perpetual_faces_n1.py"
raw = open(p, "rb").read()
eol = b"\r\n" if raw.count(b"\r\n") > (raw.count(b"\n") - raw.count(b"\r\n")) else b"\n"
E = eol.decode("ascii")
src = open(p, encoding="utf-8", newline="").read()

old = E.join([
    '          "(W32 row slot assignment verbatim), r544 bm-a] "',
    '          "+ T-141 s2 "',
])
new = E.join([
    '          "(W32 row slot assignment verbatim), r544 bm-a] "',
    '          "+ W35 materializer face [same guard set, dep=W17..W33 "',
    '          "ALL present (W34 has NO registry row -- bm-b pre-scan "',
    '          "ADMIT-READY r527, freeze pending at the bm-b seat; dep "',
    '          "pin auto-joins +34 per r531-1/r541 precedent once bm-b "',
    '          "lands the W34 freeze; finalize runtime FAIL-CLOSED composes "',
    '          "every registry key below 35), FORCED SKIP over the published "',
    '          "W34 projection windows A 111_004..113_003 / B 41_801..42_000 "',
    '          "(reserved face r518; candidate == published-projection end + 1 "',
    '          "both sides, machine-proven by results/_r545bma_w35_band_gate.py "',
    '          "refusal facts), law sec.4 W35 row 113_004..115_003 / "',
    '          "42_001..42_200, TWENTY-FOURTH ENGINE-OWNED WAVE "',
    '          "engine_owner=bm-a per engine de-throttle law "',
    '          "O-20261001-2355 sec.2 own-continuous-series (first bm-a "',
    '          "wave under the de-throttle law, zero-gap relay after W33 "',
    '          "close), r545 bm-a] "',
    '          "+ T-141 s2 "',
])
assert src.count(old) == 1, f"anchor not unique: {src.count(old)}"
open(p, "w", encoding="utf-8", newline="").write(src.replace(old, new))
import ast
ast.parse(open(p, encoding="utf-8", newline="").read())
print("summary string W35 leg landed, AST OK")
