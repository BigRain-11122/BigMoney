"""IDX_FUT_CARRY_CAPITAL — translate the index-futures carry into money per unit of capital.

Parent face: results/idx_fut_basis.json (r1685) measured the discount premium as a
percent of *contract notional*: IC +4.16%/yr, IM +6.01%/yr, IF +0.80%, IH +1.74%.
Notional percent is not money. One contract is 0.8-1.3 million CNY of index; a
1,000,000 CNY account cannot buy that with cash -- it posts margin and carries the
index's own risk. This face answers the only question a capital allocator asks:
how much per year does 100万 / 300万 / 1000万 actually earn, and how far is it from
a margin call.

What this face does NOT do: it never re-derives the carry (reads the parent JSON),
never claims a Sharpe from a risk premium, and never pretends to know a fee
schedule it cannot cite -- roll cost is a sensitivity band, not a number.

Frozen reading rules (written before the numbers were read):
  R1  size is set by risk, not by the margin box. lots = floor(capital * vol_target /
      (multiplier * price * index_vol)); the margin constraint is a ceiling, never
      the target. A book that fills its margin is not sized, it is levered.
  R2  a lot you cannot afford at the vol target is not small, it is absent: when
      lots == 0, print the capital that one lot would need, not a fractional position.
  R3  margin-call distance is printed as "the index must fall X% before the account
      is wiped", per position, never annualised and never blended into a return.

Subcommands:
  run      — deterministic, local-only; writes results/idx_fut_carry_capital.json.
  selftest — hermetic synthetic checks of R1/R2/R3 and the arithmetic.
"""
import json
import math
import os
import statistics
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

from idx_fut_basis import PAIRS, TRADING_DAYS, read_csv_rows  # noqa: E402

PARENT = os.path.join(ROOT, "results", "idx_fut_basis.json")
FUT_DIR = os.path.join(ROOT, "data", "futures_daily")
IDX_DIR = os.path.join(ROOT, "data", "index_daily")
REPO_PATH = os.path.join(ROOT, "data", "repo_daily", "GC001.csv")
OUT = os.path.join(ROOT, "results", "idx_fut_carry_capital.json")

MULTIPLIER = {"IF": 300, "IH": 300, "IC": 200, "IM": 200}
MARGIN_RATE = 0.15          # declared: exchange standard 12% + broker buffer; see notes
MARGIN_USE = 0.60           # never post more than 60% of capital as margin
VOL_TARGET = 0.08           # same target the adopted ETF book runs
ROLLS_PER_YEAR = 4          # quarterly contracts
ROLL_COST_BPS = (0, 10, 25, 50)   # per roll, round-trip fees + slippage sensitivity
CAPITAL_TIERS = (1_000_000, 3_000_000, 5_000_000, 10_000_000)
VOL_LOOKBACK = 1240         # ~5 years of index daily returns
CARRY_MIN_PCT = 3.0         # V1: net per capital must clear 3%/yr
# The parent quotes three central tendencies of the same basis series. Which one is
# fed in decides the money, so all three are priced and the declared one is named.
CARRY_READINGS = ("median_ann_pct", "trimmed_mean_ann_pct", "mean_ann_pct")
DECLARED_READING = "median_ann_pct"   # what parent verdict.carries[].net_carry_pct uses
LEV_CAP = 3.0               # V2: notional may not exceed 3x capital
STRESS_MAX_PCT = 30.0       # V3: the index's own worst drawdown may not cost 30% of capital


def index_vol(index_code, lookback=VOL_LOOKBACK):
    """Annualised stdev of daily log returns over the last `lookback` rows."""
    path = os.path.join(IDX_DIR, index_code + ".csv")
    rows = read_csv_rows(path)
    closes = [float(r["close"]) for r in rows if r.get("close")]
    closes = closes[-(lookback + 1):]
    rets = [math.log(closes[k] / closes[k - 1]) for k in range(1, len(closes)) if closes[k - 1] > 0]
    if len(rets) < 60:
        return None
    return statistics.stdev(rets) * math.sqrt(TRADING_DAYS)


def last_close(fut):
    rows = read_csv_rows(os.path.join(FUT_DIR, fut + ".csv"))
    for r in reversed(rows):
        try:
            return str(r["date"])[:10], float(r["close"])
        except (KeyError, TypeError, ValueError):
            continue
    return None, None


def cash_rate():
    """GC001 mean over the current year -- the honest yield on idle margin cash."""
    rows = read_csv_rows(REPO_PATH)
    if not rows:
        return None, None
    year = str(rows[-1]["date"])[:4]
    vals = [float(r["close"]) for r in rows if str(r["date"])[:4] == year and r.get("close")]
    if not vals:
        return None, year
    return statistics.fmean(vals) / 100.0, year


def size_position(capital, cv, vol, vol_target=VOL_TARGET, margin_rate=MARGIN_RATE,
                  margin_use=MARGIN_USE):
    """R1/R2: risk sets the size; margin is only a ceiling."""
    lots_risk = int(capital * vol_target / (cv * vol)) if vol > 0 else 0
    lots_margin = int(capital * margin_use / (cv * margin_rate)) if cv > 0 else 0
    lots = max(0, min(lots_risk, lots_margin))
    needed = (cv * vol / vol_target) if vol > 0 else None   # capital for exactly one lot
    return {"lots_risk": lots_risk, "lots_margin": lots_margin, "lots": lots,
            "one_lot_capital_needed": needed}


def build_tier(capital, cv, vol, carry_pct, cash, roll_bps_list, mdd_pct=0.0,
               carry_by_reading=None):
    s = size_position(capital, cv, vol)
    lots = s["lots"]
    row = {"capital_cny": capital, "lots": lots, "lots_by_risk": s["lots_risk"],
           "lots_by_margin": s["lots_margin"],
           "one_lot_capital_needed_cny": (round(s["one_lot_capital_needed"])
                                          if s["one_lot_capital_needed"] else None)}
    if lots <= 0:
        # R2: absent, and say what it would take
        return row
    notional = lots * cv
    margin = notional * MARGIN_RATE
    carry_cny = notional * carry_pct / 100.0
    cash_cny = (capital - margin) * cash
    roll = {bps: notional * bps / 10000.0 * ROLLS_PER_YEAR for bps in roll_bps_list}
    row.update({
        "notional_cny": round(notional),
        "notional_x_capital": round(notional / capital, 2),
        "margin_cny": round(margin),
        "margin_pct_of_capital": round(margin / capital * 100, 1),
        "carry_cny": round(carry_cny),
        "roll_cost_cny_by_bps": {str(k): round(v) for k, v in roll.items()},
        "cash_cny": round(cash_cny),
        "net_pct_of_capital": {str(k): round((carry_cny - v + cash_cny) / capital * 100, 2)
                               for k, v in roll.items()},
        # Same money under each parent reading. All three are printed because the
        # median is the most flattering of them and V1 sits close to the bar.
        "net_pct_of_capital_by_reading": {
            name: (None if c is None else
                   round((notional * c / 100.0 + cash_cny - roll[10]) / capital * 100, 2))
            for name, c in (carry_by_reading or {}).items()},
        # R3: two distances, printed separately. A margin call is a fixed 15% fall
        # (the posted margin is gone); the account is wiped only if the loss outruns
        # ALL the capital, which for a small position can be more than the index can
        # ever fall in one move -- so that one is allowed to read "never".
        "margin_call_fall_pct": round(MARGIN_RATE * 100, 1),
        "account_wipe_fall_pct": (round(capital / notional * 100, 1)
                                  if capital / notional <= 1.0 else None),
        "account_wipe_note": (None if capital / notional <= 1.0 else
                              "notional is %.0f%% of capital: no single index fall wipes it"
                              % (notional / capital * 100)),
        "vol_contrib_pct": round(notional * vol / capital * 100, 1),
        # V3's input: replay the index's own worst drawdown on this position.
        # A carry premium is paid for holding the index; this is the bill.
        "stress_loss_pct_of_capital": round(abs(mdd_pct) / 100.0 * notional / capital * 100, 1),
    })
    return row


def judge(faces, vol_target=VOL_TARGET):
    """Frozen V1/V2/V3 on the first tier that can actually hold a lot.

    Reading the verdict off a fixed tier would print "no lot" for a book that is
    merely smaller than one contract; the gate that matters is the one applied to
    the smallest capital that can trade at all.
    """
    out = {}
    for fut, f in faces.items():
        mid = next((t for t in f["tiers"] if t["lots"] > 0), None)
        if not mid:
            out[fut] = {"V1": False, "V2": None, "V3": None,
                        "why": "no tier in the table can afford one lot at the vol target",
                        "first_affordable_tier_cny": None, "ADMIT": False}
            continue
        v1 = mid["net_pct_of_capital"]["10"] >= CARRY_MIN_PCT
        # V2 is a leverage cap, not a vol check: R1 already pins vol contribution to
        # the target by construction, so a "vol <= target" gate would be a tautology.
        # What R1 does NOT cap is the notional multiple, and that is what path risk
        # (consecutive limit-down days on the index) actually scales with.
        v2 = mid["notional_x_capital"] <= LEV_CAP
        # V3 replays the index's own worst drawdown on this position: the carry is
        # payment for holding the index, and this is what holding it has already cost.
        v3 = mid["stress_loss_pct_of_capital"] <= STRESS_MAX_PCT
        by = mid.get("net_pct_of_capital_by_reading") or {}
        v1_by = {name: (None if by.get(name) is None else by[name] >= CARRY_MIN_PCT)
                 for name in CARRY_READINGS}
        admit_by = {name: (None if v1_by[name] is None else bool(v1_by[name] and v2 and v3))
                    for name in CARRY_READINGS}
        seen = {v for v in v1_by.values() if v is not None}
        out[fut] = {"V1": v1, "V2": v2, "V3": v3, "ADMIT": bool(v1 and v2 and v3),
                    "V1_by_reading": v1_by,
                    "ADMIT_by_reading": admit_by,
                    # a verdict that only one of the three readings supports is a
                    # verdict about the estimator, not about the trade
                    "ruler_stable": len(seen) <= 1,
                    "ADMIT_every_reading": bool(v1 and v2 and v3 and admit_by
                                                and all(v for v in admit_by.values()
                                                        if v is not None)),
                    "first_affordable_tier_cny": mid["capital_cny"],
                    "read_on_tier": mid["capital_cny"]}
    return out


def build():
    with open(PARENT, "r", encoding="utf-8") as f:
        parent = json.load(f)
    cash, cash_year = cash_rate()
    # The parent already subtracted the index's own appreciation (the ETF that would
    # otherwise be held accrues dividends the price index does not). Re-reading the
    # raw median here would hand the engine money the tracker already earns -- so the
    # parent's derived net_carry_pct is the input, and the raw readings are only a
    # disclosure band around it.
    parent_carries = {c.get("fut"): c for c in parent.get("verdict", {}).get("carries", [])}
    faces = {}
    for fut, e in parent["pairs"].items():
        if e.get("status") != "ok":
            continue
        code = PAIRS[fut][0]
        vol = index_vol(code)
        day, price = last_close(fut)
        if not vol or not price:
            continue
        cv = float(price) * MULTIPLIER[fut]
        pc = parent_carries.get(fut) or {}
        drift = float(pc.get("drift_pct") or 0.0)
        carry = pc.get("net_carry_pct")
        if carry is None:
            carry = float(e["carry"][DECLARED_READING]) - drift   # named fallback
            carry_src = "fallback: parent carry[%s] - drift (parent verdict missing)" % DECLARED_READING
        else:
            carry_src = "parent verdict.carries[%s].net_carry_pct" % fut
        carry = float(carry)
        carry_by_reading = {}
        for name in CARRY_READINGS:
            g = (e.get("carry") or {}).get(name)
            carry_by_reading[name] = None if g is None else round(float(g) - drift, 3)
        carry_by_reading[DECLARED_READING] = round(carry, 3)
        mdd = float(e.get("index_max_drawdown_pct") or 0.0)
        faces[fut] = {
            "index": code,
            "index_name": PAIRS[fut][1],
            "price_date": day,
            "price": price,
            "multiplier": MULTIPLIER[fut],
            "contract_value_cny": round(cv),
            "index_vol_pct": round(vol * 100, 2),
            "carry_net_ann_pct": carry,
            "carry_net_source": carry_src,
            "carry_net_by_reading": carry_by_reading,
            "carry_per_unit_vol": round(carry / (vol * 100), 3),
            "index_max_drawdown_pct": mdd,
            "parent_last_2y_median_ann_pct": e.get("last_2y_median_ann_pct"),
            "tiers": [build_tier(c, cv, vol, carry, cash, ROLL_COST_BPS, mdd,
                                 carry_by_reading=carry_by_reading)
                      for c in CAPITAL_TIERS],
        }
    return {
        "generated": __import__("datetime").datetime.now().isoformat(timespec="seconds"),
        "evidence_cutoff": max(f["price_date"] for f in faces.values()) if faces else None,
        "inputs": {
            "parent_face": os.path.relpath(PARENT, ROOT).replace("\\", "/"),
            "parent_generated": parent.get("generated"),
            "cash_rate_pct": round(cash * 100, 3) if cash is not None else None,
            "cash_rate_year": cash_year,
            "cash_rate_source": "data/repo_daily/GC001.csv yearly mean close",
            "margin_rate": MARGIN_RATE,
            "margin_rate_note": "declared constant: exchange standard plus broker buffer; "
                                "not read from a source file, so every tier also reports "
                                "lots_by_margin so a different rate can be re-read",
            "margin_use": MARGIN_USE,
            "vol_target": VOL_TARGET,
            "rolls_per_year": ROLLS_PER_YEAR,
            "roll_cost_bps_sensitivity": list(ROLL_COST_BPS),
            "capital_tiers": list(CAPITAL_TIERS),
            "vol_lookback_days": VOL_LOOKBACK,
            "carry_readings": list(CARRY_READINGS),
            "declared_reading": DECLARED_READING,
        },
        "rules": {
            "R1": "lots = min(risk budget / (cv * index_vol), margin ceiling); risk sets the size",
            "R2": "lots == 0 -> report one_lot_capital_needed instead of a fractional position",
            "R3": "margin_call_fall_pct is a fixed 15% fall; account_wipe_fall_pct is "
                  "capital/notional and reads null when no single fall can wipe it",
            "R4": "carry input = parent net_carry_pct (median basis minus control drift); "
                  "median/trimmed/mean are all priced and a verdict that only one of "
                  "them supports is flagged ruler_stable=false",
        },
        "faces": faces,
        "verdict": judge(faces),
    }


def selftest():
    ok = []

    def leg(cond, name):
        assert cond, name
        ok.append(name)

    cv, vol = 1_200_000.0, 0.22
    # R1: risk budget binds first at 100万 (not the margin box)
    s = size_position(1_000_000, cv, vol)
    leg(s["lots_risk"] == 0 and s["lots"] == 0, "R1 risk budget refuses a lot the margin box would allow")
    leg(s["lots_margin"] >= 0, "R1 margin ceiling computed")
    # 300万 is still short of one lot at the vol target; 400万 is not
    s3 = size_position(3_000_000, cv, vol)
    leg(s3["lots"] == 0, "R1 300万 still cannot hold a lot (0.91 lots at 8% target / 22% vol)")
    s4 = size_position(4_000_000, cv, vol)
    leg(s4["lots"] == 1, "R1 400万 holds exactly one lot at 8% target / 22% vol")
    # R2: the one-lot capital is the number a reader can act on
    leg(abs(s["one_lot_capital_needed"] - cv * vol / VOL_TARGET) < 1, "R2 one-lot capital = cv*vol/target")

    # arithmetic of a tier
    t = build_tier(4_000_000, cv, vol, 4.0, 0.013, ROLL_COST_BPS)
    leg(t["lots"] == 1, "tier carries the size from R1")
    leg(t["carry_cny"] == round(cv * 0.04), "carry = notional * carry_pct")
    leg(t["net_pct_of_capital"]["0"] > t["net_pct_of_capital"]["50"], "higher roll cost lowers net")
    leg(t["margin_pct_of_capital"] <= MARGIN_USE * 100 + 0.5, "margin stays under the declared cap")

    # R3: wipe-out distance is capital/notional, monotone in size
    leg(abs(t["margin_call_fall_pct"] - 15.0) < 1e-9 and t["account_wipe_fall_pct"] is None,
        "R3 a 1-lot book on 400万 is called at -15% but a single fall never wipes it")
    mid5 = build_tier(5_000_000, cv, vol, 4.0, 0.013, ROLL_COST_BPS, mdd_pct=-40.0)
    t_mdd = build_tier(4_000_000, cv, vol, 4.0, 0.013, ROLL_COST_BPS, mdd_pct=-40.0)
    leg(mid5["lots"] == 1 and mid5["stress_loss_pct_of_capital"] < t_mdd["stress_loss_pct_of_capital"],
        "R3 same position, more capital -> the same index fall costs a smaller share of it")
    big = build_tier(10_000_000, cv, vol, 4.0, 0.013, ROLL_COST_BPS, mdd_pct=-40.0)
    leg(big["lots"] > t_mdd["lots"] and big["stress_loss_pct_of_capital"] > t_mdd["stress_loss_pct_of_capital"],
        "R3 more lots at the same target -> the index drawdown costs more, not less")

    # V-gates: a fat carry with an unaffordable lot is still not admitted
    faces = {"X": {"tiers": [{"capital_cny": 3_000_000, "lots": 0}]}}
    j = judge(faces)
    leg(j["X"]["ADMIT"] is False and j["X"]["why"].startswith("no tier"),
        "V: unaffordable is not small, it is absent")

    # V2 is a leverage cap: a 4x-notional book fails even with a fat carry
    hot = {"capital_cny": 4_000_000, "lots": 3, "notional_x_capital": 4.0,
           "net_pct_of_capital": {"10": 9.0}, "vol_contrib_pct": 22.0,
           "stress_loss_pct_of_capital": 10.0}
    j2 = judge({"X": {"tiers": [hot]}})
    leg(j2["X"]["V2"] is False and j2["X"]["V1"] is True,
        "V2 is the leverage cap, not a second vote on the carry")
    # and the same book at 2x is admitted on V2
    warm = dict(hot, notional_x_capital=2.0)
    leg(judge({"X": {"tiers": [warm]}})["X"]["V2"] is True, "V2 admits 2x notional")

    # R4: the same money under three readings of the same series
    band = {"median_ann_pct": 11.0, "trimmed_mean_ann_pct": 9.0, "mean_ann_pct": 6.0}
    t3 = build_tier(4_000_000, cv, vol, 11.0, 0.013, ROLL_COST_BPS, carry_by_reading=band)
    nets = t3["net_pct_of_capital_by_reading"]
    leg(nets["median_ann_pct"] > nets["trimmed_mean_ann_pct"] > nets["mean_ann_pct"],
        "R4 three readings of the same series price three different amounts of money")
    # a verdict only the median supports is not a stable verdict
    split = dict(t3, net_pct_of_capital_by_reading=nets, notional_x_capital=0.30,
                 stress_loss_pct_of_capital=12.0, vol_contrib_pct=8.0)
    j3 = judge({"X": {"tiers": [split]}})["X"]
    leg(j3["V1"] is True and j3["V1_by_reading"]["mean_ann_pct"] is False
        and j3["ruler_stable"] is False and j3["ADMIT_every_reading"] is False,
        "R4 a verdict that hangs on the median alone is flagged unstable")
    # missing reading is named, not silently filled with the median
    part = dict(t3, net_pct_of_capital_by_reading={"median_ann_pct": nets["median_ann_pct"],
                                                   "mean_ann_pct": None},
                notional_x_capital=0.30, stress_loss_pct_of_capital=12.0, vol_contrib_pct=8.0)
    j4 = judge({"X": {"tiers": [part]}})["X"]
    leg(j4["V1_by_reading"]["mean_ann_pct"] is None and j4["V1_by_reading"]["median_ann_pct"] is True,
        "R4 an absent reading stays absent instead of borrowing the median")
    return ok


def main(argv):
    cmd = (argv[1] if len(argv) > 1 else "run").lower()
    if cmd == "selftest":
        legs = selftest()
        print("selftest: %d legs PASS" % len(legs))
        for name in legs:
            print("  [PASS] " + name)
        return 0
    face = build()
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(face, f, ensure_ascii=False, indent=1)
    print("cash %.3f%% (%s)  evidence_cutoff %s"
          % (face["inputs"]["cash_rate_pct"] or 0, face["inputs"]["cash_rate_year"], face["evidence_cutoff"]))
    for fut, f in face["faces"].items():
        print("%s %-7s px %.1f cv %.0f万 vol %.1f%% carry %+.2f%%/yr"
              % (fut, f["index_name"], f["price"], f["contract_value_cny"] / 10000,
                 f["index_vol_pct"], f["carry_net_ann_pct"]))
        for t in f["tiers"]:
            if t["lots"] == 0:
                print("    %8.0f万: no lot (one lot needs %.0f万 at 8%% target)"
                      % (t["capital_cny"] / 10000, (t["one_lot_capital_needed_cny"] or 0) / 10000))
            else:
                print("    %8.0f万: %d lot(s) %.2fx notional  net %+.2f%% (10bp roll)  vol %.0f%%"
                      "  hist-drawdown costs %.1f%% of capital"
                      % (t["capital_cny"] / 10000, t["lots"], t["notional_x_capital"],
                         t["net_pct_of_capital"]["10"], t["vol_contrib_pct"],
                         t["stress_loss_pct_of_capital"]))
        v = face["verdict"][fut]
        band = f.get("carry_net_by_reading") or {}
        print("    net carry by reading: %s"
              % "  ".join("%s %+.2f%%" % (k.replace("_ann_pct", ""), band[k] or 0)
                          for k in CARRY_READINGS if band.get(k) is not None))
        print("    verdict ADMIT=%s (V1 %s / V2 %s / V3 %s)  ruler_stable=%s  every-reading=%s"
              % (v["ADMIT"], v["V1"], v["V2"], v["V3"], v["ruler_stable"],
                 v["ADMIT_every_reading"]))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
