"""r421 bm-c close: targeted add -> staged-set audit -> commit -> rebase
(behind=6) -> orders re-scan on fresh tree -> push -> delivery self-verify.
All git children CREATE_NO_WINDOW (U060 flash-guard family)."""
import json
import subprocess
import sys

CREATE_NO_WINDOW = 0x08000000
ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"

FILES = [
    "Tools/_r421bmc_s0.py",
    "Tools/_r421bmc_mf_assist.py",
    "Tools/_r421bmc_close.py",
    "results/_r421bmc_mf_assist.json",
    "fleet/tasks/T-2026-10-03-157-P1.json",
    "fleet/inbox/MSG-2026-10-03-1543-bmc-all-moneyflow-option-a-refuted.md",
    "state-bm-c.json",
    "fleet/machines/bm-c.json",
    "round_reports-bm-c.md",
    # bm-c daemon-face churn absorb (r420 precedent)
    "results/autofill_state.bm-c.json",
    "results/dispatcher_state.bm-c.json",
    "results/saturation_engine/face_bm-c.json",
    "results/saturation_engine_state.bm-c.json",
]

MSG = ("round 421 bm-c: moneyflow option-A bm-c branch refuted "
       "(T-157 honest negative: push2/push2his both refuse bm-c egress, "
       "0.1s instant-refusal; MSG-1543 to lane owner+GM; reusable detached "
       "probe tool) + S6 37 legs rc0 + D-06 flow-sweep zero-residue "
       "[via bm-c]")


def git(args, check=True):
    r = subprocess.run(["git"] + args, capture_output=True, cwd=ROOT,
                       creationflags=CREATE_NO_WINDOW)
    out = (r.stdout or b"").decode("utf-8", "replace")
    err = (r.stderr or b"").decode("utf-8", "replace")
    if check and r.returncode != 0:
        print(f"GIT FAIL {args[:3]} rc={r.returncode}")
        print(out[-800:])
        print(err[-800:])
        sys.exit(2)
    return r.returncode, out, err


def main():
    # heartbeat epoch type law (R170/R178): must be JSON int
    with open(f"{ROOT}/fleet/machines/bm-c.json", encoding="utf-8-sig") as fh:
        hb = json.load(fh)
    e = hb.get("heartbeat_epoch_utc")
    assert isinstance(e, int) and not isinstance(e, bool), \
        f"epoch must be int, got {type(e)}"
    print(f"epoch type OK: {e} ({type(e).__name__})")

    rc, st, _ = git(["status", "--porcelain"])
    print("--- pre-add status ---")
    print(st.strip()[:1200])

    git(["add", "--"] + FILES)
    rc, staged, _ = git(["diff", "--cached", "--name-status"])
    print("--- staged set ---")
    print(staged.strip())
    staged_files = {ln.split("\t", 1)[1] for ln in staged.strip().splitlines()
                    if ln.strip()}
    expected = set(FILES)
    extra = staged_files - expected
    if extra:
        print(f"ABORT: unexpected staged files: {extra}")
        sys.exit(2)

    rc, out, err = git(["commit", "-m", MSG], check=False)
    print(f"commit rc={rc}")
    print((out + err).strip()[:600])
    if rc != 0:
        sys.exit(2)

    rc, out, err = git(["pull", "--rebase"], check=False)
    print(f"pull --rebase rc={rc}")
    print((out + err).strip()[:800])
    if rc != 0:
        print("REBASE CONFLICT -- leaving for manual path per law")
        sys.exit(3)

    # orders re-scan on the fresh tree (S7 double-scan)
    r = subprocess.run([sys.executable, "Tools/orders_diff.py"],
                        capture_output=True, cwd=ROOT,
                        creationflags=CREATE_NO_WINDOW)
    print("orders_diff:", (r.stdout or b"").decode("utf-8", "replace").strip())

    rc, out, err = git(["push"], check=False)
    print(f"push rc={rc}")
    print((out + err).strip()[:600])
    if rc != 0:
        rc2, out2, err2 = git(["pull", "--rebase"], check=False)
        print(f"pull retry rc={rc2}")
        print((out2 + err2).strip()[:400])
        if rc2 == 0:
            rc3, out3, err3 = git(["push"], check=False)
            print(f"push retry rc={rc3}")
            print((out3 + err3).strip()[:400])
            if rc3 != 0:
                sys.exit(4)
        else:
            sys.exit(4)

    # delivery self-verify (O-20261001-1108)
    git(["fetch", "origin"])
    _, ahead, _ = git(["rev-list", "--count", "origin/main..HEAD"])
    _, behind, _ = git(["rev-list", "--count", "HEAD..origin/main"])
    _, head, _ = git(["rev-parse", "--short", "HEAD"])
    print(f"DELIVERY: ahead={ahead.strip()} behind={behind.strip()} HEAD={head.strip()}")
    print("本地未达 origin commit 数 =", ahead.strip())
    return 0


if __name__ == "__main__":
    sys.exit(main())
