"""push_verify.py -- single-source round-end delivery verification.

r502-family fix (r434 bm-c false-delivery retro): a wrap script may not
claim delivery it never performed. This helper IS the claim's evidence leg:
push -> fetch -> rev-parse HEAD vs remote/branch, with 40-hex hard
validation (CAS batch law), push-text bad-word screen (fatal/rejected/
failed/error) and ahead-count==0 proof. Exit 0=DELIVERED, 1=NOT-DELIVERED
(honest red, caller must NOT write a delivered claim), 2=mechanism fault.

Usage:
  python Tools/push_verify.py [--repo PATH] [--remote origin] [--branch main] [--no-push]
  python Tools/push_verify.py selftest        # hermetic, zero git calls
All git children CREATE_NO_WINDOW (U060/O-67fbec7 zero-flash law).
"""
import argparse
import json
import re
import subprocess
import sys

CREATE = 0x08000000
HEX40 = re.compile(r"^[0-9a-f]{40}$")
BAD_WORDS = ("fatal", "rejected", "failed", "error")


def git(repo, *a):
    p = subprocess.run(["git"] + list(a), capture_output=True,
                       creationflags=CREATE, cwd=repo)
    out = (p.stdout or b"").decode("utf-8", "replace")
    err = (p.stderr or b"").decode("utf-8", "replace")
    return p.returncode, out, err


def hex40_ok(s):
    return bool(s) and HEX40.match(s.strip()) is not None


def push_text_clean(rc, out, err):
    # rc==0 + zero bad words. "Everything up-to-date" carries none -> clean.
    if rc != 0:
        return False, "push rc=%d" % rc
    txt = (out + " " + err).lower()
    hit = [w for w in BAD_WORDS if w in txt]
    if hit:
        return False, "push text hits %s" % hit
    return True, ""


def parse_count(s):
    s = s.strip()
    return int(s) if re.match(r"^\d+$", s) else None


def verify(repo, remote, branch, do_push=True):
    r = {"repo": repo, "remote": remote, "branch": branch}
    if do_push:
        rc, out, err = git(repo, "push", remote, branch)
        clean, why = push_text_clean(rc, out, err)
        r["push_rc"] = rc
        r["push_clean"] = clean
        r["push_why"] = why
        if not clean:
            r["verdict"] = "NOT-DELIVERED"
            r["reason"] = why
            return 1, r
    git(repo, "fetch", remote)
    _, tip, err1 = git(repo, "rev-parse", "HEAD")
    _, om, err2 = git(repo, "rev-parse", "%s/%s" % (remote, branch))
    tip, om = tip.strip(), om.strip()
    r["tip"] = tip
    r["remote_tip"] = om
    if not hex40_ok(tip) or not hex40_ok(om):
        r["verdict"] = "NOT-DELIVERED"
        r["reason"] = "non-40hex tip=%r remote_tip=%r err=%s/%s" % (
            tip[:12], om[:12], err1.strip()[:80], err2.strip()[:80])
        return 1, r
    _, ahead_s, _ = git(repo, "rev-list", "--count", "%s/%s..HEAD" % (remote, branch))
    _, behind_s, _ = git(repo, "rev-list", "--count", "HEAD..%s/%s" % (remote, branch))
    ahead, behind = parse_count(ahead_s), parse_count(behind_s)
    if ahead is None or behind is None:
        r["verdict"] = "MECHANISM-FAULT"
        r["reason"] = "unparseable counts ahead=%r behind=%r" % (ahead_s, behind_s)
        return 2, r
    r["ahead"] = ahead
    r["behind"] = behind
    # Delivery = every local commit is on the remote (ahead==0). In a
    # multi-writer fleet origin/main keeps moving (behind>0 is normal fleet
    # motion, not a delivery fault) -- tip==remote would be too strict.
    r["delivered"] = ahead == 0
    if r["delivered"]:
        r["verdict"] = "DELIVERED"
        r["reason"] = "" if behind == 0 else "origin moved on (behind=%d, fleet motion)" % behind
        return 0, r
    r["verdict"] = "NOT-DELIVERED"
    r["reason"] = "undelivered local commits ahead=%d (tip==remote: %s)" % (ahead, tip == om)
    return 1, r


def selftest():
    assert hex40_ok("a" * 40) and hex40_ok("0123456789abcdef" * 2 + "12345678")
    assert not hex40_ok("") and not hex40_ok("a" * 39) and not hex40_ok("z" * 40)
    assert not hex40_ok("a" * 41) and not hex40_ok("A" * 40)  # uppercase != raw oid
    ok, _ = push_text_clean(0, "Everything up-to-date", "")
    assert ok, "up-to-date must be clean"
    ok, why = push_text_clean(0, "", "fatal: must give exactly one tree")
    assert not ok and "fatal" in why
    ok, why = push_text_clean(0, "To github.com:x/y.git", " ! [rejected] main -> main")
    assert not ok and "rejected" in why
    ok, _ = push_text_clean(1, "", "")
    assert not ok
    assert parse_count("0") == 0 and parse_count(" 3 \n") == 3
    assert parse_count("") is None and parse_count("x") is None
    print("push_verify selftest: 8/8 PASS")
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", nargs="?", default="verify",
                    help="'verify' or 'selftest'")
    ap.add_argument("--repo", default=".")
    ap.add_argument("--remote", default="origin")
    ap.add_argument("--branch", default="main")
    ap.add_argument("--no-push", action="store_true",
                    help="verify only (fetch+rev-parse), no push leg")
    a = ap.parse_args()
    if a.mode == "selftest":
        return selftest()
    if a.mode != "verify":
        print("unknown mode %r" % a.mode)
        return 2
    rc, r = verify(a.repo, a.remote, a.branch, do_push=not a.no_push)
    print(json.dumps(r, ensure_ascii=False))
    return rc


if __name__ == "__main__":
    sys.exit(main())
