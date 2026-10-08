# -*- coding: utf-8 -*-
"""r781 bm-c S0 driver: round-start dirty classify (own daemon faces vs
foreign other-session faces), fetch origin, behind/ahead count.
r780 zero-delta law: behind=0 -> NO pull --rebase (daemon live-write faces
would reject rebase; dirty own faces ride to round-close add -A per r628
precedent). behind>0 -> own-face absorb then pull --rebase (retry-once
r727/r642 family). Foreign faces -> exit 2 read-only backoff.
Pattern credit: Tools/_r751bmc_s0.py + r780 close row zero-rebase window."""
import subprocess
import sys

ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
MARKERS = ("_roundzero", "orphan", "autofill", "dispatcher", "idle_trigger",
           "saturation", "_r781bmc_", "_r780bmc_", "commitmsg", "s0msg",
           "mergemsg", "precommitmsg", "watermark_probe", "token_usage",
           "watermark.jsonl", "_qa_face_probe", "round.lock")


def git(args, check=True):
    p = subprocess.run(["git", "-C", ROOT] + args, capture_output=True)
    out = (p.stdout + p.stderr).decode("utf-8", "replace")
    if check and p.returncode != 0:
        print("GITFAIL rc=%d args=%s out=%s" % (p.returncode, args[:3], out[:400]))
        sys.exit(1)
    return p.returncode, out


def classify():
    rc, st = git(["status", "--porcelain"])
    lines = [l for l in st.splitlines() if l.strip()]
    own, other = [], []
    for l in lines:
        (own if any(m in l for m in MARKERS) else other).append(l)
    return lines, own, other


def absorb(msg):
    git(["add", "-A"])
    rc, out = git(["commit", "-m", msg], check=False)
    if rc != 0 and "nothing to commit" not in out:
        print("ABSORB_FAIL rc=%d out=%s" % (rc, out[:400]))
        sys.exit(1)
    sha = git(["rev-parse", "--short=9", "HEAD"])[1].strip()
    print("ABSORB commit=%s" % sha)
    return sha


def main():
    lines, own, other = classify()
    print("DIRTY total=%d own=%d other=%d" % (len(lines), len(own), len(other)))
    for l in lines:
        print("  D " + l)
    if other:
        print("OTHER-SESSION FACES PRESENT -> read-only backoff per fleet law")
        return 2
    git(["fetch", "origin"])
    rc, out = git(["rev-list", "--count", "origin/main..HEAD"])
    ahead = out.strip()
    rc, out = git(["rev-list", "--count", "HEAD..origin/main"])
    behind = out.strip()
    print("PRE ahead=%s behind=%s" % (ahead, behind))
    if behind == "0":
        sha = git(["rev-parse", "HEAD"])[1].strip()
        print("ZERO-DELTA window head=%s (no rebase, own dirty rides to close)" % sha[:9])
        return 0
    if own:
        absorb("round 781: S0 absorb daemon live faces (pre-rebase net-tree)")
    rc, out = git(["pull", "--rebase", "origin", "main"], check=False)
    if rc != 0:
        print("PULL1 rc=%d tail=%s" % (rc, out[-400:]))
        lines2, own2, other2 = classify()
        if other2:
            print("mid-pull other faces -> abort backoff")
            return 2
        if own2:
            absorb("round 781: S0 churn-absorb retry (r727/r642 family)")
        rc, out = git(["pull", "--rebase", "origin", "main"], check=False)
        if rc != 0:
            print("PULL2_FAIL rc=%d tail=%s" % (rc, out[-600:]))
            return 3
    print("PULL ok tail=%s" % out.strip().splitlines()[-1][:200])
    sha = git(["rev-parse", "HEAD"])[1].strip()
    print("POST head=%s" % sha[:9])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
