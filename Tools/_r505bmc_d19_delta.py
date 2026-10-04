"""r505 bm-c: D-19 decisions.md delta read -- find blob transition in group
tree git history (4E5BE321 -> 755428F8) and diff the two versions to extract
new rows (BigMoney-relevant lines)."""
import hashlib
import os
import subprocess
import sys

CREATE_NO_WINDOW = 0x08000000
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GROUP = os.path.normpath(os.path.join(ROOT, "..", ".."))
OLD_WM = "4E5BE321F9B7A15D7F58BAB3771ECF329534EED8D30B090CDAC4E9F151D911DC"
NEW_SHA = "755428F8A0816334C9A42F899DE4DB9F6F4502E80A39DA716BFC3B82DCFA1B2B"


def git_raw(args, cwd):
    r = subprocess.run(["git"] + args, capture_output=True, cwd=cwd,
                       creationflags=CREATE_NO_WINDOW)
    return r.returncode, r.stdout or b"", (r.stderr or b"").decode("utf-8", "replace")


def main():
    rc, out, err = git_raw(["log", "--format=%H|%ad|%s", "--date=iso",
                            "-15", "origin/main", "--", "docs/decisions.md"], GROUP)
    if rc != 0:
        print("LOG-FAIL " + err.strip()[:200])
        sys.exit(2)
    commits = [l for l in out.decode("utf-8", "replace").splitlines() if l.strip()]
    old_blob = None
    old_commit = None
    print("--- commits touching docs/decisions.md (recent 15) ---")
    for c in commits:
        sha = c.split("|")[0]
        rc, blob, _ = git_raw(["show", sha + ":docs/decisions.md"], GROUP)
        h = hashlib.sha256(blob).hexdigest().upper()
        mark = ""
        if h == NEW_SHA:
            mark = "<= TIP-BLOB (755428F8)"
        if h == OLD_WM:
            mark = "<= OLD-WATERMARK-BLOB (4E5BE321)"
            old_blob = blob
            old_commit = sha
        print("%s %s" % (c[:110], mark))
    if old_blob is None:
        print("OLD-WATERMARK-BLOB NOT FOUND in last 15 commits -- full re-read required")
        sys.exit(3)
    rc, new_blob, _ = git_raw(["show", "origin/main:docs/decisions.md"], GROUP)
    print("--- DIFF old(%s) -> tip ---" % old_commit[:10])
    old_lines = old_blob.decode("utf-8", "replace").splitlines()
    new_lines = new_blob.decode("utf-8", "replace").splitlines()
    old_set = set(l.strip() for l in old_lines)
    added = [l for l in new_lines if l.strip() not in old_set]
    print("OLD %d lines / NEW %d lines / ADDED %d lines" %
          (len(old_lines), len(new_lines), len(added)))
    for l in added:
        print("+ " + l.strip()[:400])


if __name__ == "__main__":
    main()
