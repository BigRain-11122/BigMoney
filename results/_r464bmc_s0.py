"""r464 bm-c S0 probe: dead-rebase legacy check + round-start dirty faces +
fetch + behind/changed-set intersection (r630/r437 laws). Read-only + fetch.
File-out per r446 probe law. Zero console CJK print."""
import os
import subprocess
import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "results", "_r464bmc_s0.json")


def git(args):
    return subprocess.run(["git"] + args, capture_output=True, cwd=ROOT,
                          creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))


def main():
    ev = {"ts": datetime.datetime.now().isoformat(timespec="seconds")}
    # r630 dead-rebase legacy check
    ev["rebase_merge_dir"] = os.path.isdir(os.path.join(ROOT, ".git", "rebase-merge"))
    r = git(["status", "--porcelain=v1", "-b"])
    head = r.stdout.decode("utf-8", "replace").splitlines()
    ev["status_head"] = head[0] if head else ""
    ev["branch"] = ""
    rb = git(["branch", "--show-current"]).stdout.decode().strip()
    ev["branch"] = rb
    ev["dirty"] = [ln for ln in head[1:]]
    ev["dirty_count"] = len(ev["dirty"])
    # fetch
    fr = git(["fetch", "origin"])
    ev["fetch_rc"] = fr.returncode
    if fr.returncode != 0:
        ev["fetch_err"] = fr.stderr.decode("utf-8", "replace")[:300]
    # ahead/behind
    ab = git(["rev-list", "--left-right", "--count", "origin/main...HEAD"])
    if ab.returncode == 0:
        behind_s, ahead_s = ab.stdout.decode().split()
        ev["behind"] = int(behind_s)
        ev["ahead"] = int(ahead_s)
    else:
        ev["behind"] = None
        ev["ahead"] = None
    # origin changed set vs HEAD
    dn = git(["diff", "--name-only", "HEAD", "origin/main"])
    ev["origin_changed"] = sorted(
        ln for ln in dn.stdout.decode("utf-8", "replace").splitlines() if ln.strip())
    dirty_paths = set()
    for ln in ev["dirty"]:
        p = ln[3:].strip().strip('"')
        dirty_paths.add(p)
    ev["intersection"] = sorted(dirty_paths & set(ev["origin_changed"]))
    # HEAD tip
    ev["head_sha"] = git(["rev-parse", "HEAD"]).stdout.decode().strip()
    ev["origin_sha"] = git(["rev-parse", "origin/main"]).stdout.decode().strip()
    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        import json
        json.dump(ev, f, ensure_ascii=False, indent=1)
    print("S0_DONE dirty=%d behind=%s ahead=%s intersect=%d fetch_rc=%s" % (
        ev["dirty_count"], ev.get("behind"), ev.get("ahead"),
        len(ev["intersection"]), ev["fetch_rc"]))


if __name__ == "__main__":
    main()
