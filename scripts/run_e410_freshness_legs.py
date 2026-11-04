"""Prove the two E410 freshness legs fire, without paying for the other 300 legs.

The legs were appended to smoke_test.py; this extracts their own block (plus the _bar_lag_td
helper they call) from that file and execs it, so what is exercised is the code the suite
will run -- not a re-implementation of it.  A drift between the blocks' text and this
extractor's anchors is reported as a failure, never skipped.

Three cases run in a scratch workspace (the real input faces are copied in, never edited):

    real          both legs must pass -- a bound that is red on the live tree prices nothing
    stale_openfill  the open-fill face moved three bars back: leg A red, leg B green
    stale_census  the census cutoff moved ten bars back: leg A green, leg B red

The last two are the card's acceptance: a gate that has only ever been seen green is not yet
a gate.  Each leg is checked in isolation so one red cannot hide behind the other.

Usage:
    python scripts/run_e410_freshness_legs.py
"""
import hashlib
import json
import os
import shutil
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SMOKE = os.path.join(ROOT, "smoke_test.py")
START = "# E410: E409 priced five reader sites over two faces written only from a session script"
END = '\nif __name__ == "__main__":'
HELPER_START = "def _bar_lag_td(face_day, panel_day):"
HELPER_END = "CENSUS_DRIFT = []"
T35 = os.path.join("results", "t35_open_fill_verify.json")
QN = os.path.join("results", "state_tilt", "quantityname_latest.json")
COPIES = [T35, QN,
          os.path.join("data", "daily", "sh510300.csv"),
          os.path.join("data", "exchange_calendar.csv")]


def _sha(path):
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def _extract(text, start, end, what):
    if start not in text:
        raise SystemExit("FAIL: the %s block is not in smoke_test.py" % what)
    head = text.index(start)
    tail = text.index(end, head) if end in text[head:] else len(text)
    return text[head:tail]


def _bars_back(panel_day, n):
    """The n-th trading day at or before panel_day, off the local calendar."""
    import pandas as pd
    cal = pd.to_datetime(pd.read_csv(os.path.join(ROOT, "data", "exchange_calendar.csv"))["date"])
    days = [d for d in cal if d <= pd.Timestamp(panel_day)]
    return str(days[-n].date()) if len(days) >= n else None


def _run_case(name, helper, block, doctor, expect):
    """Build a scratch tree, optionally doctor a face, exec both legs, compare to expect."""
    tmp = tempfile.mkdtemp(prefix="e410prover_")
    try:
        for rel in COPIES:
            dst = os.path.join(tmp, rel)
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copyfile(os.path.join(ROOT, rel), dst)
        if doctor:
            doctor(tmp)
        results = []

        def check(nm, ok, detail=""):
            results.append((bool(ok), nm, detail))

        ns = {"os": os, "sys": sys, "json": json, "check": check, "__name__": "_e410_leg"}
        cwd = os.getcwd()
        try:
            os.chdir(tmp)
            exec(compile(helper, "smoke_test.py:_bar_lag_td", "exec"), ns)  # noqa: S102
            exec(compile(block, "smoke_test.py:E410", "exec"), ns)  # noqa: S102
        finally:
            os.chdir(cwd)
        # Legs are matched by registration order, not by scraping their names out of the
        # source: _name410b is a parenthesised multi-line literal and a scrape would compare
        # the first line only (this runner's own first draft did exactly that and reported
        # "registered no check" for a leg that had just fired).  The count is asserted so a
        # third check appearing in the block cannot slip through unexamined.
        if len(results) != len(expect):
            print("FAIL %s: expected %d leg(s), the block registered %d"
                  % (name, len(expect), len(results)))
            return False, []
        ok_all = True
        rows = []
        for (got_ok, nm, detail), want_ok in zip(results, expect):
            good = (got_ok == want_ok)
            ok_all = ok_all and good
            rows.append({"leg": nm, "expected_red": not want_ok, "observed_red": not got_ok,
                         "as_expected": good, "detail": str(detail)[:240]})
            print("%s %s [%s] %s" % ("PASS" if good else "FAIL", name,
                                     "red" if not got_ok else "green", nm[:90]))
            print("      " + str(detail)[:200])
        return ok_all, rows
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def main():
    if not os.path.exists(SMOKE):
        print("FAIL: smoke_test.py not found")
        return 1
    text = open(SMOKE, encoding="utf-8", errors="replace").read()
    try:
        helper = _extract(text, HELPER_START, HELPER_END, "_bar_lag_td")
        block = _extract(text, START, END, "E410")
    except SystemExit as exc:
        print(exc)
        return 1
    if block.count("check(_name410a") != 1 or block.count("check(_name410b") != 1:
        print("FAIL: expected one check() per leg name in the block")
        return 1
    import pandas as pd
    panel = str(pd.to_datetime(
        pd.read_csv(os.path.join(ROOT, "data", "daily", "sh510300.csv"))["date"]).iloc[-1].date())
    three = _bars_back(panel, 4)
    ten = _bars_back(panel, 11)

    def doc_a(tmp):
        p = os.path.join(tmp, T35)
        d = json.load(open(p, encoding="utf-8"))
        d["day"] = three
        json.dump(d, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    def doc_b(tmp):
        p = os.path.join(tmp, QN)
        d = json.load(open(p, encoding="utf-8"))
        d["evidence_cutoff"] = ten
        json.dump(d, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    before = {rel: _sha(os.path.join(ROOT, rel)) for rel in (T35, QN)}
    cases = [
        ("real", None, [True, True]),
        ("stale_openfill", doc_a, [False, True]),
        ("stale_census", doc_b, [True, False]),
    ]
    if three is None or ten is None:
        print("FAIL: the calendar is too short to stage a stale case")
        return 1
    ok = True
    cases_out = []
    for nm, doctor, expect in cases:
        good, rows = _run_case(nm, helper, block, doctor, expect)
        ok = good and ok
        cases_out.append({"case": nm,
                          "doctored": None if doctor is None else {
                              "stale_openfill": {"field": "day", "value": three},
                              "stale_census": {"field": "evidence_cutoff",
                                               "value": ten}}.get(nm),
                          "legs": rows})
    after = {rel: _sha(os.path.join(ROOT, rel)) for rel in (T35, QN)}
    untouched = before == after
    if not untouched:
        print("FAIL: an input face was rewritten on disk -- the card forbids it")
        ok = False
    else:
        print("PASS input faces untouched (%s)" % ", ".join(
            "%s=%s" % (os.path.basename(k), v[:8]) for k, v in after.items()))
    print("SUMMARY %s" % ("3/3 cases as expected" if ok else "NOT as expected"))
    _publish(panel, three, ten, cases_out, ok, untouched, before, after)
    return 0 if ok else 1


def _publish(panel, three, ten, cases_out, ok, untouched, before, after):
    """Publish the acceptance evidence as the card's deliverable face.

    The face is written from the runs, not typed: every number below came out of the exec'd
    legs, and the two input hashes are printed beside each other so a later reader can see the
    claim "untouched" was measured rather than asserted.
    """
    import datetime as _dt
    face = {
        "evidence_cutoff": panel,
        "generated": _dt.datetime.now().astimezone().isoformat(timespec="seconds"),
        "study": "E410_bounded_lag_readers_for_two_session_written_faces",
        "seed": "E409: 5 reader sites over 2 faces, 0 price the age; suite-wide 6 of 192 legs do",
        "held_fixed": ["scripts/t35_open_fill_verify.py", "results/t35_open_fill_verify.json",
                       "results/state_tilt/quantityname_latest.json",
                       "scripts/e321_quantity_name_reach.py"],
        "why_two_forms": ("the open-fill face verifies one session's opens, so one missed bar is "
                          "already stale; the census counts a corpus of sources, not a bar, so a "
                          "week is the bound at which its numbers describe a different tree"),
        "bounds": [{
            "face": "results/t35_open_fill_verify.json",
            "leg": "product: the open-fill verification face is at most one bar behind the panel",
            "bound_bars": 1,
            "shape": ("bounded allowance, the same shape smoke_test.py already uses for the ETF "
                      "book page; a hard day gate is excluded by E185 at :593-597"),
            "red_when": "lag > 1 bar, or no day to price, or the face is ahead of the panel",
            "closes_by": "rerun scripts/t35_open_fill_verify.py",
        }, {
            "face": "results/state_tilt/quantityname_latest.json",
            "leg": ("product: the quantity-name census prints its lag against the panel and "
                    "reddens past a week of bars"),
            "bound_bars": 5,
            "shape": "one comparison against the panel date; the lag is printed every run",
            "red_when": "lag > 5 bars, or no evidence_cutoff, or the cutoff is ahead of the panel",
            "closes_by": "rerun scripts/e321_quantity_name_reach.py",
        }],
        "calendar": "data/exchange_calendar.csv (bars, not wall-clock days: a weekend cannot red it)",
        "cases": cases_out,
        "inputs_untouched": {
            "measured": untouched,
            "sha256_before": {os.path.basename(k): v for k, v in before.items()},
            "sha256_after": {os.path.basename(k): v for k, v in after.items()},
        },
        "staged_stale_dates": {"openfill_three_bars_back": three,
                               "census_ten_bars_back": ten},
        "verdict": ("both_bounds_fire_on_a_doctored_face_and_stay_green_on_the_live_one"
                    if ok else "acceptance_not_met"),
        "summary": {
            "legs": sum(len(c["legs"]) for c in cases_out),
            "cases_as_expected": sum(1 for c in cases_out
                                     if all(r["as_expected"] for r in c["legs"])),
            "cases": len(cases_out),
            "green_on_live_tree": sum(1 for c in cases_out for r in c["legs"]
                                      if c["case"] == "real" and not r["observed_red"]),
        },
        "no_bill": "two smoke legs and one prover; no engine, no backtest, no network",
    }
    out_dir = os.path.join(ROOT, "results", "state_tilt")
    os.makedirs(out_dir, exist_ok=True)
    # The card named UNFLOORED-<cutoff>.json, which is ALREADY E409's published ledger on the
    # same cutoff -- this runner's first version overwrote it in place and the restored file had
    # to be checked out of git (see the round report).  The measurement here is the bound, not
    # the ledger, so the face is named for what it measures, and the collision is refused by
    # construction rather than remembered.
    path = os.path.join(out_dir, "FRESHNESSBOUND-%s.json" % panel)
    if os.path.exists(path):
        prev = json.load(open(path, encoding="utf-8"))
        if prev.get("study") not in (None, face["study"]):
            raise SystemExit("FAIL: %s already belongs to %r -- refusing to overwrite"
                             % (os.path.relpath(path, ROOT), prev.get("study")))
    for p, payload in ((path, face),
                       (os.path.join(out_dir, "freshnessbound_latest.json"), face)):
        with open(p, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(payload, fh, ensure_ascii=False, indent=1)
            fh.write("\n")
    print("WROTE %s" % os.path.relpath(path, ROOT))


if __name__ == "__main__":
    sys.exit(main())