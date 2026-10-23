"""Cross-statement PIT factor panel -- accruals, the first factor that needs
three faces at once (r1112 bm-a).

WHY: r1108 built the as-of primitive, r1109 consumed it on income only, r1111
pushed the primitive to cashflow + balance and measured that the three
statements share only 5,239 codes (44.6% of income). A cross-statement factor
(accruals = profit that is not cash) can only be built on that intersection,
AND it needs one further condition nobody has measured: all three statements
must describe the SAME report period for a given code at a given date. This
script is the first consumer that requires that coherence, and it publishes how
much of the intersection survives it.

WHAT THIS DELIVERS (product, not prose):
    * ``coherent_triple()`` -- per as-of date, per code, the newest report that
      was public at that date in ALL THREE faces and whose period_end agrees
      across them (income / cashflow / balance).
    * ``accrual_factor()`` -- accrual = (net profit - operating cash flow) /
      total assets, plus cash quality = operating cash flow / net profit, a
      global cross-sectional rank and a PEER rank computed inside the
      period_end cohort. The peer rank exists because at any month-end the
      cross-section mixes annual and quarterly filers: a YTD accrual of a
      Q1 filer is not comparable with the annual accrual of a laggard, so the
      two ranks are both published and their disagreement is measured.
    * ``compare_to_naive()`` -- the same factor built the naive way (max
      period_end join, availability ignored) against the strict build, at the
      resolution a factor builder actually consumes (rank correlation and
      top-decile membership), plus how many codes reach back to a report that
      was not public yet.
    * results/fund_pit_crossface_factor.json -- the evidence face;
    * data/fund_statement_export/pit_avail/pit_crossface_monthly.parquet --
      the panel artifact (gitignored data lane, one command to regenerate).

DEFINITION (one reading, disclosed):
    strict pick = the r1108 primitive (``asof_slice``), never reimplemented;
    coherence = income.period_end == cashflow.period_end == balance.period_end;
    naive pick = ``naive_slice`` from fund_pit_factor_panel (max period_end,
    availability ignored), same coherence filter applied to it in fairness;
    degenerate = total assets <= 0 or missing (a ratio on that denominator is
    arithmetic, not economics -- carried as a flag, not dropped, r1107).

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
    BS_ASSETS,
    BS_LEV,
    CF_OPS,
    FACES,
    NP,
    ROE,
    _TIER_DEADLINE,
    _TIER_EVENT,
    _prep,
    asof_slice,
    month_ends,
)
from fund_pit_factor_panel import (  # noqa: E402  (single source for naive)
    DECILE,
    _spearman,
    naive_slice,
    rank_pct,
    top_decile,
)

SUMMARY = os.path.join(ROOT, "results", "fund_pit_crossface_factor.json")
PANEL_NAME = "pit_crossface_monthly.parquet"
GRID_START = "2010-01-31"
GRID_END = "2026-08-31"
PANEL_WINDOW = 24
FACES_USED = ("income", "cashflow", "balance")
INCOME_COLS = (ROE, NP)
CASH_COLS = (CF_OPS,)
BALANCE_COLS = (BS_ASSETS, BS_LEV)


# ------------------------------------------------------------------- product
def _coherent(left, mid, right, cols):
    """Join three as-of slices on code and keep only agreeing report periods."""
    frame = left.merge(mid, on="code", how="inner", suffixes=("", "_cf"))
    frame = frame.merge(right, on="code", how="inner", suffixes=("", "_bs"))
    same = ((frame["period_end"] == frame["period_end_cf"])
            & (frame["period_end"] == frame["period_end_bs"]))
    frame = frame[same].reset_index(drop=True)
    frame["period_end"] = pd.to_datetime(frame["period_end"])
    avail = pd.concat([frame["avail_event"], frame["avail_event_cf"],
                       frame["avail_event_bs"]], axis=1).max(axis=1)
    frame["avail_event"] = pd.to_datetime(avail)
    tiers = pd.concat([frame["avail_tier"], frame["avail_tier_cf"],
                       frame["avail_tier_bs"]], axis=1)
    tiers.columns = ["avail_tier_income", "avail_tier_cashflow",
                     "avail_tier_balance"]
    deadline = tiers == _TIER_DEADLINE
    frame["avail_tier"] = np.where(deadline.any(axis=1),
                                   _TIER_DEADLINE, _TIER_EVENT)
    # r1107 law is "weight, do not exclude", so one collapsed worst-face tier
    # is not enough: a consumer that wants to discount a deadline-bound
    # statement must know WHICH face forced the downgrade. Keep the per-face
    # tiers plus a count; the collapsed column stays for compatibility.
    for name in tiers.columns:
        frame[name] = tiers[name]
    frame["tier_deadline_faces"] = deadline.sum(axis=1).astype(int)
    keep = ["asof", "code", "period_end", "avail_event", "avail_tier",
            "tier_deadline_faces", "avail_tier_income", "avail_tier_cashflow",
            "avail_tier_balance", *cols]
    return frame[keep]


def _slices(preps, asof, naive=False):
    pick = naive_slice if naive else asof_slice
    return (pick(preps["income"], asof, INCOME_COLS),
            pick(preps["cashflow"], asof, CASH_COLS),
            pick(preps["balance"], asof, BALANCE_COLS))


def coherent_triple(preps, asof, naive=False):
    """Newest report public in all three faces with an agreeing period_end."""
    i_slice, c_slice, b_slice = _slices(preps, asof, naive=naive)
    if i_slice.empty or c_slice.empty or b_slice.empty:
        return pd.DataFrame()
    frame = _coherent(i_slice, c_slice, b_slice,
                      [NP, ROE, CF_OPS, BS_ASSETS, BS_LEV])
    if naive and "lookahead" in i_slice:
        ahead = {"income": i_slice, "cashflow": c_slice, "balance": b_slice}
        flags = pd.concat(
            [ahead[k].set_index("code")["lookahead"].rename(k + ":lookahead")
             for k in ahead], axis=1).any(axis=1)
        frame["lookahead"] = frame["code"].map(flags).fillna(False).astype(bool)
    return frame


def degenerate_mask(assets):
    """A ratio on a non-positive denominator is arithmetic, not economics."""
    a = pd.to_numeric(pd.Series(assets), errors="coerce")
    return (~a.notna() | (a <= 0)).to_numpy()


def accrual_of(frame):
    """Accrual ratio and cash quality on a coherent-triple frame."""
    if frame is None or frame.empty:
        return pd.DataFrame()
    np_val = pd.to_numeric(frame[NP], errors="coerce")
    cf = pd.to_numeric(frame[CF_OPS], errors="coerce")
    assets = pd.to_numeric(frame[BS_ASSETS], errors="coerce")
    out = frame.copy()
    out["accrual"] = (np_val - cf) / assets
    out["cash_quality"] = np.where(np_val > 0, cf / np_val, np.nan)
    out["degenerate"] = degenerate_mask(assets)
    return out


def add_ranks(frame):
    """Global rank and peer (same period_end cohort) rank of the accrual."""
    if frame.empty:
        return frame
    mask = frame["degenerate"].to_numpy()
    frame["accrual_rank_pct"] = rank_pct(frame["accrual"].to_numpy(), mask)
    peer = np.full(len(frame), np.nan)
    for _, idx in frame.groupby("period_end").groups.items():
        sub = frame.loc[idx]
        peer[frame.index.get_indexer(idx)] = rank_pct(
            sub["accrual"].to_numpy(), sub["degenerate"].to_numpy())
    frame["accrual_rank_pct_peer"] = peer
    frame["cohort_size"] = frame.groupby("period_end")["code"].transform("size")
    return frame


def build_panel(preps, asofs, coverage=None):
    """Strict as-of cross-statement factor panel over the given month-ends.

    Every row carries its own universe context (``codes_income_asof`` /
    ``codes_all_three_asof`` / ``coherent_share_of_income_asof``) so a
    downstream build cannot silently treat this intersection-only factor as if
    it covered the income face.
    """
    cov = {r["asof"]: r for r in (coverage or [])}
    parts = []
    for d in asofs:
        frame = coherent_triple(preps, d)
        if frame.empty:
            continue
        part = add_ranks(accrual_of(frame))
        c = cov.get(d.strftime("%Y-%m-%d"))
        if c is not None:
            part["codes_income_asof"] = int(c["codes_income"])
            part["codes_all_three_asof"] = int(c["codes_all_three_faces"])
            part["coherent_share_of_income_asof"] = c["coherent_share_of_income"]
        parts.append(part)
    if not parts:
        return pd.DataFrame()
    panel = pd.concat(parts, ignore_index=True)
    lookahead = pd.to_datetime(panel["avail_event"]) > pd.to_datetime(panel["asof"])
    if bool(lookahead.any()):
        raise AssertionError(f"{int(lookahead.sum())} panel rows read a report "
                             "before it was available")
    keep = ["asof", "code", "period_end", "avail_event", "avail_tier",
            "tier_deadline_faces", "avail_tier_income", "avail_tier_cashflow",
            "avail_tier_balance", "degenerate", "cohort_size", NP, CF_OPS,
            BS_ASSETS, BS_LEV, "accrual", "accrual_rank_pct",
            "accrual_rank_pct_peer", "cash_quality"]
    if parts and "codes_income_asof" in parts[0]:
        keep += ["codes_income_asof", "codes_all_three_asof",
                 "coherent_share_of_income_asof"]
    return panel[keep]


def coverage_rows(preps, asofs):
    """How much of each month-end survives the three-face coherence filter."""
    rows = []
    for d in asofs:
        i_slice, c_slice, b_slice = _slices(preps, d)
        all_three = (len(set(i_slice["code"]) & set(c_slice["code"])
                         & set(b_slice["code"])) if len(i_slice) else 0)
        coherent = int(len(coherent_triple(preps, d)))
        rows.append({
            "asof": d.strftime("%Y-%m-%d"),
            "codes_income": int(len(i_slice)),
            "codes_all_three_faces": int(all_three),
            "codes_coherent": coherent,
            "coherent_share_of_all_three": (round(coherent / all_three, 4)
                                            if all_three else None),
            # income is the widest face (11,757 codes vs the 5,239 three-face
            # intersection), so this is the number a downstream build would
            # get wrong if it assumed the panel covers the income universe.
            "coherent_share_of_income": (round(coherent / len(i_slice), 4)
                                         if len(i_slice) else None),
        })
    return rows


def compare_to_naive(preps, asofs):
    """Strict vs naive accrual factor at the ranking a consumer sees."""
    rows = []
    for d in asofs:
        strict = accrual_of(coherent_triple(preps, d))
        naive = accrual_of(coherent_triple(preps, d, naive=True))
        if strict.empty or naive.empty:
            continue
        s_idx = strict.set_index("code")
        n_idx = naive.set_index("code")
        common = s_idx.index.intersection(n_idx.index)
        if len(common) == 0:
            continue
        differs = int((s_idx.loc[common, "period_end"]
                       != n_idx.loc[common, "period_end"]).sum())
        s_live = s_idx[~s_idx["degenerate"]]
        n_live = n_idx[~n_idx["degenerate"]]
        rho = _spearman(s_live["accrual"], n_live["accrual"].reindex(s_live.index))
        s_top = set(top_decile(s_live["accrual"], None, share=DECILE))
        n_top = set(top_decile(n_live["accrual"], None, share=DECILE))
        overlap = (len(s_top & n_top) / len(s_top)) if s_top else None
        ahead = int(naive["lookahead"].sum()) if "lookahead" in naive else 0
        rows.append({
            "asof": d.strftime("%Y-%m-%d"),
            "codes_strict": int(len(strict)),
            "codes_naive": int(len(naive)),
            "codes_common": int(len(common)),
            "codes_only_strict": int(len(strict) - len(common)),
            "codes_only_naive": int(len(naive) - len(common)),
            "report_differs": differs,
            "report_differs_share": round(differs / len(common), 4),
            "naive_codes_reading_ahead": ahead,
            "accrual_spearman": round(rho, 4) if rho is not None else None,
            "top_decile_overlap": round(overlap, 4) if overlap is not None else None,
            "strict_deadline_bound_share": round(
                float((strict["avail_tier"] == _TIER_DEADLINE).mean()), 4),
        })
    return rows


def peer_vs_global(asofs_panel):
    """How far the peer (same period_end) rank departs from the global rank."""
    rows = []
    if asofs_panel.empty:
        return rows
    for asof, group in asofs_panel.groupby("asof"):
        g = group.dropna(subset=["accrual_rank_pct", "accrual_rank_pct_peer"])
        if len(g) < 3 or g["period_end"].nunique() < 2:
            continue
        rho = _spearman(g["accrual_rank_pct"], g["accrual_rank_pct_peer"])
        rows.append({
            "asof": pd.Timestamp(asof).strftime("%Y-%m-%d"),
            "codes": int(len(g)),
            "period_cohorts": int(g["period_end"].nunique()),
            "rank_spearman": round(rho, 4) if rho is not None else None,
        })
    return rows


def _median(rows, key):
    vals = [r[key] for r in rows if r.get(key) is not None]
    return round(float(np.median(vals)), 4) if vals else None


def _worst(rows, key, fn):
    vals = [r[key] for r in rows if r.get(key) is not None]
    return round(float(fn(vals)), 4) if vals else None


def _summarise(compared, coverage, peer):
    return {
        "asofs_compared": len(compared),
        "median_coherent_codes": _median(coverage, "codes_coherent"),
        "max_coherent_codes": _worst(coverage, "codes_coherent", max),
        "median_coherent_share_of_all_three": _median(
            coverage, "coherent_share_of_all_three"),
        "min_coherent_share_of_all_three": _worst(
            coverage, "coherent_share_of_all_three", min),
        "median_report_differs_share": _median(compared, "report_differs_share"),
        "max_report_differs_share": _worst(compared, "report_differs_share", max),
        "median_accrual_spearman": _median(compared, "accrual_spearman"),
        "min_accrual_spearman": _worst(compared, "accrual_spearman", min),
        "median_top_decile_overlap": _median(compared, "top_decile_overlap"),
        "min_top_decile_overlap": _worst(compared, "top_decile_overlap", min),
        "median_naive_codes_reading_ahead": _median(
            compared, "naive_codes_reading_ahead"),
        "max_naive_codes_reading_ahead": _worst(
            compared, "naive_codes_reading_ahead", max),
        "median_peer_vs_global_rank_spearman": _median(peer, "rank_spearman"),
        "min_peer_vs_global_rank_spearman": _worst(peer, "rank_spearman", min),
    }


# ----------------------------------------------------------------------- run
def tier_provenance(panel):
    """Which face makes a cross-statement row deadline-bound (r1107 weighting).

    Published because the collapsed ``avail_tier`` says only "some face was a
    deadline fallback"; a consumer that wants to discount cashflow less than
    income cannot recover that from a boolean.
    """
    if panel is None or panel.empty:
        return {}
    rows = len(panel)
    out = {
        "panel_rows": int(rows),
        "deadline_bound_share": round(
            float((panel["avail_tier"] == _TIER_DEADLINE).mean()), 4),
        "faces_deadline_mean": round(float(panel["tier_deadline_faces"].mean()), 4),
        "faces_deadline_max": int(panel["tier_deadline_faces"].max()),
    }
    for face in ("income", "cashflow", "balance"):
        col = f"avail_tier_{face}"
        out[f"{face}_deadline_share"] = round(
            float((panel[col] == _TIER_DEADLINE).mean()), 4)
        # The face that forced the downgrade when exactly one face did.
        out[f"{face}_sole_deadline_rows"] = int(
            ((panel[col] == _TIER_DEADLINE)
             & (panel["tier_deadline_faces"] == 1)).sum())
    return out


def universe_block(coverage):
    """The 5,239-code intersection as an explicit, quantified coverage fact."""
    if not coverage:
        return {}
    return {
        "median_codes_income": _median(coverage, "codes_income"),
        "median_codes_all_three": _median(coverage, "codes_all_three_faces"),
        "median_codes_coherent": _median(coverage, "codes_coherent"),
        "median_coherent_share_of_all_three": _median(
            coverage, "coherent_share_of_all_three"),
        "median_coherent_share_of_income": _median(
            coverage, "coherent_share_of_income"),
        "min_coherent_share_of_income": _worst(
            coverage, "coherent_share_of_income", min),
        "max_codes_all_three": _worst(coverage, "codes_all_three_faces", max),
        "max_codes_income": _worst(coverage, "codes_income", max),
    }


def load_preps(log=print):
    """Read the three availability faces + value columns once."""
    preps, missing = {}, []
    for name in FACES_USED:
        spec = FACES[name]
        avail_path = os.path.join(AVAIL_DIR, spec["avail"])
        for path in (avail_path, spec["values"]):
            if not os.path.exists(path):
                missing.append(os.path.relpath(path, ROOT))
        cols = {"income": INCOME_COLS, "cashflow": CASH_COLS,
                "balance": BALANCE_COLS}[name]
        if missing:
            continue
        preps[name] = _prep(pd.read_parquet(avail_path),
                            pd.read_parquet(spec["values"])[
                                ["code", "period_end", *cols]],
                            tuple(cols))
    if missing:
        return None, missing
    return preps, []


def run(log=print):
    preps, missing = load_preps(log=log)
    if missing:
        log(f"MISSING INPUTS: {missing}")
        return 3
    try:
        last_avail = min(pd.Timestamp(p["avail_event"].max())
                         for p in preps.values())
        end = min(pd.Timestamp(GRID_END), last_avail)
        asofs = month_ends(GRID_START, end)
        coverage = coverage_rows(preps, asofs)
        compared = compare_to_naive(preps, asofs)
        panel = build_panel(preps, asofs[-PANEL_WINDOW:], coverage)
        if len(panel) and "coherent_share_of_income_asof" not in panel:
            raise AssertionError("panel lost its universe coverage column; a "
                                 "consumer would silently assume income breadth")
        peer = peer_vs_global(panel)
    except AssertionError as exc:
        log(f"MACHINERY: {exc}")
        return 2

    target = os.path.join(AVAIL_DIR, PANEL_NAME)
    if len(panel):
        os.makedirs(AVAIL_DIR, exist_ok=True)
        panel.to_parquet(target, index=False)

    receipts = {
        "ts": dt.datetime.now().astimezone().strftime("%Y-%m-%dT%H:%M:%S%z"),
        "audit": "cross-statement as-of factor panel (accruals) with a "
                 "period-coherence filter and a strict-vs-naive ranking test",
        "evidence_cutoff": asofs[-1].strftime("%Y-%m-%d"),
        "faces": list(FACES_USED),
        "avail_rows": {k: int(len(v["frame"])) for k, v in preps.items()},
        "avail_max_date": {k: pd.Timestamp(v["avail_event"].max())
                           .strftime("%Y-%m-%d") for k, v in preps.items()},
        "grid": {"start": asofs[0].strftime("%Y-%m-%d"),
                 "end": asofs[-1].strftime("%Y-%m-%d"),
                 "points": len(asofs)},
        "definition": {
            "coherence": "income.period_end == cashflow.period_end == "
                         "balance.period_end == the newest period public at "
                         "the as-of date in all three faces",
            "accrual": "(net profit - operating cash flow) / total assets, both "
                       "flows as reported for the same period (YTD cumulative)",
            "cash_quality": "operating cash flow / net profit, only where net "
                            "profit > 0 (else NaN, disclosed not filled)",
            "peer_rank": "accrual rank inside the period_end cohort, published "
                         "because a month-end cross-section mixes annual and "
                         "quarterly filers",
            "degenerate": "total assets <= 0 or missing; excluded from ranks and "
                          "from the decile test, kept in the panel (r1107)",
            "naive": "max period_end <= asof per face, availability ignored, "
                     "then the same coherence filter",
        },
        "universe_coverage": universe_block(coverage),
        "availability_provenance": tier_provenance(panel),
        "grid_summary": _summarise(compared, coverage, peer),
        "window_summary_across_grid": _summarise(
            [r for r in compared if r["asof"] >= asofs[-PANEL_WINDOW:]
             .__getitem__(0).strftime("%Y-%m-%d")],
            coverage[-PANEL_WINDOW:], peer),
        "worst_asofs": sorted(
            [r for r in compared if r.get("top_decile_overlap") is not None],
            key=lambda r: r["top_decile_overlap"])[:5],
        "panel_artifact": {
            "path": f"data/fund_statement_export/pit_avail/{PANEL_NAME}",
            "rows": int(len(panel)),
            "asofs": int(panel["asof"].nunique()) if len(panel) else 0,
            "window_start": panel["asof"].min().strftime("%Y-%m-%d")
                            if len(panel) else None,
            "codes": int(panel["code"].nunique()) if len(panel) else 0,
            "columns": list(panel.columns) if len(panel) else [],
            "note": "gitignored data lane; regenerate with this script",
        },
        "coverage_grid": coverage,
        "compare_grid": compared,
        "peer_rank_grid": peer,
    }
    os.makedirs(os.path.dirname(SUMMARY), exist_ok=True)
    tmp = SUMMARY + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(receipts, fh, ensure_ascii=False, indent=2, sort_keys=True)
        fh.write("\n")
    os.replace(tmp, SUMMARY)

    g = receipts["grid_summary"]
    log(f"grid {len(asofs)} month-ends; coherent codes median "
        f"{g['median_coherent_codes']} (share {g['median_coherent_share_of_all_three']}); "
        f"accrual rho median {g['median_accrual_spearman']} min {g['min_accrual_spearman']}; "
        f"top-decile overlap median {g['median_top_decile_overlap']} min "
        f"{g['min_top_decile_overlap']}; peer-vs-global rank rho median "
        f"{g['median_peer_vs_global_rank_spearman']}")
    log(f"panel rows={len(panel)} asofs="
        f"{receipts['panel_artifact']['asofs']} codes="
        f"{receipts['panel_artifact']['codes']} -> "
        f"{os.path.relpath(target, ROOT)}")
    log("wrote " + os.path.relpath(SUMMARY, ROOT))
    u, t = receipts["universe_coverage"], receipts["availability_provenance"]
    log(f"universe: coherent share of income median {u['median_coherent_share_of_income']} "
        f"min {u['min_coherent_share_of_income']} (all-three {u['max_codes_all_three']} "
        f"vs income {u['max_codes_income']}); deadline-bound rows "
        f"{t['deadline_bound_share']} across {t['faces_deadline_mean']} faces mean "
        f"(sole-face rows i/c/b: {t['income_sole_deadline_rows']}/"
        f"{t['cashflow_sole_deadline_rows']}/{t['balance_sole_deadline_rows']})")
    return 0


# ------------------------------------------------------------------ selftest
def _fixture(lags=None):
    """Four codes x two periods across three faces.

    ``lags`` maps a face name to {(code, period): extra days of filing delay},
    so a test can lag exactly one statement (the coherence-breaking case) or
    all three (the case where the strict triple falls back to an older period
    while the naive one does not).
    """
    lags = lags or {}
    codes = ["000001", "000002", "000003", "000004"]
    periods = ["2020-03-31", "2020-06-30"]

    def build(face, cols, base, shift):
        per_face = lags.get(face, {})
        avail, vals = [], []
        for i, code in enumerate(codes):
            for j, pe in enumerate(periods):
                avail_day = (pd.Timestamp(pe) + pd.Timedelta(days=30)
                             + pd.Timedelta(days=per_face.get((code, pe), 0)))
                avail.append({"code": code, "period_end": pe,
                              "avail_event": avail_day.strftime("%Y-%m-%d"),
                              "fallback": False})
                row = {"code": code, "period_end": pe}
                for k, col in enumerate(cols):
                    row[col] = base + shift * i + (j + 1) * 10.0 + k
                vals.append(row)
        return _prep(pd.DataFrame(avail), pd.DataFrame(vals), tuple(cols))

    return {"income": build("income", INCOME_COLS, 100.0, 3.0),
            "cashflow": build("cashflow", CASH_COLS, 40.0, 1.0),
            "balance": build("balance", BALANCE_COLS, 1000.0, 100.0)}


def selftest(log=print):
    fails = []

    def leg(name, fn):
        try:
            fn()
            log(f"  PASS {name}")
        except AssertionError as exc:
            fails.append(name)
            log(f"  FAIL {name}: {exc}")

    def leg_coherent_keeps_agreeing_periods():
        frame = coherent_triple(_fixture(), "2020-09-10")
        assert len(frame) == 4, len(frame)
        assert (frame["period_end"] == pd.Timestamp("2020-06-30")).all()

    def leg_one_face_lag_breaks_coherence():
        # income still withholds H1 for 000001 at 2020-09-10 while cashflow and
        # balance already carry it -> the code has no coherent triple, so the
        # cross-statement factor simply cannot be built for it that day.
        preps = _fixture(lags={"income": {("000001", "2020-06-30"): 80}})
        frame = coherent_triple(preps, "2020-09-10")
        assert "000001" not in set(frame["code"]), set(frame["code"])
        assert len(frame) == 3, len(frame)

    def leg_coherent_tier_is_the_worst_face():
        preps = _fixture()
        fb = preps["cashflow"]["fallback"]
        preps["cashflow"]["fallback"] = np.ones(len(fb), dtype=bool)
        frame = coherent_triple(preps, "2020-09-10")
        assert set(frame["avail_tier"]) == {_TIER_DEADLINE}, set(frame["avail_tier"])

    def leg_accrual_arithmetic():
        frame = add_ranks(accrual_of(coherent_triple(_fixture(), "2020-09-10")))
        row = frame[frame["code"] == "000001"].iloc[0]
        expect = (row[NP] - row[CF_OPS]) / row[BS_ASSETS]
        assert abs(row["accrual"] - expect) < 1e-12, (row["accrual"], expect)

    def leg_degenerate_on_nonpositive_assets():
        preps = _fixture()
        preps["balance"]["vals"][BS_ASSETS] = np.zeros(
            len(preps["balance"]["vals"][BS_ASSETS]))
        frame = add_ranks(accrual_of(coherent_triple(preps, "2020-09-10")))
        assert bool(frame["degenerate"].all())
        assert frame["accrual_rank_pct"].isna().all()
        assert frame["cash_quality"].notna().any()   # cash quality still usable

    def leg_naive_reads_ahead_and_coherence_still_applies():
        preps = _fixture(lags={"income": {("000001", "2020-06-30"): 80}})
        strict = coherent_triple(preps, "2020-09-10")
        naive = coherent_triple(preps, "2020-09-10", naive=True)
        assert "000001" not in set(strict["code"])
        assert "000001" in set(naive["code"])
        row = naive[naive["code"] == "000001"].iloc[0]
        assert row["period_end"] == pd.Timestamp("2020-06-30")
        assert bool(row["lookahead"]) is True

    def leg_compare_counts_the_period_flip():
        # all three statements lag for 000001: the strict triple falls back to
        # Q1 for that code, the naive build reports H1 on the very same code.
        lags = {f: {("000001", "2020-06-30"): 90}
                for f in ("income", "cashflow", "balance")}
        rows = compare_to_naive(_fixture(lags=lags), [pd.Timestamp("2020-09-10")])
        assert rows[0]["codes_common"] == 4, rows[0]
        assert rows[0]["report_differs"] == 1, rows[0]
        assert rows[0]["naive_codes_reading_ahead"] == 1, rows[0]

    def leg_compare_counts_the_face_gap():
        # one face lagging does not flip a period, it removes a code from the
        # strict build -- a different damage shape that must be reported too.
        preps = _fixture(lags={"income": {("000001", "2020-06-30"): 80}})
        rows = compare_to_naive(preps, [pd.Timestamp("2020-09-10")])
        assert rows[0]["codes_only_naive"] == 1, rows[0]
        assert rows[0]["report_differs"] == 0, rows[0]

    def leg_no_lag_is_a_fixed_point():
        rows = compare_to_naive(_fixture(), [pd.Timestamp("2020-09-10")])
        assert rows[0]["report_differs"] == 0, rows[0]
        assert rows[0]["accrual_spearman"] == 1.0, rows[0]

    def leg_peer_rank_differs_when_cohorts_mix():
        # 000001 stuck on Q1 while the rest carry H1: the month-end cross-section
        # mixes cohorts, so a peer rank must exist and its cohorts must be sized.
        lags = {f: {("000001", "2020-06-30"): 200}
                for f in ("income", "cashflow", "balance")}
        frame = add_ranks(accrual_of(
            coherent_triple(_fixture(lags=lags), "2020-09-10")))
        assert frame["period_end"].nunique() == 2, frame["period_end"].unique()
        assert sorted(frame["cohort_size"].unique().tolist()) == [1, 3]

    def leg_panel_asserts_no_lookahead():
        panel = build_panel(_fixture(), [pd.Timestamp("2020-09-10")])
        assert len(panel) == 4, len(panel)
        assert (pd.to_datetime(panel["avail_event"])
                <= pd.to_datetime(panel["asof"])).all()

    def leg_empty_grid_is_safe():
        preps = _fixture()
        assert build_panel(preps, [pd.Timestamp("2000-01-31")]).empty
        assert compare_to_naive(preps, [pd.Timestamp("2000-01-31")]) == []
        assert peer_vs_global(pd.DataFrame()) == []

    def leg_tier_deadline_faces_names_the_face():
        preps = _fixture()
        fb = preps["balance"]["fallback"]
        preps["balance"]["fallback"] = np.ones(len(fb), dtype=bool)
        frame = coherent_triple(preps, "2020-09-10")
        assert (frame["tier_deadline_faces"] == 1).all(), frame["tier_deadline_faces"]
        assert set(frame["avail_tier_balance"]) == {_TIER_DEADLINE}
        assert set(frame["avail_tier_income"]) == {_TIER_EVENT}
        assert set(frame["avail_tier_cashflow"]) == {_TIER_EVENT}
        assert (frame["avail_tier"] == _TIER_DEADLINE).all()

    def leg_coverage_share_of_income_is_published():
        rows = coverage_rows(_fixture(), [pd.Timestamp("2020-09-10")])
        assert rows[0]["codes_income"] == 4, rows[0]
        assert rows[0]["codes_coherent"] == 4, rows[0]
        assert rows[0]["coherent_share_of_income"] == 1.0, rows[0]

    def leg_panel_rows_carry_universe_coverage():
        asof = pd.Timestamp("2020-09-10")
        rows = coverage_rows(_fixture(), [asof])
        panel = build_panel(_fixture(), [asof], rows)
        assert "coherent_share_of_income_asof" in panel.columns, panel.columns
        assert set(panel["codes_income_asof"]) == {4}
        assert set(panel["codes_all_three_asof"]) == {4}
        assert set(panel["coherent_share_of_income_asof"]) == {1.0}

    leg("coherent triple keeps only agreeing periods",
        leg_coherent_keeps_agreeing_periods)
    leg("a single lagging face breaks coherence", leg_one_face_lag_breaks_coherence)
    leg("tier of a triple is the worst face", leg_coherent_tier_is_the_worst_face)
    leg("tier provenance names the deadline face",
        leg_tier_deadline_faces_names_the_face)
    leg("coverage publishes share of the income face",
        leg_coverage_share_of_income_is_published)
    leg("panel rows carry their universe coverage",
        leg_panel_rows_carry_universe_coverage)
    leg("accrual arithmetic", leg_accrual_arithmetic)
    leg("degenerate flag on non-positive assets",
        leg_degenerate_on_nonpositive_assets)
    leg("naive joins read ahead but keep coherence",
        leg_naive_reads_ahead_and_coherence_still_applies)
    leg("strict-vs-naive counts the period flip",
        leg_compare_counts_the_period_flip)
    leg("strict-vs-naive counts the face gap", leg_compare_counts_the_face_gap)
    leg("no lag is a fixed point", leg_no_lag_is_a_fixed_point)
    leg("peer rank separates mixed cohorts", leg_peer_rank_differs_when_cohorts_mix)
    leg("panel asserts no lookahead", leg_panel_asserts_no_lookahead)
    leg("empty grid is safe", leg_empty_grid_is_safe)

    total = 14
    if fails:
        log(f"selftest {total - len(fails)}/{total} PASS -- FAILED: {fails}")
        return 1
    log(f"selftest {total}/{total} PASS")
    return 0


def main(argv):
    cmd = (argv[1] if len(argv) > 1 else "run").lower()
    if cmd == "run":
        return run()
    if cmd == "selftest":
        return selftest()
    print("usage: fund_pit_crossface_factor.py [run|selftest]")
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))