"""How wrong was the premium we printed? Measured, not bounded.

r2228. r2227 found that 90 legs of the 2026-11-27 snapshot are priced against a
denominator that is not that session's, and answered "how wrong" with an
interval: reband the printed premium over that leg's own NAV-return
distribution. An interval is the honest answer for a number that has not been
published yet. It is a weaker answer than the one available a day later.

This face measures the error instead. A premium print is

    printed premium = close / NAV_(session-1) - 1

so once the NAV for the session itself is published, the number we were missing
is in hand. `results/etf_premium/premium_history.csv` carries the NAV level for
every print *together with the date that NAV belongs to*, so a later row hands
over NAV_k for the earlier session k. Nothing external is needed.

What the arithmetic says. With r = NAV_k / NAV_(k-1) - 1 that session's NAV
return, the printed premium is displaced by exactly

    printed - true = r * (1 + true)

i.e. a stale denominator does not make the reading noisy, it moves it by one
whole NAV day, in that day's direction, scaled by the premium. So a fund that
rallies looks dearer than it is, and a fund that falls looks cheaper -- by
construction, not by luck. This face checks that identity on every measurable
print instead of asserting it, and reports the residual as the arithmetic proof.

Answers:
  1. how large the misstatement is (median / p90 / worst, in pp);
  2. whether it is the NAV day itself (identity residual) or something else;
  3. which legs carry it, and how the headline premiums read against the truth;
  4. whether r2227's printed band contained the truth where both exist.

Rows whose session NAV has not been published since are counted UNMEASURED,
never as zero error. The snapshot series is scanned the same way as a second,
broader source; today it can recover nothing (every one-off lag heals by using
the NEXT session's NAV, so the missing level never appears), and it says so.

Output: results/etf_nav/restatement.json + research/ETF_NAV_RESTATEMENT.md.

Usage:
    python scripts/etf_nav_restatement.py run
    python scripts/etf_nav_restatement.py check
    python scripts/etf_nav_restatement.py selftest

Exploratory measurement; not a verdict on the book, no ledger booking.
"""
import argparse
import csv
import json
import os
import statistics
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from scripts import etf_nav_lag_face as L            # noqa: E402

SNAP_DIR = L.SNAP_DIR
CAL_PATH = L.CAL_PATH
HIST_PATH = os.path.join(ROOT, "results", "etf_premium", "premium_history.csv")
OUT_JSON = os.path.join(ROOT, "results", "etf_nav", "restatement.json")
OUT_MD = os.path.join(ROOT, "research", "ETF_NAV_RESTATEMENT.md")

BIG_ERROR_LINE = 0.01       # 1.00 pp of premium -- the size that moves a decision
MIN_BAND_HISTORY = 3        # returns needed before the printed band is judged
IDENTITY_TOL_PP = 1e-3      # arithmetic identity; the residual is bounded by the
                            # premium's stored precision (1e-6 -> 1e-4 pp)
EVENT_LINE = 0.35           # |NAV day move| above this = split / distribution,
                            # not a price move (same 35% line the book uses)


# ---------------------------------------------------------------- pure helpers
def implied_nav(price, premium):
    """nav = price / (1 + premium).  None where the print cannot carry one."""
    try:
        price = float(price)
        premium = float(premium)
    except (TypeError, ValueError):
        return None
    if price <= 0 or (1.0 + premium) <= 0:
        return None
    return price / (1.0 + premium)


def level_tape(prints):
    """{nav_session: {nav, from_session, revisions}} from a series of prints.

    Each print carries `nav` for `nav_date`, so the earliest print made AFTER a
    session hands over that session's NAV. Revisions are counted, not hidden:
    a vendor restating a NAV would otherwise silently move every measurement
    built on it.
    """
    tape = {}
    for p in sorted(prints, key=lambda p: p["session"]):
        d = p.get("nav_session")
        nav = p.get("nav")
        if not d or nav is None or nav <= 0:
            continue
        if d not in tape and p["session"] > d:
            tape[d] = {"nav": nav, "from_session": p["session"], "revisions": 0}
        elif d in tape and abs(tape[d]["nav"] - nav) > 1e-9:
            tape[d]["revisions"] += 1
    return tape


def measure_prints(prints, index, source):
    """Rows printed against a denominator older than their own session.

    The level tape is built PER LEG. A tape keyed by date alone would hand one
    fund's NAV to another fund printed the same day -- which is how a bond ETF
    ends up with a +100% "true premium".
    """
    by_code = {}
    for p in prints:
        by_code.setdefault(p["code"], []).append(p)
    tapes = {code: level_tape(mine) for code, mine in by_code.items()}
    rows = []
    unmeasured = 0
    n_same_day = 0
    n_events = 0
    for code, mine in by_code.items():
        tape = tapes[code]
        for p in sorted(mine, key=lambda p: p["session"]):
            lag = L.lag_of(p["session"], p.get("nav_session"), index)
            if lag is None:
                continue
            if lag <= 0:
                n_same_day += 1
                continue
            premium = p.get("premium")
            got = tape.get(p["session"])
            if premium is None or not got or not (p.get("close", 0) > 0):
                unmeasured += 1
                continue
            nav_true = got["nav"]
            prev = max([d for d in tape if d < p["session"]], default=None)
            true_premium = p["close"] / nav_true - 1.0
            err = premium - true_premium
            nav_move = (nav_true / tape[prev]["nav"] - 1.0) if prev else None
            if nav_move is not None and abs(nav_move) > EVENT_LINE:
                # a share conversion or a distribution is not a premium move
                n_events += 1
                continue
            pred = (nav_move * (1.0 + true_premium)) if nav_move is not None else None
            rows.append({
                "source": source,
                "code": code,
                "name": p.get("name") or code,
                "session": p["session"],
                "nav_session_printed": p.get("nav_session"),
                "lag_trading_days": lag,
                "close": p["close"],
                "premium_printed": premium,
                "nav_true": nav_true,
                "premium_true": true_premium,
                "error_pp": 100.0 * err,
                "nav_move_that_session": nav_move,
                "predicted_error_pp": None if pred is None else 100.0 * pred,
                "identity_residual_pp": (None if pred is None
                                         else 100.0 * (err - pred)),
                "recovered_from": got["from_session"],
            })
    return rows, unmeasured, n_same_day, tapes, n_events


def _band(vals, band=(0.10, 0.90)):
    if not vals:
        return {"n": 0, "p10": None, "p50": None, "p90": None, "worst": None}
    s = sorted(vals)
    n = len(s)
    return {"n": n,
            "p10": s[min(n - 1, max(0, int(band[0] * n)))],
            "p50": statistics.median(s),
            "p90": s[min(n - 1, max(0, int(band[1] * n)))],
            "worst": max(abs(min(s)), abs(max(s)))}


def band_check(rows, tapes):
    """Did r2227's method (reband on that leg's own NAV returns) cover the truth?"""
    inside = outside = no_band = 0
    examples = []
    for r in rows:
        leg_tape = tapes.get(r["code"], {})
        days = sorted(d for d in leg_tape if d < r["session"])
        vals = [leg_tape[d]["nav"] for d in days]
        rets = [vals[i] / vals[i - 1] - 1.0 for i in range(1, len(vals))
                if vals[i - 1] > 0]
        band = _band(rets[-120:])
        if band["n"] < MIN_BAND_HISTORY or band["p90"] is None:
            no_band += 1
            continue
        rb = L.reband(r["premium_printed"], band)
        lo, hi = rb["lo_p10_p90"], rb["hi_p10_p90"]
        if lo <= r["premium_true"] <= hi:
            inside += 1
        else:
            outside += 1
            if len(examples) < 5:
                examples.append({"code": r["code"], "session": r["session"],
                                 "printed": r["premium_printed"],
                                 "true": r["premium_true"], "band": [lo, hi]})
    return {"inside": inside, "outside": outside, "no_band": no_band,
            "n": inside + outside, "outside_examples": examples}


def summarize(rows, unmeasured, n_same_day, other_unmeasured=0, n_events=0):
    errs = [r["error_pp"] for r in rows]
    abs_errs = [abs(e) for e in errs]
    resids = [abs(r["identity_residual_pp"]) for r in rows
              if r["identity_residual_pp"] is not None]
    by_lag = {}
    for r in rows:
        by_lag.setdefault(str(r["lag_trading_days"]), []).append(abs(r["error_pp"]))
    per_code = {}
    for r in rows:
        per_code.setdefault(r["code"], []).append(r)
    worst = max(rows, key=lambda r: abs(r["error_pp"])) if rows else None
    buckets = {"<0.5%": [], "0.5-1%": [], "1-2%": [], ">=2%": []}
    for r in rows:
        mv = r.get("nav_move_that_session")
        if mv is None:
            continue
        a = abs(mv)
        key = ("<0.5%" if a < 0.005 else "0.5-1%" if a < 0.01
               else "1-2%" if a < 0.02 else ">=2%")
        buckets[key].append(abs(r["error_pp"]))
    by_move = {k: {"n": len(v),
                   "median_abs_error_pp": (statistics.median(v) if v else None)}
               for k, v in buckets.items()}
    return {
        "n_measured": len(rows),
        "n_unmeasured": unmeasured + other_unmeasured,
        "n_same_day_prints": n_same_day,
        "n_nav_events_excluded": n_events,
        "by_nav_move": by_move,
        "median_abs_error_pp": statistics.median(abs_errs) if abs_errs else None,
        "mean_signed_error_pp": (sum(errs) / len(errs)) if errs else None,
        "p90_abs_error_pp": (sorted(abs_errs)[min(len(abs_errs) - 1,
                                                   int(0.90 * len(abs_errs)))]
                             if abs_errs else None),
        "max_abs_error_pp": max(abs_errs) if abs_errs else None,
        "n_error_shares_printed_sign": sum(1 for r in rows
                                           if r["error_pp"] * r["premium_printed"] > 0),
        "identity_max_residual_pp": max(resids) if resids else None,
        "identity_rows_checked": len(resids),
        "by_lag_median_abs_pp": {k: statistics.median(v) for k, v in sorted(by_lag.items())},
        "by_lag_n": {k: len(v) for k, v in sorted(by_lag.items())},
        "per_code": {code: {
            "n": len(v),
            "median_abs_error_pp": statistics.median([abs(x["error_pp"]) for x in v]),
            "max_abs_error_pp": max(abs(x["error_pp"]) for x in v),
            "median_printed_premium": statistics.median([x["premium_printed"] for x in v]),
        } for code, v in sorted(per_code.items())},
        "worst": ({"code": worst["code"], "session": worst["session"],
                   "printed": worst["premium_printed"], "true": worst["premium_true"],
                   "error_pp": worst["error_pp"],
                   "lag": worst["lag_trading_days"]} if worst else None),
    }


def verdict_for(summary):
    if not summary["n_measured"]:
        return "NOTHING_TO_MEASURE_YET"
    med = summary["median_abs_error_pp"] or 0.0
    resid = summary["identity_max_residual_pp"]
    clean = resid is not None and resid <= IDENTITY_TOL_PP
    if med >= 100.0 * BIG_ERROR_LINE:
        if clean:
            return "A_STALE_DENOMINATOR_MOVES_THE_PREMIUM_BY_ONE_WHOLE_NAV_DAY"
        return "STALE_DENOMINATOR_MISSTATES_THE_PREMIUM_BY_MORE_THAN_A_POINT"
    if clean:
        return "THE_DISPLACEMENT_IS_THE_NAV_DAY_AND_IT_IS_SMALL_ON_MEDIAN"
    return "STALE_DENOMINATOR_TYPICALLY_COSTS_LESS_THAN_A_POINT"


def compose_statement(face):
    s = face["summary"]
    if not s["n_measured"]:
        return ("No print in this repo's data has had the NAV its own session "
                "needed published since, so the size of the misstatement is "
                "unmeasured -- not zero.")
    bits = ["%d premium prints can be checked exactly, because a later print "
            "carries the NAV they were missing (%d lagging prints still cannot; "
            "%d prints needed no correction at all)."
            % (s["n_measured"], s["n_unmeasured"], s["n_same_day_prints"])]
    bits.append("Median misstatement %.2f pp of premium, p90 %.2f pp, worst "
                "%.2f pp."
                % (s["median_abs_error_pp"], s["p90_abs_error_pp"],
                   s["max_abs_error_pp"]))
    if (s["identity_max_residual_pp"] is not None
            and s["identity_max_residual_pp"] <= IDENTITY_TOL_PP):
        bits.append("On all %d rows where the session's NAV return is known, the "
                    "error equals that NAV return times (1+true premium) to within "
                    "%.1e pp: the reading is not noisy, it is displaced by exactly "
                    "one NAV day, in that day's direction."
                    % (s["identity_rows_checked"], s["identity_max_residual_pp"]))
    w = s["worst"]
    if w:
        bits.append("Worst case: %s on %s printed %+.2f%% against a stale "
                    "denominator while the true premium was %+.2f%% -- the row was "
                    "wrong by %.2f pp."
                    % (w["code"], w["session"], 100 * w["printed"],
                       100 * w["true"], w["error_pp"]))
    mv = [k for k in ("<0.5%", "0.5-1%", "1-2%", ">=2%")
          if s["by_nav_move"].get(k, {}).get("n")]
    if len(mv) >= 2:
        lo_k, hi_k = mv[0], mv[-1]
        lo = s["by_nav_move"][lo_k]["median_abs_error_pp"]
        hi = s["by_nav_move"][hi_k]["median_abs_error_pp"]
        bits.append(
            "It is not uniform: on prints whose NAV barely moved (%s) the median "
            "error is %.2f pp, while on the %s moves it is %.2f pp -- the reading "
            "is most wrong exactly on the days the fund moved most."
            % (lo_k, lo, hi_k, hi))
    if s["n_nav_events_excluded"]:
        bits.append("%d print(s) were excluded as share conversions or "
                    "distributions (|NAV day move| > %.0f%%), because a split is "
                    "not a premium move."
                    % (s["n_nav_events_excluded"], 100 * EVENT_LINE))
    b = face["band"]
    if b["n"]:
        bits.append("Checked against r2227's band on the %d rows where both exist: "
                    "the band contained the truth %d times and missed it %d times."
                    % (b["n"], b["inside"], b["outside"]))
    else:
        bits.append("The band could not be checked: no measured row has enough "
                    "recovered NAV history behind it.")
    return " ".join(bits)


def build(snaps, index, hist):
    rows_h, un_h, same_h, tapes_h, ev_h = measure_prints(
        hist, index, "premium_history")
    rows_s, un_s, same_s, tapes_s, ev_s = (measure_prints(snaps, index, "snapshot_series")
                                           if snaps else ([], 0, 0, {}, 0))
    rows = rows_h + rows_s
    summary = summarize(rows, un_h, same_h + same_s, other_unmeasured=un_s,
                        n_events=ev_h + ev_s)
    summary["per_source"] = {
        "premium_history": {"n_measured": len(rows_h), "n_unmeasured": un_h,
                            "n_same_day_prints": same_h, "n_nav_events": ev_h},
        "snapshot_series": {"n_measured": len(rows_s), "n_unmeasured": un_s,
                            "n_same_day_prints": same_s, "n_nav_events": ev_s},
    }
    tapes = dict(tapes_h)
    tapes.update({k: v for k, v in tapes_s.items()
                  if k not in tapes})
    band = band_check(rows, tapes)
    # the published row list is the tail, not the population: aggregates are the
    # face, and a 3.6 MB re-commit every session is a cost with no reader
    tail = sorted(rows, key=lambda r: -abs(r["error_pp"]))[:30]
    latest = max([r["session"] for r in rows], default=None)
    face = {
        "generated": None,
        "evidence_cutoff": latest,
        "n_snapshots": len(snaps),
        "summary": summary,
        "band": band,
        "n_rows": len(rows),
        "rows": tail,
        "rows_note": ("the 30 largest |error| rows; the aggregate in `summary` is "
                      "derived over all rows, rerun `run` for the population"),
        "verdict": verdict_for(summary),
        "statement": None,
        "thresholds": {"big_error_pp": 100.0 * BIG_ERROR_LINE,
                       "min_band_history": MIN_BAND_HISTORY,
                       "identity_tol_pp": IDENTITY_TOL_PP},
        "notes": [
            "printed premium = close / NAV(nav_session) - 1, so a later print "
            "tagged with that session hands over the NAV we were missing; no "
            "external source is used.",
            "error = printed - true, in pp. Positive means the row overstated the "
            "premium: the leg looked dearer than it was.",
            "The identity printed - true = r*(1+true) is arithmetic, so the "
            "residual column is a check on the measurement, not a second finding; it "
            "is bounded by the stored precision of the printed premium (~1e-4 pp).",
            "A lagging print whose session NAV never appeared is counted as "
            "unmeasured, never as a zero error.",
            "Prints whose NAV day move exceeds EVENT_LINE (35%) are excluded as "
            "share conversions or distributions, and counted; a split is not a "
            "premium move.",
            "A day on which both the price and the NAV jump (an ex-dividend day) "
            "is COUNTED as a misstatement, because from the reader's side it is "
            "one -- but its cause is the distribution, and this face has no "
            "ex-dividend flag, so it cannot separate that cause from the lag.",
            "Scale: on a position worth 100,000 CNY, one point of premium is about "
            "1,000 CNY of NAV paid over or under. This face sizes nothing.",
        ],
    }
    face["statement"] = compose_statement(face)
    return face


# ------------------------------------------------------------------- loaders
def load_history(path):
    """[{code, name, session, close, nav, nav_session, premium}] in date order."""
    out = {}
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf-8", newline="") as fh:
        for r in csv.DictReader(fh):
            code = (r.get("symbol") or "").strip()
            session = (r.get("date") or "").strip()
            if not code or not session:
                continue
            try:
                close = float(r["close"])
                nav = float(r["nav"]) if r.get("nav") not in (None, "") else None
                prem = (float(r["premium_pct"]) / 100.0
                        if r.get("premium_pct") not in (None, "") else None)
            except (TypeError, ValueError):
                continue
            out.setdefault(code, []).append({
                "code": code, "name": code, "session": session, "close": close,
                "nav": nav, "nav_session": (r.get("nav_date") or "").strip(),
                "premium": prem,
            })
    rows = []
    for code in out:
        rows.extend(sorted(out[code], key=lambda p: p["session"]))
    return rows


def _snapshot_prints(snaps):
    """Flatten the snapshot series into the same print shape."""
    out = []
    for snap in snaps:
        for code, row in snap["rows"].items():
            out.append({"code": code, "name": row.get("name") or code,
                        "session": snap["session"], "close": float(row["price"]),
                        "nav": implied_nav(row.get("price"), row.get("premium")),
                        "nav_session": (row.get("nav_session") or "").strip(),
                        "premium": row.get("premium")})
    return out


# ----------------------------------------------------------------------- io
def write_faces(face):
    os.makedirs(os.path.dirname(OUT_JSON), exist_ok=True)
    with open(OUT_JSON, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(face, fh, ensure_ascii=False, indent=2, sort_keys=False)
        fh.write("\n")
    s = face["summary"]
    b = face["band"]

    def pp(x):
        return "-" if x is None else "%.2f pp" % x

    lines = ["# ETF NAV restatement face", "",
             "Generated %s · evidence cutoff %s" % (face["generated"],
                                                    face["evidence_cutoff"]),
             "", "Verdict: `%s`" % face["verdict"], "", face["statement"] or "", "",
             "## Measured misstatement", "",
             "| prints measured | still unmeasured | needed no correction | median abs | p90 abs | worst |",
             "|---|---|---|---|---|---|",
             "| %d | %d | %d | %s | %s | %s |" % (
                 s["n_measured"], s["n_unmeasured"], s["n_same_day_prints"],
                 pp(s["median_abs_error_pp"]), pp(s["p90_abs_error_pp"]),
                 pp(s["max_abs_error_pp"])),
             "", "### By leg", "",
             "| code | prints | median printed premium | median abs error | worst |",
             "|---|---|---|---|---|"]
    for code, st in s["per_code"].items():
        lines.append("| %s | %d | %+.2f%% | %.2f pp | %.2f pp |" % (
            code, st["n"], 100 * st["median_printed_premium"],
            st["median_abs_error_pp"], st["max_abs_error_pp"]))
    if s["by_lag_median_abs_pp"]:
        counts = s.get("by_lag_n") or {}
        lines += ["", "### By lag length", "",
                  "| lag (trading days) | prints | median abs error |", "|---|---|---|"]
        for lag, med in s["by_lag_median_abs_pp"].items():
            lines.append("| %s | %d | %.2f pp |" % (lag, counts.get(lag, 0), med))
    if s.get("by_nav_move"):
        lines += ["", "### Error by how far that day's NAV moved", "",
                  "| |NAV day move| | prints | median abs error |", "|---|---|---|"]
        for k in ("<0.5%", "0.5-1%", "1-2%", ">=2%"):
            b_ = s["by_nav_move"].get(k) or {}
            if b_.get("n"):
                lines.append("| %s | %d | %.2f pp |"
                             % (k, b_["n"], b_["median_abs_error_pp"]))
    lines += ["", "Rows published above are the 30 largest |error| of %d; the "
              "aggregates are derived over every row." % face.get("n_rows", 0), ""]
    lines += ["", "### Identity check (printed - true == r*(1+true))", "",
              "| rows checked | max abs residual |", "|---|---|",
              "| %d | %.2e pp |" % (s["identity_rows_checked"],
                                    s["identity_max_residual_pp"] or 0.0),
              "", "### Band check (r2227 method)", "",
              "| inside | outside | no band |", "|---|---|---|",
              "| %d | %d | %d |" % (b["inside"], b["outside"], b["no_band"])]
    if b["outside_examples"]:
        lines += ["", "Truth fell outside the printed band on:", "",
                  "| code | session | printed | true | band |", "|---|---|---|---|---|"]
        for e in b["outside_examples"]:
            lines.append("| %s | %s | %+.2f%% | %+.2f%% | %+.2f%%..%+.2f%% |" % (
                e["code"], e["session"], 100 * e["printed"], 100 * e["true"],
                100 * e["band"][0], 100 * e["band"][1]))
    lines += ["", "## Notes", ""] + ["- " + n for n in face["notes"]] + [""]
    with open(OUT_MD, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(lines))


# -------------------------------------------------------------------- check
def run_check():
    if not os.path.exists(OUT_JSON):
        print("CHECK FAILED: face missing at %s" % OUT_JSON)
        return 3
    snaps = L.load_snaps(SNAP_DIR)
    face = build(_snapshot_prints(snaps), L.index_of(L.load_calendar()),
                 load_history(HIST_PATH))
    on_disk = json.load(open(OUT_JSON, encoding="utf-8"))
    problems = [k for k in ("evidence_cutoff", "n_rows", "summary", "band",
                            "verdict", "rows", "statement")
                if on_disk.get(k) != face.get(k)]
    if problems:
        print("STALE: %s drifted from its inputs (%s). Rerun `run`."
              % (os.path.basename(OUT_JSON), ", ".join(problems)))
        return 3
    print("CHECK OK: %s matches a fresh derive from the same inputs"
          % os.path.basename(OUT_JSON))
    return 0


# ----------------------------------------------------------------- selftest
def selftest():
    cal = ["2026-11-20", "2026-11-23", "2026-11-24", "2026-11-25", "2026-11-26",
           "2026-11-27"]
    idx = L.index_of(cal)
    legs = 0
    fails = []

    def leg(name, ok, detail=""):
        nonlocal legs
        legs += 1
        if not ok:
            fails.append("%s %s" % (name, detail))

    def p(session, nav_session, close, nav, premium):
        return {"code": "X", "name": "X", "session": session,
                "nav_session": nav_session, "close": close, "nav": nav,
                "premium": premium}

    # 1. the denominator a print carries
    leg("implied-nav-exact", abs(implied_nav(1.659, 0.000965367) - 1.6574) < 1e-5)
    leg("implied-nav-guard", implied_nav(1.0, -1.0) is None)
    leg("implied-nav-bad-input", implied_nav("x", 0.01) is None)

    # 2. a T+1 leg: every print lags, and the next print hands over the missing NAV
    prints = [
        p("2026-11-24", "2026-11-23", 1.898, 1.7569, 0.080311),
        p("2026-11-25", "2026-11-24", 1.854, 1.7474, 0.061004),
        p("2026-11-26", "2026-11-25", 1.873, 1.7454, 0.073106),
        p("2026-11-27", "2026-11-26", 1.926, 1.7422, 0.105490),
    ]
    rows, unmeasured, same_day, _tap, _ev = measure_prints(prints, idx, "t")
    leg("t+1-all-lag", same_day == 0 and len(rows) + unmeasured == len(prints))
    leg("last-print-unmeasured", unmeasured == 1)
    r = [x for x in rows if x["session"] == "2026-11-26"][0]
    # NAV for 11-26 = 1.7422 (printed on 11-27); true premium = 1.873/1.7422 - 1
    leg("true-premium-arithmetic",
        abs(r["premium_true"] - (1.873 / 1.7422 - 1.0)) < 1e-9, r["premium_true"])
    leg("error-is-printed-minus-true",
        abs(r["error_pp"] - 100 * (r["premium_printed"] - r["premium_true"])) < 1e-9)
    leg("error-is-this-sessions-nav-move", r["identity_residual_pp"] is not None and
        abs(r["identity_residual_pp"]) <= IDENTITY_TOL_PP, r["identity_residual_pp"])
    leg("error-is-small-here", abs(r["error_pp"]) < 1.0, r["error_pp"])

    # 3. a flat NAV means the stale denominator is harmless, and says so
    flat = [p("2026-11-25", "2026-11-24", 2.00, 2.00, 0.0),
            p("2026-11-26", "2026-11-25", 2.00, 2.00, 0.0),
            p("2026-11-27", "2026-11-26", 2.10, 2.00, 0.05)]
    rows_flat, _, _, _tapf, _evf = measure_prints(flat, idx, "t")
    leg("flat-nav-no-error", all(abs(x["error_pp"]) < 1e-9 for x in rows_flat),
        [x["error_pp"] for x in rows_flat])

    # 4. negative control: a same-day print is never measured as lagging
    same = [p("2026-11-27", "2026-11-27", 2.0, 1.9, 0.05)]
    rows_same, un_same, sd_same, _taps, _evs = measure_prints(same, idx, "t")
    leg("same-day-not-measured", rows_same == [] and un_same == 0 and sd_same == 1)

    # 5. a missing session NAV stays unmeasured, never a zero error
    orphan = [p("2026-11-27", "2026-11-26", 2.0, 1.9, 0.05)]
    face_z = build([], idx, orphan)
    leg("unmeasured-not-zero", face_z["summary"]["n_measured"] == 0 and
        face_z["summary"]["n_unmeasured"] == 1)
    leg("unmeasured-verdict", face_z["verdict"] == "NOTHING_TO_MEASURE_YET")
    leg("unmeasured-statement-says-so", "unmeasured" in (face_z["statement"] or ""))

    # 6. the level must come from a print made after the session it prices
    tape = level_tape([p("2026-11-26", "2026-11-26", 1.0, 1.0, 0.0)])
    leg("no-self-recovery", "2026-11-26" not in tape)

    # 7. the band check counts a miss, so a broken band cannot pass silently
    levels = {"2026-11-17": 1.000, "2026-11-18": 1.020, "2026-11-19": 1.000,
              "2026-11-20": 1.030, "2026-11-23": 1.010, "2026-11-24": 1.040,
              "2026-11-25": 1.020, "2026-11-26": 1.030}
    k_tapes = {"K": {d: {"nav": v, "from_session": "2026-11-30", "revisions": 0}
                     for d, v in levels.items()}}
    tape_rows = [{"source": "t", "code": "K", "session": "2026-11-26",
                  "nav_session_printed": "2026-11-25", "nav_true": 1.030,
                  "premium_printed": 0.010, "premium_true": 0.0095}]
    bc_in = band_check(tape_rows, k_tapes)
    leg("band-counts-inside", bc_in["inside"] >= 1 and bc_in["outside"] == 0, bc_in)
    bad = [dict(x) for x in tape_rows]
    bad[-1]["premium_true"] = 0.90
    leg("band-counts-outside", band_check(bad, k_tapes)["outside"] == 1)
    leg("band-no-history-is-not-a-pass",
        band_check(tape_rows, {"K": {"2026-11-26": {"nav": 1.0,
                                                    "from_session": "x",
                                                    "revisions": 0}}})["n"] == 0)

    # 8. verdict words follow the numbers, both ways
    leg("verdict-nothing", verdict_for({"n_measured": 0}) == "NOTHING_TO_MEASURE_YET")
    leg("verdict-big-clean",
        verdict_for({"n_measured": 9, "median_abs_error_pp": 3.0,
                     "identity_max_residual_pp": 1e-12}) ==
        "A_STALE_DENOMINATOR_MOVES_THE_PREMIUM_BY_ONE_WHOLE_NAV_DAY")
    leg("verdict-big-dirty",
        verdict_for({"n_measured": 9, "median_abs_error_pp": 3.0,
                     "identity_max_residual_pp": 5.0}) ==
        "STALE_DENOMINATOR_MISSTATES_THE_PREMIUM_BY_MORE_THAN_A_POINT")
    leg("verdict-small-clean",
        verdict_for({"n_measured": 9, "median_abs_error_pp": 0.2,
                     "identity_max_residual_pp": 1e-12}) ==
        "THE_DISPLACEMENT_IS_THE_NAV_DAY_AND_IT_IS_SMALL_ON_MEDIAN")

    # 8b. two legs printing the same day must never share a denominator
    mixed = [{"code": "A", "name": "A", "session": "2026-11-25",
              "nav_session": "2026-11-24", "close": 1.00, "nav": 1.00, "premium": 0.0},
             {"code": "B", "name": "B", "session": "2026-11-25",
              "nav_session": "2026-11-24", "close": 100.0, "nav": 100.0, "premium": 0.0},
             {"code": "A", "name": "A", "session": "2026-11-26",
              "nav_session": "2026-11-25", "close": 1.00, "nav": 1.00, "premium": 0.0},
             {"code": "B", "name": "B", "session": "2026-11-26",
              "nav_session": "2026-11-25", "close": 101.0, "nav": 100.0, "premium": 0.01}]
    rows_mixed, _, _, _tapesm, _evm = measure_prints(mixed, idx, "t")
    leg("tapes-are-per-leg", all(abs(x["error_pp"]) < 1e-6 for x in rows_mixed),
        [x["error_pp"] for x in rows_mixed])

    # 8c. a share conversion must not be reported as a premium move
    split = [p("2026-11-25", "2026-11-24", 1.857, 1.857, 0.0),
             p("2026-11-26", "2026-11-25", 1.857, 0.9281, 1.0009),
             p("2026-11-27", "2026-11-26", 1.860, 1.860, 0.0)]
    rows_split, _un_sp, _sd_sp, _tp_sp, ev_sp = measure_prints(split, idx, "t")
    leg("split-excluded-not-measured", ev_sp >= 1 and
        all(abs(x["error_pp"]) < 100 for x in rows_split),
        (ev_sp, [x["error_pp"] for x in rows_split]))

    # 9. end-to-end on the T+1 series: numbers, statement and rows agree
    face = build([], idx, prints)
    leg("e2e-measured-three", face["summary"]["n_measured"] == 3,
        face["summary"]["n_measured"])
    leg("e2e-identity-clean",
        (face["summary"]["identity_max_residual_pp"] or 1) <= IDENTITY_TOL_PP,
        face["summary"]["identity_max_residual_pp"])
    leg("e2e-statement-names-worst", face["summary"]["worst"]["session"] in
        (face["statement"] or ""))

    for f in fails:
        print("FAIL " + f)
    print("%d legs, %d failed" % (legs, len(fails)))
    return 0 if not fails else 3


# ------------------------------------------------------------------------ run
def run():
    import datetime
    snaps = L.load_snaps(SNAP_DIR)
    hist = load_history(HIST_PATH)
    if not hist and not snaps:
        print("STALE: neither %s nor the snapshot series is readable" % HIST_PATH)
        return 3
    face = build(_snapshot_prints(snaps), L.index_of(L.load_calendar()), hist)
    face["generated"] = datetime.datetime.now().astimezone().strftime(
        "%Y-%m-%dT%H:%M:%S%z")
    write_faces(face)
    s = face["summary"]
    print("verdict=%s cutoff=%s measured=%d unmeasured=%d median_abs=%.2fpp "
          "residual=%.1e written %s"
          % (face["verdict"], face["evidence_cutoff"], s["n_measured"],
             s["n_unmeasured"], s["median_abs_error_pp"] or 0.0,
             s["identity_max_residual_pp"] or 0.0,
             os.path.relpath(OUT_JSON, ROOT)))
    print(face["statement"])
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", nargs="?", default="run", choices=["run", "check", "selftest"])
    args = ap.parse_args(argv)
    if args.cmd == "check":
        return run_check()
    if args.cmd == "selftest":
        return selftest()
    return run()


if __name__ == "__main__":
    sys.exit(main())
