# -*- coding: utf-8 -*-
"""One-off: drop the two ordinal keys that the previous generation already advanced."""
import io

p = "results/_w310bmc_gen_patch.py"
s = io.open(p, encoding="utf-8").read()
for line in ('    ("HUNDRED-AND-TWENTY-FIFTH", "HUNDRED-AND-TWENTY-SIXTH"),\n',
             '    ("THREE HUNDRED AND SIXTH", "THREE HUNDRED AND SEVENTH"),\n'):
    assert line in s, line
    s = s.replace(line, "")
io.open(p, "w", encoding="utf-8", newline="\n").write(s)
print("patched")