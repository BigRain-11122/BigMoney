# -*- coding: utf-8 -*-
"""r771 bm-a: fix systematic escape-form bug in _r769bma_build_freeze_edits.py.

The W155 template (results/_r768bma_w155_freeze_edits.py) stores CRLF as
literal 4-byte text (\r\n) inside its string literals (LF line endings in
its own source). The r770-drafted generator wrote needles with *runtime*
CR/LF bytes, so every anchor count==0. Fix: re-escape every in-literal
\r\n text sequence to \\r\\n so generator-runtime needles carry literal
backslash text matching the template's raw bytes. Generator file itself
has zero real CR bytes (verified), so a global text-level replace is safe.
"""
import py_compile

P = r"results/_r769bma_build_freeze_edits.py"
b = open(P, "rb").read()

LIT = b"\x5c\x72\x5c\x6e"          # \r\n  (4 bytes: backslash r backslash n)
ESC = b"\x5c\x5c\x72\x5c\x5c\x6e"  # \\r\\n (6 bytes)
n_lit = b.count(LIT)
n_esc = b.count(ESC)
real_cr = b.count(b"\x0d")
real_lf = b.count(b"\x0a")
print(f"before: literal 4-byte form={n_lit} escaped form={n_esc} realCR={real_cr} realLF={real_lf}")
assert real_cr == 0, "generator has real CR bytes -- global replace unsafe, abort"
assert n_esc == 0, "escaped form already present -- unexpected, abort"

nb = b.replace(LIT, ESC)
open(P, "wb").write(nb)
py_compile.compile(P, doraise=True)
print("patched+compiled:", P, len(b), "->", len(nb), "bytes, replaced x", n_lit)

src = nb.decode("utf-8")
esc_txt = chr(92) + chr(92) + "r" + chr(92) + chr(92) + "n"
print("escaped sequences now in source text:", src.count(esc_txt))
assert src.count(esc_txt) >= 10, "expected escaped sequences in source text"
print("OK")
