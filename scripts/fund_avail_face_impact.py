"""T27 measurement 2: does the availability repair change a HEADLINE factor
cell, and if so which one?

Context (r1097-r1102, bm-a):
  * ``avail_pit`` (published): min(latest-revision stamp, statutory deadline).
    Because the stored stamp is a revision date, this collapses a period onto
    the statutory date -- every code "learns" the quarter on the same day.
  * ``avail_first`` (this repair): per-period first announce, gated to the
    plausible disclosure window. Codes now arrive on different days.

r1099 measured the DATE shift. This module measures the consequence for the
thing a consumer actually builds: the cross-sectional sample and its ranking.

For every month-end from START to END and for each factor it records, on the
same panel and the same dates:
    n_pit / n_first          how many codes are in the sample under each face
    only_pit / only_first    composition delta
    jaccard                  sample overlap
    spearman                 rank agreement across the intersection
    top_decile_turnover     1 - |A_topk & B_topk| / k  (the practical question:
                             would the basket I would hold change?)
plus per-year medians so a regime change cannot hide inside one aggregate.

Read-only on every input face; writes results/fund_avail_face_impact.json.

Usage: python scripts/fund_avail_face_impact.py [run] [--factor roe]
       python scripts/fund_avail_face_impact.py selftest
Exit: 0 ok, 2 machinery failure.
"""
from __future__ import annotations

import datetime as dt
import bisect
import json
import os
import sys

import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
sys.path.insert(0, ROOT)

from update_fund_statements import DATA_DIR, statutory_deadline  # noqa: E402

OUT = os.path.join(ROOT, "results", "fund_avail_face_impact.json")
PIT_DIR = os.path.join(DATA_DIR, "pit_avail")

START = "2010-01-01"
END = "2026-09-30"
TOPK_SHARE = 0.10
TOPK_MIN = 10

FACTORS = {
    "roe": "\u51c0\u8d44\u4ea7\u6536\u76ca\u7387",
    "np_yoy": "\u51c0\u5229\u6da6-\u540c\u6bd4\u589e\u957f",
    "rev_yoy": "\u8425\u4e1a\u603b\u6536\u5165-\u540c\u6bd4\u589e\u957f",
    "gpm": "\u9500\u552e\u6bdb\u5229\u7387",
}


# ---------------------------------------------------------------- statistics
def spearman(a, b):
    """Pearson on average ranks; None when either side has no variance."""
    a = pd.Series(list(a), dtype="float64")
    b = pd.Series(list(b), dtype="float64")
    ok = a.notna() & b.notna()
    a, b = a[ok], b[ok]
    if len(a) < 3 or a.nunique() < 2 or b.nunique() < 2:
        return None
    ra, rb = a.rank(), b.rank()
    ra, rb = ra - ra.mean(), rb - rb.mean()
    den = (ra.pow(2).sum() ** 0.5) * (rb.pow(2).sum() ** 0.5)
    if not den:
        return None
    return float((ra * rb).sum() / den)


def top_set(values, min_k=TOPK_MIN):
    """Indices of the largest TOPK_SHARE share (never fewer than ``min_k``),
    ties broken by code so both faces are ranked deterministically."""
    pairs = sorted(values.items(), key=lambda kv: (-kv[1], kv[0]))
    k = max(min_k, int(round(len(pairs) * TOPK_SHARE)))
    return {c for c, _ in pairs[:k]}, k


# --------------------------------------------------------------- sampling
def month_ends(start=START, end=END):
    idx = pd.date_range(start=start, end=end, freq="ME")
    return [d.strftime("%Y-%m-%d") for d in idx]


def build_samples(rows, dates):
    """rows = iterable of (code, period_end, avail, value).

    For each date returns {code: value} using the LATEST period available as of
    that date. Rows are consumed once in availability order, so the sample is
    built incrementally instead of re-filtering the panel per date.
    """
    ordered = sorted(rows, key=lambda r: (r[2], r[1]))
    latest_pe = {}
    value = {}
    out = {}
    i = 0
    n = len(ordered)
    for d in dates:
        while i < n and ordered[i][2] <= d:
            code, pe, _av, val = ordered[i]
            if pe > latest_pe.get(code, ""):
                latest_pe[code] = pe
                value[code] = val
            i += 1
        out[d] = {c: value[c] for c in latest_pe
                  if value.get(c) is not None and value[c] == value[c]}
    return out


def compare(a, b, min_k=TOPK_MIN):
    """Compare two {code: value} samples."""
    sa, sb = set(a), set(b)
    inter = sa & sb
    ta, k = top_set(a, min_k)
    tb, _ = top_set(b, min_k)
    res = {
        "n_pit": len(sa),
        "n_first": len(sb),
        "only_pit": len(sa - sb),
        "only_first": len(sb - sa),
        "jaccard": (len(inter) / len(sa | sb)) if (sa | sb) else None,
        "spearman": spearman([a[c] for c in inter], [b[c] for c in inter]),
        "topk": k,
        "topk_overlap": len(ta & tb),
        "top_decile_turnover": (1.0 - len(ta & tb) / k) if k else None,
    }
    return res


def coverage_curve(rows):
    """period_end -> sorted availability dates, for the 'how much of THIS
    quarter has actually reported by day d' curve."""
    by_pe = {}
    for _code, pe, avail, _val in rows:
        by_pe.setdefault(pe, []).append(avail)
    return {pe: sorted(v) for pe, v in by_pe.items()}


def coverage_at(curve, period, date):
    lst = curve.get(period)
    if not lst:
        return None
    return bisect.bisect_right(lst, date) / len(lst)


def _agg(series):
    s = pd.Series([x for x in series if x is not None], dtype="float64")
    if s.empty:
        return {"n": 0}
    return {"n": int(len(s)), "med": float(s.median()),
            "p10": float(s.quantile(0.10)), "p90": float(s.quantile(0.90)),
            "mean": float(s.mean())}


def window_dates(periods, offsets=(-10, 0, 7, 15, 30)):
    """Probe dates around each period's statutory deadline.

    A month-end sample cannot separate the two faces: by the last day of a
    month every deadline of the quarter has already passed, so both faces have
    admitted the same rows. The separation lives INSIDE the disclosure window,
    which is exactly where an event study or a monthly rebalance that resolves
    to a day actually operates.
    """
    out = {}
    for p in periods:
        iso = str(p)[:10]
        deadline = pd.Timestamp(statutory_deadline(iso.replace("-", "")))
        for off in offsets:
            d = (deadline + pd.Timedelta(days=off)).strftime("%Y-%m-%d")
            out.setdefault(d, []).append((iso, off))
    return sorted(out), out


# ---------------------------------------------------------------------- run
def run(only_factor=None, log=print):
    pit_path = os.path.join(PIT_DIR, "income_avail.parquet")
    first_path = os.path.join(PIT_DIR, "income_avail_first.parquet")
    panel_path = os.path.join(DATA_DIR, "income_faces.parquet")
    for p in (pit_path, first_path, panel_path):
        if not os.path.exists(p):
            log(f"missing input: {os.path.relpath(p, ROOT)}")
            return 2
    panel = pd.read_parquet(panel_path)
    pit = pd.read_parquet(pit_path)
    first = pd.read_parquet(first_path)
    panel["code"] = panel["code"].astype(str).str.zfill(6)
    pit["code"] = pit["code"].astype(str).str.zfill(6)
    first["code"] = first["code"].astype(str).str.zfill(6)
    dates = month_ends()
    key = ["code", "period_end"]
    fames = {
        "avail_pit": pit[key + ["avail_pit"]].rename(
            columns={"avail_pit": "avail"}),
        "avail_first": first[key + ["avail_first"]].rename(
            columns={"avail_first": "avail"}),
    }
    out = {
        "ts": dt.datetime.now().astimezone().strftime("%Y-%m-%dT%H:%M:%S%z"),
        "audit": "T27 impact: does the first-announce face change the "
                 "cross-sectional factor cell (sample + ranking), not just "
                 "the dates?",
        "window": [dates[0], dates[-1]],
        "dates_n": len(dates),
        "topk_share": TOPK_SHARE,
        "topk_min": TOPK_MIN,
        "factors": {},
    }
    if int(first["notice_status"].eq("ok").sum()) == 0:
        log("avail_first face carries no notice_status==ok rows -- "
            "rebuild it first (fund_avail_notice.py build)")
        return 2
    for name, col in FACTORS.items():
        if only_factor and name != only_factor:
            continue
        if col not in panel.columns:
            out["factors"][name] = {"status": "missing_column"}
            continue
        base = panel[["code", "period_end", col]].rename(columns={col: "value"})
        rows = {}
        for fname, face in fames.items():
            m = face.merge(base, on=key, how="left")
            m["avail"] = pd.to_datetime(m["avail"], errors="coerce")
            m = m[m["avail"].notna() & m["value"].notna()]
            rows[fname] = list(zip(
                m["code"], m["period_end"],
                m["avail"].dt.strftime("%Y-%m-%d"), m["value"].astype(float)))
        samp_pit = build_samples(rows["avail_pit"], dates)
        samp_first = build_samples(rows["avail_first"], dates)
        per_date = {}
        for d in dates:
            per_date[d] = compare(samp_pit[d], samp_first[d])
        by_year = {}
        for d, r in per_date.items():
            by_year.setdefault(d[:4], []).append(r)
        out["factors"][name] = {
            "rows_pit": len(rows["avail_pit"]),
            "rows_first": len(rows["avail_first"]),
            "coverage": {
                "n_pit": _agg(r["n_pit"] for r in per_date.values()),
                "n_first": _agg(r["n_first"] for r in per_date.values()),
                "only_pit": _agg(r["only_pit"] for r in per_date.values()),
                "only_first": _agg(r["only_first"] for r in per_date.values()),
                "jaccard": _agg(r["jaccard"] for r in per_date.values()),
            },
            "ordering": {
                "spearman": _agg(r["spearman"] for r in per_date.values()),
                "dates_below_0_95": int(sum(
                    1 for r in per_date.values()
                    if r["spearman"] is not None and r["spearman"] < 0.95)),
            },
            "top_decile_turnover": _agg(
                r["top_decile_turnover"] for r in per_date.values()),
            "by_year": {
                y: {"spearman_med": _agg(
                        r["spearman"] for r in rs).get("med"),
                    "turnover_med": _agg(
                        r["top_decile_turnover"] for r in rs).get("med"),
                    "only_first_med": _agg(
                        r["only_first"] for r in rs).get("med")}
                for y, rs in sorted(by_year.items())},
        }
        wdates, wmap = window_dates(sorted(base["period_end"].unique()))
        wpit = build_samples(rows["avail_pit"], wdates)
        wfirst = build_samples(rows["avail_first"], wdates)
        by_off = {}
        for d in wdates:
            r = compare(wpit[d], wfirst[d])
            for _iso, off in wmap[d]:
                by_off.setdefault(off, []).append(r)
        f = out["factors"][name]
        f["window_probe"] = {
            str(off): {
                "probes": len(rs),
                "n_pit": _agg(x["n_pit"] for x in rs),
                "n_first": _agg(x["n_first"] for x in rs),
                "only_pit": _agg(x["only_pit"] for x in rs),
                "only_first": _agg(x["only_first"] for x in rs),
                "jaccard": _agg(x["jaccard"] for x in rs),
                "spearman": _agg(x["spearman"] for x in rs),
                "turnover": _agg(x["top_decile_turnover"] for x in rs),
            } for off, rs in sorted(by_off.items())}
        f["coverage_curve"] = {}
        cv_pit = coverage_curve(rows["avail_pit"])
        cv_first = coverage_curve(rows["avail_first"])
        for off in sorted({o for pairs in wmap.values() for _p, o in pairs}):
            pit, first = [], []
            for d, pairs in wmap.items():
                for iso, o in pairs:
                    if o != off:
                        continue
                    cp = coverage_at(cv_pit, iso, d)
                    cf = coverage_at(cv_first, iso, d)
                    if cp is not None and cf is not None:
                        pit.append(cp)
                        first.append(cf)
            if not pit:
                continue
            f["coverage_curve"][str(off)] = {
                "probes": len(pit),
                "frac_pit": _agg(pit),
                "frac_first": _agg(first),
                "med_gap": float(pd.Series(pit).median()
                                 - pd.Series(first).median()),
            }
        log(f"{name}: spearman med {f['ordering']['spearman'].get('med')} "
            f"| turnover med "
            f"{f['top_decile_turnover'].get('med')} "
            f"| n_pit med {f['coverage']['n_pit'].get('med')} "
            f"n_first med {f['coverage']['n_first'].get('med')} "
            f"| deadline-day n_pit "
            f"{f['window_probe'].get('0', {}).get('n_pit', {}).get('med')} "
            f"n_first "
            f"{f['window_probe'].get('0', {}).get('n_first', {}).get('med')} "
            f"| deadline coverage {f['coverage_curve'].get('0', {}).get('frac_pit', {}).get('med')} "
            f"vs {f['coverage_curve'].get('0', {}).get('frac_first', {}).get('med')}")
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    tmp = OUT + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1)
    os.replace(tmp, OUT)
    log("wrote " + os.path.relpath(OUT, ROOT))
    return 0


# ----------------------------------------------------------------- selftest
def selftest():
    checks = []
    dates = ["2025-01-31", "2025-02-28", "2025-03-31"]
    # code 1 available under both faces at 01-31; code 2 only under the
    # first-announce face until 03-31 (the repair moves it earlier).
    rows_pit = [("000001", "2024-12-31", "2025-01-31", 1.0),
                ("000002", "2024-12-31", "2025-03-31", 2.0)]
    rows_first = [("000001", "2024-12-31", "2025-01-31", 1.0),
                  ("000002", "2024-12-31", "2025-01-31", 2.0)]
    sp = build_samples(rows_pit, dates)
    sf = build_samples(rows_first, dates)
    # 1. nothing is available before the first date
    checks.append(sp["2025-01-31"].get("000001") == 1.0)
    # 2. the repair widens the sample at 02-28 and names the delta
    r = compare(sp["2025-02-28"], sf["2025-02-28"])
    checks.append(r["n_pit"] == 1 and r["n_first"] == 2
                  and r["only_first"] == 1 and r["only_pit"] == 0)
    # 3. one common name is too thin to rank -- reported as None, not 1.0
    checks.append(r["spearman"] is None)
    # 4. sample drift moves the basket, and the turnover is reported
    r4 = compare(sp["2025-02-28"], sf["2025-02-28"], min_k=1)
    checks.append(r4["top_decile_turnover"] == 1.0)
    # 5. by 03-31 the two samples agree again
    r5 = compare(sp["2025-03-31"], sf["2025-03-31"])
    checks.append(r5["jaccard"] == 1.0 and r5["only_first"] == 0)
    # 6. a code whose latest period is superseded keeps the newer value
    rows = [("000001", "2024-12-31", "2025-01-31", 1.0),
            ("000001", "2025-03-31", "2025-03-31", 9.0)]
    s6 = build_samples(rows, dates)
    checks.append(s6["2025-02-28"]["000001"] == 1.0
                  and s6["2025-03-31"]["000001"] == 9.0)
    # 7. NaN factor values never enter the sample (no fabricated zero)
    rows7 = [("000001", "2024-12-31", "2025-01-31", float("nan"))]
    checks.append(build_samples(rows7, dates)["2025-02-28"] == {})
    # 8. rank ties do not collapse the ranking
    checks.append(spearman([1, 1, 2], [1, 1, 2]) is not None)
    # 9. a constant factor has no rank correlation to report
    checks.append(spearman([1, 1, 1], [1, 2, 3]) is None)
    # 10. the top-k size is a floor plus a share, never fewer than requested
    ts, k = top_set({"a": 1.0, "b": 2.0}, min_k=1)
    checks.append(k == 1 and ts == {"b"})
    failed = [i for i, ok in enumerate(checks, 1) if not ok]
    print(f"fund_avail_face_impact selftest {len(checks) - len(failed)}"
          f"/{len(checks)} PASS")
    if failed:
        print("failed cases:", failed)
        return 1
    return 0


def main(argv=None):
    argv = argv or sys.argv[1:]
    cmd = argv[0] if argv else "run"
    if cmd == "selftest":
        return selftest()
    if cmd == "run":
        factor = None
        if "--factor" in argv:
            i = argv.index("--factor")
            if i + 1 < len(argv):
                factor = argv[i + 1]
        return run(factor)
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main())