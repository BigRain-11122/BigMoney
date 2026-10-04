"""r457 bm-c surgery commit+push: targeted add (pool face + MSG + 18 receipts),
commit, push, push_verify single-source delivery check (r436 law)."""
import os
import subprocess

CREATE_NO_WINDOW = 0x08000000
ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
ADD = (["results/runnable_pool.json",
        "fleet/inbox/MSG-2026-10-04-0915-bmc-bmb.md"] +
       ["results/_r457bmc_%s" % n for n in (
        "s0.py", "s0b.py", "s0c.py", "resync.py", "absorb2.py", "s3probe.py",
        "poolprobe.py", "poolprobe2.py", "fundnulls_watch.py",
        "quality_forensics.py", "quality_forensics2.py", "quality_forensics3.py",
        "quality_forensics4.py", "quality_forensics5.py", "quality_forensics6.py",
        "restore_preprobe.py", "pool_surgery.py", "surgery_debug.py")])
MSG = ("r457 bm-c (S3): pool surgery FUND-QUALITY-P1-NULLS owner row restored to bm-b "
       "(r637 four-face surgery missed 3rd shard; canonical burner pid 57116 alive per "
       "MSG-0857/0925/2005 + row growth 504->510; r288 keepalive self-adoption unlocked; "
       "laws r509 raw-text/r629 comma/r400 action-time; gates needle==1+reparse+trio-delta+"
       "numstat 3/1+treasure_guard rc0) + MSG-0915 advisory to bm-b + S0/S3 forensics receipts")


def git(args):
    r = subprocess.run(["git"] + args, capture_output=True, cwd=ROOT,
                       creationflags=CREATE_NO_WINDOW)
    return r.returncode, (r.stdout or b"").decode("utf-8", "replace"), \
        (r.stderr or b"").decode("utf-8", "replace")


def main():
    missing = [f for f in ADD if not os.path.exists(f.replace("/", os.sep))]
    if missing:
        print("ABORT missing files: %s" % missing)
        return
    rc, out, err = git(["add"] + ADD)
    print("ADD rc=%d %s" % (rc, err.strip()[:100]))
    rc, st, _ = git(["diff", "--cached", "--name-only"])
    staged = sorted(l.strip() for l in st.splitlines() if l.strip())
    if staged != sorted(ADD):
        print("ABORT staged mismatch:\n  %s" % "\n  ".join(set(staged) ^ set(ADD)))
        git(["reset"])
        return
    print("STAGED OK %d files" % len(staged))
    rc, out, err = git(["commit", "-m", MSG])
    print("COMMIT rc=%d %s" % (rc, (out + err).strip()[:180]))
    rc, out, err = git(["push"])
    print("PUSH rc=%d" % rc)
    print((out + err).strip()[-500:])
    # single-source delivery verify (r436: ahead==0 after fetch)
    r = subprocess.run(["python", "Tools\\push_verify.py"], capture_output=True,
                       cwd=ROOT, creationflags=CREATE_NO_WINDOW)
    print("PUSH_VERIFY rc=%d" % r.returncode)
    print(((r.stdout or b"") + (r.stderr or b"")).decode("utf-8", "replace").strip()[-400:])


if __name__ == "__main__":
    main()
