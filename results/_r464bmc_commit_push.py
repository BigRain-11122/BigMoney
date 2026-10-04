"""r464 bm-c S7 commit+push driver: targeted add of round outputs + own lane
faces (round-start was dirty -> no add -A, per commit discipline), defensive
owner-guard on staged set, commit, then delivery via Tools/push_verify.py
single-source (r436-2 law). Receipt -> results/_r464bmc_push_receipt.txt."""
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CREATE = 0x08000000
RECEIPT = os.path.join(ROOT, "results", "_r464bmc_push_receipt.txt")

# Other-machine-owned faces: must never appear in my staged set.
FOREIGN_PREFIXES = (
    "state-bm-a.json", "state.json", "round_reports-bm-a.md", "round_reports.md",
    "fleet/machines/bm-a.json", "fleet/machines/bm-b.json",
    "results/fund_value_p1/", "results/fund_quality_p1/",
    "results/fund_divlowvol_p1/", "logs/iteration-loop/",
)
FOREIGN_EXACT = set(FOREIGN_PREFIXES)

MSG = ("round 464: golden-week watch, fund-trio V715/Q551/D404 owners healthy "
       "(keepalive 12min); quiet S0 (tree at tip 2660efdf7, behind=0); S6 38/38 rc0; "
       "orders/D-19 double MATCH; one pit line (PS trailing-& backgrounding)")


def git(*a):
    p = subprocess.run(["git"] + list(a), capture_output=True, cwd=ROOT,
                       creationflags=CREATE)
    return p.returncode, (p.stdout or b"").decode("utf-8", "replace"), \
        (p.stderr or b"").decode("utf-8", "replace")


def main():
    rc, out, err = git("status", "--porcelain")
    assert rc == 0, "status fail"
    paths = []
    for ln in out.splitlines():
        if not ln.strip():
            continue
        st, p = ln[:2], ln[3:].strip().strip('"')
        if p.startswith("results/_r464bmc_push_receipt.txt"):
            continue  # receipt written after push, next-round absorb
        for fp in FOREIGN_PREFIXES:
            if p == fp or (fp.endswith("/") and p.startswith(fp)):
                raise SystemExit("FOREIGN FACE IN DIRTY SET, ABORT: " + p)
        paths.append(p)
    assert paths, "nothing to add?"
    rc, out, err = git("add", "--", *paths)
    assert rc == 0, "add fail: " + err[:300]
    rc, out, err = git("diff", "--cached", "--name-only")
    staged = [x for x in out.splitlines() if x.strip()]
    assert sorted(staged) == sorted(paths), "staged set mismatch"
    rc, out, err = git("commit", "-m", MSG)
    print("COMMIT_RC", rc)
    print(out.strip()[:300])
    if rc != 0:
        print(err.strip()[:300])
        sys.exit(1)
    # delivery: single-source push_verify (pushes + fetch + ahead==0 proof)
    pr = subprocess.run([sys.executable, "Tools/push_verify.py"],
                        capture_output=True, cwd=ROOT, creationflags=CREATE)
    ptxt = ((pr.stdout or b"").decode("utf-8", "replace") + " || " +
            (pr.stderr or b"").decode("utf-8", "replace"))
    with open(RECEIPT, "w", encoding="utf-8", newline="\n") as f:
        f.write(ptxt)
    print("PUSH_VERIFY_RC", pr.returncode)
    print(ptxt[-600:])
    sys.exit(pr.returncode if pr.returncode in (0, 1) else 2)


if __name__ == "__main__":
    main()
