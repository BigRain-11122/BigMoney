# -*- coding: utf-8 -*-
"""R263 bm-a: five-face byte probe of runnable_pool.json (R254/R255/R257 law)
before any write-back: BOM / EOL / indent / ensure_ascii / trailing newline."""
import io

raw = open("results/runnable_pool.json", "rb").read()
print("size:", len(raw))
print("BOM:", raw[:3] == b"\xef\xbb\xbf")
print("CRLF:", b"\r\n" in raw)
crlf = raw.count(b"\r\n")
lf = raw.count(b"\n") - crlf
print(f"EOL counts: CRLF={crlf} bare-LF={lf}")
print("trailing_newline:", raw.endswith(b"\n"))
txt = raw.decode("utf-8-sig")
lines = txt.splitlines()
head = [l for l in lines[:6]]
for i, l in enumerate(head):
    print(f"L{i+1}: indent={len(l)-len(l.lstrip())} | {l[:60]}")
# ensure_ascii face: any \uXXXX escapes present?
print("has_unicode_escape:", "\\u" in txt[:20000])
