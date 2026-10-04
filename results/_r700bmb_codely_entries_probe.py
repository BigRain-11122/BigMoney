# r700 bm-b: enumerate CODELY.md entries with section attribution (surgical plan input)
import re, json

text = open("CODELY.md", "rb").read().decode("utf-8")
lines = text.split("\n")
sec = "preamble"
entries = []
cur = None
sec_bytes = {}
for i, ln in enumerate(lines):
    if ln.startswith("### "):
        if cur: entries.append(cur)
        cur = None
        sec = ln[4:].strip()
        sec_bytes.setdefault(sec, 0)
        continue
    if ln.startswith("## "):
        if cur: entries.append(cur); cur = None
        sec = ln[3:].strip()
        sec_bytes.setdefault(sec, 0)
        continue
    sec_bytes[sec] = sec_bytes.get(sec, 0) + len((ln + "\n").encode("utf-8"))
    if re.match(r"^- \[", ln) and sec in ("Project", "Reference"):
        if cur: entries.append(cur)
        cur = {"section": sec, "start_line": i + 1, "header": ln[:80]}
if cur: entries.append(cur)

# compute entry byte spans (start line to next entry start or EOF)
res = []
for k, e in enumerate(entries):
    end = entries[k + 1]["start_line"] - 1 if k + 1 < len(entries) else len(lines)
    nb = len(("\n".join(lines[e["start_line"] - 1:end]) + "\n").encode("utf-8"))
    m = re.match(r"- \[(\d{4}-\d{2}-\d{2})[^\]]*\]\s*(.{0,40})", e["header"])
    res.append({"sec": e["section"], "line": e["start_line"], "bytes": nb,
                "day": m.group(1) if m else "?", "hdr": (m.group(2) if m else e["header"])[:46]})
out = {"sections_bytes": sec_bytes, "n_proj_ref_entries": len(res),
       "entries": res}
open("results/_r700bmb_codely_entries.json", "w", encoding="utf-8").write(json.dumps(out, ensure_ascii=False, indent=1))
print("sections:", {k: v for k, v in sec_bytes.items()})
tot = {}
for e in res:
    tot[e["day"]] = tot.get(e["day"], 0) + e["bytes"]
print("proj/ref entry bytes by day:", tot)
print("n entries:", len(res))
