"""r457 bm-c S7 checks: loop task / watchdog presence (schtasks via zero-window),
claw parity (CR-normalized), attrition guard scan, orders S7 double-scan.
Read-only probes; repair actions decided by caller."""
import os
import subprocess

CREATE_NO_WINDOW = 0x08000000
ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"


def run(args, cwd=ROOT, timeout=120):
    r = subprocess.run(args, capture_output=True, cwd=cwd,
                       creationflags=CREATE_NO_WINDOW, timeout=timeout)
    return r.returncode, (r.stdout or b"").decode("utf-8", "replace"), \
        (r.stderr or b"").decode("utf-8", "replace")


def claw_parity(hook, src):
    p = os.path.join(ROOT, ".git", "hooks", hook)
    if not os.path.exists(p):
        return "MISSING"
    with open(p, "rb") as fh:
        a = fh.read().replace(b"\r\n", b"\n")
    with open(os.path.join(ROOT, "Tools", "git-hooks", src), "rb") as fh:
        b = fh.read().replace(b"\r\n", b"\n")
    return "TRUE" if a == b else "DRIFT"


def main():
    rc, out, err = run(["schtasks", "/query", "/tn", "Bigmoney-IterationLoop", "/fo", "LIST"])
    print("LOOP-TASK rc=%d live=%s" % (rc, "Bigmoney-IterationLoop" in out))
    rc, out, err = run(["schtasks", "/query", "/tn", "Bigmoney-LoopWatchdog", "/fo", "LIST"])
    print("WATCHDOG rc=%d live=%s" % (rc, "Bigmoney-LoopWatchdog" in out))
    print("PRECOMMIT-CLAW %s" % claw_parity("pre-commit", "pre-commit"))
    print("PREPUSH-CLAW %s" % claw_parity("pre-push", "pre-push"))
    rc, out, err = run(["python", "scripts\\attrition_ledger_guard.py", "scan"], timeout=180)
    print("ATTRITION rc=%d | %s" % (rc, (out + err).strip().splitlines()[-1] if (out + err).strip() else "?"))
    rc, out, err = run(["python", "Tools\\orders_diff.py"], timeout=60)
    print("ORDERS-S7-DOUBLESCAN rc=%d | %s" % (rc, (out + err).strip()[:120]))


if __name__ == "__main__":
    main()
