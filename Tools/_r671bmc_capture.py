# -*- coding: utf-8 -*-
"""r671 bm-c knowledge capture: E09 methodology card append (section 二,
after E08) + TREASURE_REGISTRY 出入记录 row append. Five-class capture step
(方法论卡 append class, O-20261003-2030 §1) for the r671 dup-heal batch.
Byte-safe targeted inserts with rerun guards + count==1 post-verify."""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MA = os.path.join(ROOT, "knowledge", "METHODOLOGY_ASSETS.md")
TR = os.path.join(ROOT, "knowledge", "TREASURE_REGISTRY.md")

E09 = (
    "- **E09 append-only \u53f0\u8d26\u7ffb\u500d tripwire+keep-first \u6cbb\u6108\u6cd5**\uff08proven\uff09\uff1a"
    "\u591a\u673a\u7ade\u901f UU \u6536\u53e3\u628a\u5168\u53f2\u53f0\u8d26\u6574\u6587\u4ef6\u62fc\u63a5=\u6bcf\u7a97 \u00d72 \u6307\u6570\u7ffb\u500d"
    "\uff08r666/r668/r669 \u4e09\u7a97 2.23MB\u219217.87MB \u65e0\u58f0\u7ffb 8 \u500d\uff09\uff1b"
    "\u9632\u62a4\u4e09\u4ef6=\u2460UU/union \u6536\u53e3\u5fc5 exact-line dedup+marker \u8ba1\u6570"
    "\u2461\u6bcf\u8f6e tripwire scan\uff08\u5934\u884c\u8ba1\u6570>1 \u6216\u957f\u884c multiplicity\u22654=ACTIVE\uff09"
    "\u2462\u6cbb\u6108=keep-first dedup+\u96c6\u5408\u6052\u7b49\u96f6\u4e22\u5931\u95e8+\u9694\u79bb\u533a\u3002"
    "\u8bc1\u636e\uff1ar671 \u6cbb\u6108\uff0817,882,876\u21922,245,406B\u00b7\u7eaf\u5220\u9664\u96f6\u63d2\u5165\u00b7"
    "receipt results/_r671bmc_rr_dup_heal_receipt.json\u00b7tripwire Tools/_r671bmc_rr_dup_heal.py\uff09\u3002"
)
TRROW = (
    "- 2026-10-07 11:1x bm-c r671 \u8f6e\u62a5\u53f0\u8d26 2\u00b3 \u6574\u6587\u4ef6\u7ffb\u500d\u6cbb\u6108\u6279\uff08tripwire+keep-first dedup "
    "\u96f6\u4e22\u5931\u00b7r453 union \u65cf\u7b2c\u4e09\u9762\u5b55\u5316\uff09\uff1around_reports-bm-c.md 17,882,876\u21922,245,406B"
    "\uff08\u221215.64MB\u00b7\u5934\u00d78\u21921\u00b7300 \u6761\u76ee\u5168\u552f\u4e00\u00b7diff \u7eaf\u5220\u9664\u96f6\u63d2\u5165\uff09"
    "\u00b7\u9694\u79bb\u533a 7 \u5929\u7a97 results/_quarantine/20261007-1105_r671bmc_rr_predup/"
    "\u00b7\u6536\u636e _r671bmc_rr_dup_heal_receipt.json\u00b7\u5751\u5f8b\u76f4\u5199 pit-git-surgery.md\uff08r453 \u65cf\u6b63\u4e3b\u9762\uff09"
    "\u00b7\u65b9\u6cd5\u8bba\u5361 E09 append"
)


def main():
    # -- E09 card into METHODOLOGY_ASSETS section 二 (before ## 三) --
    raw = open(MA, "rb").read()
    eol = b"\r\n" if raw.count(b"\r\n") >= 10 else b"\n"
    guard = b"E09 append-only"
    assert raw.count(guard) == 0, "rerun guard: E09 present"
    anchor = "\u4e09\u3001\u8d1f\u65b9\u6cd5\u8d44\u4ea7".encode("utf-8")
    aidx = raw.find(b"## " + anchor)
    assert aidx > 0, "section 三 anchor"
    # insert point: start of the '## 三' line; E08's line already ends with EOL
    ins = E09.encode("utf-8") + eol
    new = raw[:aidx] + ins + raw[aidx:]
    open(MA, "wb").write(new)
    post = open(MA, "rb").read()
    assert post.count(guard) == 1, "post-verify E09 count==1"
    print("E09 appended; METHODOLOGY_ASSETS now %d B" % len(post))

    # -- registry row (append-only tail) --
    raw2 = open(TR, "rb").read()
    eol2 = b"\r\n" if raw2.count(b"\r\n") >= 10 else b"\n"
    guard2 = "bm-c r671 \u8f6e\u62a5\u53f0\u8d26".encode("utf-8")
    assert raw2.count(guard2) == 0, "rerun guard: registry row present"
    assert raw2.endswith(eol2), "registry tail EOL gate"
    new2 = raw2 + TRROW.encode("utf-8") + eol2
    open(TR, "wb").write(new2)
    post2 = open(TR, "rb").read()
    assert post2.count(guard2) == 1, "post-verify registry count==1"
    print("registry row appended; TREASURE_REGISTRY now %d B" % len(post2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
