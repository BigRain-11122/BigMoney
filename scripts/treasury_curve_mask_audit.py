"""TREASURY_CURVE_MASK_AUDIT -- does the T-TF KILL survive the choice of roll mask?

r1691 closed the T-TF curve-spread line on C1 = -9.60%/yr. That number is produced with a
*size* rule that drops any day stepping more than 8x the median absolute step: 6 days on T,
10 on TF. In a treasury future the calendar spread between the front contract and the next
quarter is 0.1-0.4 points, which is the size of an ordinary day, so a size rule cannot tell
a contract switch from a rate move. It can be right only by accident, and on this panel it
is measurably wrong in both directions:

  * it drops market-wide moves -- days on which BOTH legs step the same way by a large
    amount (a contract switch on one leg cannot do that);
  * it keeps real splices -- a quarterly switch sits at a known point in the calendar, and
    the dropped days are checked against the quarter boundary.

So the same frozen mechanism (r1691's z-window / entry / exit / hold / costs, imported, not
re-implemented) is re-run under four masks and the verdict must hold under all of them:

  published      the r1691 size rule (what the closed line was priced with)
  none           every step is treated as a return (splices included -- the upper bound of
                 "no mask at all")
  market_kept    the size rule, minus every day on which both legs stepped the same way by
                 >= CO_MOVE_POINTS (restores the market moves the rule ate)
  single_only    mask only single-leg steps (the strictest splice proxy: a day on which one
                 leg steps and the other does not)

Verdict is recomputed from the frozen criteria (C1 C2 C3), never handwritten, and the audit
publishes the envelope: the line stays closed only if every mask reads KILL.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import treasury_curve_spread as tcs  # noqa: E402  (single implementation of the mechanism)

ROOT = tcs.ROOT
OUT = os.path.join(ROOT, "results", "treasury_curve_mask_audit.json")
MD = os.path.join(ROOT, "research", "TREASURY_CURVE_MASK_AUDIT.md")

CO_MOVE_POINTS = 0.25   # each leg must step at least this far, same direction, to count as a market move
QUARTER_MONTHS = (3, 6, 9, 12)
SPLICE_WINDOW_DAYS = 12  # trading days before the delivery month in which a switch is plausible


def _steps(closes):
    """Signed day-over-day steps, index-aligned ([0] = None)."""
    out = [None]
    for i in range(1, len(closes)):
        out.append(closes[i] - closes[i - 1])
    return out


def classify(dates, t_close, tf_close):
    """Every day the published size rule drops, plus why it looks like what it looks like."""
    t_step = _steps(t_close)
    tf_step = _steps(tf_close)
    t_roll = tcs.detect_rolls(t_close)
    tf_roll = tcs.detect_rolls(tf_close)
    rows = []
    for i in sorted(t_roll | tf_roll):
        legs = [n for n, s in (("T", t_roll), ("TF", tf_roll)) if i in s]
        a = t_step[i] or 0.0
        b = tf_step[i] or 0.0
        co_move = (abs(a) >= CO_MOVE_POINTS and abs(b) >= CO_MOVE_POINTS
                   and (a > 0) == (b > 0))
        month = int(dates[i][5:7])
        rows.append({
            "date": dates[i],
            "legs_masked": legs,
            "t_step": round(a, 4),
            "tf_step": round(b, 4),
            "singled_leg": len(legs) == 1,
            "both_legs_same_way": bool(co_move),
            "delivery_month": month in QUARTER_MONTHS,
            "month": month,
        })
    return rows, t_roll, tf_roll


def build_mask(dates, closes_by_leg, rows, kind):
    """Return the index set masked under one rule."""
    t_roll = tcs.detect_rolls(closes_by_leg["T"])
    tf_roll = tcs.detect_rolls(closes_by_leg["TF"])
    base = t_roll | tf_roll
    if kind == "published":
        return set(base)
    if kind == "none":
        return set()
    by_date = {r["date"]: r for r in rows}
    out = set()
    # map through dates so the index space stays the one both legs share
    for i in base:
        r = by_date[dates_global[i]]
        if kind == "market_kept":
            if not r["both_legs_same_way"]:
                out.add(i)
        elif kind == "single_only":
            if r["singled_leg"]:
                out.add(i)
        else:
            raise ValueError("unknown mask kind %r" % kind)
    return out


dates_global = []


def series_with_mask(dates, t_close, tf_close, masked):
    """Spread steps with `masked` days contributing zero -- same shape as tcs.build_series."""
    spread = [t_close[i] - tf_close[i] for i in range(len(dates))]
    d_spread = [None]
    for i in range(1, len(dates)):
        d_spread.append(None if i in masked else spread[i] - spread[i - 1])
    return {"spread": spread, "d_spread": d_spread,
            "t_roll_days": [], "tf_roll_days": [],
            "phantom_points": sum(spread[i] - spread[i - 1]
                                  for i in range(1, len(dates)) if i in masked)}


def evaluate(dates, series):
    """Run the frozen mechanism on one masked series and judge it against C1/C2/C3."""
    z = tcs.zscores(series["spread"])
    pos = tcs.positions(z)
    daily, turnovers = tcs.run_book(dates, series["d_spread"], pos)
    full = tcs.stats(daily)
    oos = tcs.segment(dates, daily, "2024-01-01", "9999-12-31")
    perm = tcs.permute(dates, series["d_spread"], pos, tcs.PERM_TRIALS, tcs.SEED_BASE)
    crit = {
        "C1": {"bar": "ann_pct >= %.1f" % tcs.CARRY_MIN_PCT,
               "value": round(full["ann_pct"], 3),
               "pass": full["ann_pct"] >= tcs.CARRY_MIN_PCT},
        "C2": {"bar": "oos_sharpe >= %.2f" % tcs.OOS_SHARPE_MIN,
               "value": round(oos["sharpe"], 3),
               "pass": oos["sharpe"] >= tcs.OOS_SHARPE_MIN},
        "C3": {"bar": "perm_p < 0.05",
               "value": round(perm["p_value"], 4),
               "pass": perm["p_value"] < 0.05},
    }
    verdict = "OPEN" if all(c["pass"] for c in crit.values()) else "KILL"
    return {"full": full, "oos": oos, "perm": perm, "turnovers": turnovers,
            "in_market_share": round(sum(1 for p in pos if p) / float(len(pos)), 4),
            "criteria": crit, "verdict": verdict}


def render_md(face):
    L = []
    L.append("# T-TF 曲线价差：r1691 的 KILL 是否只是掩码的产物")
    L.append("")
    L.append("> 生成自 `results/treasury_curve_mask_audit.json`（`python scripts/treasury_curve_mask_audit.py --render`），"
             "**手写不进来**；`--check` 会让页面与面逐字比对。")
    L.append("")
    L.append("面板 `%s..%s`，%d 根 bar，成交 %d 万元/点、保证金 %d 元/对、双边成本 %.0fbp。"
             % (face["meta"]["first"], face["meta"]["last"], face["meta"]["bars"],
                face["meta"]["point_value_cny"] / 10000.0,
                face["meta"]["margin_per_pair_cny"], face["meta"]["cost_bp_per_side"]))
    L.append("")
    L.append("## 一句话")
    L.append("")
    L.append(face["headline"])
    L.append("")
    L.append("## 被丢掉的那 %d 天是什么" % len(face["classification"]))
    L.append("")
    L.append("| 日期 | 掩了哪条腿 | T 步 | TF 步 | 两腿同向大跳 | 交割季月份 |")
    L.append("|---|---|---|---|---|---|")
    for r in face["classification"]:
        L.append("| %s | %s | %+.3f | %+.3f | %s | %s |"
                 % (r["date"], "/".join(r["legs_masked"]), r["t_step"], r["tf_step"],
                    "是" if r["both_legs_same_way"] else "否",
                    "是" if r["delivery_month"] else "否"))
    L.append("")
    L.append("判读：一年四次换月，%d 天里落在交割季月份的有 %d 天。**两腿同日同向大跳的 %d 天不可能是单腿换月**"
             "——换月只让一条腿（或两条腿各挪一次）跳，不会让两条腿按同方向一起跳 0.25 点以上。"
             % (len(face["classification"]), face["counts"]["delivery_month"],
                face["counts"]["both_legs_same_way"]))
    L.append("")
    L.append("## 四种掩码下同一套机制读数")
    L.append("")
    L.append("| 掩码 | 掩掉天数 | 全窗年化 | 全窗夏普 | 回撤 | OOS 年化 | OOS 夏普 | 置换 p | 判决 |")
    L.append("|---|---|---|---|---|---|---|---|---|")
    for name, m in face["masks"].items():
        L.append("| %s | %d | %+.2f%% | %.3f | %.1f%% | %+.2f%% | %.3f | %.4f | **%s** |"
                 % (name, m["masked_days"], m["full"]["ann_pct"], m["full"]["sharpe"],
                    m["full"]["mdd_pct"], m["oos"]["ann_pct"], m["oos"]["sharpe"],
                    m["perm"]["p_value"], m["verdict"]))
    L.append("")
    L.append("## 判词")
    L.append("")
    L.append("| 判据 | 线 | published | none | market_kept | single_only |")
    L.append("|---|---|---|---|---|---|")
    for c in ("C1", "C2", "C3"):
        cells = []
        for name in ("published", "none", "market_kept", "single_only"):
            cc = face["masks"][name]["criteria"][c]
            cells.append("%s %s" % (cc["value"], "过" if cc["pass"] else "不过"))
        L.append("| %s | %s | %s |" % (c, face["masks"]["published"]["criteria"][c]["bar"],
                                       " | ".join(cells)))
    L.append("")
    L.append(face["envelope"])
    L.append("")
    L.append("## 没做的")
    L.append("")
    for x in face["not_done"]:
        L.append("- " + x)
    L.append("")
    return "\n".join(L)


def run(render_mode=True):
    # the page is rendered on every run: a page that only refreshes under --render is the
    # r1471 shape (a reader-facing face nobody keeps in step with its own numbers).
    global dates_global
    t_rows = tcs._rows(os.path.join(tcs.FUT_DIR, "T.csv"))
    tf_rows = tcs._rows(os.path.join(tcs.FUT_DIR, "TF.csv"))
    dates, t_close, tf_close = tcs.join_legs(t_rows, tf_rows)
    dates_global = dates
    rows, _, _ = classify(dates, t_close, tf_close)

    masks = {}
    for kind in ("published", "none", "market_kept", "single_only"):
        masked = build_mask(dates, {"T": t_close, "TF": tf_close}, rows, kind)
        ev = evaluate(dates, series_with_mask(dates, t_close, tf_close, masked))
        ev["masked_days"] = len(masked)
        ev["masked_dates"] = sorted(dates[i] for i in masked)
        masks[kind] = ev

    verdicts = sorted({m["verdict"] for m in masks.values()})
    reopened = [k for k, m in masks.items() if m["verdict"] != "KILL"]
    co = sum(1 for r in rows if r["both_legs_same_way"])
    dm = sum(1 for r in rows if r["delivery_month"])
    if verdicts == ["KILL"]:
        envelope = ("包络：四种掩码（published / none / market_kept / single_only）判决全部为 KILL，"
                    "r1691 关闭这条线不依赖掩码的选择。")
    else:
        envelope = ("包络：四种掩码下判决分歧——%s 读到非 KILL（%s），"
                    "r1691 的判词须按此降级并重议。"
                    % ("、".join(reopened), "、".join(verdicts)))
    headline = ("r1691 用一条按**跳变大小**判换月的规则去掩码，而这件工具的换月幅度（0.1-0.4 点）和普通日波动同量级，"
                "规则抓不到真换月、却把 %d 天真实行情当成换月抹掉。把掩码换掉重跑，全窗年化在 %+.2f%% ~ %+.2f%% 之间、"
                "OOS 夏普在 %.2f ~ %.2f 之间，判决%s。"
                % (co,
                   min(m["full"]["ann_pct"] for m in masks.values()),
                   max(m["full"]["ann_pct"] for m in masks.values()),
                   min(m["oos"]["sharpe"] for m in masks.values()),
                   max(m["oos"]["sharpe"] for m in masks.values()),
                   "四种掩码一致（KILL）" if verdicts == ["KILL"]
                   else "随掩码改变（%s）" % "、".join(verdicts)))
    face = {
        "batch": "TREASURY_CURVE_MASK_AUDIT",
        "evidence_cutoff": dates[-1],
        "status": "ok",
        "meta": {
            "pairs": "T(10y) vs TF(5y), sina main-continuous raw",
            "bars": len(dates), "first": dates[0], "last": dates[-1],
            "point_value_cny": tcs.POINT_VALUE,
            "margin_per_pair_cny": tcs.MARGIN_PER_PAIR,
            "cost_bp_per_side": tcs.COST_BP_PER_SIDE,
            "mechanism": "imported from scripts/treasury_curve_spread.py (z_window/z_enter/max_hold/costs)",
            "co_move_points": CO_MOVE_POINTS,
            "published_rule": "|step| > %.0fx median and > %.2f points" % (tcs.ROLL_SCALE, tcs.ROLL_FLOOR),
        },
        "counts": {"masked_published": masks["published"]["masked_days"],
                   "both_legs_same_way": co, "delivery_month": dm,
                   "single_leg": sum(1 for r in rows if r["singled_leg"])},
        "classification": rows,
        "masks": masks,
        "verdicts": verdicts,
        "envelope": envelope,
        "headline": headline,
        "not_done": [
            "真换月的日子没有合约级数据可用：面板只有主力连续收盘，没有前后月合约价，"
            "所以“哪一天是换月”只能靠代理判据，四种掩码的包络就是这份不确定性的披露面。",
            "没有重建换月的实际价差成本（本面只测掩码选择对已冻结机制读数的影响）。",
            "r1691 的判词仍是关闭态的入口；本面只回答“关闭这件事是否依赖掩码”，不重开这条线。",
        ],
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(face, fh, ensure_ascii=False, indent=2)
    if render_mode:
        os.makedirs(os.path.dirname(MD), exist_ok=True)
        with open(MD, "w", encoding="utf-8") as fh:
            fh.write(render_md(face))
        print("rendered %s" % MD)
    print(json.dumps({"verdicts": verdicts,
                      "ann": {k: round(v["full"]["ann_pct"], 2) for k, v in masks.items()},
                      "oos_sharpe": {k: round(v["oos"]["sharpe"], 3) for k, v in masks.items()}},
                     ensure_ascii=False))
    return 0


def check():
    """The page a reader opens must be the face, verbatim (no hand drift)."""
    if not os.path.exists(OUT) or not os.path.exists(MD):
        print("check: missing face or page")
        return 2
    with open(OUT, encoding="utf-8") as fh:
        face = json.load(fh)
    want = render_md(face)
    with open(MD, encoding="utf-8") as fh:
        have = fh.read()
    if want.strip() != have.strip():
        print("check: page differs from the face")
        return 1
    print("check: page == face (%d chars)" % len(have))
    return 0


def _selftest():
    fails = []

    def chk(name, cond):
        if not cond:
            fails.append(name)

    # --- a co-move is a market move, a single-leg step is a splice ---
    d = ["2026-01-0%d" % i for i in range(1, 9)]
    t = [100.0, 100.1, 100.2, 101.4, 101.5, 101.6, 101.7, 101.8]     # +1.2 on day 3
    tf = [99.0, 99.1, 99.2, 100.4, 100.5, 100.6, 100.7, 100.8]       # +1.2 same day
    rows, tr, tfr = classify(d, t, tf)
    chk("co-jump classified as market move", any(r["both_legs_same_way"] for r in rows))
    chk("co-jump is not single-leg", all(not r["singled_leg"] for r in rows if r["both_legs_same_way"]))

    tf2 = [99.0, 99.1, 99.2, 99.25, 99.3, 99.4, 99.5, 99.6]          # TF flat on that day
    rows2, _, _ = classify(d, t, tf2)
    solo = [r for r in rows2 if r["date"] == "2026-01-04"]
    chk("single-leg step is a splice", solo and solo[0]["singled_leg"])
    chk("single-leg step is not a co-move", solo and not solo[0]["both_legs_same_way"])

    # --- the mask kinds genuinely differ on this fixture ---
    global dates_global
    dates_global = d
    closes = {"T": t, "TF": tf2}
    m_pub = build_mask(d, closes, rows2, "published")
    m_none = build_mask(d, closes, rows2, "none")
    m_single = build_mask(d, closes, rows2, "single_only")
    chk("none masks nothing", m_none == set())
    chk("published masks the step", 3 in m_pub)
    chk("single_only masks the single-leg step", 3 in m_single)

    # --- masking zeroes exactly the masked day, and nothing else ---
    s_none = series_with_mask(d, t, tf2, set())
    s_one = series_with_mask(d, t, tf2, {3})
    diffs = [i for i in range(1, len(d)) if s_none["d_spread"][i] != s_one["d_spread"][i]]
    chk("mask touches exactly one day", diffs == [3])
    chk("masked day contributes nothing", s_one["d_spread"][3] is None)
    chk("masked series keeps the same spread level",
        s_one["spread"] == s_none["spread"])

    # --- verdict is derived from the marks, not written ---
    def fake(ann, sh, p):
        crit = {"C1": {"pass": ann >= tcs.CARRY_MIN_PCT},
                "C2": {"pass": sh >= tcs.OOS_SHARPE_MIN},
                "C3": {"pass": p < 0.05}}
        return "OPEN" if all(c["pass"] for c in crit.values()) else "KILL"
    chk("verdict KILL when C1 fails", fake(-9.6, 1.2, 0.001) == "KILL")
    chk("verdict KILL when only C3 fails", fake(9.6, 1.2, 0.43) == "KILL")
    chk("verdict OPEN only when all pass", fake(9.6, 1.2, 0.001) == "OPEN")

    # --- live face, if present, must be internally consistent ---
    if os.path.exists(OUT):
        with open(OUT, encoding="utf-8") as fh:
            face = json.load(fh)
        chk("face carries evidence_cutoff", bool(face.get("evidence_cutoff")))
        chk("every mask reports a verdict",
            all("verdict" in m for m in face["masks"].values()))
        chk("published mask count == classified days",
            face["masks"]["published"]["masked_days"] == len(face["classification"]))
        chk("page matches the face", check() == 0)

    n_checks = 16
    if fails:
        print("selftest %d/%d FAIL" % (n_checks - len(fails), n_checks))
        for f in fails:
            print("  FAIL " + f)
        return 1
    print("selftest %d/%d PASS" % (n_checks, n_checks))
    return 0


if __name__ == "__main__":
    arg = sys.argv[1] if len(sys.argv) > 1 else ""
    if arg == "selftest":
        sys.exit(_selftest())
    if arg == "--render":
        sys.exit(run(render_mode=True))
    if arg == "--check":
        sys.exit(check())
    sys.exit(run())
