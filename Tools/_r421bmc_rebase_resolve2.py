"""r421 bm-c rebase resolve round-2: 14 shared regen-snapshot faces, all
last-writer-wins semantics. Per-file in-file ts newer-wins resolution
(max ISO timestamp found per side; ts absent on one side -> that side only
if the other lacks it too -> default mine). Then rebase --continue with the
proven manual-commit fallback, then immediate push; on rejection -> report
(CAS direct-push is the next law step, run separately)."""
import os
import re
import subprocess
import sys

CREATE_NO_WINDOW = 0x08000000
ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
TS_RE = re.compile(r"20\d{2}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}")


def git(args, check=True):
    e = dict(os.environ)
    e["GIT_EDITOR"] = "true"
    r = subprocess.run(["git"] + args, capture_output=True, cwd=ROOT,
                       creationflags=CREATE_NO_WINDOW, env=e)
    out = (r.stdout or b"").decode("utf-8", "replace")
    err = (r.stderr or b"").decode("utf-8", "replace")
    if check and r.returncode != 0:
        print(f"GIT FAIL {args[:3]} rc={r.returncode}")
        print((out + err)[-600:])
        sys.exit(2)
    return r.returncode, out, err


def max_ts(text):
    found = TS_RE.findall(text)
    return max(found) if found else None


def main():
    rc, st, _ = git(["status", "--porcelain"])
    uu = [ln[3:].strip() for ln in st.splitlines() if ln.startswith("UU")]
    print(f"UU files: {len(uu)}")
    for f in uu:
        _, s2, _ = git(["show", f":2:{f}"], check=False)
        _, s3, _ = git(["show", f":3:{f}"], check=False)
        t2, t3 = max_ts(s2), max_ts(s3)
        if t2 and t3:
            side = "theirs" if t3 >= t2 else "ours"
        elif t3:
            side = "theirs"
        elif t2:
            side = "ours"
        else:
            side = "theirs"
        git(["checkout", f"--{side}", "--", f])
        git(["add", "--", f])
        print(f"  {f}: origin_ts={t2} mine_ts={t3} -> {side}")

    # staged set must carry zero conflict markers
    rc, diff, _ = git(["diff", "--cached", "HEAD"], check=False)
    n_markers = sum(diff.count(m) for m in ("<<<<<<<", ">>>>>>>"))
    print(f"staged-vs-HEAD markers={n_markers}")
    if n_markers:
        print("MARKERS REMAIN -- abort path")
        sys.exit(3)

    rc, out, err = git(["rebase", "--continue"], check=False)
    print(f"rebase --continue rc={rc}: {(out + err).strip()[:300]}")
    if rc != 0:
        lo = (out + err).lower()
        if "edit all merge conflicts" in lo:
            # proven recipe from round-1 stop: manual commit then continue
            msg_path = os.path.join(ROOT, ".git", "rebase-merge", "message")
            with open(msg_path, encoding="utf-8", errors="replace") as fh:
                msg = fh.read().strip()
            rc2, out2, err2 = git(["commit", "-m", msg], check=False)
            print(f"manual commit rc={rc2}: {(out2 + err2).strip()[:300]}")
            if rc2 != 0:
                sys.exit(3)
            rc3, out3, err3 = git(["rebase", "--continue"], check=False)
            print(f"rebase --continue(2) rc={rc3}: {(out3 + err3).strip()[:300]}")
            if rc3 != 0:
                lo3 = (out3 + err3).lower()
                if "no changes" in lo3 or "nothing to commit" in lo3:
                    rc4, out4, err4 = git(["rebase", "--skip"], check=False)
                    print(f"rebase --skip rc={rc4}: {(out4 + err4).strip()[:250]}")
                    if rc4 != 0:
                        sys.exit(3)
                else:
                    sys.exit(3)
        else:
            sys.exit(3)

    rc, log, _ = git(["log", "--oneline", "-3"])
    print("--- post-rebase log ---")
    print(log.strip())

    rc, out, err = git(["push"], check=False)
    print(f"push rc={rc}: {(out + err).strip()[:400]}")
    if rc != 0:
        print("RACE AGAIN -- CAS direct-push is the next law step")
        sys.exit(4)

    git(["fetch", "origin"])
    _, ahead, _ = git(["rev-list", "--count", "origin/main..HEAD"])
    _, behind, _ = git(["rev-list", "--count", "HEAD..origin/main"])
    _, head, _ = git(["rev-parse", "--short", "HEAD"])
    print(f"DELIVERY: ahead={ahead.strip()} behind={behind.strip()} HEAD={head.strip()}")
    print("本地未达 origin commit 数 =", ahead.strip())
    return 0


if __name__ == "__main__":
    sys.exit(main())
