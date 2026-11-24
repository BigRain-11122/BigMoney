#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""cash_leg_shelf_decision -- which shelf may hold the cash leg, and how large is
the tail compared with the extra it rides on?

WHY THIS FACE EXISTS
--------------------
`cb_parking_bakeoff` (r2040) priced the *class* ("convertibles pay 1.83% against the repo
leg's 1.77%, and they fall 0.665% on the days the book defends"), and
`cb_parking_shelf_at_size` (r2041) priced the *shelf* ("two orders absorb the cash leg, one
defence day costs 3.7 years of the extra").  Both faces then stopped on the convertibles the
CEO's order named.

But the shelf face already measured five shelves on one ruler -- two convertibles, one money
ETF, one short-financing ETF, one treasury ETF, each at the same ticket size, each with the
same defence-day reading.  Nobody ever asked the treasurer's actual question across all of
them: **which of these may the cash leg sit in at all?**  A shelf has to pass two gates the
book owns (it must pay more than the repo leg, and it must not lose money on the days the
book defends) and one the tape owns (the order must fit on a bad day).  The CEO's convertibles
idea is one candidate among five, not the frame.

So this face is a decision table, not a new measurement.  It re-reads the published rows,
applies the three gates mechanically, names the shelf that survives, and prints the number
that decides the argument: **how many yuan of annual tail swing ride on one yuan of annual
extra**.  For a parking decision that ratio is the whole story -- an extra of 0.2pp sitting on
a 28pp/yr tail is not carry, it is a bet.

THE QUESTION (frozen before the first run)
------------------------------------------
At the ticket's cash size, which published shelf passes "pays more than the repo leg" AND
"holds on the days the book defends" AND "the order fits the bad day", and how does the tail
swing compare with the extra?

MODEL
-----
* **No new measurement.**  Every shelf number is imported from
  `results/cb_parking_shelf_at_size.json` (ticket tier) with the parent's own provenance
  recorded as a sha.  This face does not re-open the return construction, the panel, or the
  defence-day yardstick: if the parents move, this face says STALE and stops.
* **Gate 1 / pays more** -- the tier's effective yield (residue priced at the repo rate, the
  parent's conservative caliber) must exceed the repo net CAGR.  Mechanical, no threshold.
* **Gate 2 / holds on defence days** -- the shelf's mean return on the equity yardstick's own
  <= -1% bars must be >= 0.  A cash leg is a place the book hides; a shelf that falls exactly
  when the book falls is the opposite of that job.
* **Gate 3 / fits the tape** -- the parent's participation class at the ticket's cash must not
  be BLOCKED (OPEN is called clean, THIN is called admissible-but-thin).  The band is the
  parent's convention, imported, not retyped.
* **Defence days per year** = the parent's defence-day count divided by the parent's own
  window in years (365.25 basis).  It is a frequency, not a forecast.
* **Tail swing per year (pp)** = defence days per year x the shelf's mean defence-day return.
  It is the *annualized weight of the bad days inside the shelf's own return* -- a
  decomposition of what the parent already measured, never an amount added to or subtracted
  from the published net.
* **Tail multiple** = |tail swing per year| / |extra over the repo leg|.  One number, no taste:
  136 means one yuan of carry rides on 136 yuan of annual tail.

VERDICTS (mechanical, no taste)
-------------------------------
* THE_CASH_LEG_HAS_AN_ADMISSIBLE_SHELF   -- at least one shelf passes all three gates.
* NO_SHELF_PAYS_AND_HOLDS                -- none does.
* THE_CLEAN_SHELF_IS_<code>              -- exactly one admissible shelf is OPEN at the ticket.
* NO_SHELF_ABSORBS_THE_TICKET_CLEANLY    -- admissible shelves exist but all are THIN.
* MORE_THAN_ONE_CLEAN_SHELF              -- more than one OPEN admissible shelf.
* TAIL_DWARFS_THE_EXTRA                  -- the best convertible shelf's tail multiple >= 10
                                           while its defence mean is negative.
* DEFENCE_DAYS_PAY_FOR_MORE_THAN_THE_EXTRA -- the winner's defence days contribute, in a year,
                                           at least as much as its whole extra.
* THE_WINNER_DOMINATES_THE_CONVERTIBLE_SHELF -- the winner beats the best convertible shelf on
                                           extra, on the defence day, and on participation.

Usage:
    python scripts/cash_leg_shelf_decision.py run
    python scripts/cash_leg_shelf_decision.py --check
    python scripts/cash_leg_shelf_decision.py --selftest
"""

from __future__ import annotations

import datetime as dt
import hashlib
import io
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SHELF_JSON = os.path.join(ROOT, "results", "cb_parking_shelf_at_size.json")
BAKEOFF_JSON = os.path.join(ROOT, "results", "cb_parking_bakeoff.json")
OUT_JSON = os.path.join(ROOT, "results", "cash_leg_shelf_decision.json")
OUT_MD = os.path.join(ROOT, "research", "CASH_LEG_SHELF_DECISION.md")

SCHEMA = "cash-leg-shelf-decision/v1"
ARTIFACT = "cash_leg_shelf_decision"
ORDERS_REF = ("O-20261009-1105 (CEO: convertibles may supplement the idle periods) | "
              "follows cb_parking_bakeoff r2040 / cb_parking_shelf_at_size r2041")

DAYS_PER_YEAR = 365.25
TAIL_DWARF_FLOOR = 10.0        # "the tail is an order of magnitude bigger than the extra"


# --------------------------------------------------------------------------- helpers
def _sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def _content_sha(obj):
    blob = json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


def _now():
    return dt.datetime.now().astimezone().replace(microsecond=0).isoformat()


def _f(x, nd=2):
    """Format a number.  Never scales: every field this face prints is already in its own
    unit (pp, percent, yuan, x).  Scaling here is how a 27.343% once printed as 2734.3%."""
    if x is None:
        return "-"
    return ("%." + str(nd) + "f") % x


def years_between(start, end):
    a = dt.date.fromisoformat(start)
    b = dt.date.fromisoformat(end)
    return (b - a).days / DAYS_PER_YEAR


def tail_multiple(defence_mean_pct, extra_pp, def_days_per_year):
    """|annual tail swing| / |annual extra|.  None when there is no extra to compare with."""
    if extra_pp == 0:
        return None
    return abs(defence_mean_pct * def_days_per_year) / abs(extra_pp)


def gates_of(extra_pp, defence_mean_pct, capacity_class):
    return {
        "pays_more_than_repo": extra_pp > 0,
        "holds_on_defence_days": defence_mean_pct >= 0,
        "order_fits_the_bad_day": capacity_class != "BLOCKED",
    }


def decision_of(gates, capacity_class):
    if not gates["order_fits_the_bad_day"]:
        return "REJECTED_BLOCKED"
    if not gates["pays_more_than_repo"]:
        return "REJECTED_PAYS_LESS_THAN_THE_REPO"
    if not gates["holds_on_defence_days"]:
        return "REJECTED_FALLS_ON_DEFENCE_DAYS"
    return "ADMISSIBLE_CLEAN" if capacity_class == "OPEN" else "ADMISSIBLE_THIN_TAPE"


def pick_tier(tiers, ticket_cash):
    """The published tier that sits at the ticket's cash (never a tier above it)."""
    ok = [t for t in tiers if t <= ticket_cash + 1.0]
    return max(ok) if ok else min(tiers)


def spot_problems(spot, parent_cagr_pct):
    """What would have to be wrong with the winner's own panel for this face to be silly.

    The parent face imports its returns; that is a claim about bytes nobody in *this* face has
    read.  So the winner gets one independent rebuild, and the rebuild has to agree (r1850:
    a guard that only re-derives itself never learns anything)."""
    out = []
    if not spot or spot.get("status") != "ok":
        return out
    if spot["n_days_beyond_15pct"] != 0:
        out.append("winner's panel still holds %d bars beyond 15%% (a flip survived the repair)"
                   % spot["n_days_beyond_15pct"])
    if abs(spot["cagr_pct"] - parent_cagr_pct) > 0.05:
        out.append("winner's rebuilt CAGR %s does not reproduce the parent's %s"
                   % (_f(spot["cagr_pct"], 4), _f(parent_cagr_pct, 4)))
    if spot["worst_day_pct"] <= -3.0:
        out.append("a 'defensive' winner lost %s%% in one day" % _f(spot["worst_day_pct"], 3))
    return out


def spot_check_of(code, start, parent_cagr_pct):
    try:
        import etf_composite_pf as E  # the panel the parents themselves use
    except Exception as exc:  # pragma: no cover - environment guard
        return {"status": "unavailable", "why": repr(exc)[:160]}
    try:
        close, _o, _a, _f = E.build_panel()
        if code not in close.columns:
            return {"status": "unavailable", "why": "%s missing on the panel" % code}
        c = close[code].dropna().loc[start:]
        r = c.pct_change().dropna()
        if len(r) < 200:
            return {"status": "unavailable", "why": "fewer than 200 bars"}
        years = (c.index[-1] - c.index[0]).days / DAYS_PER_YEAR
        spot = {
            "status": "ok",
            "code": code,
            "panel": "etf_composite_pf.build_panel (35% single-day flips repaired)",
            "bars": int(len(r)),
            "first": str(c.index[0].date()),
            "last": str(c.index[-1].date()),
            "years": years,
            "cagr_pct": float(((c.iloc[-1] / c.iloc[0]) ** (1.0 / years) - 1.0) * 100.0),
            "worst_day_pct": float(r.min() * 100.0),
            "best_day_pct": float(r.max() * 100.0),
            "n_days_beyond_15pct": int((r.abs() > 0.15).sum()),
            "maxdd_pct": float((c / c.cummax() - 1.0).min() * 100.0),
            "vol_pct": float(r.std() * (252 ** 0.5) * 100.0),
        }
        spot["delta_vs_parent_cagr_pp"] = spot["cagr_pct"] - parent_cagr_pct
        spot["parent_cagr_pct"] = parent_cagr_pct
        spot["problems"] = spot_problems(spot, parent_cagr_pct)
        return spot
    except Exception as exc:  # pragma: no cover - never crash the face for a spot check
        return {"status": "unavailable", "why": repr(exc)[:160]}


# --------------------------------------------------------------------------- build
def build(write=True, verbose=True):
    t0 = dt.datetime.now()
    shelf = json.load(io.open(SHELF_JSON, encoding="utf-8"))
    bake = json.load(io.open(BAKEOFF_JSON, encoding="utf-8"))

    repo = float(shelf["comparator"]["repo_net_pct"])
    ticket_cash = float(shelf["ticket_cash_cny"])
    win = shelf["window"]
    years = years_between(win["start"], win["end"])
    tier = pick_tier([float(t) for t in shelf["tiers_cny"]], ticket_cash)
    tkey = str(int(round(tier)))

    shelves = []
    for row in shelf["rows"]:
        cap = row["capacity"].get(tkey)
        if cap is None:
            continue
        defen = row["defence"]
        def_days = int(defen["days"])
        def_days_per_year = def_days / years
        def_mean = float(defen["mean_pct"])
        eff = float(cap["effective_yield_pct"])
        extra_pp = eff - repo
        klass = cap["class"]
        g = gates_of(extra_pp, def_mean, klass)
        tail_swing = def_mean * def_days_per_year
        shelves.append({
            "code": str(row["code"]),
            "label": row["label"],
            "class": row["class"],
            "own_net_cagr_pct": float(row["own_net_cagr_pct"]),
            "effective_yield_pct": eff,
            "extra_pp": extra_pp,
            "extra_cny_per_year": float(cap["cny_per_year_vs_repo"]),
            "defence_mean_pct": def_mean,
            "defence_days": def_days,
            "defence_days_per_year": def_days_per_year,
            "defence_day_cny": float(cap["one_defence_day_cny"]),
            "tail_swing_pp_per_year": tail_swing,
            "tail_multiple": tail_multiple(def_mean, extra_pp, def_days_per_year),
            "participation_pct": float(cap["participation_pct_of_bad_day"]),
            "capacity_class": klass,
            "lot_value_cny": float(row["lot_value_cny"]),
            "residue_bp": float(cap["residue_bp"]),
            "beta_to_equity": float(row.get("beta_to_equity") or 0.0),
            "gates": g,
            "decision": decision_of(g, klass),
        })

    admissible = [s for s in shelves if s["decision"].startswith("ADMISSIBLE")]
    winner = max(admissible, key=lambda s: s["extra_cny_per_year"]) if admissible else None
    cbs = [s for s in shelves if s["class"] == "convertible"]
    cb_best = max(cbs, key=lambda s: s["extra_pp"]) if cbs else None

    face = {
        "schema": SCHEMA,
        "artifact": ARTIFACT,
        "generated": _now(),
        "evidence_cutoff": shelf["evidence_cutoff"],
        "window": {"start": win["start"], "end": win["end"], "years": years},
        "question": ("现金腿在票面规模上可以停在哪一个货架上——要求同时付得比回购多、在书防守的"
                     "那些天不掉钱、一张单吃得下坏日子的成交；以及一年里坏日子的摆动是它多赚"
                     "那一截的多少倍？"),
        "order_ref": ORDERS_REF,
        "ruler": {
            "ticket_cash_cny": ticket_cash,
            "tier_key": tkey,
            "repo_net_pct": repo,
            "defence_yardstick": "equity ETF equal weight monthly <= -1% bars (parent caliber)",
            "defence_days_per_year": next(iter(shelves))["defence_days_per_year"] if shelves else None,
            "participation_bands": "OPEN <=1% of the p10 tape, THIN <=10%, BLOCKED above (parent)",
        },
        "shelves": shelves,
        "admissible": [s["code"] for s in admissible],
        "winner": winner,
        "convertible_best": cb_best,
        "headline": {
            "winner_code": winner["code"] if winner else None,
            "winner_label": winner["label"] if winner else None,
            "winner_extra_pp": winner["extra_pp"] if winner else None,
            "winner_extra_cny_per_year": winner["extra_cny_per_year"] if winner else None,
            "winner_defence_day_cny": winner["defence_day_cny"] if winner else None,
            "winner_participation_pct": winner["participation_pct"] if winner else None,
            "winner_tail_multiple": winner["tail_multiple"] if winner else None,
            "winner_tail_swing_pp_per_year": winner["tail_swing_pp_per_year"] if winner else None,
            "cb_best_code": cb_best["code"] if cb_best else None,
            "cb_best_extra_pp": cb_best["extra_pp"] if cb_best else None,
            "cb_best_defence_mean_pct": cb_best["defence_mean_pct"] if cb_best else None,
            "cb_best_defence_day_cny": cb_best["defence_day_cny"] if cb_best else None,
            "cb_best_tail_multiple": cb_best["tail_multiple"] if cb_best else None,
            "defence_days_per_year": next(iter(shelves))["defence_days_per_year"] if shelves else None,
            "defence_days": next(iter(shelves))["defence_days"] if shelves else None,
            "n_shelves": len(shelves),
            "n_admissible": len(admissible),
        },
        "verdict": [],
        "spot_check": ({"status": "skipped", "why": "no admissible shelf to spot-check"}
                       if winner is None else
                       spot_check_of(winner["code"], win["start"],
                                     winner["own_net_cagr_pct"])),
        "not_measured": [
            "本面只重读已发布的行，不重算任何货架收益",
            "「摆动/多赚」是货架自身收益的分解，永远不是加在净年化上或从净年化里减掉的钱",
            "一年几天坏日子是窗口频率，不是对明年的预测",
            "国债货架的净年化来自根面；若那张面板只含价格、不含分红，它的票息被低估，本面继承这一偏差",
            "p10 参与带之外的流动性、各 ETF 的申赎与交收机制均未建模",
        ],
        "data_sha": {"shelf_face": _sha(SHELF_JSON), "bakeoff_face": _sha(BAKEOFF_JSON)},
    }
    face["verdict"] = verdict_of(face)

    if write:
        with io.open(OUT_JSON, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(face, fh, ensure_ascii=False, indent=2, sort_keys=False)
            fh.write("\n")
        with io.open(OUT_MD, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(render_md(face))
        face = json.load(io.open(OUT_JSON, encoding="utf-8"))
        # content hash covers everything except the three run-time envelope fields
        core = {k: v for k, v in face.items()
                if k not in ("content_sha256", "elapsed_sec", "generated")}
        face["content_sha256"] = _content_sha(core)
        face["elapsed_sec"] = round((dt.datetime.now() - t0).total_seconds(), 3)
        with io.open(OUT_JSON, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(face, fh, ensure_ascii=False, indent=2, sort_keys=False)
            fh.write("\n")

    if verbose:
        print("BUILT", ARTIFACT, "|", " ".join(face["verdict"]))
        if winner:
            print("  winner %s %s | extra %s pp (%s 元/年) | defence day %s 元 | tail x%s | %s"
                  % (winner["code"], winner["label"], _f(winner["extra_pp"], 4),
                     _f(winner["extra_cny_per_year"]), _f(winner["defence_day_cny"]),
                     _f(winner["tail_multiple"], 1), winner["decision"]))
        print("  shelves", len(shelves), "admissible", len(admissible), "elapsed",
              face.get("elapsed_sec"))
    return 0


def verdict_of(face):
    out = []
    shelves = face["shelves"]
    adm = [s for s in shelves if s["decision"].startswith("ADMISSIBLE")]
    clean = [s for s in shelves if s["decision"] == "ADMISSIBLE_CLEAN"]
    if not adm:
        out.append("NO_SHELF_PAYS_AND_HOLDS")
    else:
        out.append("THE_CASH_LEG_HAS_AN_ADMISSIBLE_SHELF")
        if len(clean) == 1:
            out.append("THE_CLEAN_SHELF_IS_" + clean[0]["code"])
        elif not clean:
            out.append("NO_SHELF_ABSORBS_THE_TICKET_CLEANLY")
        else:
            out.append("MORE_THAN_ONE_CLEAN_SHELF")
    cb = face.get("convertible_best")
    if cb:
        tm = cb["tail_multiple"]
        if tm is not None and tm >= TAIL_DWARF_FLOOR and cb["defence_mean_pct"] < 0:
            out.append("TAIL_DWARFS_THE_EXTRA")
    w = face.get("winner")
    if w:
        if w["tail_swing_pp_per_year"] > 0 and (w["tail_multiple"] or 0.0) >= 1.0:
            out.append("DEFENCE_DAYS_PAY_FOR_MORE_THAN_THE_EXTRA")
        if cb and w["extra_pp"] > cb["extra_pp"] \
                and w["defence_mean_pct"] > cb["defence_mean_pct"] \
                and w["participation_pct"] < cb["participation_pct"]:
            out.append("THE_WINNER_DOMINATES_THE_CONVERTIBLE_SHELF")
    return out


# --------------------------------------------------------------------------- page
def winner_sentence(face):
    w = face["winner"]
    cb = face["convertible_best"]
    if not w:
        return "没有货架同时过三道门。"
    s = ("%s %s 一年比回购多 %s 元、坏日子当天还多 %s 元、一张单占坏日子成交的 %s%%；"
         "它的坏日子摆动是这一截的 %s 倍。"
         % (w["code"], w["label"], _f(w["extra_cny_per_year"], 0), _f(w["defence_day_cny"], 0),
            _f(w["participation_pct"], 2), _f(w["tail_multiple"], 2)))
    if cb:
        s += ("对照：%s %s 一年只多 %s 元，坏日子当天亏 %s 元，摆动是那截的 %s 倍。"
              % (cb["code"], cb["label"], _f(cb["extra_cny_per_year"], 0),
                 _f(abs(cb["defence_day_cny"]), 0), _f(cb["tail_multiple"], 1)))
    return s


def render_md(face):
    h = face["headline"]
    r = face["ruler"]
    L = []
    add = L.append
    add("# 现金腿停在哪一个货架上（决策表）")
    add("")
    add("生成 %s ｜ 证据截止 %s ｜ 窗口 %s..%s（%s 年）｜ 票面现金腿 %s 元"
        % (face["generated"], face["evidence_cutoff"], face["window"]["start"],
           face["window"]["end"], _f(face["window"]["years"], 2), _f(r["ticket_cash_cny"], 0)))
    add("")
    add("判词：" + " + ".join("`%s`" % v for v in face["verdict"]))
    add("")
    add("## 一句话")
    add("")
    add(winner_sentence(face))
    add("")
    add("一年里书防守的日子有 **%d** 天（%s 天/年）。"
        % (h["defence_days"], _f(h["defence_days_per_year"], 2)))
    add("")
    add("## 三道门（机械判定，无阈值口味）")
    add("")
    add("1. **付得比回购多** —— 票面档的有效收益（零头按回购价算）高于回购 %s%%。" % _f(r["repo_net_pct"], 4))
    add("2. **在书防守的那些天不掉钱** —— 权益标尺自身 <= -1% 的那些 bar 上，货架平均收益 >= 0。")
    add("3. **一张单吃得下坏日子** —— 认领根面 p10 成交的参与带：OPEN <= 1%、THIN <= 10%、BLOCKED 以上。")
    add("")
    add("## 货架表（票面档 %s 元）" % _f(r["ticket_cash_cny"], 0))
    add("")
    add("| 代码 | 名称 | 类 | 自身净年化 % | 比回购多 (pp) | 比回购多 (元/年) | 坏日子当天 (元) "
        "| 参与率 % | 带 | 摆动/多赚 | 判定 |")
    add("|---|---|---|---|---|---|---|---|---|---|---|")
    for s in sorted(face["shelves"], key=lambda x: -x["extra_cny_per_year"]):
        add("| %s | %s | %s | %s | %s | %s | %s | %s | %s | %sx | `%s` |"
            % (s["code"], s["label"], s["class"], _f(s["own_net_cagr_pct"], 2),
               _f(s["extra_pp"], 4), _f(s["extra_cny_per_year"], 0), _f(s["defence_day_cny"], 0),
               _f(s["participation_pct"], 2), s["capacity_class"],
               _f(s["tail_multiple"], 2), s["decision"]))
    add("")
    add("## 怎么读这张表")
    add("")
    add("- **元/年 是净的**：零头按回购价躺平、换手按 2bp/边计，都已在根面里扣掉，本面不再加钱也不再折价。")
    add("- **坏日子当天** 是货架在那个 bar 上的平均收益 × 票面现金腿，不是额外罚款；它在净年化里已经被算过一次。")
    add("- **摆动/多赚** 才是本面新加的那把尺：一年坏日子的贡献（%s 天/年 × 当天的平均）除以一年比回购多赚的那一截。"
        "1 倍以下 = 坏日子本身就在替这一截付钱；几十上百倍 = 这一截是坐在一个比它大两个数量级的摆动上。"
        % _f(h["defence_days_per_year"], 2))
    add("- 摆动是**分解**，不是加减项：把它加到净年化上是重复计算。")
    add("")
    add("## 独立抽查（赢家自己那张面板）")
    add("")
    sp = face.get("spot_check") or {}
    if sp.get("status") == "ok":
        add("- 面板：%s ｜ %d bar ｜ %s..%s" % (sp["panel"], sp["bars"], sp["first"], sp["last"]))
        add("- 自建年化 **%s%%**（根面 %s%%，差 %s pp）"
            % (_f(sp["cagr_pct"], 4), _f(sp["parent_cagr_pct"], 4),
               _f(sp["delta_vs_parent_cagr_pp"], 4)))
        add("- 最差一天 %s%%、最大回撤 %s%%、年化波动 %s%%"
            % (_f(sp["worst_day_pct"], 3), _f(sp["maxdd_pct"], 2), _f(sp["vol_pct"], 2)))
        add("- |日收益| > 15%% 的 bar：%d（翻转若逃过修复会在这里出现）" % sp["n_days_beyond_15pct"])
        if sp.get("problems"):
            add("- **抽查报警**：" + "；".join(sp["problems"]))
    else:
        add("- 未做：%s" % sp.get("why", "面板不可用"))
    add("")
    add("## 诚实边界")
    add("")
    for n in face["not_measured"]:
        add("- " + n)
    add("")
    add("## 出处")
    add("")
    add("- 货架读数：`results/cb_parking_shelf_at_size.json`（r2041）sha `%s`"
        % face["data_sha"]["shelf_face"][:12])
    add("- 类别与回购对照：`results/cb_parking_bakeoff.json`（r2040）sha `%s`"
        % face["data_sha"]["bakeoff_face"][:12])
    add("- 令号：%s" % face["order_ref"])
    add("")
    return "\n".join(L) + "\n"


# --------------------------------------------------------------------------- check
def check(json_path=None, md_path=None):
    # read the module-level paths at call time: a negative control points these at a copy
    json_path, md_path = json_path or OUT_JSON, md_path or OUT_MD
    problems, stale = [], []

    for p in (SHELF_JSON, BAKEOFF_JSON, json_path, md_path):
        if not os.path.exists(p):
            stale.append("published face missing: %s" % os.path.basename(p))
    if stale:
        for s in stale:
            print("STALE:", s)
        return 3

    face = json.load(io.open(json_path, encoding="utf-8"))
    md = io.open(md_path, encoding="utf-8").read()
    shelf = json.load(io.open(SHELF_JSON, encoding="utf-8"))
    bake = json.load(io.open(BAKEOFF_JSON, encoding="utf-8"))

    # 1. parents must be the bytes this face was built from
    if face.get("data_sha", {}).get("shelf_face") != _sha(SHELF_JSON):
        stale.append("cb_parking_shelf_at_size.json changed since this face was built")
    if face.get("data_sha", {}).get("bakeoff_face") != _sha(BAKEOFF_JSON):
        stale.append("cb_parking_bakeoff.json changed since this face was built")
    if stale:
        for s in stale:
            print("STALE:", s)
        return 3

    repo = float(shelf["comparator"]["repo_net_pct"])
    if abs(repo - float(face["ruler"]["repo_net_pct"])) > 1e-9:
        problems.append("repo leg drifted from the parent: %s vs %s"
                        % (repo, face["ruler"]["repo_net_pct"]))
    tkey = str(face["ruler"]["tier_key"])
    amount = face["ruler"]["ticket_cash_cny"]
    if isinstance(amount, bool) or not isinstance(amount, (int, float)):
        print("CHECK FAILED: ticket cash is not a number (%r)" % (amount,))
        return 3
    amount = float(amount)
    years = years_between(face["window"]["start"], face["window"]["end"])

    parent_rows = {str(r["code"]): r for r in shelf["rows"]}
    num_fields = ("extra_pp", "effective_yield_pct", "defence_mean_pct", "participation_pct",
                  "extra_cny_per_year", "defence_day_cny", "defence_days_per_year",
                  "tail_multiple")
    for s in face["shelves"]:
        bad = [k for k in num_fields
               if s.get(k) is not None
               and (isinstance(s.get(k), bool) or not isinstance(s.get(k), (int, float)))]
        if bad:
            # a number written as a string must be named, not traceback (r2040's near() lesson)
            problems.append("shelf %s has non-numeric %s" % (s.get("code"), ", ".join(bad)))
            continue
        pr = parent_rows.get(s["code"])
        if pr is None:
            problems.append("shelf %s is not in the parent face" % s["code"])
            continue
        cap = pr["capacity"].get(tkey)
        if cap is None:
            problems.append("shelf %s has no parent row at tier %s" % (s["code"], tkey))
            continue
        if s["capacity_class"] != cap["class"]:
            problems.append("shelf %s capacity class drifted from the parent" % s["code"])
        if abs(s["participation_pct"] - float(cap["participation_pct_of_bad_day"])) > 1e-9:
            problems.append("shelf %s participation drifted from the parent" % s["code"])
        if abs(s["extra_pp"] - (float(cap["effective_yield_pct"]) - repo)) > 1e-3:
            problems.append("shelf %s extra is not effective-yield minus repo" % s["code"])
        if abs(s["extra_cny_per_year"] - amount * s["extra_pp"] / 100.0) > 0.6:
            problems.append("shelf %s extra in yuan does not follow from its pp" % s["code"])
        if abs(s["defence_day_cny"] - amount * s["defence_mean_pct"] / 100.0) > 0.6:
            problems.append("shelf %s defence day in yuan does not follow from its mean" % s["code"])
        want_dpy = int(pr["defence"]["days"]) / years
        if abs(s["defence_days_per_year"] - want_dpy) > 1e-6:
            problems.append("shelf %s defence-day frequency not recomputed" % s["code"])
        want_tm = tail_multiple(s["defence_mean_pct"], s["extra_pp"], s["defence_days_per_year"])
        got_tm = s["tail_multiple"]
        if (want_tm is None) != (got_tm is None):
            problems.append("shelf %s tail multiple None-ness disagrees" % s["code"])
        elif want_tm is not None and abs(want_tm - got_tm) > 1e-6:
            problems.append("shelf %s tail multiple does not recompute" % s["code"])
        want_g = gates_of(s["extra_pp"], s["defence_mean_pct"], s["capacity_class"])
        if want_g != s["gates"]:
            problems.append("shelf %s gates do not follow from its own numbers" % s["code"])
        want_d = decision_of(want_g, s["capacity_class"])
        if want_d != s["decision"]:
            problems.append("shelf %s decision %s is not what its gates say (%s)"
                            % (s["code"], s["decision"], want_d))

    # 2. winner / admissible set must follow from the rows
    adm = [s for s in face["shelves"] if s["decision"].startswith("ADMISSIBLE")]
    if [s["code"] for s in adm] != face["admissible"]:
        problems.append("admissible set does not follow from the decisions")
    w = face["winner"]
    if adm:
        want_w = max(adm, key=lambda s: s["extra_cny_per_year"])
        if not w or w["code"] != want_w["code"]:
            problems.append("winner is not the best admissible shelf")
        elif abs(w["extra_cny_per_year"] - want_w["extra_cny_per_year"]) > 1e-9:
            problems.append("winner's yuan number drifted")
    elif w is not None:
        problems.append("a winner was named while nothing is admissible")

    # 3. verdict must be reproducible
    want_v = verdict_of(face)
    if want_v != face["verdict"]:
        problems.append("verdict does not follow from the rows: %s vs %s"
                        % (want_v, face["verdict"]))

    # 4. the page must carry the tokens and the winner sentence, unswapped
    for v in face["verdict"]:
        if v not in md:
            problems.append("page missing verdict token: %s" % v)
    for word in ("坏日子", "三道门", "摆动"):
        if word not in md:
            problems.append("page missing the %s sentence" % word)
    if "%%" in md:
        # a doubled percent is the signature of a %-format string that was never formatted
        problems.append("page carries a literal %% (a format string that never ran)")
    if _f(face["ruler"]["ticket_cash_cny"], 0) not in md:
        problems.append("page does not print the ticket's cash")
    if winner_sentence(face) not in md:
        problems.append("page drops or swaps the winner sentence")

    # 4b. the independent spot check must not contradict itself
    sp = face.get("spot_check") or {}
    if sp.get("status") == "ok":
        for k in ("cagr_pct", "worst_day_pct", "maxdd_pct", "vol_pct", "parent_cagr_pct"):
            if isinstance(sp.get(k), bool) or not isinstance(sp.get(k), (int, float)):
                problems.append("spot check field %s is not a number" % k)
                break
        else:
            want = spot_problems(sp, sp["parent_cagr_pct"])
            if want:
                problems.extend(want)
            if sp.get("problems") != want:
                problems.append("spot check's own problem list does not recompute")
            if w is not None and sp.get("code") != w["code"]:
                problems.append("spot check is not of the winner")

    # 5. content hash
    want_sha = _content_sha({k: v for k, v in face.items()
                             if k not in ("content_sha256", "elapsed_sec", "generated")})
    if want_sha != face.get("content_sha256"):
        problems.append("content_sha256 mismatch")

    if problems:
        for p in problems:
            print("CHECK FAILED:", p)
        return 3
    print("CHECK OK", ARTIFACT, face["evidence_cutoff"], "|", " ".join(face["verdict"]))
    return 0


# --------------------------------------------------------------------------- selftest
def selftest():
    errs = []
    legs = [0]

    def chk(cond, msg):
        legs[0] += 1
        if not cond:
            errs.append(msg)

    # 1. window arithmetic (day counts, not "six years means 6.0")
    chk(abs(years_between("2020-07-16", "2021-07-16") - 365.0 / 365.25) < 1e-12,
        "a plain year is 365 days on the 365.25 basis")
    chk(abs(years_between("2023-07-16", "2024-07-16") - 366.0 / 365.25) < 1e-12,
        "a window spanning a leap day is 366 days")
    chk(abs(years_between("2020-07-16", "2026-07-16") - 2191.0 / 365.25) < 1e-12,
        "the six-year window really contains 2191 days")
    chk(abs(years_between("2024-01-01", "2024-01-01")) < 1e-12, "a zero window is zero years")

    # 2. tail multiple: the three shapes it must distinguish
    chk(abs(tail_multiple(-0.7689, 0.2064, 36.55) - 136.2) < 0.2,
        "a 28pp tail on a 0.2pp extra is ~136x")
    chk(abs(tail_multiple(0.0226, 0.5659, 36.55) - 1.46) < 0.01,
        "a defence mean that pays gives a small positive multiple")
    chk(tail_multiple(-0.5, 0.0, 36.55) is None, "no extra means no multiple")
    chk(abs(tail_multiple(-0.5, -0.25, 10.0) - 20.0) < 1e-9,
        "a negative extra is compared by size, not sign")

    # 3. gates: each one must be able to fail on its own
    chk(gates_of(0.1, 0.01, "OPEN") == {"pays_more_than_repo": True,
                                        "holds_on_defence_days": True,
                                        "order_fits_the_bad_day": True},
        "a shelf above repo, up on defence days, OPEN must pass every gate")
    chk(gates_of(0.0, 0.01, "OPEN")["pays_more_than_repo"] is False,
        "exactly the repo rate is not 'pays more'")
    chk(gates_of(0.1, 0.0, "OPEN")["holds_on_defence_days"] is True,
        "a flat defence day holds (>= 0)")
    chk(gates_of(0.1, -0.0001, "OPEN")["holds_on_defence_days"] is False,
        "a shelf that gives up the smallest amount on defence days fails the gate")
    chk(gates_of(0.1, 0.0, "BLOCKED")["order_fits_the_bad_day"] is False,
        "BLOCKED never fits")

    # 4. decision ladder, in order of severity
    chk(decision_of(gates_of(0.1, 0.01, "BLOCKED"), "BLOCKED") == "REJECTED_BLOCKED",
        "capacity is decided before yield")
    chk(decision_of(gates_of(-0.1, 0.01, "OPEN"), "OPEN")
        == "REJECTED_PAYS_LESS_THAN_THE_REPO", "paying less is named as such")
    chk(decision_of(gates_of(0.1, -0.01, "THIN"), "THIN")
        == "REJECTED_FALLS_ON_DEFENCE_DAYS", "falling on defence days is named as such")
    chk(decision_of(gates_of(0.1, 0.01, "OPEN"), "OPEN") == "ADMISSIBLE_CLEAN",
        "OPEN and admissible is clean")
    chk(decision_of(gates_of(0.1, 0.01, "THIN"), "THIN") == "ADMISSIBLE_THIN_TAPE",
        "THIN is admissible but named thin")

    # 5. tier selection never reaches above the ticket
    chk(pick_tier([250000.0, 565246.0, 1000000.0], 500000.0) == 250000.0,
        "a ticket below a tier must fall back to the tier under it")
    chk(pick_tier([250000.0, 565246.0], 565246.0) == 565246.0, "an exact tier is taken")
    chk(pick_tier([250000.0, 565246.0], 565245.9) == 565246.0,
        "the parent's own ticket sits ten cents under its tier and must still take it")
    chk(pick_tier([250000.0, 565246.0], 100.0) == 250000.0,
        "a ticket under every tier takes the smallest")

    # 6. formatting helpers never scale (the 2734.3% family)
    chk(_f(27.3433, 4) == "27.3433", "_f must not scale a percent")
    chk(_f(-0.665, 3) == "-0.665", "_f must keep a negative small pp intact")
    chk(_f(None) == "-", "_f must print a dash for a missing number")

    # 7. verdict rules, positive and negative (a rule that cannot fail is not a rule)
    def shelf(code, klass, extra, dmean, part, capclass, cagr=2.0):
        g = gates_of(extra, dmean, capclass)
        return {"code": code, "label": code, "class": klass, "extra_pp": extra,
                "extra_cny_per_year": part * 0 + extra * 1000.0,
                "defence_mean_pct": dmean, "defence_day_cny": dmean * 1000.0,
                "participation_pct": part, "capacity_class": capclass,
                "tail_multiple": tail_multiple(dmean, extra, 36.55),
                "tail_swing_pp_per_year": dmean * 36.55,
                "own_net_cagr_pct": cagr, "gates": g, "decision": decision_of(g, capclass)}

    def face_of(rows):
        adm = [s for s in rows if s["decision"].startswith("ADMISSIBLE")]
        f = {"shelves": rows, "admissible": [s["code"] for s in adm],
             "winner": max(adm, key=lambda s: s["extra_cny_per_year"]) if adm else None,
             "convertible_best": max([s for s in rows if s["class"] == "convertible"],
                                     key=lambda s: s["extra_pp"], default=None)}
        f["verdict"] = verdict_of(f)
        return f

    cb = shelf("CB", "convertible", 0.2064, -0.7689, 1.13, "THIN")
    bond = shelf("BD", "bond", 0.5659, 0.0226, 0.83, "OPEN")
    v = face_of([cb, bond])["verdict"]
    chk("TAIL_DWARFS_THE_EXTRA" in v, "a 136x tail on a falling defence day must be named")
    chk("DEFENCE_DAYS_PAY_FOR_MORE_THAN_THE_EXTRA" in v,
        "a winner whose defence days pay more than its extra must be named")
    chk("THE_WINNER_DOMINATES_THE_CONVERTIBLE_SHELF" in v,
        "better extra, better defence day and smaller order is dominance")
    chk("THE_CLEAN_SHELF_IS_BD" in v, "the single OPEN admissible shelf must be named")
    bond["participation_pct"] = 3.0
    v2 = face_of([cb, bond])["verdict"]
    chk("THE_WINNER_DOMINATES_THE_CONVERTIBLE_SHELF" not in v2,
        "a wider participation must break the dominance claim")
    fake_clean = dict(bond)
    fake_clean["participation_pct"] = 3.0
    cv = dict(cb)
    cv.update({"extra_pp": 0.1, "defence_mean_pct": 0.001, "capacity_class": "OPEN",
               "participation_pct": 2.0, "decision": "ADMISSIBLE_CLEAN",
               "gates": gates_of(0.1, 0.001, "OPEN")})
    chk("MORE_THAN_ONE_CLEAN_SHELF" in face_of([cv, fake_clean])["verdict"],
        "two OPEN admissible shelves must not be called a single answer")
    dead = shelf("DD", "convertible", -0.36, 0.01, 2.5, "THIN")
    chk(face_of([dead])["verdict"][0] == "NO_SHELF_PAYS_AND_HOLDS",
        "a board of shelves that all pay less must say so")
    blk = shelf("BK", "bond", 0.55, 0.02, 15.0, "BLOCKED")
    chk(face_of([blk])["verdict"][0] == "NO_SHELF_PAYS_AND_HOLDS",
        "a shelf that cannot be bought is not a shelf that pays and holds")
    thin_only = shelf("TH", "bond", 0.5, 0.02, 4.0, "THIN")
    chk("NO_SHELF_ABSORBS_THE_TICKET_CLEANLY" in face_of([thin_only])["verdict"],
        "an all-THIN board must be called thin, not clean")

    # 8. the spot-check guard must be able to fail on a degenerate panel
    clean = {"status": "ok", "cagr_pct": 2.3517, "worst_day_pct": -1.113,
             "n_days_beyond_15pct": 0}
    chk(spot_problems(clean, 2.3463) == [], "a clean rebuild must pass the spot-check guard")
    chk(any("flip" in m for m in spot_problems(dict(clean, n_days_beyond_15pct=2), 2.3463)),
        "a surviving flip must be named")
    chk(any("does not reproduce" in m for m in spot_problems(dict(clean, cagr_pct=5.0), 2.3463)),
        "a rebuild that disagrees with the parent must be named")
    chk(any("in one day" in m for m in spot_problems(dict(clean, worst_day_pct=-4.0), 2.3463)),
        "a defensive shelf losing 4% in a day must be named")
    chk(spot_problems({"status": "unavailable"}, 2.0) == [],
        "an unavailable panel must not invent a problem")

    if errs:
        for e in errs:
            print("SELFTEST FAIL:", e)
        print("SELFTEST %d/%d FAILED" % (legs[0] - len(errs), legs[0]))
        return 1
    print("SELFTEST OK %d/%d PASS" % (legs[0], legs[0]))
    return 0


# --------------------------------------------------------------------------- main
def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    cmd = argv[0] if argv else "run"
    if cmd == "run":
        return build(write=True)
    if cmd in ("--check", "check"):
        return check()
    if cmd in ("--selftest", "selftest"):
        return selftest()
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main())
