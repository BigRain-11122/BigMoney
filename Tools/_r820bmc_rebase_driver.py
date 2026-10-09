# -*- coding: utf-8 -*-
"""r820 bm-c rebase conflict driver (r787/r789 add+continue atomic law):
auto-resolves ONLY whitelisted own/regen live faces with --theirs (my
replayed commit side; tail absorbs carry newest content anyway); any
conflict OUTSIDE the whitelist (code/fleet/ledger/union faces) = abort
rebase + rc1 (round falls back to read-only maintenance per loop law)."""
import os
import subprocess
import sys

ALLOW_PREFIXES = ("results/", "docs/daily_report/", "docs/live_usage/",
                 "data/", "logs/", "monitor/")
ALLOW_EXACT = set()
DENY_HINTS = ("CODELY.md", "fleet/", "scripts/", "Tools/", "firm/",
              "research/", "engine/", "orders", "decisions", "state-bm-a",
              "round_reports-bm-a", "round_reports-bm-b", "state-bm-b")


def run(args, env_extra=None):
    env = os.environ.copy()
    if env_extra:
        env.update(env_extra)
    p = subprocess.run(["git"] + args, capture_output=True,
                       encoding="utf-8", errors="replace", env=env)
    return p.returncode, p.stdout, p.stderr


def in_rebase():
    return os.path.isdir(".git/rebase-merge") or os.path.isdir(
        ".git/rebase-apply")


def main():
    rounds = 0
    while in_rebase() and rounds < 80:
        rounds += 1
        rc, out, err = run(["diff", "--name-only", "--diff-filter=U"])
        files = [f.strip().strip('"') for f in out.splitlines()
                 if f.strip()]
        if not files:
            rc2, o2, e2 = run(["rebase", "--continue"],
                              {"GIT_EDITOR": "true"})
            if not in_rebase():
                print("rebase COMPLETE after bare continue, rounds=%d" % rounds)
                return 0
            print("bare-continue rc=%s err=%s" % (rc2, e2[:300]))
            continue
        for f in files:
            if any(h in f for h in DENY_HINTS) or not any(
                    f.startswith(p) for p in ALLOW_PREFIXES):
                print("DENY-LIST conflict face: %s -- aborting rebase, "
                      "round falls back to read-only maintenance" % f)
                run(["rebase", "--abort"])
                return 1
        for f in files:
            run(["checkout", "--theirs", "--", f])
            run(["add", "--", f])
        rc3, o3, e3 = run(["rebase", "--continue"],
                          {"GIT_EDITOR": "true"})
        if not in_rebase():
            print("rebase COMPLETE, rounds=%d last_faces=%s"
                  % (rounds, files))
            return 0
        if rc3 != 0 and "No rebase in progress" not in (e3 or ""):
            rc4, out4, _ = run(["diff", "--name-only",
                                "--diff-filter=U"])
            if not out4.strip():
                print("continue rc=%s but no unmerged faces left; "
                      "state=%s" % (rc3, e3[:200]))
                return 2
    if in_rebase():
        print("round cap hit, still in rebase -- aborting")
        run(["rebase", "--abort"])
        return 1
    print("no rebase in progress at entry")
    return 0


if __name__ == "__main__":
    sys.exit(main())
