# r500 bm-c: byte-identity debug probe (no writes).
import hashlib, json
from collections import Counter

REPO = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
with open(REPO + r"\CODELY.md", "rb") as f:
    raw = f.read()
text = raw.decode("utf-8")
lines = text.split("\r\n")
assert lines[-1] == ""

def B(s):
    return len(s.encode("utf-8"))

out = []
deleted = []
blank_run = 0
for idx, ln in enumerate(lines[:-1], start=1):
    if idx == 87:
        deleted.append(ln); out.append("PTR"); continue
    if idx in (155, 167):
        deleted.append(ln); continue
    if 103 <= idx <= 107:
        deleted.append(ln); continue
    if ln.strip() == "":
        blank_run += 1
        if blank_run >= 2:
            continue
        out.append(ln)
    else:
        blank_run = 0
        out.append(ln)

blanks_pre = sum(1 for x in lines[:-1] if x.strip() == "")
blanks_post = sum(1 for x in out if x.strip() == "")
hdr_content_sum = sum(B(lines[102 + i]) for i in range(5))
ptr = 200
expected = len(raw) - (B(deleted[0]) + B(deleted[1]) + B(deleted[2]) + hdr_content_sum) + ptr \
           - 2 * (len(deleted) + (blanks_pre - blanks_post))
actual = sum(B(x) for x in out) + 2 * len(out)
# NOTE: out currently holds "PTR" placeholder; recompute with real pointer separately
print(json.dumps({
    "pre_bytes": len(raw),
    "pre_phys_lines": len(lines) - 1,
    "out_lines": len(out),
    "expected_out_lines": len(lines) - 1 - len(deleted) - (blanks_pre - blanks_post),
    "deleted_count": len(deleted),
    "blanks_pre": blanks_pre,
    "blanks_post": blanks_post,
    "blank_delta": blanks_pre - blanks_post,
    "hdr_content_sum": hdr_content_sum,
    "sum_out_content_bytes": sum(B(x) for x in out),
    "sum_out_plus_eol": sum(B(x) for x in out) + 2 * len(out),
    "expected_formula": expected,
    "deleted_heads": [d[:30] for d in deleted],
}, ensure_ascii=False))
