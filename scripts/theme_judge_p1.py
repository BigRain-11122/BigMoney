"""THEME_JUDGE_P1 runner -- theme wave-ride mechanical translation JUDGMENT batch.

Prereg (FROZEN v1.0, bm-a r667 freeze window, commit precedes any judged run):
research/THEME_JUDGE_P1.md. Ticket T-2026-10-04-167-P1 (s1 r666 / s2 r667 /
s3 = this runner + pool burn + finalize). CEO order lineage: O-20261001-2103
R4 negative-line explicit pointer (0.75 deep-break family needs its own frozen
judgment) + E28 same-day cluster stratification law + O-20260928-1522 A-share
native playbook canon.

Design (frozen prereg, verbatim consumers):
  - universe = v0.3 algorithmic ignition census (sha16 51b1b8226afc74b1),
    dedup canon (identity=(norm6, ignition_date), keep-first bare wins,
    1919 -> 1822 rides / 796 ETFs) imported from the r667 s2 probe -- zero
    re-implementation.
  - strata = E28 same-day cluster law on the DEDUPED set: TJ-FULL face =
    cluster days (>=10 same-day ignitions, 1171 rides; market/beta practical
    face), TJ-SOLO face = solo days (<10, 651 rides; alpha/claim face --
    prereg sec.3/4/5(b) ride counts settle the FULL-face reading).
  - system = theme_persist_p1.simulate single source (entry ignition+1 close
    T+1, break exit close<=0.80*peak, rebirth re-entry >=1.25*trough within
    250td; constants v0.2/v0.3 frozen canon, zero refit); x1/x2 cost faces.
  - judged cells 4 = {TJ-FULL, TJ-SOLO} x {x1, x2}; per-cell same-window
    B&H passive (bh_series single source) feeds skill_line_v2 passive_override.
  - nulls 4 families x K=2000, rng([20585000, k]) substream law, same-mask
    random ignition starts s in [0, len-wlen] per ride, pooled Sharpe per rep;
    checkpoint = per-chunk fragment files (race-safe atomic writes) +
    assembled nulls_{face}.jsonl faces.
  - descriptive (not N_eff): sensitivity 16 (8 (bl,rb) variants x 2 strata,
    x1), LOO 796 ETF folds, ignition-date terciles, regime segments,
    famous16 membership re-derivation, exit-reason census (legal set =
    {first_entry, break_line_sell, rebirth_buy}, gate taken at 0 illegal).
  - gates single source: science_gates g1_prime_v2 / g2_registration_v2 /
    t_from_sharpe / m1_t_value_gate / deflated_sharpe_ratio / append_ledger /
    cutoff_meta; family PBO = screening.pbo.cscv_pbo 8 blocks (pbo value
    passed to g2 as float per its contract).
  - engine import graph: ZERO (exit axis 1 = strategy's own exit; selftest
    asserts no engine module enters the import graph and no default-stack
    bridge keys exist in this source).

Usage: run | finalize | selftest
  run      -- heavy burn (pool shard theme-judge-p1-burn-0of1): panels +
             real cells 4 + nulls 4x2000 (ProcessPool, BelowNormal, 26-cap,
             CEO 10% margin law) + sens 16 + LOO/tercile/regime/D6/census ->
             results/theme_judge_p1/burn_state.json. exit 0 complete /
             2 mechanism fault (fail-closed) / 3 over budget honest stop.
  finalize -- gates + verdict + trials ledger (append_ledger dict schema) +
             gate_attrition row (r248 entries list) ->
             results/theme_judge_p1/theme_judge_p1_results.json. Idempotent
             redo via r259 prev-echo guard (n_eff_override + prev_total from
             the stored block; attrition row not double-appended).
"""
import argparse
import csv
import json
import os
import sys
import time

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))
sys.path.insert(0, os.path.join(ROOT, "results"))

import science_gates as sg  # noqa: E402
import theme_persist_p1 as TP  # noqa: E402
from theme_persist_p1 import (  # noqa: E402  single-source law
    COST_X1, MINUS20_LINE, REBOUND_MIN, REBOUND_SEARCH_TD, REG6,
    _daily_rets, _pool, bh_series, simulate,
)
import _r667bma_theme_judge_s2_probe as P2  # noqa: E402  r667 s2 kernels

BATCH = "THEME-JUDGE-P1"
PREREG = "research/THEME_JUDGE_P1.md"
CUTOFF = "2026-09-22"
V03 = os.path.join(ROOT, "results", "theme_ring",
                   "theme_events_v03_algorithmic.json")
V03_SHA16 = "51b1b8226afc74b1"
SEED_NULLS = 20585000          # science_gates.SEED_REGISTRY theme_judge_p1_nulls
K_NULLS = 2000                 # RANDOM_LARGE_SAMPLE_LAW sec.3 >=2000/family
CHUNK = 100                    # checkpoint = per-chunk fragments (80 blocks)
WIN = 751                      # ignition bar + up to 750td (census canon)
X2 = 2.0 * COST_X1
BUDGET_SEC = 600               # prereg sec.0 estimate 40-60s@26w + panels 20s
WORKERS_CAP = 26               # O-2355 ProcessPool + CEO 10% margin 26/32
STRATA = ("TJ-FULL", "TJ-SOLO")
FACES = ("TJ-FULL-x1", "TJ-FULL-x2", "TJ-SOLO-x1", "TJ-SOLO-x2")
MAIN_FACE = "TJ-SOLO-x1"
OUT_DIR = os.path.join(ROOT, "results", "theme_judge_p1")
FRAG_DIR = os.path.join(OUT_DIR, "nulls_frags")
PANEL_CLOSE = os.path.join(OUT_DIR, "panels_close.npy")
PANEL_CAL = os.path.join(OUT_DIR, "panels_cal.npy")
PANEL_META = os.path.join(OUT_DIR, "panels_meta.json")
BURN_STATE = os.path.join(OUT_DIR, "burn_state.json")
RESULTS_JSON = os.path.join(OUT_DIR, "theme_judge_p1_results.json")
EPISODES_CSV = os.path.join(OUT_DIR, "episodes.csv")
D6_REAL_JSON = os.path.join(OUT_DIR, "d6_real.json")
LEDGER_PATH = os.path.join(ROOT, "research", "TRIAL_GRAMMAR_LEDGER.md")
ATTR_JSON = os.path.join(ROOT, "results", "gate_attrition.json")
CENSUS_LEGAL = ("first_entry", "break_line_sell", "rebirth_buy")

_G = {}   # shared state: closes, cal, lens, rides_by, calendar, meta...


# ---------------------------------------------------------------- helpers

def _sharpe(rets):
    a = np.asarray(rets, dtype=float)
    if len(a) < 2 or float(np.std(a)) == 0.0:
        return 0.0
    return float(np.mean(a) / np.std(a) * np.sqrt(252.0))


def _now():
    return time.strftime("%Y-%m-%d %H:%M:%S")


def _load_episodes():
    """Census -> dedup -> strata + prereg sec.2 completeness gates (fail-closed)."""
    sha = P2.sha16_file(V03)
    assert sha == V03_SHA16, f"census sha16 drift: {sha} != {V03_SHA16}"
    eps = json.load(open(V03, encoding="utf-8"))["episodes"]
    kept, dropped = P2.dedup(eps)
    assert len(eps) == 1919 and len(kept) == 1822 and len(dropped) == 97, \
        f"dedup canon counts drift: {len(eps)}/{len(kept)}/{len(dropped)}"
    byday, cl, so = P2.strata(kept)
    assert len(cl) == 1171 and len(so) == 651, \
        f"strata counts drift: {len(cl)}/{len(so)}"
    assert sg.SEED_REGISTRY.get("theme_judge_p1_nulls") == SEED_NULLS, \
        "seed registry drift"
    assert abs(COST_X1 - 0.0013041) < 1e-9, "COST_X1 import drift"
    assert abs(MINUS20_LINE - 0.8) < 1e-12 and abs(REBOUND_MIN - 1.25) < 1e-12 \
        and REBOUND_SEARCH_TD == 250, "structural constants drift"
    # twin identity (prereg sec.2 gate 6, probe leg-5 kernel inline)
    from collections import defaultdict
    import pandas as pd
    daily = os.path.join(ROOT, "data", "daily")
    by_norm = defaultdict(list)
    for f in os.listdir(daily):
        if f.endswith(".csv"):
            by_norm[P2.norm6(f[:-4])].append(f[:-4])
    twins = {k: v for k, v in by_norm.items() if len(v) > 1}
    bad_twins = 0
    for k in sorted(twins):
        a = pd.read_csv(os.path.join(daily, f"{twins[k][0]}.csv"))
        b = pd.read_csv(os.path.join(daily, f"{twins[k][1]}.csv"))
        m = a.merge(b, on="date", suffixes=("_a", "_b"))
        if len(m) and float((m["close_a"] - m["close_b"]).abs().max()) != 0.0:
            bad_twins += 1
    assert bad_twins == 0, f"twin price identity broken on {bad_twins} pairs"
    fam = "theme_wave_ride_mechanical"
    assert fam not in getattr(sg, "CLOSED_FAMILIES", {}), \
        f"family {fam} closed -- batch void"
    flips, flips_all = [], 0
    for e in kept:
        for w in e.get("waves", []):
            bd = w.get("break_date")
            if bd and bd > CUTOFF:
                flips.append({"code": e["code"],
                              "ignition_date": e["ignition_date"],
                              "census_break_date": bd})
    for e in eps:
        for w in e.get("waves", []):
            if w.get("break_date") and w["break_date"] > CUTOFF:
                flips_all += 1
    facts = {
        "census_sha16": sha, "n_census": len(eps), "n_kept": len(kept),
        "n_dropped_dups": len(dropped), "n_cluster_rides": len(cl),
        "n_solo_rides": len(so),
        "n_cluster_days": sum(1 for v in byday.values() if v >= 10),
        "n_unique_etfs": len({P2.norm6(e["code"]) for e in kept}),
        "n_twin_pairs": len(twins), "twin_bad_pairs": bad_twins,
        "closed_family_check": f"{fam}=open",
        "waves_break_after_cutoff_kept": flips,
        "n_waves_break_after_cutoff_all_eps": flips_all,
    }
    return kept, byday, facts


def _build_panels(kept, byday, facts):
    """Truncated close panels + shared calendar + ride windows (deterministic
    from the frozen census + data/daily prefixed-file canon). Digest binds
    checkpoint rows to the exact panel build."""
    import hashlib
    import pandas as pd
    codes = sorted({P2.norm6(e["code"]) for e in kept})
    code_index = {c: i for i, c in enumerate(codes)}
    per_code, tails = {}, []
    for c in codes:
        df, fn = P2.load_close_truncated(c)
        assert df is not None, f"panel missing code {c} ({fn})"
        d64 = pd.to_datetime(df["date"]).values.astype("datetime64[D]")
        per_code[c] = (d64, df["close"].values.astype(float))
        tails.append(f"{c}:{len(df)}:{str(df['date'].iloc[-1])}")
    cal_arr = np.unique(np.concatenate([per_code[c][0] for c in codes]))
    calendar = [str(x) for x in cal_arr.astype("datetime64[D]")]
    n_codes, maxlen = len(codes), max(len(v[0]) for v in per_code.values())
    closes2d = np.full((n_codes, maxlen), np.nan, dtype=np.float64)
    cal2d = np.full((n_codes, maxlen), -1, dtype=np.int32)
    for i, c in enumerate(codes):
        d64, cl = per_code[c]
        closes2d[i, :len(cl)] = cl
        cal2d[i, :len(cl)] = np.searchsorted(cal_arr, d64)
    ign_order = sorted(kept, key=lambda e: e["ignition_date"])
    t1, t2 = len(ign_order) // 3, (2 * len(ign_order)) // 3
    famous = {P2.norm6(ev["proxy"])
              for ev in __import__("theme_event_library").EVENTS}
    rides, drops = [], {"no_ignition_bar": 0, "window_lt2": 0}
    for e in kept:
        c = P2.norm6(e["code"])
        d64, cl = per_code[c]
        pos = np.nonzero(d64 == np.datetime64(e["ignition_date"], "D"))[0]
        if len(pos) == 0:
            drops["no_ignition_bar"] += 1
            continue
        i0 = int(pos[0])
        wlen = int(min(WIN, len(cl) - i0))
        if wlen < 2:
            drops["window_lt2"] += 1
            continue
        rides.append({
            "rid": f"{c}|{e['ignition_date']}", "c": code_index[c],
            "i0": i0, "wlen": wlen, "etf": c, "ign": e["ignition_date"],
            "stratum": ("TJ-FULL" if byday[e["ignition_date"]] >= 10
                        else "TJ-SOLO"),
            "famous": c in famous,
            "tercile": (0 if e["ignition_date"] <=
                        ign_order[t1]["ignition_date"] else
                        1 if e["ignition_date"] <=
                        ign_order[t2]["ignition_date"] else 2),
        })
    assert drops == {"no_ignition_bar": 0, "window_lt2": 0}, \
        f"drop gates nonzero (prereg sec.2: 1822/1822 all enter): {drops}"
    digest = hashlib.sha256(
        (facts["census_sha16"] + "|" + ";".join(tails)).encode()
    ).hexdigest()[:16]
    meta = {"digest": digest, "calendar": calendar, "code_index": code_index,
            "code_len_list": [len(per_code[c][0]) for c in codes],
            "rides": rides, "facts": facts, "drops": drops}
    os.makedirs(OUT_DIR, exist_ok=True)
    np.save(PANEL_CLOSE, closes2d)
    np.save(PANEL_CAL, cal2d)
    with open(PANEL_META, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(meta, fh, ensure_ascii=False)
    return meta, closes2d, cal2d


def _init_worker():
    import psutil
    pri = getattr(psutil, "BELOW_NORMAL_PRIORITY_CLASS", None)
    if pri is not None:
        try:
            psutil.Process().nice(pri)   # O-1136 low-priority pool law
        except Exception:
            pass
    with open(PANEL_META, encoding="utf-8") as fh:
        meta = json.load(fh)
    _G["closes"] = np.load(PANEL_CLOSE, mmap_mode="r")
    _G["cal"] = np.load(PANEL_CAL, mmap_mode="r")
    _G["lens"] = np.asarray(meta["code_len_list"], dtype=np.int64)
    _G["meta"] = meta
    _G["rides_by"] = {s: [r for r in meta["rides"] if r["stratum"] == s]
                      for s in STRATA}
    _G["n_cal"] = len(meta["calendar"])


# ------------------------------------------------- pool task faces (worker)

def _pooled_sharpe_accum(closes, cals, n_cal, cost):
    """Pooled equal-weight daily-return Sharpe, vector accumulator path.

    Semantics identical to theme_persist_p1._daily_rets + _pool (per-ride
    day-over-day returns on the ride's own consecutive bars, equal-weight
    mean per date); the selftest equivalence leg proves this against the
    single-source dict path on synthetic panels."""
    eq = np.asarray(simulate(list(closes), cost=cost)["eq"], dtype=float)
    rets = eq[1:] / eq[:-1] - 1.0
    d = cals[1:]
    s = np.zeros(n_cal)
    n = np.zeros(n_cal, dtype=np.int32)
    np.add.at(s, d, rets)
    np.add.at(n, d, 1)
    m = n > 0
    return _sharpe(s[m] / n[m])


def _null_chunk(payload):
    """One (stratum, chunk) task: CHUNK reps of same-mask random-ignition
    nulls, both cost faces per rep (paired windows; prereg sec.3 7.29M-call
    budget face). rng([SEED, k]) substream law verbatim."""
    st, ci = payload["stratum"], payload["ci"]
    rides = _G["rides_by"][st]
    closes2d, cal2d, lens = _G["closes"], _G["cal"], _G["lens"]
    n_cal = _G["n_cal"]
    # ci = k-start offset (task gen: range(0, K_NULLS, CHUNK)) -- NOT a
    # chunk index. r670 live-strike fix: the ci*CHUNK reading produced
    # empty ks for every ci>0 and starved the null families (38/40 empty
    # frags -> assembly assert). rng([SEED_NULLS, k]) per-k substream law
    # untouched: k coverage 0..K_NULLS-1 exactly once.
    ks = list(range(ci, min(ci + CHUNK, K_NULLS)))
    s1, s2 = [], []
    for k in ks:
        rng = np.random.default_rng([SEED_NULLS, k])
        sum1 = np.zeros(n_cal); cnt1 = np.zeros(n_cal, dtype=np.int32)
        sum2 = np.zeros(n_cal); cnt2 = np.zeros(n_cal, dtype=np.int32)
        for r in rides:
            ci_code, wl = r["c"], r["wlen"]
            n = int(lens[ci_code])
            hi = n - wl
            if hi < 0:
                hi = 0
            s = int(rng.integers(0, hi + 1))
            cw = np.asarray(closes2d[ci_code, s:s + wl], dtype=float)
            calw = np.asarray(cal2d[ci_code, s:s + wl])
            for acc_sum, acc_cnt, cost in ((sum1, cnt1, COST_X1),
                                           (sum2, cnt2, X2)):
                eq = np.asarray(simulate(list(cw), cost=cost)["eq"],
                                dtype=float)
                rets = eq[1:] / eq[:-1] - 1.0
                np.add.at(acc_sum, calw[1:], rets)
                np.add.at(acc_cnt, calw[1:], 1)
        m1, m2 = cnt1 > 0, cnt2 > 0
        s1.append(_sharpe(sum1[m1] / cnt1[m1]))
        s2.append(_sharpe(sum2[m2] / cnt2[m2]))
    return {"kind": "null_chunk", "stratum": st, "ci": ci,
            "digest": _G["meta"]["digest"], "ks": ks,
            "sharpe_x1": [round(float(x), 6) for x in s1],
            "sharpe_x2": [round(float(x), 6) for x in s2]}


def _sens_task(payload):
    """One (stratum, bl, rb) sensitivity leg: pooled net at x1 (descriptive,
    prereg sec.3 E24-ii structural-constant neighborhood disclosure)."""
    st, bl, rb = payload["stratum"], payload["bl"], payload["rb"]
    rides = _G["rides_by"][st]
    closes2d, cal2d = _G["closes"], _G["cal"]
    n_cal = _G["n_cal"]
    s = np.zeros(n_cal); n = np.zeros(n_cal, dtype=np.int32)
    for r in rides:
        cw = np.asarray(closes2d[r["c"], r["i0"]:r["i0"] + r["wlen"]],
                        dtype=float)
        calw = np.asarray(cal2d[r["c"], r["i0"]:r["i0"] + r["wlen"]])
        eq = np.asarray(simulate(list(cw), break_line=bl, rebirth=rb,
                                 cost=COST_X1)["eq"], dtype=float)
        rets = eq[1:] / eq[:-1] - 1.0
        np.add.at(s, calw[1:], rets)
        np.add.at(n, calw[1:], 1)
    m = n > 0
    pr = s[m] / n[m]
    net = float(np.prod([1 + x for x in pr]) - 1) if len(pr) else 0.0
    return {"kind": "sens", "stratum": st, "break_line": bl, "rebirth": rb,
            "pooled_sys_net_x1": round(net, 6)}


def _task_dispatch(payload):
    if payload["kind"] == "null_chunk":
        return _null_chunk(payload)
    if payload["kind"] == "sens":
        return _sens_task(payload)
    raise ValueError(f"unknown task kind {payload['kind']}")


# ---------------------------------------------------------- real cells face

def _cell_pass(rides, dates_by_rid, cost, kind):
    """One (ride-set, cost) pass -> pooled metrics via the single-source dict
    path (TP._daily_rets + TP._pool, prereg sec.3) + per-ride raw output."""
    eq_map, per_ride = {}, {}
    for r in rides:
        cw = _G["closes"][r["c"], r["i0"]:r["i0"] + r["wlen"]]
        if kind == "sys":
            out = simulate(list(cw), cost=cost)
            per_ride[r["rid"]] = {"eq": out["eq"], "trades": out["trades"],
                                  "end_pos": out["end_pos"]}
        else:
            per_ride[r["rid"]] = {"eq": bh_series(list(cw), cost=cost)}
        eq_map[r["rid"]] = dict(zip(dates_by_rid[r["rid"]],
                                    per_ride[r["rid"]]["eq"]))
    dates, pooled, net = _pool(_daily_rets(eq_map))
    return {"dates": dates, "rets": pooled, "net": net, "per_ride": per_ride}


def _census_reasons(trades):
    """Positional reason canon: first buy=first_entry, every sell=
    break_line_sell, later buys=rebirth_buy; anything else = illegal."""
    reasons, illegal, buys = [], 0, 0
    for t in trades:
        idx, act, _px = t
        if act == "buy" and buys == 0:
            reasons.append("first_entry")
        elif act == "buy":
            reasons.append("rebirth_buy")
        elif act == "sell":
            reasons.append("break_line_sell")
        else:
            reasons.append(f"ILLEGAL:{act}")
            illegal += 1
        if act == "buy":
            buys += 1
    return reasons, illegal


# ---------------------------------------------------------------- run cmd

def cmd_run(_):
    t0 = time.time()
    os.makedirs(OUT_DIR, exist_ok=True)
    kept, byday, facts = _load_episodes()
    meta, closes2d, cal2d = _build_panels(kept, byday, facts)
    calendar = meta["calendar"]
    rides = meta["rides"]
    rides_by = {s: [r for r in rides if r["stratum"] == s] for s in STRATA}
    dates_by_rid = {r["rid"]: [calendar[j] for j in
                               cal2d[r["c"], r["i0"]:r["i0"] + r["wlen"]]]
                    for r in rides}
    _G.update(closes=closes2d, cal=cal2d, meta=meta, rides_by=rides_by,
              n_cal=len(calendar),
              lens=np.asarray(meta["code_len_list"], dtype=np.int64))
    digest = meta["digest"]

    # ---- real cells 4 + census + per-ride nets --------------------------
    cells, nets = {}, {}
    census = {"illegal": 0, "censored": 0, "n_rides": len(rides),
              "reasons_count": {k: 0 for k in CENSUS_LEGAL},
              "trades_per_ride": [], "end_pos_flip_rows": []}
    for st in STRATA:
        rs = rides_by[st]
        for cost_name, cost in (("x1", COST_X1), ("x2", X2)):
            face = f"{st}-{cost_name}"
            out = _cell_pass(rs, dates_by_rid, cost, "sys")
            cells[face] = {
                "sharpe_full": round(_sharpe(out["rets"]), 6),
                "pooled_net": round(float(out["net"]), 6),
                "returns": [round(float(x), 8) for x in out["rets"]],
                "dates": out["dates"], "n_entries": len(rs),
                "n_trades": sum(len(v["trades"])
                                for v in out["per_ride"].values()),
            }
            for rid, v in out["per_ride"].items():
                nets.setdefault(rid, {})[f"sys_{cost_name}"] = \
                    round(float(v["eq"][-1] - 1), 6)
            if cost_name == "x1":
                for rid, v in out["per_ride"].items():
                    reasons, ill = _census_reasons(v["trades"])
                    census["illegal"] += ill
                    for x in reasons:
                        if x in census["reasons_count"]:
                            census["reasons_count"][x] += 1
                        else:
                            census["illegal"] += 1
                    census["censored"] += 1 if v["end_pos"] else 0
                    census["trades_per_ride"].append(len(v["trades"]))
            bh = _cell_pass(rs, dates_by_rid, cost, "bh")
            cells[face]["passive_sharpe"] = round(_sharpe(bh["rets"]), 6)
            cells[face]["passive_net"] = round(float(bh["net"]), 6)
            for rid, v in bh["per_ride"].items():
                nets.setdefault(rid, {})[f"bh_{cost_name}"] = \
                    round(float(v["eq"][-1] - 1), 6)
    # decisions are price-only: cost faces must not alter the trade list
    f1 = _cell_pass(rides, dates_by_rid, COST_X1, "sys")["per_ride"]
    f2 = _cell_pass(rides, dates_by_rid, X2, "sys")["per_ride"]
    assert all(f1[r]["trades"] == f2[r]["trades"] for r in f1), \
        "cost faces must not alter decisions (price-only exit law)"
    for fl in facts["waves_break_after_cutoff_kept"]:
        rid = f"{P2.norm6(fl['code'])}|{fl['ignition_date']}"
        if rid in f1:
            census["end_pos_flip_rows"].append({
                "rid": rid, "census_break_date": fl["census_break_date"],
                "end_pos_under_truncation": bool(f1[rid]["end_pos"])})
    census["censored_share"] = round(census["censored"] / len(rides), 6)

    # ---- LOO accumulators (x1, deduped full set) + terciles --------------
    loo_sys_tot, loo_sys_sum_e, loo_sys_n_e = {}, {}, {}
    loo_bh_tot, loo_bh_sum_e, loo_bh_n_e = {}, {}, {}
    counts_sys, counts_bh = {}, {}
    terc_acc = {g: {"sys": ({}, {}), "bh": ({}, {})} for g in range(3)}
    famous_rows = {k: {"n": 0, "sys_net_mean": 0.0, "bh_net_mean": 0.0}
                   for k in ("famous", "rest")}
    bh_full = _cell_pass(rides, dates_by_rid, COST_X1, "bh")["per_ride"]
    for r in rides:
        rid, dts = r["rid"], dates_by_rid[r["rid"]]
        seq = f1[rid]["eq"]; beq = bh_full[rid]["eq"]
        for j in range(1, len(dts)):
            d = dts[j]
            v = seq[j] / seq[j - 1] - 1
            w = beq[j] / beq[j - 1] - 1
            loo_sys_tot[d] = loo_sys_tot.get(d, 0.0) + v
            loo_sys_sum_e.setdefault(d, {}); e = loo_sys_sum_e[d]
            e[r["etf"]] = e.get(r["etf"], 0.0) + v
            loo_sys_n_e.setdefault(d, {}); ne = loo_sys_n_e[d]
            ne[r["etf"]] = ne.get(r["etf"], 0) + 1
            counts_sys[d] = counts_sys.get(d, 0) + 1
            loo_bh_tot[d] = loo_bh_tot.get(d, 0.0) + w
            loo_bh_sum_e.setdefault(d, {}); eb = loo_bh_sum_e[d]
            eb[r["etf"]] = eb.get(r["etf"], 0.0) + w
            loo_bh_n_e.setdefault(d, {}); nb = loo_bh_n_e[d]
            nb[r["etf"]] = nb.get(r["etf"], 0) + 1
            counts_bh[d] = counts_bh.get(d, 0) + 1
            for kind, val in (("sys", v), ("bh", w)):
                g = terc_acc[r["tercile"]][kind]
                g[0][d] = g[0].get(d, 0.0) + val
                g[1][d] = g[1].get(d, 0) + 1
        fam_key = "famous" if r["famous"] else "rest"
        famous_rows[fam_key]["n"] += 1
        famous_rows[fam_key]["sys_net_mean"] += nets[rid]["sys_x1"]
        famous_rows[fam_key]["bh_net_mean"] += nets[rid]["bh_x1"]

    # ---- null chunks + sensitivity via ProcessPool ----------------------
    os.makedirs(FRAG_DIR, exist_ok=True)
    done = set()
    # r670: match the actual frag names (<STRATUM>_chunk_*.json -- the old
    # startswith("chunk_") filter never matched, so resume never skipped)
    # and require non-empty ks so a poisoned empty frag can never count as
    # done (the exact state the ci-bug left on disk).
    for f in os.listdir(FRAG_DIR):
        if f.endswith(".json"):
            try:
                row = json.load(open(os.path.join(FRAG_DIR, f),
                                     encoding="utf-8"))
                if row.get("digest") == digest and row.get("ks"):
                    done.add((row["stratum"], row["ci"]))
            except Exception:
                pass
    tasks = [{"kind": "null_chunk", "stratum": st, "ci": ci}
             for st in STRATA for ci in range(0, K_NULLS, CHUNK)
             if (st, ci) not in done]
    sens_tasks = [{"kind": "sens", "stratum": st, "bl": bl, "rb": rb}
                  for st in STRATA
                  for bl in (0.75, 0.80, 0.85)
                  for rb in (1.20, 1.25, 1.30)
                  if not (abs(bl - float(MINUS20_LINE)) < 1e-12
                          and abs(rb - float(REBOUND_MIN)) < 1e-12)]
    import multiprocessing as mp
    workers = min(WORKERS_CAP, max(2, (os.cpu_count() or 8) - 6))
    ctx = mp.get_context("spawn")
    with ctx.Pool(workers, initializer=_init_worker) as pool:
        results = pool.map(_task_dispatch, tasks + sens_tasks, chunksize=1)
    for row in results:
        if row["kind"] == "null_chunk":
            path = os.path.join(FRAG_DIR,
                                f"{row['stratum']}_chunk_{row['ci']:02d}.json")
            tmp = path + ".tmp"
            with open(tmp, "w", encoding="utf-8", newline="\n") as fh:
                json.dump(row, fh, ensure_ascii=False)
            os.replace(tmp, path)                      # atomic, race-safe
        else:
            cells.setdefault("sensitivity", []).append(row)

    # ---- assemble null families + checkpoint jsonl faces ----------------
    nulls = {}
    for st in STRATA:
        rows = []
        for ci in range(0, K_NULLS, CHUNK):
            row = json.load(open(os.path.join(
                FRAG_DIR, f"{st}_chunk_{ci:02d}.json"), encoding="utf-8"))
            assert row["digest"] == digest, \
                f"stale checkpoint digest on {st}/{ci}: rebuild required"
            rows.append(row)
        for cost_name, key in (("x1", "sharpe_x1"), ("x2", "sharpe_x2")):
            face = f"{st}-{cost_name}"
            vals = [v for row in rows for v in row[key]]
            assert len(vals) == K_NULLS, f"null family {face} incomplete"
            nulls[face] = [round(float(v), 6) for v in vals]
            with open(os.path.join(OUT_DIR, f"nulls_{face}.jsonl"), "w",
                      encoding="utf-8", newline="\n") as fh:
                for row in rows:
                    fh.write(json.dumps(
                        {"key": f"{face}|chunk_{row['ci']}", "ks": row["ks"],
                         "sharpes": row[key]}, ensure_ascii=False) + "\n")

    # ---- LOO folds (796 ETFs, x1, deduped full set) ---------------------
    full_sys_net = float(np.prod([1 + loo_sys_tot[d] / counts_sys[d]
                                  for d in sorted(counts_sys)]) - 1)
    full_bh_net = float(np.prod([1 + loo_bh_tot[d] / counts_bh[d]
                                 for d in sorted(counts_bh)]) - 1)
    full_sign = np.sign(full_sys_net - full_bh_net)
    loo_rows, loo_stable = [], 0
    etfs = sorted({r["etf"] for r in rides})
    for e in etfs:
        sn, bn = 1.0, 1.0
        for d in sorted(counts_sys):
            se = loo_sys_sum_e.get(d, {}).get(e, 0.0)
            ce = loo_sys_n_e.get(d, {}).get(e, 0)
            c = counts_sys[d] - ce
            if c > 0:
                sn *= 1.0 + (loo_sys_tot[d] - se) / c
        for d in sorted(counts_bh):
            se = loo_bh_sum_e.get(d, {}).get(e, 0.0)
            ce = loo_bh_n_e.get(d, {}).get(e, 0)
            c = counts_bh[d] - ce
            if c > 0:
                bn *= 1.0 + (loo_bh_tot[d] - se) / c
        m = bool(np.sign(sn - bn) == full_sign)
        loo_rows.append({"left_out_etf": e, "sys_net": round(sn - 1.0, 6),
                         "bh_net": round(bn - 1.0, 6), "sign_match": m})
        loo_stable += int(m)
    loo_share = round(loo_stable / max(1, len(etfs)), 6)

    # ---- terciles / regime / famous -------------------------------------
    terciles = {}
    for g in range(3):
        s_, n_ = terc_acc[g]["sys"]
        b_, bn_ = terc_acc[g]["bh"]
        terciles[f"tercile_{g}"] = {
            "n_rides": sum(1 for r in rides if r["tercile"] == g),
            "sys_net": round(float(np.prod([1 + s_[d] / n_[d]
                                            for d in sorted(s_)]) - 1), 6),
            "bh_net": round(float(np.prod([1 + b_[d] / bn_[d]
                                           for d in sorted(b_)]) - 1), 6),
        }
    regime_seg = None
    try:
        import pandas as pd
        bench = TP.load_series("sh510300")
        bench = bench[bench.index <= CUTOFF]
        from t22_virtual_timepoints import regime_proxy
        labels = regime_proxy(bench)
        lab_by = {d.strftime("%Y-%m-%d"): str(x)
                  for d, x in zip(bench.index, labels)}
        seg = {}
        for d in sorted(counts_sys):
            seg.setdefault(lab_by.get(d, "na"), []).append(
                loo_sys_tot[d] / counts_sys[d])
        regime_seg = {k: {"n": len(v),
                          "mean_daily": round(float(np.mean(v)), 8),
                          "cum_simple": round(float(np.sum(v)), 6)}
                      for k, v in seg.items()}
    except Exception as exc:
        regime_seg = {"error": repr(exc)}
    for k in famous_rows:
        n = famous_rows[k]["n"]
        famous_rows[k]["sys_net_mean"] = round(
            famous_rows[k]["sys_net_mean"] / n, 6) if n else None
        famous_rows[k]["bh_net_mean"] = round(
            famous_rows[k]["bh_net_mean"] / n, 6) if n else None

    # ---- D6 real faces: pooled judged system vs REG6 ---------------------
    d6 = {"face": "pooled judged system daily returns per cell vs REG6",
          "cells": {}}
    try:
        import pandas as pd
        import ew6_portfolio as E
        from live.paper import load_core
        if E.PRICES_FULL is None:
            E.PRICES_FULL = load_core()
        member_rets = {}
        for tid in REG6:
            r = E.member_run(tid)
            sr = pd.Series(r["eq"], index=pd.to_datetime(r["dates"]))
            member_rets[tid] = sr.pct_change().dropna()
        for face in FACES:
            ps = pd.Series(cells[face]["returns"],
                           index=[pd.Timestamp(d)
                                  for d in cells[face]["dates"]])
            rows = []
            for tid, sr in member_rets.items():
                j = pd.concat([ps, sr], axis=1, keys=["sys", "mem"]).dropna()
                if len(j) < 30:
                    rows.append({"member": tid, "n_common": len(j),
                                 "corr": None})
                    continue
                c = float(np.corrcoef(j["sys"].values, j["mem"].values)[0, 1])
                rows.append({"member": tid, "n_common": len(j),
                             "corr": round(c, 4)})
            vals = [abs(x["corr"]) for x in rows if x["corr"] is not None]
            d6["cells"][face] = {"vs_members": rows,
                                 "max_abs_corr": (round(max(vals), 4)
                                                  if vals else None),
                                 "any_reject_0p7": any(
                                     x["corr"] is not None
                                     and abs(x["corr"]) >= 0.7 for x in rows)}
    except Exception as exc:
        d6["error"] = repr(exc)
    with open(D6_REAL_JSON, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(d6, fh, ensure_ascii=False, indent=1, sort_keys=True)

    # ---- episodes CSV -----------------------------------------------------
    with open(EPISODES_CSV, "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=[
            "rid", "etf", "ignition_date", "stratum", "tercile", "famous",
            "wlen", "n_trades", "end_pos", "sys_net_x1", "sys_net_x2",
            "bh_net_x1", "bh_net_x2"])
        w.writeheader()
        for r in rides:
            rid = r["rid"]
            w.writerow({
                "rid": rid, "etf": r["etf"], "ignition_date": r["ign"],
                "stratum": r["stratum"], "tercile": r["tercile"],
                "famous": r["famous"], "wlen": r["wlen"],
                "n_trades": len(f1[rid]["trades"]),
                "end_pos": f1[rid]["end_pos"],
                "sys_net_x1": nets[rid]["sys_x1"],
                "sys_net_x2": nets[rid]["sys_x2"],
                "bh_net_x1": nets[rid]["bh_x1"],
                "bh_net_x2": nets[rid]["bh_x2"],
            })

    elapsed = time.time() - t0
    payload = {
        "batch": BATCH, "prereg": PREREG, "evidence_cutoff": CUTOFF,
        "panels_digest": digest, "facts": facts, "cells": cells,
        "nulls": nulls, "census": census,
        "loo": {"n_folds": len(etfs), "stable": loo_stable,
                "stable_share": loo_share,
                "full_sys_net": round(full_sys_net, 6),
                "full_bh_net": round(full_bh_net, 6), "rows": loo_rows},
        "terciles": terciles, "regime_segments": regime_seg,
        "famous16": famous_rows, "d6_real": d6,
        "audit": {"elapsed_sec": round(elapsed, 1),
                  "budget_cap_sec": BUDGET_SEC,
                  "over_budget": bool(elapsed > BUDGET_SEC),
                  "workers_cap": WORKERS_CAP, "workers_used": workers,
                  "priority": "BelowNormal (O-1136)",
                  "machine": os.environ.get("COMPUTERNAME", "unknown")},
    }
    if payload["audit"]["over_budget"]:
        print(f"OVER BUDGET {elapsed:.0f}s > {BUDGET_SEC}s -- honest stop, "
              "checkpoints preserved (exit 3)")
        return 3
    with open(BURN_STATE, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(payload, fh, ensure_ascii=False, sort_keys=True)
    print(json.dumps({
        "digest": digest, "elapsed_sec": round(elapsed, 1),
        "faces": {f: cells[f]["sharpe_full"] for f in FACES},
        "passive": {f: cells[f]["passive_sharpe"] for f in FACES},
        "null_mu": {f: round(float(np.mean(nulls[f])), 4) for f in FACES},
        "censored_share": census["censored_share"],
        "illegal_reasons": census["illegal"],
    }, ensure_ascii=False))
    return 0


# ------------------------------------------------------------ finalize cmd

def cmd_finalize(_):
    if not os.path.exists(BURN_STATE):
        print("burn_state.json absent -- run the burn first (exit 2)")
        return 2
    st = json.load(open(BURN_STATE, encoding="utf-8"))
    redo = os.path.exists(RESULTS_JSON)
    prev = json.load(open(RESULTS_JSON, encoding="utf-8")) if redo else {}
    prev_led = prev.get("trials_ledger") or {}
    prev_neff = (((prev.get("gates") or {}).get(MAIN_FACE) or {})
                 .get("g1", {}).get("skill_line", {}).get("n_eff"))
    cells = st["cells"]
    census = st["census"]
    census_blocked = census["illegal"] > 0

    # family PBO: aligned 4-cell pooled returns, CSCV 8 blocks
    import pandas as pd
    from screening import pbo as PBO
    frames = {f: pd.Series(cells[f]["returns"],
                           index=[pd.Timestamp(d)
                                  for d in cells[f]["dates"]])
              for f in FACES}
    aligned = pd.concat(frames.values(), axis=1, keys=FACES).dropna()
    pbo_out = PBO.cscv_pbo(aligned, n_blocks=8)

    gates = {}
    for face in FACES:
        vals = np.asarray(st["nulls"][face], dtype=float)
        null_pool = {"values": [float(x) for x in vals],
                     "coverage": {"n_values": len(vals),
                                  "mu": float(np.mean(vals)),
                                  "sigma": float(np.std(vals, ddof=1)),
                                  "schemas_parsed": [f"{BATCH}:{face}"],
                                  "known_unparsed": []},
                     "source": f"{BATCH} same-mask random-ignition null family"}
        g1 = sg.g1_prime_v2(
            sharpe_full=cells[face]["sharpe_full"],
            returns=cells[face]["returns"], batch_cells=4, pool="core48",
            n_trades=cells[face]["n_trades"],
            n_entries=cells[face]["n_entries"],
            null_pool=null_pool,
            passive_override=cells[face]["passive_sharpe"],
            n_eff_override=(int(prev_neff) if redo and prev_neff else None))
        n_eff = g1["skill_line"]["n_eff"]
        dsr = sg.deflated_sharpe_ratio(
            cells[face]["returns"], n_trials=n_eff,
            var_null_sr=float(np.var(vals, ddof=1)))
        g2 = sg.g2_registration_v2(g1["pass_v2"], dsr,
                                   float(pbo_out["pbo"]))
        gates[face] = {"g1": g1, "g2": g2, "dsr": dsr,
                       "null_mu": round(float(np.mean(vals)), 6),
                       "null_sigma": round(float(np.std(vals, ddof=1)), 6)}

    t_val = float(sg.t_from_sharpe(cells[MAIN_FACE]["sharpe_full"],
                                   len(cells[MAIN_FACE]["returns"])))
    m1 = sg.m1_t_value_gate(t_val)

    main_g1 = gates[MAIN_FACE]["g1"]["pass_v2"]
    main_g2 = gates[MAIN_FACE]["g2"]["eligible_v2"]
    if census_blocked:
        verdict = "consumption-blocked (exit-reason census illegal>0)"
    elif main_g1 and main_g2:
        verdict = ("judged_positive: theme wave-ride mechanical translation "
                   "passes the v2 gate on the SOLO claim face (registration "
                   "is a separate frozen step; this batch judges only) | "
                   "TJ-SOLO-x2 cost-stress g1 pass="
                   f"{gates['TJ-SOLO-x2']['g1']['pass_v2']} (descriptive)")
    else:
        verdict = ("judged_negative: family-level honest closure -- the "
                   "break-line + rebirth system cannot pass the null-"
                   "calibrated v2 gate on the algorithmic ignition full set "
                   "(FULL face = practical disclosure regardless of reading; "
                   "0.75 deep-break variant readings disclosed in the "
                   "sensitivity legs; line NOT reset by variants per E24-ii)")

    led = sg.append_ledger(
        batch_name=BATCH, batch_trials=8004,
        file_name="results/theme_judge_p1/theme_judge_p1_results.json",
        evidence_cutoff=CUTOFF,
        note=("theme wave-ride judgment batch: 4 judged cells (E28 strata "
              "x costs) + 4x2000 same-mask random-ignition nulls; "
              "T-2026-10-04-167-P1 s3"),
        prev_total=(int(prev_led["prev_total"]) if prev_led else None))
    if prev_led:
        led = dict(prev_led)  # r259 prev-echo guard: redo keeps row byte-stable

    payload = {
        "batch": BATCH, "prereg": PREREG, "verdict": verdict,
        "evidence_cutoff": CUTOFF,
        "science_gates": {"cutoff_meta": sg.cutoff_meta(CUTOFF)},
        "panels_digest": st["panels_digest"], "facts": st["facts"],
        "gates": gates, "pbo_family": pbo_out,
        "m1_t_face": {"face": MAIN_FACE, "t_from_sharpe": t_val, "gate": m1},
        # r670: sens rows live under burn_state["cells"]["sensitivity"]
        # (cmd_run appends them into the cells dict) -- st["sensitivity"]
        # was a never-exercised path bug caught at first finalize.
        "cells": cells, "sensitivity": st["cells"]["sensitivity"],
        "nulls": st["nulls"],
        "census": census, "loo": st["loo"], "terciles": st["terciles"],
        "regime_segments": st["regime_segments"], "famous16": st["famous16"],
        "d6_real": st["d6_real"],
        "exit_axis": ("1-own-exit: break 0.80 (MINUS20_LINE single source) "
                      "+ rebirth 1.25/250td; engine default stack NOT "
                      "APPLICABLE (zero engine import; selftest-asserted)"),
        "banned_direction_gate": "ADMIT rc0 at freeze window (prereg sec.0.5)",
        "trials_ledger": led,
    }
    with open(RESULTS_JSON, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=1, sort_keys=True)

    if not redo:   # gate_attrition append (r248 law: entries list)
        att = json.load(open(ATTR_JSON, encoding="utf-8-sig"))
        att["entries"].append({
            "batch": BATCH, "ts": _now(), "kind": "judgment",
            "cells_ledger_delta": 8004,
            "ledger_total_after": led.get("total"),
            "gates": {"verdict": verdict, "main_face": MAIN_FACE,
                      "g1_pass": {f: gates[f]["g1"]["pass_v2"]
                                  for f in FACES},
                      "g2_eligible": {f: gates[f]["g2"]["eligible_v2"]
                                      for f in FACES},
                      "skill_lines": {f: gates[f]["g1"]["skill_line"]["line"]
                                      for f in FACES},
                      "null_mu": {f: gates[f]["null_mu"] for f in FACES}},
            "entries": [{"face": f, "g1": gates[f]["g1"]["pass_v2"],
                         "g2": gates[f]["g2"]["eligible_v2"],
                         "sharpe": cells[f]["sharpe_full"],
                         "role": ("claim" if f == MAIN_FACE else
                                  "cost_stress" if f == "TJ-SOLO-x2" else
                                  "practical_disclosure")}
                        for f in FACES],
        })
        # r670: write-side MUST be plain utf-8 -- utf-8-sig WRITES a BOM and
        # the attrition guard reads strict utf-8 (mechanism error on BOM).
        # utf-8-sig stays on the READ side (tolerant of legacy BOMs).
        with open(ATTR_JSON, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(att, fh, ensure_ascii=False, indent=1)
    print(json.dumps({"verdict": verdict, "main_g1": main_g1,
                      "main_g2": main_g2, "pbo": pbo_out.get("pbo"),
                      "t_value": round(t_val, 4),
                      "ledger_total": led.get("total")}, ensure_ascii=False))
    return 0


# ---------------------------------------------------------------- selftest

def _synth_series(kind, n):
    if kind == "break_rebirth":
        c = np.concatenate([
            np.linspace(1.0, 2.0, 10), np.linspace(2.0, 1.4, 5),
            np.linspace(1.4, 1.0, 5), np.linspace(1.0, 1.35, 5),
            np.full(max(0, n - 25), 1.35)])
    elif kind == "no_break":
        c = np.linspace(1.0, 1.5, n)
    else:
        c = np.concatenate([np.linspace(1.0, 2.0, 10),
                            np.linspace(2.0, 0.9, n - 10)])
    return c[:n]


def _seed_band_check():
    """Band-disjoint scan (frozen claim: [SEED, SEED+2000) vs registry).

    Near-below neighbors need their consumed extent; theme_persist's is
    DERIVED from its module substream map, everything else uses a
    conservative default extent of 3000 draws."""
    assert sg.SEED_REGISTRY.get("theme_judge_p1_nulls") == SEED_NULLS
    lo, hi = SEED_NULLS, SEED_NULLS + K_NULLS
    others = {k: v for k, v in sg.SEED_REGISTRY.items()
              if isinstance(v, int) and v != SEED_NULLS}
    problems = []
    for k, s in others.items():
        if lo <= s < hi:
            problems.append(f"base seed {k}={s} inside my band")
            continue
        if s < lo and lo - s < 30000:
            extent = 3000
            if s == sg.SEED_REGISTRY.get("theme_persist_p1_nulls"):
                extent = max(TP.SUB_NULL + TP.K_NULLS, TP.SUB_PERM + 15,
                             TP.SUB_CLUST + 15)
            if lo - (s + extent) < 2000:
                problems.append(f"{k}={s}: gap {lo - (s + extent)} < 2000")
        if s > hi and s - hi < 2000:
            problems.append(f"{k}={s}: gap above band {s - hi} < 2000")
    return problems


def selftest(_=None):
    tally = [0, 0]

    def chk(name, cond):
        tally[0 if cond else 1] += 1
        print(f"  [selftest] {name}: {'PASS' if cond else 'FAIL'}")

    # 1. engine import-graph purity (fresh process, after runner import)
    eng = [m for m in sys.modules if m == "engine" or m.startswith("engine.")]
    chk("engine absent from runner import graph", not eng)
    # 2. simulate is the single-source exit implementation
    chk("simulate identity is theme_persist_p1.simulate",
        simulate is TP.simulate)
    src = open(os.path.abspath(__file__), encoding="utf-8").read()
    chk("runner defines no own exit implementation",
        ("def " + "simulate") not in src)
    bad = [w for w in ("take_" + "profit", "initial_" + "stop", "trail"
                       + "ing", "time_" + "decay", "loss_" + "time",
                       "global_" + "hard_" + "limit") if w in src]
    chk("engine default-stack names absent (no bridge keys)", not bad)
    # 3. seed band disjoint
    probs = _seed_band_check()
    chk(f"seed band [{SEED_NULLS},{SEED_NULLS + K_NULLS}) disjoint "
        f"({'; '.join(probs) if probs else 'zero clash'})", not probs)
    # 4. dedup + strata hermetic (probe kernels)
    eps = [{"code": "159915", "ignition_date": "2024-09-30"},
           {"code": "sz159915", "ignition_date": "2024-09-30"},
           {"code": "sh510050", "ignition_date": "2020-07-06"},
           {"code": "510050", "ignition_date": "2020-07-06"},
           {"code": "510300", "ignition_date": "2019-01-04"}]
    kept, dropped = P2.dedup(eps)
    chk("dedup canon: bare wins, (norm6,ign) identity",
        len(kept) == 3 and len(dropped) == 2
        and kept[0]["code"] == "159915")
    byday, cl, so = P2.strata(kept + [{"code": f"x{i}",
                                       "ignition_date": "2024-09-30"}
                                      for i in range(9)])
    chk("strata split: >=10 same-day = cluster face",
        len(cl) == 10 and len(so) == 2)
    # 5. census reasons hermetic
    r1, ill1 = _census_reasons(TP.simulate(
        list(_synth_series("break_rebirth", 40)))["trades"])
    chk("break_rebirth reasons subset of legal set, zero illegal",
        ill1 == 0 and set(r1) <= set(CENSUS_LEGAL)
        and r1[0] == "first_entry" and "break_line_sell" in r1
        and "rebirth_buy" in r1)
    r2, ill2 = _census_reasons(TP.simulate(
        list(_synth_series("no_break", 40)))["trades"])
    chk("no_break: single first_entry, censored at window end",
        ill2 == 0 and r2 == ["first_entry"])
    r3, ill3 = _census_reasons(TP.simulate(
        list(_synth_series("dead", 40)))["trades"])
    chk("dead face: first_entry + break_line_sell only",
        ill3 == 0 and r3 == ["first_entry", "break_line_sell"])
    # 6. COST_X1 + census sha16 identity (real artifacts)
    chk("COST_X1 single-source identity", abs(COST_X1 - 0.0013041) < 1e-9)
    chk("census artifact sha16 frozen identity",
        P2.sha16_file(V03) == V03_SHA16)
    # 7. accumulator == TP._pool equivalence on synthetic rides
    n_cal = 12
    cal = np.arange(n_cal, dtype=np.int32)
    rides_synth = [
        {"c": 0, "i0": 0, "wlen": 8, "rid": "a|d1", "etf": "a",
         "ign": "d1", "stratum": "TJ-SOLO", "famous": False, "tercile": 0},
        {"c": 0, "i0": 2, "wlen": 8, "rid": "a|d2", "etf": "a",
         "ign": "d2", "stratum": "TJ-SOLO", "famous": False, "tercile": 1},
        {"c": 1, "i0": 0, "wlen": 10, "rid": "b|d1", "etf": "b",
         "ign": "d1", "stratum": "TJ-FULL", "famous": True, "tercile": 0},
    ]
    closes2d = np.full((2, n_cal), np.nan)
    closes2d[0] = _synth_series("break_rebirth", n_cal)
    closes2d[1] = _synth_series("no_break", n_cal)
    cal2d = np.vstack([cal, cal])
    calendar = [f"2026-01-{i + 1:02d}" for i in range(n_cal)]
    _G.update(closes=closes2d, cal=cal2d, n_cal=n_cal,
              lens=np.asarray([n_cal, n_cal], dtype=np.int64),
              meta={"digest": "selftest", "calendar": calendar},
              rides_by={"TJ-FULL": [rides_synth[2]],
                        "TJ-SOLO": rides_synth[:2]})
    dbr = {r["rid"]: [calendar[j] for j in
                      cal2d[r["c"], r["i0"]:r["i0"] + r["wlen"]]]
           for r in rides_synth}
    fast = _pooled_sharpe_accum(closes2d[1, 0:10], cal2d[1, 0:10],
                                n_cal, COST_X1)
    eq_map = {"b|d1": dict(zip(
        dbr["b|d1"], TP.simulate(list(closes2d[1, 0:10]),
                                 cost=COST_X1)["eq"]))}
    _, pooled, _ = TP._pool(TP._daily_rets(eq_map))
    chk("accumulator path == TP._pool single-source path",
        abs(fast - _sharpe(pooled)) < 1e-12)
    # 8. grammar ledger: zero consumed GENERATION grammar row with the
    #    event-anchor/break/rebirth triple (consumption-declaration rows are
    #    the declared exception; retry legality = prereg sec.0.5)
    txt = open(LEDGER_PATH, encoding="utf-8").read()
    gen_rows = [ln for ln in txt.splitlines() if "gen=" in ln]
    clash = [ln[:60] for ln in gen_rows
             if "事件锚" in ln and "破线" in ln and "复活" in ln]
    chk("grammar ledger: zero generation-grammar clash", not clash)
    # 9. mini-pipeline determinism (synthetic panels, K=4, chunk=2)
    mod = sys.modules[__name__]
    for attr, val in (("K_NULLS", 4), ("CHUNK", 2)):
        setattr(mod, attr, val)
    try:
        outs = []
        for _ in range(2):
            frags = [_null_chunk({"kind": "null_chunk", "stratum": st,
                                  "ci": ci})
                     for st in STRATA for ci in range(0, 4, 2)]
            sens = [_sens_task({"kind": "sens", "stratum": "TJ-SOLO",
                                "bl": 0.75, "rb": 1.20})]
            outs.append(json.dumps({"frags": frags, "sens": sens},
                                   sort_keys=True))
        chk("mini-pipeline double-run byte identity", outs[0] == outs[1])
        ks_union = sorted({k for fr in frags for k in fr["ks"]})
        chk("mini-pipeline ks coverage == 0..K_NULLS-1 (r670 ci-semantics "
            "guard: chunk ks must tile the null index space exactly once)",
            ks_union == list(range(4)))
    finally:
        for attr, val in (("K_NULLS", 2000), ("CHUNK", 100)):
            setattr(mod, attr, val)
    print(f"selftest: {tally[0]} PASS, {tally[1]} FAIL")
    return 0 if tally[1] == 0 else 1


# ---------------------------------------------------------------- main

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["run", "finalize", "selftest"])
    args = ap.parse_args()
    return {"run": cmd_run, "finalize": cmd_finalize,
            "selftest": selftest}[args.cmd](args)


if __name__ == "__main__":
    sys.exit(main())
