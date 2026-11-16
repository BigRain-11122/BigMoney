"""Treasury futures (T/TF/TS) roll probe: the splice gap IS the calendar spread.

Why this exists (O-20261114-0024 sec.3 P2 row three, "国债期货曲线 T/TF 跨期"), and why it is
a 30-minute question rather than a panel project:

  1. 谁在付钱 -- the party paying is whoever must move a hedge out of this quarter's contract
     into next quarter's.  They sell the near contract and buy the far one; if the far one is
     rich, rolling costs them that difference every quarter.  That difference is exactly what
     a spliced main-contract series jumps over on the switch day, so the reading is already on
     our disk: data/futures_daily/{T,TF,TS}.csv, 2017 -> today.  No new data, no network.

  2. 数据偏差先解决 -- a main-contract series is glued: the switch day books the level
     difference between two contracts as if it were a return.  A holder who rolls does NOT
     book it.  So it is measured here as the roll reading itself and excluded from any return
     claim -- the same treatment `idx_fut_roll_gap` argues for index futures.

  SIGN CONVENTION (the part that is easy to get backwards): the splice gap is
  ln(P_after_switch / P_before_switch) = ln(P_far / P_near).  A long roller sells the near
  contract and buys the far one, so a far contract that is CHEAPER is a better entry --
  the long roller is PAID.  The tradeable reading is therefore `long_roll_pct =
  -annual_gap_pct`, and the criteria below are written against that sign, not against the
  raw gap.  Getting this wrong turns "we are paid 0.5%/yr" into "we are charged 0.5%/yr".

  3. 一次跑完 + 判据先冻结 (FROZEN block below, declared before the data was read).

  4. 判负即关线 -- a long-only desk that pays the gap every quarter has no line here.  The
     honest output is CLOSE plus a reusable probe, not an explanatory report.

FROZEN (declared before the data was read)
  C1 coverage  : a splice day is claimed only when that month's largest |log return| is at
                 least SPLICE_MULT times that month's median |log return| AND above
                 SPLICE_FLOOR.  Fewer than MIN_MONTHS_COVERED such months -> INSUFFICIENT:
                 the splicing convention on disk does not support this probe.
  C2 long carry: annualised `long_roll_pct` (= minus the sum of the splice gaps).
                 >= +OPEN_BAR %/yr OPEN (a long roller is paid), <= CLOSE_BAR %/yr CLOSE
                 (a long roller pays), otherwise WEAK.
  C3 agreement : the median `long_roll_pct` must carry the sign of the annual total, else WEAK
                 regardless.

  python scripts/bond_fut_roll_probe.py            # write results/bond_fut_roll_probe.json
  python scripts/bond_fut_roll_probe.py selftest   # offline synthetic legs
"""
import argparse
import calendar
import csv
import datetime as dt
import json
import math
import os
import statistics
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data", "futures_daily")
OUT = os.path.join(ROOT, "results", "bond_fut_roll_probe.json")

VARIETIES = ("T", "TF", "TS")

SPLICE_MULT = 3.0
SPLICE_FLOOR = 0.0005        # 5 bp
MIN_MONTHS_COVERED = 24
OPEN_BAR = 1.5               # %/yr, long roller is paid
CLOSE_BAR = -1.5             # %/yr, long roller pays


def load_rows(path):
    """(date, close) sorted; rows with a non-positive close are dropped, not repaired."""
    rows = []
    with open(path, "r", newline="", encoding="utf-8") as fh:
        for rec in csv.DictReader(fh):
            try:
                d = dt.date.fromisoformat((rec.get("date") or "").strip())
                c = float(rec.get("close") or 0.0)
            except (TypeError, ValueError):
                continue
            if c > 0:
                rows.append((d, c))
    rows.sort()
    return rows


def monthly_splice(rows):
    """One candidate splice day per calendar month: the month's largest move, kept only when
    it stands out from that month's own noise.  Returns per-month records."""
    by_month = {}
    for (d0, c0), (d1, c1) in zip(rows, rows[1:]):
        by_month.setdefault((d1.year, d1.month), []).append((d1, math.log(c1 / c0)))
    out = []
    for key in sorted(by_month):
        seq = by_month[key]
        med = statistics.median([abs(r) for _, r in seq])
        day, r = max(seq, key=lambda x: abs(x[1]))
        spliced = (abs(r) >= SPLICE_MULT * med) and (abs(r) >= SPLICE_FLOOR)
        out.append({
            "month": "%04d-%02d" % key,
            "day": day.isoformat(),
            "gap_pct": round(r * 100.0, 4),
            "median_abs_pct": round(med * 100.0, 4),
            "spliced": spliced,
        })
    return out


def variety_face(name, rows):
    months = monthly_splice(rows)
    spliced = [m for m in months if m["spliced"]]
    years = ((rows[-1][0] - rows[0][0]).days / 365.25) if len(rows) > 1 else 0.0
    total_log = sum(math.log(1.0 + m["gap_pct"] / 100.0) for m in spliced)
    gap_annual_pct = (math.expm1(total_log) * 100.0) / years if years > 0 else 0.0
    med_gap = statistics.median([m["gap_pct"] for m in spliced]) if spliced else 0.0
    return {
        "variety": name,
        "first": rows[0][0].isoformat() if rows else None,
        "last": rows[-1][0].isoformat() if rows else None,
        "years": round(years, 3),
        "months_seen": len(months),
        "months_spliced": len(spliced),
        "coverage": round(len(spliced) / len(months), 4) if months else 0.0,
        # the glued series: ln(far/near).  Reported so the reading can be audited, but the
        # verdict is written against the long roller's sign (-).
        "median_gap_pct": round(med_gap, 4),
        "gap_annual_pct": round(gap_annual_pct, 4),
        "median_long_roll_pct": round(-med_gap, 4),
        "long_roll_pct": round(-gap_annual_pct, 4),
        "splice_days": [{"month": m["month"], "day": m["day"], "gap_pct": m["gap_pct"]}
                        for m in spliced],
    }


def verdict_for(faces):
    sealed = [f for f in faces if f["months_spliced"] >= MIN_MONTHS_COVERED]
    if not sealed:
        return {"verdict": "INSUFFICIENT",
                "why": "no variety reaches %d identifiable splice months; the series on disk "
                       "does not expose the calendar spread this way" % MIN_MONTHS_COVERED}
    ann = statistics.median([f["long_roll_pct"] for f in sealed])
    agree = all((f["median_long_roll_pct"] > 0) == (f["long_roll_pct"] > 0) for f in sealed)
    if ann >= OPEN_BAR and agree:
        v = "OPEN"
    elif ann <= CLOSE_BAR and agree:
        v = "CLOSE"
    else:
        v = "WEAK"
    return {
        "verdict": v,
        "varieties_sealed": [f["variety"] for f in sealed],
        "median_long_roll_pct": round(ann, 4),
        "sign_agreement": agree,
        "why": ("a long roller is %s %.2f%%/yr at the median of the sealed varieties"
                % ("paid" if ann > 0 else "charged", abs(ann))),
    }


def run():
    faces = []
    for v in VARIETIES:
        path = os.path.join(DATA, v + ".csv")
        if not os.path.exists(path):
            continue
        faces.append(variety_face(v, load_rows(path)))
    payload = {
        "_what": "treasury futures monthly splice gaps read as the calendar spread a long "
                 "roller pays or is paid",
        "frozen_criteria": {
            "C1_coverage": {"splice_mult": SPLICE_MULT, "splice_floor_bp": SPLICE_FLOOR * 1e4,
                            "min_months_covered": MIN_MONTHS_COVERED},
            "C2_long_carry": {"open_bar_pct_yr": OPEN_BAR, "close_bar_pct_yr": CLOSE_BAR},
            "C3_agreement": "median gap sign must match the annual total sign",
        },
        "varieties": faces,
        "verdict": verdict_for(faces),
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=2)
    print("bond_fut_roll_probe :: verdict=%s" % payload["verdict"]["verdict"])
    for f in faces:
        print("  %-3s %s..%s  months_spliced=%d/%-3d  long_roll=%+.3f%%/yr  median_gap=%+.4f%%"
              % (f["variety"], f["first"], f["last"], f["months_spliced"], f["months_seen"],
                 f["long_roll_pct"], f["median_gap_pct"]))
    print("  why: %s" % payload["verdict"]["why"])
    print("  -> %s" % os.path.relpath(OUT, ROOT))
    return 0


def _synth(year=2024, months=36, monthly_drift=0.0, splice=0.0035):
    """A glued series with a known splice: the second business day of each calendar month
    jumps by `splice`, so every calendar month carries exactly one."""
    rows = []
    price = 100.0
    y, m = year, 1
    for _ in range(months):
        days = [dt.date(y, m, d) for d in range(1, calendar.monthrange(y, m)[1] + 1)]
        workdays = [d for d in days if d.weekday() < 5]
        for k, d in enumerate(workdays):
            price *= math.exp(monthly_drift / len(workdays) + (splice if k == 1 else 0.0))
            rows.append((d, price))
        y, m = (y + 1, 1) if m == 12 else (y, m + 1)
    return rows


def selftest():
    legs = []

    def leg(name, ok, detail=""):
        legs.append((name, bool(ok), detail))

    rows = _synth()
    months = monthly_splice(rows)
    leg("L1 one candidate month per calendar month", len(months) == 36, "%d" % len(months))
    leg("L2 every month is spliced", all(m["spliced"] for m in months),
        "%d/%d" % (sum(m["spliced"] for m in months), len(months)))
    gaps = [m["gap_pct"] for m in months]
    leg("L3 gap reads back the injected splice",
        abs(statistics.median(gaps) - 0.35) < 0.02, "median %.4f%%" % statistics.median(gaps))

    face = variety_face("SYN", rows)
    leg("L4 the glued gap is the sum of its splice days",
        abs(face["gap_annual_pct"] - 4.47) < 0.6,
        "%.3f%%/yr over %.2fy" % (face["gap_annual_pct"], face["years"]))
    leg("L5 the long roller's sign is the gap's opposite, not the gap",
        abs(face["long_roll_pct"] + face["gap_annual_pct"]) < 1e-6
        and abs(face["median_long_roll_pct"] + face["median_gap_pct"]) < 1e-6,
        "long %+.3f vs gap %+.3f" % (face["long_roll_pct"], face["gap_annual_pct"]))
    leg("L6 a far contract that is richer charges the long roller (CLOSE)",
        verdict_for([face])["verdict"] == "CLOSE", verdict_for([face])["verdict"])

    paid = variety_face("SYN2", _synth(splice=-0.0035))
    leg("L7 a far contract that is cheaper pays the long roller (OPEN)",
        verdict_for([paid])["verdict"] == "OPEN", verdict_for([paid])["verdict"])

    flat = variety_face("SYN3", _synth(splice=0.0))
    leg("L7b a series with no splice claims no months",
        flat["months_spliced"] == 0, "%d" % flat["months_spliced"])
    leg("L8 no splice -> INSUFFICIENT rather than a zero verdict",
        verdict_for([flat])["verdict"] == "INSUFFICIENT", verdict_for([flat])["verdict"])

    short = variety_face("SYN4", _synth(months=12))
    leg("L9 12 months cannot seal a variety", verdict_for([short])["verdict"] == "INSUFFICIENT",
        verdict_for([short])["verdict"])

    noise_rows = _synth(splice=0.0)
    noise_months = monthly_splice(noise_rows)
    leg("L10 a quiet month does not invent a splice",
        sum(m["spliced"] for m in noise_months) == 0,
        "%d" % sum(m["spliced"] for m in noise_months))

    leg("L11 monthly drift alone does not look like a splice",
        monthly_splice(_synth(splice=0.0, monthly_drift=0.02))[0]["spliced"] is False, "")

    bad = sum(1 for _, ok, _ in legs if not ok)
    for name, ok, detail in legs:
        print("%s %s%s" % ("PASS" if ok else "FAIL", name, (" :: " + detail) if detail else ""))
    print("bond_fut_roll_probe selftest %d/%d" % (len(legs) - bad, len(legs)))
    return 0 if bad == 0 else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", nargs="?", default="run")
    args = ap.parse_args()
    if args.cmd == "selftest":
        return selftest()
    return run()


if __name__ == "__main__":
    sys.exit(main())
