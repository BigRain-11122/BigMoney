"""The sheet pays for premium; the page could only say "today looks expensive".

The 11-10 live-book page prints, on its own words, that the USD 9.07% of the sheet
priced above the funds' own baskets cannot be judged: "159501/513100/159577 have fewer
than 2 usable observations on the price/NAV ruler, so this page cannot answer whether
today's premium is high". The spot-board reading (23.64% / 21.26% / 9.67%) is a single
afternoon; a premium with no history is a number without a scale.

This face gives it a scale: for every leg of the executable ticket, walk the fund's own
disclosed unit NAV history (as-collected, T-1 convention -- NAV strictly EARLIER than the
price bar, never same-day), divide the panel close by it, and rank today's reading inside
its own distribution. Answer word per leg: AT_RECORD_HIGH / UPPER_TAIL / LOWER_TAIL /
ORDINARY / THIN / UNPRICED, all derived from the series, never typed.

Three things this face refuses to do:

* It never uses a same-day NAV (that is the future relative to the close), and it states
  the NAV stamp it did use plus the lag in calendar days -- a QDII NAV is stamped on the
  foreign close, so part of every cross-border "premium" is the overseas move, not money
  someone is willing to overpay. The lag ladder (k=1/2/3 stamps) prints how much of the
  reading that accounting offset can move.
* It never adds the two rulers. IOPV (intraday basket value) and disclosed unit NAV are
  different quantities; the gate below reconciles against the spot board on the board's
  own ruler and does NOT convert one into the other.
* It never calls a high premium a sell signal. A限购 fund can stay expensive for years;
  the face prices "if it reverted to its own median, the sheet would lose X" and leaves
  the decision where it belongs.

Gate (refuse to publish, exit 2): the price panel must reproduce the published spot board
prices for the same session within 0.5%, and every published premium_pct must reconcile
to the board's own price/iopv within 0.01pp, and every priced leg's CNY figure must
satisfy over_nav = amount * (1 - 1/(1+premium)) within CNY 0.02.

Usage:
    python scripts/etf_book_premium_percentile.py run
    python scripts/etf_book_premium_percentile.py check
    python scripts/etf_book_premium_percentile.py selftest
"""
import argparse
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

NAV_DIR = os.path.join(ROOT, "data", "etf_premium", "nav_history")
OUT_DIR = os.path.join(ROOT, "results", "etf_premium")
OUT = os.path.join(OUT_DIR, "PREMIUM-PERCENTILE.json")
HIST = os.path.join(OUT_DIR, "premium_history.csv")
TICKET_DIR = os.path.join(ROOT, "results", "etf_book_order")
PRICE_DIR = os.path.join(ROOT, "data", "daily")

NAV_START = "20190101"
THIN_N = 60            # fewer observations than this is a reading without a scale
TAIL = 0.90            # upper tail: at or above the 90th percentile of its own history
PRICE_TOL = 0.005      # panel close vs published spot board price
PREM_TOL_PP = 0.01     # published premium vs recomputed price/iopv
CNY_TOL = 0.02
# The board publishes premium_pct to 4 decimals of a percent, so a reader who
# re-derives the CNY figure from that published number can only be accurate to
# half of the last digit times the amount. Scaling the tolerance by the amount
# is not a looser judgement -- it is the same 0.02 floor plus the producer's own
# quantisation, which is ~0.039 CNY on a 78.5k order and was refusing correct
# boards.
PREM_HALF_STEP_P = 5e-7

# r1566: the rank above counts every session a premium can be printed on. Some of those
# sessions are not the same measurement. When the market that turns the basket into a
# valuation was shut between the NAV stamp and this close, no new NAV could have been
# struck -- so the "premium" of that session also carries the price drift of the shut
# days, and it is not the quantity the operator is deciding on (one session's price above
# one session's valuation). The calendars are not re-implemented here: `closure_kind`
# (New York, rule-derived) and `hk_closure_kind` (Hong Kong, measured on the HSI series)
# are imported from the subscription producer at call time, so one defect keeps one copy.
# A second rank is then printed beside the first, with the number of sessions dropped, and
# the verdict word the page shows is the one that survives both rulers when they disagree
# -- a tail reading that only exists on rows whose denominator could not move is not a
# tail reading.
CAL_SOURCE = ("scripts/etf_book_premium_subscription.py (closure_kind / hk_closure_kind; "
              "single producer for both calendars)")
_CAL = {"loaded": False, "us": None, "hk": None, "hk_status": None, "error": None}


def _calendars():
    """(us_gap, hk_gap) callables, or (None, None) when the producer is unreadable.

    Imported lazily: the subscription face imports THIS module at its own top, so a
    module-level import here would close the cycle. Failure to load is not an error the
    face hides -- `calendars.status` on the published reading says which calendars it had.
    """
    if _CAL["loaded"]:
        return _CAL
    _CAL["loaded"] = True
    try:
        import etf_book_premium_subscription as sub
        _CAL["us"] = sub.closure_kind
        try:
            market, status = sub.load_hk_index(fetch=False)
            _CAL["hk"] = (lambda a, b: sub.hk_closure_kind(a, b, market))
            _CAL["hk_status"] = status
        except Exception as exc:                          # pragma: no cover
            _CAL["hk_status"] = "hk-unavailable:%s" % type(exc).__name__
    except Exception as exc:                              # pragma: no cover
        _CAL["error"] = "%s: %s" % (type(exc).__name__, str(exc)[:80])
    return _CAL


def valuation_gap(nav_date, price_date):
    """'us' / 'hk' / None: did a valuation gap sit inside (nav_date, price_date]?"""
    cal = _calendars()
    us, hk = cal.get("us"), cal.get("hk")
    hit = None
    if us is not None:
        try:
            if us(nav_date, price_date):
                hit = "us"
        except Exception:                                 # pragma: no cover
            pass
    if hk is not None:
        try:
            if hk(nav_date, price_date):
                hit = hit or "hk"
        except Exception:                                 # pragma: no cover
            pass
    return hit


def sina_sym(code):
    return ("sh" if str(code)[0] in ("5", "6") else "sz") + str(code)


def load_prices(code):
    """Panel close by date. The panel is the same one the ticket prices off."""
    path = os.path.join(PRICE_DIR, sina_sym(code) + ".csv")
    if not os.path.exists(path):
        return None
    out = {}
    with open(path, encoding="utf-8") as f:
        head = f.readline().strip().split(",")
        ic = head.index("close")
        for line in f:
            p = line.strip().split(",")
            if len(p) <= ic or not p[0]:
                continue
            try:
                out[p[0][:10]] = float(p[ic])
            except ValueError:
                continue
    return out


def load_nav(code, fetch=True, today=None):
    """As-collected unit NAV history. Returns (rows, status).

    rows = [{"date": "YYYY-MM-DD", "nav": float}] ascending. The cache is regenerable
    raw data (gitignored); the published face carries the derived series.
    """
    os.makedirs(NAV_DIR, exist_ok=True)
    path = os.path.join(NAV_DIR, str(code) + ".csv")
    rows = []
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            for line in f:
                p = line.strip().split(",")
                if len(p) < 2 or p[0] == "date":
                    continue
                try:
                    rows.append({"date": p[0][:10], "nav": float(p[1])})
                except ValueError:
                    continue
    latest = rows[-1]["date"] if rows else None
    fresh = bool(latest and today and latest >= today)
    if rows and fresh:
        return rows, "cache"
    if not fetch:
        return rows, "cache-stale"
    try:
        import akshare as ak
    except Exception as exc:                              # pragma: no cover
        return rows, "no-akshare:%s" % type(exc).__name__
    try:
        df = ak.fund_etf_fund_info_em(fund=str(code),
                                      start_date=NAV_START,
                                      end_date=(today or "20991231").replace("-", ""))
        got = {}
        for _, r in df.iterrows():
            d = str(r["净值日期"])[:10]
            try:
                v = float(r["单位净值"])
            except (TypeError, ValueError):
                continue
            if v > 0:
                got[d] = v
        merged = {r["date"]: r["nav"] for r in rows}
        merged.update(got)                                  # as-collected: later pull wins
        rows = [{"date": d, "nav": merged[d]} for d in sorted(merged)]
        tmp = path + ".tmp"
        with open(tmp, "w", encoding="utf-8", newline="\n") as f:
            f.write("date,nav\n")
            for r in rows:
                f.write("%s,%.6f\n" % (r["date"], r["nav"]))
        os.replace(tmp, path)
        return rows, "fetched"
    except Exception as exc:                               # pragma: no cover
        return rows, "fetch-error:%s" % type(exc).__name__


def premium_series(prices, navs, lag=1):
    """close(t) / nav(k-th earlier stamp) - 1.

    lag=1 means the newest NAV STRICTLY BEFORE the price date -- a NAV stamped on the
    same day is the future of that close and is never used.
    """
    if not prices or not navs:
        return []
    dates = [r["date"] for r in navs]
    out = []
    for d in sorted(prices):
        prior = [i for i, nd in enumerate(dates) if nd < d]
        if len(prior) < lag:
            continue
        i = prior[-lag]
        nav = navs[i]["nav"]
        close = prices[d]
        if nav <= 0 or close <= 0:
            continue
        out.append({"date": d, "close": close, "nav_date": navs[i]["date"],
                    "nav": nav, "premium_pct": (close / nav - 1.0) * 100.0,
                    "nav_lag_days": _days(navs[i]["date"], d)})
    return out


def _days(a, b):
    import datetime as dt
    try:
        da = dt.date.fromisoformat(a)
        db = dt.date.fromisoformat(b)
    except ValueError:
        return None
    return (db - da).days


def pct_rank(series, value):
    """Share of observations strictly below `value` (ties do not inflate the rank)."""
    if not series:
        return None
    vals = [r["premium_pct"] for r in series]
    return sum(1 for v in vals if v < value) / float(len(vals))


def q(vals, qq):
    if not vals:
        return None
    s = sorted(vals)
    if len(s) == 1:
        return s[0]
    pos = qq * (len(s) - 1)
    lo = int(pos)
    hi = min(lo + 1, len(s) - 1)
    return s[lo] + (s[hi] - s[lo]) * (pos - lo)


def stats(series):
    """Distribution of the leg's own premium readings + where the latest sits.

    Two ranks, one distribution: `rank_of_latest` counts every readable session, and
    `rank_of_latest_clean` counts only the sessions whose NAV stamp could have been struck
    (no closure of the basket's market inside the window). The counts are published so a
    reader can see how much of the scale came from rows the first ruler counts.
    """
    if not series:
        return {"n": 0, "verdict": "UNPRICED"}
    vals = [r["premium_pct"] for r in series]
    last = series[-1]
    hi = max(series, key=lambda r: r["premium_pct"])
    lo = min(series, key=lambda r: r["premium_pct"])
    rank = pct_rank(series, last["premium_pct"])
    # ties count as "at the record": a series that never moves is still at its own high
    if last["premium_pct"] >= hi["premium_pct"] - 1e-9:
        verdict = "AT_RECORD_HIGH"
    elif rank >= TAIL:
        verdict = "UPPER_TAIL"
    elif rank <= 1.0 - TAIL:
        verdict = "LOWER_TAIL"
    else:
        verdict = "ORDINARY"
    if len(vals) < THIN_N:
        verdict = "THIN"
    # r1566: the second ruler. A rank counts sessions, and not every session carries a new
    # valuation: a fund whose basket market was shut (or that simply did not strike a NAV)
    # carries the previous number forward, so that row's "premium" is the price moving
    # against a valuation that could not move. The test is the valuation itself -- a stamp
    # that repeats its predecessor carries no new number -- and the calendars in hand are
    # used only to EXPLAIN those rows, never to decide them, so a domestic fund is not
    # judged by a foreign holiday.
    stamps = []
    seen_nav = {}
    for r in series:
        nd = r.get("nav_date")
        if nd is None or r.get("nav") is None:
            continue
        if nd not in seen_nav:
            seen_nav[nd] = r["nav"]
            stamps.append((nd, r["nav"]))
    carry = set()
    for i in range(1, len(stamps)):
        if stamps[i][1] == stamps[i - 1][1]:
            carry.add(stamps[i][0])
    gaps = {}
    clean = []
    for r in series:
        if r.get("nav_date") in carry:
            g = valuation_gap(r.get("nav_date"), r.get("date")) or "unexplained"
            gaps[g] = gaps.get(g, 0) + 1
        else:
            clean.append(r)
    rank_clean = pct_rank(clean, last["premium_pct"]) if clean else None
    verdict_clean = None
    if len(clean) >= THIN_N:
        if rank_clean is not None and rank_clean >= TAIL:
            verdict_clean = "UPPER_TAIL"
        elif rank_clean is not None and rank_clean <= 1.0 - TAIL:
            verdict_clean = "LOWER_TAIL"
        else:
            verdict_clean = "ORDINARY"
        if last["premium_pct"] >= max(r["premium_pct"] for r in clean) - 1e-9:
            verdict_clean = "AT_RECORD_HIGH"
    return {"n": len(vals),
            "first_date": series[0]["date"], "last_date": last["date"],
            "latest_premium_pct": last["premium_pct"],
            "latest_nav_date": last.get("nav_date"),
            "latest_nav_lag_days": last.get("nav_lag_days"),
            "median_pct": q(vals, 0.50),
            "p05_pct": q(vals, 0.05), "p25_pct": q(vals, 0.25),
            "p75_pct": q(vals, 0.75), "p95_pct": q(vals, 0.95),
            "min_pct": lo["premium_pct"], "min_date": lo["date"],
            "max_pct": hi["premium_pct"], "max_date": hi["date"],
            "rank_of_latest": rank,
            "verdict": verdict,
            "n_clean": len(clean),
            "rank_of_latest_clean": rank_clean,
            "verdict_clean": verdict_clean,
            "n_gap_excluded": len(vals) - len(clean),
            "gap_excluded_by_calendar": gaps,
            "latest_nav_is_carry": last.get("nav_date") in carry,
            "rulers_disagree": bool(verdict_clean and verdict_clean != verdict)}


def lag_ladder(prices, navs, lags=(1, 2, 3)):
    """How much the reading moves when the NAV stamp is taken one/two steps earlier."""
    rows = []
    for k in lags:
        s = premium_series(prices, navs, lag=k)
        if not s:
            continue
        rows.append({"lag": k, "nav_date": s[-1]["nav_date"],
                     "nav_lag_days": s[-1]["nav_lag_days"],
                     "latest_premium_pct": s[-1]["premium_pct"]})
    spread = None
    if len(rows) >= 2:
        vals = [r["latest_premium_pct"] for r in rows]
        spread = max(vals) - min(vals)
    return {"ladder": rows, "spread_pp": spread}


def revert_cost(amount_cny, latest_pct, median_pct):
    """What the sheet would lose if this leg's premium reverted to its own median."""
    if amount_cny is None or latest_pct is None or median_pct is None:
        return None
    return amount_cny * (1.0 - (1.0 + median_pct / 100.0) / (1.0 + latest_pct / 100.0))


def latest_ticket():
    if not os.path.isdir(TICKET_DIR):
        return None, None
    names = sorted(n for n in os.listdir(TICKET_DIR)
                   if n.startswith("TICKET-") and n.endswith(".json"))
    if not names:
        return None, None
    path = os.path.join(TICKET_DIR, names[-1])
    with open(path, encoding="utf-8") as f:
        return path, json.load(f)


def latest_premium_face():
    if not os.path.isdir(OUT_DIR):
        return None, None
    names = sorted(n for n in os.listdir(OUT_DIR)
                   if n.startswith("PREMIUM-") and n.endswith(".json")
                   and n[8:12].isdigit())
    if not names:
        return None, None
    path = os.path.join(OUT_DIR, names[-1])
    with open(path, encoding="utf-8") as f:
        return path, json.load(f)


def gate(ticket, face, prices_by_code):
    """Reconcile the panel with the published spot board before this face may speak."""
    fails = []
    notes = []
    cny_forms = {}
    cny_tols = {}
    if not face:
        return {"ok": False, "fails": ["no premium face"]}
    session = str(face.get("session"))[:10]
    checked_price = checked_prem = checked_cny = 0
    for leg in face.get("legs", []):
        code = str(leg.get("symbol"))
        px = prices_by_code.get(code) or {}
        if session in px and leg.get("price"):
            rel = abs(px[session] / float(leg["price"]) - 1.0)
            if rel > PRICE_TOL:
                fails.append("price panel %s %s=%.4f vs board %.4f (%.2f%%)"
                             % (code, session, px[session], float(leg["price"]),
                                rel * 100.0))
            checked_price += 1
        if leg.get("price") and leg.get("iopv") and leg.get("premium_pct") is not None:
            recomputed = (float(leg["price"]) / float(leg["iopv"]) - 1.0) * 100.0
            if abs(recomputed - float(leg["premium_pct"])) > PREM_TOL_PP + 1e-9:
                fails.append("published premium %s %.4f vs price/iopv %.4f"
                             % (code, float(leg["premium_pct"]), recomputed))
            checked_prem += 1
        if leg.get("over_nav_cny") is not None and leg.get("amount_cny") \
                and leg.get("premium_pct") is not None:
            amt = float(leg["amount_cny"])
            p = float(leg["premium_pct"]) / 100.0
            exact = amt * (1.0 - 1.0 / (1.0 + p))
            linear = amt * p
            pub = float(leg["over_nav_cny"])
            # 0.02 floor + the producer's own rounding of premium_pct to 4
            # decimals of a percent (a half step of PREM_HALF_STEP_P in p, times
            # the amount). Without the second term a correct board is refused.
            tol = CNY_TOL + abs(amt) * PREM_HALF_STEP_P
            cny_tols[code] = round(tol, 4)
            gap = abs(exact - linear)
            e_ok = abs(exact - pub) <= tol
            l_ok = abs(linear - pub) <= tol
            if e_ok and l_ok and gap <= tol:
                form = "either"   # indistinguishable at this amount -- say so
            elif e_ok:
                form = "exact"
            elif l_ok:
                form = "linear"
            else:
                form = None
            if form is None:
                fails.append("CNY identity %s %.2f vs exact %.2f / linear %.2f (tol %.2f)"
                             % (code, pub, exact, linear, tol))
            else:
                # the two forms differ by amt*p^2/(1+p): disclose it, do not smooth it
                if form == "linear" and gap > 0.5:
                    notes.append("CNY figure %s is the linear amt*p form; at %.2f%% the "
                                 "exact amt*p/(1+p) differs by CNY %.2f"
                                 % (code, p * 100.0, gap))
                cny_forms[code] = form
            checked_cny += 1
    if checked_price == 0:
        fails.append("no leg could be compared against the board (session %s)" % session)
    return {"ok": not fails, "fails": fails, "notes": notes,
            "cny_identity_forms": cny_forms,
            "cny_tolerance_cny": cny_tols,
            "session": session,
            "checked_price": checked_price, "checked_premium": checked_prem,
            "checked_cny_identity": checked_cny,
            "tolerances": {"price_rel": PRICE_TOL, "premium_pp": PREM_TOL_PP,
                           "cny": CNY_TOL,
                           "prem_half_step_p": PREM_HALF_STEP_P}}


def build(ticket, face, fetch=True, today=None):
    order = (ticket.get("ticket") or {}).get("order") or []
    prices_by_code = {}
    legs = []
    hist_rows = []
    for o in order:
        code = str(o.get("symbol"))
        px = load_prices(code) or {}
        prices_by_code[code] = px
        navs, nav_status = load_nav(code, fetch=fetch, today=today)
        ser = premium_series(px, navs, lag=1)
        st = stats(ser)
        lad = lag_ladder(px, navs)
        st.update({"symbol": code, "class": o.get("class"),
                   "amount_cny": o.get("amount"), "panel_price": o.get("price"),
                   "nav_source": nav_status,
                   "n_nav_rows": len(navs),
                   "nav_tail": navs[-30:],
                   "lag_ladder": lad["ladder"], "lag_spread_pp": lad["spread_pp"]})
        st["revert_to_median_cny"] = revert_cost(
            o.get("amount"), st.get("latest_premium_pct"), st.get("median_pct"))
        legs.append(st)
        for r in ser:
            hist_rows.append((r["date"], code, r["close"], r["nav_date"], r["nav"],
                              r["premium_pct"]))
    g = gate(ticket, face, prices_by_code)
    priced = [l for l in legs if l.get("revert_to_median_cny") is not None]
    book_amount = sum(float(l["amount_cny"] or 0) for l in legs)
    total_revert = sum(l["revert_to_median_cny"] for l in priced) if priced else None
    over_median = [l for l in priced if l.get("rank_of_latest") is not None
                   and l["rank_of_latest"] >= TAIL]
    cal = _calendars()
    disagree = [l["symbol"] for l in legs if l.get("rulers_disagree")]
    out = {
        "artifact": "etf_book_premium_percentile",
        "machine": "bm-c",
        "evidence_cutoff": max((l.get("last_date") or "") for l in legs) or None,
        "ticket": {"path": None,
                   "as_of": ticket.get("as_of"),
                   "book_amount_cny": book_amount},
        "ruler": {
            "measure": "panel close / the newest unit NAV stamped strictly before that "
                       "close - 1",
            "not_the_same_as": "IOPV (intraday basket value) -- the board's 23.64% and "
                               "this face's reading are two rulers, printed side by side",
            "no_lookahead": "a NAV stamped on the price bar itself is never used",
            "rank_of_latest": "share of readable sessions whose premium is below today's",
            "rank_of_latest_clean": "the same share over the sessions that carry a NEW "
                                    "valuation -- a NAV stamp that repeats its "
                                    "predecessor's number is dropped, because that row's "
                                    "'premium' is the price moving against a valuation that "
                                    "could not",
        },
        "calendars": {
            "source": CAL_SOURCE,
            "us": "rule-derived (New York)" if cal.get("us") else "unavailable",
            "hk": "measured (HSI series)" if cal.get("hk") else "unavailable",
            "hk_status": cal.get("hk_status"),
            "error": cal.get("error"),
        },
        "legs": legs,
        "summary": {
            "legs": len(legs), "priced_legs": len(priced),
            "at_or_above_p90": [l["symbol"] for l in over_median],
            "revert_to_own_median_cny": total_revert,
            "book_amount_cny": book_amount,
            "n_gap_excluded_total": sum(int(l.get("n_gap_excluded") or 0) for l in legs),
            "n_sessions_total": sum(int(l.get("n") or 0) for l in legs),
            "rulers_disagree": disagree,
            "sentence": None,
        },
        "gate": g,
        "caveats": [
            "NAV is as-collected: a later pull may restate it, and a restated NAV moves "
            "the whole series by that revision (the raw cache is regenerable, the "
            "published history CSV is this session's reading).",
            "A cross-border (QDII) NAV is stamped on the overseas close, so part of every "
            "reading is the overseas move since that stamp -- the lag ladder prices how "
            "much of the reading that offset can shift.",
            "A限购 fund can stay expensive for years: a high percentile is a reading, "
            "not a sell order.",
            "A rank counts sessions, and a session whose NAV stamp repeats the previous "
            "valuation carries no new number -- the second rank drops those rows and the "
            "calendars in hand only explain them.",
            "The second rank does NOT drop a session whose NAV moved only slightly (a "
            "distribution or a share conversion moves the number without moving the "
            "basket). Those rows are measured on their own face "
            "(results/etf_premium/PREMIUM-SUBSCRIPTION.json), which counts the one-row "
            "suspension runs; this face does not re-decide them.",
            "The panel close is not the price the sheet pays; the sheet pays the next "
            "open plus slippage (tracked on the punctuality faces).",
        ],
    }
    out["summary"]["sentence"] = summary_sentence(out)
    return out, hist_rows


def summary_sentence(out):
    s = out["summary"]
    if not s["priced_legs"]:
        return "UNPRICED: no leg has enough disclosed NAV history to rank its premium."
    names = [l for l in out["legs"] if l.get("verdict") in
             ("AT_RECORD_HIGH", "UPPER_TAIL")]
    if names:
        head = "、".join("%s(%s, 第%s%%)" % (l["symbol"], l["verdict"],
                                             _fmt(l.get("rank_of_latest")))
                        for l in names)
    else:
        head = "没有一只站在自己历史的前 10%"
    tail = ""
    if s["revert_to_own_median_cny"] is not None:
        tail = ("；若这些腿各自回到自己的中位溢价，这张单值 ￥%s"
                % _fmt_money(s["revert_to_own_median_cny"]))
    # r1566: the second ruler is only worth printing if it can change the answer, so the
    # producer's own sentence says whether it did -- and it says it from the counts.
    gap = ""
    n_gap = int(s.get("n_gap_excluded_total") or 0)
    if n_gap:
        dis = s.get("rulers_disagree") or []
        gap = ("；把 %d 个「净值戳沿用上一日数字、分母当天不可能动」的会话剔掉后，"
               % n_gap)
        gap += ("判词改变的腿：%s" % "、".join(dis) if dis
                else "没有一只腿的判词改变")
    return "%s%s%s" % (head, tail, gap)


def _fmt(x):
    return "-" if x is None else "%.0f" % (100.0 * float(x))


def _fmt_money(x):
    return "%.0f" % float(x)


def write_hist(hist_rows):
    os.makedirs(OUT_DIR, exist_ok=True)
    tmp = HIST + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="\n") as f:
        f.write("date,symbol,close,nav_date,nav,premium_pct\n")
        for d, c, cl, nd, nav, pr in sorted(hist_rows):
            f.write("%s,%s,%.4f,%s,%.6f,%.6f\n" % (d, c, cl, nd, nav, pr))
    os.replace(tmp, HIST)


def read_hist():
    rows = []
    if not os.path.exists(HIST):
        return rows
    with open(HIST, encoding="utf-8") as f:
        for line in f:
            p = line.strip().split(",")
            if len(p) < 6 or p[0] == "date":
                continue
            rows.append({"date": p[0], "symbol": p[1], "close": float(p[2]),
                         "nav_date": p[3], "nav": float(p[4]),
                         "premium_pct": float(p[5])})
    return rows


def run(fetch=True):
    path, ticket = latest_ticket()
    if not ticket:
        print("no ticket to price")
        return 2
    fpath, face = latest_premium_face()
    today = None
    today = str(os.environ.get("BIGMONEY_TODAY") or "") or None
    out, hist = build(ticket, face, fetch=fetch, today=today)
    out["ticket"]["path"] = os.path.relpath(path, ROOT)
    out["premium_face"] = os.path.relpath(fpath, ROOT) if fpath else None
    if not out["gate"]["ok"]:
        print(json.dumps({"gate": out["gate"]}, ensure_ascii=False, indent=1))
        print("REFUSING TO PUBLISH: the panel does not reconcile with the published board")
        return 2
    write_hist(hist)
    os.makedirs(OUT_DIR, exist_ok=True)
    tmp = OUT + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="\n") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
        f.write("\n")
    os.replace(tmp, OUT)
    print(json.dumps({"evidence_cutoff": out["evidence_cutoff"],
                      "legs": {l["symbol"]: [l.get("verdict"),
                                             _round(l.get("latest_premium_pct")),
                                             _round(l.get("median_pct")),
                                             _fmt(l.get("rank_of_latest"))]
                               for l in out["legs"]},
                      "revert_cny": _round(out["summary"]["revert_to_own_median_cny"]),
                      "sentence": out["summary"]["sentence"]},
                     ensure_ascii=False, indent=1))
    return 0


def _round(x):
    return None if x is None else round(float(x), 3)


def check():
    """Every claim on the face is re-derived from the face's own published rows."""
    if not os.path.exists(OUT):
        print("no face to check")
        return 2
    with open(OUT, encoding="utf-8") as f:
        out = json.load(f)
    hist = read_hist()
    fails = []
    for leg in out["legs"]:
        rows = [h for h in hist if h["symbol"] == leg["symbol"]]
        st = stats(rows)
        for k in ("n", "verdict", "median_pct", "latest_premium_pct", "min_pct",
                  "max_pct", "rank_of_latest_clean", "verdict_clean",
                  "n_clean", "n_gap_excluded"):
            if k in ("median_pct", "latest_premium_pct", "min_pct",
                     "max_pct", "rank_of_latest_clean"):
                a, b = leg.get(k), st.get(k)
                if a is None or b is None:
                    if a is not b:
                        fails.append("%s %s: face %r vs recomputed %r"
                                     % (leg["symbol"], k, a, b))
                    continue
                if abs(a - b) > 1e-6:
                    fails.append("%s %s: face %.6f vs recomputed %s"
                                 % (leg["symbol"], k, a, b))
            elif leg.get(k) != st.get(k):
                fails.append("%s %s: face %r vs recomputed %r"
                             % (leg["symbol"], k, leg.get(k), st.get(k)))
        # conservation: every readable session is either in the clean ruler or dropped for
        # a named closure -- a reader must not have to add up two numbers that overlap
        if (leg.get("n_clean") is not None and leg.get("n_gap_excluded") is not None
                and leg.get("n") is not None
                and int(leg["n_clean"]) + int(leg["n_gap_excluded"]) != int(leg["n"])):
            fails.append("%s clean+excluded %r+%r != n %r"
                         % (leg["symbol"], leg["n_clean"], leg["n_gap_excluded"],
                            leg["n"]))
        for r in rows:
            if r["nav_date"] >= r["date"]:
                fails.append("%s used a NAV stamped on or after the close (%s)"
                             % (leg["symbol"], r["date"]))
        # the lag ladder must be re-derivable from the published NAV stamps
        nav_tail = leg.get("nav_tail") or []
        prices_map = {r["date"]: r["close"] for r in rows}
        for step in leg.get("lag_ladder") or []:
            k = int(step["lag"])
            s = premium_series(prices_map, nav_tail, lag=k)
            if not s:
                fails.append("%s lag %d not re-derivable" % (leg["symbol"], k))
                continue
            if abs(s[-1]["premium_pct"] - step["latest_premium_pct"]) > 1e-6:
                fails.append("%s lag %d: face %.6f vs recomputed %.6f"
                             % (leg["symbol"], k, step["latest_premium_pct"],
                                s[-1]["premium_pct"]))
    if not (out.get("gate") or {}).get("ok"):
        fails.append("the gate block does not say ok")
    total = 0.0
    seen = 0
    for leg in out["legs"]:
        if leg.get("revert_to_median_cny") is None:
            continue
        rc = revert_cost(leg["amount_cny"], leg["latest_premium_pct"],
                         leg["median_pct"])
        if abs(rc - leg["revert_to_median_cny"]) > 1e-6:
            fails.append("%s revert cost: face %.6f vs %.6f"
                         % (leg["symbol"], leg["revert_to_median_cny"], rc))
        total += rc
        seen += 1
    pub = out["summary"]["revert_to_own_median_cny"]
    if seen and (pub is None or abs(pub - total) > 1e-6):
        fails.append("summary revert total: face %r vs %.6f" % (pub, total))
    if out["summary"]["sentence"] != summary_sentence(out):
        fails.append("summary sentence is not the one its own rows derive")
    print("check: %s (%d legs, %d observations)"
          % ("OK" if not fails else "FAIL", len(out["legs"]), len(hist)))
    for e in fails[:10]:
        print("  ", e)
    return 0 if not fails else 1


def selftest():
    ok = tot = 0
    errs = []

    def chk(cond, what):
        nonlocal ok, tot
        tot += 1
        if cond:
            ok += 1
        else:
            errs.append(what)

    px = {"2026-01-05": 1.10, "2026-01-06": 1.20, "2026-01-07": 1.00}
    navs = [{"date": "2026-01-02", "nav": 1.00},
            {"date": "2026-01-05", "nav": 1.00},
            {"date": "2026-01-06", "nav": 1.00}]

    s = premium_series(px, navs, lag=1)
    chk([r["date"] for r in s] == ["2026-01-05", "2026-01-06", "2026-01-07"],
        "a NAV stamped before the close is usable")
    chk(abs(s[0]["premium_pct"] - 10.0) < 1e-9,
        "the 01-05 close divides the 01-05 stamp? no -- the newest stamp BEFORE it")
    chk(s[0]["nav_date"] == "2026-01-02",
        "no look-ahead: the same-day NAV is skipped")
    chk(s[2]["nav_date"] == "2026-01-06" and abs(s[2]["premium_pct"]) < 1e-9,
        "the last bar uses the newest NAV before it")

    flat = [{"date": "2026-01-%02d" % i, "close": 1.0, "nav_date": "2026-01-01",
             "nav": 1.0, "premium_pct": 0.5, "nav_lag_days": 1} for i in range(1, 90)]
    st = stats(flat)
    chk(st["verdict"] == "AT_RECORD_HIGH" and abs(st["median_pct"] - 0.5) < 1e-12,
        "a flat series is its own record, not an error")

    up = [{"date": "2026-02-%02d" % i, "close": 1.0, "nav_date": "x", "nav": 1.0,
           "premium_pct": float(i), "nav_lag_days": 1} for i in range(1, 90)]
    st = stats(up)
    chk(st["verdict"] == "AT_RECORD_HIGH" and st["rank_of_latest"] < 1.0,
        "the newest reading of a rising series is its record without a rank of 1")

    mid = [{"date": "2026-03-%02d" % i, "close": 1.0, "nav_date": "x", "nav": 1.0,
            "premium_pct": float(i), "nav_lag_days": 1} for i in range(1, 90)]
    mid.append({"date": "2026-04-01", "close": 1.0, "nav_date": "x", "nav": 1.0,
                "premium_pct": 45.0, "nav_lag_days": 1})
    st = stats(mid)
    chk(st["verdict"] == "ORDINARY" and st["rank_of_latest"] < TAIL,
        "a middle reading is ORDINARY, not a tail")

    top = [{"date": "2026-03-%02d" % i, "close": 1.0, "nav_date": "x", "nav": 1.0,
            "premium_pct": float(i), "nav_lag_days": 1} for i in range(1, 90)]
    top.append({"date": "2026-04-01", "close": 1.0, "nav_date": "x", "nav": 1.0,
                "premium_pct": 85.0, "nav_lag_days": 1})
    chk(stats(top)["verdict"] == "UPPER_TAIL", "the 95th percentile is UPPER_TAIL")
    chk(stats([])["verdict"] == "UNPRICED", "no history is UNPRICED, never a zero")
    chk(stats(flat[:10])["verdict"] == "THIN",
        "fewer than %d observations has no scale" % THIN_N)

    lad = lag_ladder(px, navs)
    chk(len(lad["ladder"]) >= 2 and lad["spread_pp"] is not None,
        "the lag ladder needs two stamps to print a spread")
    chk(abs(lad["ladder"][0]["latest_premium_pct"] - s[-1]["premium_pct"]) < 1e-9,
        "lag 1 on the ladder equals the published reading")

    chk(abs(revert_cost(100.0, 20.0, 10.0) - 100.0 * (1 - 1.10 / 1.20)) < 1e-9,
        "reverting to the median is priced on the amount paid, not on NAV")
    chk(revert_cost(None, 1.0, 1.0) is None, "a missing amount is None, not a zero")

    face = {"session": "2026-01-05", "legs": [
        {"symbol": "159501", "price": 1.10, "iopv": 1.00, "premium_pct": 10.0,
         "amount_cny": 100.0, "over_nav_cny": 100.0 * (1 - 1 / 1.10)}]}
    g = gate(ticket={}, face=face, prices_by_code={"159501": px})
    chk(g["ok"], "a consistent board and panel pass the gate")
    bad = {"session": "2026-01-05", "legs": [dict(face["legs"][0], price=1.30)]}
    chk(not gate(ticket={}, face=bad,
                 prices_by_code={"159501": px})["ok"],
        "a panel that disagrees with the board blocks publication")
    bad2 = {"session": "2026-01-05", "legs": [
        dict(face["legs"][0], premium_pct=12.0)]}
    chk(not gate(ticket={}, face=bad2,
                 prices_by_code={"159501": px})["ok"],
        "a premium that is not price/iopv blocks publication")
    chk(not gate(ticket={}, face=None, prices_by_code={})["ok"],
        "no face at all blocks publication")

    # The board publishes premium_pct to 4 decimals of a percent. A reader that
    # re-derives the CNY figure from that published number can be off by half of
    # the last digit times the amount -- 0.039 CNY on a 78.5k order. That used to
    # be refused as "the panel does not reconcile with the board".
    def _qbadge(extra=0.0, amt=78540.0):
        return {"session": "2026-01-05", "legs": [
            {"symbol": "513690", "price": 1.155, "iopv": 1.153,
             "premium_pct": 0.1735, "amount_cny": amt,
             "over_nav_cny": round(amt * 0.0017354, 2) + extra}]}
    qpx = {"513690": {"2026-01-05": 1.155}}
    gq = gate(ticket={}, face=_qbadge(), prices_by_code=qpx)
    chk(gq["ok"], "a CNY figure carrying the producer's 4-decimal rounding passes")
    chk(gq["cny_identity_forms"].get("513690") in ("exact", "linear", "either"),
        "the form is still named when it passes")
    chk(gq["cny_tolerance_cny"].get("513690", 0) > CNY_TOL,
        "the amount-scaled tolerance is printed on the face, not hidden")
    chk(not gate(ticket={}, face=_qbadge(extra=0.30), prices_by_code=qpx)["ok"],
        "a CNY figure off by 0.30 at the same amount is still refused")
    small = _qbadge(extra=0.04, amt=100.0)
    small["legs"][0]["over_nav_cny"] = round(100.0 * 0.0017354, 2) + 0.04
    chk(not gate(ticket={}, face=small, prices_by_code=qpx)["ok"],
        "the same 0.04 gap on a 100 CNY order is refused -- scaling is not loosening")
    tiny = {"session": "2026-01-05", "legs": [
        {"symbol": "512040", "price": 1.198, "iopv": 1.1982,
         "premium_pct": -0.0167, "amount_cny": 78588.8, "over_nav_cny": -13.12}]}
    gt = gate(ticket={}, face=tiny, prices_by_code={"512040": {"2026-01-05": 1.198}})
    chk(gt["ok"] and gt["cny_identity_forms"].get("512040") == "either",
        "when the two forms sit inside the tolerance of each other the face says 'either'")

    # ---- r1566: the second ruler -------------------------------------------------------
    # A rank counts sessions, and not every session carries a new valuation. These legs pin
    # that a stamp repeating its predecessor's number leaves the clean ruler, that the
    # calendars only explain those rows (a shut market is named, an unexplained carry is
    # said to be unexplained), that both words are published when they disagree, and that a
    # clean ruler without a scale says nothing rather than "unchanged".
    chk(valuation_gap("2026-07-02", "2026-07-06") == "us",
        "a New York closure inside the window is named, not silently counted")
    chk(valuation_gap("2026-06-01", "2026-06-02") is None,
        "an ordinary overnight gap is clean")
    base = [{"date": "d%03d" % i, "close": 1.0, "nav_date": "n%03d" % i,
             "nav": 1.0 + 0.001 * i, "premium_pct": float(i), "nav_lag_days": 1}
            for i in range(1, 71)]
    # one stamp that carries the previous number forward, then twenty closes that all read
    # against it -- the shut-market shape, with no calendar consulted by the filter
    anchor = {"date": "2026-07-06", "close": 1.0, "nav_date": "2026-07-01",
              "nav": 1.200, "premium_pct": 0.0, "nav_lag_days": 3}
    shut = [{"date": "2026-07-07", "close": 1.0, "nav_date": "2026-07-02",
             "nav": 1.200, "premium_pct": 95.0 + i, "nav_lag_days": 4}
            for i in range(20)]
    today = {"date": "2026-07-08", "close": 1.0, "nav_date": "2026-07-08",
             "nav": 1.210, "premium_pct": 90.0, "nav_lag_days": 1}
    two = stats(base + [anchor] + shut + [today])
    chk(two["n_gap_excluded"] == 20 and two["n_clean"] == 72,
        "the carried-forward sessions leave the clean ruler (%r of %r)"
        % (two["n_gap_excluded"], two["n"]))
    chk(two["n_clean"] + two["n_gap_excluded"] == two["n"],
        "every readable session sits in exactly one of the two rulers")
    chk(two["gap_excluded_by_calendar"] == {"us": 20},
        "the calendar explains the dropped rows instead of deciding them (%r)"
        % (two["gap_excluded_by_calendar"],))
    chk(two["verdict"] == "ORDINARY" and two["verdict_clean"] == "AT_RECORD_HIGH",
        "the two rulers can disagree, and the face prints both words")
    chk(two["rulers_disagree"] is True,
        "a disagreement is flagged, not averaged into one number")
    chk(two["latest_nav_is_carry"] is False,
        "a carried-forward NAV under today's reading is named when it happens")
    unexp = stats(base + [anchor, {"date": "2026-08-03", "close": 1.0,
                                   "nav_date": "zzz", "nav": 1.200,
                                   "premium_pct": 30.0, "nav_lag_days": 1},
                           {"date": "2026-08-04", "close": 1.0,
                            "nav_date": "zzz2", "nav": 1.220,
                            "premium_pct": 12.0, "nav_lag_days": 1}])
    chk(unexp["gap_excluded_by_calendar"] == {"unexplained": 1},
        "a carry no calendar explains says so instead of borrowing a cause (%r)"
        % (unexp["gap_excluded_by_calendar"],))
    thin_clean = stats(base[:5] + [anchor] + shut + [today])
    chk(thin_clean["verdict_clean"] is None and thin_clean["rulers_disagree"] is False,
        "a clean ruler without a scale says nothing rather than 'unchanged'")
    s_dis = summary_sentence({"summary": {"priced_legs": 1, "legs": 1,
                                          "revert_to_own_median_cny": None,
                                          "n_gap_excluded_total": 20,
                                          "rulers_disagree": ["159655"]},
                              "legs": [{"symbol": "159655", "verdict": "ORDINARY",
                                        "rank_of_latest": 0.5}]})
    chk("159655" in s_dis and "20" in s_dis,
        "the producer's own sentence names the dropped sessions and the changed leg")

    print("selftest %d/%d" % (ok, tot))
    for e in errs:
        print("  FAIL:", e)
    return 0 if not errs else 1


def ticket_check():
    """The ticket is the face a reader executes off. Its own percentile block must
    be the one this face just published -- same session, nothing missing, and the
    same money re-derived from the face's own legs."""
    if not os.path.exists(OUT):
        print("ticket-check: no percentile face to compare")
        return 2
    with open(OUT, encoding="utf-8") as f:
        out = json.load(f)
    path, tk = latest_ticket()
    if not tk:
        print("ticket-check: no ticket to compare")
        return 2
    pr = (tk.get("premium") or {})
    fails = []
    face_ds = str(out.get("evidence_cutoff") or "")[:10]
    tk_ds = str(pr.get("pct_face_asof") or "")[:10]
    if tk_ds != face_ds:
        fails.append("ticket reads the %s face, this face is %s -- stale ticket"
                     % (tk_ds or "none", face_ds or "none"))
    missing = pr.get("pct_missing_legs") or []
    if missing:
        fails.append("ticket has no percentile for %s" % ",".join(missing))
    face_rev = out["summary"]["revert_to_own_median_cny"]
    tk_rev = pr.get("pct_revert_cny")
    if face_rev is None and tk_rev not in (None, 0, 0.0):
        fails.append("ticket prints %.2f where the face has no total" % float(tk_rev or 0))
    elif face_rev is not None:
        if tk_rev is None or abs(float(tk_rev) - float(face_rev)) > 1e-6:
            fails.append("ticket money %r vs face %.6f" % (tk_rev, face_rev))
    by_code = {l["symbol"]: l for l in out["legs"]}
    for row in pr.get("rows") or []:
        leg = by_code.get(str(row.get("symbol")))
        if not leg:
            fails.append("%s is on the ticket but not on the face" % row.get("symbol"))
            continue
        if row.get("rank_verdict") != leg.get("verdict"):
            fails.append("%s verdict %r vs face %r"
                         % (row.get("symbol"), row.get("rank_verdict"), leg.get("verdict")))
        a, b = row.get("rank"), leg.get("rank_of_latest")
        if (a is None) != (b is None) or (a is not None and abs(float(a) - float(b)) > 1e-9):
            fails.append("%s percentile %r vs face %r" % (row.get("symbol"), a, b))
    print("ticket-check: %s (%s, %d legs, missing=%d)"
          % ("OK" if not fails else "FAIL", os.path.basename(path),
             len(pr.get("rows") or []), len(missing)))
    for e in fails[:10]:
        print("  ", e)
    return 0 if not fails else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["run", "check", "selftest", "ticket-check"])
    ap.add_argument("--no-fetch", action="store_true")
    a = ap.parse_args()
    if a.mode == "selftest":
        return selftest()
    if a.mode == "check":
        return check()
    if a.mode == "ticket-check":
        return ticket_check()
    return run(fetch=not a.no_fetch)


if __name__ == "__main__":
    sys.exit(main())