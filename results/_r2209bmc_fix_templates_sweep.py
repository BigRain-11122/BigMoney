"""r2209 (c): finish the template-leak repair across the whole report.

(a) repaired the r2208 row, (b) repaired the three older rows whose head was a
literal placeholder. A file-wide sweep shows the same writer leaked 13 rows:
8 heads reading "| %s |", one round column "%d", and a few tokens inside prose.

Rule used here -- never invent a number:
  * a lost timestamp becomes "(ts-lost · 行由 <sha> 落盘)" where <sha> is git
    blame's commit for that exact line (precedent: the r1303 row already says
    "ts-lost");
  * a lost round becomes "(round-lost)";
  * a token stranded inside prose becomes "(值丢失)".
"""
import io
import re
import subprocess

P = "round_reports-bm-c.md"
TOKEN = re.compile(r"%(?:s|d)")


def blame_sha(line_no):
    out = subprocess.run(
        ["git", "blame", "-L", "%d,%d" % (line_no, line_no), "--porcelain", "--", P],
        capture_output=True, text=True, encoding="utf-8", errors="replace")
    first = (out.stdout or "").split("\n", 1)[0].strip()
    return first.split(" ")[0][:7] if first else "unknown"


s = io.open(P, encoding="utf-8", newline="").read()
lines = s.split("\n")

changed = []
for i, raw in enumerate(lines):
    had_cr = raw.endswith("\r")
    body = raw[:-1] if had_cr else raw
    if not body.startswith("|") or not TOKEN.search(body):
        continue

    orig = body

    if body.startswith("| %s |"):
        sha = blame_sha(i + 1)
        body = "| (ts-lost · 行由 %s 落盘) |" % sha + body[len("| %s |"):]

    # the column right after the head may be a lost round number
    body = re.sub(r"^\| \(ts-lost · 行由 [0-9a-z]+ 落盘\) \| %d \|",
                  lambda m: m.group(0).replace("%d", "(round-lost)"), body)
    body = re.sub(r"^\| \(ts-lost · 行由 [0-9a-z]+ 落盘\) \| %d",
                  lambda m: m.group(0).replace("%d", "(round-lost)"), body)

    if TOKEN.search(body):
        body = TOKEN.sub("(值丢失)", body)

    if body != orig:
        lines[i] = body + ("\r" if had_cr else "")
        changed.append(i + 1)

io.open(P, "w", encoding="utf-8", newline="").write("\n".join(lines))
print("rows repaired:", changed)

# ---- verify ----
s2 = io.open(P, encoding="utf-8", newline="").read()
left = [(i, l.rstrip("\r")[:90]) for i, l in enumerate(s2.split("\n"), 1)
        if l.startswith("|") and ("%s" in l or "%d" in l or "%%" in l)]
print("table rows still carrying a placeholder:", left)
