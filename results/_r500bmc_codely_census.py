# r500 bm-c: CODELY.md structural census for hot/cold re-archival planning.
# Laws: r415 (block-boundary/dual-form/ASCII-anchor), r417 variant-5 (bullet-less date lines),
# r675 (block-level union, structural dupes), r446 (probe-as-file).
# Read-only analysis; writes results/_r500bmc_codely_census.json + txt summary.
import hashlib, json, re

REPO = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
PATH = REPO + r"\CODELY.md"

with open(PATH, "rb") as f:
    raw = f.read()

# EOL census (r402 double-count law: count via line-split canon)
eol_crlf = raw.count(b"\r\n")
eol_lf_total = raw.count(b"\n")
eol_lone_cr = raw.count(b"\r") - eol_crlf

text = raw.decode("utf-8", "replace")
lines = text.split("\n")

HEAD = re.compile(r"^## Codely Structured Memories")
SECT = re.compile(r"^### (User|Feedback|Project|Reference)\s*$")
# entry starts: bullet or bullet-less date form, or domain/cold pointer bullets
ENTRY = re.compile(r"^(?:- )?(?:\[(?:20\d\d)-[0-9]{2}-[0-9]{2}[^\]]*\]|域指针|冷层指针|坑律正典全量归档)")

entries = []  # (start_line, end_line, first_60, nbytes)
cur = None
sections = []  # (line_no, header)
for i, ln in enumerate(lines):
    if HEAD.match(ln) or SECT.match(ln):
        sections.append((i + 1, ln.strip()))
    if ENTRY.match(ln):
        if cur:
            entries.append(cur)
        cur = [i + 1, i + 1, ln.strip()[:70], len(ln.encode("utf-8"))]
    elif cur:
        # blank line = entry terminator; non-blank continuation extends entry
        if ln.strip() == "":
            entries.append(cur)
            cur = None
        else:
            cur[1] = i + 1
            cur[3] += len(ln.encode("utf-8"))
if cur:
    entries.append(cur)

# exact-duplicate entry detection (first-line key + byte size)
from collections import Counter
keys = Counter((e[2], e[3]) for e in entries)
dupes = {k: c for k, c in keys.items() if c > 1}

# receipt-type detection (flow/receipt markers in first line)
receipt_markers = ("回执", "执行记录", "收口窗批", "落地行", "交付行", "烧批回执")
receipts = [e for e in entries if any(m in e[2] for m in receipt_markers)]

census = {
    "total_bytes": len(raw),
    "total_lines_phys": len(lines),
    "eol": {"crlf": eol_crlf, "lf_total": eol_lf_total, "lone_cr": eol_lone_cr},
    "md5": hashlib.md5(raw).hexdigest(),
    "section_headers": sections,
    "entry_count": len(entries),
    "exact_dup_entries": {str(k): v for k, v in dupes.items()},
    "receipt_like_entries": [(e[0], e[2]) for e in receipts],
    "entries": [
        {"lines": "%d-%d" % (e[0], e[1]), "bytes": e[3], "head": e[2]} for e in entries
    ],
}
with open(REPO + r"\results\_r500bmc_codely_census.json", "w", encoding="utf-8") as f:
    json.dump(census, f, ensure_ascii=False, indent=1)

summary = {
    "bytes": len(raw),
    "lines": len(lines),
    "eol": census["eol"],
    "md5": census["md5"],
    "headers": ["L%d %s" % (a, b) for a, b in sections],
    "entry_count": len(entries),
    "dup_count": len(dupes),
    "receipt_like": len(receipts),
}
with open(REPO + r"\results\_r500bmc_codely_census_summary.txt", "w", encoding="utf-8") as f:
    json.dump(summary, f, ensure_ascii=False, indent=1)
print("CENSUS-OK " + json.dumps(summary, ensure_ascii=False))
