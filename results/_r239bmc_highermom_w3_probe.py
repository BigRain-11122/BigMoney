# INNOVATION-QUOTA-SLOT-3 supply probe (bm-c r239): ASTYLE_ZOO #95
# index_higher_mom_timing -- frozen-parameter descriptive facts (zoo freeze
# r263 bm-b DIGEST-20260926-wave10-paramfreeze-95-96.md sec.2).
# Deterministic, in-repo, zero-network. Facts only, no judgment, no lookahead.
import json
import sys

import pandas as pd

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

CUTOFF = "2026-09-28"  # evidence_cutoff frozen at prereg time (P-5C binding)
MOM_WINDOW = 20
EMA_SPAN = 90
ORDERS = (3, 4, 5)
STOP_LINE = -0.10  # since-entry cumulative return stop (single-position)

df = pd.read_csv("data/daily/sh510300.csv")
df = df[df["date"] <= CUTOFF].reset_index(drop=True)
ret = df["close"].pct_change()

facts = {
    "probe": "INNOVATION-QUOTA-SLOT-3 higher-moment timing supply probe",
    "batch_family": "index_higher_mom_timing (ASTYLE_ZOO #95, param-frozen r263 bm-b)",
    "anchor_face": {
        "path": "data/daily/sh510300.csv",
        "reader": "pd.read_csv raw (date,open,high,low,close,volume,amount)",
        "cutoff": CUTOFF,
        "warmup_law": "ret first-valid idx 1 -> moment(20) first-valid idx 20 -> "
        "EMA(90, adjust=False) first defined at idx 20 -> signal first decidable idx 21 "
        "(diff vs prior EMA); position onset t+1 (signal-at-close, zero lookahead)",
    },
    "panel": {
        "rows_cutoff": int(len(df)),
        "first_date": str(df["date"].iloc[0]),
        "last_date": str(df["date"].iloc[-1]),
        "close_min": float(df["close"].min()),
        "close_max": float(df["close"].max()),
        "ret_first_valid_idx": int(ret.first_valid_index()),
    },
    "legs": {},
}

for n in ORDERS:
    mom = ret.pow(n).rolling(MOM_WINDOW, min_periods=MOM_WINDOW).mean()
    ema = mom.ewm(span=EMA_SPAN, adjust=False).mean()
    rising = ema.diff() > 0  # signal at close of day t (uses t-1..t data only)
    sig = rising.shift(1).fillna(False).astype(bool)  # position day t+1 (T+1 onset)
    sig.iloc[:21] = False  # warmup guard: below idx 21 not decidable
    # frozen state machine: position episodes = onsets of the T+1 signal
    # (sig False->True); exit on falling signal; stop-line exit when
    # since-entry cumulative ret < -10%; after stop, re-entry only at the
    # NEXT sig episode onset (conservative stop reading).
    entries = 0
    stops = 0
    held = 0
    in_pos = False
    entry_px = None
    sig_prev = False
    for i in range(len(df)):
        s = bool(sig.iloc[i])
        if in_pos:
            r = df["close"].iloc[i] / entry_px - 1.0
            if r < STOP_LINE:
                in_pos = False
                stops += 1
            elif not s:
                in_pos = False
        if (not in_pos) and s and not sig_prev:
            in_pos = True
            entry_px = df["close"].iloc[i]
            entries += 1
        if in_pos:
            held += 1
        sig_prev = s
    facts["legs"][f"mom{n}"] = {
        "moment_first_valid_idx": int(mom.first_valid_index()),
        "ema_first_valid_idx": int(ema.first_valid_index()),
        "signal_first_decidable_idx": 21,
        "decidable_days": int(len(df) - 21),
        "raw_signal_long_days": int(rising.sum()),
        "position_days_after_stop_overlay": held,
        "entries": entries,
        "stop_exits": stops,
    }

# descriptive: extreme single-day moves in-panel (context for moment legs)
worst = ret.idxmin()
best = ret.idxmax()
facts["extreme_days"] = {
    "worst_day": {"date": str(df["date"].iloc[worst]), "ret": float(ret.iloc[worst])},
    "best_day": {"date": str(df["date"].iloc[best]), "ret": float(ret.iloc[best])},
}

# D6 loader face check (mirror W1: cn_rev_tilt_p1.load_member_rets + REG6)
import os

loader_face = (
    "scripts/cn_rev_tilt_p1.py present"
    if os.path.exists("scripts/cn_rev_tilt_p1.py")
    else "MISSING"
)
facts["d6_loader_face"] = loader_face

out_path = "results/_r239bmc_highermom_w3_probe_facts.json"
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(facts, f, ensure_ascii=False, indent=1)
print(json.dumps(facts, ensure_ascii=False, indent=1))
