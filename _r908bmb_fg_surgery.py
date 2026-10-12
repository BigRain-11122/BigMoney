"""r908 bm-b: FluxGroup CAS plumbing surgery (zero tree touch, r909 O-push lineage).

(1) Re-land POOL-SCORED-20261012.md into cph4/fleet/meme-daily-v1/topics/
    (O-20261011-1917 S3 delivery; surgical push PID7668 was killed by the
    10-12 03:03 power outage before landing; local byte-source =
    results/pool_scored/POOL-SCORED-20261012.md in this repo).
(2) Append bm-b first row to cph4/fleet/token-ledger/LEDGER.md
    (C-20261012-02 S5-L4 ledger law, in force since 10-12 15:1x while bm-b
    was dark -- first bm-b compliance row).

Method: temp-index CAS (read-tree tip -> hash-object -w -> update-index
--cacheinfo SPACE form per r739 comma-form-rejection law -> write-tree ->
commit-tree -> push origin <sha>:refs/heads/main). No checkout, no worktree,
zero touches to the shared group tree. Fail-closed assertions before push:
tree-vs-tip name-status must equal exactly the intended file set.
"""
import os
import re
import subprocess
import sys

GROUP = r"C:\Fluxgroup\FluxGroup"
REPO = os.path.dirname(os.path.abspath(__file__))
POOL_SRC = os.path.join(REPO, "results", "pool_scored", "POOL-SCORED-20261012.md")
LEDGER = "cph4/fleet/token-ledger/LEDGER.md"
TOPICS_F = "cph4/fleet/meme-daily-v1/topics/POOL-SCORED-20261012.md"
TMP_IDX = os.path.join(os.environ.get("TEMP", "."), "_r908bmb_fg_index")


def git(args, env=None, check=True):
    r = subprocess.run(["git", "-C", GROUP] + args, capture_output=True,
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
    if os.path.exists(TMP_IDX):
        os.remove(TMP_IDX)
    blob = git(["hash-object", "-w", POOL_SRC]).stdout.strip()
    git(["read-tree", tip], env=env)
    git(["update-index", "--add", "--cacheinfo", "100644", blob, TOPICS_F],
        env=env)
    tree1 = git(["write-tree"], env=env).stdout.strip()
    c1 = git(["commit-tree", tree1, "-p", tip, "-m",
              "bm-b O-1917 S3 POOL-SCORED-20261012 topics add-only delivery "
              "re-land (PID7668 killed by 10-12 03:03 power outage before "
              "landing; byte-source bigmoney results/pool_scored) "
              "[via bm-b r908]"]).stdout.strip()

    # ---- (2) token ledger row append ----
    if os.path.exists(TMP_IDX):
        os.remove(TMP_IDX)
    ledger_bytes = git(["cat-file", "-p", tip + ":" + LEDGER],
                       check=False).stdout
    if git(["cat-file", "-p", tip + ":" + LEDGER], check=False).returncode != 0:
        raise RuntimeError("LEDGER.md not on tip -- abort")
    raw = git(["show", tip + ":" + LEDGER])
    text = raw.stdout
    if hasattr(raw.stdout, "encode"):
        pass
    # get bytes properly (avoid console decode loss)
    b = subprocess.run(["git", "-C", GROUP, "show", tip + ":" + LEDGER],
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
              "[via bm-b r908]"]).stdout.strip()

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
    if os.path.exists(TMP_IDX):
        os.remove(TMP_IDX)
    if not ok:
        raise RuntimeError("origin tip != pushed commit")
    return 0


if __name__ == "__main__":
    sys.exit(main())
