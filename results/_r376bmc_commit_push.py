"""r376 bm-c commit+push for W99 finalize payload.

Laws: r580/r595 (python subprocess argv, not PS native call),
r375 (commit -F file channel), r523 (push rejected on live-daemon
machine -> surgical re-parent path), r366 (ls-tree delivery proof).
"""
import subprocess
import sys

REPO = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
NO_WINDOW = 0x08000000
MSG = REPO + r"\.codely-cli\scratch\msg-r376.txt"

PAYLOAD = [
    "results/perpetual_faces/n1_w99_results.json",
    "research/PERPETUAL_N1_W99_PREREG.md",
    "results/_r376bmc_s0_surgery.py",
    "results/_r376bmc_w99_backfill_probe.py",
]


def git(*args):
    r = subprocess.run(["git", *args], cwd=REPO, capture_output=True, creationflags=NO_WINDOW)
    out = r.stdout.decode("utf-8", "replace").strip()
    err = r.stderr.decode("utf-8", "replace").strip()
    return r.returncode, out, err


def main():
    rc, out, err = git("add", "--", *PAYLOAD)
    print("add rc", rc, err[:200])
    if rc != 0:
        sys.exit(1)
    rc, out, err = git("diff", "--cached", "--stat")
    print("staged:\n", out)
    rc, out, err = git("commit", "-F", MSG)
    print("commit rc", rc, (out or err)[:300])
    if rc != 0:
        sys.exit(1)
    rc, out, err = git("rev-parse", "HEAD")
    print("HEAD", out)
    rc, out, err = git("push", "origin", "main")
    print("push rc", rc, (out or err)[:400])


if __name__ == "__main__":
    main()
