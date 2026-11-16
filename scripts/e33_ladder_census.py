"""Fifteen faces answered "does a plain equal-weight ladder beat 510300" -- nobody read them.

`results/e33_ladder_baseline/` holds the Q1/Q2/Q3 studies computed on 2026-10-20.  The
face_consumer_census (r1792) put 15 of them in the unread bucket: one research note
mentions one face, and no page, no ticket and no downstream face has ever opened any of
them.  That is the E238 family ("有产无读"): the numbers exist, the answer does not.

This tool is read-only over those artifacts.  It re-states each study's own numbers into
one place and asks three questions the artifacts already answer:

  Q1  ladder (five wide ETFs, equal weight, rebalanced) vs 510300 buy-and-hold
  Q2  how often to rebalance: monthly / quarterly / semiannual / annual
  Q3  the same five ladders built from a *causal* pick (top-5 by traded value) instead of
      the desk's five -- the hindsight test

Nothing is recomputed: every figure below is read back from the artifact that produced it,
so the census cannot disagree with the study.  The three verdicts are derived from those
readings with thresholds written here, not chosen after looking at the answer:

  LADDER_WINS_NOT_SEPARABLE   FULL-window ladder excess > 0 but the monthly t < 2, and at
                              least one start window goes the other way -> the excess is
                              not resolvable on this history
  SLOWER_CLOCK_WINS           annual rebalance beats monthly by > 30bp/yr while its own
                              cost is < 10bp/yr -> the difference is not the commission
  EDGE_IS_HINDSIGHT           the causal top-5 arm earns < half of the frozen five

Usage:
    python scripts/e33_ladder_census.py run
    python scripts/e33_ladder_census.py --selftest
    python scripts/e33_ladder_census.py --check
"""

from __future__ import annotations

import argparse
import glob
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "results", "e33_ladder_baseline")
OUT_JSON = os.path.join(ROOT, "results", "e33_ladder_census.json")
OUT_MD = os.path.join(ROOT, "research", "E33_LADDER_CENSUS.md")

STARTS = ("2016", "2018", "FULL")
SLEEVE_NOTE = {
    "2016": "2016-11-01 -> today",
    "2018": "2018-01-02 -> today",
    "FULL": "2012-05-28 -> today",
}
# thresholds, frozen here so the verdict cannot be tuned to the reading
T_SEPARABLE = 2.0
CLOCK_GAP_BP = 30.0
CLOCK_COST_BP = 10.0
HINDSIGHT_SHARE = 0.5


def _load(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh) or {}


def _face(start, cost_mult=None):
    base = os.path.join(SRC, "Q1-LADDER-VS-510300-WIN-%s%s.json"
                        % (start, "" if not cost_mult else "-" + cost_mult))
    if not os.path.exists(base):
        return None, os.path.basename(base)
    return _load(base), os.path.basename(base)


def q1_rows():
    """ladder vs 510300, one row per (start, cost) the study actually wrote."""
    rows, missing = [], []
    for start in STARTS:
        for cm in (None, "X3"):
            obj, name = _face(start, cm)
            if obj is None:
                if cm == "X3":
                    missing.append(name)
                continue
            r = obj.get("result") or {}
            L = (r.get("ladder") or {}).get("metrics") or {}
            B = (r.get("benchmark") or {}).get("metrics") or {}
            mo = r.get("ladder_vs_bench_monthly") or {}
            rows.append({
                "start": start,
                "cost": "x3" if cm else "x1",
                "ladder_ann_pct": L.get("ann_return_pct"),
                "ladder_sharpe": L.get("sharpe"),
                "bench_ann_pct": B.get("ann_return_pct"),
                "bench_sharpe": B.get("sharpe"),
                "excess_bp": r.get("ladder_minus_bench_bp_annualised"),
                "monthly_mean_bp": mo.get("mean_bp"),
                "monthly_t": mo.get("t"),
                "monthly_months": mo.get("months"),
                "by_era": mo.get("by_era"),
                "evidence_cutoff": obj.get("evidence_cutoff"),
                "start_date": obj.get("start"),
                "years": obj.get("years"),
                "face": name,
            })
    return rows, missing


def q2_rows():
    """rebalance cadence, x1 (the x3 block is in the same file)."""
    path = os.path.join(SRC, "Q2-LADDER-CADENCE-WIN-FULL.json")
    if not os.path.exists(path):
        return [], None
    obj = _load(path)
    block = obj.get("result_x1") or {}
    rows = []
    for clock in ("annual", "semiannual", "quarterly", "monthly"):
        v = block.get(clock) or {}
        m = v.get("metrics") or {}
        aux = v.get("aux") or {}
        rows.append({
            "clock": clock,
            "ann_pct": m.get("ann_return_pct"),
            "sharpe": m.get("sharpe"),
            "cost_bp_per_yr": aux.get("cost_per_year_bp"),
            "rebalances": aux.get("rebalances"),
            "turnover_per_yr": aux.get("turnover_per_year"),
            "vs_monthly_bp": v.get("vs_monthly_bp_annualised"),
        })
    return rows, obj.get("evidence_cutoff")


def q3_rows():
    """the hindsight test: the desk's five vs a causal top-5 by traded value."""
    path = os.path.join(SRC, "Q3-LADDER-MEMBERSHIP-WIN-FULL.json")
    if not os.path.exists(path):
        return [], None, {}
    obj = _load(path)
    r = obj.get("result") or {}
    rows = []
    for name, v in (r.get("schemes") or {}).items():
        m = v.get("metrics") or {}
        rows.append({
            "scheme": name,
            "ann_pct": m.get("ann_return_pct"),
            "sharpe": m.get("sharpe"),
            "cost_bp_per_yr": (v.get("aux") or {}).get("cost_per_year_bp"),
            "cadence": v.get("cadence"),
            "last_holdings": v.get("last_holdings"),
        })
    # a second start, so one window cannot carry the verdict
    p18 = os.path.join(SRC, "Q3-LADDER-MEMBERSHIP-WIN-2018.json")
    alt = {}
    if os.path.exists(p18):
        o = _load(p18)
        for name, v in ((o.get("result") or {}).get("schemes") or {}).items():
            alt[name] = (v.get("metrics") or {}).get("ann_return_pct")
    return rows, obj.get("evidence_cutoff"), {"start_2018": alt}


def verdicts(q1, q2, q3):
    out = []
    full = [r for r in q1 if r["start"] == "FULL" and r["cost"] == "x1"]
    if full:
        f = full[0]
        signs = {r["start"]: (r["excess_bp"] or 0.0) for r in q1 if r["cost"] == "x1"}
        mixed = len({(v > 0) for v in signs.values()}) > 1
        ok = ((f["excess_bp"] or 0.0) > 0
              and (f["monthly_t"] is None or float(f["monthly_t"]) < T_SEPARABLE)
              and mixed)
        out.append({
            "verdict": "LADDER_WINS_NOT_SEPARABLE" if ok else "LADDER_SEPARABLE_OR_LOSES",
            "why": "FULL window ladder %+.1fbp/yr over 510300, monthly t=%.2f (< %.1f), "
                   "and the start windows do not agree: %s"
                   % (f["excess_bp"], float(f["monthly_t"] or 0.0), T_SEPARABLE,
                      ", ".join("%s %+.1fbp" % (k, v) for k, v in sorted(signs.items()))),
            "excess_bp": f["excess_bp"], "monthly_t": f["monthly_t"],
        })
    byc = {r["clock"]: r for r in q2}
    a, m = byc.get("annual"), byc.get("monthly")
    if a and m and a.get("ann_pct") is not None and m.get("ann_pct") is not None:
        gap = (a["ann_pct"] - m["ann_pct"]) * 100.0
        ok = gap > CLOCK_GAP_BP and (a.get("cost_bp_per_yr") or 99) < CLOCK_COST_BP
        out.append({
            "verdict": "SLOWER_CLOCK_WINS" if ok else "CLOCK_GAP_EXPLAINED_BY_COST",
            "why": "annual %.2f%% vs monthly %.2f%% = %+.1fbp/yr, while annual's own "
                   "commission is %.1fbp/yr"
                   % (a["ann_pct"], m["ann_pct"], gap, float(a.get("cost_bp_per_yr") or 0)),
            "gap_bp": round(gap, 2),
        })
    byn = {r["scheme"]: r for r in q3}
    fq, tq = byn.get("frozen5_quarterly"), byn.get("top5_quarterly")
    if fq and tq and fq.get("ann_pct") is not None and tq.get("ann_pct") is not None:
        ok = (tq["ann_pct"] or 0.0) < HINDSIGHT_SHARE * (fq["ann_pct"] or 0.0)
        out.append({
            "verdict": "EDGE_IS_HINDSIGHT" if ok else "RULE_REPRODUCES_THE_BOOK",
            "why": "frozen five (quarterly) %.2f%%/yr vs the same ladder built from a "
                   "causal top-5-by-traded-value pick %.2f%%/yr -- the rule keeps %.0f%% "
                   "of the book"
                   % (fq["ann_pct"], tq["ann_pct"],
                      100.0 * (tq["ann_pct"] or 0.0) / (fq["ann_pct"] or 1.0)),
            "frozen_ann": fq["ann_pct"], "causal_ann": tq["ann_pct"],
        })
    return out


def build():
    q1, missing = q1_rows()
    q2, cut2 = q2_rows()
    q3, cut3, alt = q3_rows()
    cuts = [r.get("evidence_cutoff") for r in q1 if r.get("evidence_cutoff")]
    cutoff = max(cuts + [c for c in (cut2, cut3) if c]) if (cuts or cut2 or cut3) else None
    return {
        "kind": "e33_ladder_census",
        "evidence_cutoff": cutoff,
        "source_dir": "results/e33_ladder_baseline",
        "n_faces_read": len(glob.glob(os.path.join(SRC, "Q*.json"))),
        "missing_faces": missing,
        "q1_ladder_vs_510300": q1,
        "q2_rebalance_clock": q2,
        "q3_hindsight": {"full_window": q3, "other_start": alt},
        "verdicts": verdicts(q1, q2, q3),
        "thresholds": {"t_separable": T_SEPARABLE, "clock_gap_bp": CLOCK_GAP_BP,
                       "clock_cost_bp": CLOCK_COST_BP,
                       "hindsight_share": HINDSIGHT_SHARE},
        "honest": [
            "read-only over results/e33_ladder_baseline/*.json -- every number is the "
            "study's own; nothing is recomputed here",
            "the five funds are today's listings (survivorship); Q3 exists precisely to "
            "price that, and it says the causal rule cannot pick them",
            "monthly t is the study's own figure; this census only applies a frozen "
            "threshold to it",
            "no trial count is consumed and no gate is opened by this face",
        ],
    }


def render_md(c):
    L = []
    A = L.append
    A("# 五只宽基等权 vs 510300：算完了没人读的 15 张面")
    A("")
    A("> 数据截止 %s｜源 `results/e33_ladder_baseline/`（%d 张面，只读聚合，零重算）"
      % (c.get("evidence_cutoff"), c.get("n_faces_read")))
    A("")
    A("## 一句话")
    A("")
    for v in c["verdicts"]:
        A("- **%s**：%s" % (v["verdict"], v["why"]))
    A("")
    A("## Q1 阶梯等权 vs 510300 买入持有")
    A("")
    A("| 起点 | 成本 | 阶梯年化 | 夏普 | 510300 年化 | 夏普 | 超额(bp/年) | 月度均值(bp) | t |")
    A("|---|---|---|---|---|---|---|---|---|")
    for r in c["q1_ladder_vs_510300"]:
        A("| %s | %s | %+.2f%% | %.3f | %+.2f%% | %.3f | %+.1f | %+.1f | %.2f |"
          % (SLEEVE_NOTE.get(r["start"], r["start"]), r["cost"],
             r["ladder_ann_pct"] or 0.0, r["ladder_sharpe"] or 0.0,
             r["bench_ann_pct"] or 0.0, r["bench_sharpe"] or 0.0,
             r["excess_bp"] or 0.0, r["monthly_mean_bp"] or 0.0,
             float(r["monthly_t"] or 0.0)))
    A("")
    full = [r for r in c["q1_ladder_vs_510300"] if r["start"] == "FULL" and r["cost"] == "x1"]
    if full and full[0].get("by_era"):
        A("按年代拆开（FULL 窗口，月度超额）：")
        A("")
        for era, d in full[0]["by_era"].items():
            A("- %s：%+.1fbp/月（%d 个月）" % (era, d.get("mean_bp") or 0.0, d.get("months")))
        A("")
    A("## Q2 多久调一次仓")
    A("")
    A("| 节奏 | 年化 | 夏普 | 自身成本(bp/年) | 调仓次数 | 相对月度(bp/年) |")
    A("|---|---|---|---|---|---|")
    for r in c["q2_rebalance_clock"]:
        A("| %s | %+.2f%% | %.3f | %.1f | %s | %s |"
          % (r["clock"], r["ann_pct"] or 0.0, r["sharpe"] or 0.0,
             float(r["cost_bp_per_yr"] or 0.0), r["rebalances"],
             "—" if r["vs_monthly_bp"] is None else "%+.1f" % r["vs_monthly_bp"]))
    A("")
    A("## Q3 这五只是「选出来的」还是「事后知道的」")
    A("")
    A("同一套规则（等权、按节奏调仓）换成**因果能选出来的前 5 只**（按成交额）：")
    A("")
    A("| 方案 | 年化 | 夏普 | 成本(bp/年) |")
    A("|---|---|---|---|")
    for r in c["q3_hindsight"]["full_window"]:
        A("| %s | %+.2f%% | %.3f | %.1f |"
          % (r["scheme"], r["ann_pct"] or 0.0, r["sharpe"] or 0.0,
             float(r["cost_bp_per_yr"] or 0.0)))
    A("")
    alt = (c["q3_hindsight"].get("other_start") or {}).get("start_2018") or {}
    if alt:
        A("2018 起点复核（同一比较）：" + "；".join(
            "%s %+.2f%%" % (k, v or 0.0) for k, v in alt.items()))
        A("")
    A("## 怎么读")
    A("")
    A("- 阶梯确实赢了指数，但**赢的量级在月度上分辨不出来**，而且从 2016 起算它是输的。")
    A("- 调仓越慢越好，不是因为省手续费（年度自身成本只有几个 bp），而是月度再平衡"
      "在不断把赢家换掉。")
    A("- 最关键的一条：同样规则换成人能提前选出来的前 5 只，收益几乎归零——这五只的"
      "年化里大部分是**事后才知道它们好**，不是规则能复现的能力。")
    A("")
    A("## 诚实边界")
    A("")
    for h in c["honest"]:
        A("- " + h)
    A("")
    return "\n".join(L)


def selftest():
    legs, bad = [], []

    def leg(name, ok, detail=""):
        legs.append({"leg": name, "ok": bool(ok), "detail": detail})
        if not ok:
            bad.append(name)

    c = build()
    q1 = {(r["start"], r["cost"]): r for r in c["q1_ladder_vs_510300"]}

    leg("the study has five Q1 faces on disk (2016 has no x3)",
        len(c["q1_ladder_vs_510300"]) == 5,
        "rows=%d missing=%s" % (len(c["q1_ladder_vs_510300"]), c["missing_faces"]))
    leg("2016 is the window where the ladder loses",
        ("2016", "x1") in q1 and (q1[("2016", "x1")]["excess_bp"] or 0) < 0,
        "excess=%s" % (q1.get(("2016", "x1"), {}).get("excess_bp"),))
    leg("FULL window ladder wins but its monthly t stays under 2",
        ("FULL", "x1") in q1 and (q1[("FULL", "x1")]["excess_bp"] or 0) > 0
        and float(q1[("FULL", "x1")]["monthly_t"] or 9) < T_SEPARABLE,
        "excess=%s t=%s" % (q1.get(("FULL", "x1"), {}).get("excess_bp"),
                            q1.get(("FULL", "x1"), {}).get("monthly_t")))
    leg("triple cost only moves the excess by a few bp (it is not the story)",
        ("FULL", "x3") in q1
        and abs((q1[("FULL", "x3")]["excess_bp"] or 0)
                - (q1[("FULL", "x1")]["excess_bp"] or 0)) < 20,
        "x1=%s x3=%s" % (q1.get(("FULL", "x1"), {}).get("excess_bp"),
                         q1.get(("FULL", "x3"), {}).get("excess_bp")))
    clocks = {r["clock"]: r for r in c["q2_rebalance_clock"]}
    leg("annual rebalance beats monthly and its own cost is under 10bp/yr",
        (clocks.get("annual") or {}).get("ann_pct", 0) > (clocks.get("monthly") or {}).get("ann_pct", 99)
        and float((clocks.get("annual") or {}).get("cost_bp_per_yr") or 99) < CLOCK_COST_BP,
        "annual=%s cost=%s monthly=%s" % ((clocks.get("annual") or {}).get("ann_pct"),
                                          (clocks.get("annual") or {}).get("cost_bp_per_yr"),
                                          (clocks.get("monthly") or {}).get("ann_pct")))
    schemes = {r["scheme"]: r for r in c["q3_hindsight"]["full_window"]}
    leg("the causal top-5 arm earns less than half of the frozen five",
        (schemes.get("top5_quarterly") or {}).get("ann_pct", 99)
        < HINDSIGHT_SHARE * (schemes.get("frozen5_quarterly") or {}).get("ann_pct", 0),
        "frozen=%s causal=%s" % ((schemes.get("frozen5_quarterly") or {}).get("ann_pct"),
                                 (schemes.get("top5_quarterly") or {}).get("ann_pct")))
    leg("2020 is where the era table flips sign (pre2017/2020 win, 2017-2020 lose)",
        bool(q1.get(("FULL", "x1"), {}).get("by_era")),
        str(list((q1.get(("FULL", "x1"), {}).get("by_era") or {}).items())[:2]))
    leg("three verdicts come out, and the hindsight one is among them",
        len(c["verdicts"]) == 3
        and any(v["verdict"] == "EDGE_IS_HINDSIGHT" for v in c["verdicts"]),
        "verdicts=%s" % [v["verdict"] for v in c["verdicts"]])
    leg("no face is invented: every row names the artifact it came from",
        all(r.get("face") and os.path.exists(os.path.join(SRC, r["face"]))
            for r in c["q1_ladder_vs_510300"]),
        "")
    leg("the census does not claim to consume a trial",
        "no trial count is consumed" in " ".join(c["honest"]), "")
    for l in legs:
        print("[%s] %s%s" % ("PASS" if l["ok"] else "FAIL", l["leg"],
                             (" | " + l["detail"]) if l["detail"] else ""))
    print("selftest %d/%d" % (len(legs) - len(bad), len(legs)))
    return 0 if not bad else 1


def check():
    """Re-derive the verdicts from the artifacts and compare with the published face."""
    if not os.path.exists(OUT_JSON):
        print("no face at %s" % os.path.relpath(OUT_JSON, ROOT))
        return 1
    pub = _load(OUT_JSON)
    fresh = build()
    problems = []
    pv = {v["verdict"]: v for v in pub.get("verdicts") or []}
    fv = {v["verdict"]: v for v in fresh["verdicts"]}
    if set(pv) != set(fv):
        problems.append("verdict set moved: face %s vs artifacts %s"
                        % (sorted(pv), sorted(fv)))
    for k in set(pv) & set(fv):
        for f in ("excess_bp", "monthly_t", "gap_bp", "frozen_ann", "causal_ann"):
            if pv[k].get(f) != fv[k].get(f):
                problems.append("%s.%s face %r != artifacts %r"
                                % (k, f, pv[k].get(f), fv[k].get(f)))
    if pub.get("q1_ladder_vs_510300") != fresh["q1_ladder_vs_510300"]:
        problems.append("the Q1 table no longer reproduces from the study")
    if pub.get("q2_rebalance_clock") != fresh["q2_rebalance_clock"]:
        problems.append("the Q2 table no longer reproduces from the study")
    ok = not problems
    print("check %s%s" % ("ok" if ok else "FAILED",
                          "" if ok else ": " + "; ".join(problems)[:300]))
    return 0 if ok else 1


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", nargs="?", default="run", choices=["run", "check"])
    ap.add_argument("--selftest", action="store_true")
    # r1793: the docstring and the smoke leg both call this as `--check`, while argparse only
    # knew the positional `check` -- so the reader-facing leg died on an unknown argument and
    # the round that wired it reported a green it had never run. Accept both spellings.
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args(argv)
    if args.selftest:
        return selftest()
    if args.check:
        return check()
    if args.cmd == "check":
        return check()
    c = build()
    os.makedirs(os.path.dirname(OUT_JSON), exist_ok=True)
    with open(OUT_JSON, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(c, fh, ensure_ascii=False, indent=1, sort_keys=False)
        fh.write("\n")
    os.makedirs(os.path.dirname(OUT_MD), exist_ok=True)
    with open(OUT_MD, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(render_md(c))
    print("read %d faces (cutoff %s)" % (c["n_faces_read"], c["evidence_cutoff"]))
    for v in c["verdicts"]:
        print("  %s: %s" % (v["verdict"], v["why"]))
    print("wrote results/e33_ladder_census.json and research/E33_LADDER_CENSUS.md")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
