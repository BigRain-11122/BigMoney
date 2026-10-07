"""r693 bm-c S7 tripwire scan (E09 law face): round-report ledger header
count, long-line multiplicity (>=4 dup groups), line count. CLEAN =
header x1 + zero dup groups. Attrition guard scan follows. Facts ->
stdout + results/_attrition_guard_scan.json (by the guard script)."""
import collections
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RR = os.path.join(ROOT, "logs", "iteration-loop", "round_reports-bm-c.md")

raw = open(RR, "rb").read()
txt = raw.decode("utf-8", errors="replace")
lines = txt.splitlines()
header = lines[0].strip() if lines else ""
header_count = sum(1 for l in lines if l.strip() == header and header)
# long-line multiplicity: lines >=200 chars with identical content
long_lines = [l for l in lines if len(l) >= 200]
dup_groups = {l: c for l, c in collections.Counter(long_lines).items() if c >= 4}
print("== tripwire:", {
    "file": "round_reports-bm-c.md",
    "bytes": len(raw),
    "lines": len(lines),
    "header_count": header_count,
    "long_line_dup_groups": len(dup_groups),
})
verdict = "CLEAN" if header_count <= 1 and not dup_groups else "ACTIVE"
print("== tripwire verdict:", verdict)
for k in list(dup_groups)[:3]:
    print("   dup sample:", k[:120])
