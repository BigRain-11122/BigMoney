"""Decompose the FILING-EVENT fallback rows by year x industry (r1105 bm-a).

WHY (r1104 left the question open)
    results/fund_avail_filing_event.json repaired the cashflow first-announce
    face (2010+ deadline fallback 91.7% -> 8.0%) by taking ``min`` over the
    three statements' in-window notice stamps of the same (code, period).
    What it did NOT answer: the rows that STILL fall back to the statutory
    deadline -- are they a random 8%, or a structured block (era, industry,
    earnings tail)? That decides whether a factor panel consuming this face
    needs a confidence column or can ignore the residual.

METHOD (pure function on committed faces, zero network, zero new data)
    inputs = data/fund_statement_export/pit_avail/<face>_avail_event.parquet
             (code, period_end, avail_event, source_face, deadline, fallback)
             data/fund_statement_export/income_faces.parquet
             (industry = 所处行业, 净资产收益率 for the earnings-tail check)
    industry(code) = modal non-null 所处行业 over that code's periods; ties
             broken by the latest period that carries a value (a company that
             re-classifies keeps its most recent label), then lexicographic.
    cells   = (period year, industry) per face -> n, fallback_n, fallback_share
             and lift = cell_share / face_share (1.0 = exactly the base rate).
    eras    = pre-2010 / 2010+ (r1104 found the defect is era-stationary only
             per face, never assume it is).
    tail    = income rows bucketed into roe deciles INSIDE their era, asking
             r1104's open question: do unverifiable stamps concentrate in the
             high-roe tail or is the concentration purely era/size?

READ, do not invent
    ``fallback=True`` means "no sibling statement proved an announcement date
    inside the disclosure window, so this row keeps the statutory deadline".
    That bound is never early (r1099/r1102), so it cannot leak future
    information; the only cost is pessimism (late arrival). Nothing here
    re-dates a row or writes a parquet -- this script measures and recommends.

Outputs
    results/fund_avail_fallback_decomp.json
    research/digests/DIGEST-20261024-bma-fallback-decomp.md
Subcommands: run | selftest
Exit codes: 0 ok, 2 machinery/panel missing.
"""
from __future__ import annotations

import datetime as dt
import json
import os
import sys

import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PIT = os.path.join(ROOT, "data", "fund_statement_export", "pit_avail")
INCOME = os.path.join(ROOT, "data", "fund_statement_export", "income_faces.parquet")
SUMMARY = os.path.join(ROOT, "results", "fund_avail_fallback_decomp.json")
DIGEST = os.path.join(
    ROOT, "research", "digests", "DIGEST-20261024-bma-fallback-decomp.md")

FACES = ("income", "cashflow", "balance")
IND_COL = "\u6240\u5904\u884c\u4e1a"          # 所处行业
ROE_COL = "\u51c0\u8d44\u4ea7\u6536\u76ca\u7387"  # 净资产收益率
ERA_SPLIT_YEAR = 2010


def era_of(year: int) -> str:
    return "pre2010" if year < ERA_SPLIT_YEAR else "2010+"


def modal_industry(panel: pd.DataFrame, ind_col: str = IND_COL,
                   code_col: str = "code", period_col: str = "period_end"):
    """code -> most frequent non-null industry; ties -> latest, then lexical."""
    sub = panel[[code_col, period_col, ind_col]].dropna(subset=[ind_col])
    if sub.empty:
        return {}
    sub = sub.copy()
    sub[period_col] = sub[period_col].astype(str)
    counts = (sub.groupby([code_col, ind_col])
                 .agg(n=(period_col, "size"), last=(period_col, "max"))
                 .reset_index()
                 .sort_values([code_col, "n", "last", ind_col],
                              ascending=[True, False, False, True]))
    first = counts.drop_duplicates(subset=[code_col], keep="first")
    return dict(zip(first[code_col].astype(str), first[ind_col]))


def cell_decomp(df: pd.DataFrame, keys, min_rows: int = 30):
    """fallback_n / share / lift per cell; lift is vs the frame's own base rate."""
    if df.empty:
        return []
    base_n = len(df)
    base_fb = int(df["fallback"].sum())
    base_share = base_fb / base_n
    out = []
    for kv, g in df.groupby(keys, dropna=False):
        kv = kv if isinstance(kv, tuple) else (kv,)
        n = len(g)
        fb = int(g["fallback"].sum())
        share = fb / n
        out.append({
            "key": [str(k) for k in kv],
            "n": n,
            "fallback_n": fb,
            "fallback_share": round(share, 4),
            "row_share": round(n / base_n, 4),
            "lift": round(share / base_share, 3) if base_share > 0 else None,
            "material": n >= min_rows,
        })
    out.sort(key=lambda r: (-(r["lift"] or 0), -r["n"]))
    return out


def roe_bucket_decomp(df: pd.DataFrame, n_buckets: int = 10):
    """Fallback share by roe decile inside each era (r1104's open question)."""
    d = df.dropna(subset=["roe"]).copy()
    if d.empty:
        return {}
    res = {}
    for era, g in d.groupby("era"):
        if len(g) < n_buckets * 5:
            res[era] = {"skipped": f"only {len(g)} rows with roe"}
            continue
        try:
            g["bucket"] = pd.qcut(g["roe"], n_buckets, labels=False,
                                  duplicates="drop")
        except ValueError as exc:  # degenerate roe column
            res[era] = {"skipped": f"qcut failed: {exc}"}
            continue
        rows = []
        for b, gg in g.groupby("bucket"):
            rows.append({
                "decile": int(b),
                "roe_min": round(float(gg["roe"].min()), 4),
                "roe_max": round(float(gg["roe"].max()), 4),
                "n": int(len(gg)),
                "fallback_share": round(float(gg["fallback"].mean()), 4),
            })
        if len(rows) < 2:  # constant roe -> qcut collapses every bucket
            res[era] = {"skipped": "degenerate roe (no decile spread)"}
            continue
        share = g["fallback"].mean()
        rows.sort(key=lambda r: r["decile"])
        res[era] = {
            "base_share": round(float(share), 4),
            "spread_top_minus_bottom": round(
                rows[-1]["fallback_share"] - rows[0]["fallback_share"], 4),
            "buckets": rows,
        }
    return res


def roe_bucket_controlled(df: pd.DataFrame, n_buckets: int = 10):
    """Same decile test but INSIDE (era, period month).

    ROE in this panel is cumulative-to-date, so a Q1 row's roe is ~1/4 of the
    same firm's annual roe. If the fallback rate also varies by report quarter,
    a plain roe decile ranking silently measures the quarter, not the firm.
    This block is the control that separates the two.
    """
    d = df.dropna(subset=["roe"]).copy()
    if d.empty:
        return {}
    d["month"] = d["period_end"].astype(str).str.slice(5, 7)
    out = {}
    for (era, month), g in d.groupby(["era", "month"]):
        if len(g) < n_buckets * 10:
            continue
        try:
            g = g.assign(bucket=pd.qcut(g["roe"], n_buckets, labels=False,
                                        duplicates="drop"))
        except ValueError:
            continue
        rows = [(int(b), float(gg["fallback"].mean()), int(len(gg)))
                for b, gg in g.groupby("bucket")]
        if len(rows) < 2:
            continue
        rows.sort()
        out[f"{era}-{month}"] = {
            "n": int(len(g)),
            "base_share": round(float(g["fallback"].mean()), 4),
            "bottom": round(rows[0][1], 4),
            "top": round(rows[-1][1], 4),
            "spread_top_minus_bottom": round(rows[-1][1] - rows[0][1], 4),
        }
    return out


def _load_faces():
    frames, missing = {}, []
    for face in FACES:
        p = os.path.join(PIT, f"{face}_avail_event.parquet")
        if not os.path.exists(p):
            missing.append(p)
            continue
        frames[face] = pd.read_parquet(p)
    return frames, missing


def build():
    if not os.path.exists(INCOME):
        raise SystemExit(f"panel missing: {INCOME}")
    frames, missing = _load_faces()
    if missing:
        raise SystemExit("avail_event parquet missing: " + ", ".join(missing))

    income = pd.read_parquet(INCOME)
    ind_map = modal_industry(income)
    # honesty guard: the source industry column is itself period-dependent, so a
    # pre-2010 "UNKNOWN x industry cell" can be a label hole rather than a fact.
    label_cov = (income.assign(year=income["period_end"].astype(str).str.slice(0, 4))
                       .groupby("year")[IND_COL]
                       .apply(lambda s: round(float(s.notna().mean()), 4))
                       .to_dict())
    roe = (income.dropna(subset=[ROE_COL])
                .assign(roe=lambda x: pd.to_numeric(x[ROE_COL], errors="coerce"))
                .dropna(subset=["roe"])[["code", "period_end", "roe"]])
    roe["code"] = roe["code"].astype(str)
    roe["period_end"] = roe["period_end"].astype(str)

    faces_out, totals = {}, {}
    for face, df in frames.items():
        d = df.copy()
        d["code"] = d["code"].astype(str)
        d["period_end"] = d["period_end"].astype(str)
        d["year"] = d["period_end"].str.slice(0, 4).astype(int)
        d["era"] = d["year"].map(era_of)
        d["industry"] = d["code"].map(ind_map).fillna("UNKNOWN")
        d["fallback"] = d["fallback"].astype(bool)

        by_year_ind = cell_decomp(d, ["year", "industry"])
        by_year = cell_decomp(d, ["year"])
        by_ind = cell_decomp(d, ["industry"])
        by_era = cell_decomp(d, ["era"])

        # what a live factor panel actually consumes: the last 8 quarters
        recent_cut = sorted(d["period_end"].unique())[-8] if len(d) else None
        recent = d[d["period_end"] >= recent_cut] if recent_cut else d.iloc[0:0]

        faces_out[face] = {
            "rows": int(len(d)),
            "fallback_n": int(d["fallback"].sum()),
            "fallback_share": round(float(d["fallback"].mean()), 4),
            "industry_coverage": round(float((d["industry"] != "UNKNOWN").mean()), 4),
            "by_era": by_era,
            "by_year": by_year,
            "heavy_industry_cells": [r for r in by_year_ind
                                     if r["material"] and r["key"][1] != "UNKNOWN"
                                     and (r["lift"] or 0) >= 1.5][:15],
            "light_industry_cells": [r for r in by_year_ind
                                     if r["material"] and r["key"][1] != "UNKNOWN"
                                     and (r["lift"] or 0) <= 0.5][:10],
            "unmapped_cells": [r for r in by_year_ind
                               if r["material"] and r["key"][1] == "UNKNOWN"
                               and (r["lift"] or 0) > 1.0][:8],
            "top_industry_lift": [r for r in by_ind if r["material"]][:10],
            "recent_quarters": {
                "from_period": recent_cut,
                "rows": int(len(recent)),
                "fallback_share": round(float(recent["fallback"].mean()), 4)
                if len(recent) else None,
                "fallback_share_era_2010plus": round(
                    float(recent[recent["era"] == "2010+"]
                          ["fallback"].mean()), 4)
                if len(recent[recent["era"] == "2010+"] ) else None,
            },
            "source_face_mix": {
                str(k): int(v) for k, v in
                d["source_face"].value_counts().head(6).items()
            },
        }
        totals[face] = d

    inc = totals["income"].merge(roe, on=["code", "period_end"], how="left")
    inc["fallback"] = inc["fallback"].astype(bool)
    tail = roe_bucket_decomp(inc)
    tail_ctl = roe_bucket_controlled(inc)

    # decision block: is the residual structured enough to need a flag?
    dec = {}
    for face, f in faces_out.items():
        recent_share = f["recent_quarters"]["fallback_share"]
        dec[face] = {
            "recent_quarters_fallback_share": recent_share,
            "overall_fallback_share": f["fallback_share"],
            "needs_row_flag": bool(recent_share is not None and recent_share >= 0.05),
        }
    out = {
        "ts": dt.datetime.now().astimezone().strftime("%Y-%m-%dT%H:%M:%S%z"),
        "audit": ("fallback (deadline-bounded) rows of the cross-statement "
                  "filing-event availability face, decomposed by year x industry "
                  "and by era-internal roe decile; measurement only, no re-dating, "
                  "no parquet rewrite"),
        "inputs": {
            "avail_event": [f"data/fund_statement_export/pit_avail/{f}_avail_event.parquet"
                            for f in FACES],
            "industry_source": "data/fund_statement_export/income_faces.parquet :: "
                               + IND_COL,
            "industry_codes_mapped": len(ind_map),
            "industry_source_label_coverage_by_year": dict(
                sorted(label_cov.items())),
        },
        "era_split_year": ERA_SPLIT_YEAR,
        "faces": faces_out,
        "earnings_tail": tail,
        "earnings_tail_controlled": tail_ctl,
        "decision": dec,
        "recommendation": (
            "keep the never-early deadline bound as is; publish the existing "
            "`fallback` boolean as the confidence column instead of inventing a "
            "new score -- it is exact (row-level), already materialised in every "
            "<face>_avail_event.parquet, and needs no threshold. Only rows in the "
            "recent-quarter block with fallback=True should be down-weighted by "
            "any consumer that needs true filing dates."),
    }
    return out


def write_outputs(out):
    os.makedirs(os.path.dirname(SUMMARY), exist_ok=True)
    with open(SUMMARY, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1)
        fh.write("\n")
    os.makedirs(os.path.dirname(DIGEST), exist_ok=True)
    lines = ["# DIGEST 2026-10-24 (bm-a r1105) -- who is still on the deadline bound",
             "",
             "Face = cross-statement filing-event availability "
             "(results/fund_avail_filing_event.json). Question: the residual "
             "rows that still fall back to the statutory deadline -- random, "
             "or structured by era / industry / earnings tail?",
             ""]
    for face, f in out["faces"].items():
        lines.append(f"## {face}: {f['fallback_n']}/{f['rows']} rows fall back "
                     f"({f['fallback_share']:.1%}); industry mapped "
                     f"{f['industry_coverage']:.1%}")
        for e in f["by_era"]:
            lines.append(f"- era {e['key'][0]}: {e['fallback_n']}/{e['n']} = "
                         f"{e['fallback_share']:.1%} (lift {e['lift']})")
        heavy = f["heavy_industry_cells"][:5]
        if heavy:
            lines.append("- heaviest year x industry cells (lift>=1.5, n>=30): "
                         + "; ".join(f"{r['key'][0]} {r['key'][1]} "
                                     f"{r['fallback_share']:.0%} of {r['n']} "
                                     f"(lift {r['lift']})" for r in heavy))
        rq = f["recent_quarters"]
        lines.append(f"- consumable window (last 8 periods, from "
                     f"{rq['from_period']}): {rq['rows']} rows, fallback "
                     f"{rq['fallback_share']}")
        unm = f.get("unmapped_cells") or []
        if unm:
            lines.append("- NOT industry structure: " + "; ".join(
                f"{r['key'][0]} unmapped {r['fallback_share']:.0%} of {r['n']} "
                f"(lift {r['lift']})" for r in unm[:4])
                + " -- the source industry column is only "
                + f"{f['industry_coverage']:.0%} populated for this face, so "
                  "these cells measure the LABEL HOLE, not a sector effect")
        lines.append("")
    lines.append("## earnings tail (income, roe deciles inside era)")
    for era, blk in out["earnings_tail"].items():
        if "skipped" in blk:
            lines.append(f"- {era}: skipped ({blk['skipped']})")
            continue
        lines.append(f"- {era}: base {blk['base_share']:.1%}, top-vs-bottom "
                     f"decile spread {blk['spread_top_minus_bottom']:+.1%}")
        b = blk["buckets"]
        lines.append(f"  - bottom decile (roe {b[0]['roe_min']}..{b[0]['roe_max']}%): "
                     f"{b[0]['fallback_share']:.1%} of {b[0]['n']}")
        lines.append(f"  - top decile (roe {b[-1]['roe_min']}..{b[-1]['roe_max']}%): "
                     f"{b[-1]['fallback_share']:.1%} of {b[-1]['n']}")
    lines.append("")
    lines.append("## earnings tail controlled for report quarter (income)")
    if not out["earnings_tail_controlled"]:
        lines.append("- no (era, quarter) cell had enough rows")
    for k, v in sorted(out["earnings_tail_controlled"].items()):
        lines.append(f"- {k}: n={v['n']}, base {v['base_share']:.1%}, "
                     f"bottom {v['bottom']:.1%} -> top {v['top']:.1%} "
                     f"(spread {v['spread_top_minus_bottom']:+.1%})")
    lines.append("")
    lines.append("## decision")
    for face, d in out["decision"].items():
        lines.append(f"- {face}: recent window fallback "
                     f"{d['recent_quarters_fallback_share']} -> "
                     f"needs_row_flag={d['needs_row_flag']}")
    lines.append("")
    lines.append(out["recommendation"])
    lines.append("")
    with open(DIGEST, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))


def selftest():
    ok = True

    def check(name, cond, detail=""):
        nonlocal ok
        print(("PASS " if cond else "FAIL ") + name + (f" | {detail}" if detail else ""))
        ok = ok and bool(cond)

    # 1. modal industry: majority wins over recency
    p = pd.DataFrame({"code": ["A", "A", "A", "B"],
                      "period_end": ["2020-03-31", "2020-06-30", "2020-09-30", "2020-03-31"],
                      IND_COL: ["X", "X", "Y", "Z"]})
    m = modal_industry(p)
    check("modal_industry majority", m["A"] == "X", str(m))
    # 2. tie -> latest period wins
    p2 = pd.DataFrame({"code": ["C", "C"], "period_end": ["2020-03-31", "2021-03-31"],
                       IND_COL: ["OLD", "NEW"]})
    check("modal_industry tie->latest", modal_industry(p2)["C"] == "NEW")
    # 3. nulls ignored
    p3 = pd.DataFrame({"code": ["D", "D"], "period_end": ["2020-03-31", "2020-06-30"],
                       IND_COL: [None, "Q"]})
    check("modal_industry nulls", modal_industry(p3)["D"] == "Q")
    # 4/5. cell decomp arithmetic + lift
    d = pd.DataFrame({"year": [2020] * 4 + [2021] * 4,
                      "industry": ["A"] * 3 + ["B"] + ["A"] * 4,
                      "fallback": [True, True, False, False, False, False, False, False]})
    cells = cell_decomp(d, ["year", "industry"])
    a20 = next(r for r in cells if r["key"] == ["2020", "A"])
    check("cell n/share", a20["n"] == 3 and abs(a20["fallback_share"] - 0.667) < 1e-3,
          str(a20))
    check("lift vs base", abs((a20["lift"] or 0) - 2.667) < 0.01, str(a20["lift"]))
    check("cell coverage sums", sum(r["n"] for r in cells) == len(d))
    # 6. roe buckets: monotone construction is detected
    rng = pd.DataFrame({"roe": list(range(100)), "era": ["2010+"] * 100,
                        "fallback": [x >= 90 for x in range(100)]})
    rb = roe_bucket_decomp(rng, n_buckets=10)
    check("roe decile count", len(rb["2010+"]["buckets"]) == 10)
    check("roe top-decile heavier",
          rb["2010+"]["buckets"][-1]["fallback_share"] >
          rb["2010+"]["buckets"][0]["fallback_share"],
          str(rb["2010+"]["spread_top_minus_bottom"]))
    # 7. degenerate roe column skips honestly
    flat = pd.DataFrame({"roe": [1.0] * 60, "era": ["2010+"] * 60,
                         "fallback": [False] * 60})
    check("degenerate roe skipped", "skipped" in roe_bucket_decomp(flat)["2010+"])
    # 8. era split
    check("era split", era_of(2009) == "pre2010" and era_of(2010) == "2010+")
    # 9. empty frame -> empty, no crash
    check("empty decomp", cell_decomp(pd.DataFrame(
        {"fallback": pd.Series(dtype=bool)}), ["era"]) == [])
    print(f"\nselftest {'ALL PASS' if ok else 'FAILED'}")
    return 0 if ok else 1


def main(argv):
    cmd = (argv[1] if len(argv) > 1 else "run").lower()
    if cmd == "selftest":
        return selftest()
    if cmd != "run":
        print("usage: fund_avail_fallback_decomp.py [run|selftest]")
        return 2
    out = build()
    write_outputs(out)
    for face, f in out["faces"].items():
        print(f"{face}: rows={f['rows']} fallback={f['fallback_n']} "
              f"({f['fallback_share']:.2%}) recent={f['recent_quarters']['fallback_share']}")
    print(f"wrote {SUMMARY}")
    print(f"wrote {DIGEST}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))