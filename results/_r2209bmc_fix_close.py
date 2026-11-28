"""r2209: repair Tools/_r820bmc_close.py -- line 130 left a string literal open.

The file has never parsed since the commit that created it (import_git_coverage
found it in r2203). Fix = close the literal at L130 and open the next one, which
is what the neighbouring lines already do. Bytes are preserved otherwise.
"""
import io
import sys

P = "Tools/_r820bmc_close.py"
QUOTE = '"'

s = io.open(P, encoding="utf-8", newline="").read()
lines = s.split("\n")

a = lines[129]
b = lines[130]
if a.rstrip("\r").endswith(QUOTE):
    print("already closed at L130 -- nothing to do")
    sys.exit(0)

cr_a = a.endswith("\r")
cr_b = b.endswith("\r")
body_b = b[:-1] if cr_b else b

lines[129] = a + QUOTE                      # keeps its own line ending
lines[130] = QUOTE + body_b + ("\r" if cr_b else "")

io.open(P, "w", encoding="utf-8", newline="").write("\n".join(lines))
print("patched L130/L131")
