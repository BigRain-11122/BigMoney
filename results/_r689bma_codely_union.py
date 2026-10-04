"""r689 bm-a CODELY.md UU resolver: block-union per r675 recipe.
origin(MERGE_HEAD) full text + my(HEAD) truly-new entry lines appended;
r479 substring-containment filter (my line being a substring of an origin
line = superseded variant, do not double-record);
r453 marker-count and structure proofs after write."""
import subprocess

path = "CODELY.md"

def side_bytes(ref):
    r = subprocess.run(["git", "show", ref + ":" + path], capture_output=True)
    assert r.returncode == 0, ref
    return r.stdout

theirs = side_bytes("MERGE_HEAD")  # origin wave
ours = side_bytes("HEAD")          # my side (has my MSG-1745 pit line)

theirs_lines = theirs.splitlines()
ours_lines = ours.splitlines()
theirs_set = set(theirs_lines)

missing = []
for ln in ours_lines:
    if ln in theirs_set:
        continue
    # r479: my line being a substring of some origin line = superseded variant
    if any(ln in t for t in theirs_set):
        continue
    missing.append(ln)

print("ours lines:", len(ours_lines), "theirs lines:", len(theirs_lines))
print("truly-new mine lines (pre-dup-filter):", len(missing))
# r453 dedup law / 四问门②复述禁令: bm-c r486 already registered the SAME
# yield-clobber lesson in the shared face (different wording, same content,
# MSG-1745-anchored). My line is a duplicate -> drop it (round flow already
# in round report + MSG-1810).
dup_filtered = []
for ln in missing:
    if b"MSG-1745" in ln and any(b"MSG-1745" in t for t in theirs_set):
        print("DROP-DUP (bm-c r486 entry already carries lesson):", ln[:80])
        continue
    dup_filtered.append(ln)
missing = dup_filtered
for m in missing:
    print("NEW:", m[:150])

# block-union: origin full + my truly-new lines (keep order, at end)
out = theirs_lines + missing
blob = b"\n".join(out) + b"\n"

# proofs: origin prefix identity
assert blob.startswith(theirs if theirs.endswith(b"\n") else theirs + b"\n"), \
    "origin prefix identity"
# r657 law: marker check by LINE-START, not substring (pit bodies legally
# embed '<<<<<<<' literals)
_start_markers = sum(1 for l in blob.splitlines()
                     if l.startswith(b"<<<<<<<") or l.startswith(b">>>>>>>")
                     or l.startswith(b"======="))
assert _start_markers == 0, "line-start conflict markers must be 0"
for m in missing:
    assert m in blob
# my yield-merge pit lesson must appear exactly once in the union -- carried
# by bm-c r486's entry (my duplicate dropped per r453/复述禁令)
key = "MSG-1745".encode("utf-8")
assert blob.count(key) == 1, "pit lesson must appear once, got %d" % blob.count(key)

with open(path, "wb") as f:
    f.write(blob)
print("CODELY union written:", len(blob), "bytes; origin lines preserved:",
      len(theirs_lines), "; mine appended:", len(missing))
