"""_r421bma_tstate_probe.py -- W7 TSTATE gate raw-face probe (prereg sec.2 facts, NOT results).

Mirror of _r410bma_volconf_probe.py lineage (W6 precedent). Computes the two
census-sourced timing-state gates on data/daily/sh510300.csv raw face
(census definitions verbatim from toolstack/gate_census.py, O-1855(4)):

  deep_pullback (MAD60_q10): dist = close/MA60 - 1;
      gate = dist < dist.rolling(252, min_periods=120).quantile(0.10)
  oversold_rsv  (RSV60_low<0.2): rsv = (close - low60)/(high60 - low60);
      gate = rsv < 0.2   (hh==ll -> NaN gate-closed)

Signal-day d close info-set (T+1 causal, entry d+1 open -- same info set as
GATE/VOL/YANG/VCONF, zero look-ahead). Cross-faces vs the four frozen gates
for independence evidence + five-gate 32-cell non-emptiness + extreme-day
states. Deterministic, zero network, read-only.
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
CUTOFF = "2026-09-22"
OUT = ROOT / "results" / "_r421bma_tstate_probe_facts.json"


def main() -> int:
    raw = pd.read_csv(ROOT / "data" / "daily" / "sh510300.csv", parse_dates=["date"])
    post_cutoff = int((raw["date"] > CUTOFF).sum())
    df = raw[raw["date"] <= CUTOFF].set_index("date").sort_index()
    c, h, l, v, o = df["close"], df["high"], df["low"], df["volume"], df["open"]
    n = len(df)

    # --- census-verbatim TSTATE gates --------------------------------------
    ma60 = c.rolling(60).mean()
    dist = c / ma60 - 1.0
    mad_q10 = dist < dist.rolling(252, min_periods=120).quantile(0.10)

    hh60, ll60 = h.rolling(60).max(), l.rolling(60).min()
    rng60 = (hh60 - ll60).replace(0, np.nan)
    rsv60 = (c - ll60) / rng60
    rsv_low = rsv60 < 0.2

    # --- frozen W3-W6 gate faces (cross-independence evidence) --------------
    ma200 = c.rolling(200).mean()
    bull, bear = c > ma200, c <= ma200
    ret = c.pct_change()
    vol20 = ret.rolling(20, min_periods=20).std(ddof=1)
    med500 = vol20.rolling(500, min_periods=500).median()
    calm, wild = vol20 <= med500, vol20 > med500
    med20v = v.rolling(20, min_periods=20).median()
    surge = v > med20v
    yang = c > o

    facts = {"cutoff": CUTOFF, "rows": int(n), "first_date": str(df.index[0].date()),
             "last_date": str(df.index[-1].date()), "zero_volume_rows": int((v <= 0).sum()),
             "post_cutoff_rows_excluded": post_cutoff}

    # honest decidable faces: NaN-comparison yields False (gate-closed), so
    # decidable = the underlying threshold/quantile series being non-NaN
    q10_ref = dist.rolling(252, min_periods=120).quantile(0.10)
    decidable = {"deep_pullback_mad60_q10": q10_ref.notna(), "oversold_rsv60_low02": rsv60.notna()}
    gates = {"deep_pullback_mad60_q10": mad_q10, "oversold_rsv60_low02": rsv_low}
    for name, g in gates.items():
        gs = decidable[name].reset_index(drop=True)
        fv = int(gs.values.argmax()) if bool(gs.any()) else -1
        dec = int(decidable[name].sum())
        facts[name] = {
            "first_decidable_bar_idx": int(fv) if fv is not None else -1,
            "warmup_gate_closed_bars": int(fv) if fv is not None else -1,
            "decidable_days": dec,
            "gate_true_days": int(g.sum()),
            "open_rate_pct_on_decidable": round(100.0 * float(g.sum()) / max(1, dec), 2),
        }

    def rate(mask_in: pd.Series, gate: pd.Series, dec: pd.Series) -> float:
        both = int((mask_in & gate).sum())
        base = int((mask_in & dec).sum())
        return round(100.0 * both / base, 2) if base else float("nan")

    faces = {"bull": bull, "bear": bear, "calm": calm, "wild": wild,
             "yang": yang, "red": ~yang, "surge": surge, "dry": ~surge}
    facts["gate_rate_inside_faces_pct"] = {
        fname: {"mad60_q10_pct": rate(fm, mad_q10, decidable["deep_pullback_mad60_q10"]),
                "rsv60_low_pct": rate(fm, rsv_low, decidable["oversold_rsv60_low02"])}
        for fname, fm in faces.items()
    }

    # five-gate 2^5 = 32 cells non-emptiness (binary marginals, W6 16-cell law extended)
    cells = {}
    all_nonempty = True
    for bname, b in (("bull", bull), ("bear", bear)):
        for vname, vv in (("calm", calm), ("wild", wild)):
            for yname, y in (("yang", yang), ("red", ~yang)):
                for sname, s in (("surge", surge), ("dry", ~surge)):
                    for tname, t in (("mad60", mad_q10), ("rsv60", rsv_low)):
                        cnt = int((b & vv & y & s & t).sum())
                        cells["%s|%s|%s|%s|%s" % (bname, vname, yname, sname, tname)] = cnt
                        if cnt == 0:
                            all_nonempty = False
    facts["five_gate_32_cells"] = cells
    facts["five_gate_32_cells_all_nonempty"] = all_nonempty
    facts["five_gate_32_cells_min"] = min(cells.values())
    facts["five_gate_32_cells_max"] = max(cells.values())

    facts["cross_lower_bounds"] = {
        "mad60q10_and_bull": int((mad_q10 & bull).sum()),
        "mad60q10_and_bear": int((mad_q10 & bear).sum()),
        "rsv60low_and_bull": int((rsv_low & bull).sum()),
        "rsv60low_and_bear": int((rsv_low & bear).sum()),
        "rsv60low_and_yang": int((rsv_low & yang).sum()),
        "mad60q10_and_surge": int((mad_q10 & surge).sum()),
    }

    extremes = ["2015-07-27", "2016-01-04", "2024-02-28", "2024-09-24",
                "2024-09-30", "2025-04-07", "2026-01-19"]
    est = {}
    for dstr in extremes:
        dts = pd.Timestamp(dstr)
        if dts in df.index:
            est[dstr] = {"mad60_q10": bool(mad_q10.loc[dts]),
                         "rsv60_low": bool(rsv_low.loc[dts]),
                         "rsv60_value": (None if pd.isna(rsv60.loc[dts])
                                         else round(float(rsv60.loc[dts]), 4))}
        else:
            est[dstr] = "not-in-panel"
    facts["extreme_day_states"] = est

    OUT.write_text(json.dumps(facts, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(facts, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
