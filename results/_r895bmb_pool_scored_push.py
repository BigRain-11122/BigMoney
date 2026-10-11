# -*- coding: utf-8 -*-
"""r895 bm-b: surgical add-only push of POOL-SCORED-20261012.md to FluxGroup main
(O-20261011-1917-bm-c section 3 deliverable; editorial seat three-question scoring).

Reuses the r894 G-soft closeout guard pattern (G1 empty-tree / G2 exact-add /
G3 zero-deletion ls-tree walk / G4 remote==base fast-forward), adapted for a
single-file deliverable. Race-safe vs the in-flight G-soft push via G4+retry.
"""
import os, sys, json, subprocess, time

REPO = r"C:\Fluxgroup\FluxGroup"
SRC = r"C:\Fluxgroup\FluxGroup\quant\bigmoney\results\pool_scored\POOL-SCORED-20261012.md"
REL = "cph4/fleet/meme-daily-v1/topics/POOL-SCORED-20261012.md"
IDX = os.path.join(os.environ.get("TEMP", r"C:\Users\Administrator\AppData\Local\Temp"),
                   "r895bmb_%d.index" % int(time.time()))
RECEIPT_PATH = r"C:\Fluxgroup\FluxGroup\quant\bigmoney\results\_r895bmb_pool_scored_receipt.json"
EMPTY_TREE = "4b825dc642cb6eb9a060e54bf8d69288fbee4904"


def run(cmd, cwd=None, env=None, timeout=None, check=True):
    r = subprocess.run(cmd, cwd=cwd, env=env, capture_output=True, timeout=timeout)
    if check and r.returncode != 0:
        raise RuntimeError("rc=%d %s\n%s" % (r.returncode, cmd[:4],
                           r.stderr.decode("utf-8", "replace")[:1200]))
    return r


def main():
    t0 = time.time()
    run(["git", "-C", REPO, "fetch", "origin"], timeout=300)
    base = run(["git", "-C", REPO, "rev-parse", "origin/main"]).stdout.decode().strip()

    sha = run(["git", "-C", REPO, "hash-object", "-w", "--", SRC]).stdout.decode().strip()
    prev = run(["git", "-C", REPO, "rev-parse", "origin/main:" + REL], check=False)
    already = prev.returncode == 0 and prev.stdout.decode().strip() == sha
    if already:
        json.dump({"pushed": False, "already_present": True, "base": base, "sha": sha},
                  open(RECEIPT_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print("already present at origin, no-op")
        return 0

    env = dict(os.environ)
    env["GIT_INDEX_FILE"] = IDX
    if os.path.exists(IDX):
        os.remove(IDX)

    pushed = False
    receipt = {"rel": REL, "base": base, "sha": sha}
    for attempt in (1, 2, 3):
        run(["git", "-C", REPO, "read-tree", base], env=env, timeout=180)
        run(["git", "-C", REPO, "update-index", "--add", "--cacheinfo",
             "100644,%s,%s" % (sha, REL)], env=env, timeout=60)
        tree = run(["git", "-C", REPO, "write-tree"], env=env, timeout=120).stdout.decode().strip()
        if tree == EMPTY_TREE:
            print("G1 FAIL empty tree"); sys.exit(4)
        b_paths = set(l.strip() for l in run(["git", "-C", REPO, "ls-tree", "-r", "--name-only", base],
                     timeout=300).stdout.decode("utf-8", "replace").splitlines() if l.strip())
        n_paths = set(l.strip() for l in run(["git", "-C", REPO, "ls-tree", "-r", "--name-only", tree],
                      timeout=300).stdout.decode("utf-8", "replace").splitlines() if l.strip())
        dels = b_paths - n_paths
        adds = n_paths - b_paths
        if dels or adds != {REL}:
            print("G3 FAIL dels=%d adds=%s" % (len(dels), sorted(adds)[:3])); sys.exit(4)
        print("G1-G3 pass tree=%s" % tree[:12])
        msg = ("POOL-SCORED-20261012: hot-topic pool three-question editorial scoring "
               "(O-20261011-1917-bm-c sec3; 60 rows -> 8 dedup'd deep-research picks, "
               "45% red-line filtered; bm-b editorial seat)")
        commit = run(["git", "-C", REPO, "commit-tree", tree, "-p", base, "-m", msg],
                     timeout=60).stdout.decode().strip()
        rr = run(["git", "-C", REPO, "ls-remote", "origin", "refs/heads/main"], timeout=120, check=False)
        remote = rr.stdout.decode().split()[0] if rr.stdout.decode().split() else "?"
        if remote != base:
            print("G4: remote moved -> refetch+retry")
            run(["git", "-C", REPO, "fetch", "origin"], timeout=300)
            base = run(["git", "-C", REPO, "rev-parse", "origin/main"]).stdout.decode().strip()
            continue
        r = run(["git", "-C", REPO, "push", "origin", commit + ":refs/heads/main"],
                check=False, timeout=720)
        if r.returncode == 0:
            pushed = True
            receipt.update({"pushed": True, "commit": commit, "attempt": attempt})
            run(["git", "-C", REPO, "update-ref", "refs/remotes/origin/main", commit], timeout=60)
            break
        print("push rejected: %s" % r.stderr.decode("utf-8", "replace")[:300])
        run(["git", "-C", REPO, "fetch", "origin"], timeout=300)
        base = run(["git", "-C", REPO, "rev-parse", "origin/main"]).stdout.decode().strip()

    receipt["elapsed_sec"] = round(time.time() - t0, 1)
    json.dump(receipt, open(RECEIPT_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("receipt written pushed=%s elapsed=%ss" % (pushed, receipt["elapsed_sec"]))
    return 0 if pushed else 3


if __name__ == "__main__":
    sys.exit(main())
