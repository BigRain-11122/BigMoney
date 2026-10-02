"""r383 bm-c W115 seat re-land over the GM-session twin yield: local
9dcf64274 tree == origin tree (empty diff verified) -> reset --mixed to
origin is a pure re-anchor (zero loss). Then re-land seat payload."""
import subprocess, sys
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


# yield-verify (fail-closed): stranded twin tree must equal origin tree
d = git("diff", "--stat", "9dcf64274", "origin/main").stdout.strip()
assert d == "", f"twin yield NOT safe, diff: {d[:300]}"
git("reset", "--mixed", git("rev-parse", "origin/main").stdout.strip())
print("re-anchored to origin:", git("log", "-1", "--format=%h").stdout.strip())

git("add", *PAYLOAD)
staged = git("diff", "--cached", "--name-only").stdout.split()
assert set(staged) == set(PAYLOAD), staged
git("commit", "-F", MSG)
sha = git("log", "-1", "--format=%h").stdout.strip()
r = git("push", check=False)
print(f"commit {sha} push rc={r.returncode}: {(r.stdout or r.stderr).strip()[:200]}")
if r.returncode != 0:
    raise SystemExit("push rejected again -- concurrent writer active, retry next round")

git("fetch", "origin")
ahead = int(git("rev-list", "--count", "origin/main..HEAD").stdout.strip())
behind = int(git("rev-list", "--count", "HEAD..origin/main").stdout.strip())
print(f"settled: ahead={ahead} behind={behind}")
assert ahead == 0 and behind == 0
ls = git("ls-tree", "--name-only", "origin/main", "--",
         "fleet/inbox/MSG-20261002-2130-bmc-w115-seat.md").stdout.strip()
assert "MSG-20261002-2130-bmc-w115-seat.md" in ls
print("SEAT DELIVERY VERIFIED: W115 seat + probe receipt on origin")
