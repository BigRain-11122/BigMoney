"""r464 bm-c final absorb: delivered-receipt3 + second-scan evidence +
treadmilled satengine lane faces, then push_verify. If raced: report, do NOT
force (next merge cycle is next round's S0 netpath)."""
import subprocess
import sys

C = 0x08000000


def git(*a):
    p = subprocess.run(["git"] + list(a), capture_output=True, creationflags=C,
                       cwd=".")
    return p.returncode, (p.stdout or b"").decode("utf-8", "replace"), \
        (p.stderr or b"").decode("utf-8", "replace")


PATHS = [
    "results/_r464bmc_push_receipt3.txt",
    "results/_r464bmc_orders_diff.json",
    "results/saturation_engine/face_bm-c.json",
    "results/saturation_engine_state.bm-c.json",
    "results/_r464bmc_final_absorb.py",
]
MSG = ("absorb r464 bm-c: DELIVERED receipt3 (tip c3be28c20 ahead=0/behind=0) "
       "+ orders second-scan zero-diff evidence + satengine lane faces "
       "(treadmill) -- round 464 close")


def main():
    rc, out, err = git("add", "--", *PATHS)
    assert rc == 0, "add fail " + err[:200]
    rc, out, err = git("commit", "-m", MSG)
    print("COMMIT_RC", rc, (out + err).strip()[:200])
    if rc != 0:
        sys.exit(1)
    pr = subprocess.run([sys.executable, "Tools/push_verify.py"],
                         capture_output=True, cwd=".", creationflags=C)
    ptxt = ((pr.stdout or b"").decode("utf-8", "replace") + " || " +
            (pr.stderr or b"").decode("utf-8", "replace"))
    print("PUSH_VERIFY_RC", pr.returncode)
    print(ptxt[-300:])
    sys.exit(pr.returncode if pr.returncode in (0, 1) else 2)


if __name__ == "__main__":
    main()
