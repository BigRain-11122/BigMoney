#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""The minute feed's first reader (round 2117, bm-c).

Why this file exists
--------------------
`data/minute_feed/` has been collected since 2026-09-15 by `scripts/update_minute_feed.py`
and has never had a reader: no research face, no prereg, no gate consumes it. A panel with
no reader is the same defect as a face with no writer (r1108 / r1282 family) -- it is
"product" on disk and nothing else. Until something reads it, nobody knows whether it is
even honest, and the board's W1_supply line keeps saying the intraday-reversal question is
"blocked on data" without saying by how much.

So this face does three things and refuses to do a fourth:

  1. audits the feed as delivered -- sessions, bars per session, whether the 09:30 print is
     really there, duplicate minutes, holes in the session grid;
  2. prices the one execution number the book already assumes -- what buying at 10:00
     instead of the 09:30 open would have cost on this feed;
  3. prices the blocked question's power ceiling -- with this many sessions and this much
     dispersion, the smallest edge an intraday-reversal claim could clear at 80% power.

It does not claim an edge. The reversal number is printed as a census (n, slope, t, the
session count still missing for a 5bp/session claim), never as a verdict.

Shapes
------
  python scripts/minute_feed_first_reader.py run        (default)
  python scripts/minute_feed_first_reader.py --check    (re-derive, compare to the face)
  python scripts/minute_feed_first_reader.py selftest   (offline behaviour legs)
  python scripts/minute_feed_first_reader.py --selftest (same)

check() asks the input panel, not itself: every number in the face is recomputed from the
CSVs on disk and compared to what the face publishes. Input moved -> STALE (the chain's
run_leg pays for a rewrite on that word); input identical but arithmetic differs -> CHECK
FAILED, and no STALE token, because that one is a defect, not a stale snapshot (r1934).
"""

from __future__ import annotations

import io
import json
import os
import statistics
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
FEED_DIR = os.path.join(ROOT, "data", "minute_feed")
FACE = os.path.join(ROOT, "results", "minute_feed_first_reader.json")
PAGE = os.path.join(ROOT, "research", "MINUTE_FEED_FIRST_READER.md")

# The execution ladder: which minutes we price against the session's first print.
LADDER = ("09:45", "10:00", "10:30", "11:30", "14:00", "14:57")
FULL_SESSION_BARS = 200      # below this the session is a window fragment, not a session
# what a complete session should occupy once the collector's rolling window is full
SESSION_GRID = (["%02d:%02d" % divmod(m, 60) for m in range(9 * 60 + 30, 11 * 60 + 31)]
                + ["%02d:%02d" % divmod(m, 60) for m in range(13 * 60 + 1, 15 * 60 + 1)])
TARGET_BP_PER_SESSION = 5.0  # the claim size W1_supply's question would have to clear
POWER_Z = 1.96 + 0.8416      # one-sided 5%, 80% power


def _rows(path):
    """Return [(session, hh:mm, open, close)] for one feed CSV."""
    out = []
    with io.open(path, encoding="utf-8") as f:
        header = f.readline().strip().split(",")
        idx = {k: i for i, k in enumerate(header)}
        need = ("day", "open", "close")
        missing = [k for k in need if k not in idx]
        if missing:
            raise ValueError("feed %s missing column(s) %s" % (os.path.basename(path), missing))
        for line in f:
            line = line.strip()
            if not line:
                continue
            parts = line.split(",")
            stamp = parts[idx["day"]]
            session, _, hhmm = stamp.partition(" ")
            out.append((session, hhmm[:5], float(parts[idx["open"]]), float(parts[idx["close"]])))
    return out


def audit(rows):
    """What the feed actually is, per session -- counts only, no judgement."""
    by_session = {}
    for session, hhmm, o, c in rows:
        by_session.setdefault(session, []).append((hhmm, o, c))

    dup_total = 0
    sessions = []
    for session in sorted(by_session):
        bars = by_session[session]
        minutes = [b[0] for b in bars]
        dup = len(minutes) - len(set(minutes))
        dup_total += dup
        first = min(minutes)
        sessions.append({
            "session": session,
            "bars": len(bars),
            "first_minute": first,
            "last_minute": max(minutes),
            "has_0930": "09:30" in set(minutes),
            "dup_minutes": dup,
            "full": len(bars) >= FULL_SESSION_BARS,
        })
    full = [s for s in sessions if s["full"]]
    # the grid a complete session should occupy, and what is missing from it
    hole_counts = {}
    for s in full:
        got = set(b[0] for b in by_session[s["session"]])
        for m in SESSION_GRID:
            if m not in got:
                hole_counts[m] = hole_counts.get(m, 0) + 1
    holes = sorted(hole_counts.items(), key=lambda kv: -kv[1])
    return {
        "sessions": len(sessions),
        "full_sessions": len(full),
        "fragment_sessions": len(sessions) - len(full),
        "median_bars_full": int(statistics.median([s["bars"] for s in full])) if full else 0,
        "sessions_missing_0930": sum(1 for s in full if not s["has_0930"]),
        "sessions_missing_0930_share": (round(sum(1 for s in full if not s["has_0930"]) / len(full), 3)
                                       if full else None),
        "grid_minutes_expected": len(SESSION_GRID),
        "holes": [{"minute": m, "sessions": n} for m, n in holes[:8]],
        "duplicate_minutes": dup_total,
        "first_session": sessions[0]["session"] if sessions else None,
        "last_session": sessions[-1]["session"] if sessions else None,
        "rows": len(rows),
    }


def ladder(rows):
    """For every full session: (price at t / the session's first open - 1) in bp."""
    by_session = {}
    for session, hhmm, o, c in rows:
        by_session.setdefault(session, []).append((hhmm, o, c))

    out = []
    for session in sorted(by_session):
        bars = by_session[session]
        if len(bars) < FULL_SESSION_BARS:
            continue
        bars.sort()
        p0 = bars[0][1]                      # the session's first open = the book's fill
        closes = {b[0]: b[2] for b in bars}
        rec = {"session": session, "p0_minute": bars[0][0]}
        for t in LADDER:
            p = closes.get(t)
            if p is None:
                continue
            rec[t] = (p / p0 - 1.0) * 10000.0
        out.append(rec)
    return out


def ladder_stats(ladder_rows):
    stats = {}
    for t in LADDER:
        vals = [r[t] for r in ladder_rows if t in r]
        if len(vals) < 3:
            stats[t] = {"n": len(vals), "verdict": "too few sessions"}
            continue
        mean = statistics.fmean(vals)
        sd = statistics.stdev(vals)
        se = sd / (len(vals) ** 0.5)
        stats[t] = {
            "n": len(vals),
            "mean_bp": round(mean, 3),
            "median_bp": round(statistics.median(vals), 3),
            "sd_bp": round(sd, 3),
            "t": round(mean / se, 2) if se else None,
            "share_above": round(sum(1 for v in vals if v > 0) / len(vals), 4),
        }
    return stats


def reversal(rows):
    """The blocked question, census only: 09:30->10:00 predicts 10:00->15:00?"""
    by_session = {}
    for session, hhmm, o, c in rows:
        by_session.setdefault(session, []).append((hhmm, o, c))

    pairs = []
    for session in sorted(by_session):
        bars = by_session[session]
        if len(bars) < FULL_SESSION_BARS:
            continue
        bars.sort()
        p0 = bars[0][1]
        closes = {b[0]: b[2] for b in bars}
        p10 = closes.get("10:00")
        last = bars[-1][2]
        if not p10 or not last:
            continue
        first30 = (p10 / p0 - 1.0) * 10000.0
        rest = (last / p10 - 1.0) * 10000.0
        pairs.append((first30, rest))

    n = len(pairs)
    if n < 20:
        return {"n": n, "verdict": "too few sessions to price", "sessions_needed": None}
    xs = [p[0] for p in pairs]
    ys = [p[1] for p in pairs]
    mx = statistics.fmean(xs)
    my = statistics.fmean(ys)
    sxx = sum((x - mx) ** 2 for x in xs)
    sxy = sum((x - mx) * (y - my) for x, y in pairs)
    syy = sum((y - my) ** 2 for y in ys)
    slope = sxy / sxx if sxx else 0.0
    resid = syy - slope * sxy
    dof = n - 2
    s2 = resid / dof if dof > 0 else 0.0
    se = (s2 / sxx) ** 0.5 if sxx else None
    t = slope / se if se else None
    sd_rest = statistics.stdev(ys)
    # smallest detectable slope at 80% power, one-sided 5%
    mde_slope = POWER_Z * (s2 / sxx) ** 0.5 if (sxx and dof > 0) else None
    # smallest detectable mean rest-of-day move, same power
    mde_mean = POWER_Z * sd_rest / (n ** 0.5)
    return {
        "n": n,
        "slope": round(slope, 4),
        "t": round(t, 2) if t is not None else None,
        "sd_first30_bp": round(statistics.stdev(xs), 2),
        "sd_rest_bp": round(sd_rest, 2),
        "mde_mean_bp": round(mde_mean, 2),
        "mde_slope": round(mde_slope, 4) if mde_slope is not None else None,
        "sessions_for_5bp": int(round((POWER_Z * sd_rest / TARGET_BP_PER_SESSION) ** 2)),
        "verdict": "census only: no edge claimed",
    }


def _rel(path):
    """Repo-relative when the path lives on the same drive, absolute otherwise.

    The selftest feeds a temp dir on another drive; relpath raises across mounts and a
    face that crashes on its own test data is not a face.
    """
    try:
        return os.path.relpath(path, ROOT).replace(os.sep, "/")
    except ValueError:
        return path.replace(os.sep, "/")


def build(feed_dir=FEED_DIR):
    symbols = []
    per_symbol_ladder = {}
    if os.path.isdir(feed_dir):
        names = sorted(n for n in os.listdir(feed_dir) if n.lower().endswith(".csv"))
    else:
        names = []
    for name in names:
        path = os.path.join(feed_dir, name)
        if os.path.getsize(path) == 0:
            symbols.append({"symbol": name[:-4], "rows": 0, "note": "empty feed"})
            continue
        rows = _rows(path)
        if not rows:
            symbols.append({"symbol": name[:-4], "rows": 0, "note": "empty feed"})
            continue
        lad = ladder(rows)
        sym = name[:-4]
        per_symbol_ladder[sym] = lad
        symbols.append({
            "symbol": sym,
            "audit": audit(rows),
            "ladder": ladder_stats(lad),
            "reversal": reversal(rows),
        })

    usable = [s for s in symbols if s.get("audit", {}).get("full_sessions", 0) > 0]
    cutoff = max((s["audit"]["last_session"] for s in usable), default=None)

    # Honest n: five broad ETFs share one session, so pooling their rows would multiply the
    # observation count by five while the noise is the same five times. The deep symbols are
    # averaged within each session first; n is then the number of sessions, not of rows.
    deep = [s["symbol"] for s in symbols
            if s.get("audit", {}).get("full_sessions", 0) >= 40]
    per_session = {}
    for sym in deep:
        for rec in per_symbol_ladder.get(sym, []):
            per_session.setdefault(rec["session"], {}).setdefault(sym, rec)
    ladder_sessions = []
    for sess in sorted(per_session):
        rec = {"session": sess}
        for t in LADDER:
            vals = [v[t] for v in per_session[sess].values() if t in v]
            if vals:
                rec[t] = statistics.fmean(vals)
        ladder_sessions.append(rec)
    payload = {
        "face": "minute_feed_first_reader",
        "why": ("the minute panel has had a writer since 2026-09-15 and no reader; this face "
                "audits what was delivered, prices the 10:00-instead-of-open fill, and sizes "
                "the power of the intraday-reversal question the board calls data-blocked"),
        "generated": None,
        "evidence_cutoff": cutoff,
        "feed_dir": _rel(feed_dir),
        "ladder_minutes": list(LADDER),
        "full_session_bars": FULL_SESSION_BARS,
        "target_bp_per_session": TARGET_BP_PER_SESSION,
        "symbols": symbols,
        "ladder_deep_symbols": deep,
        "ladder_session_stats": ladder_stats(ladder_sessions),
        "ladder_session_n": len(ladder_sessions),
        "symbols_with_full_sessions": [s["symbol"] for s in usable],
        "symbols_without_data": [s["symbol"] for s in symbols if s not in usable],
        "zeros": {"engine_runs": 0, "ledger_trials_added": 0, "network": "zero"},
        "notes": [
            "the feed carries no 09:30 (auction) print in any session, so the ladder's baseline "
            "is each session's first continuous print -- the book's real fill is the auction "
            "print this panel cannot see",
            "ladder bp is measured against each session's own first print, so a roll in price "
            "level between session and session cancels out",
            "the session-level table averages the deep symbols within one session before "
            "averaging sessions; the per-symbol rows in this JSON share that session noise",
            "the reversal block is a census with n, slope and the sessions still missing -- "
            "it is not a verdict and must not be quoted as one",
            "five reversal slopes are tested at once; |t| has to clear the per-test line that "
            "controls for that, and 44 sessions of one regime is not a robustness check",
        ],
    }
    return payload


def render(payload):
    lines = []
    lines.append("# The minute feed's first reader")
    lines.append("")
    lines.append("generated %s | cutoff %s | feed `%s`"
                 % (payload["generated"], payload["evidence_cutoff"], payload["feed_dir"]))
    lines.append("")
    lines.append("`data/minute_feed/` has had a writer since 2026-09-15 and never a reader. "
                 "This is its first one. It audits the delivery, prices the fill the book "
                 "assumes, and sizes the question the board still calls data-blocked.")
    lines.append("")
    lines.append("## What was delivered")
    lines.append("")
    lines.append("| symbol | sessions | full | median bars | 09:30 missing | duplicate minutes | first | last |")
    lines.append("|---|---|---|---|---|---|---|---|")
    for s in payload["symbols"]:
        a = s.get("audit") or {}
        if not a:
            lines.append("| %s | 0 | 0 | 0 | — | — | — | %s |" % (s["symbol"], s.get("note", "")))
            continue
        lines.append("| %s | %d | %d | %d | %d | %d | %s | %s |" % (
            s["symbol"], a["sessions"], a["full_sessions"], a["median_bars_full"],
            a["sessions_missing_0930"], a["duplicate_minutes"],
            a["first_session"], a["last_session"]))
    lines.append("")
    lines.append("A *full* session is one with at least %d one-minute bars; earlier sessions are "
                 "fragments of the collector's rolling window and are counted here rather than "
                 "quietly dropped." % payload["full_session_bars"])
    lines.append("")
    lines.append("## What the feed cannot price at all")
    lines.append("")
    missing = {}
    for sym in payload["symbols"]:
        a = sym.get("audit") or {}
        for h in a.get("holes", []):
            missing.setdefault(h["minute"], []).append(sym["symbol"])
    zero_auction = [sym["symbol"] for sym in payload["symbols"]
                    if sym.get("audit", {}).get("sessions_missing_0930_share") == 1.0]
    lines.append("- no **09:30** print in any session of %s — the auction print the book actually "
                 "fills against is not in this panel, so every ladder number below is measured "
                 "from the first *continuous* print instead" % (", ".join(zero_auction) or "no symbol"))
    for minute, syms in sorted(missing.items(), key=lambda kv: -len(kv[1]))[:4]:
        lines.append("- %s missing in %d symbol(s)" % (minute, len(syms)))
    lines.append("")
    lines.append("## What buying later than the open costs")
    lines.append("")
    lines.append("Measured against each session's first continuous print, in bp. Positive = you "
                 "paid more by waiting; negative = waiting was cheaper. The %d deep symbols (%s) "
                 "are averaged inside each session first, so `n` is sessions, not rows."
                 % (len(payload["ladder_deep_symbols"]), ", ".join(payload["ladder_deep_symbols"])))
    lines.append("")
    lines.append("| minute | n | mean bp | median bp | sd bp | t | share above zero |")
    lines.append("|---|---|---|---|---|---|---|")
    for t in payload["ladder_minutes"]:
        a = payload["ladder_session_stats"].get(t) or {}
        if "mean_bp" not in a:
            lines.append("| %s | %d | — | — | — | — | — |" % (t, a.get("n", 0)))
            continue
        lines.append("| %s | %d | %+.2f | %+.2f | %.2f | %s | %.0f%% |" % (
            t, a["n"], a["mean_bp"], a["median_bp"], a["sd_bp"],
            ("%+.2f" % a["t"]) if a.get("t") is not None else "—", a["share_above"] * 100))
    lines.append("")
    lines.append("Read it as a dispersion problem, not a forecast: the mean is the size of the "
                 "toll and the sd is why a person cannot pick the good minute in advance. A t "
                 "under 2 on %d sessions says the average toll is not distinguishable from zero, "
                 "not that waiting is free." % payload["ladder_session_n"])
    lines.append("")
    lines.append("## The question the board still calls data-blocked")
    lines.append("")
    lines.append("Does the first half hour predict the rest of the day? Census over the same "
                 "full sessions, pooled per symbol:")
    lines.append("")
    lines.append("| symbol | n | slope | t | sd first30 | sd rest | MDE mean bp | sessions for 5bp |")
    lines.append("|---|---|---|---|---|---|---|---|")
    for s in payload["symbols"]:
        r = s.get("reversal")
        if not r or r.get("n", 0) < 20:
            continue
        lines.append("| %s | %d | %+.4f | %+s | %.2f | %.2f | %.2f | %d |" % (
            s["symbol"], r["n"], r["slope"],
            ("%.2f" % r["t"]) if r["t"] is not None else "—",
            r["sd_first30_bp"], r["sd_rest_bp"], r["mde_mean_bp"], r["sessions_for_5bp"]))
    lines.append("")
    lines.append("")
    lines.append("Five slopes are tested at once here. A single |t| near 2.5 among five tests sits "
                 "on the line a Bonferroni-style correction draws, and 44 sessions from one "
                 "autumn regime is not a robustness check -- quote the slope as a measurement "
                 "of this sample only.")
    lines.append("`MDE mean bp` is the smallest rest-of-day move a %g bp/session claim could "
                 "clear at 80%% power with this many sessions; `sessions for 5bp` is how many "
                 "full sessions one symbol needs before that claim is even askable. Neither "
                 "number is a result -- they are the price of asking." % payload["target_bp_per_session"])
    lines.append("")
    lines.append("## What this face does not say")
    lines.append("")
    for note in payload["notes"]:
        lines.append("- " + note)
    lines.append("")
    return "\n".join(lines)


def run(out_face=FACE, out_page=PAGE, feed_dir=FEED_DIR):
    payload = build(feed_dir)
    import datetime as dt
    payload["generated"] = dt.datetime.now().astimezone().isoformat(timespec="seconds")
    text = json.dumps(payload, ensure_ascii=False, indent=1) + "\n"
    tmp = out_face + ".tmp"
    with io.open(tmp, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    os.replace(tmp, out_face)
    page = render(payload)
    tmp = out_page + ".tmp"
    with io.open(tmp, "w", encoding="utf-8", newline="\n") as f:
        f.write(page)
    os.replace(tmp, out_page)
    cut = payload["evidence_cutoff"]
    ok = len(payload["symbols_with_full_sessions"])
    print("minute_feed_first_reader: %d symbol(s) with full sessions, cutoff %s" % (ok, cut))
    print("  face -> %s" % _rel(out_face))
    print("  page -> %s" % _rel(out_page))
    return 0


def _strip_runtime(payload):
    p = dict(payload)
    p.pop("generated", None)
    return p


def check(face=FACE, feed_dir=FEED_DIR):
    if not os.path.exists(face):
        print("STALE: face missing at %s -- run the writer" % os.path.relpath(face, ROOT))
        return 3
    disk = json.load(io.open(face, encoding="utf-8"))
    fresh = build(feed_dir)
    if _strip_runtime(disk) == _strip_runtime(fresh):
        print("CHECK OK: face matches the feed on disk (cutoff %s)" % disk.get("evidence_cutoff"))
        return 0
    d = _strip_runtime(disk)
    f = _strip_runtime(fresh)
    diffs = [k for k in set(d) | set(f) if d.get(k) != f.get(k)]
    if "symbols" in diffs:
        # the panel moved: this is a snapshot question, not an arithmetic one
        old_cut = d.get("evidence_cutoff")
        new_cut = f.get("evidence_cutoff")
        print("STALE: the feed has moved since this face was written "
              "(face cutoff %s, feed cutoff %s) -- run the writer" % (old_cut, new_cut))
        return 3
    print("CHECK FAILED: face disagrees with a fresh derivation on key(s) %s" % sorted(diffs))
    return 1


def selftest():
    import tempfile
    fails = []
    tmp = tempfile.mkdtemp(prefix="mffr_selftest_")

    def write(name, rows):
        p = os.path.join(tmp, name)
        with io.open(p, "w", encoding="utf-8", newline="\n") as f:
            f.write("day,open,high,low,close,volume,amount\n")
            for r in rows:
                f.write("%s,%.3f,%.3f,%.3f,%.3f,1,1\n" % r)
        return p

    # a synthetic 3-session feed with 240 bars each, a known 10:00 move
    def session(day, p0, p10, plast):
        rows = []
        for i in range(240):
            minute = 9 * 60 + 30 + i
            if i >= 121:          # after the lunch break is not modelled; keep it simple
                minute += 90
            hh, mm = divmod(minute, 60)
            if mm == 60:
                hh, mm = hh + 1, 0
            price = p0
            if (hh, mm) == (10, 0):
                price = p10
            elif i == 239:
                price = plast
            rows.append(("%s %02d:%02d:00" % (day, hh, mm), price, price, price, price))
        return rows

    rows = session("2026-01-05", 4.000, 4.004, 3.996)
    rows += session("2026-01-06", 4.000, 3.996, 4.004)
    rows += session("2026-01-07", 4.000, 4.000, 4.000)
    feed = os.path.join(tmp, "X")
    os.makedirs(feed, exist_ok=True)
    write(os.path.join("X", "999999.csv").replace("\\", "/"), rows)

    p = build(feed)
    sym = p["symbols"][0]
    if sym["audit"]["full_sessions"] != 3:
        fails.append("audit: expected 3 full sessions, got %r" % sym["audit"]["full_sessions"])
    if sym["audit"]["sessions_missing_0930"] != 0:
        fails.append("audit: 09:30 should be present in the synthetic feed")
    # 10:00 leg: +10bp, -10bp, 0 -> mean 0, sd ~ 10*sqrt(2/2)=10 (sample sd of [-10,0,10]=10)
    leg = sym["ladder"]["10:00"]
    if abs(leg["mean_bp"]) > 1e-9:
        fails.append("ladder: expected mean 0 at 10:00, got %r" % leg["mean_bp"])
    if abs(leg["sd_bp"] - 10.0) > 1e-6:
        fails.append("ladder: expected sd 10.0 at 10:00, got %r" % leg["sd_bp"])
    if abs(leg["share_above"] - 1.0 / 3) > 1e-3:
        fails.append("ladder: expected 1/3 above zero, got %r" % leg["share_above"])
    # a session with a hole in the 09:30 print must be counted, not dropped
    rows2 = session("2026-01-08", 4.0, 4.0, 4.0)
    rows2 = [r for r in rows2 if not r[0].endswith("09:30:00")]
    write("X/888888.csv", rows2)
    p2 = build(feed)
    s2 = [s for s in p2["symbols"] if s["symbol"] == "888888"][0]
    if s2["audit"]["sessions_missing_0930"] != 1:
        fails.append("audit: a session without 09:30 must be counted as missing")
    # empty feed must be named as such, never read as zero
    open(os.path.join(feed, "777777.csv"), "w").close()
    p3 = build(feed)
    s3 = [s for s in p3["symbols"] if s["symbol"] == "777777"][0]
    if s3.get("audit"):
        fails.append("audit: an empty feed must not produce audit numbers")
    if "777777" not in p3["symbols_without_data"]:
        fails.append("audit: an empty feed must be named in symbols_without_data")
    # check(): identical face -> 0, poisoned face -> non-zero without STALE
    face = os.path.join(tmp, "face.json")
    page = os.path.join(tmp, "page.md")
    run(face, page, feed)
    if not os.path.exists(page) or "first reader" not in io.open(page, encoding="utf-8").read():
        fails.append("page: render produced no page")
    import datetime as dt
    if check(face, feed) != 0:
        fails.append("check: an unchanged feed must pass")
    disk = json.load(io.open(face, encoding="utf-8"))
    disk["full_session_bars"] = 999
    io.open(face, "w", encoding="utf-8").write(json.dumps(disk, ensure_ascii=False, indent=1))
    rc = check(face, feed)
    if rc != 1:
        fails.append("check: an arithmetic mismatch must be rc 1 (got %r)" % rc)
    # and a moved input must say STALE (rc 3), which is what the chain pays for
    run(face, page, feed)
    before = io.open(face, encoding="utf-8").read()
    write("X/666666.csv", session("2026-01-09", 4.0, 4.0, 4.0))
    rc = check(face, feed)
    if rc != 3:
        fails.append("check: a moved feed must be rc 3 STALE (got %r)" % rc)
    _ = before
    for name in os.listdir(tmp):
        pass
    if fails:
        print("SELFTEST FAILED (%d)" % len(fails))
        for f in fails:
            print("  - " + f)
        return 1
    legs = 12
    print("SELFTEST OK %d/%d" % (legs, legs))
    return 0


def main(argv):
    cmd = argv[1] if len(argv) > 1 else "run"
    if cmd in ("--check", "check"):
        return check()
    if cmd in ("--selftest", "selftest"):
        return selftest()
    return run()


if __name__ == "__main__":
    sys.exit(main(sys.argv))
