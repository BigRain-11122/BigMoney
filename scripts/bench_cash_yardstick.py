"""Does any published arm beat simply rolling cash?

Why this exists
---------------
Every published bench face is priced against a 4.0% absolute line, against
buy-and-hold on the same basket (r2151), or against itself after size
normalisation (r2152).  None of those is the thing a CNY account can actually
do with the money instead: lend it overnight on GC001 and go home.

That alternative is not hypothetical -- ``data/repo_daily/GC001.csv`` has
carried the tape since 2011-05-13 and the cash-leg carriers in this repo
(``alloc_backtest``, ``allocation_policy_scan``) already price it.  What has
never been asked is the only question it decides: **after costs, how many of
the published arms beat the repo tape, and how many of them beat it by more
than the tape's own noise?**

The arithmetic that matters here
--------------------------------
The repo quote is an *annualised percent*, and an overnight roll is paid for
the **natural** days it spans (sell Friday, cash returns Monday: three days of
interest).  So one day of cash return is ``rate/100/365 * natural_days``, with
the rate taken from the close **observed before** that stretch -- never the
rate that prints at its end.  Using ``/252`` or today's rate would quietly
inflate every arm's rival.

Read-only with respect to every input: this module never writes a bench face,
a verdict, or the cash tape.  It only adds its own result and page.

Usage
-----
  python scripts/bench_cash_yardstick.py             # write json + page
  python scripts/bench_cash_yardstick.py --check     # STALE / CHECK OK
  python scripts/bench_cash_yardstick.py --selftest  # offline behaviour legs
"""

import argparse
import csv
import datetime
import glob
import io
import json
import math
import os
import sys

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import bench_core as bc  # noqa: E402
import bench_excess_paired_test as ep  # noqa: E402

RESULTS = os.path.join(ROOT, "results")
RESEARCH = os.path.join(ROOT, "research")
CELLS = os.path.join(RESEARCH, "cells")
CASH_CSV = os.path.join(ROOT, "data", "repo_daily", "GC001.csv")
OUT_JSON = os.path.join(RESULTS, "bench_cash_yardstick.json")
OUT_MD = os.path.join(RESEARCH, "BENCH_CASH_YARDSTICK.md")

SCHEMA = "bench-cash-yardstick/v1"
T_CRIT = 1.96
NATURAL_DAYS_PER_YEAR = 365.0

BEATS = "BEATS_CASH"
BEATS_SIG = "BEATS_CASH_SIGNIFICANTLY"
LOSES = "LOSES_TO_CASH"
LOSES_SIG = "LOSES_TO_CASH_SIGNIFICANTLY"
UNDECIDABLE = "UNDECIDABLE_NO_CASH_TAPE"

NO_ARM_BEATS_CASH = "CASH_BEATS_EVERY_PUBLISHED_ARM"
SOME_ARMS_BEAT = "SOME_ARMS_BEAT_CASH"
SURVIVES_MULTIPLICITY = "AN_ARM_SURVIVES_MULTIPLICITY"
NO_SURVIVOR_MULTIPLICITY = "NO_ARM_SURVIVES_MULTIPLICITY"
H1_LINE_PP = 4.0
ONE_SIDED_ALPHA = 0.025  # t >= 1.96 two-sided == 2.5% in one direction


# --------------------------------------------------------------------------
# the cash tape
# --------------------------------------------------------------------------
def load_tape(path=None):
    """[(date, annualised percent close)] from the repo panel, in file order."""
    path = path or CASH_CSV
    out = []
    with io.open(path, encoding="utf-8", newline="") as fh:
        for row in csv.DictReader(fh):
            try:
                d = datetime.date.fromisoformat((row.get("date") or "")[:10])
                rate = float(row.get("close"))
            except (TypeError, ValueError):
                continue
            if math.isfinite(rate):
                out.append((d, rate))
    out.sort(key=lambda x: x[0])
    return out


def _as_date(x):
    """A plain date, whatever calendar object the panel hands us.

    pandas Timestamp subclasses datetime.datetime, which itself subclasses
    datetime.date -- so an isinstance(date) guard lets Timestamps through and
    the comparison against the tape's plain dates raises.
    """
    if hasattr(x, "date") and not type(x) is datetime.date:
        return x.date()
    return x


def rate_asof(tape, day):
    """Last rate printed at or before `day` (None when the tape starts later)."""
    day = _as_date(day)
    lo, hi, hit = 0, len(tape) - 1, None
    while lo <= hi:
        mid = (lo + hi) // 2
        if tape[mid][0] <= day:
            hit = tape[mid][1]
            lo = mid + 1
        else:
            hi = mid - 1
    return hit


def cash_returns(dates, tape):
    """Daily cash return on the panel calendar.

    Each step is paid for the natural days it spans, at the rate observed on
    the *previous* panel bar (causal: today's close is not known when the
    stretch begins).  The first bar accrues nothing.
    """
    out = np.zeros(len(dates), dtype=float)
    for i in range(1, len(dates)):
        prev, cur = _as_date(dates[i - 1]), _as_date(dates[i])
        rate = rate_asof(tape, prev)
        if rate is None:
            out[i] = 0.0
            continue
        days = (cur - prev).days
        if days <= 0:
            days = 1
        out[i] = rate / 100.0 / NATURAL_DAYS_PER_YEAR * days
    return out


def ann_pct(returns, dates):
    """Compound a daily return series to an annualised percent.

    Years are counted on the **calendar** between the first and last bar, not
    as ``n/252``: cash is paid for natural days, so a bar-counted year would
    compare 262 bars against 252 and quietly shave the cash rival (a flat 2.5%
    tape prices as 2.36% -- the selftest leg's first catch).
    """
    r = np.asarray(returns, dtype=float)
    r = r[np.isfinite(r)]
    if len(r) < 2 or len(dates) < 2:
        return None
    growth = float(np.prod(1.0 + r))
    years = max((_as_date(dates[-1]) - _as_date(dates[0])).days / NATURAL_DAYS_PER_YEAR, 1e-9)
    if growth <= 0:
        return None
    return round((growth ** (1.0 / years) - 1.0) * 100.0, 2)


def label_for(mean_ann_pp, t, n):
    if n < 60:
        return UNDECIDABLE
    if mean_ann_pp is None or mean_ann_pp <= 0:
        return LOSES_SIG if (t is not None and t <= -T_CRIT) else LOSES
    return BEATS_SIG if (t is not None and t >= T_CRIT) else BEATS


# --------------------------------------------------------------------------
# one face
# --------------------------------------------------------------------------
def audit_face(face, doc, cell_cfg, tol_pp, tape):
    products = (doc.get("coverage") or {}).get("products") or cell_cfg.get("products")
    if not products:
        return {"face": face, "skipped": "no products on the face"}
    panel = bc.load_futures_products(list(products))
    if len(panel) < 1:
        return {"face": face, "skipped": "no product data on disk"}
    dates, closes, rets, vols = bc.align_futures(panel)
    highs, lows = bc.align_highs_lows(panel, closes)
    if len(dates) < 60:
        return {"face": face, "skipped": "fewer than 60 bars on the panel"}
    cash = cash_returns(dates, tape)
    cash_ann = ann_pct(cash, dates)

    pub_list, pub_map = ep.published_rows(doc)
    specs = ep.arm_specs(cell_cfg)
    by_position = len(pub_list) == len(specs)

    rows, reproduced = [], 0
    for i, (label, sub) in enumerate(specs):
        arm = ep.net_series(sub, dates, closes, rets, vols, highs, lows)
        if arm is None:
            continue
        mine = bc.perf(arm.values, dates)
        p = pub_map.get(str(label))
        if p is None and by_position:
            p = pub_list[i]
        if p is None:
            continue
        gap = (None if mine["ann_pct"] is None or p["ann_pct"] is None
               else round(float(mine["ann_pct"]) - float(p["ann_pct"]), 3))
        if gap is not None and abs(gap) <= tol_pp:
            reproduced += 1
        else:
            # honesty leg: an arm that is not the published book cannot answer
            # a question about the published book.
            continue
        a = np.asarray(arm.values, dtype=float)
        st = ep.paired(a - cash)
        arm_ann = ann_pct(a, dates)
        rows.append({
            "face": face,
            "variant": str(label),
            "verdict": p["verdict"],
            "ann_pct": p["ann_pct"],
            "ann_pct_calendar": arm_ann,
            "cash_ann_pct": cash_ann,
            "excess_over_cash_pp": (None if arm_ann is None or cash_ann is None
                                    else round(float(arm_ann) - float(cash_ann), 2)),
            "paired_mean_ann_pp": st["mean_ann_pp"],
            "paired_t": st["t"],
            "n": st["n"],
            "label": label_for(st["mean_ann_pp"], st["t"], st["n"]),
        })
    return {
        "face": face,
        "evidence_cutoff": doc.get("evidence_cutoff"),
        "cash_ann_pct": cash_ann,
        "window": [_as_date(dates[0]).isoformat(), _as_date(dates[-1]).isoformat()],
        "n_bars": len(dates),
        "n_arm_specs": len(specs),
        "n_rows": len(rows),
        "n_reproduced": reproduced,
        "rows": rows,
    }


# --------------------------------------------------------------------------
# the whole book
# --------------------------------------------------------------------------
def build(tape=None, tol_pp=0.05):
    tape = tape if tape is not None else load_tape()
    faces, skipped = [], []
    for path in sorted(glob.glob(os.path.join(RESULTS, "bench_*.json"))):
        base = os.path.basename(path)
        if base == os.path.basename(OUT_JSON):
            continue
        face = base[6:-5] if base.startswith("bench_") else base[:-5]
        cell_path = os.path.join(CELLS, face + ".json")
        if not os.path.isfile(cell_path):
            skipped.append({"face": face, "why": "no research/cells config -- arms not reconstructible"})
            continue
        with io.open(cell_path, encoding="utf-8") as f:
            cell_cfg = json.load(f)
        with io.open(path, encoding="utf-8") as f:
            doc = json.load(f)
        try:
            got = audit_face(face, doc, cell_cfg, tol_pp, tape)
        except Exception as exc:  # a face that cannot be repriced is a skipped face
            got = {"face": face, "skipped": "%s: %s" % (type(exc).__name__, exc)}
        if "skipped" in got:
            skipped.append({"face": face, "why": got["skipped"]})
        else:
            faces.append(got)

    rows = [r for f in faces for r in f["rows"]]
    beats = [r for r in rows if r["label"] in (BEATS, BEATS_SIG)]
    beats_sig = [r for r in rows if r["label"] == BEATS_SIG]
    loses_sig = [r for r in rows if r["label"] == LOSES_SIG]
    best = max(rows, key=lambda r: (r["paired_mean_ann_pp"]
                                    if r["paired_mean_ann_pp"] is not None else -1e9),
               default=None)
    cuts = [f["evidence_cutoff"] for f in faces if f.get("evidence_cutoff")]
    cash_anns = [f["cash_ann_pct"] for f in faces if f["cash_ann_pct"] is not None]
    expected_fp = round(len(rows) * ONE_SIDED_ALPHA, 1)
    return {
        "schema": SCHEMA,
        "generated": datetime.datetime.now().astimezone().isoformat(timespec="seconds"),
        "evidence_cutoff": max(cuts) if cuts else None,
        "cutoff_rule": "max of the audited faces' own evidence_cutoff fields",
        "cash_face": {
            "instrument": "GC001 rolled overnight, natural-day accrual",
            "tape": os.path.relpath(CASH_CSV, ROOT).replace("\\", "/"),
            "first_bar": tape[0][0].isoformat() if tape else None,
            "last_bar": tape[-1][0].isoformat() if tape else None,
            "rate_convention": "annualised percent close, /365 per natural day, prior-bar rate (causal)",
        },
        "tolerance_pp": tol_pp,
        "decision_rule": ("an arm beats cash only when the paired daily difference "
                          "(arm - cash) has positive annualised mean AND t >= 1.96"),
        "headline": {
            "n_faces": len(faces),
            "n_arms": len(rows),
            "n_beats_cash": len(beats),
            "n_beats_cash_significant": len(beats_sig),
            "n_loses_cash_significant": len(loses_sig),
            "best_arm": (None if best is None else {
                "face": best["face"], "variant": best["variant"],
                "excess_over_cash_pp": best["excess_over_cash_pp"],
                "paired_mean_ann_pp": best["paired_mean_ann_pp"],
                "paired_t": best["paired_t"]}),
            "cash_ann_pct_range": [min(cash_anns) if cash_anns else None,
                                   max(cash_anns) if cash_anns else None],
            "n_point_beat_but_not_significant": len(beats) - len(beats_sig),
            "n_trials": len(rows),
            "expected_false_positives_one_sided": expected_fp,
            "h1_line_pp": H1_LINE_PP,
            "h1_line_above_cash_pp": ([round(H1_LINE_PP - max(cash_anns), 2),
                                       round(H1_LINE_PP - min(cash_anns), 2)]
                                      if cash_anns else None),
        },
        "decision": NO_ARM_BEATS_CASH if not beats_sig else SOME_ARMS_BEAT,
        "decision_after_multiplicity": (
            NO_SURVIVOR_MULTIPLICITY
            if len(beats_sig) <= expected_fp else SURVIVES_MULTIPLICITY),
        "multiplicity_rule": ("with N arms tested at 2.5% one-sided, ~N*0.025 spurious "
                              "positives are expected; a count at or below that is not "
                              "evidence of a cash-beating arm"),
        "faces": faces,
        "skipped": skipped,
    }


# --------------------------------------------------------------------------
# page
# --------------------------------------------------------------------------
def render_md(doc):
    h = doc["headline"]
    L = []
    L.append("# 每一个已发布臂，打得过「什么都不做、借钱出去」吗？")
    L.append("")
    L.append("生成时间 %s ｜ 证据截止 %s ｜ 现金腿=%s（%s → %s）"
             % (doc["generated"], doc["evidence_cutoff"], doc["cash_face"]["instrument"],
                doc["cash_face"]["first_bar"], doc["cash_face"]["last_bar"]))
    L.append("")
    L.append("## 一句话")
    L.append("")
    L.append("口径：现金每日收益 = 前一交易日 GC001 收盘年化利率 / 100 / 365 × 跨过的自然日数"
             "（周五借出、周一收回付三天利息）；臂与现金逐日配对，"
             "判据 = 配对差值年化为正且 t ≥ 1.96。")
    L.append("")
    L.append("读数：**%d 张面 / %d 条臂里，跑赢现金 %d 条，其中显著 %d 条；显著跑输 %d 条**。"
             % (h["n_faces"], h["n_arms"], h["n_beats_cash"],
                h["n_beats_cash_significant"], h["n_loses_cash_significant"]))
    L.append("")
    if h.get("best_arm"):
        b = h["best_arm"]
        L.append("最好的一条：`%s`（%s）超额 %s pp/年（配对 t=%s）。"
                 % (b["variant"], b["face"], b["paired_mean_ann_pp"], b["paired_t"]))
        L.append("")
    L.append("单臂口径：**%s**" % doc["decision"])
    L.append("")
    L.append("但一个数就够翻掉上面这句：**%d 条臂同时接受检验，按 2.5%% 单边期待约 %s 条"
             "「显著」纯属噪声**——本面测到 %d 条显著跑赢。"
             "所以乘上多重比较后本面判词是 **%s**：这张面上没有任何一条臂能被证明打得过借钱出去。"
             % (h["n_trials"], h["expected_false_positives_one_sided"],
                h["n_beats_cash_significant"], doc["decision_after_multiplicity"]))
    L.append("")
    if h.get("h1_line_above_cash_pp"):
        L.append("顺带一个对比：各面窗口里「什么都不做」的现金腿年化 %s%%~%s%%，"
                 "所以 4.0%% 那条绝对线里只有 %s~%s pp 是在买策略，其余是在买资金利率本身。"
                 % (h["cash_ann_pct_range"][0], h["cash_ann_pct_range"][1],
                    h["h1_line_above_cash_pp"][0], h["h1_line_above_cash_pp"][1]))
        L.append("")
    L.append("## 逐面读数")
    L.append("")
    L.append("| 面 | 窗口 | 现金年化% | 臂数 | 跑赢现金 | 显著跑赢 | 显著跑输 |")
    L.append("|---|---|---|---|---|---|---|")
    for f in doc["faces"]:
        rb = sum(1 for r in f["rows"] if r["label"] in (BEATS, BEATS_SIG))
        rs = sum(1 for r in f["rows"] if r["label"] == BEATS_SIG)
        rl = sum(1 for r in f["rows"] if r["label"] == LOSES_SIG)
        L.append("| %s | %s → %s | %s | %d | %d | %d | %d |"
                 % (f["face"], f["window"][0], f["window"][1], f["cash_ann_pct"],
                    f["n_rows"], rb, rs, rl))
    L.append("")
    L.append("## 这张面不回答什么")
    L.append("")
    L.append("① 它不重发任何 verdict——臂的判词仍是各自面上那个数，本面只改问「对手是谁」。")
    L.append("② 现金腿只有 GC001 一个期限，且按收盘价计息；真实零售能拿到的量受券源与券商限制。")
    L.append("③ 未建模分红再投、税费与申购赎回摩擦，臂侧成本仍是各面自己声明的单边 bp。")
    L.append("")
    L.append("复现：`python scripts\\bench_cash_yardstick.py`（`--check` 对盘面重算比对，`--selftest` 离线行为腿）")
    return "\n".join(L) + "\n"


# --------------------------------------------------------------------------
# check / selftest
# --------------------------------------------------------------------------
def _numbers(doc):
    """The part of the face that must be a function of its inputs."""
    return json.dumps({k: v for k, v in doc.items() if k != "generated"},
                      ensure_ascii=False, sort_keys=True)


def check():
    if not os.path.isfile(OUT_JSON):
        print("STALE: face missing (%s)" % os.path.relpath(OUT_JSON, ROOT))
        return 3
    with io.open(OUT_JSON, encoding="utf-8") as f:
        on_disk = json.load(f)
    fresh = build()
    if _numbers(on_disk) != _numbers(fresh):
        print("STALE: bench_cash_yardstick re-derive disagrees with the face on disk")
        return 3
    print("CHECK OK: %d faces / %d arms re-derived from the cash tape"
          % (fresh["headline"]["n_faces"], fresh["headline"]["n_arms"]))
    return 0


def selftest():
    fails = []

    def ok(name, cond, why=""):
        if not cond:
            fails.append("%s%s" % (name, (" | " + why) if why else ""))

    # 1. the /365 natural-day convention reproduces the quoted annualised rate:
    #    a flat 2.5% tape over one calendar year of weekdays must compound to
    #    ~2.5%, not to 2.5% * 252/365 and not to 2.5% * 252/252.
    d0 = datetime.date(2024, 1, 1)
    days = [d0 + datetime.timedelta(days=i) for i in range(366)
            if (d0 + datetime.timedelta(days=i)).weekday() < 5]
    tape = [(d0 - datetime.timedelta(days=1), 2.5)]
    cash = cash_returns(days, tape)
    got = ann_pct(cash, days)
    ok("annualised cash reproduces the quoted rate", got is not None and abs(got - 2.5) < 0.06,
       "got %r want ~2.5" % got)

    # 2. a Friday-to-Monday step is paid for three days, not one
    fri = datetime.date(2024, 1, 5)
    mon = datetime.date(2024, 1, 8)
    c2 = cash_returns([fri, mon], [(fri, 3.65)])
    ok("weekend accrual spans natural days", abs(c2[1] - 3.65 / 100 / 365 * 3) < 1e-12,
       "got %r" % c2[1])

    # 3. a gap with no fresh quote keeps the last one (ffill), and a rate that
    #    only prints later is never used earlier -- the lookahead leg.
    a, b, c = datetime.date(2024, 2, 1), datetime.date(2024, 2, 2), datetime.date(2024, 2, 5)
    tape3 = [(a, 2.0)]
    c3 = cash_returns([a, b, c], tape3)
    ok("ffill keeps the prior rate", abs(c3[1] - 2.0 / 100 / 365 * 1) < 1e-12, "got %r" % c3[1])
    tape4 = [(a, 2.0), (c, 9.0)]
    c4 = cash_returns([a, b, c], tape4)
    ok("a later rate never leaks backwards", abs(c4[2] - 2.0 / 100 / 365 * 3) < 1e-12,
       "got %r" % c4[2])

    # 4. paired(): the same book twice has no variation, so no t -- not t=0
    st = ep.paired(np.zeros(300))
    ok("identical series give t=None", st["t"] is None, repr(st))

    # 5. labels follow the rule, not the sign alone
    ok("big positive t clears", label_for(3.0, 2.5, 500) == BEATS_SIG)
    ok("big positive mean without t does not clear", label_for(3.0, 0.5, 500) == BEATS)
    ok("big negative t is called out", label_for(-4.0, -2.7, 500) == LOSES_SIG)
    ok("short windows are undecidable", label_for(9.0, 9.0, 30) == UNDECIDABLE)

    # 6. a tape that starts after the panel cannot invent returns
    late = [(datetime.date(2024, 6, 1), 2.0)]
    c6 = cash_returns([datetime.date(2024, 1, 2), datetime.date(2024, 1, 3)], late)
    ok("no tape means no cash return", c6[1] == 0.0, repr(c6[1]))

    if fails:
        print("SELFTEST FAILED (%d):" % len(fails))
        for f in fails:
            print("  -", f)
        return 1
    print("selftest 6/6 OK: cash convention, weekend accrual, ffill/lookahead, "
          "no-variation t, labels, missing tape")
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()
    if args.selftest:
        return selftest()
    if args.check:
        return check()
    doc = build()
    os.makedirs(RESULTS, exist_ok=True)
    os.makedirs(RESEARCH, exist_ok=True)
    with io.open(OUT_JSON, "w", encoding="utf-8", newline="\n") as f:
        json.dump(doc, f, ensure_ascii=False, indent=1, sort_keys=True)
    with io.open(OUT_MD, "w", encoding="utf-8", newline="\n") as f:
        f.write(render_md(doc))
    h = doc["headline"]
    print("faces=%d arms=%d beats_cash=%d beats_sig=%d loses_sig=%d decision=%s"
          % (h["n_faces"], h["n_arms"], h["n_beats_cash"],
             h["n_beats_cash_significant"], h["n_loses_cash_significant"], doc["decision"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
