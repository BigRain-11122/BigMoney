"""r699 x2_watch_log.jsonl UU resolve (r482/r485 union canon: theirs-verbatim
base + ours-unique appended, EOL-normalized containment math, zero-loss
assertion)."""
import subprocess

PATH = "results/x2_watch_log.jsonl"


def blob(rev):
    r = subprocess.run(["git", "show", f"{rev}:{PATH}"],
                       capture_output=True, timeout=30)
    assert r.returncode == 0, r.stderr[:200]
    return r.stdout


ours_b = blob("HEAD")
theirs_b = blob("MERGE_HEAD")
theirs_set = set()
for ln in theirs_b.split(b"\n"):
    s = ln.rstrip(b"\r").strip()
    if s:
        theirs_set.add(s)
ours_unique = []
ours_set = set()
for ln in ours_b.split(b"\n"):
    s = ln.rstrip(b"\r").strip()
    if not s or s in ours_set:
        continue
    ours_set.add(s)
    if s not in theirs_set:
        ours_unique.append(ln.rstrip(b"\r"))
raw = open(PATH, "rb").read()
eol = b"\r\n" if b"\r\n" in raw[:2000] else b"\n"
base = theirs_b.rstrip(b"\r\n")
if base and not base.endswith(b"}"):
    base = base  # theirs blob is line-complete by construction
merged = base
if ours_unique:
    merged = base + eol + eol.join(x for x in ours_unique)
else:
    merged = base
if not merged.endswith(eol):
    merged += eol
# zero-loss: every theirs line + every ours line present (stripped match)
mset = {x.rstrip(b"\r").strip() for x in merged.split(b"\n") if x.strip()}
missing = [x for x in theirs_set if x not in mset]
assert not missing, f"theirs lines lost: {missing[:2]}"
missing2 = [x for x in ours_set if x not in mset]
assert not missing2, f"ours lines lost: {missing2[:2]}"
open(PATH, "wb").write(merged)
print("union done: theirs lines=", len(theirs_set),
      "ours-unique appended=", len(ours_unique),
      "total=", len(mset))
