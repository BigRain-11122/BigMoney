# r700 bm-b: CODELY.md main-file rebound composition probe (D-20261002-06 open leg)
# Classify top-level bullet entries under Project/Reference sections by date prefix + estimate bytes per class.
import re, os, json

P = "CODELY.md"
b = open(P, "rb").read()
text = b.decode("utf-8", errors="strict")
lines = text.split("\n")
total = len(b)

# find entry-start lines: "- [date ...]" or "- [2026-..." pattern (bullet entries with bracketed date)
entry_re = re.compile(r"^- \[")
entries = []  # (line_idx, header)
for i, ln in enumerate(lines):
    if entry_re.match(ln):
        entries.append(i)

# classify each entry by first 30 chars of header
def classify(hdr):
    h = hdr.lower()
    if "冷层指针" in hdr or "域指针" in hdr:
        return "pointer"
    return "dated_entry"

sizes = {"pointer": 0, "dated_entry": 0}
dated_detail = {}
entry_bounds = []
for k, i in enumerate(entries):
    end = entries[k+1] if k+1 < len(entries) else len(lines)
    chunk = "\n".join(lines[i:end])
    nbytes = len(chunk.encode("utf-8"))
    hdr = lines[i][:60]
    cls = classify(lines[i])
    sizes[cls] += nbytes
    entry_bounds.append((i, end, nbytes, cls))
    if cls == "dated_entry":
        m = re.match(r"- \[(\d{4}-\d{2}-\d{2})", lines[i])
        day = m.group(1) if m else "?"
        dated_detail[day] = dated_detail.get(day, 0) + nbytes

# non-entry overhead (headers, User/Feedback sections before first entry etc.)
head = "\n".join(lines[:entries[0]]) if entries else ""
res = {
  "probe": "r700bmb_codely_rebound",
  "total_bytes": total,
  "r468bmc_measurement_1206": 62651,
  "rebound_delta_since_1206": total - 62651,
  "sizes": sizes,
  "overhead_bytes": len(head.encode("utf-8")),
  "n_entries": len(entries),
  "dated_bytes_by_day": dated_detail,
  "law": "D-20261002-06 ①主件 ≤30KB（10-04 梳理窗续压 ≤10KB）·memory.md >50KB 当窗即办热冷整编",
  "verdict_main": "FAIL vs 30KB budget" if total > 30000 else "PASS",
}
open("results/_r700bmb_codely_rebound.json", "w", encoding="utf-8").write(json.dumps(res, ensure_ascii=False, indent=1))
print(json.dumps(res, ensure_ascii=False, indent=1)[:800])
