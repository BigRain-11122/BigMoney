"""_r423bmb_w8tstate_probe.py -- W8 TSTATE gate raw-face probe (prereg sec.2 facts, NOT results).

Upgrade of _r421bma_tstate_probe.py (W7-era TSTATE probe) per the W8 drafting
berth (MSG-20260929-1158-bmb-all): merges the W7-frozen STREAK face into the
crossing evidence, per the parked-candidate reuse checklist face (six-gate
crossing + extreme-day re-read + STREAK x TSTATE new crossing + core48
member-level TSTATE rates). TSTATE definitions census-verbatim
(toolstack/gate_census.py, O-1855(4)); STREAK definitions W7-frozen
(research/TRIAL_LABOR_W7_PREREG.md sec.2):

  deep_pullback (MAD60_q10): dist = close/MA60 - 1;
      gate = dist < dist.rolling(252, min_periods=120).quantile(0.10)
  oversold_rsv  (RSV60_low<0.2): rsv = (close - low60)/(high60 - low60);
      gate = rsv < 0.2   (hh==ll -> NaN gate-closed)
  up_streak2:   close(d)>close(d-1) AND close(d-1)>close(d-2)
  down_streak2: mirror; neither = gate-closed for conditioned faces

Signal-day d close info-set (T+1 causal, entry d+1 open -- same info set as
GATE/VOL/YANG/VCONF, zero look-ahead). Six-gate 64-cell crossing
(gate x vol x yang x vconf x streak x tstate) + STREAK x TSTATE crossing +
extreme-day states + core48 member TSTATE rates (tl1.load_core() real roster).
Deterministic, zero network, read-only.
"""
import json
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.join("scripts"))
import trial_labor_w1 as tl1  # import-face reuse law (loader T-22/T-34 lineage)

CUTOFF = "2026-09-22"  # P-5C frozen binding, same anchor as W4-W7 probes
OUT = "results/_r423bmb_w8tstate_probe_facts.json"

EXTREME_DAYS = ["2015-07-27", "2016-01-04", "2024-02-28", "2024-09-24",
                "2024-09-30", "2025-04-07", "2026-01-19"]


def streak_faces(df):
    """up/down 2-day close-over-close run; -1=neither; NaN only first 2 bars.
    W7-frozen definition verbatim (r206 probe lineage, warmup bar-idx==2)."""
    up1 = df["close"] > df["close"].shift(1)
    up2 = df["close"].shift(1) > df["close"].shift(2)
    dn1 = df["close"] < df["close"].shift(1)
    dn2 = df["close"].shift(1) < df["close"].shift(2)
    state = pd.Series(float("nan"), index=df.index)
    judge = (df["close"].shift(2)).notna()  # bars 0-1 = warmup gate-closed
    state[judge & (up1 & up2).fillna(False)] = 1.0
    state[judge & (dn1 & dn2).fillna(False)] = 0.0
    state[judge & ~((up1 & up2).fillna(False) | (dn1 & dn2).fillna(False))] = -1.0
    return state


def tstate_faces(df):
    """census-verbatim TSTATE gates; returns (mad60_q10, rsv60_low, decidable dict)."""
    c, h, l = df["close"], df["high"], df["low"]
    ma60 = c.rolling(60).mean()
    dist = c / ma60 - 1.0
    q10_ref = dist.rolling(252, min_periods=120).quantile(0.10)
    mad_q10 = dist < q10_ref

    hh60, ll60 = h.rolling(60).max(), l.rolling(60).min()
    rng60 = (hh60 - ll60).replace(0, np.nan)
    rsv60 = (c - ll60) / rng60
    rsv_low = rsv60 < 0.2

    decidable = {"deep_pullback_mad60_q10": q10_ref.notna(),
                 "oversold_rsv60_low02": rsv60.notna()}
    return mad_q10, rsv_low, decidable, rsv60


def main() -> int:
    df = pd.read_csv(os.path.join("data", "daily", "sh510300.csv"))
    df["date"] = df["date"].astype(str)
    df = df[df["date"] <= CUTOFF].reset_index(drop=True)
    n = len(df)
    assert n == 3483, f"row count {n} != 3483 (W4-W7 probe anchor)"
    assert df["date"].iloc[-1] == CUTOFF, "last row != cutoff"
    zero_vol = int((df["volume"] <= 0).sum())

    c, h, l, v, o = (df[k] for k in ("close", "high", "low", "volume", "open"))

    # ---- TSTATE gates (census-verbatim) + anchors --------------------------
    mad_q10, rsv_low, decidable, rsv60 = tstate_faces(df)

    # ---- STREAK face (W7-frozen) -------------------------------------------
    st = streak_faces(df)
    up_st = st == 1.0
    dn_st = st == 0.0
    neither = st == -1.0
    streak_warmup = int(st.isna().sum())  # == 2 anchor

    # ---- frozen W3-W6 gate faces --------------------------------------------
    ma200 = c.rolling(200).mean()
    bull, bear = c > ma200, c <= ma200
    ret = c.pct_change()
    vol20 = ret.rolling(20, min_periods=20).std(ddof=1)
    med500 = vol20.rolling(500, min_periods=500).median()
    calm, wild = vol20 <= med500, vol20 > med500
    med20v = v.rolling(20, min_periods=20).median()
    surge = v > med20v
    yang = c > o

    facts = {"cutoff": CUTOFF, "rows": int(n), "first_date": str(df["date"].iloc[0]),
             "last_date": str(df["date"].iloc[-1]), "zero_volume_rows": zero_vol,
             "post_cutoff_rows_excluded": 3,
             "probe_lineage": "r421 TSTATE probe + r206 STREAK def merged (W8 berth upgrade)"}

    # ---- per-gate anchors (r421 anchors must reproduce exactly) -------------
    for name, g in (("deep_pullback_mad60_q10", mad_q10),
                    ("oversold_rsv60_low02", rsv_low)):
        dec_mask = decidable[name]
        fv = int(dec_mask.values.argmax()) if bool(dec_mask.any()) else -1
        dec = int(dec_mask.sum())
        facts[name] = {"first_decidable_bar_idx": fv,
                       "warmup_gate_closed_bars": fv,
                       "decidable_days": dec,
                       "gate_true_days": int(g.sum()),
                       "open_rate_pct_on_decidable": round(100.0 * float(g.sum()) / max(1, dec), 2)}

    facts["streak_face"] = {
        "warmup_bars": streak_warmup,
        "first_decidable_bar_idx": 2,
        "decidable_days": int(st.notna().sum()),
        "up_streak2_days": int(up_st.sum()),
        "down_streak2_days": int(dn_st.sum()),
        "neither_days": int(neither.sum()),
        "up_rate_pct_on_decidable": round(100.0 * float(up_st.sum()) / max(1, int(st.notna().sum())), 2),
    }

    # ---- TSTATE rate inside STREAK faces (new crossing face, open reading) --
    def rate(mask_in, gate, dec):
        both = int((mask_in & gate).sum())
        base = int((mask_in & dec).sum())
        return round(100.0 * both / base, 2) if base else float("nan")

    dec_mad = decidable["deep_pullback_mad60_q10"]
    dec_rsv = decidable["oversold_rsv60_low02"]
    facts["tstate_rate_inside_streak_pct"] = {
        "up_streak2": {"mad60_q10_pct": rate(up_st, mad_q10, dec_mad),
                       "rsv60_low_pct": rate(up_st, rsv_low, dec_rsv)},
        "down_streak2": {"mad60_q10_pct": rate(dn_st, mad_q10, dec_mad),
                         "rsv60_low_pct": rate(dn_st, rsv_low, dec_rsv)},
        "neither": {"mad60_q10_pct": rate(neither, mad_q10, dec_mad),
                   "rsv60_low_pct": rate(neither, rsv_low, dec_rsv)},
    }
    # streak rate inside tstate-open days (mirror direction)
    facts["streak_rate_inside_tstate_pct"] = {
        "mad60_q10_open": {"up_pct": rate(mad_q10, up_st, st.notna()),
                           "down_pct": rate(mad_q10, dn_st, st.notna())},
        "rsv60_low_open": {"up_pct": rate(rsv_low, up_st, st.notna()),
                           "down_pct": rate(rsv_low, dn_st, st.notna())},
    }
    # STREAK x TSTATE 4-cell crossing lower bounds
    facts["streak_tstate_cross_cells"] = {
        "up_and_mad60": int((up_st & mad_q10).sum()),
        "up_and_rsv60": int((up_st & rsv_low).sum()),
        "down_and_mad60": int((dn_st & mad_q10).sum()),
        "down_and_rsv60": int((dn_st & rsv_low).sum()),
    }

    # ---- six-gate 64-cell crossing (gate x vol x yang x vconf x streak x tstate)
    cells = {}
    n_empty = 0
    for bname, b in (("bull", bull), ("bear", bear)):
        for vname, vv in (("calm", calm), ("wild", wild)):
            for yname, y in (("yang", yang), ("red", ~yang)):
                for sname, s in (("surge", surge), ("dry", ~surge)):
                    for kname, k in (("up_streak", up_st), ("down_streak", dn_st)):
                        for tname, t in (("mad60", mad_q10), ("rsv60", rsv_low)):
                            cnt = int((b & vv & y & s & k & t).sum())
                            cells["%s|%s|%s|%s|%s|%s" % (bname, vname, yname, sname, kname, tname)] = cnt
                            if cnt == 0:
                                n_empty += 1
    facts["six_gate_64_cells"] = cells
    facts["six_gate_64_cells_empty_count"] = n_empty
    facts["six_gate_64_cells_nonzero_count"] = 64 - n_empty
    facts["six_gate_64_cells_min_nonzero"] = min([x for x in cells.values() if x > 0] or [0])
    facts["six_gate_64_cells_max"] = max(cells.values())

    # ---- extreme days: streak x tstate states (re-read with streak merged) ---
    est = {}
    for dstr in EXTREME_DAYS:
        idx = df.index[df["date"] == dstr]
        if len(idx) == 0:
            est[dstr] = "not-in-panel"
            continue
        i = int(idx[0])
        stv = None if pd.isna(st.iloc[i]) else ("up_streak2" if st.iloc[i] == 1.0 else ("down_streak2" if st.iloc[i] == 0.0 else "neither"))
        est[dstr] = {"streak": stv,
                     "mad60_q10": bool(mad_q10.iloc[i]),
                     "rsv60_low": bool(rsv_low.iloc[i]),
                     "rsv60_value": (None if pd.isna(rsv60.iloc[i]) else round(float(rsv60.iloc[i]), 4))}
    facts["extreme_day_states"] = est

    # ---- core48 member-level TSTATE open rates (real roster, import-reuse) --
    members = tl1.load_core()
    mad_rates, rsv_rates = {}, {}
    for sym in members:
        f = os.path.join("data", "daily", f"{sym}.csv")
        if not os.path.exists(f):
            continue
        m = pd.read_csv(f)
        m["date"] = m["date"].astype(str)
        m = m[m["date"] <= CUTOFF].reset_index(drop=True)
        mg, mrl, mdec, _ = tstate_faces(m)
        for nm, g, dec, store in (("mad", mg, mdec["deep_pullback_mad60_q10"], mad_rates),
                                   ("rsv", mrl, mdec["oversold_rsv60_low02"], rsv_rates)):
            base = int(dec.sum())
            store[sym] = round(100.0 * float(g.sum()) / base, 2) if base else None
    for nm, store in (("mad60_q10", mad_rates), ("rsv60_low", rsv_rates)):
        vals = [x for x in store.values() if x is not None]
        facts[f"core48_{nm}_open_rate_members"] = len(store)
        facts[f"core48_{nm}_open_rate_min"] = min(vals)
        facts[f"core48_{nm}_open_rate_median"] = sorted(vals)[len(vals) // 2]
        facts[f"core48_{nm}_open_rate_max"] = max(vals)

    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(facts, fh, ensure_ascii=False, indent=1, sort_keys=True)
    print(json.dumps({k: v for k, v in facts.items() if not isinstance(v, dict)} or {"ok": True},
                     ensure_ascii=False))
    print("six_gate_64_cells_empty_count:", facts["six_gate_64_cells_empty_count"],
          "| nonzero min:", facts["six_gate_64_cells_min_nonzero"],
          "| max:", facts["six_gate_64_cells_max"])
    print("streak_tstate_cross:", json.dumps(facts["streak_tstate_cross_cells"]))
    print("W8 TSTATE probe facts ->", OUT)
    return 0


if __name__ == "__main__":
    sys.exit(main())
