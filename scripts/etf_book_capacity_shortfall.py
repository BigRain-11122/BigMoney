#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""ETF book -- when the 1% line says the slot is too small, where does the rest of the money go?

Every capacity face so far prices SIZE as a cost (r1260's sqrt-impact ladder: 1M -> 50M -> 100M,
still assumed to fill). The gate's own ruler is not a price, it is a refusal: an order above
1% of a name's ADV is not expensive, it is not there. This face prices the refusal.

At each rebalance the published book buys five equal slots. With `lens` CNY of capital and the
gate's line, the weakest of those five names can take `line * slots * worst_ADV` CNY. When that
is below `lens`, the honest reading is not "trade it anyway and pay impact" -- it is "you can
only be invested f = cap/lens, and the remainder sits in cash".

  arm A  the published book, filled in full (every existing face)
  arm B  the same five names, scaled by f = min(1, cap/lens); (1-f) in cash at 0%
  arm C  the same as B but the idle cash earns the repo ladder's own daily rate when the panel
         is on disk; otherwise arm C is honestly absent (not silently equal to B)

Nothing is re-ranked and nothing is adopted: this is the price of respecting a ruler the book
already reports against.

Criterion, frozen before the read (also written into the payload):
  D1 binds : >= 5% of rebalances carry f < 1.
  D2 costs : |CAGR(B) - CAGR(A)| >= 0.50pp -> CAPACITY_BINDS_AND_COSTS,
             else CAPACITY_BINDS_AT_NEGLIGIBLE_COST.
  D1 false -> CAPACITY_NOT_BINDING_AT_THIS_LENS.
"""
import argparse
import json
import math
import os
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
sys.path.insert(0, ROOT)

import pandas as pd  # noqa: E402

import etf_equity_alpha as A  # noqa: E402
import etf_book_era_capacity as EC  # noqa: E402
import etf_book_liquidity_select as LS  # noqa: E402
import etf_book_scale_floor as S  # noqa: E402
import etf_robust_pf as R  # noqa: E402

OUT_JSON = os.path.join(ROOT, "results", "etf_book_capacity_shortfall.json")
OUT_MD = os.path.join(ROOT, "results", "etf_book_capacity_shortfall.md")

SLOTS = 5
REBAL = 20
COST = 0.0010
VOL_TARGET = S.VOL_TARGET

CRIT = {
    "bind_share_min": 0.05,   # D1: the line must actually refuse something
    "cost_pp": 0.50,          # D2: a cost below this is not a finding
}


# ------------------------------------------------------------------ pure math

def scale_factors(caps, lens):
    """f = min(1, cap/lens) per rebalance. An unpriced date is left at 1.0 and counted."""
    fs, unpriced = [], 0
    for c in caps:
        if c is None:
            fs.append(1.0)
            unpriced += 1
            continue
        fs.append(1.0 if c >= lens else float(c) / float(lens))
    return fs, unpriced


def apply_overlay(ser, dec_dates, fs, cash_daily=0.0):
    """Scale the book's own daily returns by f over each holding window.

    s_t = f * r_t + (1 - f) * c_t. This is the arithmetic of holding `f` of the slate: the
    book's weights are equal, so scaling every slot by the same f scales the whole return by f.
    It does not re-fit the vol target (disclosed in `honest`).
    """
    ser = ser.dropna()
    idx = [d for d in ser.index]
    window = []
    for d in idx:
        f = 1.0
        for i, dd in enumerate(dec_dates):
            if d >= dd:
                f = fs[i] if i < len(fs) else 1.0
        window.append(f)
    out = []
    for d, f in zip(idx, window):
        r = float(ser.loc[d])
        out.append(f * r + (1.0 - f) * float(cash_daily))
    return pd.Series(out, index=idx, name="scaled"), pd.Series(window, index=idx, name="f")


def deployed_stats(fs):
    if not fs:
        return {"rebalances": 0, "mean_f": None, "worst_f": None, "share_below_1": None}
    s = pd.Series([float(x) for x in fs])
    return {"rebalances": int(len(s)), "mean_f": round(float(s.mean()), 4),
            "worst_f": round(float(s.min()), 4),
            "share_below_1": round(float((s < 1.0 - 1e-12).mean()), 4)}


def verdict_of(payload):
    """Derive the verdict from the published counts only (check() re-runs this)."""
    dep = payload.get("deployed") or {}
    share = dep.get("share_below_1")
    if share is None or share < CRIT["bind_share_min"]:
        return "CAPACITY_NOT_BINDING_AT_THIS_LENS"
    cost = payload.get("cagr_cost_pp")
    if cost is None:
        return "CAPACITY_BINDS_COSTS_UNREADABLE"
    return ("CAPACITY_BINDS_AND_COSTS" if abs(float(cost)) >= CRIT["cost_pp"]
            else "CAPACITY_BINDS_AT_NEGLIGIBLE_COST")


# ------------------------------------------------------------------ stats

def _stats(ser, tag):
    st = A.stats2(ser, tag)
    blk = {k: (None if st.get(k) is None else round(float(st[k]), 4))
           for k in ("cagr", "sharpe", "maxdd") if k in st}
    blk.update(S.sub_stats(ser))
    return blk


# ------------------------------------------------------------------ run

def run() -> int:
    t0 = time.time()
    face = EC.load_gate()
    rituals = EC.rulers(face)
    if rituals.get("line_frac") is None or rituals.get("lens_cny") is None:
        print("gate face carries no usable ruler: line=%r lens=%r"
              % (rituals.get("line_pct"), rituals.get("lens_cny")), flush=True)
        return 2
    line = float(rituals["line_frac"])
    lens = float(rituals["lens_cny"])
    need = (lens / SLOTS) / line

    close, openp, amt, sc, n_flip = S.nobond_universe()
    start = pd.Timestamp(getattr(R, "START", "2020-01-01"))
    dates = [d for d in openp.index if d >= start]
    dec_dates = [dates[i] for i in range(0, len(dates) - 1, REBAL)]
    print("panel %d names / %d rebalances / need ADV %s / lens %s"
          % (len(close.columns), len(dec_dates), "%.0f" % need, "%.0f" % lens), flush=True)

    adv = LS.adv_at_dates(amt, dec_dates)
    picks_map = {}
    for d in dec_dates:
        key = str(pd.Timestamp(d).date())
        picks_map[key] = [str(x) for x in sc.loc[d].dropna().nlargest(SLOTS).index]

    cap_rows = LS.cap_rows(picks_map, adv, line)
    caps = [r["cap_cny"] for r in cap_rows]
    fs, unpriced = scale_factors(caps, lens)

    ser_a, turn_a = R.open_to_open_equity(close, openp, amt, sc, REBAL, SLOTS, COST,
                                          vol_target=VOL_TARGET, vol_floor=0.0)
    ser_b, f_daily = apply_overlay(ser_a, dec_dates, fs, cash_daily=0.0)

    dep = deployed_stats(fs)
    stat_a, stat_b = _stats(ser_a, "A"), _stats(ser_b, "B")
    cost_pp = None
    if stat_a.get("cagr") is not None and stat_b.get("cagr") is not None:
        cost_pp = round((float(stat_b["cagr"]) - float(stat_a["cagr"])) * 100.0, 4)

    payload = {
        "face": "etf_book_capacity_shortfall",
        "generated": pd.Timestamp.now(tz="Asia/Shanghai").isoformat(timespec="seconds"),
        "evidence_cutoff": str(pd.Timestamp(ser_a.index[-1]).date()),
        "script": "scripts/etf_book_capacity_shortfall.py",
        "criteria": {
            "line_pct": rituals.get("line_pct"), "line_frac": line,
            "lens_cny": lens, "lens_label": rituals.get("lens"),
            "slots": SLOTS, "per_name_cny": lens / SLOTS, "need_adv_cny": need,
            "rebal": REBAL, "cost_per_side": COST, "vol_target": VOL_TARGET,
            "frozen": dict(CRIT),
            "why": "the gate's ruler is a refusal, not a price: above 1% ADV the order is not "
                   "expensive, it is absent -- so the rest of the capital sits in cash",
        },
        "arms": {
            "A_published_full_fill": {"turnover": round(turn_a, 3), "stats": stat_a},
            "B_scaled_to_line": {"turnover": round(turn_a, 3), "stats": stat_b,
                                 "cash_yield_daily": 0.0},
            "C_scaled_with_repo_cash": None,
        },
        "deployed": dict(dep, unpriced_dates=unpriced),
        "cagr_cost_pp": cost_pp,
        "capacity_rows": [{"date": r["date"], "cap_cny": r["cap_cny"],
                           "f": fs[i]} for i, r in enumerate(cap_rows)],
        "elapsed_sec": round(time.time() - t0, 1),
        "honest": [
            "the overlay is arithmetic on the published series, not a re-run of the engine: "
            "scaling the slate by f also scales the vol-target overlay that fitted it, so B's "
            "vol is f times A's and its sharpe is not simply A's sharpe",
            "the idle cash earns 0 in arm B; r1269 already measured the repo ladder's worth at "
            "+0.10~0.15pp/yr on this book, so B is the LOWER bound and arm C is left absent "
            "rather than silently equated to B",
            "entry_lag=0 is the published behaviour, kept so arm A reproduces every printed face",
            "capacity is read from the same 40-bar ruler as every other capacity face, so this "
            "face inherits their survivors-sweep bias",
            "nothing here is adopted: this prices the ruler, it does not change the book",
        ],
    }
    payload["verdict"] = verdict_of(payload)

    os.makedirs(os.path.dirname(OUT_JSON), exist_ok=True)
    with open(OUT_JSON, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=1)
    write_md(payload)
    print("verdict %s | deployed mean f %.3f (worst %.3f, %d/%d below 1) | CAGR A %.2f%%, B %.2f%%"
          % (payload["verdict"], dep["mean_f"] or 0, dep["worst_f"] or 0,
             sum(1 for x in fs if x < 1 - 1e-12), len(fs),
             (stat_a.get("cagr") or 0) * 100, (stat_b.get("cagr") or 0) * 100), flush=True)
    print("-> %s (%.1fs)" % (OUT_JSON, time.time() - t0), flush=True)
    return 0


def write_md(p):
    a = p["arms"]["A_published_full_fill"]["stats"]
    b = p["arms"]["B_scaled_to_line"]["stats"]
    d = p["deployed"]
    n_below = sum(1 for r in p["capacity_rows"] if r["f"] < 1 - 1e-12)
    pct = lambda x: "n/a" if x is None else "%.2f%%" % (x * 100.0)
    money = lambda x: "n/a" if x is None else "{:,.0f}".format(x)
    L = ["# 那条 1% 的线是拒绝，不是价格：装不进去的钱去哪了", "",
         "证据截止 %s · 门 %s · 每名 %s 元 · 槽位 %d · 调仓 %d 日"
         % (p["evidence_cutoff"], p["criteria"]["lens_label"], money(p["criteria"]["per_name_cny"]),
            p["criteria"]["slots"], p["criteria"]["rebal"]), "",
         "## 判词：%s" % p["verdict"], "",
         "同一本书、同样五个名字：按「1%% ADV 装得下多少就买多少，剩下留现金」重读，"
         "在 %d 次调仓里有 %d 次装不满（占 %.1f%%），平均只能投出 %.1f%% 的钱，最差一次只剩 %.1f%%。"
         % (d["rebalances"], n_below, 100.0 * (d["share_below_1"] or 0),
            100.0 * (d["mean_f"] or 0), 100.0 * (d["worst_f"] or 0)), "",
         "| 臂 | 年化 | 夏普 | 回撤 | 换手 |", "|---|---:|---:|---:|---:|",
         "| A 全额成交（所有在印面） | %s | %.3f | %s | %.3f |"
         % (pct(a.get("cagr")), a.get("sharpe") or 0, pct(a.get("maxdd")),
            p["arms"]["A_published_full_fill"]["turnover"]),
         "| B 按线缩仓 + 现金 0%% | %s | %.3f | %s | %.3f |"
         % (pct(b.get("cagr")), b.get("sharpe") or 0, pct(b.get("maxdd")),
            p["arms"]["B_scaled_to_line"]["turnover"]), "",
         "守规矩的代价：**%+.2f pp/年**（B 减 A）。现金那一半按 0%% 计，所以这是下界——"
         "r1269 已量过本书记载的回购腿值 +0.10~0.15pp/年。" % (p["cagr_cost_pp"] or 0.0), "",
         "## 装不下的那几天", "",
         "| 调仓日 | 容量（元） | 能投出的比例 f |", "|---|---:|---:|",
         ]
    for r in sorted(p["capacity_rows"], key=lambda x: (x["f"] if x["f"] is not None else 1.0))[:8]:
        L.append("| %s | %s | %.1f%% |" % (r["date"], money(r["cap_cny"]), 100.0 * r["f"]))
    L += ["", "## 诚实边界", ""] + ["- " + h for h in p["honest"]]
    with open(OUT_MD, "w", encoding="utf-8") as fh:
        fh.write("\n".join(L) + "\n")


def check() -> int:
    if not os.path.exists(OUT_JSON):
        print("face missing: %s" % OUT_JSON, flush=True)
        return 2
    with open(OUT_JSON, encoding="utf-8") as fh:
        p = json.load(fh)
    v = verdict_of(p)
    ok = v == p.get("verdict")
    rows = p.get("capacity_rows") or []
    bad = [r for r in rows if r.get("f") is not None and r["cap_cny"] is not None
           and abs(r["f"] - min(1.0, r["cap_cny"] / float(p["criteria"]["lens_cny"]))) > 1e-9]
    print("check %s verdict=%s published=%s f_rows_check=%d bad=%d"
          % ("ok" if (ok and not bad) else "FAIL", v, p.get("verdict"), len(rows), len(bad)),
          flush=True)
    return 0 if (ok and not bad) else 3


# ------------------------------------------------------------------ selftest

def selftest() -> int:
    legs, fails = [], []

    def leg(name, cond, detail=""):
        legs.append(name)
        if not cond:
            fails.append("%s: %s" % (name, detail))

    fs, unp = scale_factors([1_000_000, 500_000, 2_000_000, None], 1_000_000)
    leg("L1 f formula", fs == [1.0, 0.5, 1.0, 1.0] and unp == 1, str(fs))
    fs2, _ = scale_factors([100_000], 1_000_000)
    leg("L2 partial", abs(fs2[0] - 0.1) < 1e-12, str(fs2))

    ser = pd.Series([0.01, -0.02, 0.03], index=pd.to_datetime(["2020-01-02", "2020-01-03", "2020-01-06"]))
    dec = [pd.Timestamp("2020-01-02")]
    out, fw = apply_overlay(ser, dec, [1.0])
    leg("L3 all-f-1 reproduces", all(abs(a - b) < 1e-15 for a, b in zip(out.values, ser.values)), str(out.values))

    out2, fw2 = apply_overlay(ser, dec, [0.5])
    leg("L4 half invested", all(abs(o - 0.5 * r) < 1e-15 for o, r in zip(out2.values, ser.values)), str(out2.values))
    leg("L5 window carries f", list(fw2.values) == [0.5, 0.5, 0.5], str(fw2.values))

    out3, _ = apply_overlay(ser, dec, [0.5], cash_daily=0.0002)
    leg("L6 cash leg paid", all(abs(o - (0.5 * r + 0.5 * 0.0002)) < 1e-15
                                for o, r in zip(out3.values, ser.values)), str(out3.values))

    d = deployed_stats([1.0, 0.5, 0.5, 0.0])
    leg("L7 deployed stats", d["mean_f"] == 0.5 and d["worst_f"] == 0.0 and d["share_below_1"] == 0.75, str(d))

    leg("L8 verdict not-binding", verdict_of({"deployed": {"share_below_1": 0.0}}) == "CAPACITY_NOT_BINDING_AT_THIS_LENS")
    leg("L9 verdict binds costs", verdict_of({"deployed": {"share_below_1": 0.5}, "cagr_cost_pp": -1.2}) == "CAPACITY_BINDS_AND_COSTS")
    leg("L10 verdict binds cheap", verdict_of({"deployed": {"share_below_1": 0.5}, "cagr_cost_pp": -0.1}) == "CAPACITY_BINDS_AT_NEGLIGIBLE_COST")
    leg("L11 unreadable cost", verdict_of({"deployed": {"share_below_1": 0.5}, "cagr_cost_pp": None}) == "CAPACITY_BINDS_COSTS_UNREADABLE")

    print("capacity_shortfall selftest %d/%d PASS" % (len(legs) - len(fails), len(legs)), flush=True)
    for f in fails:
        print("  FAIL " + f, flush=True)
    return 0 if not fails else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", nargs="?", default="run", choices=["run", "check", "selftest"])
    a = ap.parse_args()
    if a.cmd == "selftest":
        return selftest()
    if a.cmd == "check":
        return check()
    return run()


if __name__ == "__main__":
    sys.exit(main())
