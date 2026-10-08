# -*- coding: utf-8 -*-
"""r751 bm-c pit direct-write + round-report addendum (r666 direct-write
precedent, r749/r750 pattern): pit-lineage.md r751 entry (r549 family 4th
instance) + canonical round report addendum row; EOL-matched byte-exact
appends, sha16 reconcile line to stdout; receipt-style self-verify."""
import hashlib
import os

ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
PIT = os.path.join(ROOT, "research", "pit-lineage.md")
RPT = os.path.join(ROOT, "logs", "iteration-loop", "round_reports-bm-c.md")

PIT_ENTRY = (
    "- [2026-10-08 10:1x r751 bm-c] **closeout \u5206\u7c7b\u5668 marker \u767d\u540d\u5355\u628a\u8f6e\u81ea\u6709\u4ea7\u51fa\u8bef\u5224 other-session"
    "\uff08r549 \u65cf\u7b2c 4 \u72af\u00b7\u540c\u7a97\u53e0 untrackedCache \u9648\u65e7\u9690\u533f qa \u5bf9\uff09**\uff1apush \u68af\u5206\u7c7b\u5668\u6309 marker \u767d\u540d\u5355\u5206 own/other\u2014\u2014"
    "\u8f6e\u9996 S0 \u5df2\u51c0\u6811\u540e\uff0c\u6536\u53e3\u65f6 27 \u9762\u81ea\u6709\u4ea7\u51fa\uff08S6 \u518d\u751f\u96c6+\u7c3f\u8bb0\u4e09\u4ef6+post_review/attrition \u9762\uff09\u4e0d\u542b marker \u5168\u843d other"
    "\u2192targeted-add \u8def\u5f84\u9996 commit \u53ea\u6536 marker \u9762\u2192\u4ea7\u54c1\u9762\u6ede\u7559\u5de5\u4f5c\u6811\uff08qa \u8bc1\u636e\u5bf9\u540c\u65f6\u88ab untrackedCache \u9648\u65e7\u7a97\u4ece status \u9690\u533f=r549\u2460 \u540c\u6b3e\u53e0\u52a0\uff09"
    "\u2192\u540c\u7a97\u4fee\u6b63 add -A \u5438\u6536 b7a6ffe0a \u9001\u8fbe\u96f6\u4e22\u5931\u3002Why\uff1amarker \u767d\u540d\u5355\u53ea\u80fd\u679a\u4e3e\u300c\u5df2\u77e5\u81ea\u6709\u9762\u300d\uff0c\u5bf9\u6536\u53e3\u573a\u666f\u6c38\u8fdc\u4e0d\u5b8c\u5907"
    "\uff08S6 \u518d\u751f\u96c6 40 \u817f\u4ea7\u51fa\u9762\u968f\u94fe\u6f14\u5316\uff09\uff1b\u8f6e\u9996\u51c0\u6811\u5df2\u7ed9\u51fa\u66f4\u5f3a\u7684\u6240\u6709\u6743\u8bc1\u660e\u3002\u6b63\u6cd5=\u8f6e\u9996 S0 \u51c0\u6811 \u21d2 \u6536\u53e3\u4e00\u5207\u810f\u9762\u5fc5\u81ea\u6709"
    "\uff08\u672c\u673a daemon+\u672c\u8f6e\u4ea7\u51fa\uff09\u2192\u6536\u53e3 commit \u4e00\u5f8b\u65e0\u6761\u4ef6 add -A\uff1bmarker \u5206\u7c7b\u9000\u907f\u53ea\u9002\u7528\u300c\u8f6e\u9996\u810f\u300d\u573a\u666f\uff1b\u6536\u53e3\u540e\u5fc5 STATUS_CLEAN+"
    "NOT-AT-ORIGIN \u53cc\u81ea\u8bc1\uff08\u672c\u6b21\u53cc\u8bc1\u5373\u6355\u83b7\u9762\uff09\u3002How to apply\uff1a\u672a\u6765\u8f6e push \u68af/close \u9a71\u52a8\u5668\u6536\u53e3\u817f\u5220\u9664 marker \u5206\u652f\u6216\u4ec5\u4f5c\u65e5\u5fd7\u63d0\u793a\uff1b"
    "\u89c1\u300ctargeted add only\u300d\u51fa\u73b0\u5728\u6536\u53e3\u8def\u5f84=\u7ea2\u65d7\u3002\n")

RPT_ADDENDUM = (
    "2026-10-08T10:14+08:00 | r751 addendum | dept:\u5de5\u7a0b\uff08\u6536\u53e3\u4fee\u6b63\u7a97\uff09 | "
    "\u672c\u5730\u672a\u8fbe origin commit \u6570=0\uff08fixup \u540e push+fetch \u81ea\u8bc1\u00b7STATUS_CLEAN \u53cc\u8bc1\uff09 | "
    "\u505a\u4e86=closeout \u9996 commit \u68af\u5206\u7c7b\u5668 marker \u767d\u540d\u5355\u8bef\u5224 27 \u9762\u8f6e\u81ea\u6709\u4ea7\u51fa\uff08S6 \u518d\u751f+\u7c3f\u8bb0\u4e09\u4ef6+post_review/attrition\uff09"
    "\u4e3a other-session\u2192targeted-add \u6f0f\u6536+qa \u8bc1\u636e\u5bf9\u53d7 untrackedCache \u9648\u65e7\u7a97\u9690\u533f\uff08r549 \u65cf\u7b2c 4 \u72af\u53cc\u53e0\u52a0\uff09\u2192\u540c\u7a97\u4fee\u6b63=add -A "
    "\u5438\u6536 commit b7a6ffe0a+push \u9001\u8fbe ad5eca0d6..b7a6ffe0a+NOT-AT-ORIGIN=0+STATUS_CLEAN=True \u53cc\u81ea\u8bc1\uff1b"
    "\u5751\u76f4\u5199 research/pit-lineage.md r751 \u6761\uff08\u6b63\u6cd5=\u8f6e\u9996\u51c0\u6811\u21d2\u6536\u53e3\u4e00\u5f8b\u65e0\u6761\u4ef6 add -A\u00b7marker \u5206\u7c7b\u53ea\u5c5e\u8f6e\u9996\u810f\u573a\u666f\uff09 | "
    "\u4e0b\u8f6e\u6307\u9488\u4e0d\u53d8\uff08r752 marks \u76d8\u4e2d\u7eed\u5b88+\u4eca\u665a\u76d8\u540e re-arm \u9762\uff09\u3002[via bm-c r751]\n")


def append_eol(path, text):
    raw = open(path, "rb").read()
    eol = b"\r\n" if b"\r\n" in raw[-200:] else b"\n"
    if not raw.endswith(eol):
        with open(path, "wb") as fh:
            fh.write(raw + eol)
    payload = text.encode("utf-8")
    with open(path, "ab") as fh:
        fh.write(payload)
    back = open(path, "rb").read()
    assert payload in back, "append not found after write"
    return len(payload), hashlib.sha256(payload).hexdigest()[:16]


p_bytes, p_sha = append_eol(PIT, PIT_ENTRY)
r_bytes, r_sha = append_eol(RPT, RPT_ADDENDUM)
print("pit-lineage append bytes=%d sha16=%s" % (p_bytes, p_sha))
print("round-report addendum bytes=%d sha16=%s" % (r_bytes, r_sha))
back = open(PIT, "rb").read()
print("pit reconcile: bytes=%d verbatim-in-file=%s" % (p_bytes, PIT_ENTRY.encode("utf-8") in back))
