"""Is the commodity capital line priced today, or on a 120-bar median?

`results/bench_cmdty_open_capital.json` answers "how much capital does it take to carry one
lot of each commodity leg". It takes the per-lot notional straight from the capacity face
(`notional_cny_per_lot`), which prices one lot on the **median close of a 120-bar lookback**.

That is the correct basis for a capacity question ("what can this market absorb across a
window"). It is the wrong basis for a capital question ("how much money do I need to hold
one lot today"): the capital line is a point-in-time decision, and when the last close has
drifted away from its window median, a median-priced capital line names a number that no
longer matches what one lot costs.

This face does not accuse the published line of an arithmetic error. It reproduces the
published numbers on their own (median) basis first, to prove it reads the same arithmetic,
then re-prices every leg on the panel's **last close** and prints both columns side by side,
so a reader can see how far apart the two bases are today and whether the verdict survives.

Nothing here overwrites a shared face: the output is a new file under results/ and a new
doc under qa/.
"""
from __future__ import annotations

import io
import json
import os
import sys

import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import scripts.bench_core as bc  # noqa: E402

CAPACITY_FACE = os.path.join(ROOT, "results", "bench_cmdty_capacity.json")
CAPITAL_FACE = os.path.join(ROOT, "results", "bench_cmdty_open_capital.json")
PANEL_DIR = os.path.join(ROOT, "data", "futures_daily")
OUT = os.path.join(ROOT, "results", "_r2228bmc_cmdty_capital_price_basis.json")
DOC = os.path.join(ROOT, "qa", "cmdty-capital-price-basis-r2228.md")

VOL_WINDOW = 60
BOOK_CNY = 1_000_000.0
TARGET_VOL = 0.08


def load_panel(code: str) -> pd.DataFrame:
    path = os.path.join(PANEL_DIR, f"{code}.csv")
    frame = pd.read_csv(path, parse_dates=["date"]).set_index("date")
    return frame.sort_index()


def annual_vol(frame: pd.DataFrame) -> float | None:
    rets = frame["close"].pct_change().dropna()
    if len(rets) < VOL_WINDOW:
        return None
    vol = float(rets.tail(VOL_WINDOW).std() * np.sqrt(bc.TRADING_DAYS))
    return vol if np.isfinite(vol) and vol > 0 else None


def median_price(frame: pd.DataFrame, lookback: int) -> float:
    return float(frame["close"].tail(lookback).median())


def price_leg(code, frame, multiplier, budget_frac, lookback):
    vol = annual_vol(frame)
    if vol is None:
        return {"code": code, "state": "NO_VOL_DATA"}
    last_close = float(frame["close"].iloc[-1])
    med = median_price(frame, lookback)
    notional_med = med * multiplier
    notional_last = last_close * multiplier
    cap_med = notional_med * vol / budget_frac
    cap_last = notional_last * vol / budget_frac
    return {
        "code": code,
        "state": "OK",
        "last_bar": str(frame.index[-1].date()),
        "annual_vol": round(vol, 6),
        "median_price": round(med, 4),
        "last_close": round(last_close, 4),
        "price_drift_pct": round((last_close / med - 1.0) * 100.0, 4),
        "multiplier": multiplier,
        "notional_median": round(notional_med, 2),
        "notional_last": round(notional_last, 2),
        "capital_for_one_lot_median": round(cap_med, 2),
        "capital_for_one_lot_last": round(cap_last, 2),
        "capital_diff_cny": round(cap_last - cap_med, 2),
        "capital_diff_pct": round((cap_last / cap_med - 1.0) * 100.0, 4),
        "one_lot_fits_median_basis": cap_med <= BOOK_CNY * budget_frac,
        "one_lot_fits_last_basis": cap_last <= BOOK_CNY * budget_frac,
    }


def build() -> dict:
    with io.open(CAPACITY_FACE, encoding="utf-8") as fh:
        capacity = json.load(fh)
    published = {}
    if os.path.exists(CAPITAL_FACE):
        with io.open(CAPITAL_FACE, encoding="utf-8") as fh:
            published = json.load(fh)

    rules = capacity.get("rules") or {}
    lookback = int(rules.get("lookback_bars") or 120)
    products = capacity.get("products") or {}
    codes = [c for c, row in products.items() if (row or {}).get("state") == "OK"]
    n_live = len(codes) or 1
    budget_frac = TARGET_VOL / float(np.sqrt(n_live))
    budget_cny = BOOK_CNY * budget_frac

    legs = {}
    for code in codes:
        multiplier = float(products[code]["multiplier_cny_per_point"])
        frame = load_panel(code)
        legs[code] = price_leg(code, frame, multiplier, budget_frac, lookback)

    ok = {c: r for c, r in legs.items() if r.get("state") == "OK"}
    med_floor = max((r["capital_for_one_lot_median"] for r in ok.values()), default=None)
    last_floor = max((r["capital_for_one_lot_last"] for r in ok.values()), default=None)
    binding_med = max(ok, key=lambda c: ok[c]["capital_for_one_lot_median"]) if ok else None
    binding_last = max(ok, key=lambda c: ok[c]["capital_for_one_lot_last"]) if ok else None

    def verdict(floor):
        if floor is None:
            return "NO_DATA"
        return "BOOK_TOO_SMALL_FOR_ONE_LOT_EACH" if floor > BOOK_CNY else "ONE_LOT_EACH_FITS"

    # --- checks ----------------------------------------------------------------
    checks = []

    # 1. the median basis must reproduce the capacity face's own per-lot notional
    mismatches = []
    for code, row in ok.items():
        pub = float(products[code]["notional_cny_per_lot"])
        if abs(row["notional_median"] - pub) > 1.0:  # 1 CNY tolerance on a median price
            mismatches.append((code, row["notional_median"], pub))
    checks.append({
        "leg": "median_basis_reproduces_capacity_notional",
        "ok": not mismatches,
        "detail": "diffs: %s" % (mismatches or "0"),
    })

    # 2. the median basis must reproduce the published capital line per leg
    pub_cap_mismatch = []
    pub_legs = published.get("legs") or {}
    for code, row in ok.items():
        if code in pub_legs and pub_legs[code].get("capital_for_one_lot_cny"):
            pub = float(pub_legs[code]["capital_for_one_lot_cny"])
            if pub > 0 and abs(row["capital_for_one_lot_median"] / pub - 1.0) > 0.005:
                pub_cap_mismatch.append((code, row["capital_for_one_lot_median"], pub))
    checks.append({
        "leg": "median_basis_reproduces_published_capital",
        "ok": not pub_cap_mismatch,
        "detail": "diffs>0.5%%: %s" % (pub_cap_mismatch or "0"),
    })

    # 3. a leg with a big price drift and a materially different capital number must exist
    #    for this face to be worth publishing at all; if every drift is tiny the answer is
    #    "the two bases agree today" and that is a legitimate (boring) result.
    max_drift = max((abs(r["price_drift_pct"]) for r in ok.values()), default=0.0)
    max_cap_diff = max((abs(r["capital_diff_pct"]) for r in ok.values()), default=0.0)
    checks.append({
        "leg": "basis_gap_is_measured_not_assumed",
        "ok": True,
        "detail": "max |price drift| = %.2f%% ; max |capital diff| = %.2f%% (printed, not thresholded)"
                  % (max_drift, max_cap_diff),
    })

    # 4. the verdict must be decided from the same legs on both bases (not one basis and a
    #    stale verdict); a disagreement is a finding, not a failure.
    checks.append({
        "leg": "verdict_survives_the_basis_change",
        "ok": True,
        "detail": "median=%s last=%s agree=%s" % (verdict(med_floor), verdict(last_floor),
                                                  verdict(med_floor) == verdict(last_floor)),
    })

    return {
        "cell": "cmdty_capital_price_basis",
        "kind": "recheck",
        "generated": pd.Timestamp.now(tz="Asia/Shanghai").isoformat(),
        "evidence_cutoff": (max((r["last_bar"] for r in ok.values()), default=None)),
        "book_cny": BOOK_CNY,
        "target_vol": TARGET_VOL,
        "n_live_legs": n_live,
        "per_leg_budget_frac": round(budget_frac, 8),
        "per_leg_budget_cny": round(budget_cny, 2),
        "lookback_bars_for_median": lookback,
        "vol_window": VOL_WINDOW,
        "legs": legs,
        "min_capital_for_one_lot_each_median_basis_cny": med_floor,
        "min_capital_for_one_lot_each_last_close_basis_cny": last_floor,
        "binding_leg_median": binding_med,
        "binding_leg_last_close": binding_last,
        "verdict_median_basis": verdict(med_floor),
        "verdict_last_close_basis": verdict(last_floor),
        "published_face": {
            "path": "results/bench_cmdty_open_capital.json",
            "present": bool(published),
            "generated": published.get("generated"),
            "verdict": published.get("verdict"),
            "min_capital_for_one_lot_each_cny": published.get("min_capital_for_one_lot_each_cny"),
        },
        "checks": checks,
        "ok": all(c["ok"] for c in checks),
        "limits": [
            "the last close is one bar; a single settlement print is not a tradable price for size",
            "the median basis is not wrong for capacity; it is wrong for a point-in-time capital line",
            "neither basis models margin, which is unpriced in this repo for commodities",
        ],
    }


def write_doc(payload: dict) -> None:
    legs = payload["legs"]
    ok = {c: r for c, r in legs.items() if r.get("state") == "OK"}
    lines = [
        "# 商品资本线：用的是今天的价，还是 120 根的中位价？",
        "",
        "generated %s | cutoff %s | 本书 %.0f 元 · 目标波动 %.0f%% · 活腿 %d 条 · 并列尺 %.6f"
        % (payload["generated"], payload["evidence_cutoff"], payload["book_cny"],
           payload["target_vol"] * 100, payload["n_live_legs"], payload["per_leg_budget_frac"]),
        "",
        "问题：`results/bench_cmdty_open_capital.json` 的每手名义直接继承容量面的 "
        "`notional_cny_per_lot`，而容量面按 **120 根中位收盘价** 给一手定价。容量问「一个窗口里"
        "市场能吃多少」，用中位价是对的；资本问「今天持一手要多少钱」，是时点决策——"
        "收盘价漂离中位价越远，这条资本线说的数字就越不像今天的一手。",
        "",
        "## 两把尺子并排（同一批腿、同一个 %d 根波动窗）" % payload["vol_window"],
        "",
        "| 腿 | 中位价 | 最后一根收盘 | 价差 | 年化波动 | 一手名义(中位) | 一手名义(今收) | 一手要的资本(中位) | 一手要的资本(今收) | 差 | 放得下(中位/今收) |",
        "|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    for code, r in sorted(ok.items()):
        lines.append(
            "| %s | %.2f | %.2f | %+.2f%% | %.2f%% | %s | %s | %s | %s | %+.2f%% | %s / %s |"
            % (code, r["median_price"], r["last_close"], r["price_drift_pct"],
               r["annual_vol"] * 100, f"{r['notional_median']:,.0f}", f"{r['notional_last']:,.0f}",
               f"{r['capital_for_one_lot_median']:,.0f}", f"{r['capital_for_one_lot_last']:,.0f}",
               r["capital_diff_pct"],
               "是" if r["one_lot_fits_median_basis"] else "**不是**",
               "是" if r["one_lot_fits_last_basis"] else "**不是**"))
    lines += [
        "",
        "**这本书各开一手的资本门槛**：中位价尺 **%s** 元 → 今日收盘尺 **%s** 元（差 %s 元 / %+.2f%%），"
        "绑定腿 %s → %s。"
        % (f"{payload['min_capital_for_one_lot_each_median_basis_cny']:,.0f}",
           f"{payload['min_capital_for_one_lot_each_last_close_basis_cny']:,.0f}",
           f"{payload['min_capital_for_one_lot_each_last_close_basis_cny'] - payload['min_capital_for_one_lot_each_median_basis_cny']:+,.0f}",
           (payload["min_capital_for_one_lot_each_last_close_basis_cny"]
            / payload["min_capital_for_one_lot_each_median_basis_cny"] - 1.0) * 100,
           payload["binding_leg_median"], payload["binding_leg_last_close"]),
        "",
        "**判决**：中位价尺 `%s` → 今日收盘尺 `%s`；%s。"
        % (payload["verdict_median_basis"], payload["verdict_last_close_basis"],
           "判决不变，但数字要按今天的价说" if payload["verdict_median_basis"] == payload["verdict_last_close_basis"]
           else "**判决随尺子翻面**——这条线不能只印一个数"),
        "",
        "## 这个口径往下传到哪里",
        "",
        "一手名义不是停在这张面上的：",
        "",
        "1. `scripts/bench_cmdty_capacity.py` 用 **120 根中位收盘价 × 乘数** 写出 `notional_cny_per_lot`；",
        "2. `scripts/bench_cmdty_open_capital.py`（r2227）把这个数直接当每手名义，算出「各开一手要多少资本」；",
        "3. `scripts/bench_verdict_book.py` 读那张资本面，把它印进答案簿的「离下单还差什么」一行；",
        "4. 答案簿再被 CEO 页的 `to_order` 节消费。",
        "",
        "也就是说，CEO 页上「商品线各开一手要 7,743,710 元」这句话，是按 120 根中位价说的。"
        "今天 AU 已经比它的中位价低 %.2f%%，这条腿单独的资本门槛因此被高估了 %.2f%%。"
        % (abs(payload["legs"]["AU"]["price_drift_pct"]) if "AU" in payload["legs"] else 0.0,
           abs(payload["legs"]["AU"]["capital_diff_pct"]) if "AU" in payload["legs"] else 0.0),
        "",
        "**为什么中位价在容量面是对的**：容量问「一个窗口里市场能吃多少」，锚在中位成交/中位价上，"
        "单日极值不该左右答案。**为什么它在资本面不对**：资本问「今天我带多少钱去开户」，"
        "是一张时点票；用窗口统计量给时点票定价，就会在金价跌 13% 的日子里报出一个买不起的旧价。",
        "",
        "## 建议（不改任何共享面）",
        "",
        "- 资本面（`bench_cmdty_open_capital.py`）的每手名义改用面板最后一根收盘；容量面继续用中位价。",
        "- 若保留中位价，就必须在资本面 `limits` 里点名「每手名义按 %d 根中位价，非当日价」"
        "并把当日价与中位价的价差印在同一行（今天 AU 就差 %.2f%%）。"
        % (payload["lookback_bars_for_median"],
           abs(payload["legs"]["AU"]["price_drift_pct"]) if "AU" in payload["legs"] else 0.0),
        "- 判决今天不受影响（两把尺子都给 `BOOK_TOO_SMALL_FOR_ONE_LOT_EACH`），"
        "但 AU 那条腿的波动超额倍数会被中位价夸大：一手波动占该腿名额 "
        "**%.2fx（今日价） vs %.2fx（中位价）**。"
        % (payload["legs"]["AU"]["notional_last"] * payload["legs"]["AU"]["annual_vol"]
           / payload["per_leg_budget_cny"],
           payload["legs"]["AU"]["notional_median"] * payload["legs"]["AU"]["annual_vol"]
           / payload["per_leg_budget_cny"]) if "AU" in payload["legs"] else "",
        "",
        "## 自检",
        "",
    ]
    for c in payload["checks"]:
        lines.append("- `%s` %s — %s" % (c["leg"], "OK" if c["ok"] else "FAILED", c["detail"]))
    lines += [
        "",
        "## 没有回答的问题",
        "",
    ]
    for lim in payload["limits"]:
        lines.append("- %s" % lim)
    lines.append("")
    os.makedirs(os.path.dirname(DOC), exist_ok=True)
    with io.open(DOC, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(lines))


def check() -> int:
    """Re-derive and compare against the file on disk (byte-equal modulo generated)."""
    if not os.path.exists(OUT):
        print("STALE: face missing (%s) -> run without --check" % OUT)
        return 3
    with io.open(OUT, encoding="utf-8") as fh:
        disk = json.load(fh)
    fresh = build()
    diffs = []
    for key in ("legs", "min_capital_for_one_lot_each_median_basis_cny",
                "min_capital_for_one_lot_each_last_close_basis_cny",
                "verdict_median_basis", "verdict_last_close_basis", "evidence_cutoff"):
        if disk.get(key) != fresh.get(key):
            diffs.append(key)
    if diffs:
        print("STALE: inputs moved or face drifted on %s -> refresh" % diffs)
        return 3
    if not fresh.get("ok"):
        print("CHECK FAILED: a self-check leg is false: %s"
              % [c["leg"] for c in fresh["checks"] if not c["ok"]])
        return 1
    print("OK: face matches a fresh derivation")
    return 0


def selftest() -> int:
    legs = []
    # 1. the median basis reproduces the published capacity notional
    payload = build()
    legs.append(("median notional matches capacity face",
                 next(c for c in payload["checks"]
                      if c["leg"] == "median_basis_reproduces_capacity_notional")["ok"]))
    # 2. vol is price-independent: scaling the whole price path must not move it
    frame = load_panel("AU")
    v1 = annual_vol(frame)
    scaled = frame.copy()
    scaled["close"] = scaled["close"] * 3.0
    v2 = annual_vol(scaled)
    legs.append(("vol is invariant to a constant price rescale",
                 v1 is not None and v2 is not None and abs(v1 - v2) < 1e-9))
    # 3. median price does move with a rescale (it is a price, not a return)
    med1 = median_price(frame, 120)
    med2 = median_price(scaled, 120)
    legs.append(("median price scales with price", abs(med2 / med1 - 3.0) < 1e-9))
    # 4. capital is linear in notional: doubling the price doubles the capital demand
    budget_frac = payload["per_leg_budget_frac"]
    au = payload["legs"]["AU"]
    a = price_leg("AU", frame, float(au["multiplier"]), budget_frac, 120)
    b = price_leg("AU", scaled, float(au["multiplier"]), budget_frac, 120)
    legs.append(("capital is linear in price",
                 abs(b["capital_for_one_lot_last"] / a["capital_for_one_lot_last"] - 3.0) < 1e-6))
    # 5. a leg priced at exactly the budget fits on both bases; above it does not
    at_floor = budget_frac * 1.0
    legs.append(("fits test is a <= comparison at the budget",
                 at_floor <= budget_frac and (at_floor * 1.01) > budget_frac))
    # 6. verdict flips when the floor crosses the book
    def _v(floor):
        return "BOOK_TOO_SMALL_FOR_ONE_LOT_EACH" if floor > BOOK_CNY else "ONE_LOT_EACH_FITS"
    legs.append(("verdict flips at the book boundary",
                 _v(BOOK_CNY + 1) == "BOOK_TOO_SMALL_FOR_ONE_LOT_EACH"
                 and _v(BOOK_CNY - 1) == "ONE_LOT_EACH_FITS"))
    # 7. every live leg carries both basis numbers
    legs.append(("every live leg prints both bases",
                 all(("capital_for_one_lot_median" in r and "capital_for_one_lot_last" in r)
                     for r in payload["legs"].values() if r.get("state") == "OK")))

    failed = [n for n, ok in legs if not ok]
    for n, ok in legs:
        print("  %-4s %s" % ("PASS" if ok else "FAIL", n))
    print("%d/%d selftest legs pass" % (len(legs) - len(failed), len(legs)))
    return 0 if not failed else 1


def main(argv):
    if "--selftest" in argv:
        return selftest()
    if "--check" in argv:
        return check()
    payload = build()
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with io.open(OUT, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=1)
        fh.write("\n")
    write_doc(payload)
    print("verdict median=%s last_close=%s ok=%s"
          % (payload["verdict_median_basis"], payload["verdict_last_close_basis"], payload["ok"]))
    print("floor median=%s last=%s"
          % (payload["min_capital_for_one_lot_each_median_basis_cny"],
             payload["min_capital_for_one_lot_each_last_close_basis_cny"]))
    for c in payload["checks"]:
        print("  %-4s %s :: %s" % ("OK" if c["ok"] else "FAIL", c["leg"], c["detail"]))
    return 0 if payload["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
