"""r281 bm-b rebase resolver: 2 UU files (autofill_state.json, post_review.jsonl).

Skill recipes (classified, 0 UNKNOWN):
- autofill_state.json = mixed-dict+ledger: launches union both stage blobs ->
  sort ts ASC -> cap 50 (keep newest); last_tick = inner-ts compare, whole dict,
  same-second tie -> ours(origin HEAD, r140); write-back mirrors stage-2 blob
  byte face (CRLF producer format, r223/r234); isinstance(last_tick, dict) assert.
- post_review.jsonl = append-log: line-level union zero loss (origin order +
  ours-only new lines appended).

Stages during rebase: :2 = ours = origin/main side; :3 = theirs = my commit.
"""
import json
import subprocess

def blob(rev, path):
    return subprocess.run(["git", "show", f"{rev}:{path}"],
                           capture_output=True).stdout

def write_mirror(path, text, src_bytes):
    eol = "\r\n" if src_bytes.count(b"\r\n") > src_bytes.count(b"\n") - src_bytes.count(b"\r\n") else "\n"
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(text.replace("\r\n", "\n").replace("\n", eol))

# ---------------- autofill_state.json ----------------
p1 = "results/autofill_state.json"
ours_b = blob(":2", p1)
theirs_b = blob(":3", p1)
o = json.loads(ours_b.decode("utf-8-sig"))
t = json.loads(theirs_b.decode("utf-8-sig"))

seen, launches = set(), []
for e in o.get("launches", []) + t.get("launches", []):
    key = json.dumps(e, sort_keys=True, ensure_ascii=False)
    if key not in seen:
        seen.add(key)
        launches.append(e)
launches.sort(key=lambda e: str(e.get("ts", "")))
if len(launches) > 50:
    launches = launches[-50:]

merged = dict(o)                      # origin side = base for scalar faces
merged["launches"] = launches

lt_o, lt_t = o.get("last_tick"), t.get("last_tick")
if isinstance(lt_t, dict) and (not isinstance(lt_o, dict)
                               or str(lt_t.get("ts", "")) > str(lt_o.get("ts", ""))):
    merged["last_tick"] = lt_t        # newer inner ts -> whole dict
elif isinstance(lt_o, dict) and isinstance(lt_t, dict) \
        and str(lt_t.get("ts", "")) == str(lt_o.get("ts", "")):
    merged["last_tick"] = lt_o        # same-second tie -> ours (r140)
assert isinstance(merged.get("last_tick"), dict), "last_tick must stay dict"

txt = json.dumps(merged, ensure_ascii=False, indent=1)
if not ours_b.endswith(b"\n"):
    txt_n = txt
else:
    txt_n = txt + "\n"
write_mirror(p1, txt_n, ours_b)
json.loads(open(p1, encoding="utf-8-sig").read())          # parse-verify (r185)
print("autofill_state: launches", len(o.get("launches", [])), "+",
      len(t.get("launches", [])), "-> union", len(launches),
      "| last_tick ts:", merged["last_tick"].get("ts"))

# ---------------- post_review.jsonl ----------------
p2 = "results/post_review.jsonl"
ours_l = blob(":2", p2).decode("utf-8-sig").splitlines()
theirs_l = blob(":3", p2).decode("utf-8-sig").splitlines()
have = set()
out_lines, added = [], 0
for l in ours_l:
    if l and l not in have:
        have.add(l)
        out_lines.append(l)
for l in theirs_l:
    if l and l not in have:
        have.add(l)
        out_lines.append(l)
        added += 1
with open(p2, "w", encoding="utf-8", newline="") as f:
    f.write("\n".join(out_lines) + ("\n" if theirs_b or True else ""))
n_ok = sum(1 for l in out_lines if l.strip())
for l in out_lines[-0:] or []:
    pass
import json as _j
for l in out_lines:
    if l.strip():
        _j.loads(l)                                          # parse-verify every line
print("post_review.jsonl: union", len(out_lines), "lines (ours",
      len(ours_l), "+ theirs-new", added, ") zero-loss, all lines parse OK")
