# -*- coding: utf-8 -*-
"""r807(2nd) bm-c rebase finale manual (post-quit recovery).
Quit removed .git/rebase-merge before message read (driver bug, honest note).
State now: rebase-merge gone, HEAD detached, index holds pick-6 resolutions.
Pick 6's message + author recovered from ORIGINAL commit object
a0c2b3e8783fe8bbd3f3ec3b18e0c28485ba290c (git log format=raw). Then:
commit -F + author env -> branch -f main HEAD -> checkout main."""
import json
import os
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CREATE = 0x08000000
PICK6 = "a0c2b3e8783fe8bbd3f3ec3b18e0c28485ba290c"
RECEIPT = os.path.join(ROOT, "results", "_r807bmc_rebase_recover.json")


def git(args, env=None):
    e = dict(os.environ)
    e["PYTHONUTF8"] = "1"
    if env:
        e.update(env)
    p = subprocess.run(["git", "-C", ROOT] + args, capture_output=True,
                       creationflags=CREATE, env=e)
    return (p.returncode, (p.stdout or b"").decode("utf-8", "replace"),
            (p.stderr or b"").decode("utf-8", "replace"))


def main():
    r = {"round": "r807-recover-finale-manual", "steps": []}
    # state check
    rc, out, _ = git(["rev-parse", "HEAD"])
    head0 = out.strip()
    rc, out, _ = git(["symbolic-ref", "-q", "HEAD"])
    r["start_head"] = head0
    r["start_ref"] = out.strip() or "(detached)"
    rc, out, _ = git(["status", "--porcelain"])
    staged = [l for l in out.splitlines() if l.strip() and l[0] in "MARC"]
    r["staged_n"] = len(staged)
    r["staged_sample"] = staged[:12]
    rc, out, _ = git(["diff", "--cached", "--stat"])
    r["cached_stat_tail"] = out.strip().splitlines()[-3:]
    # recover message + author from original pick 6 commit
    rc, out, _ = git(["log", "-1", "--format=%an%n%ae%n%aI%n%B", PICK6])
    parts = out.split("\n", 3)
    an, ae, ad, msg = parts[0], parts[1], parts[2], parts[3]
    r["pick6_author"] = "%s <%s> %s" % (an, ae, ad)
    msg_path = os.path.join(ROOT, "_r807bmc_pick6msg.txt")
    with open(msg_path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(msg if msg.endswith("\n") else msg + "\n")
    env = {"GIT_AUTHOR_NAME": an, "GIT_AUTHOR_EMAIL": ae, "GIT_AUTHOR_DATE": ad,
           "EDITOR": "true", "GIT_EDITOR": "true"}
    rc, out, err = git(["commit", "-F", msg_path], env=env)
    r["steps"].append("finale commit rc=%d %r" % (rc, (err or out)[:250]))
    if rc != 0:
        r["fatal"] = "commit refused"
        print(json.dumps(r, ensure_ascii=False, indent=1))
        return 2
    rc, out, _ = git(["rev-parse", "HEAD"])
    head = out.strip()
    r["final_head"] = head
    rc, out, err = git(["branch", "-f", "main", head])
    r["steps"].append("branch -f main %s rc=%d" % (head[:9], rc))
    rc, out, err = git(["checkout", "main"])
    r["steps"].append("checkout main rc=%d %r" % (rc, (err or out)[:150]))
    rc, out, _ = git(["rev-list", "--left-right", "--count",
                      "HEAD...origin/main"])
    r["ahead_behind"] = out.strip()
    rc, out, _ = git(["log", "--oneline", "-9"])
    r["final_log"] = out.strip()
    rc, out, _ = git(["status", "--porcelain"])
    r["final_dirty"] = out.strip()
    with open(RECEIPT, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(r, fh, ensure_ascii=False, indent=1)
    print("head=%s ahead_behind=%s" % (head[:9], r["ahead_behind"]))
    for s in r["steps"]:
        print("  " + s)
    print("FINAL-LOG:\n" + r["final_log"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
