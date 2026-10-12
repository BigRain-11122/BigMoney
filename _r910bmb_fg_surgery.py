"""r910 bm-b: FluxGroup CAS plumbing surgery RETRY-2 (zero tree touch).

Lineage: _r908bmb_fg_surgery.py (v1). v1 attempt-3 wedged at `git write-tree`
child (0 CPU for 34min, spawned 00:28:29; killed r910 01:0x). v2 changes ONLY:
  - fresh temp-index name _r910bmb_fg_index (avoid any cursed state bound to
    the _r908bmb_fg_index filename / leaked handle)
  - fsmonitor/untrackedCache bypass via -c core.fsmonitor=false -c
    core.untrackedCache=false on every git call (startup-handshake hang
    candidate root cause)
  - completion receipt JSON written at end (trivial next-round verify)
Payload identical to v1: (1) re-land POOL-SCORED-20261012.md into cph4 topics,
(2) append bm-b first row to token LEDGER. CAS: read-tree tip -> hash-object
-> update-index --cacheinfo SPACE form (r739 law) -> write-tree -> commit-tree
-> push origin <sha>:refs/heads/main. Fail-closed diff-set assertion pre-push.
"""
import json
import os
import re
import subprocess
import sys

GROUP = r"C:\Fluxgroup\FluxGroup"
REPO = os.path.dirname(os.path.abspath(__file__))
POOL_SRC = os.path.join(REPO, "results", "pool_scored", "POOL-SCORED-20261012.md")
LEDGER = "cph4/fleet/token-ledger/LEDGER.md"
TOPICS_F = "cph4/fleet/meme-daily-v1/topics/POOL-SCORED-20261012.md"
TMP_IDX = os.path.join(os.environ.get("TEMP", "."), "_r910bmb_fg_index")
RECEIPT = os.path.join(REPO, "results", "_r910bmb_fg_surgery_receipt.json")
NOFS = ["-c", "core.fsmonitor=false", "-c", "core.untrackedCache=false"]


def git(args, env=None, check=True):
    r = subprocess.run(["git", "-C", GROUP] + NOFS + args, capture_output=True,
                       text=True, env=env)
    if check and r.returncode != 0:
        raise RuntimeError("git %s rc=%d: %s" % (args, r.returncode,
                                                 (r.stderr or "")[:400]))
    return r


def main():
    git(["fetch", "origin"])
    tip = git(["rev-parse", "origin/main"]).stdout.strip()
    env = dict(os.environ, GIT_INDEX_FILE=TMP_IDX)

    # ---- (1) POOL-SCORED add-only commit ----
    for p in (TMP_IDX, TMP_IDX + ".lock"):
        if os.path.exists(p):
            os.remove(p)
    blob = git(["hash-object", "-w", POOL_SRC]).stdout.strip()
    git(["read-tree", tip], env=env)
    git(["update-index", "--add", "--cacheinfo", "100644", blob, TOPICS_F],
        env=env)
    tree1 = git(["write-tree"], env=env).stdout.strip()
    c1 = git(["commit-tree", tree1, "-p", tip, "-m",
              "bm-b O-1917 S3 POOL-SCORED-20261012 topics add-only delivery "
              "re-land (PID7668 killed by 10-12 03:03 power outage before "
              "landing; byte-source bigmoney results/pool_scored) "
              "[via bm-b r910]"]).stdout.strip()

    # ---- (2) token ledger row append ----
    for p in (TMP_IDX, TMP_IDX + ".lock"):
        if os.path.exists(p):
            os.remove(p)
    if git(["cat-file", "-e", tip + ":" + LEDGER], check=False).returncode != 0:
        raise RuntimeError("LEDGER.md not on tip -- abort")
    b = subprocess.run(["git", "-C", GROUP] + NOFS + ["show", tip + ":" + LEDGER],
                       capture_output=True).stdout
    text = b.decode("utf-8")
    row = ("| 10-13 | BigMoney 循环 | 云端 LLM 轮班 | Bigmoney-IterationLoop "
           "r907-r908（掉电恢复双轮） | 记录待补 | 无人值守迭代（本地 flash 线 "
           "keepwarm.pause 让路 i2v 批=零本地替代） | smoke 49/49+轮报告心跳推送"
           "+S6 41 腿全绿 | 零云端生成任务（i2v 批=本地 INT4·GPU 100%） |\n")
    lines = text.splitlines(keepends=True)
    idx = None
    for i, ln in enumerate(lines):
        if re.match(r"^\|\s*10-\d", ln):
            idx = i
    if idx is None:
        raise RuntimeError("no dated ledger row found -- abort append")
    out = "".join(lines[:idx + 1]) + row + "".join(lines[idx + 1:])
    outb = out.encode("utf-8")
    tmpf = TMP_IDX + ".blob"
    with open(tmpf, "wb") as f:
        f.write(outb)
    blob2 = git(["hash-object", "-w", tmpf]).stdout.strip()
    os.remove(tmpf)
    git(["read-tree", c1], env=env)
    git(["update-index", "--cacheinfo", "100644", blob2, LEDGER], env=env)
    tree2 = git(["write-tree"], env=env).stdout.strip()
    c2 = git(["commit-tree", tree2, "-p", c1, "-m",
              "bm-b token-ledger first row (C-20261012-02 S5-L4 ledger law; "
              "bm-b was dark 03:03-22:16 during law's effective window) "
              "[via bm-b r910]"]).stdout.strip()

    # ---- fail-closed verification before push ----
    ds = git(["diff", "--name-status", tip, c2]).stdout.strip().splitlines()
    expect = {"A\t" + TOPICS_F, "M\t" + LEDGER}
    if set(ds) != expect:
        raise RuntimeError("diff-set mismatch: %r vs %r" % (ds, sorted(expect)))

    git(["push", "origin", c2 + ":refs/heads/main"])
    git(["fetch", "origin"])
    new_tip = git(["rev-parse", "origin/main"]).stdout.strip()
    ok = new_tip == c2
    ls = git(["ls-tree", "origin/main", TOPICS_F, LEDGER]).stdout.strip()
    print("PUSHED %s ok=%s" % (c2, ok))
    print("LS-TREE: %s" % ls)
    with open(RECEIPT, "w", encoding="utf-8") as f:
        json.dump({"ts": os.environ.get("COMPUTERNAME", "") and __import__("time").strftime("%Y-%m-%dT%H:%M:%S"),
                   "pushed": c2, "tip_after": new_tip, "ok": ok,
                   "ls_tree": ls, "tip_before": tip}, f, ensure_ascii=False, indent=1)
    for p in (TMP_IDX, TMP_IDX + ".lock"):
        if os.path.exists(p):
            os.remove(p)
    if not ok:
        raise RuntimeError("origin tip != pushed commit")
    return 0


if __name__ == "__main__":
    sys.exit(main())
