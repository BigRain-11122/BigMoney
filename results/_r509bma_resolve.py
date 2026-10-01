"""r509 bm-a carry-commit conflict resolve: pool_core_samples.jsonl
append-log union (r188 law -- line-level union of both blobs, dedupe
exact duplicate lines, zero loss)."""
import json
import os
import subprocess

R = "C:/Users/sjs20/Desktop/FluxGroup/quant/bmoney".replace("bmoney", "bigmoney")
P = "results/pool_core_samples.jsonl"

origin = subprocess.check_output(
    ["git", "-C", R, "show", f":2:{P}"]).decode("utf-8")
mine = subprocess.check_output(
    ["git", "-C", R, "show", f":3:{P}"]).decode("utf-8")

o_lines = [l for l in origin.split("\n") if l.strip()]
m_lines = [l for l in mine.split("\n") if l.strip()]
seen = set()
union = []
for l in o_lines + m_lines:
    if l in seen:
        continue
    seen.add(l)
    union.append(l)

# EOL face: probe origin blob
raw_o = subprocess.check_output(["git", "-C", R, "show", f":2:{P}"])
crlf = raw_o.count(b"\r\n") >= max(1, raw_o.count(b"\n")) // 2
sep = "\r\n" if crlf else "\n"
# trailing face
trail = raw_o.endswith(b"\n")
out = sep.join(union) + (sep if trail else "")

# verify: every line parses as JSON and row counts are a superset
for l in union:
    json.loads(l)
print("origin rows:", len(o_lines), "| mine rows:", len(m_lines),
      "| union rows:", len(union), "| crlf:", crlf, "| trail:", trail)
assert len(union) >= max(len(o_lines), len(m_lines)), "union lost rows"

fp = os.path.join(R, P)
with open(fp, "wb") as fh:
    fh.write(out.encode("utf-8"))
print("wrote", len(out), "bytes; parse-verified")
