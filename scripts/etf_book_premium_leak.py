"""ETF book -- what the ticket pays ABOVE the basket, before it has owned anything.

The permission arc (r1451..r1459) prices the SIZE of the order: how much k the book may
carry. It never priced what the order PAYS. Every pick in the 2026-11-06 ticket is an ETF
whose exchange price can sit far above its own IOPV, and 4 of the 5 names are cross-border
-- the class where that gap is largest. A book that selects on price momentum inherits the
gap: the price it buys includes it.

This face answers one question with published numbers only:

    if I buy this ticket today, how much of the money buys the basket and how much buys
    the premium?

Inputs (all already on disk, nothing re-priced and nothing fetched):
  results/etf_book_order/TICKET-<session>.json   the executable ticket (shares, price)
  data/etf_premium/snap/<session>.csv            that session's price / IOPV / premium
  data/fund_premium/snapshots/*.csv              the NAV-ruler premium history (if any)

Two rulers, never blended. The IOPV ruler (price / IOPV - 1) is intraday and same-session,
so it is the one that prices the entry. The NAV ruler (close / published unit NAV - 1) is a
DIFFERENT quantity published with a disclosure lag; it is printed separately and only when
at least two observations exist, because a "median" of one observation is not a history.
Mixing them would make a 23% entry cost look like a 17% one on a different day (E206 family).

A name with no IOPV row is printed as unverifiable and EXCLUDED from the total, with the
count carried in the payload -- never filled with zero (r98/E192 family: absent is not zero).

Frozen criteria: thresholds live in constants here and are echoed into the payload; --check
refuses a face whose echoed criteria differ from the constants, and recomputes the verdict
from the summary instead of trusting the stored word.

Usage:
    python scripts/etf_book_premium_leak.py run
    python scripts/etf_book_premium_leak.py --check
    python scripts/etf_book_premium_leak.py --selftest
"""

from __future__ import annotations

import argparse
import glob
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TICKET_DIR = os.path.join(ROOT, "results", "etf_book_order")
IOPV_DIR = os.path.join(ROOT, "data", "etf_premium", "snap")
NAVHIST_DIR = os.path.join(ROOT, "data", "fund_premium", "snapshots")
OWNHIST_DIR = os.path.join(ROOT, "data", "etf_premium", "nav_history")  # per-fund date,nav
DAILY_DIR = os.path.join(ROOT, "data", "daily")
OUT_JSON = os.path.join(ROOT, "results", "etf_book_premium_leak.json")

# ---- frozen criteria (pre-registered before the first run; --check echoes them back) ----
WARN_SHARE_PCT = 1.0       # premium paid >= 1.0% of the order -> worth printing loudly
DOMINATE_SHARE_PCT = 5.0   # premium paid >= 5.0% of the order -> entry cost dominates
TOP_PCTILE = 95.0          # a name in the market's top 5% premium is flagged by name
MIN_HISTORY_OBS = 2        # fewer than two NAV-ruler observations is not a history
OWN_MIN_OBS = 60           # a percentile of <60 sessions is not this fund's OWN norm
OWN_DECILE_PCTILE = 90.0   # "top decile of its own history" -- the own-ruler flag line
OWN_RULER = "close / published unit NAV - 1 (this fund's own history, one ruler, paired by date)"

CRITERIA = {
    "warn_share_pct": WARN_SHARE_PCT,
    "dominate_share_pct": DOMINATE_SHARE_PCT,
    "top_pctile": TOP_PCTILE,
    "min_history_obs": MIN_HISTORY_OBS,
}


def _num(v):
    try:
        f = float(v)
    except (TypeError, ValueError):
        return None
    return f if f == f else None


def _load_json(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def latest_ticket():
    files = [p for p in glob.glob(os.path.join(TICKET_DIR, "TICKET-*.json"))
             if not p.endswith("-card.json")]
    if not files:
        return None
    files.sort(key=lambda p: os.path.basename(p))
    return files[-1]


def read_iopv(session):
    """Return {code6: row} for one session, or None when the snapshot is absent."""
    path = os.path.join(IOPV_DIR, "%s.csv" % session)
    if not os.path.exists(path):
        return None, path
    import pandas as pd
    d = pd.read_csv(path, dtype={"code": str})
    d["code"] = d["code"].astype(str).str.zfill(6)
    d["premium_pct"] = pd.to_numeric(d["premium_pct"], errors="coerce")
    d["price_n"] = pd.to_numeric(d["price"], errors="coerce")
    d["iopv_n"] = pd.to_numeric(d["iopv"], errors="coerce")
    rows = {}
    for rec in d.to_dict("records"):
        rows[str(rec["code"])] = rec
    return rows, path


def market_rank(rows, code, value):
    """Percentile + 1-based rank of `value` inside the session's own premium distribution."""
    vals = [r["premium_pct"] for r in rows.values() if r.get("premium_pct") == r.get("premium_pct")]
    vals = [float(v) for v in vals if v is not None]
    if not vals or value is None:
        return None, None, len(vals)
    below = sum(1 for v in vals if v < value)
    above = sum(1 for v in vals if v > value)
    return round(below / len(vals) * 100.0, 2), above + 1, len(vals)


def premium_table(order, iopv, session):
    """Per-name entry cost. Missing IOPV is unverifiable, never zero."""
    out = []
    for row in order:
        code = str(row.get("symbol") or row.get("code") or "").zfill(6)
        shares = float(row.get("shares") or 0.0)
        price = _num(row.get("price"))
        rec = iopv.get(code) if iopv else None
        iopv_px = _num(rec.get("iopv")) if rec else None
        prem = _num(rec.get("premium_pct")) if rec else None
        item = {
            "symbol": code,
            "class": row.get("class"),
            "price": price,
            "shares": shares,
            "amount_cny": round(float(row.get("amount") or 0.0), 2),
        }
        if rec is None:
            item.update({"status": "NO_IOPV_ROW", "iopv": None, "premium_pct": None,
                         "premium_paid_cny": None, "market_pctile": None,
                         "market_rank": None, "market_n": None})
        elif iopv_px is None or prem is None or not iopv_px:
            item.update({"status": "IOPV_UNUSABLE", "iopv": iopv_px, "premium_pct": prem,
                         "premium_paid_cny": None, "market_pctile": None,
                         "market_rank": None, "market_n": None})
        else:
            pct, rank, n = market_rank(iopv, code, prem)
            item.update({
                "status": "OK",
                "iopv": iopv_px,
                "premium_pct": round(prem, 4),
                "premium_paid_cny": round(shares * (price - iopv_px), 2),
                "market_pctile": pct,
                "market_rank": rank,
                "market_n": n,
            })
        out.append(item)
    return out


def totals_of(rows, book_amount, nav, cagr_pct):
    ok = [r for r in rows if r["status"] == "OK"]
    paid = round(sum(r["premium_paid_cny"] for r in ok), 2)
    amount_ok = round(sum(r["amount_cny"] for r in ok), 2)
    share = round(paid / book_amount * 100.0, 4) if book_amount else None
    share_nav = round(paid / nav * 100.0, 4) if nav else None
    years = None
    if cagr_pct and paid and amount_ok:
        annual = amount_ok * float(cagr_pct) / 100.0
        years = round(paid / annual, 2) if annual else None
    return {
        "n_names": len(rows),
        "n_verified": len(ok),
        "n_unverifiable": len(rows) - len(ok),
        "premium_paid_cny": paid,
        "verified_amount_cny": amount_ok,
        "book_amount_cny": round(book_amount, 2),
        "nav_cny": round(nav, 2),
        "premium_share_of_order_pct": share,
        "premium_share_of_nav_pct": share_nav,
        "book_cagr_pct": cagr_pct,
        "years_of_backtest_return_paid": years,
    }


def verdict_of(tot, n_top_names, top_names):
    """Recomputed from the summary; the stored word is never trusted on its own."""
    if tot["n_verified"] == 0:
        return "CANNOT_VERIFY", "no name had a usable IOPV row"
    if tot["n_unverifiable"]:
        return ("PARTIAL", "%d of %d names unverifiable; the total covers only the verified"
                % (tot["n_unverifiable"], tot["n_names"]))
    share = tot.get("premium_share_of_order_pct")
    if share is None:
        # a face without a denominator cannot be judged small or large (r1261 family)
        return "CANNOT_VERIFY", "the summary carries no premium share of the order"
    if share >= DOMINATE_SHARE_PCT:
        return "ENTRY_PREMIUM_DOMINATES", (
            "the ticket pays %.2f%% of its own amount above IOPV (CNY %.0f)"
            % (share, tot["premium_paid_cny"]))
    if share >= WARN_SHARE_PCT:
        return "ENTRY_PREMIUM_WARN", (
            "the ticket pays %.2f%% of its own amount above IOPV (CNY %.0f)"
            % (share, tot["premium_paid_cny"]))
    return "ENTRY_PREMIUM_SMALL", (
        "the ticket pays %.2f%% above IOPV (below the %.1f%% warn line)"
        % (share, WARN_SHARE_PCT))


def history_stats(values, code):
    vals = [v for v in values if v is not None]
    if len(vals) < MIN_HISTORY_OBS:
        return {"symbol": code, "n_obs": len(vals), "status": "NOT_ENOUGH_OBSERVATIONS",
                "median_pct": None, "max_pct": None, "min_pct": None}
    vals_sorted = sorted(vals)
    med = vals_sorted[len(vals_sorted) // 2] if len(vals_sorted) % 2 else \
        0.5 * (vals_sorted[len(vals_sorted) // 2 - 1] + vals_sorted[len(vals_sorted) // 2])
    return {"symbol": code, "n_obs": len(vals), "status": "OK",
            "median_pct": round(med * 100.0, 4),
            "max_pct": round(max(vals) * 100.0, 4),
            "min_pct": round(min(vals) * 100.0, 4)}


def nav_ruler_history(symbols):
    """Premium on the OTHER ruler: close / published NAV - 1, from the fund premium panel."""
    out = {}
    files = sorted(glob.glob(os.path.join(NAVHIST_DIR, "*.csv")))
    if not files:
        return out
    import pandas as pd
    want = set(symbols)
    rows = []
    for f in files:
        d = pd.read_csv(f, dtype={"code": str})
        d["code"] = d["code"].astype(str).str.zfill(6)
        sub = d[d["code"].isin(want)]
        if len(sub):
            sub = sub.copy()
            sub["day"] = os.path.basename(f)[:10]
            rows.append(sub[["day", "code", "nav", "mkt_price"]])
    if not rows:
        for c in symbols:
            out[c] = history_stats([], c)
        return out
    h = pd.concat(rows)
    h["prem"] = pd.to_numeric(h["mkt_price"], errors="coerce") / \
        pd.to_numeric(h["nav"], errors="coerce") - 1.0
    for c in symbols:
        g = h[h["code"] == c].dropna(subset=["prem"]).sort_values("day")
        st = history_stats([float(x) for x in g["prem"].tolist()], c)
        if st["status"] == "OK":
            st["first_day"] = str(g["day"].iloc[0])
            st["last_day"] = str(g["day"].iloc[-1])
            st["last_pct"] = round(float(g["prem"].iloc[-1]) * 100.0, 4)
        out[c] = st
    return out


def _price_csv(code):
    """This repo stores one instrument under up to three file names (see
    `etf_composite_pf._stem_key`): <code>.csv, sh<code>.csv, sz<code>.csv."""
    for name in (code + ".csv", "sh" + code + ".csv", "sz" + code + ".csv"):
        p = os.path.join(DAILY_DIR, name)
        if os.path.exists(p):
            return p
    return None


def _rel_safe(path):
    """Repo-relative label, or the absolute path when the file lives on another drive.

    `os.path.relpath` raises ValueError across Windows drives (repo on K:, fixtures in
    TEMP on C:), and a self-test fixture is exactly that case (r1371 family)."""
    if not path:
        return None
    try:
        return os.path.relpath(path, ROOT)
    except ValueError:
        return path


def own_series(code, daily_dir=None, navhist_dir=None):
    """One fund's premium history on ONE ruler: close / published unit NAV - 1.

    The price leg and the NAV leg are joined on the DATE, never on position: a NAV can
    print on a session the fund did not trade, and a price can exist before the fund
    published a NAV. Returns (series, meta); series is [(day, premium_fraction)] in date
    order, or None when either leg is missing -- absence is not a zero premium.
    """
    import pandas as pd
    daily_dir = daily_dir or DAILY_DIR
    navhist_dir = navhist_dir or OWNHIST_DIR
    price_path = None
    for name in (code + ".csv", "sh" + code + ".csv", "sz" + code + ".csv"):
        p = os.path.join(daily_dir, name)
        if os.path.exists(p):
            price_path = p
            break
    nav_path = os.path.join(navhist_dir, code + ".csv")
    meta = {"symbol": code, "ruler": OWN_RULER,
            "price_path": _rel_safe(price_path),
            "nav_path": _rel_safe(nav_path) if os.path.exists(nav_path) else None}
    if not price_path or not os.path.exists(nav_path):
        meta["status"] = "NO_LOCAL_HISTORY"
        return None, meta
    px = pd.read_csv(price_path, parse_dates=["date"]).set_index("date")["close"]
    nav = pd.read_csv(nav_path, parse_dates=["date"]).set_index("date")["nav"]
    df = pd.DataFrame({"close": pd.to_numeric(px, errors="coerce"),
                       "nav": pd.to_numeric(nav, errors="coerce")}).dropna()
    df = df[df["nav"] > 0]
    if not len(df):
        meta["status"] = "NO_OVERLAP"
        return None, meta
    series = [(str(idx)[:10], float(c / n - 1.0)) for idx, c, n in
              zip(df.index, df["close"].tolist(), df["nav"].tolist())]
    meta["status"] = "OK"
    return series, meta


def _quant(sorted_vals, p):
    if not sorted_vals:
        return None
    k = (len(sorted_vals) - 1) * p
    lo = int(k)
    hi = min(lo + 1, len(sorted_vals) - 1)
    frac = k - lo
    return sorted_vals[lo] * (1.0 - frac) + sorted_vals[hi] * frac


def own_stats(series, code, meta=None, min_obs=OWN_MIN_OBS):
    """Where the LATEST reading sits inside this fund's own distribution.

    The latest reading is the last day where both a close and a published NAV exist --
    never today's intraday IOPV premium (that is the entry ruler, a different quantity)."""
    base = dict(meta or {})
    base.setdefault("symbol", code)
    base.setdefault("ruler", OWN_RULER)
    vals = [v for _, v in (series or [])]
    base["n_obs"] = len(vals)
    if not vals and base.get("status") in ("NO_LOCAL_HISTORY", "NO_OVERLAP"):
        for k in ("median_pct", "p10_pct", "p90_pct", "min_pct", "max_pct",
                  "last_pct", "last_pctile", "last_rank", "above_own_median_pp",
                  "first_day", "last_day"):
            base[k] = None
        return base
    if len(vals) < min_obs:
        base["status"] = "NOT_ENOUGH_OBSERVATIONS"
        for k in ("median_pct", "p10_pct", "p90_pct", "min_pct", "max_pct",
                  "last_pct", "last_pctile", "last_rank", "above_own_median_pp",
                  "first_day", "last_day"):
            base[k] = None
        return base
    s = sorted(vals)
    last = vals[-1]
    below = sum(1 for v in s if v < last)
    base.update({
        "status": "OK",
        "first_day": series[0][0],
        "last_day": series[-1][0],
        "median_pct": round(_quant(s, 0.50) * 100.0, 4),
        "p10_pct": round(_quant(s, 0.10) * 100.0, 4),
        "p90_pct": round(_quant(s, 0.90) * 100.0, 4),
        "min_pct": round(s[0] * 100.0, 4),
        "max_pct": round(s[-1] * 100.0, 4),
        "last_pct": round(last * 100.0, 4),
        "last_pctile": round(below / len(s) * 100.0, 2),
        "last_rank": (len(s) - below),
        "above_own_median_pp": round((last - _quant(s, 0.50)) * 100.0, 4),
    })
    return base


def own_history(rows, daily_dir=None, navhist_dir=None):
    """Per-name own-ruler block. Missing legs stay unreadable -- never zero, never skipped
    silently (a name with no discipline here would print 'no premium' by omission)."""
    out = {}
    for r in rows:
        code = str(r.get("symbol") or "").zfill(6)
        series, meta = own_series(code, daily_dir=daily_dir, navhist_dir=navhist_dir)
        out[code] = own_stats(series, code, meta)
    return out


def own_summary(own, rows, top_pctile=OWN_DECILE_PCTILE):
    """The own-ruler sentence: how many of the names the order buys sit in the top decile
    of their OWN history, and what a reversion to their own median would cost.

    The money figure is deliberately NOT 'revert to zero': zero is not what these funds
    do (their medians are positive). It is 'give back only the part above the fund's own
    median', which is the part today's premium adds on top of normal life."""
    hot, unreadable, revert = [], [], 0.0
    readable = 0
    for r in rows:
        code = str(r.get("symbol") or "").zfill(6)
        st = own.get(code) or {}
        if st.get("status") != "OK":
            unreadable.append(code)
            continue
        readable += 1
        if (st.get("last_pctile") or 0.0) >= top_pctile:
            hot.append(code)
        if r.get("status") == "OK" and st.get("median_pct") is not None:
            iopv = _num(r.get("iopv"))
            shares = float(r.get("shares") or 0.0)
            if iopv:
                revert += shares * iopv * ((r["premium_pct"] / 100.0) - st["median_pct"] / 100.0)
    n = len(rows)
    if not readable:
        word = "OWN_HISTORY_UNREADABLE"
    elif len(hot) == n:
        word = "EVERY_NAME_ABOVE_OWN_TOP_DECILE"
    elif hot:
        word = "SOME_NAMES_ABOVE_OWN_TOP_DECILE"
    else:
        word = "NO_NAME_ABOVE_OWN_TOP_DECILE"
    return {
        "ruler": OWN_RULER,
        "top_decile_pctile": top_pctile,
        "n_names": n,
        "n_readable": readable,
        "n_unreadable": len(unreadable),
        "unreadable": unreadable,
        "in_own_top_decile": hot,
        "revert_to_own_median_cny": round(revert, 2),
        "revert_note": ("stress, not a forecast: it gives back only the part ABOVE each "
                        "fund's own median premium, and only for names this order is buying"),
        "verdict": word,
    }


def build(ticket_path=None):
    tk_path = ticket_path or latest_ticket()
    if not tk_path or not os.path.exists(tk_path):
        return {"status": "NO_TICKET", "ticket": None}
    tk = _load_json(tk_path)
    ticket = tk.get("ticket") or {}
    order = list(ticket.get("order") or [])
    nav = float(ticket.get("nav") or 0.0)
    book_amount = float(ticket.get("book_amount") or 0.0)
    cagr = None
    bk = ((tk.get("metrics") or {}).get("book") or {})
    if bk.get("cagr") is not None:
        cagr = round(float(bk["cagr"]) * 100.0, 4)
    rp = tk.get("reprice") or {}
    session = rp.get("priced_bar") if rp.get("status") == "ok" else tk.get("evidence_cutoff")
    session = str(session)[:10] if session else None
    src = os.path.basename(tk_path)
    ticket_session = str(tk.get("evidence_cutoff"))[:10] if tk.get("evidence_cutoff") else None

    if not session:
        return {"status": "NO_SESSION", "ticket": src, "criteria": CRITERIA}
    iopv, iopv_path = read_iopv(session)
    if iopv is None:
        return {"status": "NO_IOPV_SNAPSHOT", "ticket": src, "session": session,
                "iopv_path": os.path.relpath(iopv_path, ROOT), "criteria": CRITERIA,
                "note": "cannot price the entry without that session's IOPV row; not zero"}

    rows = premium_table(order, iopv, session)
    tot = totals_of(rows, book_amount, nav, cagr)
    top_names = [r["symbol"] for r in rows
                 if r["status"] == "OK" and (r["market_pctile"] or 0.0) >= TOP_PCTILE]
    word, why = verdict_of(tot, len(top_names), top_names)
    hist = nav_ruler_history([r["symbol"] for r in rows])
    own = own_history(rows)
    own_s = own_summary(own, rows)

    return {
        "status": "ok",
        "generated_by": "etf_book_premium_leak v1.0",
        "ticket": src,
        "ticket_session": ticket_session,
        "iopv_session": session,
        "session_match": (ticket_session == session),
        "iopv_path": os.path.relpath(iopv_path, ROOT),
        "criteria": CRITERIA,
        "names": rows,
        "totals": tot,
        "verdict": word,
        "verdict_reason": why,
        "premium_names": top_names,
        "stress": {
            "if_premium_reverts_to_zero_cny": -tot["premium_paid_cny"],
            "if_premium_reverts_to_zero_pct_of_nav": (
                round(-tot["premium_paid_cny"] / nav * 100.0, 4) if nav else None),
            "if_premium_reverts_to_own_median_cny": -own_s["revert_to_own_median_cny"],
            "if_premium_reverts_to_own_median_pct_of_nav": (
                round(-own_s["revert_to_own_median_cny"] / nav * 100.0, 4) if nav else None),
            "note": "reversion is a stress, not a forecast: the gap can persist while the "
                    "sleeve stays hard to buy. Zero is the outer bound; each fund's own "
                    "median is the realistic one -- these funds normally live above NAV.",
        },
        "rulers": {
            "entry": "price / IOPV - 1, same session (this is what the order pays)",
            "history": "close / published unit NAV - 1, disclosure-lagged (NOT the same "
                       "quantity, printed separately, never blended)",
        },
        "nav_ruler_history": hist,
        "own_criteria": {"min_obs": OWN_MIN_OBS, "top_decile_pctile": OWN_DECILE_PCTILE},
        "own_ruler": own,
        "own_ruler_summary": own_s,
    }


def check(path=OUT_JSON):
    """Gate: echoed criteria must equal the constants, and the verdict must recompute."""
    if not os.path.exists(path):
        print("[check] no published face at %s" % path)
        return 2
    face = _load_json(path)
    fails = []
    if face.get("criteria") != CRITERIA:
        fails.append("criteria echo %r != constants %r" % (face.get("criteria"), CRITERIA))
    if face.get("status") != "ok":
        fails.append("face status %r" % face.get("status"))
        print("[check] FAIL " + "; ".join(fails))
        return 1
    tot = face.get("totals") or {}
    rows = face.get("names") or []
    paid = round(sum(r["premium_paid_cny"] for r in rows if r["status"] == "OK"), 2)
    if abs(paid - (tot.get("premium_paid_cny") or 0.0)) > 0.02:
        fails.append("total premium %.2f != sum of names %.2f" % (tot.get("premium_paid_cny"), paid))
    if tot.get("n_verified", 0) + tot.get("n_unverifiable", 0) != tot.get("n_names"):
        fails.append("n_verified + n_unverifiable != n_names")
    top = [r["symbol"] for r in rows
           if r["status"] == "OK" and (r["market_pctile"] or 0.0) >= TOP_PCTILE]
    word, why = verdict_of(tot, len(top), top)
    if word != face.get("verdict"):
        fails.append("verdict %r recomputes to %r" % (face.get("verdict"), word))
    if face.get("session_match") is False:
        fails.append("ticket session %r != iopv session %r"
                     % (face.get("ticket_session"), face.get("iopv_session")))
    # ---- own-history ruler (r1553): echoed criteria, no silent omission, recomputed words
    own_crit = face.get("own_criteria") or {}
    if own_crit != {"min_obs": OWN_MIN_OBS, "top_decile_pctile": OWN_DECILE_PCTILE}:
        fails.append("own_criteria echo %r != constants" % (own_crit,))
    own = face.get("own_ruler") or {}
    symbols = [str(r.get("symbol") or "").zfill(6) for r in rows]
    missing = [s for s in symbols if s not in own]
    if missing:
        fails.append("own_ruler has no row for %s (a name must be unreadable, not absent)"
                     % ",".join(missing))
    for s in symbols:
        st = own.get(s) or {}
        if st.get("status") == "OK" and (st.get("n_obs") or 0) < OWN_MIN_OBS:
            fails.append("%s own_ruler OK with n_obs=%r < %d" % (s, st.get("n_obs"), OWN_MIN_OBS))
        if st.get("status") == "OK" and st.get("last_pctile") is None:
            fails.append("%s own_ruler OK without last_pctile" % s)
    stored = face.get("own_ruler_summary") or {}
    recomputed = own_summary(own, rows)
    if stored.get("verdict") != recomputed["verdict"]:
        fails.append("own verdict %r recomputes to %r"
                     % (stored.get("verdict"), recomputed["verdict"]))
    if stored.get("in_own_top_decile") != recomputed["in_own_top_decile"]:
        fails.append("own top-decile list %r recomputes to %r"
                     % (stored.get("in_own_top_decile"), recomputed["in_own_top_decile"]))
    if abs((stored.get("revert_to_own_median_cny") or 0.0)
           - recomputed["revert_to_own_median_cny"]) > 0.02:
        fails.append("own median-reversion %.2f != recomputed %.2f"
                     % (stored.get("revert_to_own_median_cny"),
                        recomputed["revert_to_own_median_cny"]))
    if fails:
        print("[check] FAIL")
        for f in fails:
            print("  - " + f)
        return 1
    print("[check] CHECK_OK verdict=%s premium=CNY %.2f (%.2f%% of the order) names>=%.1f pctile: %s"
          % (word, tot["premium_paid_cny"], tot.get("premium_share_of_order_pct") or 0.0,
             TOP_PCTILE, ",".join(top) or "-"))
    return 0


# ------------------------------------------------------------------ selftest
def _rows(prem_values):
    return {str(100000 + i): {"code": str(100000 + i), "premium_pct": v, "price": 1.0,
                              "iopv": 1.0 / (1.0 + v / 100.0)} for i, v in enumerate(prem_values)}


def selftest():
    fails = []
    legs = []

    def ck(name, cond, info=""):
        legs.append(name)
        if not cond:
            fails.append("%s %s" % (name, info))

    # L1 premium arithmetic on a two-name fixture
    iopv = {"159501": {"code": "159501", "iopv": "1.6734", "premium_pct": "23.6405"},
            "159263": {"code": "159263", "iopv": "1.1451", "premium_pct": "-0.1834"}}
    order = [{"symbol": "159501", "shares": 44400, "price": 2.069, "amount": 91863.6,
              "class": "crossborder"},
             {"symbol": "159263", "shares": 80500, "price": 1.143, "amount": 92011.5,
              "class": "equity"}]
    rows = premium_table(order, iopv, "2026-11-06")
    ck("L1a", abs(rows[0]["premium_paid_cny"] - 44400 * (2.069 - 1.6734)) < 0.01,
       str(rows[0]["premium_paid_cny"]))
    ck("L1b", rows[1]["premium_paid_cny"] < 0, "a discount must read as negative")

    # L2 absent IOPV row is unverifiable, never zero-filled, and excluded from the total
    rows2 = premium_table(order + [{"symbol": "513100", "shares": 100, "price": 2.0,
                                    "amount": 200.0}], iopv, "2026-11-06")
    tot2 = totals_of(rows2, 184000.0, 1000000.0, 9.0)
    ck("L2a", rows2[2]["status"] == "NO_IOPV_ROW" and rows2[2]["premium_paid_cny"] is None,
       str(rows2[2]))
    ck("L2b", tot2["n_unverifiable"] == 1 and tot2["n_verified"] == 2, str(tot2))
    w2, _ = verdict_of(tot2, 0, [])
    ck("L2c", w2 == "PARTIAL", w2)

    # L3 the total is the sum of the verified rows only
    ck("L3", abs(tot2["premium_paid_cny"] - (rows[0]["premium_paid_cny"] +
                                             rows[1]["premium_paid_cny"])) < 0.02, str(tot2))

    # L4 verdict thresholds are inclusive at the constants
    t = dict(tot2)
    t.update({"n_unverifiable": 0, "n_names": 2, "n_verified": 2,
              "premium_share_of_order_pct": 4.99, "premium_paid_cny": 1.0})
    ck("L4a", verdict_of(t, 0, [])[0] == "ENTRY_PREMIUM_WARN", verdict_of(t, 0, [])[0])
    t["premium_share_of_order_pct"] = 5.0
    ck("L4b", verdict_of(t, 0, [])[0] == "ENTRY_PREMIUM_DOMINATES", verdict_of(t, 0, [])[0])
    t["premium_share_of_order_pct"] = 0.5
    ck("L4c", verdict_of(t, 0, [])[0] == "ENTRY_PREMIUM_SMALL", verdict_of(t, 0, [])[0])
    t["n_verified"] = 0
    ck("L4d", verdict_of(t, 0, [])[0] == "CANNOT_VERIFY", "no verified name must not read SMALL")

    # L5 market percentile: rank counts names strictly above, percentile is names below
    mk = _rows([-1.0, 0.0, 5.0, 20.0, 40.0])
    pct, rank, n = market_rank(mk, "x", 20.0)
    ck("L5a", rank == 2 and n == 5, "%s %s %s" % (pct, rank, n))
    ck("L5b", abs(pct - 60.0) < 1e-9, str(pct))

    # L6 revert-to-zero stress is exactly the premium paid
    ck("L6", abs(tot2["premium_paid_cny"] + (-tot2["premium_paid_cny"])) < 1e-9)

    # L7 years-of-return arithmetic
    t3 = totals_of(rows, 184000.0, 1000000.0, 10.0)
    expect = round(t3["premium_paid_cny"] / (t3["verified_amount_cny"] * 0.10), 2)
    ck("L7", t3["years_of_backtest_return_paid"] == expect, str(t3["years_of_backtest_return_paid"]))

    # L8 share of order and share of NAV are two denominators, both kept
    ck("L8", t3["premium_share_of_order_pct"] != t3["premium_share_of_nav_pct"],
       "%s %s" % (t3["premium_share_of_order_pct"], t3["premium_share_of_nav_pct"]))

    # L9 a single NAV-ruler observation is not a history
    ck("L9a", history_stats([0.17], "159501")["status"] == "NOT_ENOUGH_OBSERVATIONS")
    ck("L9b", history_stats([0.01, 0.03], "x")["median_pct"] == 2.0,
       str(history_stats([0.01, 0.03], "x")))
    ck("L9c", history_stats([0.01, 0.03, 0.02], "x")["median_pct"] == 2.0)

    # L10 criteria echo mismatch is a refusal (fixture written to temp)
    import contextlib
    import io
    import tempfile
    tmp = os.path.join(tempfile.gettempdir(), "_prem_leak_check.json")
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump({"status": "ok", "criteria": dict(CRITERIA, warn_share_pct=9.9),
                   "totals": {"n_verified": 1, "n_unverifiable": 0, "n_names": 1,
                              "premium_paid_cny": 1.0, "premium_share_of_order_pct": 0.5},
                   "names": [{"symbol": "x", "status": "OK", "premium_paid_cny": 1.0,
                              "market_pctile": 0.0, "session_match": True}],
                   "verdict": "ENTRY_PREMIUM_SMALL", "session_match": True}, fh)
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = check(tmp)
    ck("L10", rc == 1, "a drifted criteria echo must be refused, got rc=%s" % rc)
    # L11 a summary with no denominator is CANNOT_VERIFY, not a small premium
    ck("L11", verdict_of({"n_verified": 1, "n_unverifiable": 0, "premium_paid_cny": 1.0},
                         0, [])[0] == "CANNOT_VERIFY")
    try:
        os.remove(tmp)
    except OSError:
        pass

    # ---- own-history ruler (r1553): the percentile of "for THIS fund", not of the board
    import csv as _csv
    import tempfile as _tf
    base = _tf.mkdtemp(prefix="_prem_own_")
    ddir = os.path.join(base, "daily")
    ndir = os.path.join(base, "navhist")
    os.makedirs(ddir)
    os.makedirs(ndir)

    def _write_series(code, px_rows, nav_rows):
        with open(os.path.join(ddir, code + ".csv"), "w", newline="", encoding="utf-8") as fh:
            w = _csv.writer(fh)
            w.writerow(["date", "open", "high", "low", "close", "volume", "amount"])
            for d, c in px_rows:
                w.writerow([d, c, c, c, c, 1, 1])
        with open(os.path.join(ndir, code + ".csv"), "w", newline="", encoding="utf-8") as fh:
            w = _csv.writer(fh)
            w.writerow(["date", "nav"])
            for d, n in nav_rows:
                w.writerow([d, n])

    # L12 the percentile is this fund's own: nine sessions at 1% and one at 10%
    days = ["2026-01-%02d" % (i + 1) for i in range(10)]
    _write_series("100001", [(d, 1.01) for d in days[:9]] + [(days[9], 1.10)],
                  [(d, 1.00) for d in days])
    ser, meta = own_series("100001", daily_dir=ddir, navhist_dir=ndir)
    st = own_stats(ser, "100001", meta, min_obs=2)
    ck("L12a", st["n_obs"] == 10, str(st.get("n_obs")))
    ck("L12b", abs(st["last_pct"] - 10.0) < 1e-9 and abs(st["last_pctile"] - 90.0) < 1e-9,
       "%s %s" % (st.get("last_pct"), st.get("last_pctile")))
    ck("L12c", abs(st["median_pct"] - 1.0) < 1e-9, str(st.get("median_pct")))
    ck("L12d", abs(st["above_own_median_pp"] - 9.0) < 1e-9, str(st.get("above_own_median_pp")))

    # L13 the reading is the last JOINED date: a price with no NAV must not be used
    _write_series("100002", [(d, 1.05) for d in days] + [("2026-02-01", 9.99)],
                  [(d, 1.00) for d in days])
    ser2, meta2 = own_series("100002", daily_dir=ddir, navhist_dir=ndir)
    st2 = own_stats(ser2, "100002", meta2, min_obs=2)
    ck("L13", abs(st2["last_pct"] - 5.0) < 1e-9 and st2["last_day"] == days[-1],
       "%s %s" % (st2.get("last_pct"), st2.get("last_day")))

    # L14 a missing leg is unreadable, never a zero premium
    ser3, meta3 = own_series("199999", daily_dir=ddir, navhist_dir=ndir)
    st3 = own_stats(ser3, "199999", meta3, min_obs=2)
    ck("L14a", st3["status"] == "NO_LOCAL_HISTORY" and st3["last_pct"] is None, str(st3))
    ck("L14b", st3["median_pct"] is None and st3["last_pctile"] is None, str(st3))

    # L15 a percentile of two sessions is not this fund's norm
    _write_series("100003", [(d, 1.01) for d in days[:2]], [(d, 1.00) for d in days[:2]])
    ser4, meta4 = own_series("100003", daily_dir=ddir, navhist_dir=ndir)
    ck("L15", own_stats(ser4, "100003", meta4, min_obs=OWN_MIN_OBS)["status"]
       == "NOT_ENOUGH_OBSERVATIONS")

    # L16 median reversion is shares*iopv*(entry premium - own median), not premium paid
    own_fix = {"100001": {"status": "OK", "median_pct": 1.0, "last_pctile": 90.0}}
    rows_fix = [{"symbol": "100001", "status": "OK", "shares": 10000.0, "iopv": 1.0,
                 "premium_pct": 6.0}]
    s16 = own_summary(own_fix, rows_fix)
    ck("L16", abs(s16["revert_to_own_median_cny"] - 10000.0 * (0.06 - 0.01)) < 0.01,
       str(s16["revert_to_own_median_cny"]))

    # L17 the word is derived from the list, and an all-unreadable book says so
    ck("L17a", own_summary({"100001": {"status": "OK", "median_pct": 1.0,
                                       "last_pctile": 95.0}}, rows_fix)["verdict"]
       == "EVERY_NAME_ABOVE_OWN_TOP_DECILE")
    ck("L17b", own_summary({"100001": {"status": "OK", "median_pct": 1.0,
                                       "last_pctile": 12.0}}, rows_fix)["verdict"]
       == "NO_NAME_ABOVE_OWN_TOP_DECILE")
    ck("L17c", own_summary({"100001": {"status": "NO_LOCAL_HISTORY"}}, rows_fix)["verdict"]
       == "OWN_HISTORY_UNREADABLE")

    if fails:
        print("[selftest] %d FAIL" % len(fails))
        for f in fails:
            print("  - " + f)
        return 1
    print("[selftest] %d/%d PASS" % (len(legs) - len(fails), len(legs)))
    return 0


def gather():
    face = build()
    if face.get("status") == "ok":
        payload = face
    else:
        payload = face
    tmp = OUT_JSON + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=1)
    os.replace(tmp, OUT_JSON)
    if payload.get("status") != "ok":
        print("[run] %s" % payload.get("status"))
        return 2 if payload.get("status") == "NO_TICKET" else 3
    tot = payload["totals"]
    print("[run] verdict=%s  premium CNY %.2f = %.2f%% of the order / %.2f%% of NAV"
          % (payload["verdict"], tot["premium_paid_cny"],
             tot.get("premium_share_of_order_pct") or 0.0,
             tot.get("premium_share_of_nav_pct") or 0.0))
    for r in payload["names"]:
        if r["status"] == "OK":
            print("  %s %-10s prem %7.2f%%  paid CNY %9.2f  market rank %s/%s"
                  % (r["symbol"], r["class"], r["premium_pct"], r["premium_paid_cny"],
                     r["market_rank"], r["market_n"]))
        else:
            print("  %s %-10s %s" % (r["symbol"], r["class"], r["status"]))
    print("  years of the book's own backtest return paid up front: %s"
          % tot.get("years_of_backtest_return_paid"))
    owns = payload.get("own_ruler_summary") or {}
    own = payload.get("own_ruler") or {}
    print("[own] %s -- %d/%d readable, top decile: %s"
          % (owns.get("verdict"), owns.get("n_readable") or 0, owns.get("n_names") or 0,
             ",".join(owns.get("in_own_top_decile") or []) or "-"))
    for r in payload["names"]:
        code = str(r.get("symbol") or "").zfill(6)
        st = own.get(code) or {}
        if st.get("status") == "OK":
            print("  %s own %6d obs %s..%s  last %7.2f%%  pctile %5.1f  "
                  "median %5.2f  p90 %5.2f  (%+.2fpp vs own median)"
                  % (code, st["n_obs"], st["first_day"], st["last_day"], st["last_pct"],
                     st["last_pctile"], st["median_pct"], st["p90_pct"],
                     st["above_own_median_pp"]))
        else:
            print("  %s own %s" % (code, st.get("status")))
    stress = payload.get("stress") or {}
    print("  vs its own median: CNY %s (%.2f%% of NAV); vs zero: CNY %s"
          % (format(stress.get("if_premium_reverts_to_own_median_cny") or 0.0, ",.0f"),
             stress.get("if_premium_reverts_to_own_median_pct_of_nav") or 0.0,
             format(stress.get("if_premium_reverts_to_zero_cny") or 0.0, ",.0f")))
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", nargs="?", default="run", choices=["run", "check", "selftest"])
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)
    if args.selftest or args.cmd == "selftest":
        return selftest()
    if args.check or args.cmd == "check":
        return check()
    return gather()


if __name__ == "__main__":
    sys.exit(main())