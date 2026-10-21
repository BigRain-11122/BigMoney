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

Only **adjacent** prints are screened. A move across a gap is a resumption after
a suspension, which a real market can print, so it stays as it is.
"""

from __future__ import annotations

ARTEFACT_JUMP = 0.30

INTEGER_TOL = 0.02      # |ratio/nearest_int - 1| <= 2% reads as a share ratio


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
                    events.append({
                        "date": d, "prev_date": prev_d,
                        "prev_close": last, "close": v,
                        "ret_pct": 100.0 * r,
                        "adjacent": _sessions_between(prev_d, d, cal) == 0,
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


def screen_universe(raw, mode="neutralise", thresh=ARTEFACT_JUMP, cal=None):
    """-> (raw_screened, report) from an ``e27.load_universe()`` mapping.

    ``raw`` maps symbol -> (closes{date: px}, amounts{date: value}). Untouched
    symbols are passed through by reference; repaired ones get a new dict.
    ``cal`` is the panel session calendar and should be passed so adjacency is
    read in sessions rather than calendar days.
    """
    if mode not in ("neutralise", "neutralise_int", "drop"):
        raise ValueError("screen mode must be 'neutralise', 'neutralise_int' or "
                         "'drop', got %r" % (mode,))
    out = {}
    rows = []
    for sym in sorted(raw):
        closes, amounts = raw[sym]
        events = split_events(closes, thresh, cal=cal)
        adjacent = [e for e in events if e["adjacent"]]
        gapped = [e for e in events if not e["adjacent"]]
        skipped_adj = 0
        if mode == "neutralise_int":
            # only the prints whose ratio lands on an integer: the conservative
            # branch, since a non-integer print may be a real resumption misprint
            kept = [e for e in adjacent
                    if (e.get("implied") or {}).get("integer_like")]
            skipped_adj = len(adjacent) - len(kept)
            adjacent = kept
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
        "gapped_kept": sum(r.get("gapped_kept", 0) for r in rows),
        "names": rows,
    }
    return out, report


def _print_row(ev):
    im = ev.get("implied") or {}
    return {"date": ev["date"], "prev_date": ev["prev_date"],
            "ret_pct": round(ev["ret_pct"], 2),
            "ratio": round(im.get("ratio", ev["factor"]), 4),
            "nearest_int": im.get("nearest_int"),
            "resid_pct": round(im["resid_pct"], 3) if im else None,
            "integer_like": im.get("integer_like"),
            "factor_applied": round(ev["factor"], 6)}


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

    print("panel_screen selftest %d/%d PASS" % (ok, tot))
    return 0 if ok == tot else 1


if __name__ == "__main__":
    raise SystemExit(selftest())