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
    """Indices of the largest TOPK_SHARE share (never fewer than ``min_k``,
    never more than the sample), ties broken by code so both faces are ranked
    deterministically.

    The cap matters: without it a sample thinner than ``min_k`` reports
    turnover against names that do not exist (k=10 over a 2-name sample reads
    as 0.8 turnover between two IDENTICAL faces).
    """
    pairs = sorted(values.items(), key=lambda kv: (-kv[1], kv[0]))
    if not pairs:
        return set(), 0
    k = min(len(pairs), max(min_k, int(round(len(pairs) * TOPK_SHARE))))
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


def split_first_ok(first):
    """Separate rows whose availability is a REAL first announce from rows that
    only got the statutory-deadline fallback.

    The fallback rows are not wrong, they are unsupported: nothing in the source
    dates them. Keeping them means the measured effect is partly carried by
    rows nobody can verify, so the sensitivity face drops them outright instead
    of re-dating them -- re-dating would invent a stamp.
    """
    if "notice_status" not in first.columns:
        return first.iloc[0:0], {"missing_notice_status": int(len(first))}
    st = first["notice_status"]
    by_status = {str(k): int(v) for k, v in st.value_counts().items()}
    return first[st.eq("ok")], by_status


def drop_bias(rows_a, rows_b, dates, min_k=TOPK_MIN):
    """What a restriction REMOVES, not just how much it moves the answer.

    ``rows_b`` is a subset of ``rows_a``. If the removed names are random with
    respect to the factor, ``top_capture`` (share of the wide face's top decile
    that is made of dropped names) should equal ``dropped_share``. A ratio well
    above 1 means the restriction cuts the names that rank best, so the
    restricted face is a biased sample rather than a cleaner estimate.
    """
    sa = build_samples(rows_a, dates)
    sb = build_samples(rows_b, dates)
    per = []
    for d in dates:
        a, b = sa[d], sb[d]
        dropped = set(a) - set(b)
        rec = {"date": d, "n": len(a), "n_restricted": len(b),
               "dropped": len(dropped), "dropped_share": None,
               "top_capture": None, "over_rep": None}
        if dropped and a:
            ta, k = top_set(a, min_k)
            share = len(dropped) / len(a)
            cap = (len(dropped & ta) / k) if k else None
            rec["dropped_share"] = share
            rec["top_capture"] = cap
            rec["over_rep"] = (cap / share) if (cap is not None and share) else None
        per.append(rec)
    by_year = {}
    for r in per:
        by_year.setdefault(r["date"][:4], []).append(r)
    return {
        "per_date": per,
        "dropped_share": _agg(r["dropped_share"] for r in per),
        "top_capture": _agg(r["top_capture"] for r in per),
        "over_rep": _agg(r["over_rep"] for r in per),
        "by_year": {
            y: {"dropped_share_med": _agg(
                    r["dropped_share"] for r in rs).get("med"),
                "top_capture_med": _agg(
                    r["top_capture"] for r in rs).get("med"),
                "over_rep_med": _agg(r["over_rep"] for r in rs).get("med")}
            for y, rs in sorted(by_year.items())},
    }


def measure(rows_a, rows_b, dates, wdates, wmap, la="pit", lb="first"):
    """Every headline statistic for one pair of availability faces.

    Labels ride inside the keys so a second pair (``first`` vs ``first_ok``) can
    be published beside the primary pair without renaming published fields.
    """
    samp_a = build_samples(rows_a, dates)
    samp_b = build_samples(rows_b, dates)
    per_date = {d: compare(samp_a[d], samp_b[d]) for d in dates}
    by_year = {}
    for d, r in per_date.items():
        by_year.setdefault(d[:4], []).append(r)
    res = {
        f"rows_{la}": len(rows_a),
        f"rows_{lb}": len(rows_b),
        "coverage": {
            f"n_{la}": _agg(r["n_pit"] for r in per_date.values()),
            f"n_{lb}": _agg(r["n_first"] for r in per_date.values()),
            f"only_{la}": _agg(r["only_pit"] for r in per_date.values()),
            f"only_{lb}": _agg(r["only_first"] for r in per_date.values()),
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
            y: {"spearman_med": _agg(r["spearman"] for r in rs).get("med"),
                "turnover_med": _agg(
                    r["top_decile_turnover"] for r in rs).get("med"),
                f"only_{lb}_med": _agg(r["only_first"] for r in rs).get("med")}
            for y, rs in sorted(by_year.items())},
    }
    wa = build_samples(rows_a, wdates)
    wb = build_samples(rows_b, wdates)
    by_off = {}
    for d in wdates:
        r = compare(wa[d], wb[d])
        for _iso, off in wmap[d]:
            by_off.setdefault(off, []).append(r)
    res["window_probe"] = {
        str(off): {
            "probes": len(rs),
            f"n_{la}": _agg(x["n_pit"] for x in rs),
            f"n_{lb}": _agg(x["n_first"] for x in rs),
            f"only_{la}": _agg(x["only_pit"] for x in rs),
            f"only_{lb}": _agg(x["only_first"] for x in rs),
            "jaccard": _agg(x["jaccard"] for x in rs),
            "spearman": _agg(x["spearman"] for x in rs),
            "turnover": _agg(x["top_decile_turnover"] for x in rs),
        } for off, rs in sorted(by_off.items())
    }
    cv_a = coverage_curve(rows_a)
    cv_b = coverage_curve(rows_b)
    res["coverage_curve"] = {}
    for off in sorted({o for pairs in wmap.values() for _p, o in pairs}):
        fa, fb = [], []
        for d, pairs in wmap.items():
            for iso, o in pairs:
                if o != off:
                    continue
                ca = coverage_at(cv_a, iso, d)
                cb = coverage_at(cv_b, iso, d)
                if ca is not None and cb is not None:
                    fa.append(ca)
                    fb.append(cb)
        if not fa:
            continue
        res["coverage_curve"][str(off)] = {
            "probes": len(fa),
            f"frac_{la}": _agg(fa),
            f"frac_{lb}": _agg(fb),
            "med_gap": float(pd.Series(fa).median() - pd.Series(fb).median()),
        }
    return res


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
    first_ok, by_status = split_first_ok(first)
    fames = {
        "avail_pit": pit[key + ["avail_pit"]].rename(
            columns={"avail_pit": "avail"}),
        "avail_first": first[key + ["avail_first"]].rename(
            columns={"avail_first": "avail"}),
        "avail_first_ok": first_ok[key + ["avail_first"]].rename(
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
        "notice_ok_face": {
            "audit": "sensitivity face: only rows whose availability is a real "
                     "first announce (notice_status=='ok'); the "
                     "statutory-deadline fallback rows are dropped, not "
                     "re-dated",
            "rows_total": int(len(first)),
            "rows_ok": int(len(first_ok)),
            "rows_by_status": by_status,
        },
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
        wdates, wmap = window_dates(sorted(base["period_end"].unique()))
        f = measure(rows["avail_pit"], rows["avail_first"], dates,
                    wdates, wmap, "pit", "first")
        f["notice_ok_sensitivity"] = measure(
            rows["avail_first"], rows["avail_first_ok"], dates,
            wdates, wmap, "first", "first_ok")
        f["notice_ok_sensitivity"]["drop_selection"] = drop_bias(
            rows["avail_first"], rows["avail_first_ok"], dates)
        out["factors"][name] = f
        sens = f["notice_ok_sensitivity"]
        sel = sens["drop_selection"]
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
            f"vs {f['coverage_curve'].get('0', {}).get('frac_first', {}).get('med')}"
            f" | OK-ONLY turnover med "
            f"{sens['top_decile_turnover'].get('med')} spearman med "
            f"{sens['ordering']['spearman'].get('med')} "
            f"n_first_ok med {sens['coverage']['n_first_ok'].get('med')} "
            f"| drop_share {sel['dropped_share'].get('med')} "
            f"top_capture {sel['top_capture'].get('med')} "
            f"over_rep {sel['over_rep'].get('med')}")
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
    # 11. measure() carries the caller's labels into every keyed field, so the
    #     second pair can sit beside the primary one without a rename pass
    wdates, wmap = window_dates(sorted({"2025-03-31"}))
    m11 = measure(rows_pit, rows_first, dates, wdates, wmap, "first", "first_ok")
    checks.append("rows_first" in m11 and "rows_first_ok" in m11
                  and "only_first_ok" in m11["coverage"]
                  and "n_first_ok" in m11["coverage"]
                  and "frac_first_ok" in m11["coverage_curve"].get(
                      "0", {"frac_first_ok": None}))
    # 12. a pair of identical faces reports zero drift (the sign convention),
    #     including on a sample thinner than the top-k floor
    m12 = measure(rows_first, rows_first, dates, wdates, wmap,
                  "first", "first_ok")
    checks.append(m12["top_decile_turnover"].get("med") == 0.0
                  and m12["coverage"]["only_first_ok"].get("med") == 0
                  and m12["ordering"]["dates_below_0_95"] == 0)
    # 12b. the top-k floor never exceeds the sample itself
    ts12, k12 = top_set({"a": 1.0, "b": 2.0})
    checks.append(k12 == 2 and ts12 == {"a", "b"}
                  and top_set({}) == (set(), 0))
    # 13. the ok-only face drops fallback rows instead of re-dating them
    fake = pd.DataFrame({
        "code": ["000001", "000002", "000003"],
        "period_end": ["2024-12-31"] * 3,
        "avail_first": ["2025-02-10", "2025-04-30", "2025-04-30"],
        "notice_status": ["ok", "out_of_window", "absent"],
    })
    ok13, st13 = split_first_ok(fake)
    checks.append(list(ok13["code"]) == ["000001"]
                  and st13.get("ok") == 1 and st13.get("out_of_window") == 1
                  and st13.get("absent") == 1)
    # 14. a face with no status column yields an EMPTY ok-face, never all rows
    bare = fake[["code", "period_end", "avail_first"]]
    ok14, st14 = split_first_ok(bare)
    checks.append(len(ok14) == 0 and st14 == {"missing_notice_status": 3})
    # 15. drop_selection reports WHAT the restriction removes: dropping the
    #     single top name out of two is a 50% cut that captures 100% of the
    #     top decile -> over-representation 2x, not "no change"
    wide = [("000001", "2024-12-31", "2025-01-31", 1.0),
            ("000002", "2024-12-31", "2025-01-31", 2.0)]
    narrow = [wide[0]]
    db = drop_bias(wide, narrow, ["2025-02-28"], min_k=1)
    r15 = db["per_date"][0]
    checks.append(r15["dropped"] == 1 and r15["dropped_share"] == 0.5
                  and r15["top_capture"] == 1.0 and r15["over_rep"] == 2.0)
    # 16. a restriction that removes nothing reports no bias (None, not 0)
    db16 = drop_bias(wide, wide, ["2025-02-28"], min_k=1)
    checks.append(db16["per_date"][0]["dropped"] == 0
                  and db16["per_date"][0]["over_rep"] is None
                  and db16["over_rep"].get("n") == 0)
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