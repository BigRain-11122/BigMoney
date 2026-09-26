"""r268 bm-a: repo-root CODELY.md hot-cold recompile, morning-batch (D-20260924-01 paradigm,
R156 dated-batch precedent + bm-b r272/r273 marker-batch precedent).

Watermark discipline (D-20260925-01(4)): CODELY.md at 51,362 bytes after the R268
pit-law append (over the 51,200B=50KiB line; bm-b r272 trigger precedent 51,257B).
Flow-marker lines are exhausted (r273 moved them), so this batch archives the dated
morning-batch lesson entries (09:xx-14:xx) verbatim into research/memory-archive/
202609.md under a dated section header. Zero line loss verified by exact multiset.

Step 0 repairs the R268 append escape corruption: python -c string turned the
intended literal \\fluxgroup into \\x0c form-feed (exactly one occurrence expected).
Byte-face law (R254/R255/R257): both files probed = UTF-8, no BOM, LF-only.
"""
import re, sys

HOT = "CODELY.md"
COLD = "research/memory-archive/202609.md"

def die(msg, code):
    print(msg)
    sys.exit(code)

def faces(b):
    return {"bom": b[:3] == b"\xef\xbb\xbf", "crlf": b.count(b"\r\n"), "trailing_nl": b.endswith(b"\n")}

hot_b = open(HOT, "rb").read()
cold_b = open(COLD, "rb").read()
for name, b in (("CODELY.md", hot_b), ("archive", cold_b)):
    f = faces(b)
    if f["bom"] or f["crlf"]:
        die(f"unexpected byte face on {name}: BOM={f['bom']} CRLF={f['crlf']}", 1)

# step 0: form-feed repair (python -c escape corruption, self-caught same round)
n_ff = hot_b.count(b"\x0c")
if n_ff != 1:
    die(f"form-feed count {n_ff} != 1 (unexpected face, abort)", 1)
hot_b = hot_b.replace(b"\x0c", b"\\f")
if b"\x0c" in hot_b:
    die("form-feed still present after repair", 1)

hot_txt = hot_b.decode("utf-8")
hot_lines = hot_txt.split("\n")
pat = re.compile(r"\[2026-09-26 (09|1[0-4]):")
moved = [L for L in hot_lines if pat.search(L[:40]) and "\u5751\u5f8b" in L]
if not moved:
    die("zero morning-batch lines found (already recompiled?)", 2)
kept = [L for L in hot_lines if not (pat.search(L[:40]) and "\u5751\u5f8b" in L)]
if sorted(hot_lines) != sorted(kept + moved):
    die("multiset verification FAILED pre-write (kept+moved != original)", 1)

header = [
    "## \u51b7\u5c42\u5f52\u6863\u589e\u91cf\u00b7r268 \u6279\uff1arepo \u6839 CODELY.md \u70ed\u51b7\u6574\u7f16\uff08D-20260924-01\u00b7bm-a R268\u00b72026-09-26\uff09",
    "\u8d8a\u7ebf\u5373\u529e\u6574\u7f16\uff08R268 \u5751\u5f8b\u8ffd\u52a0\u540e 51,362B \u8d8a 51,200B=50KiB \u7ebf\u00b7bm-b r272 \u5148\u4f8b 51,257B \u89e6\u53d1\uff09\uff1a\u4ee5\u4e0b "
    + str(len(moved))
    + " \u884c\u4e3a 2026-09-26 \u6668\u6279\uff0809:xx-14:xx\uff09\u5751\u5f8b\u6761\u76ee\uff0c\u81ea\u70ed\u5c42\u79fb\u5165\u672c\u51b7\u5c42\uff0c\u96f6\u4e22\u5931\uff08\u884c\u7ea7 multiset \u6821\u9a8c PASS\uff0cbm-a R268\uff09\u3002\u68c0\u7d22\u6309\u884c\u9996\u65e5\u671f\u6bb5\u3002",
]
cold_txt = cold_b.decode("utf-8")
if not cold_txt.endswith("\n"):
    die("archive lacks trailing newline before append -- face changed, abort", 1)
block = "\n".join(header + moved) + "\n"

with open(HOT, "wb") as f:
    f.write("\n".join(kept).encode("utf-8"))
with open(COLD, "wb") as f:
    f.write((cold_txt + block).encode("utf-8"))

hot_b2 = open(HOT, "rb").read()
cold_b2 = open(COLD, "rb").read()
hot_lines2 = hot_b2.decode("utf-8").split("\n")
cold_lines2 = cold_b2.decode("utf-8").split("\n")
g1 = sorted(hot_lines) == sorted(hot_lines2 + moved)
g2 = all(L in cold_lines2 for L in moved)
f2, f3 = faces(hot_b2), faces(cold_b2)
g3 = (not f2["bom"]) and f2["crlf"] == 0 and f2["trailing_nl"] == faces(hot_b)["trailing_nl"]
g4 = (not f3["bom"]) and f3["crlf"] == 0
g5 = b"\x0c" not in hot_b2
if not (g1 and g2 and g3 and g4 and g5):
    die(f"POST-WRITE GATE FAILED g1={g1} g2={g2} g3={g3} g4={g4} g5={g5}", 1)

print(f"recompile PASS: moved {len(moved)} morning-batch lines, form-feed repaired")
print(f"CODELY.md {len(hot_b)} -> {len(hot_b2)} bytes ({round(len(hot_b2)/1024, 1)} KiB)")
print(f"archive {len(cold_b)} -> {len(cold_b2)} bytes")
print(f"gates: multiset-zero-loss={g1} verbatim-in-cold={g2} hot-face={g3} cold-face={g4} ff-repaired={g5}")
