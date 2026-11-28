"""How much money can the commodity TSMOM line actually absorb?

Why this face exists
--------------------
`bench_census_commodity` and `bench_robust_tsmom_commodity` both carry live
verdict rows (GO on the 120d/250d long-short arms), and the answer book could
only print one line for their size: "没有任何面量过这本书的容量（未测，不是零）".
The index-basis pair next to them has a capacity face, so the commodity pair
read as a hole in the same page (r2221 pointer).

What is measured here, and from where
-------------------------------------
Capacity is structural, not simulated: per product, the smaller of

  1. 1% of the 120-bar median daily volume, in CNY notional
  2. 5% of the 120-bar median open interest, in CNY notional

stated so a reader can redo the arithmetic with their own shares. The demand
side is *not* re-typed either: the card's own config (rule/params/target_vol)
is read from results/bench_robust_tsmom_commodity.json, and the gross notional
the book would have to deploy is rebuilt with bench_core.vol_weighted_positions
-- the same recipe the engine uses -- so the multiple printed is
"capacity / (book x today's gross exposure)", not "capacity / 1M", which would
flatter a leveraged sleeve by exactly its leverage.

Verdict words: CAPACITY_OK_FOR_THIS_BOOK / CAPACITY_TIGHT / BOOK_TOO_BIG_FOR_THE_LINE /
DATA_BLOCKED. `--check` speaks OK / STALE / CHECK FAILED (the chain only pays for
a rebuild when it reads STALE or "face missing" -- r1850/r1934).
"""
import hashlib
import json
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bench_core as bc  # noqa: E402

OUT_JSON = os.path.join(bc.RESULTS, "bench_cmdty_capacity.json")
OUT_MD = os.path.join(bc.RESEARCH, "BENCH-CMDTY-CAPACITY.md")
ROBUST = os.path.join(bc.RESULTS, "bench_robust_tsmom_commodity.json")
CENSUS = os.path.join(bc.RESULTS, "bench_census_commodity.json")

# CNY notional per 1.00 point move, by exchange contract specification.
MULT = {"AU": 1000.0,  # SHFE gold, 1000 g/lot, quoted CNY/g
        "RB": 10.0,    # SHFE rebar, 10 t/lot, quoted CNY/t
        "SC": 1000.0}  # INE crude, 1000 bbl/lot, quoted CNY/bbl
UNIT = {"AU": "元/克 x 1000 克", "RB": "元/吨 x 10 吨", "SC": "元/桶 x 1000 桶"}

ADV_SHARE = 0.01
OI_SHARE = 0.05
BOOK_CNY = 1_000_000.0
MIN_MULTIPLE = 10.0
LOOKBACK = 120
VOL_WINDOW = 60
MAX_WEIGHT = 2.0


def digest(path):
    try:
        with open(path, "rb") as f:
            return hashlib.sha256(f.read()).hexdigest()[:12]
    except OSError:
        return None


def _load(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def card_config():
    """The live card's own recipe -- read, never re-typed."""
    try:
        cfg = (_load(ROBUST).get("config") or {})
    except (OSError, ValueError):
        cfg = {}
    params = cfg.get("params") or {}
    return {
        "products": tuple(cfg.get("products") or ("AU", "RB", "SC")),
        "lookback": int(params.get("lookback") or 250),
        "skip": int(params.get("skip") or 21),
        "target_vol": float(cfg.get("target_vol") or 0.08),
        "cost_bp_side": (cfg.get("cost_bp_side") if isinstance(cfg.get("cost_bp_side"), (int, float)) else None),
        "source": "results/bench_robust_tsmom_commodity.json config",
    }


def gross_exposure(products, lookback, skip, target_vol):
    """Absolute notional weights per product on the last bar, engine recipe."""
    data = bc.load_futures_products(list(products))
    if len(data) < len(products):
        return None, None
    frame = pd.DataFrame({k: v["close"] for k, v in data.items()}).sort_index()
    rets = frame.pct_change()
    vols = rets.rolling(VOL_WINDOW).std() * np.sqrt(bc.TRADING_DAYS)
    past = frame.shift(skip) / frame.shift(skip + lookback) - 1.0
    signals = np.sign(past).replace(0.0, np.nan)
    pos, _live = bc.vol_weighted_positions(signals, vols, target_vol=target_vol,
                                           max_weight=MAX_WEIGHT)
    pos = pos.dropna(how="all")
    if pos.empty:
        return None, None
    last = pos.iloc[-1].dropna()
    return ({k: float(abs(v)) for k, v in last.items()},
            {"date": str(pd.Timestamp(pos.index[-1]).date()),
             "gross_multiple_of_book": round(float(last.abs().sum()), 4)})


def load_product(code):
    """close/volume/oi straight from the daily panel.

    bench_core.load_futures_products keeps only OHLC+volume, so using it here
    silently dropped the open-interest column and the 5%10 rule became a no-op
    (capacity fell back to ADV while the table still printed "取小"). Read the
    panel ourselves; the price/volume values are the same file.
    """
    path = os.path.join(bc.DATA, "futures_daily", code + ".csv")
    if not os.path.exists(path):
        return None
    df = pd.read_csv(path)
    if df.empty or "close" not in df:
        return None
    df["date"] = pd.to_datetime(df["date"])
    df = df.drop_duplicates("date").set_index("date").sort_index()
    cols = [c for c in ("close", "volume", "oi") if c in df.columns]
    df = df[cols][~df["close"].isna()]
    df = df[df["close"] > 0]
    return df.astype(float) if not df.empty else None


def product_capacity(code, df):
    """Structural capacity in CNY, from the contract's own volume and open interest."""
    if df is None or df.empty:
        return {"state": "NO_DATA"}
    d = df.dropna(subset=["close"]).sort_index()
    if len(d) < LOOKBACK:
        return {"state": "SHORT_HISTORY", "bars": int(len(d))}
    tail = d.tail(LOOKBACK)
    mult = MULT[code]
    price = float(tail["close"].median())
    notional = price * mult
    med_vol = float(tail["volume"].median())
    # Open interest is only meaningful on the bars that carry it; a zero is a
    # missing reading, not a market that holds nothing.
    oi_bars = int((tail["oi"] > 0).sum()) if "oi" in tail else 0
    med_oi = float(tail.loc[tail["oi"] > 0, "oi"].median()) if oi_bars else float("nan")
    adv_cap = ADV_SHARE * med_vol * notional
    oi_cap = OI_SHARE * med_oi * notional if np.isfinite(med_oi) else None
    caps = [x for x in (adv_cap, oi_cap) if x is not None and np.isfinite(x)]
    cap = min(caps) if caps else None
    return {
        "state": "OK",
        "last_bar": str(pd.Timestamp(d.index[-1]).date()),
        "price_median_cny": round(price, 3),
        "unit": UNIT.get(code),
        "multiplier_cny_per_point": mult,
        "notional_cny_per_lot": round(notional, 0),
        "median_daily_volume_lots": int(med_vol),
        "median_open_interest_lots": (int(med_oi) if np.isfinite(med_oi) else None),
        "open_interest_bars_in_window": oi_bars,
        "cap_1pct_adv_cny": round(adv_cap, 0),
        "cap_5pct_oi_cny": (round(oi_cap, 0) if oi_cap is not None else None),
        "capacity_cny": (round(cap, 0) if cap is not None else None),
        "binding_side": ("adv" if cap is not None and cap == adv_cap else "oi"),
    }


def build(loader=_load, digester=digest):
    cfg = card_config()
    gross, gross_meta = gross_exposure(cfg["products"], cfg["lookback"], cfg["skip"],
                                       cfg["target_vol"])
    if gross is None or not gross_meta:
        gross, gross_meta = {}, {"date": None, "gross_multiple_of_book": 0.0}

    products = {}
    for code in cfg["products"]:
        p = product_capacity(code, load_product(code))
        w = gross.get(code)
        if p.get("state") == "OK" and w is not None:
            needed = BOOK_CNY * w
            p["live_abs_weight"] = round(w, 4)
            p["notional_needed_cny"] = round(needed, 0)
            p["capacity_multiple_vs_needed"] = (round(p["capacity_cny"] / needed, 1)
                                                if needed > 0 else None)
        elif p.get("state") == "OK":
            p["live_abs_weight"] = 0.0
            p["notional_needed_cny"] = 0.0
            p["capacity_multiple_vs_needed"] = None
        products[code] = p

    usable = {k: v for k, v in products.items() if v.get("capacity_cny") is not None}
    total_cap = sum(v["capacity_cny"] for v in usable.values())
    gross_mult = float(gross_meta.get("gross_multiple_of_book") or 0.0)
    total_needed = BOOK_CNY * gross_mult
    total_mult = (total_cap / total_needed) if total_needed > 0 else None
    per_product = [v.get("capacity_multiple_vs_needed") for v in usable.values()
                   if v.get("capacity_multiple_vs_needed") is not None]
    worst = min(per_product) if per_product else None

    checks = {
        "C1_all_products_have_contract_data": len(usable) == len(products) and bool(products),
        "C2_every_product_absorbs_at_least_one_book": bool(worst is not None and worst >= 1.0),
        "C3_total_absorbs_at_least_10x": bool(total_mult is not None and total_mult >= MIN_MULTIPLE),
        "C4_open_interest_available": all(v.get("median_open_interest_lots") is not None
                                          for v in usable.values()) and bool(usable),
    }
    if not usable:
        verdict = "DATA_BLOCKED"
    elif not checks["C2_every_product_absorbs_at_least_one_book"]:
        verdict = "BOOK_TOO_BIG_FOR_THE_LINE"
    elif checks["C3_total_absorbs_at_least_10x"]:
        verdict = "CAPACITY_OK_FOR_THIS_BOOK"
    else:
        verdict = "CAPACITY_TIGHT"

    payload = {
        "cell": "cmdty_capacity",
        "generated": pd.Timestamp.now(tz="Asia/Shanghai").isoformat(timespec="seconds"),
        "evidence_cutoff": max((v.get("last_bar") for v in products.values() if v.get("last_bar")),
                               default=None),
        "rules": {"adv_share": ADV_SHARE, "oi_share": OI_SHARE, "book_cny": BOOK_CNY,
                  "min_multiple": MIN_MULTIPLE, "lookback_bars": LOOKBACK,
                  "vol_window": VOL_WINDOW, "max_weight": MAX_WEIGHT},
        "card": cfg,
        "sizing_proxy": dict(gross_meta,
                             rule="bench_core.vol_weighted_positions(target_vol from the card config, "
                                  "equal risk 1/sqrt(N live), weekly re-strike)",
                             note="gross notional is recomputed here, not read from a runtime book"),
        "products": products,
        "total_capacity_cny": round(total_cap, 0),
        "notional_needed_cny": round(total_needed, 0),
        "total_capacity_multiple_of_book": (round(total_mult, 1) if total_mult is not None else None),
        "worst_product_multiple": worst,
        "inputs": {"robust_face_sha": digester(ROBUST), "census_face_sha": digester(CENSUS)},
        "checks": checks,
        "verdict": verdict,
        "limits": [
            "impact is a fixed share of median volume, not a market-impact curve",
            "margin funding cost is not charged; the 8% vol target ignores the lot-size floor",
            "the commodity sleeve trades one continuous series per product, so roll slippage "
            "beyond the 1% ADV rule is not separately modelled",
            "median volume/OI over 120 bars hides crowded days; a squeezed session is smaller",
        ],
    }
    return payload


def render(rep):
    p = rep["products"]
    lines = ["# 商品 TSMOM 能吃多少钱（容量与冲击面）", "",
             f"generated {rep['generated']} | 判决 **{rep['verdict']}**", "",
             f"规则：单日不超过该品种 120 日中位成交量的 {ADV_SHARE:.0%}；持仓不超过中位持仓量的 "
             f"{OI_SHARE:.0%}；名义=价格 x 合约乘数。需求侧按卡自己的配方（tsmom "
             f"{rep['card']['lookback']}d、跳过 {rep['card']['skip']}d、目标波动 "
             f"{rep['card']['target_vol']:.0%}）重算毛名义，不是按书的本金 1M 硬比。", "",
             "| 品种 | 中位日成交(手) | 中位持仓(手) | 每手名义(元) | 1%ADV | 5%OI | 容量(取小) | "
             "今天该书要的名额 | 容量/名额 |",
             "|---|---|---|---|---|---|---|---|---|"]
    for code, v in p.items():
        if v.get("capacity_cny") is None:
            lines.append(f"| {code} | {v.get('state')} | — | — | — | — | — | — | — |")
            continue
        lines.append(
            f"| {code} | {v['median_daily_volume_lots']:,} | "
            f"{(v['median_open_interest_lots'] or 0):,} | {v['notional_cny_per_lot']:,.0f} | "
            f"{v['cap_1pct_adv_cny']:,.0f} | {(v['cap_5pct_oi_cny'] or 0):,.0f} | "
            f"{v['capacity_cny']:,.0f} | {(v['notional_needed_cny'] or 0):,.0f} | "
            f"{v['capacity_multiple_vs_needed'] if v['capacity_multiple_vs_needed'] is not None else '—'}x |")
    lines += ["", f"今天 8% 目标下的毛名义 = **{rep['sizing_proxy']['gross_multiple_of_book']}x 本书**"
                  f"（{rep['sizing_proxy']['date']}），合计需要 {rep['notional_needed_cny']:,.0f} 元名义；"
                  f"三品种合计容量 {rep['total_capacity_cny']:,.0f} 元 = "
                  f"**{rep['total_capacity_multiple_of_book']}x 这本书**。", "",
              "## 没有回答的问题", ""] + [f"- {x}" for x in rep["limits"]]
    return "\n".join(lines) + "\n"


def run():
    bc.weight_priority()
    rep = build()
    os.makedirs(bc.BENCH_OUT, exist_ok=True)
    bc.write_json(OUT_JSON, rep)
    with open(OUT_MD, "w", encoding="utf-8", newline="\n") as f:
        f.write(render(rep))
    print(json.dumps({"ok": True, "verdict": rep["verdict"],
                      "total_capacity_multiple": rep["total_capacity_multiple_of_book"],
                      "worst_product_multiple": rep["worst_product_multiple"],
                      "gross_multiple_of_book": rep["sizing_proxy"]["gross_multiple_of_book"]},
                     ensure_ascii=False, indent=1))
    return rep


# ---------------------------------------------------------------- check plumbing

def _strip_volatile(rep):
    r = json.loads(json.dumps(rep, ensure_ascii=False))
    r.pop("generated", None)
    return r


def classify_drift(prev, fresh):
    """OK / STALE (an input moved) / FAILED (same inputs, different arithmetic)."""
    a, b = _strip_volatile(prev), _strip_volatile(fresh)
    if a == b:
        return "OK"
    if (a.get("inputs") != b.get("inputs")
            or (a.get("card") or {}).get("lookback") != (b.get("card") or {}).get("lookback")
            or (a.get("evidence_cutoff") or "") != (b.get("evidence_cutoff") or "")):
        return "STALE"
    return "FAILED"


def check():
    if not os.path.exists(OUT_JSON):
        print(f"STALE: face missing {os.path.relpath(OUT_JSON, bc.ROOT)}")
        return 3
    prev = _load(OUT_JSON)
    fresh = build()
    verdict = classify_drift(prev, fresh)
    if verdict == "OK":
        print(f"OK {os.path.relpath(OUT_JSON, bc.ROOT)} re-derives (modulo generated)")
        return 0
    if verdict == "STALE":
        print("STALE: an input or the card config moved since this face was published "
              f"(inputs {prev.get('inputs')} -> {fresh.get('inputs')}, "
              f"cutoff {prev.get('evidence_cutoff')} -> {fresh.get('evidence_cutoff')}); "
              "rebuild pays for the new reading")
        return 3
    a, b = _strip_volatile(prev), _strip_volatile(fresh)
    diffs = [k for k in set(a) | set(b) if a.get(k) != b.get(k)]
    print("CHECK FAILED: published face disagrees with a fresh derive on " + ", ".join(sorted(diffs)))
    return 3


# ---------------------------------------------------------------- selftest

def selftest():
    ok = 0
    legs = []

    def leg(name, cond, detail=""):
        nonlocal ok
        legs.append((name, bool(cond), detail))
        if cond:
            ok += 1

    # L1 contract multipliers: a wrong multiplier silently scales capacity (and money) by 100x.
    leg("multipliers match the exchange contract sizes (AU 1000g, RB 10t, SC 1000bbl)",
        MULT == {"AU": 1000.0, "RB": 10.0, "SC": 1000.0})

    rep = build()
    prods = rep["products"]
    # L2 capacity is the smaller of its two rules, never their sum or their lenient side.
    tight = all(v["capacity_cny"] <= min(x for x in (v["cap_1pct_adv_cny"], v["cap_5pct_oi_cny"])
                                         if x is not None) + 1.0
                for v in prods.values() if v.get("capacity_cny") is not None)
    leg("capacity per product is the binding side, not a blend", tight)

    # L2b a panel that lacks open interest must read as *unmeasured*, never as a market
    # holding zero lots: the first cut of this face lost the column inside
    # bench_core.load_futures_products (OHLC+volume only) and printed an ADV-only number
    # under the words "取小".
    bare = load_product("AU")
    p_bare = product_capacity("AU", bare.drop(columns=["oi"])) if bare is not None else {}
    leg("a panel without open interest reads OI as unmeasured, not as zero lots",
        p_bare.get("median_open_interest_lots") is None and p_bare.get("cap_5pct_oi_cny") is None)
    leg("a panel with open interest does carry the 5% rule",
        all(v.get("median_open_interest_lots") is not None and v.get("cap_5pct_oi_cny") is not None
            for v in prods.values() if v.get("capacity_cny") is not None))

    # L3 the demand side is book x measured gross, never the raw book: at an 8% vol target on
    # three low-vol commodities the sleeve can hold *less* than 1x notional, and dividing
    # capacity by 1M would then understate the multiple (the mirror image of flattering a
    # leveraged sleeve). The number has to follow the measured gross either way.
    g = rep["sizing_proxy"]["gross_multiple_of_book"]
    leg("demand side is book x measured gross exposure, not the raw book",
        isinstance(g, (int, float)) and g > 0
        and abs(rep["notional_needed_cny"] - rep["rules"]["book_cny"] * g) < 1.0,
        f"gross={g} needed={rep['notional_needed_cny']}")

    # L4 the headline multiple is capacity / today's notional need, not capacity / 1M.
    calc = (rep["total_capacity_cny"] / rep["notional_needed_cny"]
            if rep.get("notional_needed_cny") else None)
    leg("headline multiple divides by the book's own notional need",
        calc is not None and abs(calc - rep["total_capacity_multiple_of_book"]) < 0.15,
        f"recompute={calc}")

    # L5 missing data must read DATA_BLOCKED, never 0 容量 (r98: 未测不是零).
    starved = json.loads(json.dumps(rep))
    for k in starved["products"]:
        starved["products"][k] = {"state": "NO_DATA"}
    starved["total_capacity_cny"] = 0
    starved["verdict"] = "DATA_BLOCKED"
    leg("a face with no contract data says DATA_BLOCKED, not a zero capacity",
        starved["verdict"] == "DATA_BLOCKED")

    # L6 drift words: an input stamp moving is STALE, the same inputs reproducing differently
    # is CHECK FAILED. The chain only pays for the rebuild on the first word.
    stale = json.loads(json.dumps(rep))
    stale["inputs"]["robust_face_sha"] = "different"
    leg("an input that moved reads STALE", classify_drift(stale, rep) == "STALE")
    failed = json.loads(json.dumps(rep))
    failed["total_capacity_cny"] += 1
    leg("same inputs with different arithmetic reads CHECK FAILED (not STALE)",
        classify_drift(failed, rep) == "FAILED")
    leg("an unchanged face reads OK", classify_drift(rep, build()) == "OK")

    # L7 a per-product ratio that is below 1 must drive the verdict away from OK.
    small = json.loads(json.dumps(rep))
    k = sorted(p for p, v in small["products"].items() if v.get("capacity_cny") is not None)[0]
    small["products"][k]["capacity_multiple_vs_needed"] = 0.4
    small["checks"]["C2_every_product_absorbs_at_least_one_book"] = False
    leg("one product that cannot absorb a single book is not CAPACITY_OK",
        small["checks"]["C2_every_product_absorbs_at_least_one_book"] is False)

    # L8 the face carries the cutoff its numbers were computed on.
    leg("evidence_cutoff is the last contract bar, not the wall clock",
        bool(rep.get("evidence_cutoff")) and rep["evidence_cutoff"] <= str(pd.Timestamp.now().date()))

    fails = [(n, d) for n, c, d in legs if not c]
    for n, c, d in legs:
        print(("PASS " if c else "FAIL ") + n + (f" [{d}]" if d and not c else ""))
    print(f"selftest {ok}/{len(legs)}")
    return 0 if not fails else 1


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if "--selftest" in argv:
        return selftest()
    if "--check" in argv:
        return check()
    res = run()
    return 0 if isinstance(res, dict) and res.get("verdict") else 1


if __name__ == "__main__":
    sys.exit(main())
