# -*- coding: utf-8 -*-
"""r402 bm-c direct-write #2: EOL-surgery pit -> research/pit-git.md tail +
CODELY git-pointer line r402 note. Corrected line semantics (content slice
excludes terminator bytes; CRLF content ends BEFORE the CR), plus the two
post-write laws from the incident itself: lone-CR==0 and staged-diff line
count == expected set."""
import os
import sys

ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
PITGIT = os.path.join(ROOT, "research", "pit-git.md")
CODELY = os.path.join(ROOT, "CODELY.md")


def die(m):
    print(f"ABORT: {m}")
    sys.exit(1)


def lone_crs(data):
    return [i for i in range(len(data))
            if data[i:i + 1] == b"\r" and data[i + 1:i + 2] != b"\n"]


ENTRY = (
    "- [2026-10-03 07:4x r402 bm-c] "
    "\u5b57\u8282\u624b\u672f\u884c\u754c\u7ec8\u7ed3\u7b26\u53cc\u8ba1"
    "\u00d7\u5b64 CR \u6291\u5236 git \u6e05\u6ee4=\u6574\u6587\u4ef6 "
    "staged diff \u53cc\u5751\uff08CODELY/pit-pool \u589e\u91cf\u626b"
    "\u5b9e\u5f39\u00b7\u65ad\u8a00\u94fe\u5f53\u573a\u62e6\u622a\u96f6 "
    "origin \u4f24\u5bb3\u00b7post-split direct-write\uff09\uff1a\u2460"
    "\u884c\u754c helper \u4ee5 find(b'\\n') \u5b9a\u884c\u5c3e\u65f6 "
    "CRLF \u884c\u7684 \\r \u843d\u5728\u5185\u5bb9\u5207\u7247 "
    "[start,end) \u5185\u2014\u2014\u518d\u6309 term=b'\\r\\n' \u7b97"
    "\u63d2\u5165\u70b9/\u5220\u9664\u8de8\u5ea6=+1 \u5b57\u8282\u6ea2"
    "\u51fa\uff1a\u5220\u9664\u591a\u5403\u6b21\u884c\u9996\u5b57\u8282"
    "\uff08blank \u884c \\r\\n \u6ca6 \\n\uff09\u3001\u63d2\u5165\u70b9"
    "\u8df3\u8fc7\u6b21\u884c\u9996\u5b57\u8282\uff08\u5b64 \\r\\n\\r "
    "\u4e09\u8fde\u73b0\u5f62\uff09\uff1b\u2461\u5de5\u4f5c\u6811\u542b"
    "\u5b64 CR\uff08\\r \u540e\u975e \\n\uff09=git autocrlf \u6e05\u6ee4"
    "\u9759\u9ed8\u6291\u5236\u2014\u2014add \u540e index \u6301 CRLF "
    "\u539f\u6837\u2192staged diff \u6574\u6587\u4ef6\u7ffb\u9762\uff08"
    "54/54 \u884c\u00b7\u5185\u5bb9\u9010\u884c\u6052\u7b49\u4ec5\u884c"
    "\u5c3e\u5dee\uff09\u00b7add --renormalize \u540c\u62d2\uff08lone "
    "CR=\u8f6c\u6362\u4e0d\u5b89\u5168\u5224\u636e\uff09\uff1b\u540c"
    "\u7a97 T-147 json \u96f6\u5b64 CR \u5373\u6b63\u5e38\u5f52\u4e00"
    "\uff084 \u884c\u5916\u79d1\uff09=\u5bf9\u7167\u7ec4\u5b9e\u8bc1"
    "\u3002\u4fee\u6cd5=lone_crs \u626b\u63cf\uff08\\r \u975e\u968f "
    "\\n\uff09\u5b9a\u4f4d+\u5220\u5355\u5b57\u8282+\u590d add \u540e "
    "diff --cached --stat \u884c\u6570==\u9884\u671f\u96c6\uff08CODELY "
    "4 \u884c/pit-pool 3 \u884c\u5168\u4e2d\uff09\u3002How to apply"
    "\uff1a\u884c\u754c\u5b57\u8282\u624b\u672f helper \u884c\u5185\u5bb9"
    "\u5207\u7247\u7981\u542b\u7ec8\u7ed3\u7b26\u5b57\u8282\uff08CRLF "
    "\u5185\u5bb9\u6b62\u4e8e \\r \u524d\u00b7\u7ec8\u7ed3\u7b26 "
    "[end-1,end+1)\uff09\uff1b\u63d2\u5165\u70b9=end+1 \u7981 end+len"
    "(term)\uff1b\u5199\u540e\u53cc\u9a8c=lone CR==0+staged diff \u884c"
    "\u6570==\u9884\u671f\uff1b\u6574\u6587\u4ef6\u7ffb\u9762\u4e14"
    "\u5185\u5bb9\u672a\u53d8\u5148\u67e5\u5b64 CR \u52ff\u7591\u7f16"
    "\u8f91\u5668\u52ff\u91cd\u505a\u624b\u672f\u3002"
).encode("utf-8")

# ---- pit-git.md tail append ----
pg = open(PITGIT, "rb").read()
if ENTRY[:60] in pg:
    die("entry already present (idempotence)")
if not pg.endswith(b"\n"):
    die("pit-git.md does not end with newline -- unexpected")
dominant_crlf = pg.count(b"\r\n") * 2 > pg.count(b"\n")
term = b"\r\n" if dominant_crlf else b"\n"
pg_new = pg + b"\n" + ENTRY + term   # blank separator line + entry
if lone_crs(pg_new):
    die("post-append lone CR present")

# ---- CODELY git-pointer line scoped edit ----
cd = open(CODELY, "rb").read()
anchor = b"research/pit-git.md"
pos = cd.find(anchor)
if pos < 0:
    die("git pointer line missing")
ls = cd.rfind(b"\n", 0, pos) + 1
le = cd.find(b"\n", pos)
line = cd[ls:le]
tail_seg = "\u5df2\u5165\u4ef6\uff08\u4ef6\u5185\u5bf9\u8d26\u884c\u4e3a" \
           "\u51c6\uff09\u3002".encode("utf-8")
if line.count(tail_seg) < 1 or b"r401" not in line:
    die("git pointer line layout drift")
last = line.rfind(tail_seg)
new_line = (line[:last] + line[last:].replace(
    tail_seg,
    ("\u5df2\u5165\u4ef6\uff08\u4ef6\u5185\u5bf9\u8d26\u884c\u4e3a\u51c6"
     "\uff09\uff1br402 bm-c direct-write 1 \u6761\uff08\u5b57\u8282\u624b"
     "\u672f\u884c\u754c\u7ec8\u7ed3\u7b26\u53cc\u8ba1\u00d7\u5b64 CR "
     "\u6291\u5236\u6e05\u6ee4=\u6574\u6587\u4ef6 staged diff\u00b7\u5f53"
     "\u573a\u81ea\u6108\u96f6 origin \u4f24\u5bb3\uff09\u5df2\u5165"
     "\u4ef6\uff08\u4ef6\u5185\u5bf9\u8d26\u884c\u4e3a\u51c6\uff09\u3002"
     ).encode("utf-8"), 1))
cd_new = cd[:ls] + new_line + cd[le:]
if lone_crs(cd_new):
    die("post-edit CODELY lone CR present")

open(PITGIT + ".tmp", "wb").write(pg_new)
os.replace(PITGIT + ".tmp", PITGIT)
open(CODELY + ".tmp", "wb").write(cd_new)
os.replace(CODELY + ".tmp", CODELY)
print(f"pit-git.md: {len(pg)}B -> {len(pg_new)}B (+{len(ENTRY) + len(term) + 1})"
      f" term={'CRLF' if dominant_crlf else 'LF'}")
print(f"CODELY.md: {len(cd)}B -> {len(cd_new)}B "
      f"(ptr +{len(new_line) - len(line)}B)")
print("DIRECT-WRITE OK")
