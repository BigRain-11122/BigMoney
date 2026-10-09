# -*- coding: utf-8 -*-
"""r807(2nd) bm-c half-open rebase triage probe (r868/r867 law face; read-only):
1) rebase-merge state files + mtimes (when did the predecessor die);
2) live process scan for any in-flight predecessor (codely/git/python working
   in this repo) -- self-exclusion via -notmatch on probe's own cmdline tokens
   (r340 self-match law);
3) stopped-sha/author-script/message presence -> stopped-at-pick vs
   clean-between-picks discrimination;
4) my absorb commit 0e90e21b2 position (parent chain vs done/todo shas)."""
import os
import subprocess
import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CREATE = 0x08000000
GITDIR = os.path.join(ROOT, ".git")
RM = os.path.join(GITDIR, "rebase-merge")


def git(args):
    r = subprocess.run(["git"] + args, cwd=ROOT, capture_output=True,
                       creationflags=CREATE)
    return r.returncode, (r.stdout or b"").decode("utf-8", "replace"), \
        (r.stderr or b"").decode("utf-8", "replace")


def main():
    print("== rebase-merge state files ==")
    for fn in sorted(os.listdir(RM)):
        p = os.path.join(RM, fn)
        mt = datetime.datetime.fromtimestamp(os.path.getmtime(p))
        sz = os.path.getsize(p) if os.path.isfile(p) else "<dir>"
        print("  %-22s mtime=%s size=%s" % (fn, mt.isoformat(timespec="seconds"), sz))
    for fn in ("stopped-sha", "author-script", "message", "amend", "no-resolv-fail"):
        p = os.path.join(RM, fn)
        print("  presence %-14s -> %s" % (fn, os.path.exists(p)))

    print("== git state ==")
    _, out, _ = git(["rev-parse", "HEAD"])
    print("HEAD", out.strip())
    _, out, _ = git(["log", "--oneline", "-8"])
    print(out)
    _, out, _ = git(["ls-files", "-u"])
    print("UU entries:", len([l for l in out.splitlines() if l.strip()]))
    _, out, _ = git(["status", "--porcelain"])
    print("status:")
    for l in out.splitlines():
        print("  " + l)
    _, out, _ = git(["merge-base", "HEAD", "origin/main"])
    print("merge-base HEAD origin/main:", out.strip())
    _, out, _ = git(["rev-parse", "origin/main"])
    print("origin/main:", out.strip())
    _, out, _ = git(["log", "--oneline", "-5", "origin/main"])
    print(out)

    print("== live process scan (self-excluded) ==")
    ps = ("Get-CimInstance Win32_Process | "
          "Where-Object { $_.Name -match 'git|python|codely|wscript|node' } | "
          "Select-Object ProcessId,Name,CreationDate,CommandLine | "
          "ConvertTo-Json -Compress")
    r = subprocess.run(["powershell", "-NoProfile", "-Command", ps],
                       capture_output=True, creationflags=CREATE)
    txt = (r.stdout or b"").decode("utf-8", "replace")
    print(txt[:4000])


if __name__ == "__main__":
    main()
