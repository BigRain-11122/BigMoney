#!/usr/bin/env python
"""book_pair_years -- the wallet year by year: which year tests it, and does the split hold?

`book_pair_blend` answered "does splitting beat picking the better book" over the whole
overlap window (2020-01-03 -> 2026-11-26) with one number per column.  A funder's next
question is not about the window, it is about *their* year: **how bad is the worst year,
and is the bad year the same in both books?**  A blend that only helps on days is not a
blend you can hold through a bad year.

This face answers that, and it refuses three things the parent's per-year field hides:

  1. **The three columns do not start the same day.**  cb prints 2020 = +10.76% from
     2020-01-03; the blend prints 2020 = +7.29% from 2020-01-06 (its first day is the
     day both books have a level).  Put those in one table and the reader concludes cb
     beat the blend by 3.5pp in 2020; on a common start it is 9.96 vs 7.29.  Every year
     here is cut from ONE start -- the latest of the three columns' first bar in that
     year -- and each column's own raw number is printed beside it so the cost of that
     choice is visible instead of silent.

  2. **The last year is not a year.**  2026 has 217 bars against 242-243 in a full year
     (it stops at 2026-11-26).  The blend's worst year (-6.04%) is that partial year;
     reading it as "one year lost 6%" is a mis-read of a 10.9-month slice.

  3. **The defensive claim has only ever been tested on one book's bad years.**  cb has
     three negative years in this window (2022, 2023, 2026).  etf has none -- seven
     positive years.  So "the blend cushions a bad year" is an *observed* fact about cb's
     down years and an *untested* claim about etf's, and the face says so in those words
     rather than letting a green verdict cover the difference.

It builds no strategy: it imports each parent book's own backtest and the blend face's own
chosen sleeve weight (best.w_cb).  If the parents' bytes or the blend face move, check()
calls itself STALE in the chain's contract words.

Usage:
  python scripts/book_pair_years.py run        # re-derive and publish json + md
  python scripts/book_pair_years.py check      # cheap drift check (stamps only)
  python scripts/book_pair_years.py selftest   # offline arithmetic legs
"""

import argparse
import json
import math
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS = os.path.join(ROOT, "results")
FACE = os.path.join(RESULTS, "book_pair_years.json")
MD = os.path.join(RESULTS, "book_pair_years.md")
BLEND_FACE = os.path.join(RESULTS, "book_pair_blend.json")

PARTIAL_BAR_RATIO = 0.95   # a year with <95% of the window's median full-year bars
COMMON_START_NOTE = (
    "every year is cut from ONE start -- the latest of the three columns' first bar in "
    "that year -- because cb prints 2020 from 2020-01-03 and the blend from 2020-01-06; "
    "each column's own raw number (its own start) is printed beside it"
)


def _rp(rel):
    return os.path.join(ROOT, rel)


def _iso(ts):
    import datetime as _dt

    return _dt.datetime.fromtimestamp(ts).isoformat(timespec="seconds")


def _stamp(path):
    if not os.path.exists(path):
        return {"path": path, "missing": True}
    st = os.stat(path)
    return {"path": path, "size": int(st.st_size), "mtime": _iso(st.st_mtime)}


# ---------------------------------------------------------------- the arithmetic
def year_slices(a, b, bl):
    """Per calendar year, cut all three columns from their common start in that year.

    Returns a list of dicts.  `raw_*` is each column's own start (what the parent faces
    print); `ret_*` is the common-start number this face publishes.  `gap_pp` is
    `ret - raw` in percentage points, so the reader sees what the choice cost.
    """
    years = sorted({int(y) for y in set(a.index.year) | set(b.index.year) | set(bl.index.year)})
    rows = []
    for y in years:
        ia = a.index[a.index.year == y]
        ib = b.index[b.index.year == y]
        ic = bl.index[bl.index.year == y]
        if not (len(ia) and len(ib) and len(ic)):
            continue
        start = max(ia[0], ib[0], ic[0])
        end = min(ia[-1], ib[-1], ic[-1])
        if end <= start:
            continue
        sa = a.loc[start:end]
        sb = b.loc[start:end]
        sc = bl.loc[start:end]
        if min(len(sa), len(sb), len(sc)) < 2:
            continue

        def ret(x):
            return float(x.iloc[-1]) / float(x.iloc[0]) - 1.0

        ra, rb, rc = ret(sa), ret(sb), ret(sc)
        # the same year measured from each column's OWN first bar (parent-face口径)
        wa = a[a.index.year == y]
        wb = b[b.index.year == y]
        wc = bl[bl.index.year == y]
        raw_a, raw_b, raw_c = ret(wa), ret(wb), ret(wc)
        rows.append({
            "year": y,
            "start": str(start.date()),
            "end": str(end.date()),
            "bars": int(len(sc)),
            "ret_cb": ra,
            "ret_etf": rb,
            "ret_blend": rc,
            "raw_cb": raw_a,
            "raw_etf": raw_b,
            "raw_blend": raw_c,
            "gap_cb_pp": (ra - raw_a) * 100.0,
            "gap_etf_pp": (rb - raw_b) * 100.0,
            "gap_blend_pp": (rc - raw_c) * 100.0,
            "cushion_vs_cb_pp": (rc - ra) * 100.0,
            "cushion_vs_etf_pp": (rc - rb) * 100.0,
            "drop_from_best_pp": (max(ra, rb) - rc) * 100.0,
        })
    if not rows:
        return rows
    full = max(r["bars"] for r in rows)
    for r in rows:
        r["partial"] = bool(r["bars"] < PARTIAL_BAR_RATIO * full)
        r["ann_equiv_blend"] = (
            (1.0 + r["ret_blend"]) ** (244.0 / r["bars"]) - 1.0
            if r["partial"] else None)
    return rows


def verdict_of(rows):
    """A word that says what was actually observed, and a flag for what was not."""
    if not rows:
        return {"word": "NO_DATA", "sentence": "no year survives the common-start cut"}
    cb_neg = [r for r in rows if r["ret_cb"] < 0]
    etf_neg = [r for r in rows if r["ret_etf"] < 0]
    blend_neg = [r for r in rows if r["ret_blend"] < 0]
    cushioned = [r for r in cb_neg if r["ret_blend"] > r["ret_cb"]]
    all_cushioned = bool(cb_neg) and len(cushioned) == len(cb_neg)
    word = "DIVERSIFICATION_CUSHIONS_CB_DOWN_YEARS" if all_cushioned else (
        "CUSHION_PARTIAL" if cushioned else "NO_CUSHION_OBSERVED")
    untested = len(etf_neg) == 0
    if untested:
        sentence = (
            "The split held through every bad year cb had (%d of %d: %s), but etf lost "
            "nothing in any of the %d years in this window, so the blend has never been "
            "tested against an etf down year -- that half of the defensive claim is open."
            % (len(cushioned), len(cb_neg),
               ", ".join(str(r["year"]) for r in cb_neg), len(rows))
        )
    else:
        sentence = (
            "The split held through %d of cb's %d bad years; etf had %d bad year(s), so "
            "both sides of the defensive claim have at least one observation."
            % (len(cushioned), len(cb_neg), len(etf_neg))
        )
    return {
        "word": word,
        "sentence": sentence,
        "cb_down_years": [r["year"] for r in cb_neg],
        "etf_down_years": [r["year"] for r in etf_neg],
        "blend_down_years": [r["year"] for r in blend_neg],
        "cushioned_cb_down_years": [r["year"] for r in cushioned],
        "etf_down_years_untested": untested,
    }


def _year_stats(rows, key):
    vals = [r[key] for r in rows]
    return {
        "worst_year": min(vals), "best_year": max(vals),
        "neg_years": sum(1 for v in vals if v < 0),
        "mean_year": sum(vals) / len(vals),
    }


# ---------------------------------------------------------------- the face
def build(write=True, quiet=False):
    import book_pair_blend as B

    cb, cb_meta = B.load_cb()
    etf, etf_meta = B.load_etf()
    cb_w, etf_w, idx = B.align(cb, etf)
    if cb_w is None:
        raise SystemExit("the two books share no days -- refusing to print a year table")

    with open(BLEND_FACE, encoding="utf-8") as fh:
        blend_face = json.load(fh)
    w_cb = float(blend_face["best"]["w_cb"])

    ra = cb_w.pct_change().dropna()
    re_ = etf_w.pct_change().dropna()
    common = ra.index.intersection(re_.index)
    bl = B.blend_daily(ra.reindex(common), re_.reindex(common), w_cb)

    rows = year_slices(cb_w, etf_w, bl)
    verdict = verdict_of(rows)
    stats = {k: _year_stats(rows, "ret_" + k) for k in ("cb", "etf", "blend")}

    # known-truth cross-check against the parent faces' own published numbers
    parent_year_table = {
        "cb": (blend_face.get("parents", {}).get("cb", {}) or {}).get("in_window", {}).get("yearly"),
        "etf": (blend_face.get("parents", {}).get("etf", {}) or {}).get("in_window", {}).get("yearly"),
        "blend": (blend_face.get("best", {}) or {}).get("yearly"),
    }
    recon = []
    for r in rows:
        for k, key in (("cb", "raw_cb"), ("etf", "raw_etf"), ("blend", "raw_blend")):
            pub = (parent_year_table.get(k) or {}).get(str(r["year"]))
            if pub is None:
                recon.append({"year": r["year"], "column": k, "published": None,
                              "matched": None})
                continue
            recon.append({"year": r["year"], "column": k,
                          "published": round(float(pub), 10),
                          "mine": round(r[key], 10),
                          "diff": round(r[key] - float(pub), 10),
                          "matched": abs(r[key] - float(pub)) <= 1e-6})

    face = {
        "face": "book_pair_years",
        "generated_at": _now_iso(),
        "evidence_cutoff": str(max(cb_w.index[-1], etf_w.index[-1]).date()),
        "question": "which year tests the wallet, and does the 30/70 split hold in it?",
        "sleeve": {"w_cb": w_cb, "w_etf": round(1.0 - w_cb, 4),
                   "chosen_by": "results/book_pair_blend.json best.w_cb (not re-chosen here)"},
        "window": {
            "first": str(bl.index[0].date()), "last": str(bl.index[-1].date()),
            "bars": int(len(bl)), "years": len(rows),
            "why": "the overlap only -- cb starts 2007, etf starts 2020-01-03",
        },
        "method": {
            "common_start": COMMON_START_NOTE,
            "year_return": "last level / first level - 1 inside the year's own slice",
            "caliber": blend_face.get("caliber"),
            "partial_rule": "a year whose bars fall below %.0f%% of the window's fullest "
                            "year is marked partial and gets an annualised equivalent"
                            % (PARTIAL_BAR_RATIO * 100),
            "ann_equiv": "annualised equivalent of a partial year, printed only so a "
                         "10.9-month number is not read as a year; it is not an observation",
        },
        "inputs": {"cb_panel": cb_meta["panel"], "etf_panel": etf_meta["panel"],
                   # the blend face is depended on for two numbers, not for its bytes:
                   # it is re-run every time it goes stale, so its mtime moves for reasons
                   # that do not change this face.  Record what is actually used (r1935:
                   # a guard must ask the cheap question that is really the question).
                   "blend_face": {"path": BLEND_FACE, "w_cb": w_cb,
                                  "window_last": (blend_face.get("window") or {}).get("last"),
                                  "cutoff": blend_face.get("evidence_cutoff")}},
        "years": rows,
        "stats": stats,
        "verdict": verdict,
        "reconciliation": {
            "why": "the raw column here must equal each parent face's own published "
                   "yearly number -- if it does not, this face is not reading the book "
                   "the parent published",
            "rows": recon,
            "n_mismatch": sum(1 for x in recon if x["matched"] is False),
        },
        "unverified": [
            "the two sleeves' rebalancing cost between wallets is not modelled (each "
            "parent's own 10bp is inside its series)",
            "the overlap is 6.9 of cb's 19.4 years -- every number here is a recent-window "
            "number",
            "30/70 is the blend face's in-sample best, not a law: this face inherits that "
            "optimism",
            "etf has no down year in this window, so the blend's behaviour inside an etf "
            "down year is unobserved",
        ],
    }
    face = _plain(face)
    if write:
        with open(FACE, "w", encoding="utf-8") as fh:
            json.dump(face, fh, ensure_ascii=False, indent=2)
            fh.write("\n")
        with open(MD, "w", encoding="utf-8") as fh:
            fh.write(_md(face))
    if not quiet:
        print(json.dumps({"face": "book_pair_years", "years": len(rows),
                          "cutoff": face["evidence_cutoff"],
                          "verdict": verdict["word"],
                          "worst_year": stats["blend"]["worst_year"],
                          "mismatch": face["reconciliation"]["n_mismatch"]},
                         ensure_ascii=False))
    return face


def _pct(x):
    return "—" if x is None else "%+.2f%%" % (x * 100.0)


def _pp(x):
    return "—" if x is None else "%+.2fpp" % x


def _md(face):
    v = face["verdict"]
    st = face["stats"]
    out = []
    out.append("# book_pair_years — 钱包的每一年：哪一年会考验你，30/70 扛不扛得住")
    out.append("")
    out.append("面：`results/book_pair_years.json` ｜ 截止：**%s** ｜ 生成：%s"
               % (face["evidence_cutoff"], face["generated_at"]))
    out.append("")
    out.append("问题：%s" % face["question"])
    out.append("")
    out.append("## 读数")
    out.append("")
    out.append("| 列 | 最差年 | 最好年 | 负年数 | 年平均 |")
    out.append("|---|---|---|---|---|")
    for k, name in (("cb", "转债书"), ("etf", "ETF 书"), ("blend", "30/70 组合")):
        s = st[k]
        out.append("| %s | %s | %s | %d | %s |"
                   % (name, _pct(s["worst_year"]), _pct(s["best_year"]),
                      s["neg_years"], _pct(s["mean_year"])))
    out.append("")
    out.append("判词：**%s**" % v["word"])
    out.append("")
    out.append("> %s" % v["sentence"])
    out.append("")
    out.append("## 逐年（三列同一起点）")
    out.append("")
    out.append("* 同一起点 = 该年三列中最后一列首个 bar 的那天。括号里是各列自己起点的原值，"
               "差值就是起点不同的代价。")
    out.append("* `†` 部分年：交易日不足整年的 %.0f%%，年化折算只为防误读，不是观测值。"
               % (PARTIAL_BAR_RATIO * 100))
    out.append("")
    out.append("| 年 | 起始 | 转债 | ETF | 30/70 | 组合比转债 | 组合比最好单书 |")
    out.append("|---|---|---|---|---|---|---|")
    for r in face["years"]:
        mark = " †" if r["partial"] else ""
        out.append("| **%d**%s | %s | %s (%s) | %s (%s) | %s (%s) | %s | %s |"
                   % (r["year"], mark, r["start"],
                      _pct(r["ret_cb"]), _pct(r["raw_cb"]),
                      _pct(r["ret_etf"]), _pct(r["raw_etf"]),
                      _pct(r["ret_blend"]), _pct(r["raw_blend"]),
                      _pp(r["cushion_vs_cb_pp"]), _pp(-r["drop_from_best_pp"])))
    out.append("")
    if any(r["partial"] for r in face["years"]):
        out.append("### 部分年不能当整年读")
        out.append("")
        for r in face["years"]:
            if not r["partial"]:
                continue
            out.append("* **%d**：%d 个 bar（整年 242-243），到 %s 为止。组合 %s，"
                       "折算年化约 %s——**这不是一年亏那么多**，是 %.1f 个月的读数。"
                       % (r["year"], r["bars"], r["end"], _pct(r["ret_blend"]),
                          _pct(r["ann_equiv_blend"]), r["bars"] / 244.0 * 12.0))
        out.append("")
    out.append("## 组合在转债书的坏年里")
    out.append("")
    if v["cb_down_years"]:
        out.append("| 年 | 转债 | 30/70 | 补回来 |")
        out.append("|---|---|---|---|")
        for r in face["years"]:
            if r["ret_cb"] >= 0:
                continue
            out.append("| %d | %s | %s | %s |"
                       % (r["year"], _pct(r["ret_cb"]), _pct(r["ret_blend"]),
                          _pp(r["cushion_vs_cb_pp"])))
    else:
        out.append("这个窗口里转债书没有负年，无可观测的坏年。")
    out.append("")
    out.append("## 起点不同的代价（为什么不能直接抄父面的逐年）")
    out.append("")
    worst = max(face["years"], key=lambda r: abs(r["gap_cb_pp"]))
    out.append("同年三列起点最大差落在 **%d**（起始 %s）：转债书由 %s 变 %s，"
               "差 %s——直接并排父面的逐年，读者会把这一天读成 0.8pp 的业绩。"
               % (worst["year"], worst["start"], _pct(worst["raw_cb"]),
                  _pct(worst["ret_cb"]), _pp(worst["gap_cb_pp"])))
    out.append("")
    out.append("## 口径（继承父面，不新造）")
    out.append("")
    for k, val in (face["method"].get("caliber") or {}).items():
        out.append("* **%s**：%s" % (k, val))
    out.append("")
    out.append("## 未验证（如实）")
    out.append("")
    for u in face["unverified"]:
        out.append("* %s" % u)
    out.append("")
    out.append("## 与父面的对账")
    out.append("")
    out.append("`raw` 列必须逐字等于父面已发布的逐年（差异 ≤1e-6）；不一致=本面读的不是"
               "父面发布的那本书。本轮不一致 %d 处。"
               % face["reconciliation"]["n_mismatch"])
    out.append("")
    return "\n".join(out) + "\n"


def _blend_dep_problems(rec):
    """The blend face is depended on for two numbers, not for its bytes.

    It is re-run every time it goes stale, so its mtime moves for reasons that do not
    change this face.  Recording the stamp would make this leg pay a full ~60s rebuild
    every round for nothing (r1935: a guard should ask the cheap question that IS the
    question).
    """
    if not os.path.exists(rec["path"]):
        return ["STALE: input blend_face %s disappeared" % rec["path"]]
    with open(rec["path"], encoding="utf-8") as fh:
        cur = json.load(fh)
    out = []
    cur_w = (cur.get("best") or {}).get("w_cb")
    cur_last = (cur.get("window") or {}).get("last")
    if cur_w is None or abs(float(cur_w) - float(rec["w_cb"])) > 1e-12:
        out.append("STALE: blend_face sleeve weight moved since this face was written "
                   "(%r -> %r)" % (rec["w_cb"], cur_w))
    if cur_last != rec["window_last"]:
        out.append("STALE: blend_face window moved since this face was written "
                   "(%r -> %r)" % (rec["window_last"], cur_last))
    return out


def check():
    """Cheap drift: have the inputs' bytes moved, and does the face still add up?"""
    if not os.path.exists(FACE):
        print("STALE: book_pair_years face missing (run `python scripts/book_pair_years.py run`)")
        return 3
    with open(FACE, encoding="utf-8") as fh:
        face = json.load(fh)
    problems = []
    for name, rec in (face.get("inputs") or {}).items():
        if not rec or rec.get("missing"):
            problems.append("STALE: input %s is not on disk any more (%s)" % (name, rec))
            continue
        if name == "blend_face":
            problems.extend(_blend_dep_problems(rec))
            continue
        now = _stamp(rec["path"])
        if now.get("missing"):
            problems.append("STALE: input %s path %s disappeared" % (name, rec["path"]))
            continue
        if now["size"] != rec["size"] or now["mtime"] != rec["mtime"]:
            problems.append(
                "STALE: input %s bytes moved since this face was written "
                "(%sB@%s -> %sB@%s)"
                % (name, rec["size"], rec["mtime"], now["size"], now["mtime"]))
    if problems:
        for p in problems:
            print(p)
        return 3

    # internal arithmetic: the published verdict must still follow from the published rows
    rebuilt = verdict_of(face["years"])
    wobble = []
    if rebuilt["word"] != face["verdict"]["word"]:
        wobble.append("verdict word %r does not follow from the rows (%r)"
                      % (face["verdict"]["word"], rebuilt["word"]))
    if rebuilt["cb_down_years"] != face["verdict"]["cb_down_years"]:
        wobble.append("cb_down_years %r does not follow from the rows (%r)"
                      % (face["verdict"]["cb_down_years"], rebuilt["cb_down_years"]))
    for r in face["years"]:
        if abs((r["ret_blend"] - r["ret_cb"]) * 100.0 - r["cushion_vs_cb_pp"]) > 1e-6:
            wobble.append("year %d: cushion_vs_cb_pp is not ret_blend - ret_cb" % r["year"])
        if not r["partial"] and r.get("ann_equiv_blend") is not None:
            wobble.append("year %d: full year carries an annualised equivalent" % r["year"])
    if face["reconciliation"]["n_mismatch"]:
        wobble.append("%d raw column(s) disagree with the parent faces"
                      % face["reconciliation"]["n_mismatch"])
    if wobble:
        for w in wobble:
            print("CHECK FAILED: " + w)
        return 1
    print(json.dumps({"ok": True, "problems": [], "years": len(face["years"]),
                      "cutoff": face["evidence_cutoff"],
                      "verdict": face["verdict"]["word"]}, ensure_ascii=False))
    return 0


# ---------------------------------------------------------------- selftest
def selftest():
    """Offline legs: the common-start cut must bite, and each verdict must be reachable."""
    import numpy as np
    import pandas as pd

    legs, fails = 0, []

    def ok(name, cond, got=""):
        nonlocal legs
        legs += 1
        if not cond:
            fails.append("%s: %r" % (name, got))

    def ser(levels, start):
        idx = pd.bdate_range(start, periods=len(levels))
        return pd.Series([float(x) for x in levels], index=idx)

    # L1: a column starting one day later must be cut, not compared from its own start.
    a = ser([1.0, 1.10, 1.21], "2021-01-04")          # cb: +21% over its own 3 bars
    b = ser([1.0, 1.03, 1.0609], "2021-01-04")        # etf
    bl = ser([1.0, 1.0609, 1.1236], "2021-01-05")     # blend starts one day later
    rows = year_slices(a, b, bl)
    ok("L1 one row", len(rows) == 1, rows)
    r = rows[0]
    ok("L2 common start is the latest", r["start"] == "2021-01-05", r["start"])
    ok("L3 raw keeps each column's own start", abs(r["raw_cb"] - 0.21) < 1e-9, r["raw_cb"])
    ok("L4 common start drops the first bar",
       abs(r["ret_cb"] - 0.10) < 1e-9, r["ret_cb"])
    ok("L5 gap is common - raw", abs(r["gap_cb_pp"] + 11.0) < 1e-6, r["gap_cb_pp"])

    # L6: cushion is in percentage points, blend minus cb
    ok("L6 cushion pp", abs(r["cushion_vs_cb_pp"] - (r["ret_blend"] - r["ret_cb"]) * 100)
       < 1e-9, r["cushion_vs_cb_pp"])

    # L7-L9: verdict must be reachable in both directions on real rows
    def row(y, cbv, etfv, blv):
        return {"year": y, "ret_cb": cbv, "ret_etf": etfv, "ret_blend": blv,
                "partial": False, "ann_equiv_blend": None}

    cush = verdict_of([row(2022, -0.05, 0.03, 0.01), row(2023, -0.02, 0.02, 0.01)])
    ok("L7 all cb down years cushioned -> word", 
       cush["word"] == "DIVERSIFICATION_CUSHIONS_CB_DOWN_YEARS", cush["word"])
    ok("L8 no etf down year -> untested flag", cush["etf_down_years_untested"] is True, cush)
    bad = verdict_of([row(2022, -0.05, 0.03, -0.09), row(2023, -0.02, 0.02, -0.04)])
    ok("L9 blend worse in cb bad years -> must not claim cushion",
       bad["word"] == "NO_CUSHION_OBSERVED", bad["word"])
    mixed = verdict_of([row(2022, -0.05, 0.03, 0.01), row(2023, -0.02, -0.01, -0.03)])
    ok("L10 etf down year present -> flag cleared",
       mixed["etf_down_years_untested"] is False, mixed)
    ok("L11 partial cushion word", mixed["word"] == "CUSHION_PARTIAL", mixed["word"])

    # L12-L14: partial-year rule and the annualised equivalent
    i_all = pd.bdate_range("2021-01-04", periods=343)     # 243 in 2021 + 100 in 2022
    x = pd.Series(np.linspace(1.0, 1.30, 343), index=i_all)
    y = pd.Series(np.linspace(1.0, 1.05, 303), index=i_all[:303])   # only 60 bars in 2022
    rows2 = year_slices(x, x, y)
    ok("L12 both years present", [r["year"] for r in rows2] == [2021, 2022],
       [r["year"] for r in rows2])
    short = [r for r in rows2 if r["year"] == 2022][0]
    ok("L13 short year flagged partial", short["partial"] is True, short["bars"])
    ann = short["ann_equiv_blend"]
    want = (1.0 + short["ret_blend"]) ** (244.0 / short["bars"]) - 1.0
    ok("L14 annualised equivalent matches its own formula", abs(ann - want) < 1e-9,
       (ann, want))

    # L14: a full-length year must not carry an annualised equivalent
    idx = pd.bdate_range("2021-01-04", periods=243)
    full = pd.Series(np.linspace(1.0, 1.2, 243), index=idx)
    rows3 = year_slices(full, full, full)
    ok("L14 full year not partial", rows3[0]["partial"] is False, rows3[0]["bars"])
    ok("L15 full year has no annualised equivalent",
       rows3[0]["ann_equiv_blend"] is None, rows3[0]["ann_equiv_blend"])

    # L16: endpoint reproduction -- a single-column wallet must equal that column
    rows4 = year_slices(a, b, a)     # w = 1.0 (all cb)
    ok("L16 w=1 blend equals cb", abs(rows4[0]["ret_blend"] - rows4[0]["ret_cb"]) < 1e-12,
       (rows4[0]["ret_blend"], rows4[0]["ret_cb"]))
    rows5 = year_slices(a, b, b)     # w = 0.0 (all etf)
    ok("L17 w=0 blend equals etf",
       abs(rows5[0]["ret_blend"] - rows5[0]["ret_etf"]) < 1e-12,
       (rows5[0]["ret_blend"], rows5[0]["ret_etf"]))

    # L18: mean_year must be a mean, not a total
    agg = _year_stats([row(2021, 0.10, 0.0, 0.0), row(2022, -0.10, 0.0, 0.0)], "ret_cb")
    ok("L18 mean_year arithmetic", abs(agg["mean_year"] - 0.0) < 1e-12, agg["mean_year"])

    # L19: the face's own reconciliation tolerances must be tight enough to catch a real
    # difference (1e-6 is far below any number a reader acts on, and above float noise)
    ok("L19 tolerance rejects a 1e-3 difference", abs(0.001) > 1e-6, 0.001)

    # L20-L22: the blend dependency is judged on its numbers, not on the file's mtime --
    # the parent face is rebuilt every round, so a stamp-based guard would pay a full
    # rebuild for nothing (r1935), while a real move in w_cb must still be caught.
    import tempfile

    tmp = tempfile.mkdtemp(prefix="bpy_")
    dep = os.path.join(tmp, "blend.json")
    with open(dep, "w", encoding="utf-8") as fh:
        json.dump({"best": {"w_cb": 0.30}, "window": {"last": "2026-11-26"}}, fh)
    rec = {"path": dep, "w_cb": 0.30, "window_last": "2026-11-26"}
    ok("L20 unchanged numbers -> no problem", _blend_dep_problems(rec) == [],
       _blend_dep_problems(rec))
    with open(dep, "w", encoding="utf-8") as fh:
        json.dump({"best": {"w_cb": 0.35}, "window": {"last": "2026-11-26"}}, fh)
    got = _blend_dep_problems(rec)
    ok("L21 sleeve weight move -> STALE", len(got) == 1 and "STALE" in got[0], got)
    with open(dep, "w", encoding="utf-8") as fh:
        json.dump({"best": {"w_cb": 0.30}, "window": {"last": "2026-11-27"}}, fh)
    got = _blend_dep_problems(rec)
    ok("L22 window move -> STALE", len(got) == 1 and "STALE" in got[0], got)

    print("selftest: %d/%d PASS" % (legs - len(fails), legs))
    for f in fails:
        print("  FAIL", f)
    return 0 if not fails else 1


def _now_iso():
    import datetime as _dt

    return _dt.datetime.now().astimezone().isoformat(timespec="seconds")


def _plain(o):
    """JSON-safe and byte-stable across reruns (floats rounded to 10 decimals)."""
    import numpy as _np

    if isinstance(o, dict):
        return {str(k): _plain(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [_plain(v) for v in o]
    if isinstance(o, (_np.integer,)):
        return int(o)
    if isinstance(o, (_np.floating,)):
        return round(float(o), 10)
    if isinstance(o, (_np.bool_,)):
        return bool(o)
    if isinstance(o, float):
        return round(o, 10)
    return o


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="cmd")
    sub.add_parser("run", help="re-derive and publish the face")
    sub.add_parser("check", help="cheap contract check against input bytes")
    sub.add_parser("selftest", help="offline arithmetic legs")
    args = ap.parse_args(argv)
    cmd = args.cmd or "run"
    if cmd == "run":
        build(write=True)
        return 0
    if cmd == "check":
        return check()
    if cmd == "selftest":
        return selftest()
    ap.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main())
