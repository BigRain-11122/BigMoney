"""r730 bm-c close commit: deterministic product-face adds first (r549
stale-untrackedCache law), add -u for own regen faces, commit -F fresh
message file (r689/r591 laws), explicit two-step fetch+rebase (r586 law,
no autostash per r789), push origin explicit (r849 law), delivery proof
rev-list + ls-remote. Daemon live-write race fallback: treasure_guard-gated
checkout of unstaged live faces then retry rebase once."""
import os
import subprocess
import sys

REPO = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
MSG = os.path.join(REPO, "_r730bmc_commitmsg2.txt")

PRODUCTS = [
    "qa/smoke-r730.md", "qa/equity-curve-r730.png",
    "Tools/_r730bmc_s0.py", "Tools/_r730bmc_s05.py", "Tools/_r730bmc_s6.py",
    "Tools/_r730bmc_qa_ignite.py", "Tools/_r730bmc_close.py",
    "results/_r730bmc_s05_facts.json", "results/_r730bmc_s6_log.txt",
    "results/_r730bmc_qa_runner.out", "results/_r730bmc_qa_runner.err",
    "results/_r730bmc_rr_tail.txt", "_r730bmc_commitmsg.txt",
]


def git(args, check=True):
    p = subprocess.run(["git", "-C", REPO] + args, capture_output=True)
    out = p.stdout.decode("utf-8", "replace")
    err = p.stderr.decode("utf-8", "replace")
    print("git %s rc=%d" % (args[0], p.returncode))
    if out.strip():
        print(out.strip()[:400])
    if err.strip():
        print("STDERR:", err.strip()[:400])
    if check and p.returncode != 0:
        return p
    return p


def hard(args):
    p = git(args)
    if p.returncode != 0:
        print("HARD FAIL:", " ".join(args))
        sys.exit(p.returncode)
    return p


def main():
    for t in PRODUCTS:
        hard(["add", "--", t])
    hard(["add", "-u"])
    cached = git(["diff", "--cached", "--name-only"])
    names = [l for l in cached.stdout.decode("utf-8", "replace").splitlines() if l.strip()]
    print("staged %d files" % len(names))
    with open(MSG, "w", encoding="utf-8", newline="\n") as f:
        f.write("round 730: QA det-50th 5/5 + S6 40/40 rc0 (dualrun streak 50) "
                "+ 5x HANDOVER window line r726-730 + S0 clean window "
                "(absorb 3789dc0a3, treasure_guard-gated checkout, three-way "
                "delivery proof)\n")
    hard(["commit", "-F", MSG])

    # two-step integration (r586 law), no autostash (r789 law)
    hard(["fetch", "origin"])
    rb = git(["rebase", "origin/main"])
    if rb.returncode != 0:
        # daemon live-write race fallback: gate unstaged live faces then checkout
        df = git(["diff", "--name-only"])
        dirty = [l for l in df.stdout.decode("utf-8", "replace").splitlines() if l.strip()]
        print("unstaged dirty faces:", dirty)
        if dirty:
            tg = subprocess.run([sys.executable, os.path.join(REPO, "Tools", "treasure_guard.py"),
                                 "restore"] + dirty, capture_output=True)
            print("treasure_guard rc=%d" % tg.returncode)
            if tg.returncode != 0:
                print(tg.stdout.decode("utf-8", "replace")[-300:])
                print("TREASURE GUARD REFUSED - manual review required")
                sys.exit(3)
            rb2 = git(["rebase", "origin/main"])
            if rb2.returncode != 0:
                print("REBASE STILL FAILING - honest stop, no force, no autostash")
                sys.exit(4)
    p = git(["push", "origin", "main"])
    if p.returncode != 0:
        print("PUSH REJECTED - honest stop, no force, no autostash")
        sys.exit(5)
    hard(["fetch", "origin"])
    behind = git(["rev-list", "--count", "HEAD..origin/main"]).stdout.decode().strip()
    ahead = git(["rev-list", "--count", "origin/main..HEAD"]).stdout.decode().strip()
    head = git(["rev-parse", "HEAD"]).stdout.decode().strip()
    remote = git(["ls-remote", "origin", "refs/heads/main"]).stdout.decode().strip()
    print("DELIVERY PROOF: HEAD=%s behind=%s ahead=%s" % (head[:12], behind, ahead))
    print("REMOTE: %s" % remote[:80])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
