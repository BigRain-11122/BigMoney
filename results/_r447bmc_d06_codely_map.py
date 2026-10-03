# -*- coding: utf-8 -*-
"""r447 bm-c D-06 CODELY.md tail-heal reconnaissance (file-output law, r446).

Read-only. Dumps results/_r447bmc_d06_codely_map.json:
  - EOL census (CRLF/loneCR/loneLF triple-count identity law, r419/r420)
  - per-line: byte len, EOL kind, mojibake flag + cp936->utf8 round-trip recovery,
    readable-twin line number (normalized containment), entry-marker count
  - global: duplicate entry keys, merged-line defects, mojibake span
Zero writes to CODELY.md itself.
"""
import io, json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "CODELY.md")
OUT = os.path.join(ROOT, "results", "_r447bmc_d06_codely_map.json")

raw = open(SRC, "rb").read()
crlf = raw.count(b"\r\n")
cr = raw.count(b"\r")
lf = raw.count(b"\n")
lone_cr = cr - crlf
lone_lf = lf - crlf

# split preserving EOLs
lines = []  # (text_without_eol, eol_bytes)
pos = 0
for m in re.finditer(rb"\r\n|\r|\n", raw):
    lines.append((raw[pos:m.start()].decode("utf-8", "replace"),
                  raw[m.start():m.end()].decode("latin-1")))
    pos = m.end()
if pos < len(raw):
    lines.append((raw[pos:].decode("utf-8", "replace"), ""))

def recover(text):
    """cp936 round-trip: mojibake_str.encode(cp936) == original utf8 bytes."""
    try:
        b = text.encode("cp936")
        rec = b.decode("utf-8")
        if rec != text:
            return rec
    except (UnicodeEncodeError, UnicodeDecodeError):
        pass
    return None

MARKER = re.compile(r"-\s*\[\d{4}-\d{2}-\d{2}[^\]]{0,40}\]")
KEY = re.compile(r"\[(\d{4}-\d{2}-\d{2}(?:[ \d:x]*)?)\][^]*?\br(\d{3})\b[^]*?\b(bm-[abc])\b")

norm = lambda s: re.sub(r"\s+", "", s)
readable_norms = {i: norm(t) for i, (t, _) in enumerate(lines, 1)}

recs = []
moji_rows = []
key_seen = {}
merged = []
for i, (t, eol) in enumerate(lines, 1):
    rec = recover(t)
    markers = MARKER.findall(t)
    row = {"n": i, "bytes": len(t.encode("utf-8")) + len(eol), "eol": eol.replace("\r\n", "CRLF").replace("\r", "CR").replace("\n", "LF"),
           "mojibake": rec is not None, "markers": len(markers)}
    if rec is not None:
        # twin search: normalized recovered text matched inside any readable line
        rn = norm(rec)
        twin = None
        for j, nrm in readable_norms.items():
            if j == i:
                continue
            if not lines[j-1][1] == lines[j-1][1]:
                pass
            tj = lines[j-1][0]
            if recover(tj) is not None:
                continue  # skip other mojibake lines as twins
            if rn and (rn in nrm or nrm in rn) and len(rn) >= 20:
                twin = j
                break
        row["twin"] = twin
        row["recovered_len"] = len(rec)
        moji_rows.append((i, twin, rec))
    if len(markers) >= 2:
        merged.append(i)
    for mk in markers:
        # extract rough key: date + rNNN + machine
        m2 = re.search(r"(\d{4}-\d{2}-\d{2})", mk)
        seg = t[max(0, t.find(mk)): t.find(mk) + 120]
        m3 = re.search(r"r(\d{3})", seg)
        m4 = re.search(r"bm-([abc])", seg)
        if m2 and m3 and m4:
            k = (m2.group(1), "r" + m3.group(1), "bm-" + m4.group(1))
            key_seen.setdefault(k, []).append(i)
    recs.append(row)

dups = {str(k): v for k, v in key_seen.items() if len(v) > 1}

report = {
    "file": "CODELY.md",
    "total_bytes": len(raw),
    "eol": {"crlf": crlf, "lone_cr": lone_cr, "lone_lf": lone_lf},
    "n_lines": len(lines),
    "mojibake_lines": [r[0] for r in moji_rows],
    "mojibake_with_twin": {str(i): twin for i, twin, _ in moji_rows},
    "mojibake_no_twin": [i for i, twin, _ in moji_rows if twin is None],
    "merged_marker_lines": merged,
    "duplicate_entry_keys": dups,
    "line_map": recs,
    "recovered_preview": {str(i): rec[:180] for i, twin, rec in moji_rows},
}
with io.open(OUT, "w", encoding="utf-8", newline="\n") as f:
    json.dump(report, f, ensure_ascii=False, indent=1)
print("MAP-WRITTEN bytes=%d crlf=%d lone_cr=%d lone_lf=%d moji=%d no_twin=%s merged=%s dups=%s" % (
    len(raw), crlf, lone_cr, lone_lf, len(moji_rows),
    [i for i, twin, _ in moji_rows if twin is None], merged, list(dups)[:8]))
