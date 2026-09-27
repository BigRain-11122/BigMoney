import json

p = 'results/gate_attrition.json'
d = json.load(open(p, encoding='utf-8'))
row = {
    "batch": "MASS_TRIAL_W1",
    "ts": "2026-09-27 23:1x",
    "kind": "measurement",
    "cells_ledger_delta": 975,
    "ledger_total_after": 287526,
    "gates": {
        "screen_pass": {"n_candidates": 975, "n_survivors": 166,
                        "line": "beat_rate_6m>=0.60 AND trades>=30 AND dd>=-0.35"},
        "null_face": {"p50": 0.45, "p95": 0.5333, "n": 20,
                      "note": "null max 0.55 < 0.60 line; margin thin, disclosed"},
        "dedup_face": {"param_dupes": 1, "signal_dupes": 4, "rejections": 2,
                       "dead_signal": 42},
        "control_face": {"n_defaults": 75, "n_pass": 8,
                         "n_signal_error": 2,
                         "note": "4/6 registered-trader entry families pass at defaults "
                                 "(low_vol_long/engulf_reversal/needle_probe/"
                                 "vol_drought_reversal); composite families excluded "
                                 "from wave-1 grammar per prereg; 2 errors = "
                                 "month-required-arg defaults rows"}
    },
    "eliminated": 975 - 166,
    "refs": {"prereg": "research/MASS_TRIAL_W1_PREREG.md",
             "ticket": "T-2026-09-27-94"}
}
d['entries'].append(row)
d['history'].append(row)
json.dump(d, open(p, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('appended; entries now', len(d['entries']))
