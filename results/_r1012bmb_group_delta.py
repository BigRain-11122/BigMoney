"""r1012 bm-b: group orders/decisions delta extractor (D-19 fresh-delta consume leg).
Reads origin blobs via git show, BOM-detects encoding, writes clean UTF-8 faces,
and isolates rows newer than my consumed watermark (orders 193095774d consumed
content up to 2026-10-18 21:11 rows; decisions 4cfdd17c held at 23:07 probe).
Writes results/_r1012bmb_group_delta.json + two .txt faces for reading."""
import io
import json
import re
import subprocess

GRP = r"C:\Fluxgroup\FluxGroup"


def blob(path):
    r = subprocess.run(["git", "-C", GRP, "show", "origin/main:" + path],
                       capture_output=True, timeout=120)
    if r.returncode != 0:
        raise RuntimeError("git show failed: %r" % r.stderr[:200])
    return r.stdout


def decode(b):
    if b.startswith(b"\xff\xfe") or b.startswith(b"\xfe\xff"):
        return b.decode("utf-16", "replace"), "utf-16(BOM)"
    try:
        return b.decode("utf-8"), "utf-8"
    except UnicodeDecodeError:
        return b.decode("utf-8", "replace"), "utf-8(replace)"


out = {}
for name, path in (("orders", "docs/orders.md"), ("decisions", "docs/decisions.md")):
    b = blob(path)
    text, enc = decode(b)
    lines = text.splitlines()
    face = "results/_r1012bmb_group_%s_face.txt" % name
    with io.open(face, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    # collect recent rows: any line whose visible ts is 2026-10-18 22:xx/23:xx,
    # plus (for orders) any line mentioning BigMoney/quant/bm-b that is dated 10-18
    recent = []
    for ln in lines:
        if re.search(r"2026-10-18\s*2[23]:", ln):
            recent.append(ln)
    out[name] = {"encoding": enc, "total_lines": len(lines), "recent_22_23_rows": len(recent)}
    with io.open("results/_r1012bmb_group_%s_recent.txt" % name, "w", encoding="utf-8") as f:
        f.write("\n\n".join(recent))
    # tail 40 lines for context (chronology check)
    out[name]["tail_first_line"] = lines[-1][:120] if lines else ""
    out[name]["tail_last_line"] = lines[0][:120] if lines else ""

with io.open("results/_r1012bmb_group_delta.json", "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
print(json.dumps(out, ensure_ascii=False, indent=1))
