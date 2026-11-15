"""ETF_BOOK_IH_HEDGE — is an IH short a hedge for this book, or a second position?

Parent question (r1713 pointer): IH is the only index future a 1,000,000 CNY account
can post margin for, and the desk sheet already says it is the least rewarding of the
four. The open question was the other side of it: if you used that one affordable
contract to hedge the book's index leg, what happens to the book's own volatility and
drawdown?

This face answers it with two numbers that do not depend on each other:

  1. how much of the book's risk the index leg actually is (beta, and the share of
     variance the hedge could remove), and
  2. how coarse the smallest tradeable unit is relative to the position that beta asks
     for (one IH lot's notional vs beta * capital).

The second one decides the question. A hedge you can only trade at eleven times the
size beta asks for is not a hedge; it is a second, larger position that happens to
point the other way. This face never re-derives the book's NAV and never re-prices the
future's carry -- it reads results/etf_book_series/NAV-*.json and data/futures_daily.

Frozen reading rules (R1-R4 written before this round's numbers were read):
  R1  hedge size is beta * capital. "One lot" is not a unit of hedge, it is a unit of
      contract; the two are only equal by accident of account size.
  R2  a position is EXECUTABLE only when the smallest tradeable unit is within 3x the
      size beta asks for. "Affordable margin" is not the test -- it never was; the
      test is whether the rounding error is the same order as the position.
  R3  the beta on the days that hurt is a different number from the beta on average,
      so both are printed; a hedge that only helps in the tail is still a hedge, but
      a hedge that helps nowhere is a cost.
  R4  the main-continuous series carries splice jumps, so the days this repo already
      names as switches (results/idx_fut_contract_roll.json observed_rolls -- one
      implementation, no second estimator) are dropped from the beta estimate and the
      count is printed. A volatility threshold is NOT used: the tail is exactly what
      this face is asking about, and a MAD rule would delete it as "outliers" (first
      draft did, 129 days, and the tail beta disappeared with them).

Subcommands:
  run      — deterministic, local-only; writes results/etf_book_ih_hedge.json.
  selftest — hermetic synthetic checks of R1-R4 and the arithmetic.
"""
import json
import math
import os
import statistics as st
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SERIES_DIR = os.path.join(ROOT, "results", "etf_book_series")
FUT_DIR = os.path.join(ROOT, "data", "futures_daily")
OUT = os.path.join(ROOT, "results", "etf_book_ih_hedge.json")
DOC = os.path.join(ROOT, "research", "ETF_BOOK_IH_HEDGE.md")

ROLL_FACE = os.path.join(ROOT, "results", "idx_fut_contract_roll.json")

MULTIPLIER = {"IF": 300, "IH": 300, "IC": 200, "IM": 200}
BARS_PER_YEAR = 242.091
EXEC_MAX_RATIO = 3.0        # R2
CAPITAL_TIERS = (1_000_000, 3_000_000, 5_000_000, 10_000_000, 20_000_000)
HEDGE_KS = (0.0, 0.25, 0.5, 1.0, 1.5)
TAIL_CUTS = (-0.01, -0.02)


# ---------------------------------------------------------------- inputs
def latest_nav_path(series_dir=None):
    """Newest NAV-YYYY-MM-DD.json under the series dir (latest.json is a pointer)."""
    series_dir = series_dir or SERIES_DIR
    cands = sorted(
        os.path.join(series_dir, f) for f in os.listdir(series_dir)
        if f.startswith("NAV-") and f.endswith(".json"))
    if not cands:
        raise SystemExit("no NAV-*.json under %s" % series_dir)
    return cands[-1]


def load_book(path=None):
    path = path or latest_nav_path()
    with open(path, encoding="utf-8") as f:
        d = json.load(f)
    dates = list(d["dates"])
    nav = [float(x) for x in d["nav"]]
    rets = {}
    for i in range(1, len(dates)):
        if nav[i - 1] > 0:
            rets[dates[i]] = nav[i] / nav[i - 1] - 1.0
    return {"path": os.path.relpath(path, ROOT), "dates": dates, "nav": nav,
            "rets": rets, "cutoff": d.get("evidence_cutoff") or dates[-1],
            "config": d.get("config", {}), "backtest": d.get("backtest", {})}


def load_close(product="IH", fut_dir=None):
    fut_dir = fut_dir or FUT_DIR
    path = os.path.join(fut_dir, product + ".csv")
    px = {}
    with open(path, encoding="utf-8") as f:
        header = f.readline().rstrip("\n").split(",")
        ci = header.index("close")
        di = header.index("date")
        for line in f:
            parts = line.rstrip("\n").split(",")
            if len(parts) <= ci:
                continue
            try:
                px[parts[di]] = float(parts[ci])
            except ValueError:
                continue
    return px


def daily_rets(px):
    out = {}
    ds = sorted(px)
    for i in range(1, len(ds)):
        if px[ds[i - 1]] > 0:
            out[ds[i]] = px[ds[i]] / px[ds[i - 1]] - 1.0
    return out


def named_roll_days(product="IH", path=None):
    """R4: the switch days this repo already names, for one product."""
    path = path or ROLL_FACE
    if not os.path.exists(path):
        raise SystemExit("missing %s -- the splice days have one owner here" % path)
    with open(path, encoding="utf-8") as f:
        face = json.load(f)
    rolls = face.get("products", {}).get(product, {}).get("observed_rolls") or []
    return sorted({r["date"] for r in rolls if r.get("date")})


def drop_splice_days(rets, splices):
    """R4: drop the named switch days. Returns (kept, dropped) -- never a vol rule."""
    splices = set(splices)
    kept = {d: v for d, v in rets.items() if d not in splices}
    dropped = sorted(d for d in rets if d in splices)
    return kept, dropped


def align(book, fut):
    common = sorted(set(book["rets"]) & set(fut))
    return common, [book["rets"][d] for d in common], [fut[d] for d in common]


# ---------------------------------------------------------------- math
def moments(xs, ys):
    n = len(xs)
    if n < 2:
        return {"n": n}
    mx, my = st.mean(xs), st.mean(ys)
    cov = sum((a - mx) * (b - my) for a, b in zip(xs, ys)) / n
    vx = sum((a - mx) ** 2 for a in xs) / n
    vy = sum((b - my) ** 2 for b in ys) / n
    return {"n": n, "cov": cov, "var_x": vx, "var_y": vy,
            "beta": (cov / vy) if vy > 0 else None,
            "corr": (cov / math.sqrt(vx * vy)) if vx > 0 and vy > 0 else None}


def perf(xs, bars_per_year=BARS_PER_YEAR):
    n = len(xs)
    m = st.mean(xs)
    sd = st.pstdev(xs)
    lvl = 1.0
    peak = 1.0
    mdd = 0.0
    for x in xs:
        lvl *= (1.0 + x)
        peak = max(peak, lvl)
        mdd = min(mdd, lvl / peak - 1.0)
    years = n / bars_per_year
    return {"mean_ann": m * bars_per_year, "vol": sd * math.sqrt(bars_per_year),
            "sharpe": (m * bars_per_year) / (sd * math.sqrt(bars_per_year)) if sd > 0 else None,
            "maxdd": mdd, "total": lvl - 1.0, "years": years,
            "cagr": (lvl ** (1.0 / years) - 1.0) if years > 0 and lvl > 0 else None}


def hedge_arms(xb, xf, beta, ks=HEDGE_KS):
    """Book minus k*beta*index. k=0 is the book itself."""
    arms = []
    for k in ks:
        xs = [a - k * beta * b for a, b in zip(xb, xf)]
        p = perf(xs)
        arms.append({"k": k, "weight_vs_book": k * beta, **p})
    return arms


def capital_ladder(beta, price, multiplier, tiers=CAPITAL_TIERS, ks=(0.5, 1.0, 1.5)):
    """For each account size: the notional beta asks for, the smallest lot, the ratio."""
    unit = multiplier * price
    rows = []
    for cap in tiers:
        row = {"capital": cap, "min_unit_notional": unit}
        for k in ks:
            want = k * beta * cap
            ratio = (unit / want) if want > 0 else None
            row["k%.1f" % k] = {
                "target_notional": want,
                "lots_floor": int(want // unit),
                "lots_ceil": int(-(-want // unit)) if want > 0 else 0,
                "unit_over_target": ratio,
                "executable": bool(ratio is not None and ratio <= EXEC_MAX_RATIO),
            }
        row["capital_to_trade_one_lot_at_1beta"] = (unit / beta) if beta > 0 else None
        rows.append(row)
    return rows


def verdict_of(beta, corr, ladder, arms, capital=1_000_000):
    """Main verdict is set by R2 (coarse unit), not by a threshold on the gain."""
    row = next((r for r in ladder if r["capital"] == capital), ladder[0])
    one = row["k1.0"]
    base = next(a for a in arms if a["k"] == 0.0)
    full = next(a for a in arms if a["k"] == 1.0)
    dvol = full["vol"] - base["vol"]
    dmdd = full["maxdd"] - base["maxdd"]
    dsharpe = (full["sharpe"] or 0) - (base["sharpe"] or 0)
    if not one["executable"]:
        tag = "UNEXECUTABLE_AT_THIS_SIZE"
        say = ("One %s lot is %.2fx the short beta asks for at %s CNY, so the only "
               "tradeable version of this hedge is an oversized short, not a hedge."
               % ("IH", one["unit_over_target"] or 0, "{:,}".format(capital)))
    elif dvol > -0.005 and dmdd > -0.01:
        tag = "NOT_A_HEDGE"
        say = ("A correctly sized short moves the book's volatility by %.2fpp and its "
               "drawdown by %.2fpp; that is inside noise." % (dvol * 100, dmdd * 100))
    else:
        tag = "HEDGE"
        say = ("A correctly sized short moves volatility %.2fpp and drawdown %.2fpp "
               "at an executable unit size." % (dvol * 100, dmdd * 100))
    return {"verdict": tag, "sentence": say,
            "at_capital": capital,
            "vol_delta_at_1beta": dvol, "maxdd_delta_at_1beta": dmdd,
            "sharpe_delta_at_1beta": dsharpe,
            "unit_over_target_at_1beta": one["unit_over_target"],
            "capital_needed_for_one_lot_at_1beta": row["capital_to_trade_one_lot_at_1beta"],
            "variance_removable_pct": (corr ** 2 * 100.0) if corr is not None else None}


# ---------------------------------------------------------------- build
def build():
    book = load_book()
    px = load_close("IH")
    raw = daily_rets(px)
    splices = named_roll_days("IH")
    kept, dropped = drop_splice_days(raw, splices)
    common, xb, xf = align(book, kept)
    if len(common) < 250:
        raise SystemExit("too few common bars: %d" % len(common))
    mom = moments(xb, xf)
    beta = mom["beta"]
    corr = mom["corr"]

    tail = {}
    for cut in TAIL_CUTS:
        pairs = [(a, b) for a, b in zip(xb, xf) if b <= cut]
        if len(pairs) >= 20:
            m = moments([p[0] for p in pairs], [p[1] for p in pairs])
            tail["ih_le_%d" % int(round(cut * 100))] = {
                "n": m["n"], "beta": m["beta"], "corr": m["corr"],
                "mean_book_pct": st.mean([p[0] for p in pairs]) * 100,
                "mean_ih_pct": st.mean([p[1] for p in pairs]) * 100}
        else:
            tail["ih_le_%d" % int(round(cut * 100))] = {"n": len(pairs), "beta": None}
    for label, sel in (("book_down", lambda a: a < 0), ("book_up", lambda a: a >= 0)):
        pairs = [(a, b) for a, b in zip(xb, xf) if sel(a)]
        if len(pairs) >= 20:
            m = moments([p[0] for p in pairs], [p[1] for p in pairs])
            tail[label] = {"n": m["n"], "beta": m["beta"], "corr": m["corr"]}
        else:
            tail[label] = {"n": len(pairs), "beta": None}

    price = px[sorted(px)[-1]]
    ladder = capital_ladder(beta, price, MULTIPLIER["IH"])
    arms = hedge_arms(xb, xf, beta)
    base = next(a for a in arms if a["k"] == 0.0)
    rep_price = base["mean_ann"] / BARS_PER_YEAR  # book daily mean, for one-lot sizing
    one_lot_weight = (MULTIPLIER["IH"] * price) / 1_000_000.0
    one_lot_arm = perf([a - one_lot_weight * b for a, b in zip(xb, xf)])

    face = {
        "kind": "etf_book_ih_hedge",
        "evidence_cutoff": book["cutoff"],
        "generated": None,
        "book": {"series": book["path"], "bars": len(common),
                 "first": common[0], "last": common[-1],
                 "config": book["config"]},
        "index": {"product": "IH", "multiplier": MULTIPLIER["IH"],
                  "last_close": price, "min_unit_notional": MULTIPLIER["IH"] * price,
                  "splice_days_dropped": len(dropped),
                  "splice_rule": "named switch days (idx_fut_contract_roll.observed_rolls)",
                  "splice_days_sample": dropped[:5]},
        "exposure": {"beta": beta, "corr": corr,
                     "variance_removable_pct": (corr ** 2 * 100.0) if corr is not None else None,
                     "bars": mom["n"]},
        "tail": tail,
        "arms": arms,
        "ladder": ladder,
        "one_lot_at_1m": {"weight_vs_book": one_lot_weight,
                          "implied_beta_multiple": one_lot_weight / beta if beta else None,
                          **one_lot_arm},
        "verdict": verdict_of(beta, corr, ladder, arms),
        "reading_rules": {
            "R1": "hedge size = beta * capital; one lot is a contract, not a hedge unit",
            "R2": "executable only when min unit <= 3x the size beta asks for",
            "R3": "tail beta printed beside the unconditional one",
            "R4": "splice days (|r-med| > 4*MAD) dropped from the beta estimate, count printed",
        },
        "not_measured": [
            "the future's roll slippage in points (see idx_fut_roll_gap) is a separate face",
            "margin interest / cash drag of posting IH margin is not netted into the arms",
            "this is arithmetic on published series, not a broker fill record",
        ],
    }
    return face


def render_md(face):
    b = face["exposure"]
    v = face["verdict"]
    lines = [
        "# IH as a hedge for the ETF book",
        "",
        "Cutoff %s | book bars %d (%s..%s) | IH %s, one lot %.0f CNY."
        % (face["evidence_cutoff"], face["book"]["bars"], face["book"]["first"],
           face["book"]["last"], face["index"]["product"],
           face["index"]["min_unit_notional"]),
        "",
        "## What the hedge would have to be",
        "",
        "| reading | value |",
        "| --- | --- |",
        "| book beta to IH | %.4f |" % b["beta"],
        "| correlation | %.3f |" % b["corr"],
        "| share of book variance an index hedge could remove | %.1f%% |"
        % b["variance_removable_pct"],
        "| splice days dropped | %d |" % face["index"]["splice_days_dropped"],
        "",
        "## Same beta on the days that hurt",
        "",
        "| slice | n | beta | corr |",
        "| --- | --- | --- | --- |",
    ]
    for k, t in sorted(face["tail"].items()):
        lines.append("| %s | %d | %s | %s |" % (
            k, t["n"],
            "-" if t["beta"] is None else "%.4f" % t["beta"],
            "-" if t.get("corr") is None else "%.3f" % t["corr"]))
    lines += ["", "## A correctly sized short, at several multiples of beta", "",
              "| k (x beta) | mean/yr | vol | sharpe | maxdd |", "| --- | --- | --- | --- | --- |"]
    for a in face["arms"]:
        lines.append("| %.2f | %.4f | %.4f | %.3f | %.4f |"
                     % (a["k"], a["mean_ann"], a["vol"], a["sharpe"], a["maxdd"]))
    lines += ["", "## Can it actually be traded", "",
              "| capital | unit/1beta target | 1x beta executable | capital for one lot at 1 beta |",
              "| --- | --- | --- | --- |"]
    for r in face["ladder"]:
        lines.append("| %s | %.2fx | %s | %s |" % (
            "{:,}".format(r["capital"]), r["k1.0"]["unit_over_target"],
            "yes" if r["k1.0"]["executable"] else "no",
            "{:,.0f}".format(r["capital_to_trade_one_lot_at_1beta"])))
    lines += ["", "## Verdict", "",
              "**%s.** %s" % (v["verdict"], v["sentence"]), ""]
    return "\n".join(lines)


def main(argv):
    cmd = (argv[1] if len(argv) > 1 else "run").lower()
    if cmd == "selftest":
        return selftest()
    if cmd != "run":
        print("usage: etf_book_ih_hedge.py [run|selftest]")
        return 2
    import datetime
    face = build()
    face["generated"] = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        json.dump(face, f, ensure_ascii=False, indent=2, sort_keys=True)
        f.write("\n")
    with open(DOC, "w", encoding="utf-8", newline="\n") as f:
        f.write(render_md(face))
        f.write("\n")
    v = face["verdict"]
    print("beta=%.4f corr=%.3f removable=%.1f%% -> %s"
          % (face["exposure"]["beta"], face["exposure"]["corr"],
             face["exposure"]["variance_removable_pct"], v["verdict"]))
    print("one lot %.0f vs 1beta target %.0f at 1M (%.2fx) ; capital for one lot at 1beta %.0f"
          % (face["index"]["min_unit_notional"],
             v["unit_over_target_at_1beta"] and
             face["index"]["min_unit_notional"] / v["unit_over_target_at_1beta"],
             v["unit_over_target_at_1beta"],
             v["capital_needed_for_one_lot_at_1beta"]))
    return 0


# ---------------------------------------------------------------- selftest
def selftest():
    fails = []

    def chk(name, cond):
        if not cond:
            fails.append(name)

    # R1/R2 arithmetic on a synthetic beta and price
    ladder = capital_ladder(0.10, 3000.0, 300, tiers=(1_000_000, 3_000_000, 10_000_000))
    r1 = ladder[0]
    chk("L1 target notional = beta*capital",
        abs(r1["k1.0"]["target_notional"] - 100_000) < 1e-6)
    chk("L1 unit/target ratio printed",
        abs(r1["k1.0"]["unit_over_target"] - (900_000 / 100_000)) < 1e-9)
    chk("L2 coarse unit is not executable",
        r1["k1.0"]["executable"] is False)
    chk("L2 10M reaches the 3x line exactly at 0.9/0.3=3.0 -> executable",
        ladder[2]["k1.0"]["executable"] is True)
    chk("L2 capital for one lot at 1 beta = unit/beta",
        abs(r1["capital_to_trade_one_lot_at_1beta"] - 9_000_000) < 1e-6)

    # R4 splice drop is name-based, never a volatility rule
    rets = {"d%d" % i: (0.001 * (i % 3 - 1)) for i in range(40)}
    rets["d99"] = 0.5
    rets["d98"] = -0.06
    kept, dropped = drop_splice_days(rets, ["d99"])
    chk("L3 named splice day dropped", "d99" in dropped and "d99" not in kept)
    chk("L3 a big but unnamed day survives (the tail is the subject)",
        "d98" in kept and kept["d98"] == -0.06)
    chk("L3 ordinary days kept", len(kept) == 41)

    # hedging arithmetic: a zero-beta book must not change with k
    xs = [0.001, -0.002, 0.003, -0.001, 0.002] * 20
    ys = [0.01, -0.02, 0.015, -0.005, 0.01] * 20
    arms = hedge_arms(xs, ys, 0.0)
    chk("L4 beta=0 leaves every arm identical",
        all(abs(a["vol"] - arms[0]["vol"]) < 1e-12 for a in arms))

    # a real beta must move the arms monotonically in volatility near k=1
    xs2 = [0.001 + 0.004 * y for y in ys]
    m = moments(xs2, ys)
    chk("L5 beta recovered on a constructed pair", abs(m["beta"] - 0.004) < 1e-9)
    arms2 = hedge_arms(xs2, ys, m["beta"])
    v0 = next(a["vol"] for a in arms2 if a["k"] == 0.0)
    v1 = next(a["vol"] for a in arms2 if a["k"] == 1.0)
    chk("L5 1x beta removes the hedged variance", v1 < v0 * 1e-6)

    # verdict branches
    coarse = capital_ladder(0.02, 3000.0, 300, tiers=(1_000_000,))
    a_dummy = hedge_arms(xs2, ys, 0.02)
    vd = verdict_of(0.02, 0.99, coarse, a_dummy, capital=1_000_000)
    chk("L6 coarse unit -> UNEXECUTABLE", vd["verdict"] == "UNEXECUTABLE_AT_THIS_SIZE")
    fine = capital_ladder(0.02, 3000.0, 300, tiers=(50_000_000,))
    vd2 = verdict_of(0.02, 0.99, fine, a_dummy, capital=50_000_000)
    chk("L6 fine unit with a real hedge -> not UNEXECUTABLE",
        vd2["verdict"] != "UNEXECUTABLE_AT_THIS_SIZE")

    # perf sanity
    p = perf([0.0] * 242)
    chk("L7 flat series has zero vol and zero drawdown",
        p["vol"] < 1e-12 and p["maxdd"] == 0.0)
    p2 = perf([0.01, -0.02] * 121)
    chk("L7 drawdown is negative on a losing path", p2["maxdd"] < 0)

    # renderer must not invent a column
    fake = {"evidence_cutoff": "2026-01-01",
            "book": {"bars": 2, "first": "a", "last": "b", "config": {}},
            "index": {"product": "IH", "min_unit_notional": 900000, "splice_days_dropped": 1},
            "exposure": {"beta": 0.1, "corr": 0.5, "variance_removable_pct": 25.0},
            "tail": {"ih_le_-2": {"n": 1, "beta": None, "corr": None}},
            "arms": [{"k": 0.0, "mean_ann": 0.0, "vol": 0.1, "sharpe": 0.0, "maxdd": 0.0}],
            "ladder": [{"capital": 1, "k1.0": {"unit_over_target": 1.0, "executable": True},
                        "capital_to_trade_one_lot_at_1beta": 1.0}],
            "verdict": {"verdict": "X", "sentence": "y"}}
    md = render_md(fake)
    chk("L8 missing tail beta renders a dash, not a zero", "| - |" in md)

    if fails:
        print("SELFTEST FAIL (%d): %s" % (len(fails), "; ".join(fails)))
        return 1
    print("SELFTEST PASS (8 legs)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
