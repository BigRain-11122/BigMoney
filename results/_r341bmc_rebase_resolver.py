"""r341 bm-c rebase conflict resolver: post_review.jsonl (r294 union law) +
REPORT-20261002.md (r505 wall-clock-newest law). Zero global dedupe (r294)."""
import json
import re

P_JSONL = r"K:\Fluxgroup\FluxGroup\quant\bigmoney\results\post_review.jsonl"
P_MD = r"K:\Fluxgroup\FluxGroup\quant\bigmoney\results\post_review\REPORT-20261002.md"

b = open(P_JSONL, "rb").read().decode("utf-8", "replace").splitlines()
mk = [i for i, l in enumerate(b)
      if re.match(r"^(<{7} |\|{7} )", l) or l == "=" * 7 or re.match(r"^>{7} ", l)]
assert len(mk) == 4, f"expected exactly one diff3 conflict region, got {mk}"
a1, base, a2, a3 = mk
head_lines = b[a1 + 1: base]          # origin side new lines
mine_lines = b[a2 + 1: a3]           # our side new lines
print("head new:", len(head_lines), "| mine new:", len(mine_lines))

def ids(lines):
    out = []
    for l in lines:
        try:
            out.append(json.loads(l).get("id"))
        except Exception:
            out.append(None)
    return out

hid, mid = ids(head_lines), ids(mine_lines)
print("head ids:", hid[:8], "...", hid[-4:] if len(hid) > 8 else "")
print("mine ids:", mid[:8], "...", mid[-4:] if len(mid) > 8 else "")
# union: dedupe ONLY within the new-line zone, exact (id, content) pairs;
# identical id+content on both sides = the same appended row -> keep once.
seen, union = set(), []
for l in head_lines + mine_lines:
    key = l.strip()
    if key in seen:
        continue
    seen.add(key)
    union.append(l)
dup_id = [i for i in hid if hid.count(i) > 1] or [i for i in mid if mid.count(i) > 1]
print("union new lines:", len(union), "| exact-dup dropped:", len(head_lines) + len(mine_lines) - len(union))

out = b[:a1] + union + b[a3 + 1:]
open(P_JSONL, "w", encoding="utf-8", newline="\n").write("\n".join(out) + "\n")
# integrity: every line parses as JSON, no markers left
chk = open(P_JSONL, encoding="utf-8").read().splitlines()
assert not any(re.match(r"^(<{7} |\|{7}|={7}$|>{7} )", l) for l in chk), "marker left"
for l in chk:
    json.loads(l)
print("jsonl resolved:", len(chk), "lines, all parse OK")

# --- REPORT-20261002.md add/add: wall-clock newest (r505) -------------------
import subprocess
def side(rev):
    return subprocess.check_output(
        ["git", "-C", r"K:\Fluxgroup\FluxGroup\quant\bigmoney", "show", rev]
    ).decode("utf-8", "replace")
ours = side(":2:" + "results/post_review/REPORT-20261002.md")
theirs = side(":3:" + "results/post_review/REPORT-20261002.md")
ts = re.compile(r"20\d{2}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}")
o = max(ts.findall(ours) or [""])
t = max(ts.findall(theirs) or [""])
if ours == theirs:
    pick, why = theirs, "identical"
else:
    pick, why = (theirs, "origin-newer") if t >= o else (ours, "local-newer")
print("report ts local:", o, "origin:", t, "->", why)
open(P_MD, "w", encoding="utf-8", newline="\n").write(pick)
print("report resolved:", why, len(pick), "bytes")
