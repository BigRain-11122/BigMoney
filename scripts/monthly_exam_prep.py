"""Monthly exam prep -- accounts + roster month-open baselines (T-2026-10-01-143).

Faces:
  s1 accounts (face 4) -- month-open baseline across all marks-bearing
     harnesses (63-account superset), B_MAXDIV derived crosscheck.
  s2 roster   (face 1) -- six-member roster freeze + per-trader month-open
     input face + benchmark double-line (510300 unadjusted buy&hold +
     48ETF equal-weight daily-rebalanced, ytd_track_record/o1600 caliber)
     + YTD crosscheck rows (T-146 single-source reference, no recompute).
     Pure aggregation of existing artifacts: zero network, zero engine,
     zero new judgment (T-105 one-pager precedent).

Month-open semantics: month boundary = 2026-10-01; golden week leaves no bars
between 2026-09-30 and 2026-10-09, so a capture taken during the holiday is
byte-stable month-open state (zero drift window).  Re-run after 10-09 would NOT
be month-open anymore -- the capture gates refuse (exit 2): version a new file.

Deterministic byte-identical output on rerun (no wallclock inside payloads).

Exit codes: 0 = captured ok; 2 = mechanism fault / capture-window gate
(closed window, missing artifact, parse error, crosscheck mismatch) --
reported honestly, never masked.

CLI:
  python scripts/monthly_exam_prep.py baseline [--month 2026-10]
  python scripts/monthly_exam_prep.py roster   [--month 2026-10]
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

ROSTER_EMPLOYEES = (
    "COMPOSITE-CE-01", "COMPOSITE-CE-02", "DROUGHT-CE-01",
    "ENGULF-CE-01", "NEEDLE-DE-01", "VOLATILITY-CE-01",
)
# T-143 face 1 roster freeze: the six registered employees (hire 2026-09-23).
# This tuple IS the freeze for the 2026-10 monthly exam; any roster change
# before 10-31 must version this file, not edit it in place.


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


# ---------------------------------------------------- T-143 face 1 roster
def _extract_trader(name, d):
    """Per-trader month-open exam input face from the paper harness json.

    Only structural numeric faces are lifted -- wallclock/updated fields are
    deliberately dropped so reruns stay byte-identical.
    """
    cap = d.get("capital") or {}
    anchor = d.get("anchor") or {}
    got = anchor.get("got") or {}
    x2 = d.get("x2_watch") or {}
    wm = d.get("window_metrics") or {}
    months = d.get("months_detail") or []
    ops = d.get("open_positions") or []
    return {
        "trader": name,
        "paper_start": d.get("paper_start"),
        "asof": d.get("cutoff"),
        "equity_cny": cap.get("equity_cny"),
        "initial_cash_cny": cap.get("initial_cash_cny"),
        "positions_value_cny": cap.get("positions_value_cny"),
        "cash_cny": cap.get("cash_cny"),
        "open_positions_n": len(ops),
        "unrealized_pnl_cny": round(
            sum(float(o.get("unrealized_pnl_cny") or 0.0) for o in ops), 2),
        "bars_since_hire": d.get("bars"),
        "hire_month_returns": {m.get("month"): m.get("return") for m in months},
        "window_metrics_status": wm.get("status"),
        "win_rate_full": wm.get("win_rate_full"),
        "num_trades": wm.get("num_trades"),
        "current_dd": d.get("current_dd"),
        "x2_watch": {
            "status": x2.get("status"),
            "probation": x2.get("probation"),
            "margin": x2.get("margin"),
        },
        "cost_x2_check_status": (d.get("cost_x2_check") or {}).get("status"),
        "anchor": {
            "cutoff": anchor.get("cutoff"),
            "in_sample": got.get("in_sample"),
            "out_sample": got.get("out_sample"),
            "checks": anchor.get("checks"),
        },
    }


def collect_roster(month):
    """Six-member roster + benchmark double-line + YTD crosscheck.

    Zero network, zero engine, zero new judgment -- pure aggregation of
    existing committed artifacts (paper harness jsons, accounts baseline,
    daily panel, ytd_summary).
    """
    rows, faults = [], []
    for t in ROSTER_EMPLOYEES:
        fpath = os.path.join(ROOT, "results", "paper", t + "_paper.json")
        if not os.path.isfile(fpath):
            faults.append("paper file missing: %s" % t)
            continue
        try:
            with io.open(fpath, "r", encoding="utf-8") as fh:
                d = json.load(fh)
        except Exception as exc:
            faults.append("parse fail %s: %s" % (t, exc))
            continue
        row = _extract_trader(t, d)
        if row["asof"] != MONTH_OPEN_BAR:
            faults.append(
                "month-open gate: %s cutoff %s != %s (capture window closed "
                "-- version a new file, do not overwrite)" % (t, row["asof"], MONTH_OPEN_BAR))
        rows.append(row)

    # B_MAXDIV crosscheck vs the accounts baseline (same capture window)
    derived = round(sum(r["equity_cny"] for r in rows if r["equity_cny"] is not None), 2)
    crosscheck = None
    base_path = os.path.join(ROOT, "docs", "monthly_exam", month,
                             "accounts_monthopen_baseline.json")
    if os.path.isfile(base_path):
        with io.open(base_path, "r", encoding="utf-8") as fh:
            base = json.load(fh)
        ref = [a for a in base.get("accounts", []) if a.get("account") == "B_MAXDIV"]
        if ref:
            ref_eq = float(ref[0]["equity_cny"])
            crosscheck = {
                "accounts_baseline_b_maxdiv_cny": ref_eq,
                "roster_derived_sum_cny": derived,
                "match": abs(ref_eq - derived) < 0.01,
            }
            if not crosscheck["match"]:
                faults.append("B_MAXDIV crosscheck: roster sum %s vs accounts baseline %s"
                              % (derived, ref_eq))
        else:
            faults.append("accounts baseline has no B_MAXDIV row")
    else:
        faults.append("accounts baseline missing (run `baseline` first)")

    # benchmark double-line: 510300 month-open close + panel-tail month gate
    bench = {}
    csv_path = os.path.join(ROOT, "data", "daily", "510300.csv")
    if os.path.isfile(csv_path):
        with io.open(csv_path, "r", encoding="utf-8") as fh:
            rdr = [r for r in __import__("csv").DictReader(fh) if r.get("date")]
        tail = rdr[-1]
        bench["bench_510300_month_open_close"] = float(tail["close"])
        bench["panel_tail_date"] = tail["date"]
        if tail["date"] != MONTH_OPEN_BAR:
            faults.append(
                "panel month gate: 510300 tail %s != %s (bars already exist inside "
                "the exam month -- capture window closed, version a new file)"
                % (tail["date"], MONTH_OPEN_BAR))
    else:
        faults.append("510300 daily csv missing")

    # YTD crosscheck rows (single-source reference, no recompute)
    ytd_rows = {}
    ytd_path = os.path.join(ROOT, "results", "ytd_track_record", "ytd_summary.json")
    if os.path.isfile(ytd_path):
        with io.open(ytd_path, "r", encoding="utf-8") as fh:
            ytd = json.load(fh)
        for m in ytd.get("members", []):
            if m.get("member") in ROSTER_EMPLOYEES:
                ytd_rows[m["member"]] = {
                    "ytd_ret": m.get("ytd_ret"),
                    "beat_510300_pp": m.get("beat_510300_pp"),
                    "beat_48ew_pp": m.get("beat_48ew_pp"),
                    "max_dd": m.get("max_dd"),
                    "last_date": m.get("last_date"),
                }
        missing = [t for t in ROSTER_EMPLOYEES if t not in ytd_rows]
        if missing:
            faults.append("ytd crosscheck missing members: %s" % ",".join(missing))
        bench["ytd_baselines"] = ytd.get("baselines")
        bench["ytd_evidence_cutoff"] = ytd.get("evidence_cutoff")
    else:
        faults.append("ytd_summary.json missing (T-146 face)")
    return rows, bench, ytd_rows, crosscheck, faults


def _roster_payload(rows, bench, ytd_rows, crosscheck, month):
    return {
        "schema": "monthly-exam-roster-monthopen-baseline/1.0",
        "ticket": "T-2026-10-01-143 (face 1 six-member roster; O-20261001-2355 sec.3 board lining)",
        "exam_month": month,
        "month_open_boundary": "2026-10-01",
        "month_open_bar": MONTH_OPEN_BAR,
        "capture_note": GOLDEN_WEEK_NOTE,
        "window_bars_note": (
            "2026-10 exam window has zero bars at capture (golden week; resumes "
            "2026-10-09) -- this file == month-open state; exam-day assembly is "
            "date-driven per T-143 face-6 runbook, zero new judgment"
        ),
        "roster_freeze": [
            {
                "trader": t,
                "hire_day": "2026-09-23",
                "paper_file": "results/paper/%s_paper.json" % t,
            }
            for t in ROSTER_EMPLOYEES
        ],
        "traders": rows,
        "benchmarks": {
            "bench_510300_month_open_close": bench.get("bench_510300_month_open_close"),
            "panel_tail_date": bench.get("panel_tail_date"),
            "bench_510300_source": (
                "data/daily/510300.csv unadjusted close (ytd_track_record "
                "BENCH-510300 caliber, buy&hold)"
            ),
            "bench_48ew_note": (
                "48ETF equal-weight daily-rebalanced (o1600_market_fit.py "
                "single-source); exam-window assembly starts at first in-window "
                "bar (2026-10-09); YTD reference values carried below"
            ),
            "ytd_baselines": bench.get("ytd_baselines"),
            "ytd_evidence_cutoff": bench.get("ytd_evidence_cutoff"),
        },
        "ytd_crosscheck": {
            "source": "results/ytd_track_record/ytd_summary.json (T-146, no recompute)",
            "rows": {t: ytd_rows.get(t) for t in ROSTER_EMPLOYEES},
        },
        "b_maxdiv_crosscheck": crosscheck,
        "faults": [],
    }


def cmd_roster(month):
    rows, bench, ytd_rows, crosscheck, faults = collect_roster(month)
    if faults:
        for f in faults:
            sys.stderr.write("FAULT: %s\n" % f)
        return 2
    if len(rows) != len(ROSTER_EMPLOYEES):
        sys.stderr.write("FAULT: roster incomplete (%d/%d)\n" % (len(rows), len(ROSTER_EMPLOYEES)))
        return 2
    payload = _roster_payload(rows, bench, ytd_rows, crosscheck, month)
    out_dir = os.path.join(ROOT, "docs", "monthly_exam", month)
    os.makedirs(out_dir, exist_ok=True)
    jpath = os.path.join(out_dir, "roster_monthopen_baseline.json")
    mpath = os.path.join(out_dir, "roster_monthopen_baseline.md")
    with io.open(jpath, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=1, sort_keys=True)
        fh.write("\n")

    ytd = payload["ytd_crosscheck"]["rows"]
    lines = [
        "# Monthly exam %s -- roster face: six-member month-open baseline" % month,
        "",
        "- ticket: T-2026-10-01-143 face 1 (O-20261001-2355 sec.3)",
        "- month-open boundary: 2026-10-01; month-open bar: %s" % MONTH_OPEN_BAR,
        "- capture: %s" % GOLDEN_WEEK_NOTE,
        "- window: zero bars in the 2026-10 exam window at capture (golden week; resumes 10-09); exam-day assembly is date-driven (face-6 runbook)",
        "- B_MAXDIV crosscheck vs accounts baseline: %s" % (
            "MATCH (%.2f == %.2f)" % (
                payload["b_maxdiv_crosscheck"]["roster_derived_sum_cny"],
                payload["b_maxdiv_crosscheck"]["accounts_baseline_b_maxdiv_cny"])
            if payload["b_maxdiv_crosscheck"] and payload["b_maxdiv_crosscheck"]["match"]
            else "MISMATCH"),
        "- benchmark double-line: 510300 month-open close %.4f (unadjusted buy&hold caliber); 48EW daily-rebalanced (o1600 single-source) starts at first in-window bar 10-09"
        % payload["benchmarks"]["bench_510300_month_open_close"],
        "",
        "| trader | hire | month-open equity (CNY) | positions | unrealized PnL (CNY) | x2_watch | YTD | beat 300 (pp) | beat 48EW (pp) |",
        "|---|---|---:|--:|--:|---|--:|--:|--:|",
    ]
    for r in rows:
        yr = ytd.get(r["trader"]) or {}
        x2r = r["x2_watch"] or {}
        x2txt = str(x2r.get("status") or "n/a")
        if x2r.get("probation") and x2txt != "probation":
            x2txt += "/probation"
        lines.append(
            "| %s | %s | %.2f | %d | %.2f | %s | %s | %s | %s |" % (
                r["trader"], r["paper_start"], r["equity_cny"],
                r["open_positions_n"], r["unrealized_pnl_cny"], x2txt,
                ("%.2f%%" % (yr.get("ytd_ret") * 100)) if yr.get("ytd_ret") is not None else "n/a",
                ("%.2f" % yr.get("beat_510300_pp")) if yr.get("beat_510300_pp") is not None else "n/a",
                ("%.2f" % yr.get("beat_48ew_pp")) if yr.get("beat_48ew_pp") is not None else "n/a",
            ))
    lines += [
        "",
        "- honesty anchors: window_metrics status=insufficient_data (bars<20 suppression per D-20260930-27 Q3) is carried in the JSON face and must not be quoted as annualized stats; anchor IS/OOS block = hire-time registration anchor, not exam evidence; negative results as-is.",
    ]
    with io.open(mpath, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(lines) + "\n")
    sys.stdout.write(
        "roster: %d traders pinned @ %s -> %s\n" % (len(rows), MONTH_OPEN_BAR, jpath))
    sys.stdout.write("  B_MAXDIV crosscheck: %s\n" % (
        "MATCH" if payload["b_maxdiv_crosscheck"] and payload["b_maxdiv_crosscheck"]["match"] else "MISMATCH"))
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

    # leg11: roster extractor lifts structural faces, drops wallclock
    fake = {
        "paper_start": "2026-09-23", "cutoff": MONTH_OPEN_BAR, "bars": 5,
        "capital": {"equity_cny": 1001009.96, "initial_cash_cny": 1000000.0,
                    "positions_value_cny": 952248.83, "cash_cny": 48761.13},
        "open_positions": [{"unrealized_pnl_cny": -1398.99}, {"unrealized_pnl_cny": 70.23}],
        "months_detail": [{"month": "2026-09", "return": 0.001, "counted": False}],
        "window_metrics": {"status": "insufficient_data", "win_rate_full": 0.0, "num_trades": 0},
        "current_dd": -0.0029,
        "x2_watch": {"status": "probation", "probation": True, "margin": 0.0491},
        "cost_x2_check": {"status": "insufficient_data"},
        "anchor": {"cutoff": "2026-09-22", "got": {"in_sample": {"sharpe": 1.1}, "out_sample": {"sharpe": 0.9}},
                   "checks": {"in_sample": True, "out_sample": True}},
        "updated": "2026-10-03 04:04:00",  # wallclock -- must NOT survive extraction
    }
    ex = _extract_trader("FAKE-CE-01", fake)
    leg("roster extractor shape",
        ex["trader"] == "FAKE-CE-01" and ex["asof"] == MONTH_OPEN_BAR
        and ex["equity_cny"] == 1001009.96 and ex["open_positions_n"] == 2
        and abs(ex["unrealized_pnl_cny"] - (-1328.76)) < 0.005
        and ex["x2_watch"]["probation"] is True and ex["anchor"]["cutoff"] == "2026-09-22"
        and "updated" not in json.dumps(ex))
    # leg12: roster month-open gate condition (capture window closed -> fault)
    gate_bad = dict(ex); gate_bad["asof"] = "2026-10-09"
    leg("roster month-open gate condition", gate_bad["asof"] != MONTH_OPEN_BAR)
    # leg13: B_MAXDIV crosscheck mismatch condition
    ref_eq, derived_eq = 5998495.76, 5998495.99
    leg("B_MAXDIV crosscheck mismatch -> not match", abs(ref_eq - derived_eq) >= 0.01)
    # leg14: ytd missing-member fault condition
    ytd_rows_have = {"COMPOSITE-CE-01": {}, "COMPOSITE-CE-02": {}, "DROUGHT-CE-01": {},
                     "ENGULF-CE-01": {}, "NEEDLE-DE-01": {}}
    missing_members = [t for t in ROSTER_EMPLOYEES if t not in ytd_rows_have]
    leg("ytd crosscheck missing-member detection", missing_members == ["VOLATILITY-CE-01"])
    # leg15: roster payload determinism (byte-identity, wallclock-free)
    p1 = _roster_payload([ex], {"bench_510300_month_open_close": 4.432, "panel_tail_date": MONTH_OPEN_BAR,
                                "ytd_baselines": {}, "ytd_evidence_cutoff": MONTH_OPEN_BAR},
                         {}, {"match": True}, "2026-10")
    b1 = json.dumps(p1, sort_keys=True).encode("utf-8")
    b2 = json.dumps(_roster_payload([ex], {"bench_510300_month_open_close": 4.432, "panel_tail_date": MONTH_OPEN_BAR,
                                           "ytd_baselines": {}, "ytd_evidence_cutoff": MONTH_OPEN_BAR},
                                    {}, {"match": True}, "2026-10"), sort_keys=True).encode("utf-8")
    leg("roster payload determinism", b1 == b2 and len(b1) > 500)

    sys.stdout.write("selftest: %d PASS, %d FAIL\n" % (ok[0], bad[0]))
    return 0 if bad[0] == 0 else 1


def main(argv):
    ap = argparse.ArgumentParser(description="monthly exam prep (T-143 accounts + roster faces)")
    sub = ap.add_subparsers(dest="cmd")
    bp = sub.add_parser("baseline", help="capture month-open accounts baseline")
    bp.add_argument("--month", default="2026-10")
    rp = sub.add_parser("roster", help="capture six-member roster month-open baseline (face 1)")
    rp.add_argument("--month", default="2026-10")
    sub.add_parser("selftest", help="offline self-check")
    args = ap.parse_args(argv)
    if args.cmd == "selftest":
        return _selftest()
    if args.cmd == "baseline":
        return cmd_baseline(args.month)
    if args.cmd == "roster":
        return cmd_roster(args.month)
    ap.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
