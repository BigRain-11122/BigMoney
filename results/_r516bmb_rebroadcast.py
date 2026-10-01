"""r516 bm-b surgical rebroadcast of commit C onto moved origin (r523 law)."""
import os
import subprocess

REPO = r"C:\Fluxgroup\FluxGroup\quant\bigmoney"
BASE = "9c57353e55"  # common ancestor: my first surgical (origin's former tip)
MSG_EXTRA = " + fresh p1d_gates daemon probe regen"


def git(args, env=None, check=True):
    e = dict(os.environ)
    if env:
        e.update(env)
    r = subprocess.run(["git", "-C", REPO] + args, capture_output=True,
                       env=e, text=True, encoding="utf-8", errors="replace")
    if check and r.returncode != 0:
        raise RuntimeError(f"git {args} rc={r.returncode}\n{r.stdout}\n{r.stderr}")
    return r


def main():
    git(["fetch", "origin"])
    payload = set(git(["diff", "--name-only", BASE, "HEAD"]).stdout.split())
    payload.add("results/p1d_gates.json")
    theirs = set(git(["diff", "--name-only", BASE, "origin/main"]).stdout.split())
    overlap = sorted(payload & theirs)
    if overlap:
        raise SystemExit("ORIGIN TOUCHED PAYLOAD (manual merge needed): "
                         + ", ".join(overlap))
    payload = sorted(payload)
    print(f"payload {len(payload)} files, overlap NONE")

    # claw on payload files (line-anchored markers, r322 law)
    for p in payload:
        with open(os.path.join(REPO, p), encoding="utf-8", errors="replace") as f:
            for i, ln in enumerate(f, 1):
                s = ln.rstrip("\r\n")
                if s.startswith("<<<<<<<") or s.startswith(">>>>>>>") or s == "=======":
                    raise SystemExit(f"CONFLICT MARKER {p}:{i}")

    idx = os.path.join(REPO, ".git", "r516bmb_temp_index2")
    env = {"GIT_INDEX_FILE": idx}
    for attempt in range(1, 4):
        if os.path.exists(idx):
            os.remove(idx)
        git(["fetch", "origin"])
        base = git(["rev-parse", "origin/main"]).stdout.strip()
        git(["read-tree", base], env=env)
        git(["add", "--"] + payload, env=env)
        tree = git(["write-tree"], env=env).stdout.strip()
        # preserve original commit message + authorship metadata
        msg = git(["log", "-1", "--format=%B", "HEAD"]).stdout
        msg = msg.rstrip("\n") + MSG_EXTRA
        r = subprocess.run(["git", "-C", REPO, "commit-tree", tree, "-p", base],
                           input=msg, capture_output=True, text=True,
                           encoding="utf-8", errors="replace")
        if r.returncode != 0:
            raise RuntimeError(r.stderr)
        sha = r.stdout.strip()
        pr = git(["push", "origin", f"{sha}:refs/heads/main"], check=False)
        if pr.returncode == 0:
            print(f"push OK attempt {attempt}: {sha[:10]} parent {base[:10]}")
            break
        print(f"push rejected attempt {attempt}, rebuilding")
    else:
        raise SystemExit("push failed after 3 attempts")
    if os.path.exists(idx):
        os.remove(idx)

    git(["reset", "--mixed", "origin/main"])
    st = git(["status", "--porcelain"]).stdout.splitlines()
    print("post-reset dirty:", len(st))
    for l in st:
        print("  ", l)
    print("REBROADCAST COMPLETE")


if __name__ == "__main__":
    main()
