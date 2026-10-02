"""r383 bm-c W115 seat publish: single-focus commit (seat MSG + probe receipt)
+ push with r589-style retry (reset-FF-reland on origin advance)."""
import subprocess, sys, os
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
CN = 0x08000000
MSG = r"K:\Fluxgroup\FluxGroup\quant\.codely-cli\scratch\msg_r383_w115_seat.txt"
PAYLOAD = ["fleet/inbox/MSG-20261002-2130-bmc-w115-seat.md",
           "results/_r383bmc_w115_probe.py"]


def git(*args, check=True):
    r = subprocess.run(["git", "-C", ROOT] + list(args), capture_output=True,
                       encoding="utf-8", errors="replace", creationflags=CN)
    if check and r.returncode != 0:
        raise SystemExit(f"git {args[:2]} rc={r.returncode}: {r.stderr[:400]}")
    return r


def one_pass(tag):
    git("add", *PAYLOAD)
    staged = git("diff", "--cached", "--name-only").stdout.split()
    assert set(staged) == set(PAYLOAD), staged
    git("commit", "-F", MSG)
    sha = git("log", "-1", "--format=%h").stdout.strip()
    r = git("push", check=False)
    print(f"[{tag}] commit {sha} push rc={r.returncode} "
          f"{(r.stdout or r.stderr).strip()[:160]}")
    return r.returncode == 0


rc = one_pass("try1")
if not rc:
    # r589 reloop: uncommit, FF to fresh origin, re-land
    git("reset", "--mixed", "HEAD~1")
    git("fetch", "origin")
    origin_sha = git("rev-parse", "origin/main").stdout.strip()
    # blocker files: anything dirty that the new origin commit touches gets
    # checked out to base first (base == current HEAD after reset)
    r = git("merge", "--ff-only", origin_sha, check=False)
    if r.returncode != 0:
        print("FF refused:", r.stderr[:300])
        # restore blockers to HEAD versions then retry FF
        por = git("status", "--porcelain").stdout
        print("status snapshot:", por[:500])
        raise SystemExit("manual follow-up needed")
    rc = one_pass("try2")

if not rc:
    raise SystemExit("seat push failed twice -- manual follow-up")

git("fetch", "origin")
ahead = int(git("rev-list", "--count", "origin/main..HEAD").stdout.strip())
behind = int(git("rev-list", "--count", "HEAD..origin/main").stdout.strip())
print(f"settled: ahead={ahead} behind={behind}")
assert ahead == 0 and behind == 0
ls = git("ls-tree", "--name-only", "origin/main", "--",
         "fleet/inbox/MSG-20261002-2130-bmc-w115-seat.md").stdout.strip()
assert "MSG-20261002-2130-bmc-w115-seat.md" in ls, "seat MSG not on origin"
print("SEAT DELIVERY VERIFIED: W115 seat + probe receipt on origin")
