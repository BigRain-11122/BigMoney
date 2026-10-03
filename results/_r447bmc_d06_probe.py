# -*- coding: utf-8 -*-
"""r447 bm-c D-06 final-sweep reconnaissance probe (read-only).

Targets (T-144(c) remaining scope, due 10-07):
  1. research/pit-data.md  -- CRLF-face line census
  2. research/pit-git.md    -- assert-layer family lines (r402/r419/r420 kin)
  3. CODELY.md (repo root) -- hot-layer tail census: mojibake span + line map
Zero writes. Pure census output for sweep planning.
"""
import os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def census(path, patterns):
    full = os.path.join(ROOT, path)
    if not os.path.isfile(full):
        print("MISSING", path); return
    raw = open(full, "rb").read()
    text = raw.decode("utf-8", "replace")
    lines = text.split("\n")
    print("=== %s === bytes=%d lines=%d" % (path, len(raw), len(lines)))
    for i, ln in enumerate(lines, 1):
        for tag, pat in patterns:
            if re.search(pat, ln):
                print("  L%-4d [%s] %s" % (i, tag, ln[:150]))
                break

census("research/pit-data.md", [
    ("CRLF", r"CRLF|\\r\\n|行界|终结符"),
    ("MD5",  r"md5|MD5"),
])
census("research/pit-git.md", [
    ("ASSERT", r"断言|assert|三计数|恒等律|needle|furniture"),
    ("MD5",   r"md5|MD5"),
])
# CODELY.md tail census: locate mojibake lines (GBK-mojibake signature chars)
full = os.path.join(ROOT, "CODELY.md")
raw = open(full, "rb").read()
try:
    text = raw.decode("utf-8")
    enc = "utf-8-clean"
except UnicodeDecodeError:
    enc = "utf-8-with-errors"
text = raw.decode("utf-8", "replace")
lines = text.split("\n")
moji = [i for i, ln in enumerate(lines, 1) if re.search(r"[\u93c8\u9428\u62c9\u5c3a\u51b6\u94a3\u7bc7\u8bc9]", ln) or ("CEO 鏈" in ln)]
print("=== CODELY.md === bytes=%d lines=%d decode=%s mojibake_lines=%s" % (
    len(raw), len(lines), enc, (moji[:3] + ["..."] + moji[-3:]) if len(moji) > 6 else moji))
if moji:
    print("  first mojibake L%d: %s" % (moji[0], lines[moji[0]-1][:120]))
    print("  last  mojibake L%d: %s" % (moji[-1], lines[moji[-1]-1][:120]))
    print("  contiguity: %d..%d, non-moji inside span: %d" % (
        moji[0], moji[-1], sum(1 for i in range(moji[0], moji[-1]+1) if i not in set(moji))))
print("DONE rc=0")
