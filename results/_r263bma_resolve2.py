# -*- coding: utf-8 -*-
"""R263 bm-a resolver #2: T-83 additive UU union -- keep bm-b progress_r267 line
AND bm-a yield_note_bm_a line (both sides additive, zero overlap)."""
import json

P = "fleet/tasks/T-2026-09-26-83-P1.json"
raw = open(P, "rb").read()
txt = raw.decode("utf-8")
lines = txt.splitlines()
out, mode = [], "copy"
head_lines, mine_lines = [], []
for ln in lines:
    s = ln.strip()
    if s.startswith("<<<<<<<"):
        mode = "head"; continue
    if s.startswith("=======") and mode == "head":
        mode = "mine"; continue
    if s.startswith(">>>>>>>"):
        mode = "union"; continue
    if mode == "head":
        head_lines.append(ln); continue
    if mode == "mine":
        mine_lines.append(ln); continue
    out.append(ln)

assert head_lines and mine_lines, f"unexpected conflict shape h={len(head_lines)} m={len(mine_lines)}"
# comma discipline: head lines join, then mine lines; head last line must end
# with comma before mine block; mine last line is pre-close-brace (no comma)
joined = head_lines + mine_lines
for i, ln in enumerate(joined[:-1]):
    if ln.rstrip().endswith(("\"", "}")) and not ln.rstrip().endswith(","):
        joined[i] = ln.rstrip() + ","
merged = out[:-1] + joined + out[-1:]   # reinsert before closing-brace tail
body = "\n".join(merged)
json.loads(body)                        # parse-verify BEFORE write (r185)
if raw.endswith(b"\n") and not body.endswith("\r\n"):
    body += "\r\n"
body = body.replace("\n", "\r\n") if b"\r\n" in raw else body
open(P, "wb").write(body.encode("utf-8"))
t = json.loads(open(P, encoding="utf-8-sig").read())
assert "progress_r267" in t and "yield_note_bm_a" in t, "union lost a side"
print("resolved: union keeps progress_r267 (bm-b) + yield_note_bm_a (bm-a), parse-verified")
