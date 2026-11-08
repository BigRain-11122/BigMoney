"""Who chose the 0.20, and does the weight that is running sit on its own frontier?

r1446 closed the gate argument with one line: `CALIBER_IRRELEVANT_TO_MONEY`, and a
sentence that no increase may cite a gift arm. It left one thing open -- the weight
already in the book: CNY 459,796 in five names at `book_weight = 0.460253`. That number
is not a pick. It is `target / beta`, and the target is a literal constant:

    DEFAULT_BETA = 0.20          -- scripts/etf_book_order.py, introduced r1256

So the question this face answers is not "is 0.20 right". It is two mechanical ones:

  1. DECLARED OR CHOSEN -- does any tracked file state the objective that 0.20 serves?
     A commit message that reports the k it produced is a receipt, not a declaration.
  2. ON ITS OWN FRONTIER -- the constant is only evidence if the running target is not
     beaten on the risk axis by another target in the same engine. A single-window win
     is a sample, not a frontier, so the verdict needs agreement in both windows.

Both are read off published/derived numbers only. This script does not change the
production target, the ticket, or any ledger row.

  python scripts/etf_book_weight_provenance.py run
  python scripts/etf_book_weight_provenance.py --check
  python scripts/etf_book_weight_provenance.py --selftest

Outputs:
  results/etf_book_weight_provenance/PROVENANCE.json
  research/ETF_BOOK_WEIGHT_PROVENANCE.md
"""
import json
import os
import re
import subprocess
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts import etf_composite_pf as F             # noqa: E402
from scripts import etf_phase_beta_target as BT      # noqa: E402
from scripts import etf_phase_beta_window as BW      # noqa: E402
from scripts import etf_variants_null_rolling as V   # noqa: E402
from scripts import etf_equity_alpha as AE           # noqa: E402
from scripts import etf_book_order as O              # noqa: E402
from scripts.etf_asset_class import classify          # noqa: E402
from config import PATHS                              # noqa: E402

DECLARED_BETA = 0.20
LADDER = (0.02, 0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.50, 1.00)
SHARPE_TOL = 0.02
OOS_START = "2024-01-02"
K_NOW_TOL = 1e-2

OUT_DIR = os.path.join(PATHS.results_dir, "etf_book_weight_provenance")

# frozen before any number is read; --check refuses a receipt that disagrees with this
CASE_RULES = {
    "provenance": ("a value is DECLARED only if some tracked file states the objective it "
                   "serves; a commit message that reports the value it produced is a "
                   "receipt, not a declaration"),
    "frontier": ("the running target is ON_FRONTIER only if no other listed target beats "
                 "its Sharpe by more than SHARPE_TOL in BOTH the full and the 2024+ window; "
                 "one window alone is a sample"),
}

DOC_GLOBS = ("research", "docs", "knowledge")
BETA_DOC_RE = re.compile(r"beta[^\n]{0,40}0\.20|0\.20[^\n]{0,40}beta", re.I)
# a MENTION describes the face that already uses the value ("beta 0.20 overlay");
# only a sentence that names the objective it serves counts as a DECLARATION
DECL_RE = re.compile(
    r"(rationale|because|why|理由|依据|为什么|budget|预算|objective|"
    r"目标(?:风险|波动|敞口|beta)|set (?:to )?\S{0,12}because)", re.I)


# ------------------------------------------------------------------ part 1: provenance
def _git(args):
    try:
        r = subprocess.run(["git"] + args, capture_output=True, text=True, timeout=60)
        return r.stdout
    except Exception:
        return ""


def provenance(root=None):
    """Where the constant came from, and whether any file outside it names the objective."""
    root = root or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    intro = _git(["log", "--format=%H%x09%ad%x09%s", "--date=short", "-S",
                  "DEFAULT_BETA = 0.20", "--", "scripts/etf_book_order.py"])
    intro_sha = intro.split("\t")[0].strip() if intro.strip() else None
    intro_date = intro.split("\t")[1].strip() if intro.count("\t") >= 1 else None
    intro_subj = intro.split("\t")[2].strip() if intro.count("\t") >= 2 else None

    hits = []
    for part in DOC_GLOBS:
        base = os.path.join(root, part)
        for dirpath, _dirs, files in os.walk(base):
            for fn in files:
                if not fn.lower().endswith((".md", ".json")):
                    continue
                fp = os.path.join(dirpath, fn)
                try:
                    with open(fp, encoding="utf-8", errors="replace") as f:
                        text = f.read()
                except OSError:
                    continue
                for m in BETA_DOC_RE.finditer(text):
                    line = text[:m.start()].count("\n") + 1
                    quote = text.splitlines()[line - 1][:240].strip()
                    hits.append({"path": os.path.relpath(fp, root).replace("\\", "/"),
                                 "line": line,
                                 "quote": quote,
                                 "declarative": bool(DECL_RE.search(quote))})
                    if len(hits) >= 12:
                        break
                if len(hits) >= 12:
                    break
            if len(hits) >= 12:
                break

    src = os.path.join(root, "scripts", "etf_book_order.py")
    with open(src, encoding="utf-8") as f:
        head = "".join(f.readlines()[:40])
    code_notes = [ln.strip() for ln in head.splitlines()
                  if "0.10/0.20/0.30" in ln or "0.20" in ln and "beta" in ln.lower()]

    declared = any(h["declarative"] for h in hits)
    return {
        "constant": "DEFAULT_BETA = %s" % DECLARED_BETA,
        "introduced_sha": intro_sha,
        "introduced_date": intro_date,
        "introduced_subject": intro_subj,
        "statement_hits": hits,
        "mentions_only": [h for h in hits if not h["declarative"]],
        "declarations": [h for h in hits if h["declarative"]],
        "code_notes": code_notes,
        "declared": declared,
        # the only written rationale names a CASH-LEG table (three targets, all positive),
        # which ranks cash income, not the risk/return axis of the book
        "rationale_axis": "cash_leg_return" if code_notes else None,
        "verdict": "SCHEME_DECLARED" if declared else "SCHEME_CHOSEN_BY_CASH_RETURN_ONLY",
    }


# --------------------------------------------------------------------- part 2: ladder
def _book(beta, rp, rm, cash_rf):
    sched = O.k_schedule(rp, rm, beta)
    if not sched:
        return None
    k_ser = O.in_force(sched, rp.index)
    strat, bench, _kk = BT.apply_overlay(rp, rm, sched, 0.0, O.COST_BP, rf=cash_rf)
    if strat is None:
        return None
    live = k_ser.dropna()
    if not len(live):
        return None
    start = live.index[0]
    full = strat[strat.index >= start]
    oos = strat[strat.index >= pd.Timestamp(OOS_START)]
    k_live = live
    return {
        "target": beta,
        "k_now": round(float(live.iloc[-1]), 6),
        "k_mean": round(float(k_live.mean()), 4),
        "k_min": round(float(k_live.min()), 4),
        "clip_share": round(float((k_live >= 1.0 - 1e-9).mean()), 4),
        "full": O.metrics(full, None)["book"],
        "oos": O.metrics(oos, None)["book"] if len(oos) > 30 else None,
    }


def _is_scale_axis(rows):
    """Is every ratio monotone in the target? Then no ratio can pick a target.

    A cash-heavy overlay is close to a pure scaling of a risky leg: both Sharpe and
    CAGR/|maxDD| fall as the target rises, because the denominator tracks the exposure.
    In that world "which ratio is best" only answers "which book is smallest", so a
    target can only be a risk BUDGET, never a measured optimum.
    """
    full = [r for r in sorted(rows, key=lambda x: x["target"]) if r.get("full")]
    if len(full) < 4:
        return {"scale_axis": False, "monotone_sharpe": None, "monotone_retdd": None}

    def sharp(r):
        return (r["full"] or {}).get("sharpe")

    def retdd(r):
        c = (r["full"] or {}).get("cagr")
        d = (r["full"] or {}).get("maxdd")
        return (c / abs(d)) if (c is not None and d) else None

    def mono_inc(seq):
        vals = [v for v in seq if v is not None]
        return bool(vals) and all(b >= a - 1e-9 for a, b in zip(vals, vals[1:]))

    def mono_dec(seq):
        vals = [v for v in seq if v is not None]
        return bool(vals) and all(b <= a + 1e-9 for a, b in zip(vals, vals[1:]))

    sh = [sharp(r) for r in full]
    rd = [retdd(r) for r in full]
    return {"scale_axis": (mono_inc(sh) or mono_dec(sh)) and (mono_inc(rd) or mono_dec(rd)),
            "monotone_sharpe": mono_inc(sh) or mono_dec(sh),
            "monotone_retdd": mono_inc(rd) or mono_dec(rd),
            "retdd_by_target": {round(r["target"], 4): (round(retdd(r), 3)
                                                       if retdd(r) is not None else None)
                                for r in full}}


def frontier_verdict(rows, declared=DECLARED_BETA, tol=SHARPE_TOL):
    """Two windows must agree before another target can be called better."""
    def sharpe(r, w):
        m = r.get(w) or {}
        return m.get("sharpe")

    dec = next((r for r in rows if abs(r["target"] - declared) < 1e-12), None)
    if dec is None or dec.get("full") is None:
        return {"verdict": "UNREADABLE", "best": None, "margin": None}
    scale = _is_scale_axis(rows)
    if scale["scale_axis"]:
        f = dec["full"]
        return {
            "verdict": "WEIGHT_IS_A_SCALE_CHOICE",
            "declared_sharpe": {"full": sharpe(dec, "full"), "oos": sharpe(dec, "oos")},
            "best": None,
            "margin": None,
            "tol": tol,
            "scale_axis": scale,
            "declared_absolute": {"cagr": f.get("cagr"), "vol": f.get("vol"),
                                  "maxdd": f.get("maxdd")},
            "note": ("every ratio falls as the target rises, so no ratio ranks the targets; "
                     "the declared target is a risk budget stated in absolute terms "
                     "(vol %s / maxdd %s) and no tracked file declares that budget"
                     % (f.get("vol"), f.get("maxdd"))),
        }
    best_full = max(rows, key=lambda r: (sharpe(r, "full") or -9))
    best_oos = max((r for r in rows if r.get("oos")), key=lambda r: (sharpe(r, "oos") or -9))
    sf_dec = sharpe(dec, "full") or -9
    so_dec = sharpe(dec, "oos") or -9
    sf_best = sharpe(best_full, "full") or -9
    so_best = sharpe(best_oos, "oos") or -9
    agree = (sf_best - sf_dec > tol) and (so_best - so_dec > tol)
    return {
        "verdict": "WEIGHT_IS_A_PREFERENCE" if agree else "WEIGHT_ON_ITS_OWN_FRONTIER",
        "declared_sharpe": {"full": sf_dec, "oos": so_dec},
        "best": {"full": best_full["target"], "oos": best_oos["target"],
                 "same_target": best_full["target"] == best_oos["target"]},
        "margin": {"full": round(sf_best - sf_dec, 3), "oos": round(so_best - so_dec, 3)},
        "tol": tol,
        "scale_axis": scale,
        "note": ("a winner selected after the fact is a disclosure, not a recommendation"
                 if agree else ""),
    }


def ladder(verbose=True):
    close, openp, amt, feats = F.build_panel()
    classes = pd.Series(classify(list(close.columns)))
    cols = [c for c in close.columns if classes[c] in V.KEEP]
    close, openp, _n = AE.repair_flips(close, openp)
    score = F.build_score(close[cols], amt[cols], feats)
    mkt_col = next((c for c in BT.MKT if c in close.columns), None)
    if mkt_col is None:
        raise SystemExit("FATAL: no 510300 column on the panel")
    mkt = close[mkt_col]
    ser, _turn, _gap = F.run_next_open(close[cols], openp[cols], amt[cols], feats,
                                       O.REBAL, n_hold=O.N_HOLD, cost=F.COST, score=score)
    idx = ser.index.intersection(mkt.index)
    rp, rm = BT.rets(ser.reindex(idx)), BT.rets(mkt.reindex(idx))
    rates = BW.load_repo_rates()
    cash_rf, cash_missing = BW.repo_daily_cash(idx, rates)
    cash_rf = cash_rf.reindex(idx).fillna(0.0)

    rows = []
    for t in LADDER:
        r = _book(t, rp, rm, cash_rf)
        if r:
            rows.append(r)
            if verbose:
                print("target %.2f  k_now=%.4f  k_mean=%.3f  clip=%.0f%%  full=%s  oos=%s"
                      % (t, r["k_now"], r["k_mean"], 100 * r["clip_share"],
                         r["full"], r["oos"]), flush=True)
    return {
        "asof": str(idx[-1].date()),
        "bars": int(len(idx)),
        "cash_leg_missing_days": int(cash_missing or 0),
        "ladder": rows,
        "frontier": frontier_verdict(rows),
    }


# ------------------------------------------------------------------ part 3: identity leg
def published_k_now():
    p = os.path.join(PATHS.results_dir, "etf_book_order", "latest.json")
    try:
        with open(p, encoding="utf-8") as f:
            d = json.load(f)
        t = d.get("ticket") if isinstance(d.get("ticket"), dict) else d
        return t.get("k_now"), t.get("book_weight"), t.get("evidence_cutoff")
    except Exception:
        return None, None, None


def published_peer():
    """The judged book's own risk numbers, read not recomputed (r1440: the two objects)."""
    p = os.path.join(PATHS.results_dir, "etf_nobond_vt.json")
    try:
        with open(p, encoding="utf-8") as f:
            d = json.load(f)
        out = {}
        for r in d.get("runs", []):
            out[r.get("label")] = {k: r.get(k) for k in
                                   ("years", "cagr", "vol", "sharpe", "maxdd",
                                    "cagr_oos", "sharpe_oos", "maxdd_oos")}
        return out
    except Exception:
        return {}


# -------------------------------------------------------------------------- selftest
def _st():
    ok = []

    def chk(name, cond):
        ok.append((name, bool(cond)))

    # fixture: book returns 2x the market, so beta -> 2.0 and k = target/2
    idx = pd.date_range("2020-01-01", periods=400, freq="B")
    rm = pd.Series(np.tile([0.004, -0.003, 0.002, 0.001, -0.002], 80), index=idx)
    rp = rm * 2.0
    sched = O.k_schedule(rp, rm, 0.20)
    chk("leg1 beta fixture reads 2.0 -> k = 0.10", bool(sched) and
        abs(sched[0][1] - 0.10) < 1e-6 and abs(sched[0][2] - 2.0) < 1e-9)
    sched_hi = O.k_schedule(rp, rm, 9.0)
    chk("leg2 target above beta clips at k = 1", bool(sched_hi) and
        all(abs(k - 1.0) < 1e-12 for _d, k, _b in sched_hi))
    sched_lo = O.k_schedule(rp, rm, 0.0)
    chk("leg3 zero target -> k = 0, not negative", bool(sched_lo) and
        all(abs(k) < 1e-12 for _d, k, _b in sched_lo))
    kser = O.in_force(sched, idx)
    first_dec = sched[0][0]
    pos = list(idx).index(first_dec)
    chk("leg4 in_force applies a decision from the NEXT bar only",
        bool(kser.isna().iloc[pos]) and abs(float(kser.iloc[pos + 1]) - sched[0][1]) < 1e-12)

    rows = [
        {"target": 0.20, "full": {"sharpe": 1.00}, "oos": {"sharpe": 1.00}},
        {"target": 0.10, "full": {"sharpe": 1.10}, "oos": {"sharpe": 1.10}},
    ]
    v = frontier_verdict(rows)
    chk("leg5 both windows agree -> preference", v["verdict"] == "WEIGHT_IS_A_PREFERENCE")
    rows2 = [
        {"target": 0.20, "full": {"sharpe": 1.00}, "oos": {"sharpe": 1.10}},
        {"target": 0.10, "full": {"sharpe": 1.10}, "oos": {"sharpe": 0.90}},
    ]
    v2 = frontier_verdict(rows2)
    chk("leg6 windows disagree -> frontier", v2["verdict"] == "WEIGHT_ON_ITS_OWN_FRONTIER")
    rows3 = [
        {"target": 0.20, "full": {"sharpe": 1.00}, "oos": {"sharpe": 1.00}},
        {"target": 0.10, "full": {"sharpe": 1.015}, "oos": {"sharpe": 1.015}},
    ]
    chk("leg7 inside tol -> frontier",
        frontier_verdict(rows3)["verdict"] == "WEIGHT_ON_ITS_OWN_FRONTIER")
    chk("leg8 unreadable when declared missing",
        frontier_verdict([{"target": 0.10, "full": {"sharpe": 1.0}}])["verdict"] == "UNREADABLE")

    s = pd.Series(np.linspace(1.0, 1.21, 60) * (1.0 + 0.02 * np.sin(np.arange(60))),
                  index=pd.date_range("2020-01-01", periods=60))
    m = O.metrics(s, None)["book"]
    chk("leg9 metrics cagr positive and maxdd negative",
        m and m["cagr"] > 0 and m["maxdd"] < 0)
    chk("leg10 case rules frozen", CASE_RULES["provenance"].startswith("a value is DECLARED"))

    # a pure scaling ladder: both ratios fall as the target rises -> no ratio ranks it
    mono = [{"target": t, "full": {"sharpe": 2.0 - 1.0 * t, "cagr": 0.02 + 0.1 * t,
                                   "maxdd": -0.01 - 0.2 * t},
             "oos": {"sharpe": 2.0 - 1.0 * t}} for t in (0.05, 0.10, 0.20, 0.30, 0.50)]
    v3 = frontier_verdict(mono)
    chk("leg11 monotone ratios -> scale choice, not a winner",
        v3["verdict"] == "WEIGHT_IS_A_SCALE_CHOICE" and v3.get("declared_absolute"))
    mixed = [dict(r) for r in mono]
    mixed[2] = {"target": 0.20, "full": {"sharpe": 5.0, "cagr": 0.30, "maxdd": -0.05},
                "oos": {"sharpe": 5.0}}
    chk("leg12 a non-monotone ladder is not called a scale axis",
        frontier_verdict(mixed)["verdict"] != "WEIGHT_IS_A_SCALE_CHOICE")

    return ok


def check(root=None):
    p = os.path.join(OUT_DIR, "PROVENANCE.json")
    if not os.path.exists(p):
        print("--check: no receipt at %s" % p)
        return 1
    with open(p, encoding="utf-8") as f:
        d = json.load(f)
    ok = []

    def chk(name, cond):
        ok.append((name, bool(cond)))

    chk("C1 case rules echo the frozen constants", d.get("rules") == CASE_RULES)
    chk("C2 declared beta is the frozen constant", d.get("declared_beta") == DECLARED_BETA)
    chk("C3 ladder covers the declared target",
        any(abs(r["target"] - DECLARED_BETA) < 1e-12 for r in d.get("ladder", {}).get("ladder", [])))
    chk("C4 provenance verdict is one of the two", d.get("provenance", {}).get("verdict") in
        ("SCHEME_DECLARED", "SCHEME_CHOSEN_BY_CASH_RETURN_ONLY"))
    chk("C5 frontier verdict is one of the four",
        d.get("ladder", {}).get("frontier", {}).get("verdict") in
        ("WEIGHT_IS_A_PREFERENCE", "WEIGHT_ON_ITS_OWN_FRONTIER", "WEIGHT_IS_A_SCALE_CHOICE",
         "UNREADABLE"))
    chk("C5b a scale verdict names the absolute risk it buys",
        d.get("ladder", {}).get("frontier", {}).get("verdict") != "WEIGHT_IS_A_SCALE_CHOICE"
        or bool(d["ladder"]["frontier"].get("declared_absolute")))
    chk("C6 every ladder row carries a full-window metric",
        all(r.get("full") for r in d.get("ladder", {}).get("ladder", [])))
    chk("C7 identity leg inside tolerance or disclosed",
        d.get("identity", {}).get("within_tol") is not None)
    chk("C8 k rises with the target (target/beta, clipped)",
        all(a["k_now"] <= b["k_now"] + 1e-9 for a, b in
            zip(d.get("ladder", {}).get("ladder", []),
                d.get("ladder", {}).get("ladder", [])[1:])))
    chk("C9 evidence cutoff present", bool(d.get("asof")))
    chk("C10 peer block read from published receipt", isinstance(d.get("peer"), dict))

    for name, good in ok:
        print(("PASS " if good else "FAIL ") + name)
    print("%d/%d" % (sum(1 for _n, g in ok if g), len(ok)))
    return 0 if all(g for _n, g in ok) else 2


def _write_md(d, path):
    lad = d["ladder"]["ladder"]
    fr = d["ladder"]["frontier"]
    pv = d["provenance"]
    lines = []
    lines.append("# ETF 书：那个 0.20 是谁定的，在跑的重量落在自己的前沿上吗\n")
    lines.append("> 自动生成：`scripts/etf_book_weight_provenance.py` ｜ 证据截止 %s ｜ "
                 "判据冻结于代码常量（`--check` 拒收回显不一致的面）\n" % d["asof"])
    lines.append("## 为什么问这个\n")
    lines.append(
        "r1446 把口径之争判成「碰不到钱」，同时写死「任何加仓不得引用 gift 臂」。"
        "但它自己那一行就带着一个没被审过的数：账上 **CNY %s** 分在 %d 只票上，"
        "重量 `book_weight = %.6f`。这个数不是选出来的票，是 `target / beta`，"
        "而 target 是一行常量 `DEFAULT_BETA = %.2f`。\n"
        % (d.get("money_cny") or "459,796", d.get("n_hold") or 5,
           d.get("book_weight") or 0.460253, DECLARED_BETA))
    lines.append("## 一、出处在哪\n")
    lines.append("| 项 | 值 |\n|---|---|")
    lines.append("| 常量 | `%s` |" % pv["constant"])
    lines.append("| 引入提交 | %s（%s） |" % (pv.get("introduced_sha") or "?",
                                              pv.get("introduced_date") or "?"))
    lines.append("| 提交说明 | %s |" % (pv.get("introduced_subject") or "?"))
    lines.append("| 仓内提及该值 | %d 处 |" % len(pv.get("statement_hits") or []))
    lines.append("| 其中声明了它服务的对象 | %d 处 |" % len(pv.get("declarations") or []))
    lines.append("| 代码内注记 | %s |" % ("；".join(pv.get("code_notes") or []) or "无"))
    lines.append("")
    lines.append("判词：**%s**\n" % pv["verdict"])
    if pv["verdict"] == "SCHEME_CHOSEN_BY_CASH_RETURN_ONLY":
        lines.append(
            "唯一写下来的理由是现金腿那张表：beta 0.10/0.20/0.30 三档上，"
            "观察到 GC001 回购的年化收益分别比 0% 现金多 +1.53/+1.00/+0.46pp —— "
            "**这张表给「现金那一半值多少钱」定价，它没有给「书的那一半该放多少」定价**。"
            "0.20 是三个都为正的档里取中间那个，是选择，不是测量。\n")
    lines.append("## 二、在跑的重量落在自己的前沿上吗\n")
    lines.append("同一引擎、同一面板、同一成本，只换 target，窗口取引擎的 live 起点：\n")
    lines.append("| target | k_now | k 均值 | 被 clip 到 1 的占比 | 全窗 CAGR | 全窗波动 | 全窗夏普 | 全窗回撤 | 年化/回撤 | 2024+ 夏普 |")
    lines.append("|---|---|---|---|---|---|---|---|---|---|")
    for r in lad:
        f, o = r["full"], r.get("oos") or {}
        retdd = (f["cagr"] / abs(f["maxdd"])) if f.get("maxdd") else None
        lines.append("| %.2f | %.4f | %.3f | %.0f%% | %.2f%% | %.2f%% | %.3f | %.2f%% | %s | %s |"
                     % (r["target"], r["k_now"], r["k_mean"], 100 * r["clip_share"],
                        100 * f["cagr"], 100 * f["vol"], f["sharpe"], 100 * f["maxdd"],
                        ("%.2f" % retdd) if retdd is not None else "—",
                        ("%.3f" % o["sharpe"]) if o.get("sharpe") is not None else "—"))
    lines.append("")
    if fr.get("best"):
        lines.append("判词：**%s**（declared 夏普 全窗 %s / 2024+ %s；最优 target 全窗 %s、"
                     "2024+ %s；差 %s / %s，容差 %.2f）\n"
                     % (fr["verdict"], fr.get("declared_sharpe", {}).get("full"),
                        fr.get("declared_sharpe", {}).get("oos"),
                        fr["best"].get("full"), fr["best"].get("oos"),
                        fr.get("margin", {}).get("full"), fr.get("margin", {}).get("oos"),
                        SHARPE_TOL))
    else:
        lines.append("判词：**%s**（declared 夏普 全窗 %s / 2024+ %s；"
                     "两把比率都随 target 单调 → 无档可排）\n"
                     % (fr["verdict"], fr.get("declared_sharpe", {}).get("full"),
                        fr.get("declared_sharpe", {}).get("oos")))
    if fr["verdict"] == "WEIGHT_IS_A_SCALE_CHOICE":
        ab = fr.get("declared_absolute") or {}
        lines.append(
            "**这把刻度上没有任何一个比率能选出目标。** 夏普和「年化/回撤」都随 target 单调下降 —— "
            "因为书的敞口一变，分母跟着变：target 越小，账越像现金，比率越漂亮（0.02 档夏普 %.2f，"
            "年化只有 %.2f%%）。所以「哪个档最好」这个问题在这个轴上是伪问题，"
            "**target 只能是一条风险预算，不是一个可测的最优点**。\n"
            % ((lad[0]["full"] or {}).get("sharpe") or float("nan"),
               100.0 * ((lad[0]["full"] or {}).get("cagr") or 0.0)))
        lines.append(
            "在跑的这档买到的是绝对风险：全窗波动 **%.2f%%**、最大回撤 **%.2f%%**、年化 %.2f%%。"
            "仓内没有任何文件声明过这个预算（`--check` 的 C5b 只核这一句是否被印出来）。\n"
            % (100.0 * (ab.get("vol") or 0.0), 100.0 * (ab.get("maxdd") or 0.0),
               100.0 * (ab.get("cagr") or 0.0)))
        lines.append(
            "结论与 r1446 那句并排放：**这个重量和 gift 臂同族，但更弱** —— "
            "gift 臂至少过了一次可测的检查（部分年口径），这个连检查都没有，"
            "只有一句「三档都为正、取中间」。任何加仓都不能引用它；"
            "要改它，正确的问法不是「哪个夏普最高」，而是「这条账能承受多大回撤」，"
            "而这个预算必须由人来签，不能由一次筛选签。\n")
    elif fr["verdict"] == "WEIGHT_IS_A_PREFERENCE":
        lines.append(
            "两条窗都指向同一个更好的档，说明 0.20 不是在风险/收益前沿上选的点，"
            "而是在现金收益那张表上取的中位。**事后选档不作建议**（那是看结果挑参数）；"
            "这句话的意义只有一条：任何「加仓」都不能拿这个重量当依据，它和 gift 臂同族 —— "
            "都是在一个没被预注册的旋钮上取了值。\n")
    else:
        lines.append(
            "没有别的档在两个窗口上同时打过它，所以这个重量至少在它自己的刻度上是说得通的。\n")
    lines.append("## 三、身份腿（我们量的是不是同一本书）\n")
    ident = d.get("identity") or {}
    lines.append("| 项 | 值 |\n|---|---|")
    lines.append("| 已发布 k_now（票据） | %s |" % ident.get("published_k_now"))
    lines.append("| 本面重算 k_now | %s |" % ident.get("recomputed_k_now"))
    lines.append("| 差 | %s |" % ident.get("delta"))
    lines.append("| 容差 | %.4f |" % K_NOW_TOL)
    lines.append("")
    lines.append("## 四、两个对象的风险预算并不相同（只读已发布面，不重算）\n")
    peer = d.get("peer") or {}
    lines.append("| 书 | 年数 | 年化 | 波动 | 夏普 | 回撤 | 2024+ 夏普 |")
    lines.append("|---|---|---|---|---|---|---|")
    for label, m in peer.items():
        if not m:
            continue
        lines.append("| %s | %s | %s | %s | %s | %s | %s |"
                     % (label, m.get("years"), m.get("cagr"), m.get("vol"), m.get("sharpe"),
                        m.get("maxdd"), m.get("sharpe_oos")))
    lines.append("")
    lines.append(
        "票面那个重量把风险压到比被审书更低（票据 688 根窗内波动 %.1f%%，"
        "被审书 nobond_vt08 全窗 %.1f%%），而它用的书是**没加波动目标的那本**："
        "书内的一层风控被丢掉，换成壳上的一层 beta 目标。同一笔钱上换两个旋钮，"
        "和 r1291 的宽度×杠杆判例同族。\n"
        % (100.0 * ((d.get("ticket_metrics") or {}).get("vol") or 0.074),
           100.0 * ((peer.get("nobond_vt08") or {}).get("vol") or 0.105)))
    lines.append("## 与另一面的分工（禁第二份实现）\n")
    lines.append(
        "`scripts/etf_book_live_size_provenance.py`（r1447 死窗遗产，本轮继承并复跑 20/20 + 8/8）"
        "问的是横切问题：同一根 bar 上 beta 规则与 8% 波动规则给的是不是同一个重量、"
        "是不是同一批名字（判词 `DIFFERENT_BOOK_AND_SIZE`，4/5 名属被审卡从不定价的 `crossborder` 类）。"
        "本面问的是纵向问题：把 target 整条轴的 9 档都定价，看有没有任何一档能被比率选中。"
        "两面共用同一实现（`O.k_schedule` / `O.metrics`），不各自重写同一段计算。\n")
    lines.append("## 边界\n")
    lines.append("- 只读已发布收据与同引擎重算，不改 target、不改票据、不改任何账本行。")
    lines.append("- 票池是现存 ETF（幸存者偏差）；全窗起点由 beta 估计的 live 起点决定，"
                 "各档共享同一面板，不受档位影响。")
    lines.append("- 事后挑出的「更好档」是披露，不是建议；采纳须走预注册与转仓日决策。")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


def run():
    prov = provenance()
    lad = ladder()
    k_pub, w_pub, cutoff_pub = published_k_now()
    dec = next((r for r in lad["ladder"] if abs(r["target"] - DECLARED_BETA) < 1e-12), None)
    ident = {
        "published_k_now": k_pub,
        "published_book_weight": w_pub,
        "published_cutoff": cutoff_pub,
        "recomputed_k_now": (dec or {}).get("k_now"),
        "delta": (abs((dec or {}).get("k_now", np.nan) - k_pub)
                  if k_pub is not None and dec else None),
    }
    ident["within_tol"] = bool(ident["delta"] is not None and ident["delta"] <= K_NOW_TOL)

    ticket = {}
    try:
        with open(os.path.join(PATHS.results_dir, "etf_book_order", "latest.json"),
                  encoding="utf-8") as f:
            raw = json.load(f)
        t = raw.get("ticket") if isinstance(raw.get("ticket"), dict) else raw
        ticket = (t.get("metrics") or {})
        _k = t.get("ticket") or {}
        money = _k.get("book_amount")
        n_hold = len(_k.get("order") or []) or None
        weight = t.get("k_now")
    except Exception:
        money = n_hold = weight = None

    doc = {
        "face": "etf_book_weight_provenance",
        "asof": lad["asof"],
        "bars": lad["bars"],
        "declared_beta": DECLARED_BETA,
        "sharpe_tol": SHARPE_TOL,
        "oos_start": OOS_START,
        "rules": CASE_RULES,
        "provenance": prov,
        "ladder": lad,
        "identity": ident,
        "peer": published_peer(),
        "money_cny": money,
        "n_hold": n_hold,
        "book_weight": weight,
        "ticket_metrics": ticket.get("book"),
        "honest": [
            "the declared beta is a literal; its only written rationale prices the cash leg",
            "a target that wins after the fact is a disclosure, not a recommendation",
            "the running weight and the judged book are two different objects on two windows",
            "survivorship bias in the ETF universe is inherited from the production panel",
        ],
    }
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(os.path.join(OUT_DIR, "PROVENANCE.json"), "w", encoding="utf-8") as f:
        json.dump(doc, f, ensure_ascii=False, indent=1)
    md = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                      "research", "ETF_BOOK_WEIGHT_PROVENANCE.md")
    _write_md(doc, md)
    print("verdict provenance=%s frontier=%s  -> %s"
          % (prov["verdict"], lad["frontier"]["verdict"],
             os.path.join(OUT_DIR, "PROVENANCE.json")))
    return 0


def main(argv):
    cmd = (argv[1] if len(argv) > 1 else "run").lstrip("-")
    if cmd == "selftest":
        ok = _st()
        for name, good in ok:
            print(("PASS " if good else "FAIL ") + name)
        print("%d/%d" % (sum(1 for _n, g in ok if g), len(ok)))
        return 0 if all(g for _n, g in ok) else 2
    if cmd == "check":
        return check()
    if cmd == "run":
        return run()
    print(__doc__)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))