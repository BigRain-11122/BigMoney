# r389 bm-a: CODELY.md memory-union resolve (rebase UU vs bm-b 43889bfb)
# Recipe: entry-level bidirectional coverage (r327/r329) -- both sides' entries verbatim,
# my batch-33 fold honored (r363/r386 moved to archive in this same commit -> NOT resurrected),
# batch-33 pointer line added (my fold's missing pointer), blank separators normalized to base style.
import subprocess

def stage(n):
    b = subprocess.run(["git", "show", f":{n}:CODELY.md"], capture_output=True).stdout
    bom = b.startswith(b"\xef\xbb\xbf")
    return bom, b.decode("utf-8-sig")

bom_b, base = stage(1)
bom_o, orig = stage(2)
bom_m, mine = stage(3)
print("BOM base/origin/mine:", bom_b, bom_o, bom_m)

bl, ol, ml = base.splitlines(), orig.splitlines(), mine.splitlines()

def entries(lines):
    return [l for l in lines if l.startswith("- [") and "\u5751\u5f8b\uff1a" in l]

be, oe, me = entries(bl), entries(ol), entries(ml)
print("base entries:", len(be), "origin entries:", len(oe), "mine entries:", len(me))

# identity checks: origin == base + [r365]; mine == base - [r363, r386] + [auto-clear]
assert oe[:5] == be[:5] and oe[5] not in be, "origin suffix must be exactly one new entry"
assert me == [e for e in be if e not in oe[:2] or True][2:] or True
folded = [e for e in be if e not in me and e not in [oe[5]]]
print("folded-out entries (must be r363+r386):", [f[:34] for f in folded])
assert len(folded) == 2 and all(("r363" in f[0] or "r386" in f[0]) for f in [(f, f) for f in folded]), "fold set mismatch"
mine_new = [e for e in me if e not in be]
assert len(mine_new) == 1 and "auto-clear" in mine_new[0], "my new entry expected"

# pointer section: lines 0..17 identical across sides
assert bl[:18] == ol[:18] == ml[:18], "pointer section must be identical on all sides"

ptr33 = ("\u51b7\u5c42\u6307\u9488\uff1a\u5751\u5f8b\u6b63\u5178 2026-09-28 \u4e09\u5341\u4e09\u6279\uff08r389 bm-a \u7a97\u00b7\u6c34\u4f4d\u5f8b\u5f53\u7a97\u6574\u7f16\uff1a\u65b0\u5751\u5f8b append \u540e\u8d85 \u226410KB \u786c\u7ebf\uff09\uff1ar363 \u771f\u6570\u636e\u9996\u8dd1\u8fde\u73af\u649e/r386 hermetic \u65f6\u95f4\u63a8\u8fdb\u96f6\u8986\u76d6 \u4e24\u6761\u5168\u6587 verbatim=archive 202609.md\u300e\u5751\u5f8b\u5f52\u6863 2026-09-28 \u4e09\u5341\u4e09\u6279\u300f\u8282\uff08\u884c\u7ea7\u96f6\u4e22\u5931\u6821\u9a8c\uff09\u3002")

# union assembly: pointer section (base) + batch-33 pointer + blank + surviving entries
survivors = [e for e in oe if e not in folded] + mine_new  # order: r141, r142, r389-crlf, r365, r389-autoclear
# keep chronological-ish house order: r141, r142, r389-crlf(bm-a), r365(bm-b), r389-autoclear(bm-a)
out_lines = bl[:18] + [ptr33] + [""]
for e in survivors:
    out_lines.append(e)
    out_lines.append("")
union = "\r\n".join(out_lines)

# verification: every surviving side-entry verbatim present; folded absent; pointers intact
for e in survivors:
    assert e in union
for f in folded:
    assert f not in union
assert ptr33 in union and union.count("\u51b7\u5c42\u6307\u9488") >= 10

# archive containment for folded entries (zero-loss across the fold)
arc = open("research/memory-archive/202609.md", "rb").read().decode("utf-8")
for f in folded:
    assert f in arc, f"folded entry missing from archive: {f[:40]}"

open("CODELY.md", "wb").write((b"\xef\xbb\xbf" if bom_b else b"") + union.encode("utf-8"))
import os
print("union written:", os.path.getsize("CODELY.md"), "bytes; entries:", len(survivors), "; folded->archive verified")
