"""r422 bm-c rebase resolve: 14 shared regen-snapshot faces (bm-a r630 twins
churn vs adopted 422a S6 outputs), last-writer-wins semantics. Per-file
in-file ts newer-wins (r621 snapshot-family law; r421 resolve2 proven recipe).
Rebase --continue with manual-commit fallback; NO push here (S7 closeout owns
push). Symbolic-ref self-check per r624 detached-HEAD law."""
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
    picks = {}
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
        picks[f] = (side, t2, t3)
        print(f"  {f}: origin_ts={t2} mine_ts={t3} -> {side}")

    n_theirs = sum(1 for s, _, _ in picks.values() if s == "theirs")
    n_ours = sum(1 for s, _, _ in picks.values() if s == "ours")
    print(f"picks: theirs(mine)={n_theirs} ours(origin)={n_ours}")

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
        if "edit all merge conflicts" in lo or "did you forget to call git add" in lo:
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

    # authority self-checks: no unresolved entries, not detached
    _, u, _ = git(["ls-files", "-u"])
    print(f"ls-files -u lines={len(u.strip().splitlines()) if u.strip() else 0}")
    if u.strip():
        sys.exit(3)
    rc5, sym, _ = git(["symbolic-ref", "-q", "HEAD"], check=False)
    print(f"symbolic-ref rc={rc5} -> {sym.strip() or 'DETACHED!!'}")
    if rc5 != 0:
        sys.exit(3)

    rc, log, _ = git(["log", "--oneline", "-3"])
    print("--- post-rebase log ---")
    print(log.strip())
    _, ahead, _ = git(["rev-list", "--count", "origin/main..HEAD"])
    _, behind, _ = git(["rev-list", "--count", "HEAD..origin/main"])
    print(f"DELIVERY: ahead={ahead.strip()} behind={behind.strip()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
