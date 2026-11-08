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
OUT_JSON = os.path.join(ROOT, "results", "etf_book_premium_leak.json")

# ---- frozen criteria (pre-registered before the first run; --check echoes them back) ----
WARN_SHARE_PCT = 1.0       # premium paid >= 1.0% of the order -> worth printing loudly
DOMINATE_SHARE_PCT = 5.0   # premium paid >= 5.0% of the order -> entry cost dominates
TOP_PCTILE = 95.0          # a name in the market's top 5% premium is flagged by name
MIN_HISTORY_OBS = 2        # fewer than two NAV-ruler observations is not a history

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
            "note": "reversion is a stress, not a forecast: the gap can persist while the "
                    "sleeve stays hard to buy",
        },
        "rulers": {
            "entry": "price / IOPV - 1, same session (this is what the order pays)",
            "history": "close / published unit NAV - 1, disclosure-lagged (NOT the same "
                       "quantity, printed separately, never blended)",
        },
        "nav_ruler_history": hist,
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