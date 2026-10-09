# -*- coding: utf-8 -*-
"""r807(2nd) bm-c rebase recovery finale (pick 6/6 = last stop).
State: all 6 picks in done, pick 6 (a0c2b3e87 s0-tail2) resolved+staged,
its commit pending. Plain `git commit -F` refuses at this terminal stop;
continue hits the interactive-editor (TERM=dumb) face. Cure: continue with
no-op editor (EDITOR=true GIT_EDITOR=true) -> commit_staged_changes uses the
stored message unedited; fallback = r624 finale (quit + commit -F with
author env + branch -f main + checkout). Exit 0 = rebase completed."""
import json
import os
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CREATE = 0x08000000
RM = os.path.join(ROOT, ".git", "rebase-merge")
RECEIPT = os.path.join(ROOT, "results", "_r807bmc_rebase_recover.json")
EXPECT_STOP = "a0c2b3e8783fe8bbd3f3ec3b18e0c28485ba290c"


def git(args, env=None):
    e = dict(os.environ)
    e["PYTHONUTF8"] = "1"
    if env:
        e.update(env)
    p = subprocess.run(["git", "-C", ROOT] + args, capture_output=True,
                       creationflags=CREATE, env=e)
    return (p.returncode, (p.stdout or b"").decode("utf-8", "replace"),
            (p.stderr or b"").decode("utf-8", "replace"))


def rd(p):
    with open(p, encoding="utf-8", errors="replace") as fh:
        return fh.read().strip()


def report(r):
    rc, out, _ = git(["rev-parse", "HEAD"])
    r["final_head"] = out.strip()
    rc, out, _ = git(["log", "--oneline", "-8"])
    r["final_log"] = out.strip()
    rc, out, _ = git(["status", "--porcelain"])
    r["final_dirty"] = out.strip()
    rc, out, _ = git(["rev-list", "--left-right", "--count",
                      "HEAD...origin/main"])
    r["ahead_behind"] = out.strip()
    rc, out, _ = git(["symbolic-ref", "-q", "HEAD"])
    r["on_branch"] = out.strip() or "(detached)"
    with open(RECEIPT, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(r, fh, ensure_ascii=False, indent=1)
    print("completed=%s head=%s branch=%s ahead_behind=%s"
          % (r.get("completed"), r["final_head"][:9], r["on_branch"],
             r["ahead_behind"]))
    for s in r["steps"]:
        print("  " + s)
    print("FINAL-LOG:\n" + r["final_log"])


def main():
    r = {"round": "r807-recover-finale", "steps": []}
    assert os.path.isdir(RM), "rebase-merge missing"
    stopped = rd(os.path.join(RM, "stopped-sha"))
    assert stopped == EXPECT_STOP, "unexpected stop %s" % stopped
    r["steps"].append("stop=%s (all 6 picks done)" % stopped[:9])

    # attempt 1: continue with no-op editor
    env = {"EDITOR": "true", "GIT_EDITOR": "true", "GIT_SEQUENCE_EDITOR": "true",
           "TERM": "dumb"}
    rc, out, err = git(["rebase", "--continue"], env=env)
    r["steps"].append("continue(true-editor) rc=%d %r" % (
        rc, (err or out)[:250]))
    if not os.path.isdir(RM):
        r["completed"] = True
        report(r)
        return 0

    # attempt 2: r624 finale -- quit + manual commit + branch -f + checkout
    rc, out, err = git(["rebase", "--quit"])
    r["steps"].append("quit rc=%d %r" % (rc, (err or out)[:150]))
    aenv = {}
    for line in rd(os.path.join(RM, "author-script")).splitlines() \
            if os.path.exists(os.path.join(RM, "author-script")) else []:
        if "=" in line:
            k, v = line.split("=", 1)
            k = k.strip()
            if k in ("GIT_AUTHOR_NAME", "GIT_AUTHOR_EMAIL", "GIT_AUTHOR_DATE"):
                aenv[k] = v.strip().strip("'")
    msg_path = os.path.join(ROOT, "_r807bmc_pick6msg.txt")
    with open(msg_path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(rd(os.path.join(RM, "message")) + "\n")
    rc, out, err = git(["commit", "-F", msg_path], env=aenv)
    r["steps"].append("finale commit rc=%d %r" % (rc, (err or out)[:250]))
    if rc != 0:
        r["fatal"] = "finale commit refused"
        report(r)
        return 2
    rc, out, err = git(["rev-parse", "HEAD"])
    head = out.strip()
    rc, out, err = git(["branch", "-f", "main", head])
    r["steps"].append("branch -f main %s rc=%d" % (head[:9], rc))
    rc, out, err = git(["checkout", "main"])
    r["steps"].append("checkout main rc=%d %r" % (rc, (err or out)[:150]))
    r["completed"] = not os.path.isdir(RM) and "main" in \
        (git(["symbolic-ref", "HEAD"])[1].strip() or "")
    report(r)
    return 0 if r["completed"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
