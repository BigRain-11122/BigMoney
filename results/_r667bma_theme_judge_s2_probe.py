"""THEME_JUDGE_P1 s2 pre-freeze probe (r667 bm-a, T-2026-10-04-167-P1).

Deterministic, zero-network, zero-engine probe facts for the prereg freeze:
  leg 1  census sha16 byte assert (51b1b8226afc74b1)
  leg 2  dedup canon counts (identity=(norm6, ignition_date), keep-first
         in (norm6, ign, raw) sort => bare form wins ties)
  leg 3  E28 cluster strata recount AFTER dedup (same-day >=10 = CLUSTER)
  leg 4  panel tails census + truncation edge counts (cutoff 2026-09-22)
  leg 5  twin-file price identity on overlap (dedup is counting-only)
  leg 6  D6 admission proxy: pooled same-window B&H daily returns (probe
         sleeve, levels not the judged system) vs REG6 members, |corr| list

Selftest: hermetic synthetic asserts for dedup canon + strata split.
No judged-cell Sharpe is computed here (freeze discipline: predictions are
written before any judged run; D6 proxy is the fund-family probe precedent).
"""
import hashlib
import json
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, "scripts")
sys.path.insert(0, "results")

V03 = "results/theme_ring/theme_events_v03_algorithmic.json"
OUT = "results/theme_judge_p1_d6_probe.json"
DAILY = "data/daily"
CUTOFF = "2026-09-22"
SHA16_EXPECT = "51b1b8226afc74b1"


def sha16_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()[:16]


def norm6(code):
    return code[2:] if code[:2] in ("sh", "sz") else code


def code_to_file(code):
    """r666 probe canon verbatim (frozen normalization)."""
    c = code[2:] if code[:2] in ("sh", "sz") else code
    if c.startswith("1"):
        return f"sz{c}.csv"
    if c.startswith("5"):
        return f"sh{c}.csv"
    return f"UNKNOWN-{code}.csv"


def load_close_truncated(code):
    fn = code_to_file(code)
    path = os.path.join(DAILY, fn)
    if not os.path.exists(path):
        return None, fn
    df = pd.read_csv(path, usecols=["date", "close"])
    df = df[df["date"] <= CUTOFF]
    return df, fn


def dedup(episodes):
    """Identity=(norm6, ignition_date); keep first in deterministic sort."""
    rows = sorted(episodes, key=lambda e: (norm6(e["code"]),
                                          e["ignition_date"], e["code"]))
    seen, kept, dropped = set(), [], []
    for e in rows:
        key = (norm6(e["code"]), e["ignition_date"])
        if key in seen:
            dropped.append(e)
            continue
        seen.add(key)
        kept.append(e)
    return kept, dropped


def strata(kept):
    from collections import Counter
    byday = Counter(e["ignition_date"] for e in kept)
    cl = [e for e in kept if byday[e["ignition_date"]] >= 10]
    so = [e for e in kept if byday[e["ignition_date"]] < 10]
    return byday, cl, so


def bh_pool_probe(kept):
    """Pooled same-window B&H daily returns (D6 probe sleeve, NOT judged)."""
    sys_eq = {}
    drop = {"no_ignition_bar": 0, "window_lt2": 0}
    for e in kept:
        df, fn = load_close_truncated(e["code"])
        if df is None:
            drop["no_ignition_bar"] += 1
            continue
        dates = df["date"].values
        idx = np.nonzero(dates == e["ignition_date"])[0]
        if len(idx) == 0:
            drop["no_ignition_bar"] += 1
            continue
        i0 = int(idx[0])
        win = df.iloc[i0:i0 + 751]
        if len(win) < 2:
            drop["window_lt2"] += 1
            continue
        # B&H sleeve: entry close of bar 1 (T+1), hold to window end
        closes = win["close"].values.astype(float)
        dts = list(win["date"].values)
        entry = closes[1]
        eq = {}
        for j in range(1, len(dts)):
            eq[dts[j]] = closes[j] / entry
        sys_eq[f"{norm6(e['code'])}|{e['ignition_date']}"] = eq
    return sys_eq, drop


def pool_daily_rets(sys_eq):
    acc = {}
    for _, d_eq in sys_eq.items():
        ks = sorted(d_eq)
        for i in range(1, len(ks)):
            r = d_eq[ks[i]] / d_eq[ks[i - 1]] - 1
            acc.setdefault(ks[i], []).append(r)
    dates = sorted(acc)
    pooled = [float(np.mean(acc[d])) for d in dates]
    return dates, pooled


def d6_members(pooled_dates, pooled):
    import theme_persist_p1 as T
    import ew6_portfolio as E
    from live.paper import load_core
    if E.PRICES_FULL is None:
        E.PRICES_FULL = load_core()
    ps = pd.Series(pooled, index=[pd.Timestamp(d) for d in pooled_dates])
    rows = []
    for tid in T.REG6:
        r = E.member_run(tid)
        sr = pd.Series(r["eq"], index=pd.to_datetime(r["dates"])).pct_change().dropna()
        j = pd.concat([ps, sr], axis=1, keys=["sys", "mem"]).dropna()
        if len(j) < 30:
            rows.append(dict(member=tid, n_common=len(j), corr=None))
            continue
        c = float(np.corrcoef(j["sys"].values, j["mem"].values)[0, 1])
        rows.append(dict(member=tid, n_common=len(j), corr=round(c, 4)))
    vals = [abs(r["corr"]) for r in rows if r["corr"] is not None]
    return rows, (max(vals) if vals else None)


def run_probe():
    facts = {"probe": "r667 bm-a THEME_JUDGE_P1 s2 pre-freeze probe",
             "cutoff": CUTOFF}
    sha = sha16_file(V03)
    facts["v03_sha16"] = sha
    assert sha == SHA16_EXPECT, f"census sha16 drift {sha}"
    d = json.load(open(V03, encoding="utf-8"))
    eps = d["episodes"]
    kept, dropped = dedup(eps)
    facts["dedup"] = {
        "n_rows": len(eps), "n_kept": len(kept), "n_dropped": len(dropped),
        "identity": "(norm6(code), ignition_date), keep-first sort=(norm6,ign,raw)",
        "n_unique_norm_codes": len({norm6(e["code"]) for e in kept}),
    }
    byday, cl, so = strata(kept)
    top = sorted(byday.items(), key=lambda x: -x[1])[:6]
    facts["strata"] = {
        "unit": "same-day ignition count on DEDUPED set (E28 >=10 law)",
        "n_cluster_face": len(cl), "n_solo_face": len(so),
        "n_cluster_days_ge10": sum(1 for v in byday.values() if v >= 10),
        "top_days": [{"date": k, "n": v} for k, v in top],
    }
    # leg 4: tails census + truncation edges
    tails, missing = {}, 0
    late_breaks = 0
    for e in eps:
        for w in e.get("waves", []):
            if w.get("break_date") and w["break_date"] > CUTOFF:
                late_breaks += 1
    codes = sorted({e["code"] for e in eps})
    for c in codes:
        df, fn = load_close_truncated(c)
        if df is None:
            missing += 1
            continue
        t = str(df["date"].iloc[-1])
        tails[t] = tails.get(t, 0) + 1
    sys_eq, drop = bh_pool_probe(kept)
    facts["panel"] = {
        "tails_after_truncation_by_code": tails,
        "n_files_missing": missing,
        "waves_break_after_cutoff": late_breaks,
        "episode_drop_gates": drop,
        "n_rides_in_pool": len(sys_eq),
    }
    # leg 5: twin identity (all twin pairs present in episode codes)
    from collections import defaultdict
    by_norm = defaultdict(list)
    for f in os.listdir(DAILY):
        if f.endswith(".csv"):
            by_norm[norm6(f[:-4])].append(f[:-4])
    twins = {k: v for k, v in by_norm.items() if len(v) > 1}
    twin_checks = []
    for k in sorted(twins):
        a = pd.read_csv(os.path.join(DAILY, f"{twins[k][0]}.csv"))
        b = pd.read_csv(os.path.join(DAILY, f"{twins[k][1]}.csv"))
        m = a.merge(b, on="date", suffixes=("_a", "_b"))
        if len(m):
            diff = float((m["close_a"] - m["close_b"]).abs().max())
            twin_checks.append({"norm": k, "n_overlap": len(m), "max_abs_close_diff": diff})
        else:
            twin_checks.append({"norm": k, "n_overlap": 0, "max_abs_close_diff": None})
    facts["twin_identity"] = {
        "n_twin_pairs": len(twin_checks),
        "all_identical": all(t["max_abs_close_diff"] == 0.0
                             for t in twin_checks if t["max_abs_close_diff"] is not None),
        "pairs": twin_checks[:8],
    }
    # leg 6: D6 proxy vs REG6
    dates, pooled = pool_daily_rets(sys_eq)
    rows, max_abs = d6_members(dates, pooled)
    facts["d6_proxy"] = {
        "face": "pooled same-window B&H probe sleeve (fund-family probe precedent)",
        "n_pooled_days": len(dates),
        "first_day": dates[0] if dates else None,
        "last_day": dates[-1] if dates else None,
        "vs_members": rows,
        "max_abs_corr": max_abs,
        "admit_0p7": bool(max_abs is not None and max_abs < 0.7),
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(facts, fh, ensure_ascii=False, indent=1)
    print(json.dumps({k: facts[k] for k in
                      ("v03_sha16", "dedup", "strata", "d6_proxy")},
                     ensure_ascii=False, indent=1)[:1800])
    print("panel:", json.dumps(facts["panel"], ensure_ascii=False)[:400])
    print("twin all_identical:", facts["twin_identity"]["all_identical"],
          "n_pairs:", facts["twin_identity"]["n_twin_pairs"])


def selftest():
    eps = [
        {"code": "159915", "ignition_date": "2024-09-30"},
        {"code": "sz159915", "ignition_date": "2024-09-30"},
        {"code": "sh510050", "ignition_date": "2020-07-06"},
        {"code": "510050", "ignition_date": "2020-07-06"},
        {"code": "510300", "ignition_date": "2019-01-04"},
        {"code": "159919", "ignition_date": "2024-09-30"},
    ]
    kept, dropped = dedup(eps)
    assert len(kept) == 4 and len(dropped) == 2, (kept, dropped)
    assert kept[0]["code"] == "159915" and kept[3]["code"] == "510300"
    byday, cl, so = strata(kept + [{"code": "x" + str(i),
                                     "ignition_date": "2024-09-30"}
                                    for i in range(9)])
    assert len(cl) == 11 and len(so) == 2, (len(cl), len(so))
    print("selftest 2/2 PASS")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "selftest":
        selftest()
    else:
        run_probe()
