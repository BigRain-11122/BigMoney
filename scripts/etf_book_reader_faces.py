"""r1907: the width's family face is written AFTER the two faces that quote it.

The chain writes the production card (leg 80) and the executable sheet (legs 109/113)
before the width-arm family is rebuilt (legs 146-150). When that rebuild moves the
panel verdict -- here ONE_WORLD over 10 arms on 2026-11-20 -- the card and the sheet
keep quoting the width with no lineage sentence for the whole of the next day, and the
only thing that noticed was a smoke leg that went red on the readers it was written to
protect. r1850 established the shape of the repair: a check leg that says STALE and a
declared refresh the chain pays for only when it is stale.

This module is that probe. It compares the family face's mtime with the two reader
faces' mtimes and re-emits both writers when the family is newer. Nothing here judges
the family: the verdict, the arm count and the licence sentence all come from
`etf_book_production.family_coherence()`, which is the family face's own reader.

Usage:
    python scripts/etf_book_reader_faces.py check    # STALE / ok, rc 0 or 3
    python scripts/etf_book_reader_faces.py run      # re-emit the two writers if stale
    python scripts/etf_book_reader_faces.py selftest # offline (synthetic files)
"""
import argparse
import json
import os
import subprocess
import sys
import tempfile
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

ARMS = os.path.join("results", "etf_book_phase_atlas_arms.json")
CARD = os.path.join("results", "etf_book_production", "CARD.md")
ORDER_PTR = os.path.join("results", "etf_book_order", "latest.json")
WRITERS = [
    [sys.executable, os.path.join(ROOT, "scripts", "etf_book_production.py")],
    [sys.executable, os.path.join(ROOT, "scripts", "etf_book_order.py"), "run"],
    [sys.executable, os.path.join(ROOT, "scripts", "etf_book_order.py"), "card"],
]


def _mtime(root, rel):
    p = os.path.join(root, rel)
    try:
        return os.path.getmtime(p)
    except OSError:
        return None


def _ticket_md(root):
    """The sheet the pointer names, not whichever ORDER-*.md happens to be newest."""
    ptr = os.path.join(root, ORDER_PTR)
    try:
        with open(ptr, encoding="utf-8") as fh:
            doc = json.load(fh) or {}
    except (OSError, ValueError):
        return None, "order pointer unreadable"
    as_of = doc.get("as_of")
    if not as_of:
        return None, "order pointer names no as_of"
    rel = os.path.join("results", "etf_book_order", "ORDER-%s.md" % as_of)
    return rel, as_of


def status(root=ROOT):
    """(stale: bool|None, why: str). None = nothing to compare, never a pass."""
    arms = _mtime(root, ARMS)
    if arms is None:
        return None, "no width family face on disk -- nothing for the readers to lag"
    card = _mtime(root, CARD)
    if card is None:
        return True, "face missing: results/etf_book_production/CARD.md"
    tmd, why = _ticket_md(root)
    if tmd is None:
        return True, "face missing: results/etf_book_order/latest.json (%s)" % why
    ticket = _mtime(root, tmd)
    if ticket is None:
        return True, "face missing: %s" % tmd
    behind = []
    if card < arms:
        behind.append("card -%ds" % int(arms - card))
    if ticket < arms:
        behind.append("sheet -%ds" % int(arms - ticket))
    if behind:
        return True, "reader faces older than the width family (%s)" % ", ".join(behind)
    return False, "reader faces newer than the width family (card +%ds, sheet +%ds)" % (
        int(card - arms), int(ticket - arms))


def cmd_check(root=ROOT):
    stale, why = status(root)
    if stale is None:
        print("ok %s" % why)
        return 0
    if stale:
        print("STALE %s" % why)
        return 3
    print("ok %s" % why)
    return 0


def cmd_run():
    stale, why = status()
    if stale is None or stale is False:
        print("ok %s" % why)
        return 0
    print("STALE %s -> re-emitting the two reader faces" % why)
    rc = 0
    for w in WRITERS:
        t0 = time.time()
        r = subprocess.run(w, capture_output=True, text=True,
                           encoding="utf-8", errors="replace")
        print("%2d %-58s %5.1fs" % (r.returncode, " ".join(w[1:])[-58:],
                                    time.time() - t0))
        if r.returncode:
            rc = r.returncode
            tail = ((r.stdout or "") + (r.stderr or "")).strip().splitlines()[-3:]
            for ln in tail:
                print("   " + ln[:160])
    stale2, why2 = status()
    print("after: %s" % why2)
    if stale2:
        return rc or 3
    return rc


def selftest():
    bad = []
    seen = [0]

    def chk(name, cond, note=""):
        seen[0] += 1
        print(("PASS " if cond else "FAIL ") + name + ((" | " + note) if note else ""))
        if not cond:
            bad.append(name)

    with tempfile.TemporaryDirectory() as td:
        os.makedirs(os.path.join(td, "results", "etf_book_production"))
        os.makedirs(os.path.join(td, "results", "etf_book_order"))

        def touch(rel, ts):
            p = os.path.join(td, rel)
            os.makedirs(os.path.dirname(p), exist_ok=True)
            with open(p, "w", encoding="utf-8") as fh:
                fh.write("{}")
            os.utime(p, (ts, ts))

        def ptr(as_of):
            p = os.path.join(td, ORDER_PTR)
            with open(p, "w", encoding="utf-8") as fh:
                json.dump({"as_of": as_of}, fh)

        # 1: nothing on disk is a reason, not a pass and not a red
        s, why = status(td)
        chk("an absent family face is 'cannot compare', never 'ok'",
            s is None and "nothing for the readers to lag" in why, why)

        # 2: readers ahead of the family = not stale
        touch(ARMS, 1000.0)
        touch(CARD, 1001.0)
        touch("results/etf_book_order/ORDER-2026-11-20.md", 1001.0)
        ptr("2026-11-20")
        s, why = status(td)
        chk("both readers ahead of the family reads ok", s is False, why)

        # 3: the family written after the readers = stale, and it says which one lags
        touch(ARMS, 2000.0)
        s, why = status(td)
        chk("a family face newer than both readers is STALE",
            s is True and "card -" in why and "sheet -" in why, why)

        # 4: the card alone behind is still stale
        touch(CARD, 3000.0)
        touch("results/etf_book_order/ORDER-2026-11-20.md", 3000.0)
        touch(ARMS, 2500.0)
        touch(CARD, 2000.0)
        s, why = status(td)
        chk("one reader behind is stale even when the other is ahead",
            s is True and "card -" in why and "sheet" not in why.split("(")[-1], why)

        # 5: a missing sheet is 'face missing', and the pointer must name the file
        os.remove(os.path.join(td, "results/etf_book_order/ORDER-2026-11-20.md"))
        s, why = status(td)
        chk("a missing sheet is face missing, not ok", s is True and "face missing" in why, why)

        # 6: a pointer naming another day does not borrow the newest sheet on disk
        touch("results/etf_book_order/ORDER-2026-11-19.md", 5000.0)
        s, why = status(td)
        chk("the sheet read is the one the pointer names",
            s is True and "ORDER-2026-11-20.md" in why, why)

        # 7: the probe text the chain pays refresh on
        touch("results/etf_book_order/ORDER-2026-11-20.md", 1000.0)
        touch(CARD, 1000.0)
        touch(ARMS, 2000.0)
        import io as _io
        buf = _io.StringIO()
        old = sys.stdout
        sys.stdout = buf
        try:
            rc = cmd_check(td)
        finally:
            sys.stdout = old
        chk("check says STALE and returns non-zero on a lagging pair",
            rc == 3 and "STALE" in buf.getvalue(), buf.getvalue().strip()[:120])

    print("selftest %d/%d" % (seen[0] - len(bad), seen[0]) if not bad
          else "selftest FAILED %d/%d: %s" % (seen[0] - len(bad), seen[0], bad))
    return 0 if not bad else 1


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["check", "run", "selftest"])
    a = ap.parse_args(argv)
    if a.cmd == "check":
        return cmd_check()
    if a.cmd == "run":
        return cmd_run()
    return selftest()


if __name__ == "__main__":
    sys.exit(main())
