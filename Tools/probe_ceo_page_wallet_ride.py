"""Is the CEO page older than the wallet-ride face it now quotes? (r2205)

`scripts/ceo_live_usage.py` prints section ⑩c from `results/three_book_wallet_ride.json`
and stamps that face's own `generated`, because the ride leg runs AFTER the page leg in
`Tools/s6_chain_bmc.py` (r1781: a section fed by another script prints its source's
clock, or it silently shows the previous trip).  A stamp alone leaves the page one
generation behind forever; the fix is a probe that answers one cheap question --

    is the ride face NEWER than the page that quotes it?

-- and lets `run_leg` pay for a page rebuild only in that case.  Without it the reader
opens a page whose ⑩c numbers belong to yesterday's measurement and only the stamp says
so; with it the chain closes the loop the same round the ride is rebuilt.

Usage:
    python Tools/probe_ceo_page_wallet_ride.py check    # rc0 fresh / rc3 STALE
    python Tools/probe_ceo_page_wallet_ride.py run      # rebuild the page
    python Tools/probe_ceo_page_wallet_ride.py selftest # offline, proves rc3 is spoken

rc3 with the literal word "STALE" is the contract `run_leg` reads (`_repairable`); a
probe that prints anything else on drift is a leg that never heals (r1850).
"""
import os
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FACE = os.path.join(ROOT, "results", "three_book_wallet_ride.json")
PAGE = os.path.join(ROOT, "docs", "live_usage", "LIVE-latest.md")
WRITER = os.path.join("scripts", "ceo_live_usage.py")


def stale_reason(face=FACE, page=PAGE):
    """None when the page is at least as new as the face, else a one-line reason."""
    if not os.path.exists(face):
        return "face missing: %s (the page cannot be judged stale against nothing)" % face
    if not os.path.exists(page):
        return "face missing: %s (no page to quote it)" % page
    fm = os.path.getmtime(face)
    pm = os.path.getmtime(page)
    if fm > pm:
        return ("STALE page is %.0fs older than the ride face it quotes "
                "(%s < %s)" % (fm - pm, os.path.basename(page), os.path.basename(face)))
    return None


def check():
    why = stale_reason()
    if why:
        print(why)
        return 3
    print("OK page is at least as new as the ride face (%.0fs margin)"
          % (os.path.getmtime(PAGE) - os.path.getmtime(FACE)))
    return 0


def run():
    r = subprocess.run([sys.executable, WRITER], cwd=ROOT,
                       capture_output=True, text=True, encoding="utf-8",
                       errors="replace", timeout=600)
    tail = (r.stdout or "").strip().splitlines()[-1:] or [""]
    print(tail[0][:200])
    return r.returncode


def selftest():
    legs = []

    def _t(name, ok, detail=""):
        legs.append((name, bool(ok), detail))

    with tempfile.TemporaryDirectory() as td:
        face = os.path.join(td, "face.json")
        page = os.path.join(td, "page.md")
        with open(face, "w", encoding="utf-8") as fh:
            fh.write("{}")
        with open(page, "w", encoding="utf-8") as fh:
            fh.write("# page")
        os.utime(face, (1000, 1000))
        os.utime(page, (2000, 2000))
        _t("fresh page passes", stale_reason(face, page) is None,
           "%r" % (stale_reason(face, page),))
        os.utime(page, (500, 500))
        why = stale_reason(face, page)
        _t("older page speaks STALE", bool(why) and "STALE" in why, "%r" % (why,))
        _t("missing page speaks face missing",
           "face missing" in (stale_reason(face, os.path.join(td, "nope.md")) or ""),
           "")
        _t("missing face speaks face missing",
           "face missing" in (stale_reason(os.path.join(td, "nope.json"), page) or ""), "")
        _t("reason names both files", bool(why) and "page.md" in why and "face.json" in why,
           "%r" % (why,))
    bad = [n for n, ok, _ in legs if not ok]
    for n, ok, d in legs:
        print("%s %s %s" % ("PASS" if ok else "FAIL", n, d))
    print("selftest %d/%d" % (len(legs) - len(bad), len(legs)))
    return 0 if not bad else 2


def main(argv):
    cmd = (argv[1] if len(argv) > 1 else "check").lower()
    if cmd == "check":
        return check()
    if cmd == "run":
        return run()
    if cmd == "selftest":
        return selftest()
    print("usage: probe_ceo_page_wallet_ride.py [check|run|selftest]")
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
