"""r696 bm-b: append one CODELY.md pit entry (bytes mode, EOL-detected, r679 idem gate)."""
import sys

ROOT = __file__.rsplit("\\", 1)[0].rsplit("\\", 1)[0]
PATH = ROOT + "\\CODELY.md"

MARK = "r696 bm-b] ls-tree \u76ee\u5f55\u8def\u5f84\u5f62\u6001\u5751"
ENTRY = ("- [2026-10-04 21:4x r696 bm-b] ls-tree \u76ee\u5f55\u8def\u5f84\u5f62\u6001\u5751\uff08S0.5 \u4ee4\u5dee\u96c6\u63a2\u9488\u9996\u8dd1\u5b9e\u5f39\u00b7\u5f53\u573a\u81ea\u7ea0\uff09\uff1a"
         "`git ls-tree --name-only HEAD fleet/orders/` \u5e26\u76ee\u5f55 pathspec \u8fd4\u56de\u6811\u6761\u76ee\u672c\u4f53\u800c\u975e\u5b50\u6587\u4ef6\u2014\u2014\u63a2\u9488\u9759\u9ed8\u4ea7\u51fa ORDERS=0 \u7a7a\u96c6+\u5168\u91cf ack_extra \u5047\u5f62\u6001\uff1b"
         "\u76ee\u5f55\u5b50\u4ef6\u679a\u4e3e\u6b63\u5f62=tree-ish \u76f4\u53d6 `git ls-tree --name-only HEAD:fleet/orders`\uff08\u6216 -r \u5f62\uff09\u3002"
         "\u4fee=results/_r696bmb_orders_check.py\uff08r477 \u5168\u540d\u53e3\u5f84\u5f8b\u5185\u5efa\uff09\u3002"
         "How to apply\uff1als-tree \u679a\u4e3e\u76ee\u5f55\u5b50\u4ef6\u4e00\u5f8b tree-ish \u5f62\uff08HEAD:<dir>\uff09\uff1b"
         "\u89c1\u300c\u6e05\u5355=0 \u4f46\u53f0\u8d26\u975e\u7a7a\u300d\u5148\u67e5 ls-tree \u8c03\u7528\u5f62\u6001\u518d\u7acb\u53d9\u4e8b\uff08r641 \u590d\u73b0\u8bc1\u4f2a\u5f8b\u65cf\uff09\u3002")

with open(PATH, "rb") as f:
    blob = f.read()
assert blob.count(MARK.encode("utf-8")) == 0, "idem gate: entry already present"
eol = b"\r\n" if blob.count(b"\r\n") * 2 > blob.count(b"\n") else b"\n"
if not blob.endswith(eol):
    blob += eol
blob += ENTRY.encode("utf-8") + eol
with open(PATH, "wb") as f:
    f.write(blob)
with open(PATH, "rb") as f:
    check = f.read()
assert check.count(MARK.encode("utf-8")) == 1, "post-marker count must be 1"
print("APPEND OK, size=", len(check))
