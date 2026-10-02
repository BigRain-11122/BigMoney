"""r376 bm-c surgical re-parent after pre-push claw divergence block (r366 family).

Path: fetch -> verify divergence -> check payload∩incoming collision ->
read-tree new base -> inject my 4 payload blobs -> commit-tree -p new_base ->
push sha:main (claw-natural: payload adds only, deletes none) ->
ls-tree delivery proof.
"""
import subprocess
import sys

REPO = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
NO_WINDOW = 0x08000000
PAYLOAD = [
    "results/perpetual_faces/n1_w99_results.json",
    "research/PERPETUAL_N1_W99_PREREG.md",
    "results/_r376bmc_s0_surgery.py",
    "results/_r376bmc_w99_backfill_probe.py",
]
MY_COMMIT = "61a0f132bc85ed39725bcb2db99fde493a3aea14"


def git(*args, check=True):
    r = subprocess.run(["git", *args], cwd=REPO, capture_output=True, creationflags=NO_WINDOW)
    out = r.stdout.decode("utf-8", "replace").strip()
    err = r.stderr.decode("utf-8", "replace").strip()
    if check and r.returncode != 0:
        print("GITFAIL", list(args), r.returncode, err[:400])
        sys.exit(1)
    return r.returncode, out, err


def main():
    git("fetch", "origin")
    rc, new_base, _ = git("rev-parse", "origin/main")
    rc, out, _ = git("log", "--oneline", f"fbbde996f..{new_base}")
    print("incoming since my base fbbde996f:")
    print(out)
    # collision check: did incoming commits touch my payload files?
    for p in PAYLOAD:
        rc, out, err = git("diff", "--name-only", f"fbbde996f..{new_base}", "--", p, check=False)
        touched = bool(out.strip())
        print(f"payload {p}: incoming_touches={touched}")
    # my payload blobs from my commit tree
    rc, my_tree, _ = git("rev-parse", f"{MY_COMMIT}^{{tree}}")
    blobs = {}
    for p in PAYLOAD:
        rc, sha, _ = git("rev-parse", f"{MY_COMMIT}:{p}")
        blobs[p] = sha
    # build surgical tree: new_base tree + my blobs
    git("read-tree", new_base)
    for p in PAYLOAD:
        rc, mode, _ = git("ls-tree", MY_COMMIT, "--", p)
        # fixed-column parse: mode SP type SP sha TAB path (r366 law)
        parts = mode.split()
        m = parts[0]
        git("update-index", "--add", "--cacheinfo", f"{m},{blobs[p]},{p}")
    rc, tree, _ = git("write-tree")
    print("surgical tree:", tree)
    # assertions: deletion set empty (payload only adds/overwrites own files)
    rc, out, _ = git("diff-tree", "--name-status", "-r", new_base, tree)
    print("tree delta vs new_base:")
    print(out)
    deltas = [l for l in out.splitlines() if l.strip()]
    bad = [l for l in deltas if l.startswith("D")]
    assert not bad, f"DELETION SET non-empty: {bad}"
    for l in deltas:
        st, path = l.split("\t")[0], l.split("\t")[-1]
        assert path in PAYLOAD, f"unexpected delta {l}"
        print("delta-ok:", st, path)
    rc, new_commit, _ = git("commit-tree", tree, "-p", new_base, "-F",
                            REPO + r"\.codely-cli\scratch\msg-r376.txt")
    print("surgical commit:", new_commit)
    rc, out, err = git("push", "origin", f"{new_commit}:refs/heads/main", check=False)
    print("push rc", rc, (out or err)[:300])
    if rc != 0:
        sys.exit(1)
    # delivery proof
    git("fetch", "origin")
    for p in PAYLOAD:
        rc, out, _ = git("ls-tree", "origin/main", "--", p)
        print("delivered:", out)
    rc, out, _ = git("rev-parse", "origin/main")
    print("origin/main now:", out)


if __name__ == "__main__":
    main()
