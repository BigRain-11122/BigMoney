# r684 bm-b: pre-commit merge gates (r423 law x3 + pool semantic check)
import io, json, subprocess

def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8",
                       errors="replace")
    return r.stdout + r.stderr

# gate 1: zero UU/AA remaining
st = run(["git", "status", "--porcelain"]).splitlines()
unresolved = [l for l in st if l[:2] in ("UU", "AA", "DD", "AU", "UA",
                                         "DU", "UD")]
print("unresolved conflicts:", len(unresolved), unresolved[:5])
assert not unresolved

# gate 2: zero conflict markers in staged+worktree repo-wide (tracked files)
out = run(["git", "grep", "-l", "^<<<<<<<"])
print("tracked files with markers:", repr(out.strip()))
assert out.strip() == "", out

# gate 3: pool semantic check -- my RC entry + their W3 flips both present
pool = json.loads(io.open("results/runnable_pool.json", encoding="utf-8").read())
ids = {e.get("id") for e in pool.get("entries", [])}
print("pool entries:", len(pool["entries"]))
print("RC entry present:", "CONTEST-YTD-P1-RC-0OF1" in ids)
w3 = [e for e in pool["entries"] if "W3-JUDGE" in str(e.get("id", ""))]
for e in w3:
    print("W3:", e["id"], [(s.get("key"), s.get("status")) for s in
                           e.get("shards", [])])
assert "CONTEST-YTD-P1-RC-0OF1" in ids

# gate 4: my round products intact in merged tree
for p, needle in [
    ("scripts/contest_ytd_legs.py", "CONTEST_YTD_LEGS"),
    ("results/contest_p1/contest_table.json", '"pending_burn": 10'),
    ("fleet/tasks/T-2026-10-02-148-P1.json", "progress_r684_bmb"),
    ("state.json", '"round_no": 684'),
]:
    raw = io.open(p, encoding="utf-8", errors="replace").read()
    assert needle in raw, (p, needle)
    print("intact:", p)

# gate 5: daemon dirty faces NOT swallowed (only our 14 + merge result staged)
staged = [l for l in st if l[0] in ("M", "A") and l[1] == " "]
print("staged count:", len(staged))
print("MERGE_HEAD present:", run(["git", "rev-parse", "--verify",
                                 "MERGE_HEAD"]).strip()[:12])
