#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""ETF book -- the liquidity floor, read in the two eras the book already splits itself into.

r1875 priced the depth screen over the whole window and answered SUBSTITUTION_NOT_SEPARABLE:
the capacity uplift is mechanical (every floored pick clears the need by construction) and
the return difference sits inside its own noise. That reading is an average over 84
rebalances spanning two very different markets -- the book's own workbook splits them at
2023-12-31 (IS/OOS), and every capacity face already prints that split.

This face asks the question a desk actually faces: does the same rule, read only where the
money has been made lately (2024-01-01 onwards), buy capacity without paying returns?

  arm A  the published book            (plain top-5, nothing added)
  arm B  same scores, skip names whose capacity ADV < 200,000 / 1% (= 20M), fill from below
  arm R  drop as many picks per date at RANDOM and fill from below

Nothing new is implemented: the arms, the ADV walk, the capacity algebra, the random-fill
and the verdict doors all come from `etf_book_liquidity_select` (r1875); the era boundary
comes from `etf_book_scale_floor.IS_END` (the book's own split). This face only slices.

Criterion, frozen before the read (also written into the payload):

  D1 binds : the era's substitution share >= 1% of that era's rebalances;
             else NO_CONFLICT_IN_THIS_ERA -- the two rulers agree and there is nothing
             to adopt in this era.
  D2 pays  : within the era, paired monthly (B-A) >= -0.50pp AND paired monthly (B-R) > 0
             with |t| >= 2.0 over >= 24 paired months -> GATE_PAYS_IN_THIS_ERA;
             a (B-R) that cannot clear its own noise -> NOT_SEPARABLE_IN_THIS_ERA;
             an era with fewer than 24 paired months -> ERA_TOO_SHORT_TO_READ
             (a t-stat on 11 months is not a reading).
  otherwise GATE_COSTS_MORE_THAN_IT_BUYS_IN_THIS_ERA.

The headline verdict is the LATE era's verdict, because that is the regime the desk is
trading. The early era and the full window are printed beside it, never averaged into it.
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
import etf_book_liquidity_select as LS  # noqa: E402
import etf_book_scale_floor as S  # noqa: E402
import etf_robust_pf as R  # noqa: E402

OUT_JSON = os.path.join(ROOT, "results", "etf_book_liquidity_era.json")
OUT_MD = os.path.join(ROOT, "results", "etf_book_liquidity_era.md")
UPSTREAM_JSON = os.path.join(ROOT, "results", "etf_book_liquidity_select.json")

SLOTS = LS.SLOTS
REBAL = LS.REBAL
COST = LS.COST
VOL_TARGET = LS.VOL_TARGET
SEED = LS.SEED
START = pd.Timestamp(getattr(R, "START", "2020-01-01"))
IS_END = pd.Timestamp(getattr(S, "IS_END", "2023-12-31"))

CRIT = {
    "bind_share_min": 0.01,
    "cagr_tol_pp": 0.50,
    "t_min": 2.0,
    "min_paired_months": 24,
}

# Frozen before the read: the book's own IS/OOS boundary, not a boundary chosen after seeing
# where the returns sit. Two eras, half-open on the left, inclusive on the right.
ERAS = (
    {"name": "is_2020_2023", "label": "2020-2023", "start": str(START.date()),
     "end": str(IS_END.date())},
    {"name": "oos_2024_", "label": "2024-2026", "start": str((IS_END + pd.Timedelta(days=1)).date()),
     "end": None},
)


# ------------------------------------------------------------------ monthly reading

def monthly_returns(ser):
    """Month-end levels -> month-over-month returns.

    Computed on the FULL series so the first month inside an era still carries its own
    month-over-month move; slicing the levels first would silently drop it.
    """
    lv = ser.dropna().resample("ME").last()
    return lv.pct_change().dropna()


def paired_months(mb, ma, label, start=None, end=None):
    """Paired monthly difference of two return series restricted to one era."""
    j = pd.concat([mb.rename("b"), ma.rename("a")], axis=1).dropna()
    if start is not None:
        j = j[j.index >= pd.Timestamp(start)]
    if end is not None:
        j = j[j.index <= pd.Timestamp(end)]
    d = j["b"] - j["a"]
    n = int(len(d))
    out = {"label": label, "months": n, "mean_pp": None, "t": None,
           "b_better_months": int((d > 0).sum()) if n else None}
    if n == 0:
        out["why"] = "no calendar month inside this era carries both books"
        return out
    mean = float(d.mean())
    sd = float(d.std(ddof=1)) if n > 1 else 0.0
    out["mean_pp"] = round(mean * 100.0, 4)
    out["t"] = round(mean / (sd / math.sqrt(n)), 3) if (n > 1 and sd > 0) else None
    return out


def months_in(ser_ret, start, end):
    s = ser_ret
    s = s[s.index >= pd.Timestamp(start)]
    if end is not None:
        s = s[s.index <= pd.Timestamp(end)]
    return s


# ------------------------------------------------------------------ era slicing

def in_era(key, start, end):
    d = pd.Timestamp(key)
    if d < pd.Timestamp(start):
        return False
    if end is not None and d > pd.Timestamp(end):
        return False
    return True


def caps_in_era(rows, start, end, lens):
    """Capacity summary over the rows whose decision date falls inside the era."""
    picked = [dict(r) for r in rows if in_era(r["date"], start, end)]
    return LS.cap_summary(picked, lens), picked


def by_year(keys):
    out = {}
    for k in keys:
        y = str(pd.Timestamp(k).year)
        out[y] = out.get(y, 0) + 1
    return dict(sorted(out.items()))


def era_block(name, label, start, end, dec_dates, subs, cap_a, cap_b, ret_a, ret_b, ret_r,
              lens):
    """One era: the same four numbers r1875 prints, restricted to that era's months."""
    dates = [str(pd.Timestamp(d).date()) for d in dec_dates if in_era(pd.Timestamp(d), start, end)]
    sub_dates = [k for k in dates if subs.get(k, 0) > 0]
    n_sub = sum(subs.get(k, 0) for k in dates)
    sum_a, rows_a = caps_in_era(cap_a, start, end, lens)
    sum_b, rows_b = caps_in_era(cap_b, start, end, lens)
    blk = {
        "name": name,
        "label": label,
        "start": start,
        "end": end,
        "rebalances": len(dates),
        "substitution": {
            "rebalances": len(dates),
            "rebalances_with_a_substitution": len(sub_dates),
            "share_of_rebalances": round(len(sub_dates) / len(dates), 4) if dates else None,
            "names_substituted": int(n_sub),
            "trigger_years": by_year(sub_dates),
            "rebalance_years": by_year(dates),
            "first_trigger": sub_dates[0] if sub_dates else None,
            "last_trigger": sub_dates[-1] if sub_dates else None,
        },
        "capacity": {"A_published": sum_a, "B_floor": sum_b},
        "capacity_uplift_median": (
            round(sum_b["median_cny"] / sum_a["median_cny"], 4)
            if (sum_b.get("median_cny") and sum_a.get("median_cny")) else None),
        "paired_ba": paired_months(ret_b, ret_a, "B-A", start, end),
        "paired_br": paired_months(ret_b, ret_r, "B-R", start, end),
    }
    blk["verdict"] = era_verdict(blk)
    return blk


def era_verdict(blk):
    """Derived from the block's own published counts (check() re-runs this)."""
    sub = blk.get("substitution") or {}
    share = sub.get("share_of_rebalances")
    if share is None or share < CRIT["bind_share_min"]:
        return "NO_CONFLICT_IN_THIS_ERA"
    br = blk.get("paired_br") or {}
    ba = blk.get("paired_ba") or {}
    if (br.get("months") or 0) < CRIT["min_paired_months"]:
        return "ERA_TOO_SHORT_TO_READ"
    t = br.get("t")
    if t is None or abs(t) < CRIT["t_min"]:
        return "NOT_SEPARABLE_IN_THIS_ERA"
    if (br.get("mean_pp") or 0.0) > 0 and (ba.get("mean_pp") or 0.0) >= -CRIT["cagr_tol_pp"]:
        return "GATE_PAYS_IN_THIS_ERA"
    return "GATE_COSTS_MORE_THAN_IT_BUYS_IN_THIS_ERA"


# ------------------------------------------------------------------ upstream reconciliation

def reconcile(ours, upstream_path=UPSTREAM_JSON, tol=1e-4):
    """Compare the full-window arms against r1875's own toast.

    A different evidence cutoff is a generation difference, not a defect (r1311): it is
    reported as `generation_differs` and never fails the face. Only two faces cut on the
    SAME bar are comparable number for number.
    """
    out = {"upstream": os.path.basename(upstream_path), "present": os.path.exists(upstream_path),
           "same_cutoff": None, "checked": False, "deltas": [], "note": None}
    if not out["present"]:
        out["note"] = "upstream face absent: nothing to reconcile against"
        return out
    with open(upstream_path, "r", encoding="utf-8") as f:
        up = json.load(f)
    out["upstream_cutoff"] = up.get("evidence_cutoff")
    out["same_cutoff"] = (up.get("evidence_cutoff") == ours.get("evidence_cutoff"))
    if not out["same_cutoff"]:
        out["note"] = ("upstream face is a different generation (cut %s vs %s): not compared "
                       "number for number" % (up.get("evidence_cutoff"), ours.get("evidence_cutoff")))
        return out
    out["checked"] = True
    for arm in ("A_published", "B_floor", "R_random_fill"):
        u = ((up.get("arms") or {}).get(arm) or {}).get("stats") or {}
        o = ((ours.get("arms") or {}).get(arm) or {}).get("stats") or {}
        for k in ("cagr", "sharpe", "maxdd"):
            if u.get(k) is None or o.get(k) is None:
                continue
            if abs(float(u[k]) - float(o[k])) > tol:
                out["deltas"].append({"arm": arm, "field": k, "upstream": u[k], "here": o[k]})
    return out


# ------------------------------------------------------------------ run

def _stats(ser):
    st = A.stats2(ser, "era")
    blk = {k: (None if st.get(k) is None else round(float(st[k]), 4))
           for k in ("cagr", "sharpe", "maxdd") if k in st}
    blk.update(S.sub_stats(ser))
    return blk


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
    dates = [d for d in op.index if d >= START]
    dec_dates = [dates[i] for i in range(0, len(dates) - 1, REBAL)]
    print("panel %d names / %d rebalances / need ADV %.0f"
          % (len(close.columns), len(dec_dates), need), flush=True)
    adv = LS.adv_at_dates(amt, dec_dates)

    ctrl, floor_picks, subs, fallbacks = {}, {}, {}, []
    for d in dec_dates:
        key = str(pd.Timestamp(d).date())
        row = sc.loc[d]
        base = [str(x) for x in row.dropna().nlargest(SLOTS).index]
        ctrl[key] = base
        picks, blocked, fb = LS.picks_with_floor(row, adv.get(key, {}), need, SLOTS)
        floor_picks[key] = picks
        if fb:
            fallbacks.append(key)
        subs[key] = len(set(base) - set(picks))

    rng = random.Random(SEED)
    rand_picks = {}
    for d in dec_dates:
        key = str(pd.Timestamp(d).date())
        ranked = [str(x) for x in sc.loc[d].dropna().sort_values(ascending=False).index]
        rand_picks[key] = LS.random_fill(ctrl[key], ranked, subs[key], rng)

    def book(picks_map):
        return R.open_to_open_equity(close, openp, amt, sc, REBAL, SLOTS, COST,
                                     vol_target=VOL_TARGET, vol_floor=0.0,
                                     select_hook=LS._hook(picks_map))

    ser_a, turn_a = R.open_to_open_equity(close, openp, amt, sc, REBAL, SLOTS, COST,
                                          vol_target=VOL_TARGET, vol_floor=0.0)
    ser_b, turn_b = book(floor_picks)
    ser_r, turn_r = book(rand_picks)

    ret_a, ret_b, ret_r = (monthly_returns(ser_a), monthly_returns(ser_b),
                           monthly_returns(ser_r))
    cap_a = LS.cap_rows(ctrl, adv, line)
    cap_b = LS.cap_rows(floor_picks, adv, line)
    cap_r = LS.cap_rows(rand_picks, adv, line)

    eras = []
    for spec in ERAS:
        eras.append(era_block(spec["name"], spec["label"], spec["start"], spec["end"],
                             dec_dates, subs, cap_a, cap_b, ret_a, ret_b, ret_r, lens))

    full = {
        "name": "full_window", "label": "2020-2026", "start": str(START.date()), "end": None,
        "rebalances": len(dec_dates),
        "substitution": {
            "rebalances": len(dec_dates),
            "rebalances_with_a_substitution": sum(1 for v in subs.values() if v > 0),
            "share_of_rebalances": round(sum(1 for v in subs.values() if v > 0) / len(dec_dates), 4),
            "names_substituted": int(sum(subs.values())),
            "trigger_years": by_year([k for k, v in subs.items() if v > 0]),
            "rebalance_years": by_year(list(subs)),
            "fallback_dates": fallbacks,
        },
        "capacity": {"A_published": LS.cap_summary(cap_a, lens),
                     "B_floor": LS.cap_summary(cap_b, lens)},
        "paired_ba": paired_months(ret_b, ret_a, "B-A"),
        "paired_br": paired_months(ret_b, ret_r, "B-R"),
    }
    full["verdict"] = era_verdict(full)

    payload = {
        "face": "etf_book_liquidity_era",
        "generated": pd.Timestamp.now(tz="Asia/Shanghai").isoformat(timespec="seconds"),
        "evidence_cutoff": str(pd.Timestamp(ser_a.index[-1]).date()),
        "inputs": {
            "panel_last_bar": LS.panel_bar() or str(pd.Timestamp(close.index[-1]).date()),
            "gate": LS.gate_ruler() or {"line_pct": rituals.get("line_pct"),
                                        "line_frac": line, "lens_cny": lens},
            "data_end": str(pd.Timestamp(close.index[-1]).date()),
            "why": "what this face priced; check() ages the face against the live panel and "
                   "the live gate instead of only re-deriving its own rows (r2167)",
        },
        "criteria": {
            "line_pct": rituals.get("line_pct"), "line_frac": line,
            "lens_cny": lens, "lens_label": rituals.get("lens"),
            "slots": SLOTS, "per_name_cny": per_name, "need_adv_cny": need,
            "rebal": REBAL, "cost_per_side": COST, "vol_target": VOL_TARGET,
            "seed": SEED, "start": str(START.date()), "is_end": str(IS_END.date()),
            "eras": [dict(e) for e in ERAS],
            "frozen": dict(CRIT),
            "why_two_eras": "the boundary is the book's own IS/OOS split (etf_book_scale_floor."
                            "IS_END), not a line chosen after seeing where the returns sit",
        },
        "arms": {
            "A_published": {"turnover": round(turn_a, 3), "stats": _stats(ser_a)},
            "B_floor": {"turnover": round(turn_b, 3), "stats": _stats(ser_b)},
            "R_random_fill": {"turnover": round(turn_r, 3), "stats": _stats(ser_r)},
        },
        "eras": eras,
        "full_window": full,
        "capacity_rows": {"A_published": cap_a, "B_floor": cap_b, "R_random_fill": cap_r},
        "honest": [
            "the eras are the book's own IS/OOS split: slicing the SAME path twice is not two "
            "independent samples, and the late era is shorter (its t is computed on its own "
            "months and says so)",
            "the vol-target overlay is fitted over the whole path before slicing, so an era's "
            "sharpe is read off the same weights the published book carries -- this face "
            "re-runs the book, it does not re-fit it",
            "capacity is bought MECHANICALLY by B inside either era (every floored pick clears "
            "the need by construction); the uplift is not evidence, the paid price is",
            "the panel is a survivors sweep (r1319/r1874): names the source never served could "
            "not have been ranked in any arm of any era",
            "nothing here is adopted: this face prices the same rule per era; a rule that pays "
            "in only one era is a regime statement, not a gate",
        ],
        "elapsed_sec": round(time.time() - t0, 2),
    }
    payload["verdict"] = eras[-1]["verdict"]
    payload["repro"] = reconcile(payload)
    payload["sentence"] = _sentence(payload)

    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=1)
    with open(OUT_MD, "w", encoding="utf-8") as f:
        f.write(render_md(payload))
    print("eras %s | late=%s | repro checked=%s"
          % (" / ".join("%s:%s" % (e["label"], e["verdict"]) for e in eras),
             payload["verdict"], payload["repro"].get("checked")), flush=True)
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


_HEADLINE = {
    "GATE_PAYS_IN_THIS_ERA": "在最近这一段里，这条闸既买到了容量又没赔收益",
    "NOT_SEPARABLE_IN_THIS_ERA": "在最近这一段里，容量是机械买到的，收益差读不出",
    "GATE_COSTS_MORE_THAN_IT_BUYS_IN_THIS_ERA": "在最近这一段里，这条闸买到容量的代价高于它买到的东西",
    "NO_CONFLICT_IN_THIS_ERA": "在最近这一段里，两把尺没有分家，没有可采纳的东西",
    "ERA_TOO_SHORT_TO_READ": "最近这一段太短，读不出结论",
}


def _sentence(p):
    late = p["eras"][-1]
    early = p["eras"][0]
    caps = (late["capacity"]["A_published"], late["capacity"]["B_floor"])
    head = ("%s（%s）：%d/%d 次调仓里 %d 次需要替换，容量最薄日 %s → %s"
            % (_HEADLINE.get(late["verdict"], late["verdict"]), late["label"],
               late["substitution"]["rebalances_with_a_substitution"],
               late["substitution"]["rebalances"],
               late["substitution"]["names_substituted"],
               _m(caps[0].get("min_cny")), _m(caps[1].get("min_cny"))))
    tail = ("；B-A %s pp/月 t=%s，B-R %s pp/月 t=%s（%d 个月）；对照前段 %s 判 %s"
            % (late["paired_ba"].get("mean_pp"), late["paired_ba"].get("t"),
               late["paired_br"].get("mean_pp"), late["paired_br"].get("t"),
               late["paired_br"].get("months") or 0,
               early["label"], early["verdict"]))
    return head + tail


def render_md(p):
    c = p["criteria"]
    lines = ["# 流动性闸的年代读数：同一条规则，在钱赚得最多的那一段还成不成立", "",
             "证据截止 %s · 门 %.0f 万口径 · 每名需要 ADV %s · 槽位 %d · 调仓 %d 日"
             % (p["evidence_cutoff"], (c["lens_cny"] or 0) / 1e4, _m(c["need_adv_cny"]),
                c["slots"], c["rebal"]), "",
             "## 判词：%s（%s）" % (p["verdict"], p["eras"][-1]["label"]), "",
             p.get("sentence") or "", "",
             "| 段 | 调仓 | 触发 | 换名 | 容量中位 A | 容量中位 B | 容量最薄 A | 容量最薄 B "
             "| B-A pp/月 | t | B-R pp/月 | t | 判词 |",
             "|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for e in p["eras"] + [p["full_window"]]:
        sub = e["substitution"]
        ca, cb = e["capacity"]["A_published"], e["capacity"]["B_floor"]
        lines.append("| %s | %d | %d | %d | %s | %s | %s | %s | %s | %s | %s | %s | %s |"
                     % (e["label"], sub["rebalances"], sub["rebalances_with_a_substitution"],
                        sub["names_substituted"], _m(ca.get("median_cny")),
                        _m(cb.get("median_cny")), _m(ca.get("min_cny")), _m(cb.get("min_cny")),
                        e["paired_ba"].get("mean_pp"), e["paired_ba"].get("t"),
                        e["paired_br"].get("mean_pp"), e["paired_br"].get("t"),
                        e["verdict"]))
    lines += ["", "## 触发日落在哪几年", "",
              "每格=「该年调仓次数 / 其中触发了多少次替换」。**0 次触发但当年有调仓**=这一年两把尺"
              "没有分家（读作结论），与「这一年不在窗口里」不是同一件事，所以两种都印出来。", "",
              "| 段 | 逐年 |", "|---|---|"]
    for e in p["eras"] + [p["full_window"]]:
        sub = e["substitution"]
        reb_y = sub.get("rebalance_years") or {}
        trig_y = sub.get("trigger_years") or {}
        cells = ["%s %d/%d" % (y, reb_y.get(y, 0), trig_y.get(y, 0)) for y in sorted(reb_y)]
        lines.append("| %s | %s |" % (e["label"], " · ".join(cells) if cells else "-"))
    stray = sorted(set((p["full_window"].get("substitution") or {}).get("trigger_years") or {})
                   - set((p["full_window"].get("substitution") or {}).get("rebalance_years") or {}))
    if stray:
        lines.append("")
        lines.append("**触发年不在调仓年集内（%s）——面坏了，别读这张表。**" % ", ".join(stray))

    lines += ["", "## 三臂全窗（本面自算，供与 r1875 对账）", "",
              "| 臂 | 年化 | 夏普 | 回撤 | 换手 |", "|---|---|---|---|---|"]
    for key, name in (("A_published", "A 在印书"), ("B_floor", "B 加流动性闸"),
                      ("R_random_fill", "R 随机换同样多")):
        arm = p["arms"][key]
        st = arm["stats"]
        lines.append("| %s | %.2f%% | %.3f | %.2f%% | %.3f |"
                     % (name, (st.get("cagr") or 0) * 100, st.get("sharpe") or 0,
                        (st.get("maxdd") or 0) * 100, arm.get("turnover") or 0))
    rep = p.get("repro") or {}
    lines += ["", "## 与 r1875 对账", "",
              "- 上游面：%s（存在=%s，同一证据截止=%s）"
              % (rep.get("upstream"), rep.get("present"), rep.get("same_cutoff")),
              "- 已逐数比对：%s；分歧 %d 处" % (rep.get("checked"), len(rep.get("deltas") or []))]
    if rep.get("note"):
        lines.append("- 注记：%s" % rep["note"])
    lines += ["", "## 诚实边界", ""]
    for h in p["honest"]:
        lines.append("- " + h)
    return "\n".join(lines) + "\n"


# ------------------------------------------------------------------ check

def check(payload=None, live="disk", ruler="disk"):
    problems = []
    notes = []
    if payload is None:
        with open(OUT_JSON, "r", encoding="utf-8") as f:
            payload = json.load(f)
    stale = LS.drift(payload, live, ruler)
    if stale:
        print("check STALE: this face sliced a window the panel or the gate has since left "
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

    eras = payload.get("eras") or []
    if len(eras) != 2:
        problems.append("expected two eras, got %d" % len(eras))
    rb_sum = sum((e.get("substitution") or {}).get("rebalances") or 0 for e in eras)
    full = payload.get("full_window") or {}
    if full.get("rebalances") and rb_sum and rb_sum != full["rebalances"]:
        problems.append("era rebalances %d do not partition the full %d"
                        % (rb_sum, full["rebalances"]))
    fsub_rb = (full.get("substitution") or {}).get("rebalances")
    if fsub_rb and full.get("rebalances") and fsub_rb != full["rebalances"]:
        problems.append("the full window prints two rebalance counts: %s and %s"
                        % (full["rebalances"], fsub_rb))
    sub_sum = sum((e.get("substitution") or {}).get("names_substituted") or 0 for e in eras)
    if full.get("substitution") and full["substitution"].get("names_substituted") is not None \
            and sub_sum and sub_sum != full["substitution"]["names_substituted"]:
        problems.append("era substitutions %d do not sum to the full %d"
                        % (sub_sum, full["substitution"]["names_substituted"]))
    trig_sum = sum((e.get("substitution") or {}).get("rebalances_with_a_substitution") or 0
                   for e in eras)
    if full.get("substitution") and trig_sum and \
            trig_sum != (full["substitution"].get("rebalances_with_a_substitution") or 0):
        problems.append("era trigger dates do not sum to the full window's")

    for e in eras:
        sub = e.get("substitution") or {}
        n, t = sub.get("rebalances") or 0, sub.get("rebalances_with_a_substitution")
        if t is not None and n and t > n:
            problems.append("%s: more trigger dates than rebalances" % e.get("name"))
        ys = sub.get("trigger_years") or {}
        if t is not None and sum(ys.values()) != t:
            problems.append("%s: trigger_years do not sum to the trigger count" % e.get("name"))
        ry = sub.get("rebalance_years") or {}
        if n and ry and sum(ry.values()) != n:
            problems.append("%s: rebalance_years do not sum to the rebalance count" % e.get("name"))
        if set(ys) - set(ry):
            problems.append("%s: a trigger lands in a year with no rebalance" % e.get("name"))
        again = era_verdict(e)
        if again != e.get("verdict"):
            problems.append("%s: verdict %r re-derives as %r"
                            % (e.get("name"), e.get("verdict"), again))
        b_months = (e.get("paired_br") or {}).get("months")
        if b_months is not None and b_months > n * 3:
            problems.append("%s: more paired months than the era can hold" % e.get("name"))

    late = eras[-1] if eras else {}
    if late.get("verdict") and payload.get("verdict") != late["verdict"]:
        problems.append("headline verdict is not the late era's verdict")

    rep = payload.get("repro") or {}
    if rep.get("checked") and rep.get("deltas"):
        problems.append("full-window arms disagree with the upstream face in %d field(s)"
                        % len(rep["deltas"]))
    if rep.get("note"):
        notes.append(rep["note"])

    ok = not problems
    if problems:
        # A number that will not re-derive is a defect, not a moved world: the chain must
        # not buy a rebuild for it, so this line never carries the word STALE (r1934).
        print("check FAIL:")
        for x in problems:
            print("  -", x)
        return 1
    print(json.dumps({"ok": ok, "problems": problems, "notes": notes,
                      "verdict": payload.get("verdict")}, ensure_ascii=False))
    return 0 if ok else 1


# ------------------------------------------------------------------ selftest

def selftest() -> int:
    checks = []

    def leg(name, ok, detail=""):
        checks.append((name, bool(ok), detail))

    # L1 month-over-month is computed on the full path, so the first month of an era keeps
    # its own move instead of vanishing (the classic slice-then-diff bug)
    idx = pd.date_range("2020-01-31", periods=48, freq="ME")
    lv = pd.Series([100.0 * (1.01 ** i) for i in range(48)], index=idx)
    ser = lv.copy()
    ret = monthly_returns(ser)
    leg("L1 monthly returns keep the first month of a slice",
        len(ret) == 47 and abs(ret.iloc[0] - 0.01) < 1e-12, "%d months" % len(ret))

    # L2 the two eras partition the return months exactly -- no month counted twice, none lost
    is_idx = pd.date_range("2021-01-31", "2023-12-31", freq="ME")
    oos_idx = pd.date_range("2024-01-31", "2026-11-30", freq="ME")
    leg("L2 eras partition the months",
        len(is_idx) + len(oos_idx) == len(is_idx.union(oos_idx))
        and len(is_idx.intersection(oos_idx)) == 0,
        "is=%d oos=%d" % (len(is_idx), len(oos_idx)))

    # L3 a gain that only exists in the late era is read only there
    a = pd.Series(1.0, index=pd.date_range("2021-01-31", periods=60, freq="ME"))
    b = a.copy()
    levels = [1.0] * 36
    for _ in range(24):                      # 2024-01 onwards compounds +1% a month
        levels.append(levels[-1] * 1.01)
    b = pd.Series(levels, index=a.index)
    early = paired_months(b.pct_change().dropna(), a.pct_change().dropna(), "B-A",
                          "2021-01-01", "2023-12-31")
    late = paired_months(b.pct_change().dropna(), a.pct_change().dropna(), "B-A",
                         "2024-01-01", None)
    leg("L3 a late-only gain is read late and not early",
        abs(early["mean_pp"] or 0.0) < 1e-9 and abs((late["mean_pp"] or 0.0) - 1.0) < 1e-6,
        "early=%r late=%r" % (early["mean_pp"], late["mean_pp"]))

    # L4-L7 verdict doors read only the block's own counts
    def blk(share, months, t, br_pp, ba_pp=-0.1):
        return {"substitution": {"share_of_rebalances": share},
                "paired_ba": {"mean_pp": ba_pp, "t": 1.0},
                "paired_br": {"mean_pp": br_pp, "t": t, "months": months}}

    leg("L4 no bind -> NO_CONFLICT", era_verdict(blk(0.0, 40, 3.0, 0.5)) == "NO_CONFLICT_IN_THIS_ERA")
    leg("L5 short era -> ERA_TOO_SHORT_TO_READ",
        era_verdict(blk(0.2, 11, 9.0, 5.0)) == "ERA_TOO_SHORT_TO_READ")
    leg("L6 inside noise -> NOT_SEPARABLE",
        era_verdict(blk(0.2, 35, 1.1, 0.5)) == "NOT_SEPARABLE_IN_THIS_ERA")
    leg("L7 pays -> GATE_PAYS / costs -> COSTS",
        era_verdict(blk(0.2, 35, 2.5, 0.5)) == "GATE_PAYS_IN_THIS_ERA"
        and era_verdict(blk(0.2, 35, -2.5, -0.5)) == "GATE_COSTS_MORE_THAN_IT_BUYS_IN_THIS_ERA")

    # L8 a giant mean with a thin t is still not a reading (the price of a short era)
    leg("L8 big mean + thin t never prints PAYS",
        era_verdict(blk(0.2, 35, 0.9, 9.0)) == "NOT_SEPARABLE_IN_THIS_ERA")

    # L9 trigger_years sum to the trigger count (the split cannot invent or lose a day)
    keys = ["2021-03-01", "2021-07-01", "2024-02-01", "2025-05-01", "2025-09-01"]
    ys = by_year(keys)
    leg("L9 trigger_years sum to the count", sum(ys.values()) == len(keys), "%r" % (ys,))

    # L10 capacity rows are filtered by their own date, and an unpriced row is not a zero
    rows = [{"date": "2022-06-01", "cap_cny": 1e6, "worst_adv_cny": 2e7},
            {"date": "2025-06-01", "cap_cny": None, "worst_adv_cny": None},
            {"date": "2025-07-01", "cap_cny": 3e6, "worst_adv_cny": 6e7}]
    s_late, picked = caps_in_era(rows, "2024-01-01", None, 1e6)
    leg("L10 era capacity excludes other eras and never prices an unpriced row",
        len(picked) == 2 and s_late["n_priced"] == 1 and s_late["min_cny"] == 3e6,
        "%r" % (s_late,))

    # L11 reconciliation across generations is a note, not a failure
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        p = os.path.join(td, "up.json")
        with open(p, "w", encoding="utf-8") as f:
            json.dump({"evidence_cutoff": "2026-11-19",
                       "arms": {"A_published": {"stats": {"cagr": 0.1138}}}}, f)
        r_same = reconcile({"evidence_cutoff": "2026-11-19",
                            "arms": {"A_published": {"stats": {"cagr": 0.1138}}}}, p)
        r_diff = reconcile({"evidence_cutoff": "2026-11-18",
                            "arms": {"A_published": {"stats": {"cagr": 0.1000}}}}, p)
    leg("L11 same cutoff compares, different cutoff is a note",
        r_same["checked"] and not r_same["deltas"]
        and (not r_diff["checked"]) and r_diff["note"], "%r / %r" % (r_same, r_diff))

    # L12 a real disagreement on the same cutoff IS flagged
    with tempfile.TemporaryDirectory() as td:
        p = os.path.join(td, "up.json")
        with open(p, "w", encoding="utf-8") as f:
            json.dump({"evidence_cutoff": "2026-11-19",
                       "arms": {"A_published": {"stats": {"cagr": 0.1138}}}}, f)
        bad = reconcile({"evidence_cutoff": "2026-11-19",
                         "arms": {"A_published": {"stats": {"cagr": 0.1100}}}}, p)
    leg("L12 same-cutoff disagreement is flagged", len(bad["deltas"]) == 1, "%r" % (bad["deltas"],))

    # L13 the printed table names a zero-trigger year beside its own rebalance count --
    # "nothing fired in 2022" must not read the same as "2022 is not in the window"
    rp = {
        "evidence_cutoff": "2026-11-19",
        "criteria": {"lens_cny": 1e6, "need_adv_cny": 2e7, "slots": 5, "rebal": 20},
        "verdict": "NOT_SEPARABLE_IN_THIS_ERA",
        "sentence": "",
        "eras": [{"name": "is_x", "label": "2020-2023",
                  "substitution": {"rebalances": 2, "rebalances_with_a_substitution": 0,
                                   "names_substituted": 0, "share_of_rebalances": 0.0,
                                   "trigger_years": {}, "rebalance_years": {"2022": 2}},
                  "capacity": {"A_published": {"median_cny": 1e6, "min_cny": 1e6},
                               "B_floor": {"median_cny": 1e6, "min_cny": 1e6}},
                  "paired_ba": {}, "paired_br": {}, "verdict": "NO_CONFLICT_IN_THIS_ERA"}],
        "full_window": {"label": "2020-2026",
                        "substitution": {"rebalances": 2, "rebalances_with_a_substitution": 0,
                                         "names_substituted": 0, "share_of_rebalances": 0.0,
                                         "trigger_years": {}, "rebalance_years": {"2022": 2}},
                        "capacity": {"A_published": {"median_cny": 1e6, "min_cny": 1e6},
                                     "B_floor": {"median_cny": 1e6, "min_cny": 1e6}},
                        "paired_ba": {}, "paired_br": {},
                        "verdict": "NO_CONFLICT_IN_THIS_ERA"},
        "arms": {"A_published": {"stats": {"cagr": 0.1, "sharpe": 1.0, "maxdd": -0.1},
                                 "turnover": 1.0},
                 "B_floor": {"stats": {"cagr": 0.1, "sharpe": 1.0, "maxdd": -0.1},
                             "turnover": 1.0},
                 "R_random_fill": {"stats": {"cagr": 0.1, "sharpe": 1.0, "maxdd": -0.1},
                                   "turnover": 1.0}},
        "repro": {}, "honest": [],
    }
    md = render_md(rp)
    leg("L13 a zero-trigger year prints beside its rebalances", "2022 2/0" in md,
        "row missing from the printed table")

    # L14-L16 this check must be able to say "the world moved", and only then (r1935/r2165)
    gate = {"line_pct": 1.0, "line_frac": 0.01, "lens_cny": 1_000_000.0}
    rp["inputs"] = {"panel_last_bar": "2026-11-26", "gate": dict(gate)}
    leg("L14 a face on its own bar and ruler has nothing to age",
        LS.drift(rp, "2026-11-26", dict(gate)) == [],
        "%r" % (LS.drift(rp, "2026-11-26", dict(gate)),))

    def _run_check(pl, live_bar, live_gate):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc = check(pl, live_bar, live_gate)
        return rc, buf.getvalue()

    rc, txt = _run_check(rp, "2026-11-27", dict(gate))
    leg("L15 end-to-end: a rolled panel is rc3 and says STALE", rc == 3 and "STALE" in txt,
        "rc=%r" % (rc,))
    rc, txt = _run_check(rp, "2026-11-26", dict(gate))
    leg("L16 end-to-end: a structural mismatch is rc1 and never says STALE",
        rc == 1 and "STALE" not in txt, "rc=%r txt=%r" % (rc, txt[:80]))

    bad_legs = [c for c in checks if not c[1]]
    for name, ok, detail in checks:
        print("  %-62s %s %s" % (name[:62], "PASS" if ok else "FAIL", detail if not ok else ""))
    print("selftest %d/%d PASS" % (len(checks) - len(bad_legs), len(checks)))
    return 0 if not bad_legs else 1


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
