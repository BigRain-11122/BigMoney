# -*- coding: utf-8 -*-
"""r897 bm-b: group-repo lazy-fetch trap defusal + sequential relaunch of r894/r895 pushes.

Live-fire root cause (20:44/20:49): write-tree on the blob:none partial-clone group
repo triggers an automatic ~2.9k-tree lazy fetch; on a stalled night ssh route the
fetch hangs forever (no TCP keepalive). Prior detached workers (r894 gsoft closeout /
r895 pool_scored) stalled 46-51 min with zero progress; all chain PIDs killed and
verified dead at 21:4x; remote untouched. Route alive now (ls-remote instant).

Fix: materialize ALL trees of the fresh origin/main tip ONCE via a fresh ssh conn
(fetch + bounded retried `ls-tree -r origin/main`), THEN relaunch the two existing
push scripts sequentially (r894 first = O-1810-3 owner-leg deliverable, then r895
POOL-SCORED). Their write-tree/ls-tree then run fully local; G4 keeps each push
fast-forward-safe. Child trees killed via taskkill /T on timeout (shim-orphan pit).
"""
import os, sys, json, subprocess, time

REPO = r"C:\Fluxgroup\FluxGroup"
BIGM = r"C:\Fluxgroup\FluxGroup\quant\bigmoney"
RECEIPT = os.path.join(BIGM, r"results\_r897bmb_grouppush_receipt.json")
SCRIPTS = [
    ("r894_gsoft", os.path.join(BIGM, r"results\_r894bmb_gsoft_closeout.py")),
    ("r895_pool_scored", os.path.join(BIGM, r"results\_r895bmb_pool_scored_push.py")),
]


def run(cmd, timeout, check=True, retries=1):
    last = None
    for i in range(retries + 1):
        try:
            r = subprocess.run(cmd, cwd=REPO, capture_output=True, timeout=timeout)
            if check and r.returncode != 0:
                last = "rc=%d %s" % (r.returncode, r.stderr.decode("utf-8", "replace")[:300])
                continue
            return r
        except subprocess.TimeoutExpired:
            last = "timeout after %ss (attempt %d)" % (timeout, i + 1)
    raise RuntimeError(last or "unknown")


def main():
    t0 = time.time()
    receipt = {"stage": "start", "ts": time.strftime("%Y-%m-%dT%H:%M:%S+08:00")}
    def flush():
        json.dump(receipt, open(RECEIPT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    # P1: fetch fresh origin/main (bounded, retried)
    run(["git", "-C", REPO, "fetch", "origin"], timeout=240, retries=1)
    tip = run(["git", "-C", REPO, "rev-parse", "origin/main"], timeout=30).stdout.decode().strip()
    receipt.update({"stage": "fetched", "origin_main": tip})
    flush()

    # P2: materialize ALL trees of the tip through a fresh conn (defuses lazy fetch)
    run(["git", "-C", REPO, "ls-tree", "-r", "--name-only", "origin/main"], timeout=600, retries=1)
    receipt.update({"stage": "trees_materialized", "ls_tree_sec": round(time.time() - t0, 1)})
    flush()

    # P3: relaunch the two existing push scripts sequentially (bounded 30 min each,
    # whole-tree kill on timeout per shim-orphan pit)
    for tag, path in SCRIPTS:
        ts = time.time()
        p = subprocess.Popen([sys.executable, path],
                              cwd=BIGM, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        try:
            out, err = p.communicate(timeout=1800)
            receipt[tag] = {"rc": p.returncode, "sec": round(time.time() - ts, 1),
                            "tail": (out.decode("utf-8", "replace") + err.decode("utf-8", "replace"))[-400:]}
        except subprocess.TimeoutExpired:
            subprocess.run(["taskkill", "/F", "/T", "/PID", str(p.pid)], capture_output=True)
            receipt[tag] = {"rc": "TIMEOUT-KILLED-1800s", "sec": round(time.time() - ts, 1)}
        receipt["stage"] = "done_" + tag
        flush()

    receipt.update({"stage": "complete", "elapsed_sec": round(time.time() - t0, 1)})
    flush()
    ok = all(isinstance(receipt.get(t, {}).get("rc"), int) and receipt[t]["rc"] == 0 for t, _ in SCRIPTS)
    return 0 if ok else 3


if __name__ == "__main__":
    sys.exit(main())
