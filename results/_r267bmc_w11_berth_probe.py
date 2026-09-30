"""_r267bmc_w11_berth_probe.py -- INNOVATION-QUOTA-SLOT-11 berth probe (zoo #95 index_higher_mom_timing).

Berth window (bm-c r267). Read-only. Facts -> results/_r267bmc_w11_berth_probe_facts.json.
Construction single-source = this probe (clean-room; r263 param-freeze candidate carried verbatim):
  - panel: data/daily/sh510300.csv (in-repo qfq daily, 510300)
  - moment: M_n = rolling(20).mean of r_t**n, n in {3,4,5}  (raw origin moment, E[r^n])
  - EMA smoothing: pandas ewm(alpha=2/91, adjust=False) on M_n (window 90 -> alpha=2/91, author-verbatim)
  - signal: T-day signal = sign of EMA diff on T-1 (EMA_{t-1} > EMA_{t-2} -> long intent; trend trigger, NOT threshold cross)
  - stop: position return since entry close < -0.10 -> exit (single 10% stop line)
D6 berth-scope faces (signal-face point-biserial, full five-face protocol deferred to freeze window step-5 per prereg plan):
  batch-internal MOM3/4/5 mutual corr (variant faces, burn-both disclosure) + vs REGIME_GUARD below-MA20 width proxy
  + vs #87 nhnl_b20 face (core48) + vs VSTD20 second-moment proxy on 510300 (vol-family high-risk pair honest proxy).
Face builders verbatim-imported from in-tree probes (anti-rebuild law):
  load_core48/below_ma20_share/nhnl_b20 from _r259bmc_w9_crowding_probe; load_csv_series/pearson_ind from _r264bmc_w10_berth_probe.
"""
import json
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _r259bmc_w9_crowding_probe import load_core48, below_ma20_share, nhnl_b20  # noqa: E402
from _r264bmc_w10_berth_probe import load_csv_series, pearson_ind  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PANEL = os.path.join(ROOT, "data", "daily", "sh510300.csv")
OUT = os.path.join(ROOT, "results", "_r267bmc_w11_berth_probe_facts.json")

MOMENT_WINDOW = 20
EMA_ALPHA = 2.0 / 91.0  # window 90 author-verbatim
STOP = -0.10
ORDERS = (3, 4, 5)
WARMUP = MOMENT_WINDOW + 2  # rolling 20 -> first valid idx 19; ema.diff needs 20; shift(1) needs 21


def build_faces_510300():
    rows = load_csv_series(PANEL, "date", "close")  # dict date_str -> close
    date_strs = list(rows.keys())
    s = pd.Series(list(rows.values()), index=pd.DatetimeIndex(pd.to_datetime(date_strs)), dtype=float)
    ret = s.pct_change()
    faces = {}
    ind_dicts = {}
    stats = {}
    for n in ORDERS:
        m = (ret ** n).rolling(MOMENT_WINDOW).mean()
        ema = m.ewm(alpha=EMA_ALPHA, adjust=False).mean()
        ema_diff = ema.diff()
        sig = (ema_diff.shift(1) > 0).astype(float)  # T-day signal = EMA rose on T-1
        decidable = sig.iloc[WARMUP:]
        pos = []
        entry_close = None
        n_entries = 0
        n_stop_exits = 0
        n_flip_exits = 0
        prev = 0.0
        for dt, sg in decidable.items():
            if prev == 0.0 and sg > 0:
                prev = 1.0
                entry_close = s.loc[dt]
                n_entries += 1
            elif prev == 1.0:
                if sg <= 0:
                    prev = 0.0
                    entry_close = None
                    n_flip_exits += 1
                else:
                    pos_ret = (s.loc[dt] / entry_close - 1.0) if entry_close else 0.0
                    if pos_ret < STOP:
                        prev = 0.0
                        entry_close = None
                        n_stop_exits += 1
            pos.append(prev)
        pos_ser = pd.Series(pos, index=decidable.index, dtype=float)
        faces[n] = pos_ser
        ind_dicts[n] = {d.strftime("%Y-%m-%d"): float(v) for d, v in pos_ser.items()}
        long_days = int(pos_ser.sum())
        stats[n] = {
            "decidable_days": int(len(decidable)),
            "first_decidable": str(decidable.index[0].date()),
            "long_days": long_days,
            "flat_days": int(len(decidable) - long_days),
            "long_occupancy": round(long_days / max(1, len(decidable)), 4),
            "entries": n_entries,
            "stop_exits": n_stop_exits,
            "flip_exits": n_flip_exits,
            "f6_gate_30": bool(n_entries >= 30),
        }
    return s, ret, faces, ind_dicts, stats, date_strs


def main() -> int:
    s, ret, faces, ind_dicts, stats, date_strs = build_faces_510300()
    panel = {
        "rows": len(date_strs),
        "first_date": date_strs[0],
        "last_date": date_strs[-1],
        "moment_window": MOMENT_WINDOW,
        "ema_alpha": EMA_ALPHA,
        "stop": STOP,
    }
    # batch-internal variant faces (aligned by construction)
    bi = {}
    for a in (3, 4, 5):
        for b in (3, 4, 5):
            if a < b:
                bi[f"MOM{a}_vs_MOM{b}"] = round(float(np.corrcoef(faces[a].values, faces[b].values)[0, 1]), 4)
    # in-register proxy faces via pearson_ind (dict protocol)
    c48, c48_members = load_core48()  # tuple (closes df, member list) per W9 probe signature
    below = below_ma20_share(c48)
    nhnl = nhnl_b20(c48)
    vstd20 = ret.rolling(MOMENT_WINDOW).std()
    def to_dict(ser):
        return {d.strftime("%Y-%m-%d"): float(v) for d, v in ser.dropna().items()}
    d6 = {
        "batch_internal": bi,
        "note_variant_faces": "MOM3/4/5 = variant faces of one construction axis (moment order); merge-clause relevant, burn-both per W9 analog",
    }
    for name, ser in (
        ("vs_regime_guard_width_below_ma20", below),
        ("vs_87_nhnl_b20", nhnl),
        ("vs_vstd20_second_moment_proxy", vstd20),
    ):
        ser_d = to_dict(ser)
        d6[name] = {}
        for n in ORDERS:
            r, n_common = pearson_ind(sorted(ind_dicts[n].keys()), ind_dicts[n], ser_d)
            d6[name][f"MOM{n}"] = {"pearson": r, "n_common": n_common}
    d6["berth_scope_note"] = "vol-family registered-trader return-face corr + T33 cells + registered six + repo/month-end faces = freeze-window step-5 full protocol (prereg sec.1 plan); VSTD20 = second-moment proxy honest disclosure"
    # extreme-day faces: top |r| days and their MOM5/MOM3 state
    absr = ret.abs().sort_values(ascending=False)
    extreme = []
    for dt, v in absr.head(8).items():
        extreme.append({
            "date": str(dt.date()),
            "ret": round(float(ret.loc[dt]), 6),
            "mom5_state": float(faces[5].loc[dt]) if dt in faces[5].index else None,
            "mom3_state": float(faces[3].loc[dt]) if dt in faces[3].index else None,
        })
    facts = {
        "probe": "INNOVATION-QUOTA-SLOT-11 berth (zoo #95 index_higher_mom_timing)",
        "berth_round": "bm-c r267 2026-09-30",
        "param_freeze_source": "zoo #95 row r263 param-freeze candidate carried verbatim: moment order {3,4,5} three-leg full spectrum / window 20 / EMA 90 (alpha=2/91) / trigger = EMA slope sign / stop -0.1 single line; clean-room, no source-code copy",
        "panel_510300": panel,
        "cells_state_stats": stats,
        "d6_signal_face": d6,
        "extreme_days": extreme,
        "consumers": "INNOVATION-QUOTA-SLOT-11 prereg draft (research/INNOVATION_QUOTA_W11_PREREG.md BERTH) -> freeze window steps 1-5 -> runner build -> pool enqueue -> judged verdict (T-34 fastline candidate pool consumer either way)",
        "evidence_cutoff_asof": "2026-09-29 (as-of face; panel last bar = last complete bar, P-5C lockbox at freeze)",
    }
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(facts, fh, ensure_ascii=False, indent=1, sort_keys=True)
    print("W11 berth probe facts ->", OUT)
    print(json.dumps({"panel": panel, "stats": stats, "bi": bi}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
