"""CN-REGIME-POLICY-P1 pre-freeze probe (T-2026-09-26-73 s3 slice-3).

Evidence-only fact collector for the prereg freeze (R250 probe precedent:
facts frozen into results/cn_regime_policy_probe.json and cited by the
prereg; zero backtest verdicts here -- running the real corpus through
the probe is data-census, not a judged face).

Design lineage:
  - Order O-20260926-0926 s3 (CN-REGIME-POLICY model); digest
    DIGEST-20260926-t73-s2-sliceB-policy.md = the s2 prior-research
    obligation face (policy calendar law NOT VALIDATED as alpha on the
    F1 primary face; P4B={4,7,10,12} source-corrected politburo months;
    directionally weak-negative spreads -> s3 scope-down face:
    v3 ladder reuse + policy-month DEFENSIVE tilt, never an alpha slot).
  - Regime axis = imported frozen deep-replay layer (regime_deep_replay,
    REGIME_GUARD_DEEP_REPLAY_V2 lineage); ladder = market_clock_call
    POSITION_LADDER (T-74 L5 frozen canon, HOT bonus excluded = v3-only
    face honest note).
"""
import json
import os
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import pandas as pd

import regime_deep_replay as RDR
from market_clock_call import POSITION_LADDER

CORPUS = os.path.join(ROOT, "data", "daily", "sh510300.csv")
OUT = os.path.join(ROOT, "results", "cn_regime_policy_probe.json")
EVIDENCE_CUTOFF = "2026-09-22"
P4B = (4, 7, 10, 12)          # slice-B source-corrected politburo months


def load_corpus():
    df = pd.read_csv(CORPUS, encoding="utf-8-sig")
    df["date"] = pd.to_datetime(df["date"])
    df = df.set_index("date").sort_index()
    return df


def main():
    t0 = time.time()
    df = load_corpus()
    bench = RDR.load_index_bench()
    mats, _ds, _br = RDR.run_matrices(bench)
    states = mats["v3"]["states"]

    idx = df.index
    s = pd.Series(states).sort_index()
    # exact date-set alignment (R250 law: date-drift refusal downstream)
    state_dates = set(pd.Timestamp(d) for d in s.index)
    corpus_dates = set(idx)
    only_corpus = sorted(str(d.date()) for d in corpus_dates - state_dates)
    only_states = sorted(str(d.date()) for d in state_dates - corpus_dates)
    w = s[(s.index >= idx[0]) & (s.index <= idx[-1])]
    covered = int(sum(pd.Timestamp(d) in corpus_dates for d in w.index))
    # gate face = corpus coverage (every ETF bar must have a state);
    # bench pre-ETF era (2005..2012) states are expected residue,
    # disclosed by count only (prevents JSON bloat).
    pre_era = sorted(pd.Timestamp(d) for d in state_dates - corpus_dates)

    nan_face = {c: int(df[c].isna().sum()) for c in
                ("open", "high", "low", "close", "volume", "amount")}
    adv20 = (df["volume"] * df["close"]).rolling(20).mean()

    months = pd.Series(idx.month, index=idx)
    n_policy_bars = int(months.isin(P4B).sum())

    payload = {
        "meta": {
            "ticket": "T-2026-09-26-73", "slice": "s3 slice-3 probe",
            "probe": "scripts/cn_regime_policy_probe.py",
            "evidence_cutoff": EVIDENCE_CUTOFF,
            "p4b_months": list(P4B),
            "ladder_canon": {k: POSITION_LADDER[k]
                             for k in sorted(POSITION_LADDER)},
            "ladder_source": "market_clock_call.POSITION_LADDER "
                             "(T-74 L5 frozen canon; HOT bonus excluded "
                             "-- v3-only face)",
            "regime_source": "regime_deep_replay.run_matrices v3 "
                             "(imported frozen layer)",
        },
        "corpus": {
            "file": "data/daily/sh510300.csv", "rows": len(df),
            "first": str(idx[0].date()), "last": str(idx[-1].date()),
            "nan_counts": nan_face,
            "cutoff_equals_last": str(idx[-1].date()) == EVIDENCE_CUTOFF,
        },
        "v3_replay": {
            "bench_rows": len(bench),
            "bench_first": str(bench.index[0].date()),
            "bench_last": str(bench.index[-1].date()),
            "bench_cutoff_equals_last":
                str(bench.index[-1].date()) == EVIDENCE_CUTOFF,
            "window_states": covered,
            "window_state_share_of_states":
                round(covered / len(w), 4) if len(w) else None,
            "state_counts_window":
                {k: int(v) for k, v in w.value_counts().items()},
            "state_changes_window":
                int((w != w.shift()).sum()),
            "corpus_only_dates": only_corpus,
            "corpus_fully_covered": not only_corpus,
            "pre_era_states_only_count": len(pre_era),
            "pre_era_states_first":
                str(pre_era[0].date()) if pre_era else None,
            "pre_era_states_last":
                str(pre_era[-1].date()) if pre_era else None,
            "pre_era_note": "bench index face starts 2005-04-08, ETF "
                            "corpus starts 2012-05-28; pre-ETF-era bench "
                            "days are expected residue, never a gap",
        },
        "capacity": {
            "adv20_cny_min": float(adv20.min()),
            "adv20_cny_median": float(adv20.median()),
            "max_trade_notional_cny": 1_000_000.0 * 0.80,
            "adv_cap_rate": 0.01,
            "cap_min_cny": float(adv20.min()) * 0.01,
            "non_binding_margin_x":
                round(float(adv20.min()) * 0.01
                      / (1_000_000.0 * 0.80), 1),
        },
        "policy_axis": {
            "policy_month_bars_in_window": n_policy_bars,
            "non_policy_month_bars": len(df) - n_policy_bars,
            "exhaustive_c12_4": 495,
        },
        "elapsed_sec": round(time.time() - t0, 1),
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=1)
    print("probe ->", OUT)
    print(json.dumps(payload["v3_replay"], ensure_ascii=False))
    print(json.dumps(payload["capacity"], ensure_ascii=False))


if __name__ == "__main__":
    main()
