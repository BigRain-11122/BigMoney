# -*- coding: utf-8 -*-
"""r753 bm-c: append boot self-clone pit entry to research/pit-lineage.md (byte-exact)."""
import io

P = r"K:\Fluxgroup\FluxGroup\quant\bigmoney\research\pit-lineage.md"
ENTRY = u"- [2026-10-08 10:4x r753 bm-c] **boot \u81ea\u4e3e\u4ef6\u4e0d\u53ef\u81ea\u514b\u9686\u5751\uff08\u514b\u9686\u95e8\u94fe\u00b7\u9884\u9632\u9762\u6761\u76ee\u00b7r753 \u63a8\u5bfc+\u65ad\u8a00\u62e6\u622a\u94fe\u5206\u6790\u00b7\u975e\u5b9e\u5f39\u96f6\u635f\u5931\uff09**\uff1a\u8f6e\u514b\u9686\u95e8\u8840\u7edf\u7684 boot\uff08_rNNbmc_boot.py\uff09\u81ea\u8eab**\u7981**\u6309\u964d\u5e8f\u53cc\u66ff\u6362\u5f8b\u81ea\u514b\u9686\u2014\u2014\u8be5\u5f8b\u4f5c\u7528\u57df=clone \u6e90\uff08\u542b N-1/N \u4e24\u4ee3 token \u7684 _rN-1bmc_clone.py\uff09\uff0cboot \u81ea\u8eab\u7684\u7b2c\u4e8c\u66ff\u6362\u5bf9\u884c\uff08replace(\"N-2\",\"N-1\") \u5f62\uff09\u7ecf\u540c\u4e00\u53cc\u66ff\u6362\u540e\u53d8 replace(\"N-2\",\"N\")\uff08751\u2192752 \u7684\u884c\u53d8 750\u2192752\uff09\uff1aclone \u6e90\u5185 N-1 token \u5168\u6570\u6b8b\u7559\u2192boot \u7684 'stale N-1' \u65ad\u8a00\u5f53\u573a\u7ea2\uff08\u62a5\u9519\u9690\u6666\u4e0d\u6307\u5411\u66ff\u6362\u5bf9\uff09\u2014\u2014\u82e5\u8bef\u8d70\u300c\u653e\u5bbd\u65ad\u8a00\u300d\u4fee\u7ebf\u5373\u4ea7\u9519\u6e90\u514b\u9686\uff08src \u843d _rN-2bmc_ \u8df3\u4ee3\u8bfb\u6e90\uff09\u3002\u6b63\u6cd5=\u6bcf\u8f6e boot \u4e00\u5f8b\u624b\u5199\u56db\u7ec4\u6570\u5b57\uff08SRC/DST \u8def\u5f84+\u4e24\u66ff\u6362\u5bf9 N\u2192N+1 \u5148\u884c\u518d N-1\u2192N\uff09\uff0c\u5199\u540e\u8dd1 boot \u7531\u5176\u65ad\u8a00\u94fe\u81ea\u8bc1\uff08stale \u952e+round \u6807+\u524d\u7f00\u8ba1\u6570\u4e09\u65ad\u8a00\u5168\u7eff=\u66ff\u6362\u5bf9\u6b63\u786e\u6027\u673a\u5668\u53ef\u8bc1\uff09\u3002How to apply\uff1a\u590d\u5236\u514b\u9686\u95e8\u8840\u7edf\u65f6 boot \u8d70\u624b\u5199\u4e0d\u8d70 Copy-Item+replace\uff1b\u89c1 boot \u65ad\u8a00\u7ea2\u5148\u6838\u4e24\u66ff\u6362\u5bf9\u884c\u518d\u6838\u65ad\u8a00\uff0c\u7981\u53cd\u5411\u653e\u5bbd\u65ad\u8a00\u3002"

raw = io.open(P, "rb").read()
before = len(raw)
assert raw.endswith(b"\n"), "file must end with newline (got tail=%r)" % raw[-12:]
assert b"targeted add only" in raw[-4000:], "anchor (r751 entry) not in tail window"
assert u"\u51fa\u73b0\u5728\u6536\u53e3\u8def\u5f84=\u7ea2\u65d7\u3002".encode("utf-8") in raw[-400:], "tail anchor bytes mismatch"
add = ENTRY.encode("utf-8") + b"\n"
assert raw.endswith(b"\n") and not raw.endswith(b"\r\n"), "tail probe: expected bare-LF tail, got %r" % raw[-8:]
io.open(P, "ab").write(add)
after = len(io.open(P, "rb").read())
delta = after - before
assert delta == len(add), "byte delta mismatch %d != %d" % (delta, len(add))
assert ENTRY.encode("utf-8") in io.open(P, "rb").read()[-len(add)-50:], "append verify failed"
print("append ok before=%d after=%d delta=%d entry_bytes=%d" % (before, after, delta, len(add)))
