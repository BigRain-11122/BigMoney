# -*- coding: utf-8 -*-
"""R263 bm-a -- CN-CORE-DDCTL-P1 s2 pre-freeze probe (T-2026-09-26-73
s3 slice-6, core-leg drawdown-control doctrine prereg candidate).

Freezes the NEW gate-axis facts the prereg cites (probe-authoritative):
  * core-leg (510880) trailing-252d drawdown series on the clean_value
    face (family signal convention: rolling on FULL union calendar, the
    timeline floor truncates only the SIM window -- never signal history);
  * hysteresis gate state machines for X in {10, 20} evaluated at the
    family quarterly rebalance grid from first_active (2013-07-17) on:
    ON when dd_r < -X/100, stays ON until dd_r > -X/200 (re-entry at
    half-threshold), else OFF;
  * episode spans / transition counts / occupancy per threshold;
  * core clean face vs raw close face max-abs diff (zero events + nan
    free -> expected 0).

Family frozen panel faces (T=3333 / first 2013-01-04 / cutoff 2026-09-22
/ events 3 / core zero / first_active 2013-07-17) are re-asserted from
the SAME single sources (SRP loaders, CS schedule) -- zero new judge
code, anti-repeat law. Offline, in-repo corpus, zero network.
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))
sys.path.insert(0, os.path.join(ROOT, "screening"))

import numpy as np
import pandas as pd

import t73_s2_style_rotation as SRP
import cn_core_sat_p1 as CS

OUT = os.path.join(ROOT, "results", "core_ddctl_probe.json")
CORE = CS.CORE
W_DD = 252          # trailing window (family W252 law, single window no search)
THRESHOLDS = (10, 20)   # percent dd trigger levels (frozen two-caliber axis)


def gate_states(dd_at, rebals, x):
    """Hysteresis state machine over ordered rebal points.
    ON when dd < -x/100; stays ON until dd > -x/200 (re-entry at half)."""
    st = "off"
    states, transitions = {}, []
    for r in rebals:
        d = dd_at[r]
        if st == "off":
            if d < -x / 100.0:
                st = "on"
                transitions.append(("on", r))
        else:
            if d > -x / 200.0:
                st = "off"
                transitions.append(("off", r))
        states[r] = st
    return states, transitions


def main():
    closeU, retU = SRP.load_panels()
    events = SRP.fund_events(retU)
    evt_set = {(s, e["date"]) for s in CS.LEGS_ALL
               for e in events.get(s, [])}
    cleanU, flagged = SRP.clean_rets(retU, events)
    cv_core = SRP.clean_value(closeU, cleanU, CORE)

    idx = closeU.index
    tl = idx[(idx >= pd.Timestamp("2013-01-01"))
             & (idx <= pd.Timestamp(CS.EVIDENCE_CUTOFF))]
    T = len(tl)

    # family availability face (satellite signals, strict-window rolling)
    sig = {s: ((1.0 + cleanU[s]).rolling(CS.W, min_periods=CS.W)
               .apply(lambda a: float(np.prod(a)), raw=True) - 1.0
               ).reindex(tl) for s in CS.SAT}

    # dd series: core clean close vs trailing-252 max (full history)
    roll_max = cv_core.rolling(W_DD, min_periods=W_DD).max()
    dd_full = cv_core / roll_max - 1.0
    dd_tl = dd_full.reindex(tl)

    # availability / first_active (family face re-derived)
    sched = CS.rebal_schedule(T)
    first_active_r = None
    for r in sched:
        avail = sum(1 for s in CS.SAT if np.isfinite(sig[s].iloc[r]))
        if avail >= CS.MIN_AVAIL:
            first_active_r = r
            break
    active_rebals = [r for r in sched if r >= first_active_r]

    dd_at = {r: float(dd_tl.iloc[r]) for r in active_rebals}
    dd_vals = np.array([dd_at[r] for r in active_rebals])

    # core clean vs raw face (zero events + nan free -> 0 diff expected)
    df = CS._leg_frame(CORE)
    raw_tl = df["close"].reindex(tl)
    facediff = float(np.nanmax(np.abs(
        cv_core.reindex(tl).to_numpy() - raw_tl.to_numpy())))

    arms = {}
    for x in THRESHOLDS:
        states, trans = gate_states(dd_at, active_rebals, x)
        on_rs = [r for r in active_rebals if states[r] == "on"]
        episodes, cur = [], None
        for r in active_rebals:
            if states[r] == "on" and cur is None:
                cur = {"from": str(tl[r].date())}
            elif states[r] == "off" and cur is not None:
                cur["to_exclusive"] = str(tl[r].date())
                episodes.append(cur)
                cur = None
        if cur is not None:
            episodes.append(cur)          # still ON at timeline end
        arms[f"DD{x}"] = {
            "x_pct": x,
            "on_transitions": sum(1 for t, _ in trans if t == "on"),
            "off_transitions": sum(1 for t, _ in trans if t == "off"),
            "gated_rebal_count": len(on_rs),
            "active_rebal_count": len(active_rebals),
            "occupancy_frac": round(len(on_rs) / len(active_rebals), 4),
            "first_on_date": (str(tl[on_rs[0]].date()) if on_rs
                              else None),
            "episodes": episodes,
            "dd_at_first_active": round(dd_at[active_rebals[0]], 6),
        }

    payload = {
        "probe": "CN-CORE-DDCTL-P1 s2 pre-freeze (R263 bm-a)",
        "family_faces_reasserted": {
            "T": int(T),
            "T_ok": bool(T == CS.T_FROZEN),
            "first": str(tl[0].date()),
            "cutoff": str(tl[-1].date()),
            "cutoff_ok": bool(str(tl[-1].date()) == CS.EVIDENCE_CUTOFF),
            "events": sorted(f"{s}@{d}" for s, d in evt_set),
            "events_ok": bool(evt_set == CS.EVT_FROZEN),
            "core_zero_events": bool(not events.get(CORE)),
            "first_active": str(tl[first_active_r].date()),
            "first_active_ok": bool(str(tl[first_active_r].date())
                                    == CS.FIRST_ACTIVE_FROZEN),
        },
        "dd_axis": {
            "window": W_DD,
            "face": "core clean_value full-history trailing-252 max",
            "hysteresis": "on: dd_r < -x/100; off: dd_r > -x/200",
            "eval": "family quarterly grid (anchor 62 step 63) from "
                    "first_active onward, state carried across periods",
            "min_dd_at_active_rebals": round(float(dd_vals.min()), 6),
            "min_dd_date": str(tl[active_rebals[int(
                np.argmin(dd_vals))]].date()),
            "median_dd_at_active_rebals": round(float(np.median(dd_vals)),
                                                6),
            "core_clean_vs_raw_max_abs_diff": facediff,
        },
        "arms": arms,
        "candidate_seed_base": 20_261_130,
        "seed_span": "20261130 + k, k<100 (50 per threshold arm; registry "
                     "max = 20261080+50 = 20261130 -> collision-free)",
    }
    gates = payload["family_faces_reasserted"]
    ok = all(gates[k] for k in ("T_ok", "cutoff_ok", "events_ok",
                                "core_zero_events", "first_active_ok"))
    payload["all_ok"] = bool(ok and facediff < 1e-9)   # float-noise face
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=1)
    print(json.dumps(payload, ensure_ascii=False, indent=1))
    return 0 if payload["all_ok"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
