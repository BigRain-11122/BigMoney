"""Which repo tenor should the book's uninvested sleeve be rolled into TODAY, and does the
answer change because the cash has to be back before the next decision bar?

The ladder face (r1114, `etf_book_cash_ladder.py`) priced six tenor policies over the whole
history and printed an instruction ticket -- but its ticket is stamped with its own cutoff
(2026-10-27) and its rungs say "roll GC001 on the first bar at/after 2026-10-27". Nobody
reads that as today's instruction, so the reader is left with the number the CEO page prints
(CNY 5,295/yr at the 1-day rate) and no answer to "so which one do I buy this morning?".

This face answers exactly that one question, from three files on disk:

  cash to place        results/etf_book_cut_order_gap.json  (nav - ordered book)
  the deadline         the same file's decision_date (the bar the cash must be free for)
  the quotes           data/repo_daily/*.csv  (bm-a lane; own last bar disclosed)

Rules that are not negotiable (each has a selftest leg):

  * a contract opened today is never exited early, so a tenor only qualifies if its
    maturity bar is at or before the decision date -- the cash must be raisable then;
  * the quote is that tenor's own close on the panel's last bar; if a tenor has no quote on
    that bar it is excluded and named, never ffilled from an older bar;
  * the fee is the exchange schedule in `etf_book_cash_ladder.FEE_BP`, annualised by the
    contract's own tenor, and printed separately from the gross quote;
  * lot feasibility is priced: Shanghai repo moves in CNY 100,000 lots, Shenzhen in CNY
    1,000 lots, so "which tenor" is only half the answer -- "how much of the sleeve can
    actually be placed" is the other half;
  * no panel, no decision date, or no cash reading = NO_INSTRUCTION with the reason named,
    never a zero.

Read-only over existing faces; no preregistration, no ledger booking, no strategy change.
The instruction is what the book's own cash sleeve would do today under the ladder rule; it
is not an order and not investment advice.

Usage:
  python scripts/etf_book_cash_roll_today.py --selftest
  python scripts/etf_book_cash_roll_today.py [--check]
"""

import argparse
import hashlib
import json
import os
import sys
import time

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE)

from scripts import etf_book_cash_ladder as L  # noqa: E402

OUT_PATH = os.path.join(BASE, "results", "etf_book_cash_roll_today.json")
PERM_PATH = os.path.join(BASE, "results", "etf_book_cut_order_gap.json")

SH_LOT = 100000          # Shanghai GC: 100,000 CNY face per order, 1,000 increments
SZ_LOT = 1000            # Shenzhen R: 1,000 CNY face per order
CASH_EPS = 1e-6


# ---------------------------------------------------------------------------------------
# lot feasibility
# ---------------------------------------------------------------------------------------
def placeable(cash_cny):
    """Split a cash sleeve into a Shanghai part, a Shenzhen part and the coin left over."""
    cash = float(cash_cny)
    if cash < 0:
        raise ValueError("negative cash sleeve: %.2f" % cash)
    sh = (int(cash // SH_LOT) * SH_LOT) if cash >= SH_LOT else 0
    rest = cash - sh
    sz = (int(rest // SZ_LOT) * SZ_LOT) if rest >= SZ_LOT else 0
    return {"sh_cny": float(sh), "sz_cny": float(sz), "leftover_cny": round(rest - sz, 2),
            "placed_cny": float(sh + sz), "cash_cny": cash}


# ---------------------------------------------------------------------------------------
# the ladder decision
# ---------------------------------------------------------------------------------------
def choose(cash_cny, as_of, decision_date, quotes, last_bars, fees=None):
    """Pick today's tenor under the "cash must be back by decision_date" constraint.

    quotes     {name: annualised close in percent}
    last_bars  {name: the ISO date that quote belongs to}
    Returns a dict; every number in it is re-derivable from the arguments alone.
    """
    import datetime as _dt

    d0 = _dt.date.fromisoformat(as_of)
    d1 = _dt.date.fromisoformat(decision_date)
    window_days = (d1 - d0).days

    part = placeable(cash_cny)
    rows, excluded, missing = [], [], []
    for name, tenor, venue in L.TENORS:
        q = quotes.get(name)
        bar = last_bars.get(name)
        if q is None or bar != as_of:
            missing.append({"contract": name, "quote_bar": bar, "asked_bar": as_of})
            continue
        fee_bp = float(L.fee_bp(name, fees))
        fee_pp_year = fee_bp / 100.0 * (365.0 / tenor)
        net_ann = float(q) - fee_pp_year
        maturity = (d0 + _dt.timedelta(days=tenor)).isoformat()
        fits = maturity <= decision_date
        row = {"contract": name, "tenor_days": tenor, "venue": venue,
               "quoted_pct": round(float(q), 4),
               "fee_bp_per_contract": fee_bp,
               "fee_pp_per_year": round(fee_pp_year, 4),
               "net_ann_pct": round(net_ann, 4),
               "matures": maturity,
               "fits_before_decision": fits,
               "window_return_pct": round(net_ann * window_days / 365.0, 4)}
        if fits:
            rows.append(row)
        else:
            row["locked_past_decision_days"] = (
                _dt.date.fromisoformat(maturity) - d1).days
            excluded.append(row)

    base = next((r for r in rows if r["contract"] == "GC001"), None)
    best_sh = max([r for r in rows if r["venue"] == "SH"],
                  key=lambda r: r["net_ann_pct"], default=None)
    best_sz = max([r for r in rows if r["venue"] == "SZ"],
                  key=lambda r: r["net_ann_pct"], default=None)

    out = {"as_of": as_of, "decision_date": decision_date, "window_days": window_days,
           "cash_cny": part["cash_cny"], "placeable": part,
           "eligible": sorted(rows, key=lambda r: -r["net_ann_pct"]),
           "excluded_locked": sorted(excluded, key=lambda r: -r["net_ann_pct"]),
           "excluded_no_quote": missing,
           "baseline": base, "best_sh": best_sh, "best_sz": best_sz}
    if best_sh is None and best_sz is None:
        out["verdict"] = "NO_INSTRUCTION"
        out["reason"] = ("no tenor has a quote on %s that matures on or before %s"
                         % (as_of, decision_date))
        return out

    worth_year = 0.0
    worth_window = 0.0
    if base is not None:
        for r, amt in ((best_sh, part["sh_cny"]), (best_sz, part["sz_cny"])):
            if r is None or amt <= 0:
                continue
            worth_year += amt * (r["net_ann_pct"] - base["net_ann_pct"]) / 100.0
            worth_window += amt * (r["window_return_pct"] - base["window_return_pct"]) / 100.0
    out["worth_vs_daily_roll_cny_year"] = round(worth_year, 2)
    out["worth_vs_daily_roll_cny_window"] = round(worth_window, 2)

    name = (best_sh or best_sz)["contract"]
    if base is not None and best_sh is not None and best_sh["contract"] == "GC001":
        out["verdict"] = "ROLL_GC001_TODAY"
        out["sentence"] = ("the sleeve is worth %.2f%%/yr net on %s and rolling it every day "
                           "is already the best tenor that gets the cash back by %s -- the "
                           "ladder buys %.2f CNY a year, which is nothing"
                           % (best_sh["net_ann_pct"], as_of, decision_date, worth_year))
    else:
        out["verdict"] = "ROLL_%s_TODAY" % name.replace("-", "")
        out["sentence"] = ("%s pays %.2f%%/yr net and still matures by %s; versus rolling "
                           "1-day every session it is worth %.2f CNY a year (%.2f CNY over "
                           "the %d days to the next decision)"
                           % (name, (best_sh or best_sz)["net_ann_pct"], decision_date,
                              worth_year, worth_window, window_days))
    return out


# ---------------------------------------------------------------------------------------
# disk readers
# ---------------------------------------------------------------------------------------
def _digest(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def _panel_digest(panel_dir=None):
    """One digest over the tenor files this instruction prices off (name + bytes)."""
    panel_dir = panel_dir or L.PANEL_DIR
    if not os.path.isdir(panel_dir):
        return None
    h = hashlib.sha256()
    for name in sorted(os.listdir(panel_dir)):
        if not name.endswith(".csv"):
            continue
        h.update(name.encode("utf-8"))
        h.update(_digest(os.path.join(panel_dir, name)).encode("ascii"))
    return h.hexdigest()


def read_inputs(perm_path=PERM_PATH, panel_dir=L.PANEL_DIR):
    """Return (perm, quotes, last_bars, problems). Never invents a missing number."""
    problems = []
    perm = {}
    if not os.path.exists(perm_path):
        problems.append("missing %s" % os.path.relpath(perm_path, BASE))
    else:
        with open(perm_path, encoding="utf-8") as fh:
            perm = json.load(fh)
    series = L.load_panel(panel_dir)
    if not series:
        problems.append("no repo panel under %s" % os.path.relpath(panel_dir, BASE))
    quotes, last_bars = {}, {}
    for name, s in series.items():
        s = s.dropna()
        if not len(s):
            continue
        quotes[name] = float(s.iloc[-1])
        last_bars[name] = str(s.index[-1].date())
    return perm, quotes, last_bars, problems


def build(perm, quotes, last_bars, problems):
    out = {"face": "etf_book_cash_roll_today",
           "question": ("which repo tenor does the book's uninvested sleeve roll into today, "
                        "and is the answer constrained by the next decision bar?"),
           "generated": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
           "panel_last_bars": last_bars,
           "inputs": {"permission_face": os.path.relpath(PERM_PATH, BASE),
                      "permission_sha256": (_digest(PERM_PATH)
                                            if os.path.exists(PERM_PATH) else None),
                      "repo_panel_sha256": _panel_digest()}}
    if problems:
        out["verdict"] = "NO_INSTRUCTION"
        out["reason"] = "; ".join(problems)
        out["sentence"] = ("cannot give today's roll instruction: %s" % out["reason"])
        return out

    nav = perm.get("nav_cny")
    ordered = perm.get("ordered_book_cny")
    decision = perm.get("decision_date")
    missing = [k for k, v in (("nav_cny", nav), ("ordered_book_cny", ordered),
                              ("decision_date", decision)) if v in (None, "")]
    if missing:
        out["verdict"] = "NO_INSTRUCTION"
        out["reason"] = "permission face lacks %s" % ", ".join(missing)
        out["sentence"] = ("cannot give today's roll instruction: %s" % out["reason"])
        return out

    cash = float(nav) - float(ordered)
    as_of = last_bars.get("GC001")
    out["inputs"].update({"nav_cny": float(nav), "ordered_book_cny": float(ordered),
                          "cash_cny": cash, "book_as_of": perm.get("as_of"),
                          "decision_date": decision,
                          "repo_panel_as_of": as_of})
    if as_of is None:
        out["verdict"] = "NO_INSTRUCTION"
        out["reason"] = "repo panel has no GC001 bar"
        out["sentence"] = out["reason"]
        return out
    if perm.get("as_of") and perm["as_of"] > as_of:
        out["panel_lag"] = {"book_as_of": perm["as_of"], "repo_panel_as_of": as_of,
                            "note": ("the repo panel is behind the book bar; the quotes are "
                                     "read off their own last bar and never ffilled")}
    out.update(choose(cash, as_of, decision, quotes, last_bars))
    out["cash_cny"] = cash
    return out


def check(out=None, perm_path=PERM_PATH, panel_dir=L.PANEL_DIR):
    """Re-derive today's instruction from disk and compare it to the published face."""
    if out is None:
        with open(OUT_PATH, encoding="utf-8") as fh:
            out = json.load(fh)
    perm, quotes, last_bars, problems = read_inputs(perm_path, panel_dir)
    fresh = build(perm, quotes, last_bars, problems)
    problems = list(problems)
    keys = ("verdict", "cash_cny", "as_of", "decision_date", "window_days")
    for k in keys:
        if fresh.get(k) != out.get(k):
            problems.append("%s: published %r vs re-derived %r"
                            % (k, out.get(k), fresh.get(k)))
    if out.get("best_sh") and fresh.get("best_sh"):
        if out["best_sh"].get("contract") != fresh["best_sh"].get("contract"):
            problems.append("best_sh: published %s vs re-derived %s"
                            % (out["best_sh"].get("contract"), fresh["best_sh"].get("contract")))
        elif abs(out["best_sh"].get("net_ann_pct", 0) - fresh["best_sh"]["net_ann_pct"]) > 1e-6:
            problems.append("best_sh net_ann_pct moved")
    if out.get("placeable") and fresh.get("placeable"):
        for k in ("sh_cny", "sz_cny", "leftover_cny"):
            if abs(float(out["placeable"].get(k, -1)) - fresh["placeable"][k]) > CASH_EPS:
                problems.append("placeable.%s: published %r vs re-derived %r"
                                % (k, out["placeable"].get(k), fresh["placeable"][k]))
    # r2159: the instruction is priced on the book's permission face and on the repo panel's
    # bytes.  When either moved, the old sentence was right for the file it was written on --
    # that is drift, and it must say STALE, the one word the chain pays a rebuild for.
    rec = out.get("inputs") or {}
    now = fresh.get("inputs") or {}
    moved = []
    if rec.get("permission_sha256") != now.get("permission_sha256"):
        moved.append("the book's permission face was rewritten since this instruction "
                     "was written")
    if rec.get("repo_panel_sha256") != now.get("repo_panel_sha256"):
        moved.append("the repo panel bytes changed since this instruction was written")
    if problems:
        if moved:
            problems = ["STALE " + m for m in moved] + [
                "the printed instruction moved with it: " + " | ".join(problems)]
        else:
            problems = ["CHECK FAILED " + p for p in problems]
    return {"ok": not problems, "problems": problems, "moved_inputs": moved,
            "checked_at": time.strftime("%Y-%m-%dT%H:%M:%S%z")}


# ---------------------------------------------------------------------------------------
# selftest
# ---------------------------------------------------------------------------------------
def selftest():
    fails, legs = [], []

    def leg(name, ok, detail=""):
        legs.append((name, bool(ok), detail))
        if not ok:
            fails.append(name)

    # -- lot feasibility -------------------------------------------------------------
    p = placeable(568120)
    leg("cash relaxed into 100k SH + 1k SZ lots leaves 120", 
        (p["sh_cny"], p["sz_cny"], p["leftover_cny"]) == (500000.0, 68000.0, 120.0),
        str(p))
    leg("placed + leftover == cash (no money invented)",
        abs(p["placed_cny"] + p["leftover_cny"] - p["cash_cny"]) < CASH_EPS)
    p2 = placeable(999000)
    leg("just under the SH lot limit goes to SZ, not to zero",
        p2["sh_cny"] == 900000.0 and p2["sz_cny"] == 99000.0, str(p2))
    p3 = placeable(500)
    leg("below the SZ lot the sleeve is all leftover and nothing is placed",
        p3["placed_cny"] == 0.0 and p3["leftover_cny"] == 500.0, str(p3))

    # -- tenor selection on a synthetic panel ----------------------------------------
    quotes = {"GC001": 1.275, "GC003": 1.26, "GC004": 1.255, "GC007": 1.35,
              "GC014": 1.30, "GC028": 1.36, "GC091": 1.315, "GC182": 1.305,
              "R-001": 1.28, "R-003": 1.285, "R-007": 1.35}
    bars = {k: "2026-11-17" for k in quotes}
    out = choose(568120, "2026-11-17", "2026-12-09", quotes, bars)
    leg("a tenor whose maturity lands after the decision date is excluded, not ranked",
        "GC028" not in [r["contract"] for r in out["eligible"]]
        and "GC028" in [r["contract"] for r in out["excluded_locked"]],
        str([r["contract"] for r in out["eligible"]]))
    leg("the excluded tenor still prints its own number and how long it would be stuck",
        all(r.get("locked_past_decision_days", 0) > 0 for r in out["excluded_locked"]))
    leg("GC001 (daily roll) always qualifies: a 1-day contract matures the next day",
        any(r["contract"] == "GC001" for r in out["eligible"]))
    leg("verdict token is derived from the winning name, not written down",
        out["verdict"] == "ROLL_%s_TODAY" % out["best_sh"]["contract"].replace("-", ""),
        out["verdict"])
    leg("net annual = quote - annualised fee, recomputed independently",
        all(abs(r["net_ann_pct"] - (r["quoted_pct"]
                                    - r["fee_bp_per_contract"] / 100.0 * 365.0 / r["tenor_days"]))
            < 1e-3 for r in out["eligible"]))
    leg("the fee is printed separately from the gross quote",
        all({"fee_pp_per_year", "fee_bp_per_contract"} <= set(r) for r in out["eligible"]))
    leg("percent fields stay percentages (a 1.35 quote is 1.35, not 135)",
        out["eligible"][0]["quoted_pct"] < 10)
    leg("the winner never scores below the daily-roll baseline",
        out["best_sh"]["net_ann_pct"] >= out["baseline"]["net_ann_pct"] - 1e-9)

    # a quote missing on the asked bar is excluded and named, never ffilled
    bars2 = dict(bars)
    bars2["GC007"] = "2026-11-14"
    out2 = choose(568120, "2026-11-17", "2026-12-09", quotes, bars2)
    leg("a tenor without a quote on the panel's own last bar is named as excluded",
        "GC007" in [m["contract"] for m in out2["excluded_no_quote"]]
        and "GC007" not in [r["contract"] for r in out2["eligible"]])
    leg("dropping one quote does not silently move the winner to that tenor",
        out2["best_sh"]["contract"] != "GC007")

    # no instruction rather than a fake one
    out3 = choose(568120, "2026-11-17", "2026-11-17", {}, bars)
    leg("empty panel yields NO_INSTRUCTION with a reason, never a zero",
        out3["verdict"] == "NO_INSTRUCTION" and bool(out3.get("reason")))
    out4 = choose(568120, "2026-11-17", "2026-11-18", quotes, bars)
    leg("a decision date inside the window leaves only the 1-day contracts eligible",
        sorted(r["contract"] for r in out4["eligible"]) == ["GC001", "R-001"],
        str([r["contract"] for r in out4["eligible"]]))

    # -- disk readers ----------------------------------------------------------------
    perm, q, b, problems = read_inputs()
    leg("the live permission face and repo panel both read from disk",
        not problems and bool(q) and bool(b), str(problems))
    leg("every panel quote carries the bar it belongs to",
        all(isinstance(v, str) and len(v) == 10 for v in b.values()))
    live = build(perm, q, b, problems)
    leg("the published face's cash is nav minus the ordered book, to the cent",
        abs(live["cash_cny"] - (float(perm["nav_cny"]) - float(perm["ordered_book_cny"])))
        < CASH_EPS, str(live.get("cash_cny")))
    leg("missing inputs produce NO_INSTRUCTION instead of a sentence with a number in it",
        build({}, {}, {}, ["missing x"])["verdict"] == "NO_INSTRUCTION")

    # r2159: a wrong number with still inputs is a defect; a moved input is drift, and only
    # the literal word STALE buys the 1.1s rebuild that makes this face current again.
    import copy as _copy
    poisoned = _copy.deepcopy(live)
    poisoned["cash_cny"] = float(live["cash_cny"]) + 54.0
    res = check(out=poisoned)
    leg("a wrong number with unchanged inputs is called a defect, not drift",
        (not res["ok"])
        and any("CHECK FAILED" in x for x in res["problems"])
        and not any("STALE" in x for x in res["problems"]), str(res["problems"]))
    stale = _copy.deepcopy(poisoned)
    stale["inputs"] = dict(live["inputs"], permission_sha256="deadbeef")
    res2 = check(out=stale)
    leg("a rewritten permission face says STALE and names the file it was priced on",
        (not res2["ok"]) and any(x.startswith("STALE") for x in res2["problems"]),
        str(res2["problems"]))

    for name, ok, detail in legs:
        print("[%s] %s%s" % ("PASS" if ok else "FAIL", name,
                             (" | " + detail) if (detail and not ok) else ""))
    print("\nselftest %d/%d" % (len(legs) - len(fails), len(legs)))
    return 0 if not fails else 1


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args(argv)
    if args.selftest:
        return selftest()
    if args.check:
        r = check()
        print(json.dumps(r, ensure_ascii=False, indent=1))
        return 0 if r["ok"] else 1

    t0 = time.time()
    perm, quotes, last_bars, problems = read_inputs()
    out = build(perm, quotes, last_bars, problems)
    out["elapsed_sec"] = round(time.time() - t0, 2)
    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1)
    print("%s | %s" % (out["verdict"], out.get("sentence", "")))
    if out.get("best_sh"):
        print("best SH %s %.3f%%/yr net | cash %.0f -> SH %.0f + SZ %.0f (left %.0f) | "
              "worth %+.2f CNY/yr vs daily roll"
              % (out["best_sh"]["contract"], out["best_sh"]["net_ann_pct"],
                 out["cash_cny"], out["placeable"]["sh_cny"], out["placeable"]["sz_cny"],
                 out["placeable"]["leftover_cny"], out["worth_vs_daily_roll_cny_year"]))
    print("wrote %s (%.1fs)" % (os.path.relpath(OUT_PATH, BASE), time.time() - t0))
    return 0


if __name__ == "__main__":
    sys.exit(main())
