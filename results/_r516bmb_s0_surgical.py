"""r516 bm-b S0 surgical integration onto origin (r523 law path).

Adopts r515 crashed-session tail (perpetual_faces_n1.py derive fix, verified
compile+selftest PASS) + W16 shards 3-11/12 in-flight products + bm-b lane
rides. Payload files are asserted untouched-by-origin (old HEAD ==
origin/main for those paths) before inclusion; push retry loop rebuilds the
temp index if origin moves mid-window.
"""
import json
import os
import subprocess
import sys

REPO = r"C:\Fluxgroup\FluxGroup\quant\bigmoney"
PAYLOAD = [
    "scripts/perpetual_faces_n1.py",
    "logs/iteration-loop/round_reports.md",
    "state.json",
    "fleet/machines/bm-b.json",
    "results/pool_core_samples.jsonl",
    "results/astock_daily_update_status.json",
    "results/etf_daily_pull_status.json",
    "results/autofill_state.bm-b.json",
    "results/compute_audit.bm-b.json",
    "results/pool_dualrun.bm-b.jsonl",
    "results/regime_state.bm-b.json",
    "results/token_usage.bm-b.json",
    "results/update_status.bm-b.json",
    "results/futures_update_status.bm-b.json",
    "results/lhb_update_status.bm-b.json",
    "results/saturation_engine/face_bm-b.json",
    "results/saturation_engine/history_bm-b.jsonl",
    "results/saturation_engine/ledger_bm-b.jsonl",
    "results/saturation_engine/state_bm-b.json",
] + [
    f"results/p2cal_ext/n1_w16/shard-{k}-of-12.json" for k in range(3, 12)
]
# tracked, modified, but NOT ours to publish: stale regen faces (origin newer),
# in-flight p1d_gates.json (daemon batch running now). Left in tree.
SKIP_CHECKOUT = {"results/p1d_gates.json"}
MSG = ("round 516 S0 surgical: adopt r515 crashed-session tail "
       "(perpetual_faces_n1.py W16 finalize derive-law fix, compile+selftest "
       "PASS) + W16 shards 3-11/12 in-flight products (12/12 complete on disk, "
       "audit.machine=bm-b all) + bm-b engine/lane rides onto 1c34788cf "
       "[via bm-b]")


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
    # 0. conflict-marker claw on payload text files (commit-tree bypasses hooks)
    for p in PAYLOAD:
        fp = os.path.join(REPO, p)
        if not os.path.exists(fp):
            raise SystemExit(f"PAYLOAD MISSING: {p}")
        with open(fp, encoding="utf-8", errors="replace") as f:
            lines = f.readlines()
        for i, ln in enumerate(lines, 1):
            s = ln.rstrip("\r\n")
            # line-anchored real conflict markers only (r322: prose arrows
            # inside historical ledger lines are legal content)
            if s.startswith("<<<<<<<") or s.startswith(">>>>>>>") or s == "=======":
                raise SystemExit(f"CONFLICT MARKER {fp}:{i}: {s[:60]}")
    print(f"claw: {len(PAYLOAD)} payload files clean")

    head = git(["rev-parse", "HEAD"]).stdout.strip()
    # 1. per-file origin-overlap assertion (r507 law)
    touched = []
    for p in PAYLOAD:
        a = git(["rev-parse", f"{head}:{p}"], check=False)
        b = git(["rev-parse", f"origin/main:{p}"], check=False)
        if a.returncode == 0 and b.returncode == 0 and a.stdout.strip() != b.stdout.strip():
            touched.append(p)
    if touched:
        raise SystemExit("ORIGIN TOUCHED PAYLOAD (needs manual merge): "
                         + ", ".join(touched))
    print("origin-overlap assertion: PASS (payload untouched by origin)")

    # 2. capture dirty set BEFORE any reset (for post-reset checkout list)
    st = git(["status", "--porcelain"]).stdout.splitlines()
    checkout = []
    for line in st:
        code, path = line[:2], line[3:].strip().strip('"')
        if code.strip() == "D":
            checkout.append(path)
            continue
        if path in SKIP_CHECKOUT or path in PAYLOAD:
            continue
        if code.strip() == "M":
            checkout.append(path)
    with open(os.path.join(REPO, "results", "_r516bmb_checkout_list.txt"),
              "w", encoding="utf-8") as f:
        f.write("\n".join(checkout))
    print(f"post-reset checkout queue: {len(checkout)} files")

    # 3. surgical commit with push-retry loop
    idx = os.path.join(REPO, ".git", "r516bmb_temp_index")
    env = {"GIT_INDEX_FILE": idx}
    for attempt in range(1, 4):
        if os.path.exists(idx):
            os.remove(idx)
        git(["fetch", "origin"])
        base = git(["rev-parse", "origin/main"]).stdout.strip()
        git(["read-tree", base], env=env)
        git(["add", "--"] + PAYLOAD, env=env)
        tree = git(["write-tree"], env=env).stdout.strip()
        sha = subprocess.run(
            ["git", "-C", REPO, "commit-tree", tree, "-p", base, "-m", MSG],
            capture_output=True, text=True, encoding="utf-8",
            errors="replace", check=True).stdout.strip()
        r = git(["push", "origin", f"{sha}:refs/heads/main"], check=False)
        if r.returncode == 0:
            print(f"push OK attempt {attempt}: {sha[:10]} parent {base[:10]}")
            break
        print(f"push rejected attempt {attempt} (origin moved), rebuilding")
    else:
        raise SystemExit("push failed after 3 attempts")
    if os.path.exists(idx):
        os.remove(idx)

    # 4. re-anchor + sync non-payload faces from origin (r296-3 / r523 tail)
    git(["fetch", "origin"])
    new = git(["rev-parse", "origin/main"]).stdout.strip()
    if new != sha:
        raise SystemExit(f"origin/main {new[:10]} != pushed {sha[:10]}")
    git(["reset", "--mixed", "origin/main"])
    with open(os.path.join(REPO, "results", "_r516bmb_checkout_list.txt"),
              encoding="utf-8") as f:
        paths = [p for p in f.read().splitlines() if p]
    for p in paths:
        git(["checkout", "--", p])
    print(f"checkout restored: {len(paths)} non-payload faces")

    # 5. report
    st2 = git(["status", "--porcelain"]).stdout.splitlines()
    print("post-surgical dirty entries:", len(st2))
    for line in st2:
        print("  ", line)
    print("S0 SURGICAL COMPLETE")


if __name__ == "__main__":
    main()
