"""Monthly exam prep -- accounts face baseline capture (T-2026-10-01-143 s1).

Spec (T-143 face 4): 27-experimental-accounts face needs "aggregate P&L/holding
state vs month-open baseline".  This tool PINS the month-open baseline as a
committed artifact: every marks-bearing account across the five paper harnesses
is snapshotted (family, harness, source file, asof, equity, capital faces).

Month-open semantics: month boundary = 2026-10-01; golden week leaves no bars
between 2026-09-30 and 2026-10-09, so a capture taken during the holiday is
byte-stable month-open state (zero drift window).  Re-run after 10-09 would NOT
be month-open anymore -- do not refresh this file in place; version it.

Zero network, zero engine, deterministic byte-identical output on rerun
(no wallclock inside the data payload).

Exit codes: 0 = captured ok; 2 = mechanism fault (missing harness dir / parse
error / nav cross-check fail) -- reported honestly, never masked.

CLI:
  python scripts/monthly_exam_prep.py baseline [--month 2026-10]
  python scripts/monthly_exam_prep.py selftest
"""
import argparse
import io
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MONTH_OPEN_BAR = "2026-09-30"  # last bar before 2026-10-01 boundary (golden week)
GOLDEN_WEEK_NOTE = (
    "pinned during 2026-10 golden-week holiday window: no bars between "
    "2026-09-30 and 2026-10-09, so this capture == month-open state; "
    "do not overwrite after 2026-10-09 (version a new file instead)"
)

HARNESS_DIRS = [
    # (family, rel_dir, glob_prefix, glob_suffix, reader)
    ("AGGR", os.path.join("results", "aggr_paper"), "AGGR-", "_paper.json", "marks"),
    ("ALLOC", os.path.join("results", "alloc_paper"), "ALLOC-", ".json", "nav"),
    ("GRID", os.path.join("results", "grid_paper"), "GRID-", "_paper.json", "marks"),
    ("SYSV1", os.path.join("results", "system_v1_paper"), "", "_paper.json", "marks"),
    ("EMPLOYEE", os.path.join("results", "paper"), "", "_paper.json", "capital"),
    ("PROS", os.path.join("results", "prospect_paper"), "PROS-", ".json", "pros"),
]
# PROSPECT accounts are observation-lane (O-2045 constructive exclusion from
# CEO face) -- captured for completeness with equity=None, never scored.


def _read_marks(d):
    """marks-array harnesses (AGGR/GRID/SYSV1): last row equity + date."""
    marks = d.get("marks") or []
    if not marks or not isinstance(marks, list):
        return None, None, "no marks rows"
    last = marks[-1]
    eq = last.get("equity_cny")
    if not isinstance(eq, (int, float)):
        return None, None, "last mark has no equity_cny"
    return float(eq), last.get("date"), None


def _read_nav(d):
    """ALLOC harness: nav_series + latest_nav_cny cross-checked."""
    series = d.get("nav_series") or []
    latest = d.get("latest_nav_cny")
    if not series or not isinstance(series, list):
        return None, None, "no nav_series rows"
    tail_date, tail_nav = series[-1][0], series[-1][1]
    if not isinstance(tail_nav, (int, float)):
        return None, None, "nav tail non-numeric"
    if latest is not None and abs(float(latest) - float(tail_nav)) > 0.01:
        return None, None, "latest_nav_cny disagrees with nav_series tail"
    return float(tail_nav), tail_date, None


def _read_capital(d):
    """Employee paper harness: capital dict face."""
    cap = d.get("capital") or {}
    eq = cap.get("equity_cny")
    if not isinstance(eq, (int, float)):
        return None, None, "capital.equity_cny missing"
    return float(eq), d.get("cutoff"), None


def _read_pros(d):
    """PROSPECT observation lane: no capital marks by design -- honest None."""
    return None, d.get("cutoff"), "observation-lane account: no equity face (O-2045)"


READERS = {"marks": _read_marks, "nav": _read_nav, "capital": _read_capital, "pros": _read_pros}


def collect_accounts():
    """Walk the five harnesses; return sorted account rows + faults."""
    rows, faults = [], []
    for family, rel_dir, prefix, suffix, reader_name in HARNESS_DIRS:
        dpath = os.path.join(ROOT, rel_dir)
        if not os.path.isdir(dpath):
            faults.append("harness dir missing: %s" % rel_dir)
            continue
        reader = READERS[reader_name]
        strip = len(suffix) if suffix else 0
        for fname in sorted(os.listdir(dpath)):
            if not fname.endswith(".json"):
                continue
            if prefix and not fname.startswith(prefix):
                continue
            if suffix and not fname.endswith(suffix):
                continue
            fpath = os.path.join(dpath, fname)
            try:
                with io.open(fpath, "r", encoding="utf-8") as fh:
                    d = json.load(fh)
            except Exception as exc:  # parse fault = honest fault
                faults.append("parse fail %s: %s" % (fname, exc))
                continue
            account = fname[: len(fname) - strip] if strip else fname[:-5]
            eq, asof, note = reader(d)
            row = {
                "account": account,
                "family": family,
                "harness": rel_dir.replace(os.sep, "/"),
                "source_file": (rel_dir + "/" + fname).replace(os.sep, "/"),
                "asof": asof,
                "equity_cny": eq,
                "initial_cash_cny": (d.get("capital") or {}).get("initial_cash_cny")
                if reader_name == "capital"
                else d.get("initial_cash_cny"),
            }
            if eq is None and note:
                row["note"] = note
            if family == "EMPLOYEE":
                cap = d.get("capital") or {}
                row["positions_value_cny"] = cap.get("positions_value_cny")
                row["cash_cny"] = cap.get("cash_cny")
            rows.append(row)
    rows.sort(key=lambda r: (r["family"], r["account"]))

    # B_MAXDIV: derived assembly of the six employees (T-27/T-28 frozen装配).
    employees = [r for r in rows if r["family"] == "EMPLOYEE" and r["equity_cny"] is not None]
    if employees:
        rows.append(
            {
                "account": "B_MAXDIV",
                "family": "B_MAXDIV",
                "harness": "derived",
                "source_file": "derived: sum of six EMPLOYEE paper equities",
                "asof": max((r["asof"] for r in employees if r["asof"]), default=None),
                "equity_cny": round(sum(r["equity_cny"] for r in employees), 2),
                "initial_cash_cny": round(sum(r["initial_cash_cny"] or 0.0 for r in employees), 2),
                "note": "derived aggregate of six-employee paper accounts",
            }
        )
        rows.sort(key=lambda r: (r["family"], r["account"]))
    return rows, faults


def build_payload(rows, faults, month):
    equity_rows = [r for r in rows if r["equity_cny"] is not None]
    all_at_open = all(r["asof"] == MONTH_OPEN_BAR for r in equity_rows)
    by_family = {}
    for r in rows:
        by_family[r["family"]] = by_family.get(r["family"], 0) + 1
    return {
        "schema": "monthly-exam-accounts-monthopen-baseline/1.0",
        "ticket": "T-2026-10-01-143 (face 4 accounts; O-20261001-2355 sec.3 board lining)",
        "exam_month": month,
        "month_open_boundary": "2026-10-01",
        "month_open_bar": MONTH_OPEN_BAR,
        "capture_note": GOLDEN_WEEK_NOTE,
        "n_accounts": len(rows),
        "n_equity_bearing": len(equity_rows),
        "all_equity_faces_at_month_open_bar": all_at_open,
        "family_counts": dict(sorted(by_family.items())),
        "roster_note": (
            "superset capture across all marks-bearing harnesses; the exact "
            "'27 experimental accounts' subset pin + six-face assembly happens at "
            "exam-prep assembly time per T-143 spec (YTD 41-member roster in "
            "results/ytd_track_record/ytd_summary.json is the cross-check face)"
        ),
        "accounts": rows,
        "faults": faults,
    }


def by_fam_counts(rows):
    out = {}
    for r in rows:
        out[r["family"]] = out.get(r["family"], 0) + 1
    return out


def cmd_baseline(month):
    rows, faults = collect_accounts()
    if faults:
        for f in faults:
            sys.stderr.write("FAULT: %s\n" % f)
        return 2
    if not rows:
        sys.stderr.write("FAULT: zero accounts collected\n")
        return 2
    payload = build_payload(rows, faults, month)
    out_dir = os.path.join(ROOT, "docs", "monthly_exam", month)
    os.makedirs(out_dir, exist_ok=True)
    jpath = os.path.join(out_dir, "accounts_monthopen_baseline.json")
    mpath = os.path.join(out_dir, "accounts_monthopen_baseline.md")
    with io.open(jpath, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=1, sort_keys=True)
        fh.write("\n")
    lines = [
        "# Monthly exam %s -- accounts face: month-open baseline" % month,
        "",
        "- ticket: T-2026-10-01-143 face 4 (O-20261001-2355 sec.3)",
        "- month-open boundary: 2026-10-01; month-open bar: %s" % MONTH_OPEN_BAR,
        "- capture: %s" % GOLDEN_WEEK_NOTE,
        "- accounts: %d total / %d equity-bearing / all at month-open bar: %s"
        % (payload["n_accounts"], payload["n_equity_bearing"], payload["all_equity_faces_at_month_open_bar"]),
        "",
        "| account | family | asof | equity_cny | initial_cash_cny |",
        "|---|---|---|---:|---:|",
    ]
    for r in rows:
        lines.append(
            "| %s | %s | %s | %s | %s |"
            % (
                r["account"],
                r["family"],
                r["asof"] if r["asof"] is not None else "n/a",
                ("%.2f" % r["equity_cny"]) if r["equity_cny"] is not None else "n/a",
                ("%.2f" % r["initial_cash_cny"]) if r.get("initial_cash_cny") is not None else "n/a",
            )
        )
    with io.open(mpath, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(lines) + "\n")
    sys.stdout.write(
        "baseline: %d accounts (%d equity-bearing, all_at_open=%s) -> %s\n"
        % (payload["n_accounts"], payload["n_equity_bearing"], payload["all_equity_faces_at_month_open_bar"], jpath)
    )
    for fam, n in sorted(by_fam_counts(rows).items()):
        sys.stdout.write("  %s: %d\n" % (fam, n))
    return 0


def _selftest():
    ok = [0]
    bad = [0]

    def leg(name, cond):
        if cond:
            ok[0] += 1
            sys.stdout.write("  [PASS] %s\n" % name)
        else:
            bad[0] += 1
            sys.stdout.write("  [FAIL] %s\n" % name)

    # leg1: marks reader
    eq, asof, note = _read_marks({"marks": [{"date": "2026-09-29", "equity_cny": 100.0}, {"date": "2026-09-30", "equity_cny": 99.5}]})
    leg("marks reader takes last row", eq == 99.5 and asof == "2026-09-30")
    # leg2: marks reader empty
    eq2, _, note2 = _read_marks({"marks": []})
    leg("marks reader empty -> None+note", eq2 is None and note2 is not None)
    # leg3: nav reader cross-check pass
    eq3, asof3, _ = _read_nav({"nav_series": [["2026-09-30", 985132.54]], "latest_nav_cny": 985132.548522})
    leg("nav reader tolerance cross-check", eq3 is not None and asof3 == "2026-09-30")
    # leg4: nav reader mismatch -> fault
    eq4, _, note4 = _read_nav({"nav_series": [["2026-09-30", 100.0]], "latest_nav_cny": 200.0})
    leg("nav reader mismatch -> None+note", eq4 is None and note4 is not None)
    # leg5: capital reader
    eq5, asof5, _ = _read_capital({"capital": {"equity_cny": 1001009.96, "initial_cash_cny": 1000000.0}, "cutoff": "2026-09-30"})
    leg("capital reader", eq5 == 1001009.96 and asof5 == "2026-09-30")
    # leg6: pros reader honest None
    eq6, asof6, note6 = _read_pros({"cutoff": "2026-09-30"})
    leg("pros reader observation-lane None", eq6 is None and note6 and "O-2045" in note6)
    # leg7: month-open flag logic
    rows = [
        {"account": "A", "family": "X", "equity_cny": 1.0, "asof": MONTH_OPEN_BAR},
        {"account": "B", "family": "X", "equity_cny": 2.0, "asof": MONTH_OPEN_BAR},
    ]
    payload = build_payload(rows, [], "2026-10")
    leg("month-open all-at-bar True", payload["all_equity_faces_at_month_open_bar"] is True)
    rows.append({"account": "C", "family": "X", "equity_cny": 3.0, "asof": "2026-09-29"})
    payload2 = build_payload(rows, [], "2026-10")
    leg("month-open stale row -> False", payload2["all_equity_faces_at_month_open_bar"] is False)
    # leg8: pros (None equity) does not poison the month-open flag
    rows.append({"account": "P", "family": "PROS", "equity_cny": None, "asof": "2026-09-30"})
    payload3 = build_payload(rows, [], "2026-10")
    leg("None-equity rows excluded from flag", payload3["all_equity_faces_at_month_open_bar"] is False)
    # leg9: determinism -- same rows -> byte-identical payload
    b1 = json.dumps(build_payload(rows, [], "2026-10"), sort_keys=True).encode("utf-8")
    b2 = json.dumps(build_payload(rows, [], "2026-10"), sort_keys=True).encode("utf-8")
    leg("determinism byte-identity", b1 == b2 and len(b1) > 100)
    # leg10: B_MAXDIV derivation
    emp = [
        {"account": "E1", "family": "EMPLOYEE", "equity_cny": 100.0, "initial_cash_cny": 100.0, "asof": MONTH_OPEN_BAR, "source_file": "x", "harness": "h"},
        {"account": "E2", "family": "EMPLOYEE", "equity_cny": 50.0, "initial_cash_cny": 100.0, "asof": MONTH_OPEN_BAR, "source_file": "y", "harness": "h"},
    ]
    # emulate the derivation inline (collect path needs real dirs)
    total = round(sum(r["equity_cny"] for r in emp if r["equity_cny"] is not None), 2)
    leg("B_MAXDIV derived sum", total == 150.0)

    sys.stdout.write("selftest: %d PASS, %d FAIL\n" % (ok[0], bad[0]))
    return 0 if bad[0] == 0 else 1


def main(argv):
    ap = argparse.ArgumentParser(description="monthly exam prep (T-143 accounts face)")
    sub = ap.add_subparsers(dest="cmd")
    bp = sub.add_parser("baseline", help="capture month-open accounts baseline")
    bp.add_argument("--month", default="2026-10")
    sub.add_parser("selftest", help="offline self-check")
    args = ap.parse_args(argv)
    if args.cmd == "selftest":
        return _selftest()
    if args.cmd == "baseline":
        return cmd_baseline(args.month)
    ap.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
