"""Monthly PIT fundamental factor panel -- the first CONSUMER of the availability face (r1109 bm-a).

WHY: r1108 shipped ``asof_slice()`` but still measured lookahead only as a row
count ("how many codes a period_end join read too early"). A row count is not a
consumer statement: a factor builder cares whether the *ranking* it feeds on is
the same one it would have seen in real time. This script answers that at the
resolution the consumer operates at (r1102 measurement-resolution law): month-
end rebalancing dates.

WHAT THIS DELIVERS (product, not prose):
    * ``pit_factor_panel()`` -- month-end cross-sections carrying, per code, the
      newest report that was actually public at that date (``asof``,
      ``period_end``, ``avail_event``, ``avail_tier``) plus three factors
      (roe / net-profit yoy / revenue yoy), a cross-sectional ``roe_rank_pct``
      and a ``degenerate`` flag (|roe| > 200 or book value per share <= 0 --
      r1107: the degenerate block is where a raw roe rank puts its top rows).
    * ``compare_to_naive()`` -- per month-end, the STRICT (as-of) cross-section
      against the NAIVE (max period_end <= asof) one on the same codes: how many
      codes change report, Spearman rank correlation of roe, and top-decile
      membership overlap. This is the factor-level damage of lookahead.
    * results/fund_pit_factor_panel.json -- the evidence face;
    * data/fund_statement_export/pit_avail/pit_factor_monthly.parquet -- the
      panel artifact (gitignored data lane, regenerate with one command).

DEFINITION (one reading, disclosed): strict pick = max period_end among rows
with ``avail_event <= asof`` (r1108 primitive, imported, never reimplemented);
naive pick = max period_end <= asof regardless of availability. Ties broken by
period_end then availability. Ranks are computed inside one as-of date only.

Subcommands: run | selftest
Exit codes: 0 ok, 2 machinery failure, 3 availability/statement input missing.
"""
from __future__ import annotations

import datetime as dt
import json
import os
import sys

import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if os.path.join(ROOT, "scripts") not in sys.path:
    sys.path.insert(0, os.path.join(ROOT, "scripts"))

from fund_avail_asof_panel import (  # noqa: E402  (single source for the join)
    AVAIL_DIR,
    INCOME,
    NP,
    REV,
    ROE,
    _BIG,
    _TIER_DEADLINE,
    _TIER_EVENT,
    _days,
    _prep,
    asof_slice,
    month_ends,
)

BPS = "\u6bcf\u80a1\u51c0\u8d44\u4ea7"          # book value per share
SUMMARY = os.path.join(ROOT, "results", "fund_pit_factor_panel.json")
PANEL_NAME = "pit_factor_monthly.parquet"
GRID_START = "2010-01-31"
GRID_END = "2026-08-31"
PANEL_WINDOW = 24
DECILE = 0.10
ROE_DEGENERATE = 200.0
FACTORS = (ROE, NP, REV)


# ------------------------------------------------------------------ helpers
def _naive_index(prep):
    """Sorted (code_index * _BIG + period_day) keys -> frame row, rebuilt once.

    Mirrors the layout :func:`fund_avail_asof_panel._prep` builds internally so
    the naive pick can be read off the same prepared frame without touching it.
    """
    if "_naive" in prep:
        return prep["_naive"]
    frame = prep["frame"]
    _, inv = np.unique(frame["code"].to_numpy(), return_inverse=True)
    key2 = inv.astype(np.int64) * _BIG + prep["pe_days"]
    order = np.argsort(key2, kind="stable")
    sorted_key = key2[order]
    block = sorted_key // _BIG
    starts = np.flatnonzero(np.r_[True, block[1:] != block[:-1]]).astype(np.int64)
    if not np.all(np.diff(sorted_key) >= 0):
        raise AssertionError("naive keys are not monotone")
    prep["_naive"] = {"key": sorted_key, "row": order, "starts": starts}
    return prep["_naive"]


def naive_slice(prep, asof, value_cols=()):
    """What a period_end join would have handed the factor builder at ``asof``."""
    idx = _naive_index(prep)
    days = np.int64(int(pd.Timestamp(asof).to_datetime64()
                        .astype("datetime64[D]").astype(np.int64)))
    targets = np.arange(len(prep["codes"]), dtype=np.int64) * _BIG + days
    pos = np.searchsorted(idx["key"], targets, side="right") - 1
    valid = pos >= idx["starts"]
    rows = idx["row"][np.where(valid, pos, 0)]
    out = pd.DataFrame({"asof": pd.Timestamp(asof),
                        "code": prep["codes"][valid],
                        "period_end": prep["period_end"][rows[valid]],
                        "avail_event": prep["avail_event"][rows[valid]],
                        "avail_tier": np.where(prep["fallback"][rows[valid]],
                                               _TIER_DEADLINE, _TIER_EVENT),
                        "lookahead": (prep["avail_event"][rows[valid]]
                                      > np.datetime64(pd.Timestamp(asof)))})
    for col in value_cols:
        out[col] = prep["vals"][col][rows[valid]]
    return out.reset_index(drop=True)


def degenerate_mask(roe, bps):
    """Rows a raw roe rank would put on top for arithmetic, not economics."""
    r = pd.to_numeric(pd.Series(roe), errors="coerce")
    b = pd.to_numeric(pd.Series(bps), errors="coerce")
    return ((r.abs() > ROE_DEGENERATE) | ((b.notna()) & (b <= 0))).to_numpy()


def rank_pct(values, mask=None):
    """Cross-sectional percentile in [0, 1]; masked rows stay NaN (disclosed)."""
    s = pd.to_numeric(pd.Series(values), errors="coerce")
    if mask is not None:
        s = s.where(~pd.Series(mask, index=s.index))
    return s.rank(pct=True, method="average").to_numpy()


def top_decile(values, mask=None, share=DECILE):
    """Codes in the top ``share`` of a descending ranking (masked rows dropped)."""
    s = pd.to_numeric(pd.Series(values), errors="coerce")
    if mask is not None:
        s = s.where(~pd.Series(mask, index=s.index))
    live = s.dropna()
    if live.empty:
        return np.array([], dtype=object)
    k = max(1, int(round(len(live) * share)))
    return live.sort_values(ascending=False, kind="stable").index[:k].to_numpy()


def _spearman(a, b):
    """Spearman rho on the pairwise-complete intersection (0 rows -> None)."""
    x = pd.to_numeric(pd.Series(a), errors="coerce")
    y = pd.to_numeric(pd.Series(b), errors="coerce")
    ok = x.notna() & y.notna()
    if int(ok.sum()) < 3:
        return None
    rx = x[ok].rank(method="average")
    ry = y[ok].rank(method="average")
    if rx.nunique() < 2 or ry.nunique() < 2:
        return None
    return float(rx.corr(ry))


# ------------------------------------------------------------------- product
def pit_factor_panel(prep, asofs, bps=None):
    """Strict as-of cross-sections with factors, rank percentile, confidence."""
    parts = []
    for d in asofs:
        frame = asof_slice(prep, d, FACTORS)
        if frame.empty:
            continue
        frame = frame.reset_index(drop=True)
        book = (bps.reindex(frame["code"]).to_numpy()
                if bps is not None else np.full(len(frame), np.nan))
        mask = degenerate_mask(frame[ROE].to_numpy(), book)
        frame["degenerate"] = mask
        frame["roe_rank_pct"] = rank_pct(frame[ROE].to_numpy(), mask)
        frame["np_yoy"] = pd.to_numeric(frame[NP], errors="coerce")
        frame["rev_yoy"] = pd.to_numeric(frame[REV], errors="coerce")
        parts.append(frame)
    if not parts:
        return pd.DataFrame()
    panel = pd.concat(parts, ignore_index=True)
    lookahead = (pd.to_datetime(panel["avail_event"])
                 > pd.to_datetime(panel["asof"]))
    if bool(lookahead.any()):
        raise AssertionError(f"{int(lookahead.sum())} panel rows read a report "
                             "before it was available")
    keep = ["asof", "code", "period_end", "avail_event", "avail_tier",
            "degenerate", ROE, "roe_rank_pct", "np_yoy", "rev_yoy"]
    return panel[keep]


def compare_to_naive(prep, asofs):
    """Strict vs naive cross-section at consumer resolution, per month-end."""
    rows = []
    for d in asofs:
        strict = asof_slice(prep, d, FACTORS).reset_index(drop=True)
        naive = naive_slice(prep, d, FACTORS).reset_index(drop=True)
        if strict.empty and naive.empty:
            continue
        s_idx = strict.set_index("code")
        n_idx = naive.set_index("code")
        common = s_idx.index.intersection(n_idx.index)
        differs = int((s_idx.loc[common, "period_end"]
                       != n_idx.loc[common, "period_end"]).sum())
        mask = degenerate_mask(s_idx[ROE].to_numpy(), np.full(len(s_idx), np.nan))
        s_live = s_idx[~mask]
        n_mask = degenerate_mask(n_idx[ROE].to_numpy(), np.full(len(n_idx), np.nan))
        n_live = n_idx[~n_mask]
        s_top = set(top_decile(s_live[ROE], None))
        n_top = set(top_decile(n_live[ROE], None))
        overlap = (len(s_top & n_top) / len(s_top)) if s_top else None
        rho = _spearman(s_live[ROE], n_live[ROE].reindex(s_live.index))
        rows.append({
            "asof": d.strftime("%Y-%m-%d"),
            "codes_strict": int(len(strict)),
            "codes_naive": int(len(naive)),
            "codes_common": int(len(common)),
            "codes_only_strict": int(len(strict) - len(common)),
            "report_differs": differs,
            "report_differs_share": (round(differs / len(common), 4)
                                     if len(common) else None),
            "deadline_bound_share": (round(float((strict["avail_tier"]
                                                  == _TIER_DEADLINE).mean()), 4)
                                     if len(strict) else None),
            "naive_lookahead_codes": int(naive["lookahead"].sum()),
            "naive_picks_that_move_rank": differs,
            "roe_spearman": (round(rho, 4) if rho is not None else None),
            "top_decile_overlap": (round(overlap, 4) if overlap is not None
                                   else None),
        })
    return rows


def _bps_series():
    """Book value per share, last stored value per (code, period_end)."""
    if not os.path.exists(INCOME):
        return None
    frame = pd.read_parquet(INCOME, columns=["code", "period_end", BPS])
    frame["code"] = frame["code"].astype(str).str.zfill(6)
    frame = frame.dropna(subset=[BPS]).drop_duplicates(["code", "period_end"],
                                                       keep="last")
    # index by code only: the panel needs a book-value plausibility screen, not
    # a period-exact join (the degenerate test is |roe|>200 OR bps<=0).
    return frame.groupby("code")[BPS].last()


def _summarise(rows):
    def med(key):
        vals = [r[key] for r in rows if r.get(key) is not None]
        return round(float(np.median(vals)), 4) if vals else None

    def worst(key, fn=max):
        vals = [r[key] for r in rows if r.get(key) is not None]
        return round(float(fn(vals)), 4) if vals else None

    return {
        "asofs": len(rows),
        "median_report_differs_share": med("report_differs_share"),
        "max_report_differs_share": worst("report_differs_share"),
        "median_roe_spearman": med("roe_spearman"),
        "min_roe_spearman": worst("roe_spearman", min),
        "median_top_decile_overlap": med("top_decile_overlap"),
        "min_top_decile_overlap": worst("top_decile_overlap", min),
        "median_naive_lookahead_codes": med("naive_lookahead_codes"),
        "max_naive_lookahead_codes": worst("naive_lookahead_codes"),
    }


# ----------------------------------------------------------------------- run
def run(log=print):
    avail_path = os.path.join(AVAIL_DIR, "income_avail_event.parquet")
    missing = [p for p in (avail_path, INCOME) if not os.path.exists(p)]
    if missing:
        log(f"MISSING INPUTS: {missing}")
        return 3
    try:
        avail = pd.read_parquet(avail_path)
        values = pd.read_parquet(INCOME)[["code", "period_end", *FACTORS]]
        prep = _prep(avail, values, FACTORS)
        bps = _bps_series()

        last_avail = pd.Timestamp(prep["avail_event"].max())
        end = min(pd.Timestamp(GRID_END), last_avail)
        asofs = month_ends(GRID_START, end)

        rows = compare_to_naive(prep, asofs)
        panel = pit_factor_panel(prep, asofs[-PANEL_WINDOW:], bps)
    except AssertionError as exc:
        log(f"MACHINERY: {exc}")
        return 2

    target = os.path.join(AVAIL_DIR, PANEL_NAME)
    if len(panel):
        os.makedirs(AVAIL_DIR, exist_ok=True)
        panel.to_parquet(target, index=False)

    window = rows[-PANEL_WINDOW:]
    receipts = {
        "ts": dt.datetime.now().astimezone().strftime("%Y-%m-%dT%H:%M:%S%z"),
        "audit": "monthly PIT fundamental factor panel + strict-vs-naive "
                 "comparison at month-end rebalancing resolution",
        "face": "income",
        "avail_rows": int(len(prep["frame"])),
        "avail_max_date": last_avail.strftime("%Y-%m-%d"),
        "grid": {"start": asofs[0].strftime("%Y-%m-%d"),
                 "end": asofs[-1].strftime("%Y-%m-%d"),
                 "points": len(asofs)},
        "definition": {
            "strict": "candidates avail_event<=asof; choice max period_end; "
                      "tie -> earliest availability (r1108 primitive)",
            "naive": "choice max period_end <= asof, availability ignored",
            "degenerate": f"|roe|>{ROE_DEGENERATE:g} or book value per share <=0; "
                          "excluded from roe_rank_pct and from the decile test "
                          "(r1107: do not drop them from the panel itself)",
            "top_decile": f"descending roe rank, top {DECILE:.0%} of live rows",
        },
        "window_summary": _summarise(window),
        "grid_summary": _summarise(rows),
        "worst_asofs": sorted(
            [r for r in rows if r.get("top_decile_overlap") is not None],
            key=lambda r: r["top_decile_overlap"])[:5],
        "panel_artifact": {
            "path": f"data/fund_statement_export/pit_avail/{PANEL_NAME}",
            "rows": int(len(panel)),
            "asofs": int(panel["asof"].nunique()) if len(panel) else 0,
            "window_start": panel["asof"].min().strftime("%Y-%m-%d")
                            if len(panel) else None,
            "columns": list(panel.columns) if len(panel) else [],
            "note": "gitignored data lane; regenerate with this script",
        },
        "grid_rows": rows,
    }
    os.makedirs(os.path.dirname(SUMMARY), exist_ok=True)
    tmp = SUMMARY + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(receipts, fh, ensure_ascii=False, indent=2, sort_keys=True)
        fh.write("\n")
    os.replace(tmp, SUMMARY)

    w = receipts["window_summary"]
    log(f"grid {len(asofs)} month-ends -> {len(rows)} compared; "
        f"window({len(window)}): median report_differs="
        f"{w['median_report_differs_share']} median roe rho="
        f"{w['median_roe_spearman']} min top-decile overlap="
        f"{w['min_top_decile_overlap']}")
    log(f"panel rows={len(panel)} asofs={receipts['panel_artifact']['asofs']}"
        f" -> {os.path.relpath(target, ROOT)}")
    log("wrote " + os.path.relpath(SUMMARY, ROOT))
    return 0


# ------------------------------------------------------------------ selftest
def selftest(log=print):
    fails = []

    def leg(name, fn):
        try:
            fn()
            log(f"  PASS {name}")
        except AssertionError as exc:
            fails.append(name)
            log(f"  FAIL {name}: {exc}")

    def _synthetic(lags=(0, 0, 0)):
        """3 codes x 2 periods; ``lags`` push each period's availability later."""
        codes = ["000001", "000002", "000003"]
        periods = ["2020-03-31", "2020-06-30"]
        avail, vals = [], []
        for i, code in enumerate(codes):
            for j, pe in enumerate(periods):
                base = pd.Timestamp(pe) + pd.Timedelta(days=30)
                avail.append({"code": code, "period_end": pe,
                              "avail_event": (base + pd.Timedelta(
                                  days=lags[i] if j else 0)).strftime("%Y-%m-%d"),
                              "fallback": False})
                vals.append({"code": code, "period_end": pe,
                             ROE: 10.0 + i + j, NP: 1e8 * (i + 1),
                             REV: 5e8 * (i + 1)})
        return _prep(pd.DataFrame(avail), pd.DataFrame(vals), FACTORS)

    def leg_strict_respects_availability():
        prep = _synthetic(lags=(0, 0, 200))
        frame = asof_slice(prep, "2020-07-10", FACTORS)
        row = frame[frame["code"] == "000003"].iloc[0]
        assert row["period_end"] == pd.Timestamp("2020-03-31"), row["period_end"]

    def leg_naive_reads_ahead():
        prep = _synthetic(lags=(0, 0, 200))
        frame = naive_slice(prep, "2020-07-10", FACTORS)
        row = frame[frame["code"] == "000003"].iloc[0]
        assert row["period_end"] == pd.Timestamp("2020-06-30")
        assert bool(row["lookahead"]) is True

    def leg_compare_counts_the_flip():
        prep = _synthetic(lags=(0, 0, 200))
        rows = compare_to_naive(prep, [pd.Timestamp("2020-08-10")])
        assert rows[0]["report_differs"] == 1, rows[0]
        assert rows[0]["naive_lookahead_codes"] == 1, rows[0]
        assert rows[0]["codes_only_strict"] == 0, rows[0]

    def leg_no_lag_is_a_fixed_point():
        prep = _synthetic()
        rows = compare_to_naive(prep, [pd.Timestamp("2020-08-10")])
        assert rows[0]["report_differs"] == 0, rows[0]
        assert rows[0]["roe_spearman"] == 1.0, rows[0]
        assert rows[0]["top_decile_overlap"] == 1.0, rows[0]

    def leg_degenerate_flag():
        mask = degenerate_mask([5.0, 250.0, -300.0, np.nan], [3.0, 2.0, 1.0, 0.0])
        assert mask.tolist() == [False, True, True, True], mask.tolist()

    def leg_rank_excludes_degenerate():
        vals = np.array([250.0, 12.0, 8.0, 3.0])
        mask = degenerate_mask(vals, [1.0, 1.0, 1.0, 1.0])
        pct = rank_pct(vals, mask)
        assert np.isnan(pct[0])
        assert pct[1] > pct[2] > pct[3], pct.tolist()

    def leg_top_decile_drops_masked():
        vals = np.array([250.0, 12.0, 8.0, 3.0, 1.0])
        mask = degenerate_mask(vals, [1.0] * 5)
        top = top_decile(vals, mask, share=0.25)
        assert list(top) == [1], list(top)         # 4 live rows -> k=1
        top = top_decile(vals, mask, share=0.5)
        assert list(top) == [1, 2], list(top)

    def leg_panel_is_lookahead_free():
        prep = _synthetic(lags=(0, 0, 200))
        panel = pit_factor_panel(prep, [pd.Timestamp("2020-07-10")])
        assert len(panel) == 3, len(panel)
        assert not bool((pd.to_datetime(panel["avail_event"])
                         > pd.to_datetime(panel["asof"])).any())
        assert set(panel["avail_tier"]) <= {_TIER_EVENT, _TIER_DEADLINE}

    def leg_spearman_handles_ties_and_nulls():
        assert _spearman([1.0, 2.0], [1.0, 2.0]) is None       # < 3 rows
        assert _spearman([1.0, 1.0, 1.0], [1.0, 2.0, 3.0]) is None
        rho = _spearman([1.0, 2.0, 3.0, np.nan], [3.0, 2.0, 1.0, 9.0])
        assert rho == -1.0, rho

    leg("strict respects availability", leg_strict_respects_availability)
    leg("naive reads ahead", leg_naive_reads_ahead)
    leg("comparison counts the flip", leg_compare_counts_the_flip)
    leg("no lag is a fixed point", leg_no_lag_is_a_fixed_point)
    leg("degenerate flag", leg_degenerate_flag)
    leg("rank excludes degenerate", leg_rank_excludes_degenerate)
    leg("top decile drops masked", leg_top_decile_drops_masked)
    leg("panel is lookahead free", leg_panel_is_lookahead_free)
    leg("spearman ties/nulls", leg_spearman_handles_ties_and_nulls)

    log(f"selftest {9 - len(fails)}/9 PASS")
    return 0 if not fails else 1


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    cmd = argv[0] if argv else "run"
    if cmd == "selftest":
        return selftest()
    if cmd == "run":
        return run()
    print(f"unknown subcommand {cmd!r}; expected run|selftest")
    return 2


if __name__ == "__main__":
    sys.exit(main())