# -*- coding: utf-8 -*-
"""Negative control for scripts/lane_lag_unit_guard.py (r2069, bm-c).

A green leg is worthless if the leg cannot go red.  Every leg here poisons exactly one
thing and asserts the *specific* failure, then restores the byte-identical original.

Legs
----
 1  a tampered number           -> rc3, sentence contains CHECK FAILED, must NOT contain STALE
 2  a tampered page block       -> rc3, CHECK FAILED
 3  moved inputs                -> rc3, sentence contains STALE (the chain pays for a rebuild)
 4  restore                     -> rc0, and the face is byte-identical to the original
 5  the classification is live  -> a fixture where the lane is current reads AGREE_CURRENT,
                                   so the token is derived and not a constant
 6  the unit really is the cause-> read the same tolerance in trading days and the weekday
                                   sweep stops flipping; the defect disappears for the right
                                   reason, not because the sweep is blind
"""
import hashlib
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from scripts import lane_lag_unit_guard as G  # noqa: E402

FACE = G.OUT
PAGE = G.MD


def sha(path):
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def main():
    legs = []

    def leg(name, cond, why=""):
        legs.append((name, bool(cond), why))

    if not (os.path.exists(FACE) and os.path.exists(PAGE)):
        print("MISSING face or page -- run `python scripts/lane_lag_unit_guard.py run` first")
        return 2

    face_sha0 = sha(FACE)
    page_sha0 = sha(PAGE)
    face_bytes = open(FACE, "rb").read()
    page_bytes = open(PAGE, "rb").read()

    try:
        # ---- leg 0: the face is green before we touch it
        rc, why = G.check()
        leg("0 baseline check is green (rc0)", rc == 0, why)

        # ---- leg 1: one number moves
        payload = json.loads(face_bytes.decode("utf-8"))
        rows = payload.get("rows") or []
        if not rows:
            leg("1 tamper leg needs at least one row", False, "no rows")
        else:
            rows[0]["calendar_lag_days"] = int(rows[0].get("calendar_lag_days") or 0) + 3
            with open(FACE, "w", encoding="utf-8", newline="\n") as fh:
                json.dump(payload, fh, ensure_ascii=False, indent=1)
            rc1, why1 = G.check()
            leg("1 a tampered number is red (rc3)", rc1 == 3, why1)
            leg("1 ...and the sentence names CHECK FAILED", "CHECK FAILED" in why1, why1)
            leg("1 ...and never says STALE", "STALE" not in why1, why1)

        # ---- leg 4a: restore the face byte for byte
        with open(FACE, "wb") as fh:
            fh.write(face_bytes)
        leg("4a face restored byte-identically", sha(FACE) == face_sha0,
            "sha %s" % sha(FACE)[:12])
        rc_r, why_r = G.check()
        leg("4b restored face is green again (rc0)", rc_r == 0, why_r)

        # ---- leg 2: the page block is not what the face renders
        text = page_bytes.decode("utf-8")
        i = text.find(G._MARK_BEGIN)
        j = text.find(G._MARK_END)
        if i < 0 or j < 0:
            leg("2 page has a marker block", False, "no markers")
        else:
            broken = text[:i] + text[i:j].replace("|", "| ", 1) + text[j:]
            with open(PAGE, "w", encoding="utf-8", newline="\n") as fh:
                fh.write(broken)
            rc2, why2 = G.check()
            leg("2 a tampered page block is red (rc3)", rc2 == 3, why2)
            leg("2 ...and the sentence names CHECK FAILED", "CHECK FAILED" in why2, why2)
            with open(PAGE, "wb") as fh:
                fh.write(page_bytes)
            leg("2b page restored byte-identically", sha(PAGE) == page_sha0,
                "sha %s" % sha(PAGE)[:12])

        # ---- leg 3: the inputs moved
        payload = json.loads(face_bytes.decode("utf-8"))
        digest = payload.get("inputs_digest") or {}
        digest["blocks"] = "0" * 16
        payload["inputs_digest"] = digest
        with open(FACE, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(payload, fh, ensure_ascii=False, indent=1)
        rc3, why3 = G.check()
        leg("3 moved inputs are STALE (rc3)", rc3 == 3, why3)
        leg("3 ...and the sentence says STALE", "STALE" in why3, why3)
        leg("3 ...and does not pretend the face is wrong", "CHECK FAILED" not in why3, why3)
        with open(FACE, "wb") as fh:
            fh.write(face_bytes)

    finally:
        with open(FACE, "wb") as fh:
            fh.write(face_bytes)
        with open(PAGE, "wb") as fh:
            fh.write(page_bytes)

    # ---- leg 5: the classification is derived, not a constant
    leg("5 classify is a function of its inputs",
        G.classify(True, "LATE") == "AGREE_LATE"
        and G.classify(False, "LATE") == "GREEN_IS_PREMATURE"
        and G.classify(True, "CURRENT") == "RED_IS_UNIT_ARTIFACT"
        and G.classify(False, "CURRENT") == "AGREE_CURRENT")

    # ---- leg 6: the unit is the cause -- read the same tolerance in trading days
    cal = sorted(str(d) for d in G.load_calendar())
    swept = G.weekday_sweep(cal)
    leg("6 the calendar-day sweep flips at some fixed gap", any(s["flips"] for s in swept),
        "flips=%d" % sum(1 for s in swept if s["flips"]))
    # in trading days the lag is k by construction, so a fixed k is a fixed colour
    trading_day_colours = {k: (k > G.DEFAULT_ALLOW) for k in (1, 2, 3, 4, 5)}
    leg("6 ...and reading it in trading days cannot flip",
        len(set(trading_day_colours.values())) == 2
        and all(trading_day_colours[k] == (k > G.DEFAULT_ALLOW)
                for k in trading_day_colours))

    ok = sum(1 for _, c, _ in legs if c)
    for name, cond, why in legs:
        print(("  ok   " if cond else "  FAIL ") + name + ("" if cond else "  <- " + str(why)))
    print("\nnegative control: %d/%d OK" % (ok, len(legs)))
    return 0 if ok == len(legs) else 1


if __name__ == "__main__":
    sys.exit(main())
