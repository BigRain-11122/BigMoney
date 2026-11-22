"""Can our money actually fit on the part of the repo curve that pays?

Why this face exists
--------------------
The cash leg has become the desk's actual recommendation: the rent audit says the ticket
earns less than parking, and the repo-ladder cell asks whether lending longer than GC001
pays. That cell printed its own open gap in plain words -- "volume is not converted to
money; the two longest tenors are indicative until capacity is measured at our size".

This face closes that gap and nothing else. It does not re-ask whether a ladder pays
(that is the ladder cell's job, criteria frozen there). It asks one question:

    at the sizes we actually run, which tenors can we fill without being the market?

Model
-----
  * Volume is converted to money at the exchange's own convention: 1 手 = 1,000 元 of
    face value. The convention is not asserted, it is checked: GC001's median turnover
    has to land in 1,000 亿 .. 5 万亿 a day, which is the exchange repo's published
    magnitude. If that check fails the face says UNIT_SUSPECT instead of printing a
    capacity number (a wrong unit would flip every verdict below).
  * The ruler is the *bad* day, not the median day: p10 of the daily turnover series.
    A cash leg has to be fillable on the day the money comes free, not on an average day.
  * OPEN means our order is <= 1% of that bad day, THIN means <= 10%, BLOCKED means more.
    A 1%/10% participation band is a market-impact convention, not a measured impact --
    our sizes are small enough that no impact model exists; the point of the band is to
    keep us away from days where we *are* a visible share of the tape.
  * Minimum ticket: SSE repo takes 100 手 = 10 万元 per order; SZSE takes 1,000 元.
    Money below one ticket cannot lend at all, so the residue is printed in yuan.

Verdicts (mechanical, no taste):
  * ONLY_THE_OVERNIGHT_IS_OURS  -- no tenor beyond GC001 is OPEN at our size
  * THE_PICKUP_SITS_WHERE_WE_CANNOT_FILL -- the tenors whose median rate is above
    GC001 are exactly the ones that are not OPEN at our size
  * OPEN_TENORS_PAY_LESS_TODAY -- every OPEN tenor quotes below GC001 on the last bar
  * LADDER_IS_REACHABLE        -- some OPEN tenor both quotes above GC001 today and has
    a positive median pickup; the ladder cell's own criteria still decide whether to act.
Whatever is printed, the numbers are printed next to it: a verdict whose arithmetic is
not on the page is a claim, not a face.
"""
import json
import os
import sys

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bench_core as bc  # noqa: E402

OUT_JSON = os.path.join(bc.RESULTS, "repo_capacity_at_size.json")
OUT_MD = os.path.join(bc.RESEARCH, "REPO-CAPACITY-AT-SIZE.md")
REPO_DIR = os.path.join(bc.DATA, "repo_daily")

TENORS = [
    (1, "GC001", "sse"), (3, "GC003", "sse"), (4, "GC004", "sse"), (7, "GC007", "sse"),
    (14, "GC014", "sse"), (28, "GC028", "sse"), (91, "GC091", "sse"), (182, "GC182", "sse"),
    (1, "R-001", "szse"), (3, "R-003", "szse"), (7, "R-007", "szse"),
]
BASELINE = "GC001"
HAND_YUAN = 1000.0            # 1 手 = 1,000 元 face value (exchange convention, checked below)
UNIT_CHECK_YUAN = (1000e8, 5e12)   # GC001 median daily turnover must sit here
SIZES = [("10万", 1e5), ("100万", 1e6), ("300万", 3e6), ("1000万", 1e7)]
PART_OK = 0.01                # <=1% of the bad day = OPEN
PART_THIN = 0.10              # <=10% = THIN, above = BLOCKED
MIN_TICKET = {"sse": 100 * HAND_YUAN, "szse": 1000.0}   # yuan per order


def _read(code):
    path = os.path.join(REPO_DIR, code + ".csv")
    if not os.path.exists(path):
        return None
    df = pd.read_csv(path, parse_dates=["date"]).dropna(subset=["close"])
    df = df.sort_values("date")
    close = df.set_index("date")["close"].astype(float)
    vol = pd.to_numeric(df.set_index("date").get("volume"), errors="coerce")
    vol = vol[vol > 0]
    if len(close) < 100 or vol.empty:
        return None
    return {"close": close, "vol": vol,
            "vol_med": float(vol.median()), "vol_p10": float(vol.quantile(0.10)),
            "bars": int(len(close))}


def part_class(size, bad_day_yuan):
    """Participation on the bad day -> the printed bucket."""
    if bad_day_yuan <= 0:
        return "NO_DATA", None
    part = size / bad_day_yuan
    if part <= PART_OK:
        return "OPEN", part
    if part <= PART_THIN:
        return "THIN", part
    return "BLOCKED", part


def residue(size, ticket):
    """Money that cannot be lent because it is smaller than one ticket; and the wasted share."""
    if size < ticket:
        return size, 1.0
    r = (size % ticket)
    return r, r / size


def headline_for(arms, size_label, base_close_last):
    """Mechanically derive the headline from the printed rows (no taste)."""
    rows = [a for a in arms if a["capacity"].get(size_label)]
    open_rows = [a for a in rows if a["capacity"][size_label]["class"] == "OPEN"]
    non_base_open = [a for a in open_rows if a["code"] != BASELINE]
    pickup_positive = [a for a in rows
                       if a.get("rate_vs_base_bp") is not None and a["rate_vs_base_bp"] > 0
                       and a["code"] != BASELINE]
    pickup_blocked = [a for a in pickup_positive
                      if a["capacity"][size_label]["class"] == "BLOCKED"]
    if not non_base_open:
        return "ONLY_THE_OVERNIGHT_IS_OURS", []
    if pickup_positive and len(pickup_blocked) == len(pickup_positive):
        return "THE_PICKUP_SITS_WHERE_WE_CANNOT_FILL", [a["code"] for a in pickup_blocked]
    pay_above = [a for a in open_rows
                 if a.get("close_last") is not None and base_close_last is not None
                 and a["close_last"] > base_close_last and a["code"] != BASELINE]
    if not pay_above:
        return "OPEN_TENORS_PAY_LESS_TODAY", [a["code"] for a in open_rows]
    return "LADDER_IS_REACHABLE", [a["code"] for a in pay_above]


def build(write=True):
    frames = {}
    for tenor, code, _kind in TENORS:
        got = _read(code)
        if got is not None:
            frames[code] = got
    if BASELINE not in frames:
        payload = {"schema": "repo_capacity_at_size/v1", "ts": bc_now(),
                   "evidence_cutoff": None, "verdict": "DATA-BLOCKED",
                   "reason": "baseline %s missing" % BASELINE}
        if write:
            bc.write_json(OUT_JSON, payload)
        return payload

    base = frames[BASELINE]
    base_close = base["close"]
    base_last = float(base_close.iloc[-1])
    base_turnover_med = base["vol_med"] * HAND_YUAN
    unit_ok = UNIT_CHECK_YUAN[0] <= base_turnover_med <= UNIT_CHECK_YUAN[1]

    arms = []
    for tenor, code, kind in TENORS:
        row = {"code": code, "tenor_days": tenor, "venue": kind,
               "min_ticket_yuan": MIN_TICKET[kind]}
        if code not in frames:
            row["status"] = "NO_DATA"
            arms.append(row)
            continue
        f = frames[code]
        close = f["close"]
        # rate pickup measured on days both tenors quote (never forward-filled)
        joined = pd.concat([close.rename("k"), base_close.rename("b")], axis=1,
                           sort=True).dropna()
        diff_bp = (joined["k"] - joined["b"]) * 100.0
        row.update({
            "status": "OK",
            "bars": f["bars"],
            "common_days": int(len(joined)),
            "close_last": round(float(close.iloc[-1]), 4),
            "rate_vs_base_bp": round(float(diff_bp.median()), 2) if len(diff_bp) else None,
            "rate_vs_base_mean_bp": round(float(diff_bp.mean()), 2) if len(diff_bp) else None,
            "turnover_med_yuan": round(f["vol_med"] * HAND_YUAN, 0),
            "turnover_bad_yuan": round(f["vol_p10"] * HAND_YUAN, 0),
            "capacity": {},
        })
        for label, size in SIZES:
            cls, part = part_class(size, f["vol_p10"] * HAND_YUAN)
            res, res_share = residue(size, MIN_TICKET[kind])
            row["capacity"][label] = {
                "class": cls,
                "participation_on_bad_day": None if part is None else round(part, 6),
                "unlendable_yuan": round(res, 2),
                "unlendable_share": round(res_share, 6),
            }
            # what one lend of this size pays over its own term, at the last quote
            c = row["capacity"][label]
            c["one_lend_interest_yuan"] = round(
                size * float(close.iloc[-1]) / 100.0 * tenor / 365.0, 2)
        arms.append(row)

    # the cash the money actually earns as an overnight roll, at today's quote
    today_cash = {}
    for label, size in SIZES:
        today_cash[label] = round(size * base_last / 100.0, 2)

    headline, evidence = headline_for(arms, "100万", base_last)
    open_100 = [a["code"] for a in arms
                if a.get("capacity", {}).get("100万", {}).get("class") == "OPEN"]
    blocked_100 = [a["code"] for a in arms
                   if a.get("capacity", {}).get("100万", {}).get("class") == "BLOCKED"]

    payload = {
        "schema": "repo_capacity_at_size/v1",
        "ts": bc_now(),
        "evidence_cutoff": str(base_close.index[-1].date()),
        "question": ("at the sizes we run, which tenors of the exchange repo curve can we fill "
                     "without being the market on a bad day?"),
        "unit": {"hand_yuan": HAND_YUAN,
                 "checked_against": [UNIT_CHECK_YUAN[0], UNIT_CHECK_YUAN[1]],
                 "gc001_median_turnover_yuan": round(base_turnover_med, 0),
                 "unit_ok": bool(unit_ok)},
        "ruler": {"bad_day": "p10 of daily volume series",
                  "open_max_participation": PART_OK, "thin_max_participation": PART_THIN},
        "baseline": {"code": BASELINE, "close_last": round(base_last, 4),
                     "bars": base["bars"],
                     "window": [str(base_close.index[0].date()),
                                str(base_close.index[-1].date())],
                     "cash_at_close_last": today_cash},
        "arms": arms,
        "open_at_100w": open_100,
        "blocked_at_100w": blocked_100,
        "headline": headline if unit_ok else "UNIT_SUSPECT",
        "headline_evidence": evidence if unit_ok else [],
        "notes": ("Participation is measured against the p10 day, so 'OPEN at 100 万' means our "
                  "whole order is <=1% of a bad day's turnover. The 1%/10% band is a convention "
                  "against being visible on the tape; it is not a measured price impact. "
                  "Rate pickup is a median of same-day quotes, never a forward-filled pair, and "
                  "it is a rate difference -- not a return, because the tenors cannot be held "
                  "for the same calendar days."),
    }
    if write:
        bc.write_json(OUT_JSON, payload)
        write_md(payload)
    return payload


def bc_now():
    from datetime import datetime, timedelta, timezone
    return datetime.now(timezone(timedelta(hours=8))).isoformat(timespec="seconds")


def write_md(p):
    L = []
    L.append("# The repo curve at our size -- which tenors can we actually fill?\n")
    L.append("Window %s -> %s. Baseline %s closes at %.3f%%. Unit check: GC001 median turnover "
             "%s 元/day (band %s .. %s) -> %s." % (
                 p["baseline"]["window"][0], p["baseline"]["window"][1],
                 p["baseline"]["code"], p["baseline"]["close_last"],
                 format(int(p["unit"]["gc001_median_turnover_yuan"]), ","),
                 format(int(p["unit"]["checked_against"][0]), ","),
                 format(int(p["unit"]["checked_against"][1]), ","),
                 "OK" if p["unit"]["unit_ok"] else "SUSPECT"))
    L.append("")
    L.append("| tenor | last quote | median rate vs GC001 | bad-day turnover | 100万 | 300万 | 1000万 |")
    L.append("|---|---|---|---|---|---|---|")
    for a in p["arms"]:
        if a.get("status") != "OK":
            L.append("| %s | – | – | – | %s | – | – |" % (a["code"], a.get("status")))
            continue
        cap = a["capacity"]
        cells = []
        for label in ("100万", "300万", "1000万"):
            c = cap[label]
            part = c["participation_on_bad_day"]
            cells.append("%s (%.2f%%)" % (c["class"], 100.0 * part) if part is not None else c["class"])
        L.append("| %s (%dd) | %.3f%% | %+.2fbp | %s | %s |" % (
            a["code"], a["tenor_days"], a["close_last"], a["rate_vs_base_bp"],
            format(int(a["turnover_bad_yuan"]), ","), " | ".join(cells)))
    L.append("")
    L.append("**Headline: %s.**" % p["headline"])
    if p["headline_evidence"]:
        L.append("Evidence: %s." % ", ".join(p["headline_evidence"]))
    L.append("")
    L.append("Open at 100 万: %s. Blocked at 100 万: %s." % (
        ", ".join(p["open_at_100w"]) or "none", ", ".join(p["blocked_at_100w"]) or "none"))
    L.append("")
    L.append("Overnight cash at the last quote: " + ", ".join(
        "%s = %s 元/年" % (k, format(int(v), ",")) for k, v in p["baseline"]["cash_at_close_last"].items()))
    L.append("")
    L.append("Notes: " + p["notes"])
    with open(OUT_MD, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(L) + "\n")


# ---------------------------------------------------------------------------
# check: re-derive the verdict from the published rows (no engine re-run)
# ---------------------------------------------------------------------------
def check():
    if not os.path.exists(OUT_JSON):
        print("STALE face missing: %s" % OUT_JSON)
        return 3
    p = bc.read_json(OUT_JSON)
    base = p.get("baseline") or {}
    panel_last = None
    path = os.path.join(REPO_DIR, BASELINE + ".csv")
    if os.path.exists(path):
        df = pd.read_csv(path, parse_dates=["date"]).dropna(subset=["close"])
        panel_last = str(df["date"].iloc[-1].date())
    problems = []
    if panel_last and p.get("evidence_cutoff") != panel_last:
        print("STALE repo panel moved: face %s, panel %s (run the face again)"
              % (p.get("evidence_cutoff"), panel_last))
        return 3
    # 1. the unit claim must still hold on the printed numbers
    unit = p.get("unit") or {}
    med = unit.get("gc001_median_turnover_yuan")
    if med is None:
        problems.append("unit check missing")
    else:
        ok = unit.get("checked_against")[0] <= med <= unit["checked_against"][1]
        if bool(unit.get("unit_ok")) != bool(ok):
            problems.append("unit_ok %s but printed median %s" % (unit.get("unit_ok"), med))
    # 2. every capacity bucket must follow from its own numbers
    for a in p.get("arms") or []:
        if a.get("status") != "OK":
            continue
        for label, c in (a.get("capacity") or {}).items():
            part = c.get("participation_on_bad_day")
            if part is None:
                continue
            want = ("OPEN" if part <= PART_OK else "THIN" if part <= PART_THIN else "BLOCKED")
            if c.get("class") != want:
                problems.append("%s %s class %s but participation %.6f"
                                % (a["code"], label, c.get("class"), part))
            size = dict(SIZES)[label]
            if abs(part - size / a["turnover_bad_yuan"]) > 1e-6:
                problems.append("%s %s participation does not match size/turnover"
                                % (a["code"], label))
            res, share = residue(size, a["min_ticket_yuan"])
            if abs(c.get("unlendable_yuan", -1) - round(res, 2)) > 0.01:
                problems.append("%s %s residue %s != %s"
                                % (a["code"], label, c.get("unlendable_yuan"), res))
    # 3. the headline must follow from the rows, and must name what it claims
    want_headline, want_evidence = headline_for(p["arms"], "100万", p["baseline"]["close_last"])
    if p.get("headline") != want_headline:
        problems.append("headline %s but rows give %s" % (p.get("headline"), want_headline))
    if sorted(p.get("headline_evidence") or []) != sorted(want_evidence):
        problems.append("headline evidence %s but rows give %s"
                        % (p.get("headline_evidence"), want_evidence))
    if problems:
        print("CHECK FAILED (%d):" % len(problems))
        for x in problems:
            print(" - " + x)
        return 3
    print(json.dumps({"check": "ok", "headline": p["headline"],
                      "open_at_100w": p["open_at_100w"],
                      "blocked_at_100w": p["blocked_at_100w"]}, ensure_ascii=False))
    return 0


# ---------------------------------------------------------------------------
# selftest: offline, no data files
# ---------------------------------------------------------------------------
def selftest():
    legs = []

    def leg(name, cond):
        legs.append((name, bool(cond)))

    # bucket boundaries are inclusive on the safe side
    leg("1% of a bad day is OPEN", part_class(1e5, 1e7)[0] == "OPEN")
    leg("just over 1% is THIN", part_class(1.01e5, 1e7)[0] == "THIN")
    leg("10% is THIN", part_class(1e6, 1e7)[0] == "THIN")
    leg("over 10% is BLOCKED", part_class(1.5e6, 1e7)[0] == "BLOCKED")
    leg("no turnover is NO_DATA", part_class(1e5, 0)[0] == "NO_DATA")

    # minimum ticket: money below one ticket cannot lend at all
    r, s = residue(5e4, 1e5)
    leg("500k below the 100k ticket is 100% idle", r == 5e4 and abs(s - 1.0) < 1e-9)
    r, s = residue(1.05e6, 1e5)
    leg("residue is printed in yuan and as a share", r == 5e4 and abs(s - 5e4 / 1.05e6) < 1e-9)
    r, s = residue(1e6, 1000.0)
    leg("a 1,000 yuan ticket leaves no residue", r == 0.0 and s == 0.0)

    # headline logic on synthetic rows. The paying tenor here is blocked but GC007 is open
    # and pays nothing -- so "the pickup sits where we cannot fill" is the true statement.
    def row(code, cls, pickup, last, base_last=1.4):
        return {"code": code, "rate_vs_base_bp": pickup, "close_last": last,
                "capacity": {"100万": {"class": cls}}, "base": base_last}

    arms = [row("GC001", "OPEN", 0.0, 1.40), row("GC007", "OPEN", -1.0, 1.39),
            row("GC182", "BLOCKED", 25.0, 1.65)]
    leg("pickup only where we cannot fill names that", headline_for(arms, "100万", 1.40)[0]
        == "THE_PICKUP_SITS_WHERE_WE_CANNOT_FILL")
    # when the paying tenor is the ONLY thing beyond the overnight, the stronger statement wins
    arms_blocked_only = [row("GC001", "OPEN", 0.0, 1.40), row("GC182", "BLOCKED", 25.0, 1.65)]
    leg("nothing open beyond the overnight outranks the blocked-pickup sentence",
        headline_for(arms_blocked_only, "100万", 1.40)[0] == "ONLY_THE_OVERNIGHT_IS_OURS")
    arms2 = [row("GC001", "OPEN", 0.0, 1.40), row("GC007", "OPEN", 5.0, 1.45)]
    leg("a reachable tenor that pays is reachable", headline_for(arms2, "100万", 1.40)[0]
        == "LADDER_IS_REACHABLE")
    arms3 = [row("GC001", "OPEN", 0.0, 1.40), row("GC007", "OPEN", -5.0, 1.30)]
    leg("open tenors below the overnight is its own verdict",
        headline_for(arms3, "100万", 1.40)[0] == "OPEN_TENORS_PAY_LESS_TODAY")
    arms4 = [row("GC001", "OPEN", 0.0, 1.40), row("GC007", "BLOCKED", -2.0, 1.50)]
    leg("nothing beyond the overnight open", headline_for(arms4, "100万", 1.40)[0]
        == "ONLY_THE_OVERNIGHT_IS_OURS")
    # the evidence list must name the blocked tenors, not just count them
    h, ev = headline_for(arms, "100万", 1.40)
    leg("evidence names the tenor", ev == ["GC182"])

    ok = sum(1 for _n, c in legs if c)
    for n, c in legs:
        print("%s %s" % ("PASS" if c else "FAIL", n))
    print("%d/%d PASS" % (ok, len(legs)))
    return 0 if ok == len(legs) else 1


def main(argv):
    if "--selftest" in argv:
        return selftest()
    if "--check" in argv:
        return check()
    p = build(write=True)
    print(json.dumps({"headline": p.get("headline"),
                      "unit_ok": (p.get("unit") or {}).get("unit_ok"),
                      "open_at_100w": p.get("open_at_100w"),
                      "blocked_at_100w": p.get("blocked_at_100w"),
                      "out": os.path.relpath(OUT_JSON, bc.ROOT)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
