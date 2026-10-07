"""r700 bm-c S7 quartet probe: schtasks /query (authority face, R49 law) for
Bigmoney-* family + pre-commit/pre-push claw presence/parity.
Zero-window schtasks children. Lineage Tools/_r557bmc_s7_quartet.py
(byte-identical logic, round label swap only)."""
import os
import subprocess

CREATE_NO_WINDOW = 0x08000000
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def schtasks_query(task):
    r = subprocess.run(["schtasks", "/query", "/tn", task],
                       capture_output=True, creationflags=CREATE_NO_WINDOW)
    out = (r.stdout or b"").decode("gbk", "replace")
    return r.returncode, out


def main():
    family = [
        # canonical bm-c registered names: NO machine suffix (r504/r517 law)
        "Bigmoney-IterationLoop",
        "Bigmoney-LoopWatchdog",
        "Bigmoney-SaturationEngine",
        "Bigmoney-PoolWorker",
        "Bigmoney-Autofill",
        "Bigmoney-ResidentDispatcher",
        "Bigmoney-IntradayMarks",   # expected MISSING during market closure
    ]
    for t in family:
        rc, out = schtasks_query(t)
        if rc == 0:
            line = [l for l in out.splitlines() if t.lower() in l.lower()]
            m = ""
            if line:
                parts = line[0].split()
                if len(parts) >= 5:
                    m = "state=%s last=%s next=%s" % (
                        parts[3] if len(parts) > 3 else "?",
                        parts[4] if len(parts) > 4 else "?",
                        parts[5] if len(parts) > 5 else "?")
            print(f"{t}: PRESENT {m}")
        else:
            print(f"{t}: MISSING rc={rc}")

    # claws parity
    for hook, src in (("pre-commit", "pre-commit"), ("pre-push", "pre-push")):
        hp = os.path.join(ROOT, ".git", "hooks", hook)
        sp = os.path.join(ROOT, "Tools", "git-hooks", src)
        if not os.path.exists(hp):
            print(f"claw {hook}: MISSING -> register needed")
            continue
        if not os.path.exists(sp):
            print(f"claw {hook}: SRC-MISSING (tools face)")
            continue
        a = open(hp, "rb").read().replace(b"\r\n", b"\n")
        b = open(sp, "rb").read().replace(b"\r\n", b"\n")
        print(f"claw {hook}: {'IN-PLACE' if a == b else 'DIVERGED -> register needed'}")


if __name__ == "__main__":
    main()
