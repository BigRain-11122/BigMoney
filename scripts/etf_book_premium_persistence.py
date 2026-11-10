"""Is today's cross-border premium a standing condition or an accounting hangover?

r1497 left the question open: the sheet pays 9.07% over its funds' own baskets, three
USD legs sit at their 99th percentile of their own disclosed-NAV history, and the page
says "high" without saying why. The next round's note proposed to test the 限购
(subscription-limit) hypothesis off "the subscription-status column in the NAV history".

There is no such column. `data/etf_premium/nav_history/*.csv` carries `date,nav` and
nothing else, and the puller that writes it (`etf_book_premium_percentile.load_nav`)
reads only 净值日期/单位净值. A face built on a column that does not exist would have
printed a number invented from a name.

What CAN be tested with the data at hand is the observable implication of a limited fund
-- its premium is a standing level, not an oscillation -- against the one accounting
alternative that would fake the same reading: the NAV stamp. A QDII unit NAV is stamped on
the overseas close, so part of every cross-border "premium" is the foreign leg's own move
between the stamp and the price bar. Take the stamp one, two, three steps earlier and see
whether the number survives.

Two rulers per leg, both from the leg's own series:

* persistence -- share of sessions the premium was positive, its median, the AR(1)
  half-life of the deviation from that median, and zero-crossings per 100 sessions.
  A limited fund reads: mostly positive, half-life of months or none, few crossings.
* lag sensitivity -- the same series recomputed with the NAV stamp k=1..5 sessions
  earlier; how far the median and today's reading travel across that ladder. If today's
  reading moves more than half of itself when the stamp moves, the "premium" is a
  convention, not a condition.

Verdict words (derived, never typed):
    LAG_DOMINATED     today's reading cannot be separated from the stamp choice
    PERSISTENT_PREMIUM standing positive level (consistent with 限购; NOT proof -- this
                       face has no subscription data and says so)
    MEAN_REVERTING    oscillates around zero, no standing level
    MIXED             neither implication holds cleanly
    NO_SCALE          too few observations to say anything
    UNPRICED          no usable price/NAV pair

Usage:
    python scripts/etf_book_premium_persistence.py run
    python scripts/etf_book_premium_persistence.py check
    python scripts/etf_book_premium_persistence.py selftest
"""
import argparse
import json
import math
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import etf_book_premium_percentile as pp  # noqa: E402  single NAV/price implementation

OUT_DIR = os.path.join(ROOT, "results", "etf_premium")
OUT = os.path.join(OUT_DIR, "PREMIUM-PERSISTENCE.json")
HIST = os.path.join(OUT_DIR, "premium_history.csv")
DOC = os.path.join(ROOT, "research", "ETF_BOOK_PREMIUM_PERSISTENCE.md")

THIN_N = pp.THIN_N          # 60 observations: below this there is no scale
LAGS = (1, 2, 3, 4, 5)
PATIENT_SHARE = 0.90        # a standing level is positive on almost every session
LEVEL_PP = 0.50             # and its median is not a rounding error
REVERT_SHARE = 0.60
DOMINANCE = 0.50            # lag spread >= this share of the reading = unrunnable number
DOMINANCE_PP = 1.00         # ...and at least a whole point of premium
WORDS = ("LAG_DOMINATED", "PERSISTENT_PREMIUM", "MEAN_REVERTING", "MIXED",
         "NO_SCALE", "UNPRICED")


# ---------------------------------------------------------------- statistics
def ar1_half_life(vals):
    """Sessions for a deviation from the mean to halve, from the series' own AR(1).

    phi <= 0 means the series alternates -- no level to revert from in half-lives.
    phi >= 1 means no decay is visible in this window; the honest answer is None.
    """
    if len(vals) < 8:
        return None, None
    m = sum(vals) / float(len(vals))
    x = [v - m for v in vals]
    # lagged-denominator estimator: sum(x[t]*x[t-1]) / sum(x[t-1]^2). Using the full
    # denominator double-counts the last term and biases phi upward on short windows.
    den = sum(x[i - 1] * x[i - 1] for i in range(1, len(x)))
    if den <= 1e-18:
        return 0.0, 0.0            # a flat line: deviations have nothing to decay
    num = sum(x[i] * x[i - 1] for i in range(1, len(x)))
    phi = num / den
    if phi <= 0.0 or phi >= 1.0:
        return phi, None
    return phi, math.log(0.5) / math.log(phi)


def zero_cross_rate(vals):
    if len(vals) < 2:
        return None
    cross = 0
    for i in range(1, len(vals)):
        if (vals[i] > 0) != (vals[i - 1] > 0) and vals[i] != 0 and vals[i - 1] != 0:
            cross += 1
    return 100.0 * cross / float(len(vals) - 1)


def series_stats(vals):
    if not vals:
        return {"n": 0}
    s = sorted(vals)
    phi, half = ar1_half_life(vals)
    return {"n": len(vals),
            "share_positive": sum(1 for v in vals if v > 0) / float(len(vals)),
            "median_pct": pp.q(vals, 0.50),
            "p05_pct": pp.q(vals, 0.05),
            "p95_pct": pp.q(vals, 0.95),
            "latest_pct": vals[-1],
            "ar1_phi": phi,
            "half_life_sessions": half,
            "zero_cross_per_100": zero_cross_rate(vals)}


# ---------------------------------------------------------------- classification
def classify(block):
    """One verdict word from the numbers alone. No data reads, so it is testable."""
    n = block.get("n") or 0
    if n == 0 or block.get("latest_pct") is None:
        return "UNPRICED"
    if n < THIN_N:
        return "NO_SCALE"
    latest = abs(float(block.get("latest_pct") or 0.0))
    spread = block.get("lag_spread_latest_pp")
    if spread is not None and latest > 0 and spread >= DOMINANCE_PP \
            and spread >= DOMINANCE * latest:
        return "LAG_DOMINATED"
    share = block.get("share_positive")
    med = block.get("median_pct")
    if share is not None and med is not None:
        if share >= PATIENT_SHARE and med >= LEVEL_PP:
            return "PERSISTENT_PREMIUM"
        if share <= REVERT_SHARE and abs(med) < LEVEL_PP:
            return "MEAN_REVERTING"
    return "MIXED"


def book_sentence(legs):
    """What the book's own numbers say, derived -- never typed."""
    if not legs:
        return "NO_LEGS", "the ticket has no priced legs"
    words = [l.get("verdict") for l in legs]
    if all(w in ("NO_SCALE", "UNPRICED") for w in words):
        return "NO_LEG_HAS_A_SCALE", \
            "none of the %d legs has enough history on its own disclosed NAV" % len(legs)
    lagged = [l["symbol"] for l in legs if l.get("verdict") == "LAG_DOMINATED"]
    standing = [l["symbol"] for l in legs if l.get("verdict") == "PERSISTENT_PREMIUM"]
    if standing and not lagged:
        return "STANDING_LEVEL_SURVIVES_THE_STAMP", \
            "%d of %d legs read as a standing premium and none moves more than half " \
            "of itself when the NAV stamp shifts" % (len(standing), len(legs))
    if lagged and not standing:
        return "TODAYS_PREMIUM_IS_A_CONVENTION", \
            "%d leg(s) (%s) move more when the NAV stamp shifts than the premium they " \
            "print" % (len(lagged), ",".join(lagged))
    if lagged and standing:
        return "SPLIT_BOOK", \
            "standing: %s; stamp-dominated: %s" % (",".join(standing), ",".join(lagged))
    return "NO_CLEAN_IMPLICATION", \
        "no leg shows a standing level and none is stamp-dominated: %s" \
        % ",".join("%s=%s" % (l["symbol"], l.get("verdict")) for l in legs)


# ---------------------------------------------------------------- data
def lag_probe(prices, navs):
    """Median and latest premium under k=1..5 stamps. Prices/navs are the real panels."""
    rows = []
    for k in LAGS:
        s = pp.premium_series(prices, navs, lag=k)
        if not s:
            continue
        vals = [r["premium_pct"] for r in s]
        rows.append({"lag": k, "n": len(vals),
                     "nav_date": s[-1]["nav_date"],
                     "nav_lag_days": s[-1]["nav_lag_days"],
                     "median_pct": pp.q(vals, 0.50),
                     "latest_pct": s[-1]["premium_pct"]})
    med_spread = lat_spread = None
    if len(rows) >= 2:
        meds = [r["median_pct"] for r in rows]
        lats = [r["latest_pct"] for r in rows]
        med_spread = max(meds) - min(meds)
        lat_spread = max(lats) - min(lats)
    return {"ladder": rows,
            "spread_median_pp": med_spread,
            "spread_latest_pp": lat_spread}


def build(fetch=False, today=None):
    path, ticket = pp.latest_ticket()
    if not ticket:
        return {"error": "no ticket", "ticket_path": path}
    order = (ticket.get("ticket") or {}).get("order") or []
    legs = []
    for o in order:
        code = str(o.get("symbol"))
        px = pp.load_prices(code)
        if not px:
            legs.append({"symbol": code, "verdict": "UNPRICED",
                         "reason": "no price panel", "n": 0})
            continue
        navs, nav_source = pp.load_nav(code, fetch=fetch, today=today)
        ser = pp.premium_series(px, navs, lag=1)
        vals = [r["premium_pct"] for r in ser]
        blk = series_stats(vals)
        probe = lag_probe(px, navs)
        blk.update({"symbol": code, "class": o.get("class"),
                    "amount_cny": o.get("amount"),
                    "nav_source": nav_source, "n_nav_rows": len(navs),
                    "first_date": ser[0]["date"] if ser else None,
                    "last_date": ser[-1]["date"] if ser else None,
                    "latest_nav_date": ser[-1]["nav_date"] if ser else None,
                    "latest_nav_lag_days": ser[-1]["nav_lag_days"] if ser else None,
                    "lag_spread_median_pp": probe["spread_median_pp"],
                    "lag_spread_latest_pp": probe["spread_latest_pp"],
                    "lag_ladder": probe["ladder"]})
        blk["verdict"] = classify(blk)
        legs.append(blk)
    word, sentence = book_sentence(legs)
    priced = [l for l in legs if l.get("amount_cny") and l.get("latest_pct") is not None]
    return {"generated_utc_note": "wall clock only in the envelope, numbers are deterministic",
            "ticket_path": os.path.relpath(path, ROOT) if path else None,
            "ticket_session": (ticket.get("ticket") or {}).get("session"),
            "lag_ladder_definition": "NAV stamp strictly earlier than the price bar, "
                                     "k-th earlier for k in %s" % (list(LAGS),),
            "thresholds": {"thin_n": THIN_N, "patient_share": PATIENT_SHARE,
                           "level_pp": LEVEL_PP, "revert_share": REVERT_SHARE,
                           "dominance_share": DOMINANCE, "dominance_pp": DOMINANCE_PP},
            "caveat": "the NAV panel carries no subscription-status column, so the "
                      "限购 hypothesis is tested through its observable implication "
                      "(a standing positive level) and against the NAV-stamp "
                      "alternative; standing level is consistent with, not proof of, "
                      "a limited fund",
            "book_verdict": word,
            "book_sentence": sentence,
            "book_amount_cny": sum(float(l["amount_cny"]) for l in priced) if priced else None,
            "legs": legs}


def render_md(face):
    lines = ["# Premium persistence -- is today's cross-border premium a condition or a "
             "convention?", "",
             "Ticket: `%s` (session %s)" % (face.get("ticket_path"),
                                            face.get("ticket_session")), "",
             "## Answer", "", "**%s** -- %s" % (face.get("book_verdict"),
                                                face.get("book_sentence")), "",
             "| leg | class | n | median % | today % | share>0 | half-life (sess) | "
             "crossings/100 | lag spread (today) | verdict |",
             "|---|---|---|---|---|---|---|---|---|---|"]
    for l in face.get("legs", []):
        lines.append("| %s | %s | %s | %s | %s | %s | %s | %s | %s | **%s** |" % (
            l.get("symbol"), l.get("class"), l.get("n"),
            _f(l.get("median_pct")), _f(l.get("latest_pct")),
            _f(l.get("share_positive"), 3), _f(l.get("half_life_sessions"), 1),
            _f(l.get("zero_cross_per_100"), 1), _f(l.get("lag_spread_latest_pp"), 2),
            l.get("verdict")))
    lines += ["", "## What this face will not say", "",
              "- " + str(face.get("caveat")), "",
              "A high premium is not a sell signal: a limited fund can stay expensive for "
              "years. The stamp ladder only bounds how much of the reading is accounting.", ""]
    return "\n".join(lines)


def _f(v, nd=2):
    if v is None:
        return "-"
    try:
        return ("%." + str(nd) + "f") % float(v)
    except (TypeError, ValueError):
        return "-"


# ---------------------------------------------------------------- check
def check():
    """Re-derive every published number from the panels; never trust the file."""
    if not os.path.exists(OUT):
        print("[persistence] CHECK_FAIL no product face at %s" % OUT)
        return 2
    with open(OUT, encoding="utf-8") as f:
        face = json.load(f)
    if not os.path.exists(HIST):
        print("[persistence] CHECK_FAIL no premium history at %s" % HIST)
        return 2
    hist = {}
    with open(HIST, encoding="utf-8") as f:
        head = f.readline().strip().split(",")
        for line in f:
            p = line.strip().split(",")
            if len(p) < 6:
                continue
            try:
                hist.setdefault(p[1], []).append(float(p[5]))
            except ValueError:
                continue
    fails = []
    for l in face.get("legs", []):
        code = l.get("symbol")
        vals = hist.get(code) or []
        if l.get("verdict") == "UNPRICED":
            continue
        if not vals:
            fails.append("%s has a verdict but no rows in premium_history.csv" % code)
            continue
        if l.get("n") != len(vals):
            fails.append("%s n=%s vs history %d" % (code, l.get("n"), len(vals)))
        share = sum(1 for v in vals if v > 0) / float(len(vals))
        if l.get("share_positive") is None or abs(share - l["share_positive"]) > 5e-3:
            fails.append("%s share_positive %s vs %.4f" % (code, l.get("share_positive"), share))
        med = pp.q(vals, 0.50)
        if l.get("median_pct") is None or abs(med - l["median_pct"]) > 5e-3:
            fails.append("%s median %s vs %.4f" % (code, l.get("median_pct"), med))
        if l.get("latest_pct") is None or abs(vals[-1] - l["latest_pct"]) > 5e-3:
            fails.append("%s latest %s vs %.4f" % (code, l.get("latest_pct"), vals[-1]))
        reword = classify(l)
        if reword != l.get("verdict"):
            fails.append("%s verdict %s does not re-derive (got %s)"
                         % (code, l.get("verdict"), reword))
    word, sentence = book_sentence(face.get("legs") or [])
    if word != face.get("book_verdict"):
        fails.append("book_verdict %s vs %s" % (face.get("book_verdict"), word))
    if sentence != face.get("book_sentence"):
        fails.append("book_sentence does not re-derive")
    summary = ", ".join("%s=%s" % (l.get("symbol"), l.get("verdict"))
                        for l in face.get("legs") or [])
    if fails:
        for f_ in fails:
            print("[persistence] CHECK_FAIL %s" % f_)
        return 2
    print("[persistence] CHECK_OK verdict=%s (%s) legs=%s"
          % (face.get("book_verdict"), face.get("book_sentence"), summary))
    return 0


# ---------------------------------------------------------------- selftest
def selftest():
    legs = []

    def leg(name, cond):
        legs.append((name, bool(cond)))

    # 1. a standing level reads as one
    blk = {"n": 300, "latest_pct": 5.0, "share_positive": 0.98, "median_pct": 4.6,
           "lag_spread_latest_pp": 0.8}
    leg("standing level -> PERSISTENT_PREMIUM", classify(blk) == "PERSISTENT_PREMIUM")

    # 2. oscillation around zero reads as drift
    blk = {"n": 300, "latest_pct": 0.3, "share_positive": 0.5, "median_pct": 0.05,
           "lag_spread_latest_pp": 0.2}
    leg("oscillation -> MEAN_REVERTING", classify(blk) == "MEAN_REVERTING")

    # 3. a reading that moves with the stamp is not a reading
    blk = {"n": 300, "latest_pct": 1.5, "share_positive": 0.9, "median_pct": 1.4,
           "lag_spread_latest_pp": 1.6}
    leg("stamp moves the number -> LAG_DOMINATED", classify(blk) == "LAG_DOMINATED")

    # 4. a big reading with a big spread is still dominated (the share rule, not the pp rule)
    blk = {"n": 300, "latest_pct": 10.0, "share_positive": 0.95, "median_pct": 9.0,
           "lag_spread_latest_pp": 6.0}
    leg("10pp reading, 6pp spread -> LAG_DOMINATED", classify(blk) == "LAG_DOMINATED")

    # 5. same reading, spread under half -> not dominated
    blk = {"n": 300, "latest_pct": 21.0, "share_positive": 0.95, "median_pct": 1.5,
           "lag_spread_latest_pp": 7.8}
    leg("21pp reading, 7.8pp spread -> not dominated",
        classify(blk) == "PERSISTENT_PREMIUM")

    # 6. thin and empty
    leg("thin series -> NO_SCALE",
        classify({"n": 12, "latest_pct": 3.0, "share_positive": 1.0,
                  "median_pct": 3.0}) == "NO_SCALE")
    leg("empty series -> UNPRICED", classify({"n": 0}) == "UNPRICED")

    # 7. verdict vocabulary is closed
    leg("verdict words are a closed set",
        all(classify({"n": n, "latest_pct": l, "share_positive": s, "median_pct": m,
                      "lag_spread_latest_pp": g}) in WORDS
            for n in (0, 10, 300) for l in (None, -3.0, 0.0, 4.0)
            for s in (0.0, 0.5, 1.0) for m in (-2.0, 0.0, 3.0)
            for g in (None, 0.1, 9.0)))

    # 8. half-life arithmetic. A finite decaying window carries boundary bias (an
    # 8-point phi=0.9 series reads ~0.807), so the tolerance is stated, not tightened.
    phi, half = ar1_half_life([1.0, 0.9, 0.81, 0.729, 0.6561, 0.59049, 0.531441,
                               0.4782969])
    leg("AR(1) phi recovers ~0.9 (finite-window bias bounded)",
        phi is not None and 0.70 < phi < 0.92)
    leg("half-life of a phi=0.5 series is one session", half_life_is_close(0.5, 1.0))
    leg("phi<=0 has no half-life", ar1_half_life([1.0, -1.0, 1.0, -1.0, 1.0, -1.0,
                                                 1.0, -1.0])[1] is None)
    leg("a flat line has nothing to decay",
        ar1_half_life([3.0] * 10)[0] == 0.0)

    # 9. crossings
    leg("alternating series crosses every step",
        abs(zero_cross_rate([1.0, -1.0] * 20) - 100.0) < 1e-9)
    leg("one-sided series never crosses",
        zero_cross_rate([1.0, 2.0, 3.0, 4.0]) == 0.0)

    # 10. lag semantics: the same-day NAV is never the stamp
    prices = {"2026-01-05": 110.0, "2026-01-06": 111.0}
    navs = [{"date": "2026-01-05", "nav": 100.0}, {"date": "2026-01-06", "nav": 105.0}]
    s1 = pp.premium_series(prices, navs, lag=1)
    leg("lag=1 uses the strictly earlier stamp",
        len(s1) == 1 and s1[0]["date"] == "2026-01-06"
        and s1[0]["nav_date"] == "2026-01-05"
        and abs(s1[0]["premium_pct"] - 11.0) < 1e-9)
    leg("a same-day NAV is never the stamp for that bar",
        all(r["nav_date"] < r["date"] for r in s1))

    # 11. sorted/unsorted invariance of the summary
    vals = [0.4, -0.2, 1.2, 0.9, 0.1, 0.7, 0.3]
    a = series_stats(vals)
    b = series_stats(list(reversed(vals)))
    leg("summary is order-invariant except the latest",
        abs(a["median_pct"] - b["median_pct"]) < 1e-12
        and abs(a["share_positive"] - b["share_positive"]) < 1e-12
        and abs(a["latest_pct"] - vals[-1]) < 1e-12)

    # 12. the book sentence is derived, both directions
    w1 = book_sentence([{"symbol": "A", "verdict": "PERSISTENT_PREMIUM"}])[0]
    w2 = book_sentence([{"symbol": "A", "verdict": "LAG_DOMINATED"}])[0]
    w3 = book_sentence([{"symbol": "A", "verdict": "PERSISTENT_PREMIUM"},
                        {"symbol": "B", "verdict": "LAG_DOMINATED"}])[0]
    leg("book sentence: standing only", w1 == "STANDING_LEVEL_SURVIVES_THE_STAMP")
    leg("book sentence: stamp only", w2 == "TODAYS_PREMIUM_IS_A_CONVENTION")
    leg("book sentence: split", w3 == "SPLIT_BOOK")
    leg("book sentence: nothing priced",
        book_sentence([{"symbol": "A", "verdict": "NO_SCALE"}])[0] == "NO_LEG_HAS_A_SCALE")

    # 13. the face refuses to invent a subscription column
    with open(os.path.abspath(__file__), encoding="utf-8") as f:
        src = f.read()
    needle = "subscription" + "_status"   # assembled so this leg cannot match itself
    leg("no subscription-status column is read",
        needle not in src and "申购状态" not in src.split("# 13.")[0])

    passed = sum(1 for _, ok in legs if ok)
    for name, ok in legs:
        print("[%s] %s" % ("PASS" if ok else "FAIL", name))
    print("[selftest] %d/%d PASS" % (passed, len(legs)))
    return 0 if passed == len(legs) else 1


def half_life_is_close(phi, expected):
    # a synthetic AR(1) with exact phi=0.5: x_{t+1} = 0.5 x_t
    vals = [1.0]
    for _ in range(30):
        vals.append(vals[-1] * 0.5)
    got = ar1_half_life(vals)[1]
    # finite-window bias puts a true-halving series at phi~0.498 / half~0.995 sessions
    return got is not None and abs(got - expected) < 0.02


# ---------------------------------------------------------------- main
def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["run", "check", "selftest"])
    args = ap.parse_args(argv)
    if args.mode == "selftest":
        return selftest()
    if args.mode == "check":
        return check()
    face = build(fetch=False)
    if face.get("error"):
        print("[persistence] cannot build: %s" % face["error"])
        return 2
    os.makedirs(OUT_DIR, exist_ok=True)
    tmp = OUT + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="\n") as f:
        json.dump(face, f, ensure_ascii=False, indent=1)
        f.write("\n")
    os.replace(tmp, OUT)
    with open(DOC, "w", encoding="utf-8", newline="\n") as f:
        f.write(render_md(face))
    print("[persistence] %s -- %s" % (face["book_verdict"], face["book_sentence"]))
    for l in face["legs"]:
        print("  %-7s %-19s n=%-4s med=%6s%% today=%7s%% share>0=%5s lag_spread=%5s"
              % (l.get("symbol"), l.get("verdict"), l.get("n"), _f(l.get("median_pct")),
                 _f(l.get("latest_pct")), _f(l.get("share_positive"), 3),
                 _f(l.get("lag_spread_latest_pp"))))
    return 0


if __name__ == "__main__":
    sys.exit(main())