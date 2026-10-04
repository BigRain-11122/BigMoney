"""r685 bm-a: append MASS_TRIAL_W3 screen attrition row to gate_attrition.json.

Mirror of MASS_TRIAL_W2 row form (same gate faces). Append-only face (r448
guard: entries monotone). Roundtrip checked first (r678); surgical tail insert
if dump not byte-identical.
"""
import json, time

PATH = r"results/gate_attrition.json"
raw = open(PATH, "rb").read()
d = json.loads(raw.decode("utf-8"))
assert not any(e.get("batch") == "MASS_TRIAL_W3" for e in d["entries"]), "W3 row exists"

row = {
    "batch": "MASS_TRIAL_W3",
    "ts": time.strftime("%Y-%m-%d %H:%M:%S"),
    "kind": "measurement",
    "cells_ledger_delta": 4814,
    "ledger_total_after": 646799,
    "gates": {
        "screen_pass": {
            "n_candidates": 4814, "n_survivors": 785,
            "line": "beat_rate_6m>=0.60 AND trades>=30 AND dd>=-0.35",
        },
        "null_face": {
            "p50": 0.45, "p95": 0.5333, "n": 20,
            "note": "null max 0.55 < 0.60 line; margin thin (0.0467); third "
                    "consecutive wave identical p95 0.5333 (w1/w2/w3), disclosed",
        },
        "dedup_face": {
            "param_dupes": 417, "signal_dupes": 734, "rejections": 9,
            "dead_signal": 227,
            "cross_wave_param_dupes": 916, "cross_wave_signal_dupes": 358,
            "cross_wave_note": "1274 cross-wave collapses vs prereg pred "
                "150-600: above upper edge 2.1x, mechanism review disclosed at "
                "enrollment r481 (rate 21.9% vs w2 28.6% = base-growth-"
                "consistent on base 5811), per sec.5#6",
        },
        "control_face": {
            "n_defaults": 75, "n_pass": 5, "n_signal_error": 2,
            "passed": ["patterns.vol_drought_reversal", "volatility.low_vol_long",
                       "patterns.island_reversal", "patterns.morning_star",
                       "folk.ants_climb"],
            "stability_note": "identical 5 controls + identical beat values vs "
                "w2 (same corrected-engine stack, same cutoff 2026-09-22) -- "
                "first same-stack cross-wave control replication; w1 face kept "
                "as history; 2 errors = month-required-arg default rows "
                "DEF-26/27 frozen carry (candidate face zero error)",
        },
    },
    "refs": {
        "results": "results/mass_trial/w3_screen_summary.json",
        "prereg": "research/MASS_TRIAL_W3_PREREG.md",
        "ticket": "T-2026-10-03-158",
    },
    "note": "T-158 wave-3 stage-1 screen close: 4814 cells, 785 survivors "
             "(16.3%), four-shard relay bm-c 0-2 + bm-a 3 (r482/r685); ledger "
             "641985->646799; shard-3 burner-side session closeout r685 "
             "(1228/1228 exact, 0 dup); mid-flight 1227 re-burn dup lines "
             "id-deduped keep-first per r482 bm-c law, zero info loss "
             "(elapsed_s-only variance, asserted)",
    "eliminated": 4029,
}

d["entries"].append(row)
out = json.dumps(d, ensure_ascii=False, indent=1) + ("\n" if raw.endswith(b"\n") else "")
rt = out.encode("utf-8")
if rt == raw:
    open(PATH, "wb").write(rt)
    method = "roundtrip-identical dump"
else:
    # surgical: insert entry block before the entries-closing bracket
    raise SystemExit("roundtrip differs -- surgical path required (not hit this "
                    "run; rerun with surgical editor)")
# post-write verify
d2 = json.load(open(PATH, encoding="utf-8"))
assert len(d2["entries"]) == len(d["entries"])
assert any(e.get("batch") == "MASS_TRIAL_W3" for e in d2["entries"])
print(json.dumps({"appended": "MASS_TRIAL_W3", "entries": len(d2["entries"]),
                  "method": method, "eliminated": 4029,
                  "ledger_total_after": 646799}))
