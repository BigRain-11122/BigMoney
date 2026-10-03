# -*- coding: utf-8 -*-
"""r447 bm-c codec diagnostic: locate exact break char in mojibake lines."""
import io, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "CODELY.md")
OUT = os.path.join(ROOT, "results", "_r447bmc_diag_codec.txt")

raw = open(SRC, "rb").read()
texts = [b.decode("utf-8", "replace") for b in raw.split(b"\r\n")]

moji = [i for i, t in enumerate(texts) if "\u20ac" in t or re.search(r"[\u93c8\u9426\u62c9\u5c3a]", t)]
buf = []
buf.append("candidate mojibake lines (1-based): %s" % [i + 1 for i in moji][:25])
if moji:
    i = moji[0]
    t = texts[i]
    buf.append("line %d len=%d" % (i + 1, len(t)))
    # per-char encode failure census for cp936 / gbk / gb18030
    for codec in ("cp936", "gbk", "gb18030"):
        bad = []
        for k, ch in enumerate(t):
            try:
                ch.encode(codec)
            except UnicodeEncodeError:
                bad.append((k, hex(ord(ch))))
        buf.append("codec %s per-char encode failures: %d %s" % (
            codec, len(bad), bad[:12]))
        try:
            b = t.encode(codec)
            buf.append("codec %s full-line encode OK bytes=%d" % (codec, len(b)))
            try:
                rec = b.decode("utf-8")
                buf.append("codec %s roundtrip decode utf-8 OK rec!=orig:%s rec_len=%d" % (
                    codec, rec != t, len(rec)))
            except UnicodeDecodeError as e:
                buf.append("codec %s roundtrip utf-8 decode FAIL at byte %d: %s" % (
                    codec, e.start, str(e)[:120]))
        except UnicodeEncodeError as e:
            buf.append("codec %s full-line encode FAIL at char %d (U+%04X): %s" % (
                codec, e.start, ord(t[e.start]) if e.start < len(t) else -1, str(e)[:100]))
    # first 40 codepoints of the line
    buf.append("first 60 codepoints: " + " ".join("%04X" % ord(c) for c in t[:60]))
    # try line-by-line: maybe only SOME chars came from cp936-decode and the
    # euro single-byte got doubled somewhere. attempt partial recovery:
    # encode with cp936 ignoring the known-bad chars, then decode utf-8 replace.
    for codec in ("cp936", "gb18030"):
        try:
            b = t.encode(codec, errors="replace")
            rec = b.decode("utf-8", errors="replace")
            ratio = len(re.findall(r"[\u4e00-\u9fff]", rec)) / max(1, len(rec))
            buf.append("codec %s lenient roundtrip cjk_ratio=%.3f head=%r" % (codec, ratio, rec[:60]))
        except Exception as e:
            buf.append("codec %s lenient FAIL %s" % (codec, str(e)[:80]))
with io.open(OUT, "w", encoding="utf-8", newline="\n") as f:
    f.write("\n".join(buf))
print("DIAG-WRITTEN lines=%d" % len(buf))
