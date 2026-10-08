# -*- coding: utf-8 -*-
# r750 bm-c: direct-write pit entry to research/pit-protocol-lane.md
# (r666 direct-write precedent; main CODELY.md ~30,684B is ~436B under the
# 30,720B cap -> no main-file append, domain file is the ledger-mechanics home)
import hashlib

P = r"K:\Fluxgroup\FluxGroup\quant\bigmoney\research\pit-protocol-lane.md"
ENTRY = (
    "- [2026-10-08 09:5x r750 bm-c] **\u6536\u5c3e\u811a\u672c\u8f6e\u62a5\u884c\u8def\u5f84\u8de8\u673a\u5f8b\u8bef\u7528\u5751\uff08r749 \u884c\u843d ROOT \u51bb\u7ed3\u9762\u2192r750 \u8de8\u9762\u6cbb\u6108\u5b9e\u5f55\uff09**\uff1a"
    "bm-a r844/r865 \u5f8b\uff08\u6b63\u5178=\u4ed3\u6839 round_reports-bm-a.md\u00b7\u6536\u5c3e\u540e grep ROOT \u9a8c\u884c\uff09\u662f bm-a \u81ea\u6709\u9762\u5f8b\u2014\u2014bm-a r844 \u8d77\u81ea\u5bb6\u6b63\u5178\u5df2\u7531 logs/iteration-loop/ \u8fc1\u4ed3\u6839\uff1b"
    "bm-c \u6b63\u5178\u9762\u6052=fleet/README \u00a76+r645 \u7eaa\u5143\u51bb\u7ed3\u6ce8\u8bb0\uff08logs/iteration-loop/round_reports-bm-c.md\u00b7ROOT \u9762\u5df2\u5ba3\u544a\u300c\u672c\u4ef6\u505c\u5199\u300d\uff09\uff1b"
    "r749 \u6536\u5c3e\u6a21\u677f\u673a\u68b0\u7167\u642c r865 \u4fee\u590d\uff08RPT \u6539\u4ed3\u6839+grep ROOT \u65ad\u8a00\uff09\u2192r749 \u884c\u843d ROOT \u51bb\u7ed3\u9762=\u8de8\u9762\u843d\u884c\u00b7\u8f6e\u8d26\u672c\u5206\u88c2"
    "\uff08r643-748 \u5728\u6b63\u5178\u00b7r749 \u5728\u51bb\u7ed3\u9762\uff09\uff1b\u8f6e\u5185\u81ea\u9a8c grep ROOT \u901a\u8fc7=\u65ad\u8a00\u9762\u968f\u9519\u9762\u8d70\u672a\u62e6\u622a\u3002"
    "\u6b63\u6cd5=\u2460\u8f6e\u62a5\u884c\u8def\u5f84\u4ee5\u672c\u673a\u6b63\u5178\u9762\u58f0\u660e\u4e3a\u51c6\uff08fleet/README \u00a76+\u672c\u673a\u9762\u5185\u51bb\u7ed3\u6ce8\u8bb0\uff09\uff0c\u8de8\u673a\u514b\u9686\u8def\u5f84\u5f8b\u524d\u5fc5\u6838\u672c\u673a\u9762\uff1b"
    "\u2461\u5df2\u843d\u9519\u9762\u884c=r865-heal \u955c\u50cf verbatim \u590d\u8fc1\u6b63\u5178\u9762+\u9519\u9762\u4e0d\u52a8\uff08append-only\u00b7git \u53f2\u4fdd\u5168\uff09+heal \u6ce8\u8bb0\u884c+\u6536\u636e\uff1b"
    "\u2462\u6536\u5c3e\u81ea\u9a8c grep \u672c\u673a\u6b63\u5178\u9762\uff08\u975e\u4ed6\u673a ROOT \u9762\uff09\u3002"
    "How to apply\uff1a\u514b\u9686\u6536\u5c3e/\u8bb0\u8d26\u811a\u672c\u65f6 RPT \u8def\u5f84\u5e38\u91cf\u5fc5\u6838\u672c\u673a\u6b63\u5178\u9762\uff1bm-c \u4e00\u5207\u6536\u5c3e\u811a\u672c RPT=logs/iteration-loop/round_reports-bm-c.md\uff1b"
    "r749 close \u6a21\u677f\uff08ROOT \u8def\u5f84\uff09=\u5df2\u6cbb\u6108\u9519\u9762\u7981\u518d\u514b\u9686\uff1bbm-b \u6cbf\u7528 logs/iteration-loop/round_reports.md\uff08\u00a76\uff09\u540c\u5f8b\u3002"
)
raw = open(P, "rb").read()
eol = b"\r\n" if b"\r\n" in raw[-200:] else b"\n"
block = ENTRY.encode("utf-8")
sha16 = hashlib.sha256(block).hexdigest()[:16]
rec_line = ("- \u5bf9\u8d26\u884c r750 bm-c: entry bytes=%d sha16=%s verbatim-in-file (direct-write r666 precedent; "
            "main CODELY.md under 30,720B cap untouched; zero-loss asserted)" % (len(block), sha16)).encode("utf-8")
if not raw.endswith(eol):
    raw += eol
with open(P, "wb") as f:
    f.write(raw + block + eol + rec_line + eol)
print("appended bytes=%d sha16=%s new_size=%d eol=%r" % (
    len(block), sha16, len(raw) + len(block) + 2 * len(eol) + len(rec_line), eol))
