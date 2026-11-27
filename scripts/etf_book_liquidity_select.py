#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""ETF book -- the same scores, minus the names that cannot take the slot.

r1874 asked whether 2015's capacity refusal was a depth problem or a ranking problem, and
answered: ranking (21 names cleared the per-slot bar while the score's own five carried
82.9x less). The obvious next move -- screen the picks by depth -- has a catch this face
measures before adopting anything: the book ALREADY screens by depth. `MIN_AMT` is a 20-bar
median turnover floor of 20M CNY, and 20M is exactly the per-slot need at the 1M lens
(200,000 / 1%). On paper there is nothing left to filter.

The two rulers are not the same ruler. The buy screen reads the 20-bar median AT the
decision bar; the capacity ruler reads the median OF the last 20 such medians (~40 bars).
A name whose turnover spiked can pass the buy screen while its own capacity reading still
says it cannot take the slot -- and that is the only population a selection floor can act
on. This face prices that population:

  arm A  the published book            (plain top-5, nothing added)
  arm B  same scores, skip names whose capacity ADV < 200,000 / 1% (= 20M), fill from below
  arm R  drop as many picks per date at RANDOM and fill from below -- the price of the act
         of substituting, so B's edge is not the substitution itself (r1865's second door)

Capacity is bought mechanically by B (its five names clear the need by construction); the
open question is what the substitution costs, and whether the names it drops are worse
names or just momentarily thin ones.

Criterion, frozen before the read (also written into the payload):
  D1 binds : B substitutes on >= 1% of rebalances; else NO_CONFLICT -- the two screens
             agree and there is nothing to adopt.
  D2 pays  : paired monthly (B-A) >= -0.50pp AND paired monthly (B-R) >= 0 with
             |t| >= 2.0 over >= 24 paired months -> FLOOR_PAYS.
  otherwise FLOOR_BUYS_CAPACITY_AT_A_MEASURED_PRICE, which prints both prices and adopts
  nothing; a B-R reading that cannot clear its own noise is SUBSTITUTION_NOT_SEPARABLE.

Every input is causal: the ADV reading used at a decision is the one visible ON that bar.
"""
import argparse
import contextlib
import io
import json
import math
import os
import random
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
sys.path.insert(0, ROOT)

import pandas as pd  # noqa: E402

import etf_equity_alpha as A  # noqa: E402
import etf_book_era_capacity as EC  # noqa: E402
import etf_book_era_roster as ER  # noqa: E402
import etf_book_scale_floor as S  # noqa: E402
import etf_robust_pf as R  # noqa: E402

OUT_JSON = os.path.join(ROOT, "results", "etf_book_liquidity_select.json")
OUT_MD = os.path.join(ROOT, "results", "etf_book_liquidity_select.md")

SLOTS = 5
REBAL = 20
COST = 0.0010
VOL_TARGET = S.VOL_TARGET
SEED = 20261120
IS_END = S.IS_END
ADV_BARS = ER.ADV_BARS

CRIT = {
    "bind_share_min": 0.01,      # D1: the floor must actually fire
    "cagr_tol_pp": 0.50,         # D2: monthly B-A may be this cheap at worst
    "t_min": 2.0,                # D2: B must beat R by more than its own noise
    "min_paired_months": 24,     # D2: a t-stat on 6 months is not a reading
}


# ---------------------------------------------------------------- outside anchors

def panel_bar():
    """The bar the frozen core48 panel is on right now, read off its own CSVs (r2167).

    `S.nobond_universe()` rebuilds the panel (seconds), so a check that called it every
    round would be too slow to run -- and this check used to re-derive only its own rows,
    which makes it green on any panel (r1935). This is the cheap outside question: the tail
    date of each core48 file.
    """
    try:
        import live.paper as P
        core = sorted(P.load_core())
    except Exception:                                          # noqa: BLE001
        return None
    daily = os.path.join(ROOT, "data", "daily")
    last = None
    for sym in core:
        path = os.path.join(daily, "%s.csv" % sym)
        if not os.path.exists(path):
            continue
        try:
            with open(path, "rb") as f:
                f.seek(0, 2)
                f.seek(max(0, f.tell() - 400))
                tail = f.read().decode("utf-8", "replace")
        except Exception:                                      # noqa: BLE001
            continue
        body = [x for x in tail.splitlines() if x.strip()]
        if not body:
            continue
        day = body[-1].split(",")[0].strip()[:10]
        if last is None or day > last:
            last = day
    return last


def gate_ruler():
    """The line and the lens this face's 'need ADV' is built from (a cheap gate read)."""
    try:
        r = EC.rulers(EC.load_gate())
    except Exception:                                          # noqa: BLE001
        return None
    return {"line_pct": r.get("line_pct"), "line_frac": r.get("line_frac"),
            "lens_cny": r.get("lens_cny")}


def drift(payload, live="disk", ruler="disk"):
    """Has the world moved under this face? Only an outside anchor can answer (r1935).

    A newer panel or a re-published gate is a rebuild, not a contradiction: the chain pays
    for the writer when the probe says STALE (r1850), and it must never pay because a face
    disagreed with itself.
    """
    if live == "disk":
        live = panel_bar()
    if ruler == "disk":
        ruler = gate_ruler()
    was = (payload or {}).get("inputs") or {}
    out = []
    if not was.get("panel_last_bar"):
        out.append("the face records no panel bar, so there is nothing to age it against")
    elif live is None:
        out.append("the panel bar cannot be read (core48 tails unreadable), so this face "
                   "cannot be aged")
    elif str(was["panel_last_bar"]) != str(live):
        out.append("the panel is on bar %s, this face priced %s"
                   % (live, was["panel_last_bar"]))
    g0 = was.get("gate") or {}
    if ruler is None:
        out.append("the gate ruler cannot be read, so this face cannot be aged")
    else:
        for k in ("line_frac", "lens_cny"):
            a, b = g0.get(k), ruler.get(k)
            if a is None:
                out.append("the face records no gate %s" % k)
            elif b is not None and abs(float(a) - float(b)) > 1e-12 * max(1.0, abs(float(b))):
                out.append("the gate's %s is %r, this face priced %r" % (k, b, a))
    return out


# ------------------------------------------------------------------ liquidity ruler

def adv_at_dates(amt, dates, bars=ADV_BARS):
    """Median of the last `bars` readings of `amt` at or before each date.

    Deliberately the same definition as `etf_book_era_roster.adv_at_anchors` (which is
    what every capacity face reads): a name's holes are dropped, not filled, and at least
    `bars` readings are required. Implemented here as one vectorised pass so a whole
    rebalance schedule costs seconds; selftest L1 pins it against the roster's own walk.
    """
    dates = list(dates)
    out = {}
    for sym in amt.columns:
        s = amt[sym].dropna()
        if s.empty:
            continue
        r = s.rolling(bars, min_periods=bars).median()
        r = r.reindex(amt.index).ffill()
        col = r.reindex(dates)
        name = str(sym)
        for d, v in col.items():
            if pd.notna(v):
                out.setdefault(str(pd.Timestamp(d).date()), {})[name] = float(v)
    return out


def picks_with_floor(row, advs, need, n_hold):
    """Top `n_hold` of `row`, skipping names whose capacity ADV cannot take the slot.

    Returns (picks, blocked, used_fallback). Blocked names are restored in rank order only
    when the book would otherwise be short -- a thin book is a different animal from a
    wide one and must never be reported as "the floor chose this".
    """
    ranked = row.dropna().sort_values(ascending=False)
    picks, blocked = [], []
    for nm in ranked.index:
        if len(picks) >= n_hold:
            break
        key = str(nm)
        a = advs.get(key)
        if a is None or a < need:
            blocked.append(key)
            continue
        picks.append(key)
    used_fallback = False
    if len(picks) < n_hold:
        used_fallback = True
        for nm in blocked:
            if nm in picks:
                continue
            picks.append(nm)
            if len(picks) >= n_hold:
                break
    for nm in ranked.index:                      # last resort: a row too short to fill
        key = str(nm)
        if len(picks) >= n_hold:
            break
        if key not in picks:
            picks.append(key)
    return picks, blocked, used_fallback


def random_fill(base, ranked, k, rng):
    """Drop `k` of `base` at random, replace with the next names below it."""
    if k <= 0:
        return list(base)
    held = set(base)
    pool = [str(x) for x in ranked if str(x) not in held]
    drop = set(rng.sample(list(base), min(k, len(base))))
    keep = [x for x in base if x not in drop]
    return keep + pool[:len(base) - len(keep)]


# ------------------------------------------------------------------ capacity

def cap_rows(picks_map, adv, line, slots=SLOTS):
    """One row per decision: the capital that fills the weakest of these slots at `line`."""
    rows = []
    for key in sorted(picks_map):
        picks = picks_map[key]
        advs = [adv.get(key, {}).get(n) for n in picks]
        if not picks or any(a is None for a in advs):
            rows.append({"date": key, "cap_cny": None, "worst_adv_cny": None,
                         "n_slots_priced": 0})
            continue
        worst = float(min(advs))
        rows.append({"date": key, "cap_cny": float(line) * slots * worst,
                     "worst_adv_cny": worst, "n_slots_priced": len(advs)})
    return rows


def cap_summary(rows, lens_cny):
    caps = [r["cap_cny"] for r in rows if r.get("cap_cny") is not None]
    if not caps:
        return {"n_priced": 0, "median_cny": None, "min_cny": None,
                "share_below_lens": None}
    s = pd.Series(caps)
    return {"n_priced": len(caps), "median_cny": float(s.median()),
            "min_cny": float(s.min()),
            "share_below_lens": float((s < float(lens_cny)).mean()),
            "n_rows": len(rows)}


# ------------------------------------------------------------------ paired reading

def paired(ser_b, ser_a, label):
    """Paired monthly difference between two books on the same calendar months."""
    mb = ser_b.dropna().resample("ME").last().pct_change().dropna()
    ma = ser_a.dropna().resample("ME").last().pct_change().dropna()
    j = pd.concat([mb.rename("b"), ma.rename("a")], axis=1).dropna()
    d = j["b"] - j["a"]
    n = int(len(d))
    out = {"label": label, "months": n, "mean_pp": None, "t": None,
           "b_better_months": int((d > 0).sum()) if n else None}
    if n == 0:
        out["why"] = "no calendar month carries both books"
        return out
    mean = float(d.mean())
    sd = float(d.std(ddof=1)) if n > 1 else 0.0
    out["mean_pp"] = round(mean * 100.0, 4)
    out["t"] = round(mean / (sd / math.sqrt(n)), 3) if (n > 1 and sd > 0) else None
    return out


# ------------------------------------------------------------------ statistics

def _stats(ser, tag):
    st = A.stats2(ser, tag)
    blk = {k: (None if st.get(k) is None else round(float(st[k]), 4))
           for k in ("cagr", "sharpe", "maxdd") if k in st}
    blk.update(S.sub_stats(ser))
    return blk


def _hook(picks_map):
    """A select_hook that replays a pre-computed choice; shape errors fall back loudly."""
    def h(row, held, n_hold, d):
        key = str(pd.Timestamp(d).date())
        picks = picks_map.get(key)
        if picks is None or len(picks) != n_hold:
            return [str(x) for x in row.dropna().nlargest(n_hold).index]
        return [str(x) for x in picks]
    return h


# ------------------------------------------------------------------ verdict

def verdict_of(payload):
    """Derive the verdict from the published counts only (check() re-runs this)."""
    sub = payload.get("substitution") or {}
    share = sub.get("share_of_rebalances")
    if share is None or share < CRIT["bind_share_min"]:
        return "NO_CONFLICT"
    ba = payload.get("paired_ba") or {}
    br = payload.get("paired_br") or {}
    months = br.get("months") or 0
    if months < CRIT["min_paired_months"]:
        return "SUBSTITUTION_NOT_SEPARABLE"
    t_br = br.get("t")
    if t_br is None or abs(t_br) < CRIT["t_min"]:
        return "SUBSTITUTION_NOT_SEPARABLE"
    if (br.get("mean_pp") or 0.0) > 0 and (ba.get("mean_pp") or 0.0) >= -CRIT["cagr_tol_pp"]:
        return "FLOOR_PAYS"
    return "FLOOR_BUYS_CAPACITY_AT_A_MEASURED_PRICE"


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
    per_name = lens / SLOTS
    need = per_name / line

    close, openp, amt, sc, n_flip = S.nobond_universe()
    op = openp.reindex(columns=close.columns)
    start = pd.Timestamp(getattr(R, "START", "2020-01-01"))
    dates = [d for d in op.index if d >= start]
    dec_dates = [dates[i] for i in range(0, len(dates) - 1, REBAL)]
    print("panel %d names / %d rebalances / need ADV %s" % (len(close.columns), len(dec_dates),
                                                            S._fmt_money(need)
                                                            if hasattr(S, "_fmt_money") else "%.0f" % need),
          flush=True)
    adv = adv_at_dates(amt, dec_dates)

    ctrl, floor_picks, subs, fallbacks = {}, {}, {}, []
    for d in dec_dates:
        key = str(pd.Timestamp(d).date())
        row = sc.loc[d]
        base = [str(x) for x in row.dropna().nlargest(SLOTS).index]
        ctrl[key] = base
        picks, blocked, fb = picks_with_floor(row, adv.get(key, {}), need, SLOTS)
        floor_picks[key] = picks
        if fb:
            fallbacks.append(key)
        subs[key] = len(set(base) - set(picks))

    rng = random.Random(SEED)
    rand_picks = {}
    for d in dec_dates:
        key = str(pd.Timestamp(d).date())
        ranked = [str(x) for x in sc.loc[d].dropna().sort_values(ascending=False).index]
        rand_picks[key] = random_fill(ctrl[key], ranked, subs[key], rng)

    def book(picks_map):
        ser, turn = R.open_to_open_equity(close, openp, amt, sc, REBAL, SLOTS, COST,
                                          vol_target=VOL_TARGET, vol_floor=0.0,
                                          select_hook=_hook(picks_map))
        return ser, turn

    ser_a, turn_a = R.open_to_open_equity(close, openp, amt, sc, REBAL, SLOTS, COST,
                                          vol_target=VOL_TARGET, vol_floor=0.0)
    ser_b, turn_b = book(floor_picks)
    ser_r, turn_r = book(rand_picks)

    stat_a, stat_b, stat_r = _stats(ser_a, "A"), _stats(ser_b, "B"), _stats(ser_r, "R")
    cap_a = cap_rows(ctrl, adv, line)
    cap_b = cap_rows(floor_picks, adv, line)
    cap_r = cap_rows(rand_picks, adv, line)
    sum_a = cap_summary(cap_a, lens)
    sum_b = cap_summary(cap_b, lens)
    sum_r = cap_summary(cap_r, lens)

    n_sub_dates = sum(1 for k, v in subs.items() if v > 0)
    payload = {
        "face": "etf_book_liquidity_select",
        "generated": pd.Timestamp.now(tz="Asia/Shanghai").isoformat(timespec="seconds"),
        "evidence_cutoff": str(pd.Timestamp(ser_a.index[-1]).date()),
        "inputs": {
            "panel_last_bar": panel_bar() or str(pd.Timestamp(close.index[-1]).date()),
            "gate": gate_ruler() or {"line_pct": rituals.get("line_pct"),
                                     "line_frac": line, "lens_cny": lens},
            "data_end": str(pd.Timestamp(close.index[-1]).date()),
            "why": "what this face priced; check() ages the face against the live panel and "
                   "the live gate instead of only re-deriving its own rows (r2167)",
        },
        "criteria": {
            "line_pct": rituals.get("line_pct"), "line_frac": line,
            "lens_cny": lens, "lens_label": rituals.get("lens"),
            "slots": SLOTS, "per_name_cny": per_name, "need_adv_cny": need,
            "rebal": REBAL, "n_hold": SLOTS, "cost_per_side": COST,
            "vol_target": VOL_TARGET, "adv_bars": ADV_BARS, "seed": SEED,
            "frozen": dict(CRIT),
            "why_need": "per-slot order / the gate's own 1% line -- the same algebra every "
                        "capacity face prints (cap = line * slots * worst ADV)",
            "book_screen": "MIN_AMT %.0f CNY is a 20-bar median read AT the decision bar; "
                           "the capacity ruler reads the median OF the last 20 such medians"
                           % (20e6,),
        },
        "arms": {"A_published": {"turnover": round(turn_a, 3), "stats": stat_a,
                                 "capacity": sum_a},
                 "B_floor": {"turnover": round(turn_b, 3), "stats": stat_b,
                             "capacity": sum_b},
                 "R_random_fill": {"turnover": round(turn_r, 3), "stats": stat_r,
                                   "capacity": sum_r}},
        "substitution": {
            "rebalances": len(dec_dates),
            "rebalances_with_a_substitution": n_sub_dates,
            "share_of_rebalances": round(n_sub_dates / len(dec_dates), 4) if dec_dates else None,
            "names_substituted": int(sum(subs.values())),
            "fallback_dates": fallbacks,
        },
        "paired_ba": paired(ser_b, ser_a, "B-A"),
        "paired_br": paired(ser_b, ser_r, "B-R"),
        "capacity_uplift_median": (
            round(sum_b["median_cny"] / sum_a["median_cny"], 4)
            if (sum_b["median_cny"] and sum_a["median_cny"]) else None),
        "capacity_rows": {"A_published": cap_a, "B_floor": cap_b},
        "honest": [
            "capacity is bought MECHANICALLY by B: every floored pick clears the need by "
            "construction, so the uplift ratio is not evidence -- the open number is what "
            "the substitution costs (paired B-A) and whether it beats random (paired B-R)",
            "the panel is a survivors sweep (r1319/r1874): names the source never served "
            "could not have been ranked, so they cannot appear in any arm",
            "entry_lag=0 is the published behaviour, kept so arm A reproduces every "
            "printed face; the same one-bar gift applies to all three arms",
            "the fallback dates are listed, not hidden: a book that could not fill five "
            "deep slots is a different animal from a wide one",
            "nothing here is adopted: this face prices the rule",
        ],
        "elapsed_sec": round(time.time() - t0, 2),
    }
    payload["verdict"] = verdict_of(payload)
    payload["sentence"] = _sentence(payload)

    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=1)
    with open(OUT_MD, "w", encoding="utf-8") as f:
        f.write(render_md(payload))
    print("A cagr %.4f cap_med %s | B cagr %.4f cap_med %s | R cagr %.4f | sub %d/%d -> %s"
          % (stat_a.get("cagr") or 0, sum_a["median_cny"], stat_b.get("cagr") or 0,
             sum_b["median_cny"], stat_r.get("cagr") or 0, n_sub_dates, len(dec_dates),
             payload["verdict"]), flush=True)
    print("wrote %s" % os.path.relpath(OUT_JSON, ROOT), flush=True)
    return 0


def _m(v):
    if v is None:
        return "-"
    if abs(v) >= 1e8:
        return "%.2f亿" % (v / 1e8)
    if abs(v) >= 1e4:
        return "%.1f万" % (v / 1e4)
    return "%.0f" % v


def _sentence(p):
    """Both halves in one line: what the return side proved, and what capacity bought."""
    a, b = p["arms"]["A_published"], p["arms"]["B_floor"]
    caps = (a["capacity"], b["capacity"])
    if p["verdict"] == "NO_CONFLICT":
        return ("两个口径在这份面板上没有分家：%d 次调仓里没有一次需要替换，"
                "所以在 100 万透镜下没有可采纳的东西。" % p["substitution"]["rebalances"])
    head = ("%d/%d 次调仓里，在印书的五个名字有一个装不下每名 %s 的名额"
            % (p["substitution"]["rebalances_with_a_substitution"],
               p["substitution"]["rebalances"], _m(p["criteria"]["per_name_cny"])))
    capacity = ("；加闸后容量最薄日从 %s 抬到 %s，低于透镜的调仓从 %.0f%% 降到 %.0f%%"
                % (_m(caps[0]["min_cny"]), _m(caps[1]["min_cny"]),
                   (caps[0]["share_below_lens"] or 0) * 100,
                   (caps[1]["share_below_lens"] or 0) * 100))
    if p["verdict"] == "FLOOR_PAYS":
        tail = "；替换本身还赚钱（B-R 月度 %s，t=%s），可采纳。" % (
            p["paired_br"].get("mean_pp"), p["paired_br"].get("t"))
    elif p["verdict"] == "SUBSTITUTION_NOT_SEPARABLE":
        tail = ("；但收益差读不出（B-A %s pp/月 t=%s，B-R %s pp/月 t=%s）——"
                "容量是机械买到的，收益是中性的，别把它当 alpha 卖。"
                % (p["paired_ba"].get("mean_pp"), p["paired_ba"].get("t"),
                   p["paired_br"].get("mean_pp"), p["paired_br"].get("t")))
    else:
        tail = "；替换的代价高于它买到的东西（%s pp/月），不采纳。" % (
            p["paired_br"].get("mean_pp"),)
    return head + capacity + tail


def render_md(p):
    c, a = p["criteria"], p["arms"]
    lines = ["# 流动性筛选面：同一批分数，去掉装不下名额的名字", "",
             "证据截止 %s · 门 %.0f 万口径 · 每名需要 ADV %s · 槽位 %d · 调仓 %d 日"
             % (p["evidence_cutoff"], (c["lens_cny"] or 0) / 1e4, _m(c["need_adv_cny"]),
                c["slots"], c["rebal"]), "",
             "## 判词：%s" % p["verdict"], "",
             p.get("sentence") or "", "",
             "| 臂 | 年化 | 夏普 | 回撤 | 容量中位 | 容量最薄 | 容量低于门槛的比例 |",
             "|---|---|---|---|---|---|---|"]
    for key, name in (("A_published", "A 在印书"), ("B_floor", "B 加流动性闸"),
                      ("R_random_fill", "R 随机换同样多")):
        arm = a[key]
        st = arm["stats"]
        lines.append("| %s | %.2f%% | %.3f | %.2f%% | %s | %s | %.1f%% |"
                     % (name, (st.get("cagr") or 0) * 100, st.get("sharpe") or 0,
                        (st.get("maxdd") or 0) * 100, _m(arm["capacity"]["median_cny"]),
                        _m(arm["capacity"]["min_cny"]),
                        (arm["capacity"]["share_below_lens"] or 0) * 100))
    lines += ["", "## 配对读数", "",
              "- B-A 月度：%s pp/月，t=%s（%d 个月）"
              % (p["paired_ba"].get("mean_pp"), p["paired_ba"].get("t"),
                 p["paired_ba"].get("months") or 0),
              "- B-R 月度：%s pp/月，t=%s（%d 个月）"
              % (p["paired_br"].get("mean_pp"), p["paired_br"].get("t"),
                 p["paired_br"].get("months") or 0),
              "- 闸触发：%d/%d 次调仓发生了替换，共换 %d 个名字"
              % (p["substitution"]["rebalances_with_a_substitution"],
                 p["substitution"]["rebalances"], p["substitution"]["names_substituted"]),
              "", "## 诚实边界", ""]
    for h in p["honest"]:
        lines.append("- " + h)
    return "\n".join(lines) + "\n"


# ------------------------------------------------------------------ check

def check(payload=None, live="disk", ruler="disk"):
    problems = []
    if payload is None:
        with open(OUT_JSON, "r", encoding="utf-8") as f:
            payload = json.load(f)
    stale = drift(payload, live, ruler)
    if stale:
        print("check STALE: this face priced a book the panel or the gate has since left "
              "behind")
        for x in stale:
            print("  -", x)
        return 3
    c = payload.get("criteria") or {}
    line, slots = c.get("line_frac"), c.get("slots")
    lens, per_name = c.get("lens_cny"), c.get("per_name_cny")
    need = c.get("need_adv_cny")
    if line is None or slots is None:
        problems.append("criteria lost the ruler")
    elif per_name and lens and abs(per_name * slots - lens) > max(1e-6, 1e-9 * lens):
        problems.append("per_name*slots != lens")
    if need and per_name and line and abs(need - per_name / line) > 1e-6 * need:
        problems.append("need_adv is not per_name/line")
    for arm in ("A_published", "B_floor"):
        rows = (payload.get("capacity_rows") or {}).get(arm) or []
        for r in rows:
            if r.get("worst_adv_cny") is None or r.get("cap_cny") is None:
                continue
            want = float(line) * float(slots) * float(r["worst_adv_cny"])
            if abs(want - r["cap_cny"]) > max(1e-6, 1e-9 * want):
                problems.append("%s %s: cap re-derives as %.2f" % (arm, r["date"], want))
                break
    sub = payload.get("substitution") or {}
    rb, ns = sub.get("rebalances"), sub.get("rebalances_with_a_substitution")
    if rb and ns is not None and ns > rb:
        problems.append("more substitution dates than rebalances")
    if rb and sub.get("share_of_rebalances") is not None:
        if abs(sub["share_of_rebalances"] - round(ns / rb, 4)) > 1e-9:
            problems.append("share_of_rebalances does not match its own counts")
    again = verdict_of(payload)
    if again != payload.get("verdict"):
        problems.append("verdict %r re-derives as %r" % (payload.get("verdict"), again))
    ok = not problems
    if problems:
        # A number that will not re-derive is a defect, not a moved world: the chain must
        # not buy a rebuild for it, so this line never carries the word STALE (r1934).
        print("check FAIL:")
        for x in problems:
            print("  -", x)
        return 1
    print(json.dumps({"ok": ok, "problems": problems, "verdict": payload.get("verdict")},
                     ensure_ascii=False))
    return 0 if ok else 1


# ------------------------------------------------------------------ selftest

def selftest() -> int:
    checks = []

    def leg(name, ok, detail=""):
        checks.append((name, bool(ok), detail))

    # L1 the vectorised ADV is the roster's own walk, holes and all
    idx = pd.date_range("2020-01-01", periods=40, freq="D")
    a = pd.Series(range(1, 41), index=idx, dtype="float64")
    b = a.copy()
    b.iloc[[3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13]] = float("nan")   # a long hole
    b = b.dropna()
    amt = pd.DataFrame({"A": a, "B": b.reindex(idx)})
    dates = [idx[25], idx[39]]
    fast = adv_at_dates(amt, dates, bars=20)
    slow = ER.adv_at_anchors(amt, dates, bars=20)
    got = [fast.get(str(pd.Timestamp(d).date()), {}).get("B") for d in dates]
    want = [slow.loc["B", d] for d in dates]
    leg("L1 vectorised ADV == roster walk on a holed series",
        all((g is None) == (pd.isna(w)) and (g is None or abs(g - w) < 1e-9)
            for g, w in zip(got, want)), "%r vs %r" % (got, want))

    # L2 the need algebra is the capacity faces' own
    leg("L2 need = per_name / line", abs(200_000.0 / 0.01 - 20_000_000.0) < 1e-6)

    # L3 a thin top name is skipped, the next one is taken
    row = pd.Series({"X": 0.9, "Y": 0.8, "Z": 0.7, "W": 0.6, "V": 0.5, "U": 0.4})
    advs = {"X": 5e6, "Y": 3e7, "Z": 3e7, "W": 3e7, "V": 3e7, "U": 3e7}
    picks, blocked, fb = picks_with_floor(row, advs, 2e7, 5)
    leg("L3 thin name skipped and replaced from below",
        picks == ["Y", "Z", "W", "V", "U"] and blocked == ["X"] and not fb, "%r" % (picks,))

    # L4 fallback fires only when the row cannot fill, and says so
    advs2 = {k: 5e6 for k in row.index}
    v = [row, advs2, 2e7, 5]
    picks2, blocked2, fb2 = picks_with_floor(v[0], v[1], v[2], v[3])
    leg("L4 short book restores blocked names and flags the fallback",
        fb2 and len(picks2) == 5 and picks2[0] == "X", "%r fb=%r" % (picks2, fb2))

    # L5 capacity binds on the weakest slot
    pm = {"d1": ["a", "b"]}
    adv = {"d1": {"a": 9e7, "b": 2e7}}
    r0 = cap_rows(pm, adv, 0.01, slots=2)[0]
    leg("L5 cap = line*slots*min(adv)", abs(r0["cap_cny"] - 0.01 * 2 * 2e7) < 1e-6)

    # L6 a missing ADV leaves the row unpriced rather than guessed
    r1 = cap_rows({"d2": ["a", "zz"]}, {"d2": {"a": 9e7}}, 0.01, slots=2)[0]
    leg("L6 unpriced row is None, never a small number",
        r1["cap_cny"] is None and r1["n_slots_priced"] == 0)

    # L7-L10 verdict doors read only counts
    base = {"substitution": {"share_of_rebalances": 0.0},
            "paired_ba": {"mean_pp": 9.0, "months": 60}, "paired_br": {"mean_pp": 9.0, "t": 9}}
    leg("L7 no substitutions -> NO_CONFLICT", verdict_of(dict(base)) == "NO_CONFLICT")
    p = {"substitution": {"share_of_rebalances": 0.5},
         "paired_ba": {"mean_pp": -0.1, "months": 60},
         "paired_br": {"mean_pp": 0.2, "t": 2.5, "months": 60}}
    leg("L8 both doors clear -> FLOOR_PAYS", verdict_of(dict(p)) == "FLOOR_PAYS")
    p2 = {"substitution": {"share_of_rebalances": 0.5},
          "paired_ba": {"mean_pp": -0.1, "months": 60},
          "paired_br": {"mean_pp": 0.2, "t": 1.1, "months": 60}}
    leg("L9 a t inside its own noise -> NOT SEPARABLE",
        verdict_of(dict(p2)) == "SUBSTITUTION_NOT_SEPARABLE")
    p3 = {"substitution": {"share_of_rebalances": 0.5},
          "paired_ba": {"mean_pp": -0.1, "months": 60},
          "paired_br": {"mean_pp": -0.3, "t": -3.0, "months": 60}}
    leg("L10 losing to random -> MEASURED PRICE",
        verdict_of(dict(p3)) == "FLOOR_BUYS_CAPACITY_AT_A_MEASURED_PRICE")

    # L11 random fill substitutes exactly k and never duplicates
    base_p = ["a", "b", "c", "d", "e"]
    ranked = ["a", "b", "c", "d", "e", "f", "g", "h"]
    rr = random_fill(base_p, ranked, 2, random.Random(7))
    leg("L11 random fill keeps the count and the uniqueness",
        len(rr) == 5 and len(set(rr)) == 5 and len(set(base_p) - set(rr)) == 2, "%r" % (rr,))

    # L12 paired() on identical books is exactly zero; on a shifted one it is not
    vals = [1.0 + i * 0.001 for i in range(200)]
    s = pd.Series(vals, index=pd.date_range("2021-01-31", periods=200, freq="ME"))
    z = paired(s, s, "same")
    t = pd.Series([1.0] + [1.004 ** i for i in range(1, 200)], index=s.index)
    sh = paired(t, s, "shift")
    leg("L12 paired() zero on the same book, non-zero on a shifted one",
        z["mean_pp"] == 0.0 and sh["mean_pp"] not in (0.0, None), "%r/%r" % (z, sh))

    # L13-L18 the check must be able to say "the world moved", and only then (r1935/r2165)
    gate = {"line_pct": 1.0, "line_frac": 0.01, "lens_cny": 1_000_000.0}
    face = {"inputs": {"panel_last_bar": "2026-11-26", "gate": dict(gate)},
            "criteria": {"line_frac": 0.01, "slots": 5, "lens_cny": 1_000_000.0,
                         "per_name_cny": 200_000.0, "need_adv_cny": 20_000_000.0},
            "capacity_rows": {"A_published": [], "B_floor": []},
            "substitution": {"rebalances": 10, "rebalances_with_a_substitution": 0,
                             "share_of_rebalances": 0.0},
            "paired_ba": {"mean_pp": 0.0, "months": 60}, "paired_br": {"mean_pp": 0.2,
                                                                      "t": 2.5,
                                                                      "months": 60},
            "verdict": "NO_CONFLICT"}
    leg("L13 a face on its own bar and ruler has nothing to age",
        drift(face, "2026-11-26", dict(gate)) == [],
        "%r" % (drift(face, "2026-11-26", dict(gate)),))
    leg("L14 the panel rolling a bar reads as drift",
        bool(drift(face, "2026-11-27", dict(gate))))
    leg("L15 a re-published gate ruler reads as drift",
        bool(drift(face, "2026-11-26", {"line_pct": 2.0, "line_frac": 0.02,
                                        "lens_cny": 1_000_000.0})))
    leg("L16 a face with no recorded anchor is not 'fine'", bool(drift({}, "2026-11-26", gate)))

    def _run_check(pl, live_bar, live_gate):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc = check(pl, live_bar, live_gate)
        return rc, buf.getvalue()

    rc, txt = _run_check(face, "2026-11-27", dict(gate))
    leg("L17 end-to-end: a rolled panel is rc3 and says STALE", rc == 3 and "STALE" in txt,
        "rc=%r" % (rc,))
    bad = json.loads(json.dumps(face))
    bad["substitution"]["share_of_rebalances"] = 0.9
    rc, txt = _run_check(bad, "2026-11-26", dict(gate))
    leg("L18 end-to-end: a number that will not re-derive is rc1 and never says STALE",
        rc == 1 and "STALE" not in txt, "rc=%r txt=%r" % (rc, txt[:80]))

    bad = [c for c in checks if not c[1]]
    for name, ok, detail in checks:
        print("  %-58s %s %s" % (name[:58], "PASS" if ok else "FAIL", detail if not ok else ""))
    print("selftest %d/%d PASS" % (len(checks) - len(bad), len(checks)))
    return 0 if not bad else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("cmd", nargs="?", default="run", choices=("run", "check", "selftest"))
    args = ap.parse_args(argv)
    if args.cmd == "run":
        return run()
    if args.cmd == "check":
        return check()
    return selftest()


if __name__ == "__main__":
    sys.exit(main())
