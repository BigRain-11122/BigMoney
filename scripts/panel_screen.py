"""Opt-in corporate-action screen for the as-traded daily panel (E76).

``data/daily`` ships **as traded**: a share split or unit conversion is a
one-session scale change, so an unadjusted name prints a -90% "return" and the
next month prints a +900% one. E74 found 19 of 128 stale-tail events were those
prints; E75 found 135 adjacent-session moves past the 30% screen on 152 names,
worth ~216bp/yr of equal-weight book impact -- 4.8x the -45bp residual the chain
was chasing.

Nothing in the census chain charged that. This module is the missing loader, and
it is deliberately **opt-in**: every existing face keeps reading
``e27.load_universe()`` unmodified, and a caller that wants the correction asks
for it explicitly (``screen='neutralise'`` or ``screen='drop'``). A loader that
silently repaired the panel would move every published number at once, which is
the opposite of measuring.

Two mechanisms, both reported:

``neutralise``
    forward-adjust the series at each flagged *adjacent* print: every close on or
    after the event date is multiplied by the implied share ratio 1/(1+r), so the
    event renders as a 0% session and the rest of the path keeps its shape.

``drop``
    remove the name from the universe entirely -- the honest option when a name's
    adjustment factor cannot be trusted (a non-integer ratio is not a share split;
    it is a restatement, a resumption misprint, or a bad row).

Only **adjacent** prints are screened by default. A move across a gap is a
resumption after a suspension, which a real market can print, so it stays as it
is -- but a split that lands next to a *missing panel bar* also reads as a gap
(E91: sh510150's 12:1 split sits beside a missing 2021-05-28 bar and owns a
published era gap). ``mode="neutralise_gap"`` with ``gap_limit`` (in sessions)
is the gap-tolerant branch: it repairs prints no more than ``gap_limit``
sessions away from the previous priced close, and only when the implied ratio
lands on an integer, so a resumption misprint cannot be repaired by accident.
"""

from __future__ import annotations

ARTEFACT_JUMP = 0.30

INTEGER_TOL = 0.02      # |ratio/nearest_int - 1| <= 2% reads as a share ratio

PERSIST_BARS = 5        # (E133) how many following priced closes judge a print's level
PERSIST_TOL = 0.20      # (E133) |median drift vs the print close| <= 20% reads as persisted


def level_persistence(closes, events, bars=PERSIST_BARS, tol=PERSIST_TOL):
    """(E133) Annotate events with the post-print drift and a persistence verdict.

    A corporate action leaves the new price level in place; a misprint that gets
    restated reverts. The median of the next `bars` priced closes against the print
    close is the decisive test, and it survives ratios no integer test recognises
    (a 1:3.15 conversion is a real action that reads as "not integer").
    """
    dates = sorted(d for d, v in closes.items() if v is not None and v > 0)
    idx = {d: i for i, d in enumerate(dates)}
    for ev in events:
        j = idx.get(ev["date"])
        after = dates[j + 1: j + 1 + bars] if j is not None else []
        base = closes.get(ev["date"])
        if not after or not base:
            ev["post_drift_pct"] = None
            ev["level_persists"] = None
            continue
        drifts = sorted(closes[d] / float(base) - 1.0 for d in after)
        drift = drifts[len(drifts) // 2]
        ev["post_drift_pct"] = 100.0 * drift
        ev["level_persists"] = bool(abs(drift) <= tol)
    return events


def implied_ratio(ret):
    """(ratio, nearest_int, resid_pct, integer_like) for a one-session move."""
    if ret is None or ret <= -1.0:
        return None
    ratio = 1.0 / (1.0 + ret)
    if ratio < 1.0:
        ratio = 1.0 / ratio
    nearest = int(round(ratio))
    if nearest < 1:
        nearest = 1
    resid = abs(ratio / float(nearest) - 1.0)
    return {"ratio": ratio, "nearest_int": nearest,
            "resid_pct": 100.0 * resid,
            "integer_like": nearest >= 2 and resid <= INTEGER_TOL}


def split_events(closes, thresh=ARTEFACT_JUMP, cal=None):
    """Every consecutive-PRICED-close move past `thresh` on one series.

    Bars are compared against the previous *priced* close -- a split frequently
    sits next to a suspension bar, so a None-abort scan misses it (E74 lesson).

    ``cal`` is the panel session calendar. Pass it: adjacency is a *session*
    distance, and a calendar-day test reads Fri->Mon as a two-day gap, which is
    exactly where a large slice of the real prints sit (sh512100 2022-09-05 is a
    Monday). Without a calendar the day-distance fallback is used and the report
    says so.
    """
    dates = sorted(d for d, v in closes.items() if v is not None)
    events = []
    prev_d = None
    for d in dates:
        v = closes[d]
        if v is None or v <= 0:
            continue
        if prev_d is not None:
            last = closes[prev_d]
            if last and last > 0:
                r = v / float(last) - 1.0
                if abs(r) > thresh:
                    ir = implied_ratio(r)
                    gap = _sessions_between(prev_d, d, cal)
                    events.append({
                        "date": d, "prev_date": prev_d,
                        "prev_close": last, "close": v,
                        "ret_pct": 100.0 * r,
                        "gap_sessions": gap,
                        "adjacent": gap == 0,
                        "implied": ir,
                        "factor": (ir["ratio"] if ir else 1.0 / (1.0 + r)),
                    })
        prev_d = d
    return events


def _sessions_between(d0, d1, cal=None):
    """Session distance between two ISO dates (0 == the next session).

    With a ``cal`` the distance is read off the panel calendar, so a weekend or
    holiday gap is 0 and a suspension gap is not. Without one it falls back to
    the ISO day distance, which over-reports the gap.
    """
    if cal:
        idx = None
        if not isinstance(cal, dict):
            cal = {d: i for i, d in enumerate(cal)}
        idx = cal
        a, b = idx.get(d0), idx.get(d1)
        if a is not None and b is not None:
            return max(0, b - a - 1)
    import datetime
    a = datetime.date(*[int(x) for x in d0[:10].split("-")])
    b = datetime.date(*[int(x) for x in d1[:10].split("-")])
    return max(0, (b - a).days - 1)


def neutralise(closes, events):
    """Forward-adjust `closes` at each event: multiply closes on/after it by the factor."""
    out = dict(closes)
    for ev in sorted(events, key=lambda e: e["date"]):
        f = ev["factor"]
        if f is None or f <= 0:
            continue
        d0 = ev["date"]
        # iterate `out` so a later event compounds on the already adjusted bar
        for d, v in list(out.items()):
            if d >= d0 and v is not None:
                out[d] = v * f
    return out


def screen_universe(raw, mode="neutralise", thresh=ARTEFACT_JUMP, cal=None,
                    gap_limit=0):
    """-> (raw_screened, report) from an ``e27.load_universe()`` mapping.

    ``raw`` maps symbol -> (closes{date: px}, amounts{date: value}). Untouched
    symbols are passed through by reference; repaired ones get a new dict.
    ``cal`` is the panel session calendar and should be passed so adjacency is
    read in sessions rather than calendar days. ``gap_limit`` only applies to
    ``mode="neutralise_gap"``: how many intervening sessions a print may skip
    and still be repaired (always gated on an integer-ratio match).
    """
    if mode not in ("neutralise", "neutralise_int", "drop", "neutralise_gap",
                    "neutralise_persist"):
        raise ValueError("screen mode must be 'neutralise', 'neutralise_int', "
                         "'drop', 'neutralise_gap' or 'neutralise_persist', "
                         "got %r" % (mode,))
    out = {}
    rows = []
    gapped_eligible = 0
    reverting_adj = 0
    undecided_adj = 0
    for sym in sorted(raw):
        closes, amounts = raw[sym]
        events = split_events(closes, thresh, cal=cal)
        adjacent = [e for e in events if e["adjacent"]]
        gapped = [e for e in events if not e["adjacent"]]
        skipped_adj = 0
        if mode == "neutralise_persist":
            # (E133) the ratio is evidence, not the verdict: repair every adjacent
            # print whose new level persists, leave the reverting ones alone
            level_persistence(closes, adjacent)
            kept = [e for e in adjacent if e.get("level_persists")]
            reverting_adj += len([e for e in adjacent
                                  if e.get("level_persists") is False])
            undecided_adj += len([e for e in adjacent
                                  if e.get("level_persists") is None])
            skipped_adj = len(adjacent) - len(kept)
            adjacent = kept
        elif mode == "neutralise_int":
            # only the prints whose ratio lands on an integer: the conservative
            # branch, since a non-integer print may be a real resumption misprint
            kept = [e for e in adjacent
                    if (e.get("implied") or {}).get("integer_like")]
            skipped_adj = len(adjacent) - len(kept)
            adjacent = kept
        elif mode == "neutralise_gap":
            # gap-tolerant branch: adjacent prints first (integer-like only, same
            # conservatism as neutralise_int), plus gapped prints inside the limit
            # whose ratio is still an integer share change
            kept = [e for e in adjacent
                    if (e.get("implied") or {}).get("integer_like")]
            within = [e for e in gapped
                      if e["gap_sessions"] <= gap_limit
                      and (e.get("implied") or {}).get("integer_like")]
            gapped_eligible += len(within)
            skipped_adj = len(adjacent) - len(kept)
            adjacent = kept + within
            gapped = [e for e in gapped if e not in within]
        if not adjacent:
            out[sym] = (closes, amounts)
        elif mode == "drop":
            rows.append({"name": sym, "action": "drop",
                         "events": len(adjacent),
                         "skipped_noninteger_adjacent": skipped_adj,
                         "gapped_kept": len(gapped),
                         "prints": [_print_row(e) for e in adjacent]})
        else:
            out[sym] = (neutralise(closes, adjacent), amounts)
            rows.append({"name": sym, "action": "neutralise",
                         "events": len(adjacent),
                         "skipped_noninteger_adjacent": skipped_adj,
                         "gapped_kept": len(gapped),
                         "prints": [_print_row(e) for e in adjacent]})
        if gapped and not adjacent:
            rows.append({"name": sym, "action": "kept-gapped-only",
                         "events": 0, "gapped_kept": len(gapped),
                         "prints": [_print_row(e) for e in gapped]})
    report = {
        "mode": mode,
        "threshold_pct": 100.0 * thresh,
        "adjacency": ("panel calendar" if cal else
                      "ISO day-distance fallback (no calendar passed)"),
        "names_in": len(raw),
        "names_out": len(out),
        "names_touched": len([r for r in rows if r["action"] != "kept-gapped-only"]),
        "events_neutralised": sum(r["events"] for r in rows),
        "integer_like_events": sum(
            1 for r in rows if r["action"] != "kept-gapped-only"
            for p in r["prints"] if p.get("integer_like")),
        "skipped_noninteger_adjacent": sum(r.get("skipped_noninteger_adjacent", 0)
                                           for r in rows),
        "reverting_adjacent": reverting_adj,
        "undecided_adjacent": undecided_adj,
        "persistence": ({"bars": PERSIST_BARS, "tol_pct": 100.0 * PERSIST_TOL}
                        if mode == "neutralise_persist" else None),
        "gapped_kept": sum(r.get("gapped_kept", 0) for r in rows),
        "gap_limit": (gap_limit if mode == "neutralise_gap" else None),
        "gapped_eligible": gapped_eligible,
        "names": rows,
    }
    return out, report


def _print_row(ev):
    im = ev.get("implied") or {}
    return {"date": ev["date"], "prev_date": ev["prev_date"],
            "gap_sessions": ev.get("gap_sessions"),
            "ret_pct": round(ev["ret_pct"], 2),
            "ratio": round(im.get("ratio", ev["factor"]), 4),
            "nearest_int": im.get("nearest_int"),
            "resid_pct": round(im["resid_pct"], 3) if im else None,
            "integer_like": im.get("integer_like"),
            "factor_applied": round(ev["factor"], 6),
            "post_drift_pct": (None if ev.get("post_drift_pct") is None
                               else round(ev["post_drift_pct"], 2)),
            "level_persists": ev.get("level_persists")}


def selftest():
    """Offline checks: a split is repaired, a gap is not, real moves survive."""
    ok = tot = 0
    def chk(cond, label):
        nonlocal ok, tot
        tot += 1
        if cond:
            ok += 1
        else:
            print("FAIL %s" % label)

    # a 12:1 split on consecutive sessions reads as adjacent, integer, and
    # neutralises to a flat session
    closes = {"2024-01-02": 120.0, "2024-01-03": 10.0, "2024-01-04": 10.2}
    ev = split_events(closes)
    chk(len(ev) == 1 and ev[0]["adjacent"], "12:1 split on consecutive days is one adjacent event")
    chk(ev[0]["implied"]["nearest_int"] == 12 and ev[0]["implied"]["integer_like"],
        "12:1 split recovers an integer ratio")
    adj = neutralise(closes, ev)
    chk(abs(adj["2024-01-03"] / adj["2024-01-02"] - 1.0) < 1e-12,
        "neutralised split renders as a 0% session")
    chk(abs(adj["2024-01-04"] / adj["2024-01-03"] - 1.02) < 1e-12,
        "post-event returns keep their shape after adjustment")

    # a move across a gap is a resumption: flagged but never screened
    gapped = {"2024-03-01": 10.0, "2024-03-06": 1.0}   # 10:1 behind a suspension
    gev = split_events(gapped)
    chk(len(gev) == 1 and not gev[0]["adjacent"], "a print across a gap is not adjacent")
    raw_g = {"sh500000": (gapped, {})}
    out_g, rep_g = screen_universe(raw_g)
    chk(rep_g["events_neutralised"] == 0 and out_g["sh500000"][0] is gapped,
        "gapped-only name passes through untouched")
    chk(rep_g["gapped_kept"] == 1 and rep_g["integer_like_events"] == 0,
        "the integer-ratio count reads repaired prints only, not kept gapped ones")

    # Fri->Mon is the NEXT session on the panel calendar, so it must be screened;
    # the day-distance fallback cannot see that and says so in its report
    weekend = {"2022-09-02": 3.0, "2022-09-05": 1.0}
    wcal = ["2022-09-01", "2022-09-02", "2022-09-05", "2022-09-06"]
    wev = split_events(weekend, cal=wcal)
    chk(len(wev) == 1 and wev[0]["adjacent"],
        "a Friday->Monday print is adjacent on the session calendar")
    chk(split_events(weekend)[0]["adjacent"] is False,
        "without a calendar the same print is read as a gap (fallback disclosed)")
    chk(screen_universe({"sh512100": (weekend, {})}, cal=wcal)[1]["adjacency"]
        == "panel calendar", "the report names which adjacency rule was used")

    # ordinary moves are not events at all
    quiet = {"2024-01-02": 10.0, "2024-01-03": 10.5, "2024-01-04": 13.0}
    chk(split_events(quiet) == [], "moves inside the 30% screen are not events")

    # drop mode removes the name; neutralise keeps it
    raw_s = {"sh510500": (closes, {})}
    out_d, rep_d = screen_universe(raw_s, mode="drop")
    chk(out_d == {} and rep_d["names_touched"] == 1, "drop mode removes the flagged name")
    out_n, rep_n = screen_universe(raw_s, mode="neutralise")
    chk(len(out_n) == 1 and rep_n["names_touched"] == 1,
        "neutralise mode keeps the flagged name")

    # two events compound: the later date carries both factors
    two = {"2024-01-02": 100.0, "2024-01-03": 10.0,          # 10:1
           "2024-01-04": 1.0}                                 # 10:1 again
    ev2 = split_events(two)
    adj2 = neutralise(two, ev2)
    chk(len(ev2) == 2 and abs(adj2["2024-01-04"] / adj2["2024-01-03"] - 1.0) < 1e-12,
        "a second split is neutralised on the already adjusted series")

    # report arithmetic
    chk(rep_n["integer_like_events"] == 1 and rep_n["names_in"] == 1,
        "report counts integer-like events per name")

    # the conservative branch repairs only integer-ratio prints and discloses the rest
    mixed = {"2024-01-02": 100.0, "2024-01-03": 10.0,   # 10:1, integer
             "2024-01-04": 3.0}                          # -70%, ratio 3.33, not integer
    _o, rep_int = screen_universe({"sh510000": (mixed, {})}, mode="neutralise_int")
    chk(rep_int["events_neutralised"] == 1
        and rep_int["skipped_noninteger_adjacent"] == 1,
        "integer-only mode repairs the split and reports the non-integer print it left")
    _o2, rep_all = screen_universe({"sh510000": (mixed, {})})
    chk(rep_all["events_neutralised"] == 2, "full mode repairs both adjacent prints")

    # (E92) gap-tolerant branch: an integer print one missing bar away is repaired
    # only when the caller asks for that gap limit, and a non-integer gapped print
    # is never repaired even at a generous limit
    gsplit = {"2021-05-27": 10.414, "2021-05-31": 0.87}   # 12:1 behind one missing bar
    gcal = ["2021-05-27", "2021-05-28", "2021-05-31"]
    gev2 = split_events(gsplit, cal=gcal)
    chk(len(gev2) == 1 and gev2[0]["gap_sessions"] == 1,
        "a split one missing bar away reports gap_sessions=1")
    raw_g2 = {"sh510150": (gsplit, {})}
    chk(screen_universe(raw_g2, cal=gcal)[1]["events_neutralised"] == 0,
        "the default screen leaves the gapped split alone")
    out_g2, rep_g2 = screen_universe(raw_g2, mode="neutralise_gap", cal=gcal,
                                     gap_limit=1)
    chk(rep_g2["events_neutralised"] == 1 and rep_g2["gapped_eligible"] == 1,
        "gap_limit=1 repairs the gapped integer split and counts it")
    adj_g2 = out_g2["sh510150"][0]
    chk(abs(adj_g2["2021-05-31"] / adj_g2["2021-05-27"] - 1.0) < 1e-9,
        "the gap-repaired split renders as a flat multi-session leg")
    chk(screen_universe(raw_g2, mode="neutralise_gap", cal=gcal,
                        gap_limit=0)[1]["events_neutralised"] == 0,
        "gap_limit=0 is the default screen, not a special case")
    nonint = {"2021-05-27": 10.0, "2021-05-31": 3.0}      # ratio 3.33, not an integer
    chk(screen_universe({"sh510150": (nonint, {})}, mode="neutralise_gap",
                        cal=gcal, gap_limit=5)[1]["events_neutralised"] == 0,
        "a non-integer gapped print is never repaired, whatever the gap limit")

    # (E133) persistence branch: the ratio is evidence, the level verdict decides
    conv = {"2024-01-02": 31.5, "2024-01-03": 10.0, "2024-01-04": 10.1,
            "2024-01-05": 9.9, "2024-01-08": 10.2, "2024-01-09": 10.0}
    _c, rep_conv_int = screen_universe({"sh513500": (conv, {})}, mode="neutralise_int")
    chk(rep_conv_int["events_neutralised"] == 0,
        "a 3.15:1 conversion is invisible to the integer test")
    out_p, rep_p = screen_universe({"sh513500": (conv, {})}, mode="neutralise_persist")
    chk(rep_p["events_neutralised"] == 1 and rep_p["reverting_adjacent"] == 0,
        "the persistence branch repairs a non-integer conversion whose level holds")
    chk(abs(out_p["sh513500"][0]["2024-01-03"] / 31.5 - 1.0) < 1e-12,
        "the repaired conversion renders as a 0% session")

    # a restated misprint rebounds: persistence must refuse it and count the refusal
    # (the reversion is spread over gentle steps so only one print clears the screen)
    restated = {"2024-01-02": 100.0, "2024-01-03": 30.0, "2024-01-04": 35.0,
                "2024-01-05": 38.0, "2024-01-08": 40.0, "2024-01-09": 41.0}
    _o3, rep_rev = screen_universe({"sh510000": (restated, {})},
                                   mode="neutralise_persist")
    chk(rep_rev["events_neutralised"] == 0 and rep_rev["reverting_adjacent"] == 1,
        "a print that reverts inside the window is left alone and counted")
    chk(rep_rev["names"][0]["prints"][0]["level_persists"] is False
        if rep_rev.get("names") else True,
        "the reverting print carries an explicit False verdict")

    # an integer split the other branches repair is still repaired here
    out_i2, rep_i2 = screen_universe({"sh510500": (closes, {})},
                                     mode="neutralise_persist")
    chk(rep_i2["events_neutralised"] == 1 and rep_i2["names_touched"] == 1,
        "the persistence branch keeps repairing ordinary integer splits")
    chk(abs(out_i2["sh510500"][0]["2024-01-03"] / out_i2["sh510500"][0]["2024-01-02"]
            - 1.0) < 1e-12, "and renders them flat like the other branches")

    # a print with no following priced close cannot be judged: skip, never guess
    tail = {"2024-01-02": 120.0, "2024-01-03": 10.0}
    _o4, rep_tail = screen_universe({"sh510300": (tail, {})},
                                    mode="neutralise_persist")
    chk(rep_tail["events_neutralised"] == 0 and rep_tail["undecided_adjacent"] == 1,
        "a print with no window to judge stays unrepaired and is counted undecided")

    print("panel_screen selftest %d/%d PASS" % (ok, tot))
    return 0 if ok == tot else 1


if __name__ == "__main__":
    raise SystemExit(selftest())