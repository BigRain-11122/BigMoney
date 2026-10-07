# -*- coding: utf-8 -*-
"""r671 bm-c pit direct-write probe+append: pit-git-surgery.md tail EOL probe,
then byte-safe append of the r671 whole-file-dup pit entry (family home of
r453/r675/r479 union-dedup law). Zero main-CODELY occupancy (r668/r670
S4-direct-write precedent)."""
import os
import sys

PIT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   "research", "pit-git-surgery.md")

ENTRY = (
    "- [2026-10-07 11:0x r671 bm-c] append-only \u53f0\u8d26\u6574\u6587\u4ef6\u7ffb\u500d\u76f2\u533a\u5751"
    "\uff08r453/r675 union \u65cf\u7b2c\u4e09\u9762\u00b7round_reports-bm-c.md \u5b9e\u5f39\u00b7r671 \u5f53\u8f6e\u6cbb\u6108\uff09\uff1a"
    "UU \u6536\u53e3\u628a r453 \u7684\u300c\u6761\u76ee\u7ea7 exact-line dedup\u300d\u6f0f\u6210\u300c\u6574\u6587\u4ef6 bare-concat\u300d\u2014\u2014"
    "\u4e24\u4e2a\u5e76\u53d1/\u7ade\u901f\u7a97\u4f1a\u8bdd\u5404\u6301\u5168\u53f2\u526f\u672c\u65f6 union=\u53cc\u53f2\u62fc\u63a5\uff0c"
    "\u6bcf\u7a97 \u00d72 \u6307\u6570\u7d2f\u8fdb\uff08\u5b9e\u5f39=r666/r668/r669 \u4e09\u7a97 push-race \u6536\u53e3\u00b7blob 2,230,045\u21924,461,521\u21928,933,204\u219217,873,611B\u00b7"
    "9,265 \u884c\u00b7\u5934\u884c\u00d78\u00b7\u6761\u76ee\u00d78\uff09\u65e0 tripwire \u5219\u4e0d\u53ef\u89c1\uff08\u4e0b\u4e00\u7ffb\u500d=35MB\u00b7\u79bb 95MB \u7ea2\u7ebf\u53ea\u5269 5 \u7ffb\uff09\uff1b"
    "\u6cbb\u6108=keep-first exact-line dedup+\u96c6\u5408\u6052\u7b49\u96f6\u4e22\u5931\u95e8+\u9694\u79bb\u533a\uff08r671 \u5f53\u8f6e\u00b717,882,876\u21922,245,406B\u00b7"
    "diff=\u7eaf\u5220\u9664\u96f6\u63d2\u5165\u00b7receipt _r671bmc_rr_dup_heal_receipt.json\uff09\uff1b"
    "\u6b63\u6cd5=\u2460append-only \u9762\u4e00\u5207 union/\u6536\u53e3\u5fc5 exact-line dedup+marker \u8ba1\u6570\uff08r453 \u5f8b\u6267\u6cd5\u9762\u6269\u5230\u8f6e\u62a5/\u5fc3\u8df3\u53f0\u8d26\uff09"
    "\u2461tripwire=\u6bcf\u8f6e scan\uff08\u5934\u884c\u8ba1\u6570>1 \u6216\u4efb\u4e00\u957f\u884c multiplicity\u22654=ACTIVE DUP\u00b7"
    "Tools/_r671bmc_rr_dup_heal.py scan\uff09\u2462\u8f6e\u62a5\u7c7b\u5355 commit blob \u5c3a\u5bf8\u73af\u6bd4\u7ffb\u500d=\u7ea2\u65d7\u3002"
    "How to apply\uff1aUU \u89e3\u9762\u52a8 append-only \u53f0\u8d26\u524d\u5148\u8dd1 tripwire scan\uff1b\u6536\u53e3 push \u524d\u590d\u8dd1\u4e00\u6b21\uff1b\u6cbb\u6108\u540e scan CLEAN \u624d\u8bb8 add\u3002\n"
)


def main():
    raw = open(PIT, "rb").read()
    eol = b"\r\n" if raw.count(b"\r\n") >= 10 else b"\n"
    probe = "\u7ffb\u500d\u76f2\u533a\u5751".encode("utf-8")
    assert raw.count(probe) == 0, "rerun guard: entry already present"
    assert raw.count(b"\n") > 10, "sanity gate (34 long-line entries legit)"
    sep = b"" if raw.endswith(eol) else eol
    new = raw + sep + ENTRY.encode("utf-8")
    open(PIT, "wb").write(new)
    post = open(PIT, "rb").read()
    assert post.count(probe) == 1, "post-verify count==1"
    print("PIT appended; file now %d B (eol=%s)" % (len(post), eol.decode()))
    return 0


if __name__ == "__main__":
    sys.exit(main())
