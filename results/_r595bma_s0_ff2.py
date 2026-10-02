# -*- coding: utf-8 -*-
"""FF2 integration (bm-c r385): CAS + reset + checkout all except CODELY.md;
CODELY = origin-verbatim + rescue the still-dropped r594 bm-a entry + my 2 tail entries."""
import subprocess

def git(*a, binary=False):
    r = subprocess.run(["git"] + list(a), capture_output=True)
    if binary:
        return r.returncode, r.stdout, r.stderr
    return r.returncode, r.stdout.decode("utf-8", "replace"), r.stderr.decode("utf-8", "replace")

rc, _, err = git("fetch", "origin"); assert rc == 0, err
rc, old, _ = git("rev-parse", "HEAD"); rc, new, _ = git("rev-parse", "origin/main")
old, new = old.strip(), new.strip()
if old == new:
    print("ALREADY-INTEGRATED"); raise SystemExit(0)
rc, mb, _ = git("merge-base", old, new); assert mb.strip() == old, "NOT-FF"
print("FF", old[:9], "->", new[:9])
rc, _, err = git("update-ref", "refs/heads/main", new, old); assert rc == 0, err
rc, _, err = git("reset", "--mixed", new); assert rc == 0, err
rc, out, _ = git("diff", "--name-only", "-z", old, new)
targets = [f for f in out.split("\0") if f and f != "CODELY.md"]
if targets:
    rc, _, err = git("checkout", "--", *targets); assert rc == 0, err
print("checkout origin-verbatim:", len(targets), "faces")

# CODELY union: origin base + rescue dropped lines + my tail
_, origin_blob, _ = git("show", f"{new}:CODELY.md", binary=True)
origin = origin_blob.replace(b"\r\n", b"\n")
local = open("CODELY.md", "rb").read().replace(b"\r\n", b"\n")
origin_lines = origin.split(b"\n")
origin_set = set(origin_lines)
local_lines = local.split(b"\n")
# lines I carry that origin lacks (non-blank)
mine_unique = [l for l in local_lines if l not in origin_set and l.strip()]
print("my unique lines vs origin:", len(mine_unique))
for l in mine_unique:
    print("  -", l[:70].decode("utf-8", "replace"))
# insert before the r595 bm-b entry if it precedes it chronologically, else append at tail
result = list(origin_lines)
for l in mine_unique:
    if l.startswith(b"- [2026-10-02 21:2x r594 bm-a"):
        anchor = b"- [2026-10-02 21:2x r595 bm-b]"
        i = next(idx for idx, x in enumerate(result) if x.startswith(anchor))
        result = result[:i] + [b"", l, b""] + result[i:]
        print("inserted r594 entry before r595 bm-b at line", i)
    else:
        if result and result[-1] != b"":
            result.append(b"")
        result.append(l)
        print("appended tail entry")
merged = b"\n".join(result)
if not merged.endswith(b"\n"):
    merged += b"\n"
open("CODELY.md", "wb").write(merged.replace(b"\n", b"\r\n"))
for probe in [b"21:2x r594 bm-a", b"21:2x r595 bm-b", b"21:5x r595 bm-a", b"r382 stranded"]:
    print("probe", probe.decode("utf-8", "replace"), "count", merged.count(probe))
rc, st, _ = git("status", "--porcelain")
d_faces = [l for l in st.splitlines() if l.startswith("D") or l[1] == "D" and l[0] != "?"]
print("D-faces remaining:", d_faces)
print("FF2-OK")
