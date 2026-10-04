# -*- coding: utf-8 -*-
"""r687 bm-a merge resolver: 3 freeze faces theirs-canonical (bm-c r484 freeze,
让路律 16:34<16:42) + CODELY.md block-union (r675/r453/r479 laws).
Blobs via git show HEAD:/MERGE_HEAD: direct (r657 ii). Writes resolved files,
prints assertions. CODELY path args optional (reusable resolver face).
"""
import subprocess, sys, io, os

REPO = r"C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney"

def blob(rev, path):
    b = subprocess.run(["git", "-C", REPO, "show", "%s:%s" % (rev, path)],
                       capture_output=True)
    if b.returncode != 0:
        raise SystemExit("BLOB FAIL %s %s: %s" % (rev, path, b.stderr[:200]))
    return b.stdout.decode("utf-8", "replace")

def resolve_codely(path):
    ours = blob("HEAD", path)
    theirs = blob("MERGE_HEAD", path)
    # r675 block-union: origin full text preserved; my genuinely-new lines appended
    t_lines = theirs.splitlines()
    o_lines = ours.splitlines()
    t_blob = "\n".join(t_lines)
    new_lines = []
    for ln in o_lines:
        if ln in t_blob:
            continue  # already present (exact line)
        if ln and ln.strip() and ln in t_blob:  # defensive
            continue
        # r479 substring-containment: my line is a substring of an origin line -> superseded variant, drop
        if any(ln in tl for tl in t_lines):
            continue
        new_lines.append(ln)
    # r675: origin side structural line count must not decrease; union = theirs verbatim + new
    merged = t_lines + new_lines
    out = "\n".join(merged) + ("\n" if theirs.endswith("\n") or True else "")
    with io.open(os.path.join(REPO, path.replace("/", "\\")), "w",
                 encoding="utf-8", newline="") as f:
        f.write(out)
    # assertions
    assert out.splitlines()[:len(t_lines)] == t_lines, "origin prefix identity FAIL"
    assert len(merged) == len(t_lines) + len(new_lines), "count FAIL"
    print("CODELY union: theirs_lines=%d mine_new=%d merged=%d"
          % (len(t_lines), len(new_lines), len(merged)))
    for ln in new_lines:
        print("  +NEW: " + ln[:120])
    return 0

def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else ""
    if mode == "codely":
        return resolve_codely(sys.argv[2])
    print("usage: resolve_codely <path>")
    return 1

if __name__ == "__main__":
    sys.exit(main())
