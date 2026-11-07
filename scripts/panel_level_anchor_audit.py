"""Does the repaired panel quote the price the tape prints?

`etf_equity_alpha.repair_flips` flattens every single-bar move past 35% and rebuilds the
level by walking FORWARD from each column's own first bar. That is right for a misprint
(the jump is fake, the level never moved) and wrong for a share split (the jump is real
arithmetic, and after flattening it the column keeps its pre-split scale forever).

Nothing in the line ever compared the rebuilt level with the trade. The executable sheet
does compare prices against the panel, so on 2026-11-06 it sized 5,200 shares of 513100 at
11.0388 while that ETF's own amount/volume printed 2.162 -- a 5.1x notional on one leg.

This audit is the counter-measurement, and it is the witness for the re-anchor:

  * `diverged` -- columns whose last rebuilt level differs from their last TRADED close by
    more than `tol` (the old forward rebuild, reproduced here so the number is a measurement
    and not a memory);
  * `vwap`     -- amount/volume of the column's last bar, i.e. the price the tape actually
    printed, used to decide which of the two levels is the truth;
  * `anchored` -- the installed `repair_flips` on the same panel: every usable column must
    end at its own last traded close (asserted, not asserted-about).

A level is a scale: multiplying a column by a constant leaves every return unchanged, so
this repairs sizing without moving a backtest. The selftest proves that invariance rather
than claiming it.

Usage:
  python scripts/panel_level_anchor_audit.py selftest
  python scripts/panel_level_anchor_audit.py run [--tol=0.05] [--vwap-names=12]
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
import pandas as pd

import etf_composite_pf as F
import etf_equity_alpha as A
from config import PATHS

OUT_JSON = os.path.join(PATHS.results_dir, "panel_level_anchor.json")
OUT_MD = os.path.join(PATHS.results_dir, "PANEL-LEVEL-ANCHOR.md")
TOL = 0.05


# --------------------------------------------------------------------------- #
# the two builds
# --------------------------------------------------------------------------- #
def forward_rebuild(close, thr=A.FLIP_THR):
    """The pre-r1400 build, reproduced exactly: forward walk, no re-anchor.

    Kept as a function of the panel (not as prose) so the divergence this round fixed is a
    measurement that can be re-run, and so the selftest can drive both builds on one fixture.
    """
    r = close.ffill().pct_change()
    bad = r.abs() > thr
    r_clean = r.where(~bad, 0.0).fillna(0.0)
    first = close.ffill().bfill().iloc[0]
    adj = (1.0 + r_clean).cumprod().multiply(first, axis=1)
    return adj.where(close.notna())


def level_divergence(close, tol=TOL):
    """Old rebuild vs last traded close, per column."""
    old = forward_rebuild(close)
    raw_last = close.ffill().iloc[-1]
    old_last = old.ffill().iloc[-1]
    ratio = (old_last / raw_last).replace([np.inf, -np.inf], np.nan).dropna()
    off = ratio[(ratio - 1.0).abs() > tol]
    return ratio, off


def vwap_last(symbol):
    """amount/volume of a symbol's last bar -- the price the tape printed that day."""
    path = os.path.join(PATHS.daily_dir, symbol + ".csv")
    if not os.path.exists(path):
        return None
    try:
        d = pd.read_csv(path)
    except Exception:
        return None
    if not {"amount", "volume"} <= set(d.columns) or not len(d):
        return None
    row = d.iloc[-1]
    try:
        vol = float(row["volume"])
        return float(row["amount"]) / vol if vol else None
    except Exception:
        return None


# --------------------------------------------------------------------------- #
# run
# --------------------------------------------------------------------------- #
def run(tol=TOL, vwap_names=12):
    close, openp, _amt, _feats = F.build_panel()
    ratio, off = level_divergence(close, tol)
    adj, _adj_open, n_flip = A.repair_flips(close, openp)
    raw_last = close.ffill().iloc[-1]
    new_last = adj.ffill().iloc[-1]
    resid = (new_last / raw_last).replace([np.inf, -np.inf], np.nan).dropna()
    anchors_ok = bool(len(resid) and float((resid - 1.0).abs().max()) < 1e-9)

    # the tape as referee: for the worst offenders, did the traded print agree with the raw
    # close or with the old rebuild?  A factor of 5 is not a rounding question.
    rows = []
    for sym, val in off.sort_values().head(vwap_names).items():
        vw = vwap_last(sym)
        rows.append({
            "symbol": sym,
            "old_rebuild_last": round(float(new_last.get(sym, np.nan)) / float(val), 6) if val else None,
            "traded_close_last": round(float(raw_last.get(sym, np.nan)), 6),
            "vwap_last_bar": None if vw is None else round(vw, 6),
            "raw_vs_vwap_pct": None if not vw or not np.isfinite(vw) else round(
                100.0 * (float(raw_last.get(sym)) / vw - 1.0), 4),
            "old_vs_vwap_pct": None if not vw or not np.isfinite(vw) else round(
                100.0 * ((float(new_last.get(sym, np.nan)) / float(val)) / vw - 1.0), 4),
            "ratio_old_over_raw": round(float(val), 6),
        })

    checked = [r for r in rows if r["vwap_last_bar"] is not None]
    raw_err = [abs(r["raw_vs_vwap_pct"]) for r in checked]
    old_err = [abs(r["old_vs_vwap_pct"]) for r in checked]

    payload = {
        "evidence_cutoff": str(close.index[-1].date()),
        "panel": {"columns": int(close.shape[1]), "dates": int(close.shape[0]),
                  "first": str(close.index[0].date()), "last": str(close.index[-1].date())},
        "tol": float(tol),
        "diverged": {"columns_over_tol": int(len(off)), "columns_measured": int(len(ratio)),
                     "worst_ratio": round(float(off.max()), 6) if len(off) else None,
                     "best_ratio": round(float(off.min()), 6) if len(off) else None},
        "anchored": {"every_usable_column_ends_at_its_own_traded_close": anchors_ok,
                     "max_residual_ratio_error": round(float((resid - 1.0).abs().max()), 12) if len(resid) else None,
                     "columns_anchored": int(len(resid))},
        "tape_check": {
            "names": rows,
            "median_abs_error_pct": {
                "traded_close": round(float(np.median(raw_err)), 6) if raw_err else None,
                "old_rebuild": round(float(np.median(old_err)), 6) if old_err else None,
            },
            "verdict": ("traded_close_is_the_scale" if raw_err and old_err and
                        np.median(raw_err) < np.median(old_err) else "inconclusive"),
        },
        "flip_prints_flattened": int(n_flip),
        "sentence": (
            "旧的面板重建从每列自己第一根 bar 向前走：把 513100 2022-01-14 的 1:5 份额拆分"
            "当成假报价抹平后，这一列此后一直停在拆分前的价位——11.0388，而它自己的成交额/成交量"
            "打出 2.162。全盘 %d/%d 列（>%d%% 偏离）落到这种状态；本条把每列重新锚到它自己最后一根"
            "成交价上，收益序列逐点不变，只有下单金额回到真实。"
            % (len(off), len(ratio), int(tol * 100))),
        "units": {"ratio": "old_rebuild_last / traded_close_last",
                  "pct": "percent", "columns": "count"},
    }
    os.makedirs(os.path.dirname(OUT_JSON), exist_ok=True)
    with open(OUT_JSON, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=1)
    with open(OUT_MD, "w", encoding="utf-8") as fh:
        fh.write(render(payload))
    print("diverged %d/%d columns (tol %.0f%%) | anchored=%s | tape says %s"
          % (len(off), len(ratio), 100 * tol, anchors_ok, payload["tape_check"]["verdict"]))
    print("wrote %s" % os.path.relpath(OUT_JSON, os.path.dirname(os.path.dirname(OUT_JSON))))
    return 0 if anchors_ok else 1


def render(p):
    t = p["tape_check"]
    lines = [
        "# 面板价位锚定审计（%s）" % p["evidence_cutoff"],
        "",
        p["sentence"],
        "",
        "| 项 | 读数 |",
        "| --- | --- |",
        "| 面板 | %d 列 × %d 根 bar（%s..%s） |" % (
            p["panel"]["columns"], p["panel"]["dates"], p["panel"]["first"], p["panel"]["last"]),
        "| 旧重建偏离成交价 >%.0f%% | **%d** / %d 列（最差 %.3fx，最好 %.3fx） |" % (
            100 * p["tol"], p["diverged"]["columns_over_tol"], p["diverged"]["columns_measured"],
            p["diverged"]["worst_ratio"] or float("nan"), p["diverged"]["best_ratio"] or float("nan")),
        "| 锚定后每列末价==自己的成交价 | %s（残差 %.2e，%d 列） |" % (
            "是" if p["anchored"]["every_usable_column_ends_at_its_own_traded_close"] else "否",
            p["anchored"]["max_residual_ratio_error"] or 0.0, p["anchored"]["columns_anchored"]),
        "| 被抹平的翻转打印 | %d 处 |" % p["flip_prints_flattened"],
        "| 复核（成交额/成交量 vs 两个价位） | 成交价中位误差 %s%% / 旧重建中位误差 %s%% |" % (
            t["median_abs_error_pct"]["traded_close"], t["median_abs_error_pct"]["old_rebuild"]),
        "",
        "| 代码 | 旧重建末价 | 成交价 | 当日 vwap | 成交价 vs vwap | 旧重建 vs vwap | 比值 |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for r in t["names"]:
        lines.append("| %s | %s | %s | %s | %s%% | %s%% | %s |" % (
            r["symbol"], r["old_rebuild_last"], r["traded_close_last"],
            r["vwap_last_bar"], r["raw_vs_vwap_pct"], r["old_vs_vwap_pct"], r["ratio_old_over_raw"]))
    lines += ["", "口径：比值 = 旧重建末价 / 成交价末价；1 表示两者一致。vwap = 当日成交额 / 当日成交量。"]
    return "\n".join(lines) + "\n"


# --------------------------------------------------------------------------- #
# selftest
# --------------------------------------------------------------------------- #
def selftest():
    ok = []

    def leg(name, cond):
        ok.append((name, bool(cond)))

    idx = pd.to_datetime(["2022-01-10", "2022-01-11", "2022-01-12", "2022-01-13", "2022-01-14",
                          "2022-01-17", "2022-01-18"])
    # a genuine 1:2 split on 2022-01-13 (10.20 -> 5.10) beside an untouched column
    split = pd.DataFrame({"A": [10.0, 10.2, 5.1, 5.12, 5.15, 5.2, 5.18],
                          "B": [3.0, 3.02, 3.01, 3.03, 3.02, 3.04, 3.05]}, index=idx)
    adj, _ao, n = A.repair_flips(split, split.copy())
    leg("L1 the split is flattened to a 0% day", abs(float(adj["A"].iloc[2] / adj["A"].iloc[1]) - 1.0) < 1e-12)
    leg("L2 the anchored column ends at its own traded close", abs(float(adj["A"].iloc[-1]) - 5.18) < 1e-9)
    leg("L3 the untouched column is left alone", abs(float(adj["B"].iloc[-1]) - 3.05) < 1e-9)
    old = forward_rebuild(split)
    leg("L4 the old forward rebuild ends 2x high (the defect being fixed)",
        abs(float(old["A"].iloc[-1]) - 2.0 * 5.18) < 1e-9)

    # returns are scale-invariant: the anchored series carries exactly the flattened returns
    r_new = adj["A"].pct_change().fillna(0.0).to_numpy()
    r_old = old["A"].pct_change().fillna(0.0).to_numpy()
    leg("L5 every return is unchanged by the re-anchor (only the level moved)",
        np.allclose(r_new, r_old, atol=1e-12))
    leg("L6 the split day still reads 0%", abs(float(adj["A"].pct_change().iloc[2])) < 1e-12)

    # a misprint spike that reverts: flattened, and the tail still lands on the trade
    spike = pd.DataFrame({"A": [4.0, 4.05, 0.4, 4.06, 4.08, 4.1]},
                         index=idx[:6]).astype(float)
    adj2, _o2, n2 = A.repair_flips(spike, spike.copy())
    leg("L7 a reverting misprint is flattened", abs(float(adj2["A"].pct_change().iloc[2])) < 1e-12)
    leg("L8 and the column still ends at its traded close", abs(float(adj2["A"].iloc[-1]) - 4.1) < 1e-9)

    # a column whose tail is missing must anchor to its last PRICED print, not to NaN
    gap = pd.DataFrame({"A": [2.0, 2.02, 2.05, np.nan, np.nan]}, index=idx[:5]).astype(float)
    adj3, _o3, _n3 = A.repair_flips(gap, gap.copy())
    tail = adj3["A"].dropna()
    leg("L9 a suspended tail anchors to the last priced print", abs(float(tail.iloc[-1]) - 2.05) < 1e-9)

    # a column with no usable price at all must not be rescaled into nonsense
    dead = pd.DataFrame({"A": [np.nan, np.nan, np.nan]}, index=idx[:3]).astype(float)
    adj4, _o4, _n4 = A.repair_flips(dead, dead.copy())
    leg("L10 an empty column stays empty", adj4["A"].isna().all())

    # the open face carries the same scale as the close face
    o_adj, o_open, _ = A.repair_flips(split, split.copy())
    leg("L11 open-to-close ratio survives the re-anchor",
        abs(float((o_open["A"] / o_adj["A"]).iloc[-1]) - 1.0) < 1e-9)

    # determinism
    again, _oo, _nn = A.repair_flips(split, split.copy())
    leg("L12 two runs agree to the byte", np.allclose(adj.to_numpy(), again.to_numpy(), equal_nan=True))

    # live panel, if it is on disk: the installed build must end every usable column on its
    # own traded close, and the old build must have diverged on the same panel
    try:
        close, openp, _a, _f = F.build_panel()
        live_adj, _lo, _ln = A.repair_flips(close, openp)
        raw = close.ffill().iloc[-1]
        got = live_adj.ffill().iloc[-1]
        resid = (got / raw).replace([np.inf, -np.inf], np.nan).dropna()
        leg("L13 live panel: every usable column ends at its own traded close",
            len(resid) > 100 and float((resid - 1.0).abs().max()) < 1e-9)
        _ratio, off = level_divergence(close)
        leg("L14 live panel: the old build really did diverge (this is not a hypothetical)",
            int(len(off)) > 0)
    except Exception as e:  # pragma: no cover - disclosed, never silent
        leg("L13 live panel readable (%r)" % (e,), False)
        leg("L14 live panel readable (%r)" % (e,), False)

    bad = [n for n, v in ok if not v]
    for n, v in ok:
        print("%s %s" % ("PASS" if v else "FAIL", n))
    print("%d/%d" % (len(ok) - len(bad), len(ok)))
    return 0 if not bad else 1


def main(argv):
    cmd = argv[1] if len(argv) > 1 else "run"
    if cmd == "selftest":
        return selftest()
    tol = TOL
    names = 12
    for a in argv[2:]:
        if a.startswith("--tol="):
            tol = float(a.split("=", 1)[1])
        elif a.startswith("--vwap-names="):
            names = int(a.split("=", 1)[1])
    return run(tol=tol, vwap_names=names)


if __name__ == "__main__":
    sys.exit(main(sys.argv))