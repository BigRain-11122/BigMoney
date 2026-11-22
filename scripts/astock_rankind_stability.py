"""Is the within-industry rank's long leg a property or a few stretches of luck?

r1945 (scripts/astock_resid_industry_neutral.py) found that ranking residuals *inside*
industries turns the only implementable leg of the A-share residual-reversal track from
-0.39%/yr into +3.76%/yr, but its per-rebalance t is 1.49 over 77 rebalances. Its own
digest named the next stone: split the sample into phases before anyone believes it.

This face is derived, not re-run: it consumes the per-rebalance rows the published
upstream face already carries (same quintile forward returns, same 8bp/side cost), so
the two faces cannot disagree about any single rebalance -- there is only one computation.

Four readings, all frozen before the run (see CRITERIA below):

  yearly        per-calendar-year annualised Q1 excess for the three arms
  phases        four contiguous blocks of ~19 rebalances, sign consistency
  sign-flip     p(|mean|) under 20,000 random sign flips, fixed seed
  drop-best-year  remove the single best year and re-measure: if the edge lives in one
                  year, the claim is a story about that year, not a property

Headline verdict (worst-flag-wins, declared here and not afterwards):

  ONE_YEAR_STORY   mean after dropping the best year <= 0
  PROPERTY         4/4 phases positive AND sign-flip p <= 0.05 AND drop-best mean > 0
  DIRECTION_ONLY   >=3/4 phases positive AND drop-best mean > 0 (but p > 0.05)
  NO_EDGE          otherwise

This is a census-derived reading: no prereg, no adoption, no strategy advice. The
boundary is unchanged from upstream -- one sample window, 77 rebalances, no live trading
constraints beyond the 8bp/side charge already inside the rows.

Usage:
    python scripts/astock_rankind_stability.py run
    python scripts/astock_rankind_stability.py check
    python scripts/astock_rankind_stability.py selftest
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from datetime import datetime, timezone

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import astock_resid_reversal_probe as base  # noqa: E402  (single source: maths)

UPSTREAM = os.path.join(ROOT, "results", "astock_resid_industry_neutral.json")
OUT = os.path.join(ROOT, "results", "astock_rankind_stability.json")

ARMS = ("resid", "ind", "rankind")
Q1_KEY = "q1_excess_%s"
LS_KEY = "ls_%s_net"

PHASES = 4
MIN_REBALANCES = 12
DRAWS = 20000
SEED = 20261122
P_FLOOR = 0.05
PHASE_MIN = 3

CRITERIA = {
    "phases": PHASES,
    "phase_positive_min": PHASE_MIN,
    "signflip_draws": DRAWS,
    "signflip_seed": SEED,
    "signflip_p_floor": P_FLOOR,
    "drop": "drop the single best calendar year, then re-measure the mean",
    "verdict_order": ["ONE_YEAR_STORY", "PROPERTY", "DIRECTION_ONLY", "NO_EDGE"],
    "note": "frozen in this file before the first run; no threshold was touched afterwards",
}


# ------------------------------------------------------------------ helpers
def sha256_of(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def year_of(date: str) -> str:
    return str(date)[:4]


def series(rows, key):
    """Return [(date, value)] keeping order; rows without the key are an error, not a skip."""
    out = []
    for r in rows:
        if key not in r:
            raise KeyError("row %s has no %r" % (r.get("date"), key))
        out.append((str(r["date"]), float(r[key])))
    return out


def _stat(values):
    """Reuse the published t formula instead of writing a second one.

    Upstream declines to report a mean below three draws; a phase of two rebalances
    still needs a number here, so the same formula is applied locally in that case only.
    """
    rows = [{"v": float(v)} for v in values]
    st = dict(base.summarise(rows, "v"))
    if "hit" not in st:  # upstream only reports hit once there are >= 3 draws
        arr = np.asarray(values, dtype=np.float64)
        arr = arr[np.isfinite(arr)]
        st["hit"] = float(np.mean(arr > 0)) if arr.size else None
        if st.get("mean") is None and arr.size:
            st["mean"] = float(arr.mean())
        if st.get("t") is None and arr.size >= 2:
            sd = float(arr.std(ddof=1))
            st["t"] = (st["mean"] / (sd / np.sqrt(arr.size))) if sd > 0 else None
    return st


def group_years(pairs):
    order, buckets = [], {}
    for date, value in pairs:
        y = year_of(date)
        if y not in buckets:
            buckets[y] = []
            order.append(y)
        buckets[y].append((date, value))
    out = []
    for y in order:
        vals = [v for _, v in buckets[y]]
        st = _stat(vals)
        out.append({
            "year": y,
            "n": len(vals),
            "first": buckets[y][0][0],
            "last": buckets[y][-1][0],
            "mean": st["mean"],
            "t": st["t"],
            "hit": st["hit"],
            "annual": base.compound(vals),
        })
    return out


def group_phases(pairs, phases: int = PHASES):
    n = len(pairs)
    phases = max(1, min(phases, n))
    if n < phases:
        raise ValueError("need at least %d rebalances, have %d" % (phases, n))
    size, rem = divmod(n, phases)
    out, start = [], 0
    for i in range(phases):
        take = size + (1 if i < rem else 0)
        chunk = pairs[start:start + take]
        vals = [v for _, v in chunk]
        st = _stat(vals)
        out.append({
            "phase": i + 1,
            "n": len(vals),
            "first": chunk[0][0],
            "last": chunk[-1][0],
            "mean": st["mean"],
            "t": st["t"],
            "annual": base.compound(vals),
            "positive": bool(st["mean"] > 0),
        })
        start += take
    return out


def signflip_p(values, draws: int = DRAWS, seed: int = SEED):
    """Two-sided p for the mean under random sign flips (valid when signs are exchangeable)."""
    arr = np.asarray(values, dtype=np.float64)
    if arr.size == 0 or not np.all(np.isfinite(arr)):
        return None
    observed = abs(float(arr.mean()))
    rng = np.random.default_rng(seed)
    hits = 0
    chunk = 2000
    left = draws
    while left > 0:
        take = min(chunk, left)
        signs = rng.choice([-1.0, 1.0], size=(take, arr.size))
        means = np.abs((signs * arr).mean(axis=1))
        hits += int(np.count_nonzero(means >= observed - 1e-15))
        left -= take
    return float(hits) / float(draws)


def drop_best_year(pairs):
    yearly = group_years(pairs)
    total = float(sum(v for _, v in pairs))
    if len(yearly) < 2:
        return {"year": None, "mean_without": None, "annual_without": None,
                "mean_all": _stat([v for _, v in pairs])["mean"],
                "share_of_sum": None}
    best = max(yearly, key=lambda r: r["mean"])
    best_vals = [v for date, v in pairs if year_of(date) == best["year"]]
    kept = [v for date, v in pairs if year_of(date) != best["year"]]
    return {
        "year": best["year"],
        "mean_all": _stat([v for _, v in pairs])["mean"],
        "mean_without": _stat(kept)["mean"] if kept else None,
        "annual_without": base.compound(kept) if kept else None,
        "share_of_sum": (float(sum(best_vals)) / total) if total else None,
    }


def verdict_for(positive_phases, total_phases, p, mean_after_drop):
    if mean_after_drop is None:
        return "INSUFFICIENT"
    if mean_after_drop <= 0:
        return "ONE_YEAR_STORY"
    if positive_phases == total_phases and p is not None and p <= P_FLOOR:
        return "PROPERTY"
    if positive_phases >= PHASE_MIN:
        return "DIRECTION_ONLY"
    return "NO_EDGE"


def arm_block(rows, arm):
    q1 = series(rows, Q1_KEY % arm)
    ls = series(rows, LS_KEY % arm)
    ph = group_phases(q1)
    pos = sum(1 for x in ph if x["positive"])
    q1_vals = [v for _, v in q1]
    ls_vals = [v for _, v in ls]
    drop = drop_best_year(q1)
    p_q1 = signflip_p(q1_vals)
    return {
        "q1_excess": {
            "summary": _stat(q1_vals),
            "annual": base.compound(q1_vals),
            "yearly": group_years(q1),
            "phases": ph,
            "positive_phases": pos,
            "phases_total": len(ph),
            "signflip_p": p_q1,
            "drop_best_year": drop,
            "verdict": verdict_for(pos, len(ph), p_q1, drop["mean_without"]),
        },
        "long_short": {
            "summary": _stat(ls_vals),
            "annual": base.compound(ls_vals),
            "yearly": group_years(ls),
            "phases": group_phases(ls),
            "positive_phases": sum(1 for x in group_phases(ls) if x["positive"]),
            "signflip_p": signflip_p(ls_vals),
        },
    }


def differential_block(rows, a: str = "rankind", b: str = "ind"):
    """The claim that matters: does ranking inside industries beat the industry regression?"""
    av = series(rows, Q1_KEY % a)
    bv = dict(series(rows, Q1_KEY % b))
    diff = [(d, v - bv[d]) for d, v in av]
    vals = [v for _, v in diff]
    ph = group_phases(diff)
    p = signflip_p(vals)
    drop = drop_best_year(diff)
    pos = sum(1 for x in ph if x["positive"])
    return {
        "pair": "%s-minus-%s" % (a, b),
        "summary": _stat(vals),
        "annual": base.compound(vals),
        "yearly": group_years(diff),
        "phases": ph,
        "positive_phases": pos,
        "phases_total": len(ph),
        "signflip_p": p,
        "drop_best_year": drop,
        "verdict": verdict_for(pos, len(ph), p, drop["mean_without"]),
    }


def build_report(upstream, upstream_path: str = UPSTREAM):
    rows = upstream.get("rows") or []
    if len(rows) < MIN_REBALANCES:
        raise SystemExit("NOT_ENOUGH_REBALANCES rows=%d (need >= %d)" % (len(rows), MIN_REBALANCES))
    arms = {arm: arm_block(rows, arm) for arm in ARMS}
    diff = differential_block(rows)
    headline = arms["rankind"]["q1_excess"]
    one_line = (
        "rankind long leg: mean %+.5f/rebalance (t=%.2f), %d/%d phases positive, "
        "sign-flip p=%.3f; drop-best-year(%s) -> mean %+.5f (annual %+.2f%%, the year "
        "carries %.0f%% of the summed excess) -> %s"
        % (
            headline["summary"]["mean"], headline["summary"]["t"] or 0.0,
            headline["positive_phases"], headline["phases_total"],
            headline["signflip_p"] if headline["signflip_p"] is not None else float("nan"),
            headline["drop_best_year"]["year"],
            headline["drop_best_year"]["mean_without"] or 0.0,
            100.0 * (headline["drop_best_year"]["annual_without"] or 0.0),
            100.0 * (headline["drop_best_year"]["share_of_sum"] or 0.0),
            headline["verdict"],
        )
    )
    return {
        "generated": datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds"),
        "evidence_cutoff": upstream.get("evidence_cutoff"),
        "machine": "bm-c",
        "kind": "census-derived",
        "prereg": None,
        "adoption": None,
        "upstream": {
            "path": os.path.relpath(upstream_path, ROOT).replace("\\", "/"),
            "sha256": sha256_of(upstream_path),
            "generated": upstream.get("generated"),
            "kind": upstream.get("kind"),
            "rebalances": len(rows),
            "verdict": upstream.get("verdict"),
        },
        "criteria": CRITERIA,
        "window": {
            "n": len(rows),
            "first": rows[0]["date"],
            "last": rows[-1]["date"],
            "hold_days": base.HOLD,
            "cost_one_side": base.COST_ONE_SIDE,
        },
        "arms": arms,
        "differential": diff,
        "headline": {
            "arm": "rankind",
            "read": "long_leg_q1_excess",
            "verdict": headline["verdict"],
            "one_line": one_line,
        },
        "boundaries": [
            "derived from one published sample window; the 77 rebalances are the same 77",
            "no phase-aware prereg: this answers whether the track deserves one, not a candidate",
            "portfolio construction is still quintile-of-eligible-universe, not a tradable book",
            "sign-flip p assumes signs are exchangeable; it tests the mean, not a trading rule",
            "ST/limit-up/limit-down and delisting are still unhandled exactly as in upstream",
        ],
    }


# ------------------------------------------------------------------ check
VOLATILE = {"generated", "upstream"}


def _flatten(obj, prefix=""):
    out = {}
    if isinstance(obj, dict):
        for k, v in obj.items():
            if not prefix and k in VOLATILE:
                continue
            out.update(_flatten(v, "%s.%s" % (prefix, k) if prefix else str(k)))
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            out.update(_flatten(v, "%s[%d]" % (prefix, i)))
    else:
        out[prefix] = obj
    return out


def _same(a, b):
    if isinstance(a, bool) or isinstance(b, bool):
        return a is b or a == b
    if isinstance(a, (int, float)) and isinstance(b, (int, float)):
        return abs(float(a) - float(b)) <= 1e-12
    return a == b


def check() -> int:
    if not os.path.exists(OUT):
        print("STALE face missing: %s" % os.path.relpath(OUT, ROOT))
        return 3
    with open(OUT, encoding="utf-8") as fh:
        published = json.load(fh)
    upstream = json.load(open(UPSTREAM, encoding="utf-8"))
    recorded_sha = (published.get("upstream") or {}).get("sha256")
    live_sha = sha256_of(UPSTREAM)
    if recorded_sha != live_sha:
        print("STALE upstream bytes changed (%s... -> %s...): re-run" % (
            str(recorded_sha)[:12], live_sha[:12]))
        return 3
    fresh = build_report(upstream)
    a, b = _flatten(published), _flatten(fresh)
    problems = []
    for key in sorted(set(a) | set(b)):
        if key not in a:
            problems.append("%s missing from published" % key)
        elif key not in b:
            problems.append("%s no longer produced" % key)
        elif not _same(a[key], b[key]):
            problems.append("%s published=%r recomputed=%r" % (key, a[key], b[key]))
    if problems:
        print("CHECK FAILED: %d field(s) drift" % len(problems))
        for p in problems[:10]:
            print("  " + p)
        return 3
    hl = fresh["headline"]
    print("CHECK OK %s | %s | %d fields re-derived | %s" % (
        hl["verdict"], fresh["differential"]["verdict"], len(b), hl["one_line"]))
    return 0


# ------------------------------------------------------------------ selftest
def selftest() -> int:
    legs = []
    tmp = os.path.join(ROOT, "results", "_r1946bmc_sha_probe.txt")
    with open(tmp, "wb") as fh:
        fh.write(b"abc")
    try:
        legs.append(("sha256 of known bytes", sha256_of(tmp) ==
                     hashlib.sha256(b"abc").hexdigest()))
    finally:
        os.remove(tmp)

    legs.append(("year_of keeps the calendar year", year_of("2026-11-20") == "2026"))

    rows = [
        {"date": "2020-07-06", "q1_excess_rankind": 0.01, "q1_excess_ind": 0.00},
        {"date": "2020-12-01", "q1_excess_rankind": 0.02, "q1_excess_ind": 0.01},
        {"date": "2021-03-01", "q1_excess_rankind": 0.03, "q1_excess_ind": 0.02},
        {"date": "2021-08-01", "q1_excess_rankind": 0.04, "q1_excess_ind": 0.03},
    ]
    pairs = series(rows, "q1_excess_rankind")
    legs.append(("series keeps order and values",
                 [v for _, v in pairs] == [0.01, 0.02, 0.03, 0.04]))

    missing = False
    try:
        series([{"date": "2020-01-01"}], "q1_excess_rankind")
    except KeyError:
        missing = True
    legs.append(("a row without the key is an error, not a silent skip", missing))

    yearly = group_years(pairs)
    legs.append(("yearly groups partition every rebalance",
                 sum(y["n"] for y in yearly) == len(pairs)))
    legs.append(("yearly is ordered ascending", [y["year"] for y in yearly] == ["2020", "2021"]))

    ph = group_phases(pairs, 2)
    legs.append(("phases cover the sample in order, sizes differ by <=1",
                 ph[0]["n"] + ph[1]["n"] == len(pairs) and abs(ph[0]["n"] - ph[1]["n"]) <= 1
                 and ph[0]["first"] == "2020-07-06" and ph[1]["last"] == "2021-08-01"))

    st = _stat([0.01, 0.02, 0.03])
    legs.append(("t-stat reuses the upstream formula",
                 abs(st["mean"] - 0.02) < 1e-12 and st["n"] == 3 and st["hit"] == 1.0))

    p_pos = signflip_p([0.01] * 40, draws=4000, seed=SEED)
    legs.append(("all-positive series: sign-flip p is ~0", p_pos is not None and p_pos <= 0.001))

    p_null = signflip_p([0.01, -0.01] * 20, draws=4000, seed=SEED)
    legs.append(("a mean-zero series: sign-flip p is ~0.5", p_null is not None and p_null > 0.4))

    legs.append(("sign-flip is deterministic under a fixed seed",
                 signflip_p([0.02] * 30, draws=2000, seed=SEED)
                 == signflip_p([0.02] * 30, draws=2000, seed=SEED)))

    drop = drop_best_year([("2020-07-06", 0.05), ("2020-12-01", 0.04),
                           ("2021-03-01", -0.01), ("2021-08-01", 0.00)])
    legs.append(("drop-best-year removes the right year and moves the mean down",
                 drop["year"] == "2020" and drop["mean_without"] < drop["mean_all"]))

    legs.append(("verdict mapping: one-year story wins over phase count",
                 verdict_for(4, 4, 0.001, -0.001) == "ONE_YEAR_STORY"))
    legs.append(("verdict mapping: property needs 4/4, p<=0.05 and survives the drop",
                 verdict_for(4, 4, 0.01, 0.001) == "PROPERTY"
                 and verdict_for(3, 4, 0.01, 0.001) == "DIRECTION_ONLY"
                 and verdict_for(2, 4, 0.01, 0.001) == "NO_EDGE"))

    diff_rows = [
        {"date": "2020-07-06", "q1_excess_rankind": 0.02, "q1_excess_ind": 0.01},
        {"date": "2020-12-01", "q1_excess_rankind": 0.03, "q1_excess_ind": 0.01},
    ]
    d = differential_block(diff_rows)
    legs.append(("differential subtracts the control arm rebalance for rebalance",
                 abs(d["summary"]["mean"] - 0.015) < 1e-12))

    # the guard has to be shown failing, or it is only a promise
    import contextlib
    import io as _io
    import json as _json
    import shutil
    import tempfile

    tmpdir = tempfile.mkdtemp(prefix="_r1946bmc_stab_")
    up = os.path.join(tmpdir, "up.json")
    out = os.path.join(tmpdir, "out.json")
    shutil.copyfile(UPSTREAM, up)
    if os.path.exists(OUT):
        shutil.copyfile(OUT, out)
    else:
        with open(out, "w", encoding="utf-8") as fh:
            _json.dump(build_report(_json.load(open(UPSTREAM, encoding="utf-8"))), fh)
    saved = (globals()["UPSTREAM"], globals()["OUT"])
    rc_clean = rc_stale = rc_fail = None
    text_stale = text_fail = ""
    try:
        globals()["UPSTREAM"], globals()["OUT"] = up, out
        with contextlib.redirect_stdout(_io.StringIO()):
            rc_clean = check()
        with open(up, "ab") as fh:
            fh.write(b"\n")
        buf = _io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc_stale = check()
        text_stale = buf.getvalue()
        shutil.copyfile(saved[0], up)
        face = _json.load(open(out, encoding="utf-8"))
        face["arms"]["rankind"]["q1_excess"]["summary"]["mean"] += 1e-6
        with open(out, "w", encoding="utf-8") as fh:
            _json.dump(face, fh)
        buf = _io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc_fail = check()
        text_fail = buf.getvalue()
    finally:
        globals()["UPSTREAM"], globals()["OUT"] = saved
        shutil.rmtree(tmpdir, ignore_errors=True)

    legs.append(("identical bytes re-derive clean", rc_clean == 0))
    legs.append(("one byte of upstream drift reads STALE, not clean",
                 rc_stale == 3 and "STALE" in text_stale))
    legs.append(("a published number that disagrees reads CHECK FAILED without STALE",
                 rc_fail == 3 and "CHECK FAILED" in text_fail and "STALE" not in text_fail))

    ok = sum(1 for _, good in legs if good)
    for name, good in legs:
        print("%s %s" % ("PASS" if good else "FAIL", name))
    print("selftest %d/%d %s" % (ok, len(legs), "PASS" if ok == len(legs) else "FAIL"))
    return 0 if ok == len(legs) else 3


# ------------------------------------------------------------------ main
def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("cmd", choices=["run", "check", "selftest"], nargs="?", default="run")
    ap.add_argument("--out", default=OUT)
    args = ap.parse_args(argv)

    if args.cmd == "selftest":
        return selftest()
    if args.cmd == "check":
        return check()

    upstream = json.load(open(UPSTREAM, encoding="utf-8"))
    report = build_report(upstream)
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as fh:
        json.dump(report, fh, ensure_ascii=False, indent=1, sort_keys=True)
        fh.write("\n")
    print(report["headline"]["one_line"])
    print("differential %s: mean %+.5f t=%s p=%.3f -> %s" % (
        report["differential"]["pair"],
        report["differential"]["summary"]["mean"],
        "%.2f" % report["differential"]["summary"]["t"]
        if report["differential"]["summary"]["t"] is not None else "None",
        report["differential"]["signflip_p"] or float("nan"),
        report["differential"]["verdict"]))
    for arm in ARMS:
        q = report["arms"][arm]["q1_excess"]
        print("%-8s annual %+7.2f%% | mean %+.5f t=%5.2f | phases %d/%d | p=%.3f | drop %s -> %s"
              % (arm,
                 100.0 * (q["annual"] or 0.0),
                 q["summary"]["mean"],
                 q["summary"]["t"] or 0.0,
                 q["positive_phases"], q["phases_total"],
                 q["signflip_p"] if q["signflip_p"] is not None else float("nan"),
                 q["drop_best_year"]["year"], q["verdict"]))
    print("-> %s" % os.path.relpath(args.out, ROOT).replace("\\", "/"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
