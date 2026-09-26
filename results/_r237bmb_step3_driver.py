# -*- coding: utf-8 -*-
# r237 bm-b rebase step-3 resolver: autofill mixed / post_review.jsonl union / REPORT take-new
import subprocess, json, io, os, sys, re
sys.path.insert(0, os.environ["TEMP"])
from r237b_replay_resolver import resolve_autofill, probe

REPO = r"C:\Users\Administrator\Desktop\Bigmoney"

def stage(p, n):
    b = subprocess.run(["git", "show", f":{n}:{p}"], capture_output=True, cwd=REPO).stdout
    assert b, f"stage {n} empty {p}"
    return b

def to_temp(p, n):
    q = os.path.join(os.environ["TEMP"], "r237s3_" + str(n) + "_" + p.replace("/", "_"))
    open(q, "wb").write(stage(p, n))
    return q

# 1) autofill mixed recipe
p = "results/autofill_state.json"
r = resolve_autofill(to_temp(p, 2), to_temp(p, 3), os.path.join(REPO, p))
print("autofill:", r)

# 2) post_review.jsonl line-level union zero-loss
p = "results/post_review.jsonl"
A = [l for l in io.open(to_temp(p, 2), encoding="utf-8-sig").read().splitlines() if l.strip()]
B = [l for l in io.open(to_temp(p, 3), encoding="utf-8-sig").read().splitlines() if l.strip()]
seen = set(); lines = []
for l in A + B:
    if l not in seen:
        seen.add(l); lines.append(l)
base = stage(p, 2)
crlf = base.count(b"\r\n") > (base.count(b"\n") - base.count(b"\r\n"))
nl = "\r\n" if crlf else "\n"
open(os.path.join(REPO, p), "wb").write((nl.join(lines) + nl).encode("utf-8"))
back = [l for l in io.open(os.path.join(REPO, p), encoding="utf-8-sig").read().splitlines() if l.strip()]
for l in back[-3:]:
    json.loads(l)
print("post_review.jsonl:", len(A), "|", len(B), "->", len(back), "union; tail rows parse OK")

# 3) REPORT-20260926.md take-new by generated ts
p = "results/post_review/REPORT-20260926.md"
a = stage(p, 2).decode("utf-8", errors="replace")
b = stage(p, 3).decode("utf-8", errors="replace")
ma = re.search(r"(2026-09-26 [\d:]+)", a); mb = re.search(r"(2026-09-26 [\d:]+)", b)
ta = ma.group(1) if ma else ""; tb = mb.group(1) if mb else ""
pick = b if tb > ta else a
raw = pick
# newline mirror: probe the file in repo (conflicted worktree has markers; use stage bytes)
base = stage(p, 2)
crlf = base.count(b"\r\n") > (base.count(b"\n") - base.count(b"\r\n"))
if crlf and "\r\n" not in raw:
    raw = raw.replace("\n", "\r\n")
open(os.path.join(REPO, p), "wb").write(raw.encode("utf-8"))
print("REPORT:", ta, "vs", tb, "->", "theirs(mine 09:30)" if tb > ta else "ours")

# verify no markers anywhere
for f in ["results/autofill_state.json", "results/post_review.jsonl", "results/post_review/REPORT-20260926.md"]:
    bb = open(os.path.join(REPO, f), "rb").read()
    assert b"<<<<<<<" not in bb and b">>>>>>>" not in bb, f"markers in {f}"
st = json.load(io.open(os.path.join(REPO, "results/autofill_state.json"), encoding="utf-8-sig"))
assert isinstance(st["last_tick"], dict)
print("STEP3 RESOLVED+VERIFIED; last_tick ts =", st["last_tick"].get("ts"), "; launches =", len(st.get("launches", [])))
