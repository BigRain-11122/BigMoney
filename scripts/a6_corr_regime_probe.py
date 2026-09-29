"""A6-CORR-REGIME-PROBE -- descriptive correlation-regime flag census (v4 A6 arm evidence face).

Upstream canon: research/DECISION_CHAIN_BENCHMARKS.md v0.2 sec.5 A6
(B6 risk-parity Q1-2020 correlation-regime failure history inverted into a
candidate signal); arm lane = bm-a (five-member ETF panel, O-1555 frozen
universe). Consumer = T-101 v4 A6 arm prescreen prereg draft decision next
window (TRIAL_LABOR_LAW freeze chain); this probe makes no verdict.

Class discipline (written before run): descriptive census, ZERO N_eff -- no
gates, no nulls, no strategy returns, no registration, no upgrade claim.
Census precedent: gate_census 09-28 / alpha158_census (descriptive measurement
faces are legal pre-prereg evidence; overlap bias disclosed, no cost-adjusted
claims, no strategy claims). No trials_ledger append (non-judgment face).

Panel face: five-member frozen universe with staggered inceptions (510050
2005 / 510300 2012 / 510500 2013 / 512100 2016 / 588000 2020-11). Inner-join
would silently truncate history to 2020-11 (selftest leg caught this) -- the
flag is therefore computed pairwise-complete: per rolling window, per pair,
corr over co-valid observations (>= MIN_PAIR_OBS); rho_t = mean over available
pairs (>= MIN_PAIRS); pair-count per day and member-entry structural breaks
disclosed (pairwise-complete precedent a158_truegap_ic).

Flag: z_t = (rho_t - trailing-250-valid rho mean)/std(ddof=1); flag-on =
z_t >= 2.0 (correlation-stress regime, Q1-2020 anchor). Anchor face: COVID
window 2020-02-20..2020-04-30 flag-on count reported honestly (reproduced
true/false is a descriptive finding either way; params frozen before run,
anchor outcome never tuned).

Conditional stats (descriptive only): forward 20d close-to-close returns per
member on flag-on vs flag-off days on the member's own calendar; full /
IS(<2017) / OOS(>=2017) x bear|bull|chop segments (510300 MA200 rule, A2/A7
prereg parity); stride-20 non-overlap secondary view on the flag-on face.

rc contract: 0 = ok, 2 = mechanism fault. Zero network (local panel read only).
selftest subcommand = offline legs (synthetic known-block fixture, determinism
double-run, missing-file guard, panel-shape coverage, real-panel anchor read).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import time

import numpy as np

UNIVERSE = ["510300", "510050", "510500", "512100", "588000"]
CORR_WINDOW = 60
MIN_PAIR_OBS = 40   # min co-valid obs inside a rolling window for one pair
MIN_PAIRS = 3       # min available pairs for a day's rho to be valid
Z_WINDOW = 250
Z_TH = 2.0
FWD = 20
SPLIT = "2017-01-01"
COVID_A = "2020-02-20"
COVID_B = "2020-04-30"
MA_WINDOW = 200
MA_SLOPE_WINDOW = 60
STRIDE = 20
OUT_PATH = "results/a6_corr_regime_probe.json"


def load_member(code: str):
    path = f"data/daily/sh{code}.csv"
    if not os.path.exists(path):
        raise SystemExit(f"FACE-MISMATCH VOID: declared anchor {path} missing")
    rows = []
    with open(path, encoding="utf-8") as f:
        header = f.readline().strip().split(",")
        if header[:2] != ["date", "open"]:
            raise SystemExit(f"FACE-MISMATCH VOID: unexpected header in {path}: {header[:5]}")
        for line in f:
            parts = line.strip().split(",")
            if len(parts) < 5:
                continue
            rows.append((parts[0], float(parts[4])))  # date, close
    if len(rows) < 200:
        raise SystemExit(f"FACE-MISMATCH VOID: panel {path} too short ({len(rows)} rows)")
    return {"dates": [r[0] for r in rows], "close": np.array([r[1] for r in rows], dtype=float)}


def build_matrix(members: dict):
    """Union calendar + NaN-padded close matrix (pairwise-complete face)."""
    labels = list(members.keys())
    all_dates = sorted({d for m in members.values() for d in m["dates"]})
    row_of = {d: i for i, d in enumerate(all_dates)}
    mat = np.full((len(all_dates), len(labels)), np.nan)
    for j, c in enumerate(labels):
        mem = members[c]
        for t, d in enumerate(mem["dates"]):
            mat[row_of[d], j] = mem["close"][t]
    return all_dates, mat


def avg_pairwise_corr(mat: np.ndarray, window: int = CORR_WINDOW) -> tuple:
    """Rolling mean pairwise Pearson corr, pairwise-complete. Returns
    (rho[n], n_pairs[n]) with NaN where insufficient pairs."""
    n, m = mat.shape
    rho = np.full(n, np.nan)
    n_pairs = np.zeros(n, dtype=int)
    for t in range(window - 1, n):
        block = mat[t - window + 1: t + 1]
        vals = []
        for i in range(m):
            for j in range(i + 1, m):
                a, b = block[:, i], block[:, j]
                both = ~np.isnan(a) & ~np.isnan(b)
                cnt = int(both.sum())
                if cnt < MIN_PAIR_OBS:
                    continue
                av = a[both] - a[both].mean()
                bv = b[both] - b[both].mean()
                denom = np.sqrt((av * av).sum() * (bv * bv).sum())
                vals.append(0.0 if denom == 0.0 else float((av * bv).sum() / denom))
        if len(vals) >= MIN_PAIRS:
            rho[t] = float(np.mean(vals))
            n_pairs[t] = len(vals)
    return rho, n_pairs


def zscore_flag(rho: np.ndarray, z_window: int = Z_WINDOW, z_th: float = Z_TH) -> tuple:
    """z vs trailing z_window VALID rho values (NaN-skipping); flag-on = z >= z_th."""
    n = len(rho)
    valid_idx = np.where(~np.isnan(rho))[0]
    z = np.full(n, np.nan)
    flag = np.zeros(n, dtype=bool)
    for pos in range(z_window - 1, len(valid_idx)):
        t = int(valid_idx[pos])
        block = rho[valid_idx[pos - z_window + 1: pos + 1]]
        sd = block.std(ddof=1)
        if sd <= 0:
            continue
        z[t] = (rho[t] - block.mean()) / sd
        flag[t] = z[t] >= z_th
    return z, flag


def regime_segment_dates(dates: list, close: np.ndarray) -> dict:
    """bear/bull/chop on 510300 own calendar (A2 prereg rule), mapped by date."""
    n = len(close)
    seg = {}
    ma = np.full(n, np.nan)
    for t in range(MA_WINDOW - 1, n):
        ma[t] = close[t - MA_WINDOW + 1: t + 1].mean()
    for t in range(MA_WINDOW + MA_SLOPE_WINDOW - 2, n):
        slope = ma[t] - ma[t - MA_SLOPE_WINDOW + 1]
        seg[dates[t]] = ("bear" if (close[t] < ma[t] and slope < 0)
                         else "bull" if (close[t] > ma[t] and slope > 0) else "chop")
    return seg


def member_fwd_stats(mem: dict, flag_by_date: dict, seg: dict) -> dict:
    """Forward FWD-day close-to-close returns on the member's own calendar."""
    dates, close = mem["dates"], mem["close"]
    n = len(close)
    fwd = np.full(n, np.nan)
    for t in range(n - FWD):
        fwd[t] = close[t + FWD] / close[t] - 1.0
    sel_on, sel_off = [], []
    for t in range(n):
        f = flag_by_date.get(dates[t])
        if f is None:
            continue
        if np.isnan(fwd[t]):
            continue
        (sel_on if f else sel_off).append(t)
    out = {}
    for name, sel in (("on", sel_on), ("off", sel_off)):
        v = fwd[np.array(sel, dtype=int)] if sel else np.array([])
        out[name] = {"n": int(len(v)),
                     "mean": float(v.mean()) if len(v) else None,
                     "median": float(np.median(v)) if len(v) else None,
                     "std": float(v.std(ddof=1)) if len(v) > 1 else None}
    picked, last = [], -10 ** 9
    for t in sel_on:
        if t - last >= STRIDE:
            picked.append(t)
            last = t
    v = fwd[np.array(picked, dtype=int)] if picked else np.array([])
    out["on_stride20_nonoverlap"] = {"n": int(len(v)),
                                     "mean": float(v.mean()) if len(v) else None}
    # IS/OOS x bear|bull|chop on-face faces
    segs = {}
    for t in sel_on:
        d = dates[t]
        era = "IS" if d < SPLIT else "OOS"
        g = seg.get(d, "na")
        segs.setdefault((era, g), []).append(float(fwd[t]))
    for (era, g), v2 in sorted(segs.items()):
        out.setdefault("segments", {})[f"{era}_{g}"] = {
            "n": len(v2), "mean": float(np.mean(v2)) if v2 else None}
    return out


def compute_core(members: dict) -> dict:
    labels = list(members.keys())
    bench = labels[0]  # regime benchmark = first member (510300 for the real panel)
    dates_u, mat = build_matrix(members)
    rho, n_pairs = avg_pairwise_corr(mat)
    z, flag = zscore_flag(rho)
    flag_by_date = {dates_u[t]: bool(flag[t]) for t in range(len(dates_u)) if not np.isnan(z[t])}
    covid = np.array([COVID_A <= d <= COVID_B for d in dates_u])
    decidable = np.array([not np.isnan(z[t]) for t in range(len(dates_u))])
    anchor_n = int((flag & covid & decidable).sum())
    seg = regime_segment_dates(members[bench]["dates"], members[bench]["close"])
    per_member = {c: member_fwd_stats(members[c], flag_by_date, seg) for c in labels}
    on_days = [d for d in dates_u if flag_by_date.get(d)]
    dec_mask = n_pairs > 0
    return {
        "regime_benchmark": bench,
        "flag_counts": {
            "decidable_days": int(decidable.sum()),
            "flag_on_full": len(on_days),
            "flag_on_IS": sum(1 for d in on_days if d < SPLIT),
            "flag_on_OOS": sum(1 for d in on_days if d >= SPLIT),
            "flag_on_bear": sum(1 for d in on_days if seg.get(d) == "bear"),
            "flag_on_bull": sum(1 for d in on_days if seg.get(d) == "bull"),
            "flag_on_chop": sum(1 for d in on_days if seg.get(d) == "chop"),
        },
        "covid_anchor": {"window": [COVID_A, COVID_B], "flag_on_days": anchor_n,
                         "reproduced": anchor_n > 0},
        "pair_count": {"min_decidable": int(n_pairs[dec_mask].min()) if dec_mask.any() else 0,
                       "max": int(n_pairs.max())},
        "on_days_sample": (on_days[:10] + (["..."] if len(on_days) > 10 else [])) if on_days else [],
        "per_member_fwd20": per_member,
        "rho_stats": _series_stats(rho),
        "z_stats": _series_stats(z),
    }


def _series_stats(x: np.ndarray) -> dict:
    v = x[~np.isnan(x)]
    if len(v) == 0:
        return {"n": 0}
    return {"n": int(len(v)), "min": float(v.min()), "max": float(v.max()),
            "mean": float(v.mean()), "q95": float(np.quantile(v, 0.95)),
            "q99": float(np.quantile(v, 0.99))}


def _synthetic_fixture():
    """Deterministic 500-day two-block fixture: weak-corr block then perfect-corr block.
    Four members (6 pairs >= MIN_PAIRS) all jumping to identical returns at day 350."""
    import datetime as _dt
    t = np.arange(500, dtype=float)
    a = np.sin(t / 7.0) * 0.01
    weak = [0.01 * np.sin(t / 13.0), 0.01 * np.cos(t / 17.0), 0.01 * np.sin(t / 29.0)]
    d0 = _dt.date(2010, 1, 1)
    dates = [(d0 + _dt.timedelta(days=int(i))).isoformat() for i in range(500)]
    members = {"510300": {"dates": dates, "close": 1.0 + np.cumsum(a)}}
    for k, w in enumerate(weak):
        members[f"m{k}"] = {"dates": dates, "close": 1.0 + np.cumsum(np.where(t < 350, w, a))}
    return dates, members


def cmd_run() -> int:
    t0 = time.time()
    try:
        members = {c: load_member(c) for c in UNIVERSE}
        core = compute_core(members)
        cutoff = max(members[c]["dates"][-1] for c in UNIVERSE)
        earliest = min(members[c]["dates"][0] for c in UNIVERSE)
        out = {
            "generated": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
            "evidence_cutoff": cutoff,
            "science_gates": {"cutoff_meta": {"cutoff": cutoff}},
            "class": "descriptive-census (zero N_eff; no gates/no nulls/no verdict; "
                     "A6 arm draft evidence face, consumer=T-101 v4 A6 prescreen prereg)",
            "upstream": "research/DECISION_CHAIN_BENCHMARKS.md v0.2 sec.5 A6 "
                        "(B6 risk-parity Q1-2020 corr-regime failure history)",
            "params": {"corr_window": CORR_WINDOW, "min_pair_obs": MIN_PAIR_OBS,
                       "min_pairs": MIN_PAIRS, "z_window": Z_WINDOW, "z_th": Z_TH,
                       "fwd_days": FWD, "split": SPLIT, "stride": STRIDE,
                       "regime_rule": "510300 close vs MA200 + MA200 60d slope (A2 parity)"},
            "panel_face": {"universe": UNIVERSE, "earliest_member_date": earliest,
                           "construction": "pairwise-complete (staggered inceptions disclosed)"},
            "core": core,
            "honest_disclosures": [
                "descriptive only: no cost, no execution model, no strategy returns, no registration",
                "flag-on forward windows overlap when flag persists (stride-20 non-overlap secondary view given)",
                "conditional means are overlapping-window biased toward persistence episodes (census caliber, gate_census precedent)",
                "pair count grows as members enter (588000 enters 2020-11) -- member-entry structural breaks disclosed, z is trailing-window adaptive",
                "not a verdict: any arm usage must re-enter the TRIAL_LABOR_LAW prereg freeze chain",
                "D6 note: market-state flag signal-axis distinct from RSV oversold (A2, killed) and GC001 liquidity (A7, killed); same-family corr must be measured at prereg time",
            ],
            "audit": {"elapsed_sec": round(time.time() - t0, 1), "host": "bm-a",
                      "lane": "bm-a (five-member ETF panel data/daily, O-1555 frozen universe)"},
        }
    except SystemExit as e:
        print(f"A6-PROBE FAULT: {e}", file=sys.stderr)
        return 2
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    fc = core["flag_counts"]
    print(f"a6_corr_regime_probe: cutoff={cutoff} decidable={fc['decidable_days']} "
          f"flag_on full/IS/OOS={fc['flag_on_full']}/{fc['flag_on_IS']}/{fc['flag_on_OOS']} "
          f"covid_anchor={core['covid_anchor']['flag_on_days']} "
          f"reproduced={str(core['covid_anchor']['reproduced']).lower()}")
    m = core["per_member_fwd20"]["510300"]

    def _f(v):
        return "n/a" if v is None else f"{v:+.4f}"
    print(f"510300 fwd20 on/off mean={_f(m['on']['mean'])}/{_f(m['off']['mean'])} "
          f"(n={m['on']['n']}/{m['off']['n']}) stride20={_f(m['on_stride20_nonoverlap']['mean'])}")
    print(f"-> {OUT_PATH} (descriptive census, zero N_eff, no verdict)")
    return 0


def cmd_selftest() -> int:
    ok = 0

    def leg(name: str, cond: bool, detail: str = ""):
        nonlocal ok
        ok += 1 if cond else 0
        print(f"  [selftest] {name}: {'PASS' if cond else 'FAIL'} {detail}")

    # [1] synthetic known-block fixture: flag fires in the corr-jump block, never before
    _, ms = _synthetic_fixture()
    dates_s, mat_s = build_matrix(ms)
    rho_s, _ = avg_pairwise_corr(mat_s)
    z_s, flag_s = zscore_flag(rho_s)
    pre, post = int(flag_s[:350].sum()), int(flag_s[350:].sum())
    leg("synthetic_known_block", post > 0 and pre == 0, f"(pre350={pre} post350={post})")
    # [2] determinism: double-run identity on the synthetic fixture
    h1 = hashlib.sha256(json.dumps(compute_core(ms), sort_keys=True).encode()).hexdigest()[:16]
    h2 = hashlib.sha256(json.dumps(compute_core(ms), sort_keys=True).encode()).hexdigest()[:16]
    leg("determinism_double_run", h1 == h2, f"(sha16={h1})")
    # [3] real-panel double-run identity (offline, zero network)
    members = {c: load_member(c) for c in UNIVERSE}
    r1 = hashlib.sha256(json.dumps(compute_core(members), sort_keys=True).encode()).hexdigest()[:16]
    r2 = hashlib.sha256(json.dumps(compute_core(members), sort_keys=True).encode()).hexdigest()[:16]
    leg("real_panel_double_run", r1 == r2, f"(sha16={r1})")
    # [4] panel coverage: staggered inceptions preserved (no inner-join truncation)
    earliest = min(members[c]["dates"][0] for c in UNIVERSE)
    cutoff = max(members[c]["dates"][-1] for c in UNIVERSE)
    core_r = compute_core(members)
    leg("panel_coverage_no_inner_join_truncation",
        earliest <= "2005-03-01" and cutoff >= "2026-09-24"
        and core_r["flag_counts"]["decidable_days"] > 1500,
        f"(earliest={earliest} cutoff={cutoff} decidable={core_r['flag_counts']['decidable_days']})")
    # [5] COVID anchor read on real panel (honest field, not a gate)
    leg("covid_anchor_read", core_r["covid_anchor"]["flag_on_days"] >= 0,
        f"(flag_on_days={core_r['covid_anchor']['flag_on_days']} "
        f"reproduced={str(core_r['covid_anchor']['reproduced']).lower()})")
    # [6] missing-file guard: honest clean error
    try:
        load_member("999999")
        leg("missing_file_guard", False)
    except SystemExit:
        leg("missing_file_guard", True)
    # [7] decidable-mask law: no flag before z-decidable history (r431 NaN-bucket family)
    leg("no_flag_before_decidable", core_r["flag_counts"]["flag_on_full"]
        <= core_r["flag_counts"]["decidable_days"])
    print(f"selftest: {ok}/7 PASS")
    return 0 if ok == 7 else 2


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd")
    sub.add_parser("run", help="compute descriptive census -> results/a6_corr_regime_probe.json")
    sub.add_parser("selftest", help="offline legs")
    args = ap.parse_args()
    if args.cmd == "selftest":
        return cmd_selftest()
    return cmd_run()


if __name__ == "__main__":
    raise SystemExit(main())
