"""r1077 bm-a UU resolver (versioned, fleet law):
- results/_r686bmb_d19_check.json : bm-b owned face -> origin verbatim (OURS = rebase base = origin/main tip)
- results/watermark_red.json     : watermark probe face -> ts newer-wins (local 10:39:03 bm-a > origin 10:18:03 bm-b) -> THEIRS
- results/paper/marks/marks-20261019.jsonl : append-only daily marks -> union both sides, dedupe full-line, sort by ts
Assert: zero conflict markers remain in all three files after resolve.
"""
import json
import re
import subprocess
import sys

MARK = re.compile(r"^(<{7}|={7}|>{7})")

def sh(*args):
    return subprocess.run(args, capture_output=True, text=True, encoding="utf-8", errors="replace")

def assert_no_markers(path):
    with open(path, "rb") as f:
        data = f.read().decode("utf-8", errors="replace")
    bad = [ln for ln in data.splitlines() if MARK.match(ln.strip())]
    if bad:
        print(f"MARKER-FAIL {path}: {len(bad)} marker lines remain")
        sys.exit(1)
    print(f"marker-clean {path}")

# 1) bm-b owned face: take origin (ours = rebase base)
r = sh("git", "checkout", "--ours", "--", "results/_r686bmb_d19_check.json")
print("d19 take-ours rc", r.returncode, r.stderr.strip())
assert_no_markers("results/_r686bmb_d19_check.json")
json.load(open("results/_r686bmb_d19_check.json", encoding="utf-8"))
print("d19 json valid")

# 2) watermark_red: newer-wins -> local face (theirs = commit being replayed)
r = sh("git", "checkout", "--theirs", "--", "results/watermark_red.json")
print("wm take-theirs rc", r.returncode, r.stderr.strip())
assert_no_markers("results/watermark_red.json")
wm = json.load(open("results/watermark_red.json", encoding="utf-8"))
print("wm face:", wm.get("ts"), wm.get("machine"), "red=", wm.get("red"))

# 3) marks-20261019.jsonl: union (ours=origin lines, theirs=local lines)
ours = sh("git", "show", ":2:results/paper/marks/marks-20261019.jsonl")
theirs = sh("git", "show", ":3:results/paper/marks/marks-20261019.jsonl")
o_lines = [ln for ln in ours.stdout.splitlines() if ln.strip()]
t_lines = [ln for ln in theirs.stdout.splitlines() if ln.strip()]
seen, rows = set(), []
for ln in o_lines + t_lines:
    key = ln.strip()
    if key in seen:
        continue
    seen.add(key)
    try:
        obj = json.loads(ln)
        rows.append((str(obj.get("ts", "")), ln))
    except json.JSONDecodeError:
        rows.append(("", ln))
rows.sort(key=lambda x: x[0])
out_path = "results/paper/marks/marks-20261019.jsonl"
with open(out_path, "w", encoding="utf-8", newline="\n") as f:
    for _, ln in rows:
        f.write(ln.rstrip("\r") + "\n")
print(f"marks union: ours={len(o_lines)} theirs={len(t_lines)} -> unique={len(rows)}")
assert_no_markers(out_path)

# stage all three
for p in ("results/_r686bmb_d19_check.json", "results/watermark_red.json", out_path):
    r = sh("git", "add", "--", p)
    if r.returncode != 0:
        print("add-fail", p, r.stderr.strip())
        sys.exit(1)
print("STAGED-OK all three")
