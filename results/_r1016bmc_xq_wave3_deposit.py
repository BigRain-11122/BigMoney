# -*- coding: utf-8 -*-
"""r1016 bm-c: wave3 XQ boards group-tree CAS direct-deposit (A-trial 29 + casting 16).

Law family: E01 CAS direct-commit + execution-time tip (r593) + r565 early-visibility.
Deposit faces (all under cph4/fleet/mv-album-001-jay/outbound/xq-wave3/):
  - XQ-A-TRIAL-BOARD_q88.jpg          (contact board 29 frames)
  - XQ-CASTING-TRIAL-BOARD_q88.jpg    (contact board 16 frames)
  - XQ-A-TRIAL-RECEIPT-r1015.json     (runner receipt verbatim copy)
  - XQ-CASTING-RECEIPT-r1015.json     (runner receipt verbatim copy)
Plus: docs/orders.md receipt row appended at tail (origin-blob surgery, no worktree contact).
CAS push <sha>:refs/heads/main; verify ls-remote; update local main ref.
"""
import hashlib
import json
import os
import subprocess
import sys
import time

REPO = r"K:\Fluxgroup\FluxGroup"
ARCH = r"K:\Fluxgroup\archive\mv-album-001-jay"
BIGM = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
OUT = os.path.join(BIGM, "results", "_r1016bmc_xq_wave3_deposit.json")
CNW = 0x08000000
IDX = os.path.join(BIGM, "results", "_r1016bmc_tmp_index")

PAYLOAD = [
    (os.path.join(ARCH, "xq-kf-a-trial", "XQ-A-TRIAL-BOARD_q88.jpg"),
     "cph4/fleet/mv-album-001-jay/outbound/xq-wave3/XQ-A-TRIAL-BOARD_q88.jpg"),
    (os.path.join(ARCH, "xq-casting-trial", "XQ-CASTING-TRIAL-BOARD_q88.jpg"),
     "cph4/fleet/mv-album-001-jay/outbound/xq-wave3/XQ-CASTING-TRIAL-BOARD_q88.jpg"),
    (os.path.join(BIGM, "results", "_r1015bmc_xq_trial_receipt.json"),
     "cph4/fleet/mv-album-001-jay/outbound/xq-wave3/XQ-A-TRIAL-RECEIPT-r1015.json"),
    (os.path.join(BIGM, "results", "_r1015bmc_xq_casting_receipt.json"),
     "cph4/fleet/mv-album-001-jay/outbound/xq-wave3/XQ-CASTING-RECEIPT-r1015.json"),
]

ORD_ROW_FILE = os.path.join(BIGM, "results", "_r1016bmc_xq_ord_row.txt")


def git(args, check=True, env=None, binary=False):
    r = subprocess.run(["git"] + args, capture_output=True, cwd=REPO,
                       creationflags=CNW, env=env)
    if check and r.returncode != 0:
        sys.exit("GIT FAIL %s -> %s" % (args[:4], (r.stderr or r.stdout).decode("utf-8", "replace")[:400]))
    return r


def main():
    t0 = time.time()
    # gate: both runner receipts must exist and be COMPLETE
    tri = json.load(open(PAYLOAD[2][0], encoding="utf-8"))
    cas = json.load(open(PAYLOAD[3][0], encoding="utf-8"))
    assert tri.get("count_ok") == 29 and tri.get("lint_fail", 0) == 0, "trial not 29/29"
    assert cas.get("count_ok") == 16, "casting not 16/16"
    for src, _ in PAYLOAD:
        assert os.path.isfile(src) and os.path.getsize(src) > 1000, "missing payload %s" % src

    git(["fetch", "origin"])
    tip = git(["rev-parse", "origin/main"]).stdout.decode().strip()
    # orders.md tail-anchored append (origin blob surgery)
    ord_bytes = git(["show", tip + ":docs/orders.md"], check=True).stdout
    row = open(ORD_ROW_FILE, encoding="utf-8").read().rstrip("\n").encode("utf-8")
    new_ord = ord_bytes.rstrip(b"\n") + b"\n" + row + b"\n"
    assert ord_bytes.rstrip(b"\n") in new_ord, "orders append must be additive"
    with open(os.path.join(BIGM, "results", "_r1016bmc_orders_new.md"), "wb") as f:
        f.write(new_ord)

    env = dict(os.environ, GIT_INDEX_FILE=IDX)
    if os.path.exists(IDX):
        os.remove(IDX)
    git(["read-tree", tip], env=env)
    staged = []
    for src, dst in PAYLOAD:
        sha = git(["hash-object", "-w", src]).stdout.decode().strip()
        git(["update-index", "--add", "--cacheinfo", "100644,%s,%s" % (sha, dst)], env=env)
        staged.append({"path": dst, "sha": sha, "bytes": os.path.getsize(src)})
    ord_sha = git(["hash-object", "-w", os.path.join(BIGM, "results", "_r1016bmc_orders_new.md")]).stdout.decode().strip()
    git(["update-index", "--cacheinfo", "100644,%s,docs/orders.md" % ord_sha], env=env)
    tree = git(["write-tree"], env=env).stdout.decode().strip()
    cmt = git(["commit-tree", tree, "-p", tip, "-m",
               "wave3 xq: A-trial 29/29 + casting 16/16 boards+receipts (bm-c r1016) + orders receipt row"]).stdout.decode().strip()
    # deletion-set assert (no-reversal law): staged payload must be pure additions
    r = git(["diff-tree", "--no-commit-id", "--name-status", "-r", tip, cmt])
    changes = [l for l in r.stdout.decode("utf-8").splitlines() if l.strip()]
    dels = [l for l in changes if l.startswith("D")]
    assert not dels, "deletion-set non-empty: %s" % dels
    # CAS push
    pr = git(["push", "origin", cmt + ":refs/heads/main"], check=False)
    pushed = pr.returncode == 0
    if not pushed:
        sys.exit("CAS push rejected (raced): %s" % (pr.stderr or pr.stdout).decode("utf-8", "replace")[:300])
    remote = git(["ls-remote", "origin", "refs/heads/main"]).stdout.decode().split()[0]
    assert remote == cmt, "remote verify fail: %s != %s" % (remote, cmt)
    git(["update-ref", "refs/heads/main", cmt])
    rec = {"round": "r1016", "tip_before": tip, "commit": cmt, "remote_verified": remote,
           "orders_sha": ord_sha, "staged": staged, "changes": changes,
           "elapsed_sec": round(time.time() - t0, 1), "verdict": "DEPOSITED"}
    json.dump(rec, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    for k in ("commit", "orders_sha", "elapsed_sec"):
        print(k, "=", rec[k])
    print("DEPOSIT-OK")


if __name__ == "__main__":
    main()
