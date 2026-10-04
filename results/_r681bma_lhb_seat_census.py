"""LHB seat-axis cheap census (r681 bm-a, TRIAL_LABOR_LAW cheap-probe lineage, r680 LHB census sibling).

Question (CEO orientation law: 游资情绪周期族): does following the trades of top STATISTICAL
seats (frequent, net-buying seats; no alias registry needed) carry positive capturable
returns vs the all-board LHB baseline?

Pre-registered read rules (frozen before run):
  - seat aggregate caliber: OPERATEDEPT_CODE across all 36 sampled windows (10-day-apart
    snapshots, honest coverage note)
  - TOP-NET seats = top 50 by cumulative NET (must be net-positive overall)
  - TOP-FREQ seats = top 50 by appearance count (must be net-positive overall)
  - event = seat row with NET > 0 and BUY > 0
  - faces measured vs all-board baseline:
      ret1_open = close(T+1)/open(T+1) - 1   (capturable 1d, gross)
      ret5_open = close(T+5)/open(T+1) - 1  (capturable 5d, gross)
      gap       = open(T+1)/close(T) - 1     (the leg static columns hide, E30 law)
  - cost: COST_SIDE x1 both legs (13.041 bp/side, r680 constant)
  - verdict rules (frozen):
      ENRICH  = any top-seat face net beats baseline by > +50bp AND win-rate edge > +5pp
      NEUTRAL = edge within +-20bp
      CLOSE   = top-seat face net <= baseline net + 20bp (no edge)  -> axis closed at board level
  - dedup: seat (code,day,seat) rows aggregated to (code,day) per seat-list membership;
    one vote per (code,day) event (r680 EM multi-reason dupe law)

Read-only. Output: results/_r681bma_lhb_seat_census.json
"""
import json, os
import numpy as np
import pandas as pd

OUT = "results/_r681bma_lhb_seat_census.json"
SEAT_DIR = "Money02/data/lhb_seat"
BARS_DIR = "Money02/data/bars"
COST_SIDE = 0.0013041  # x1 cost spec (r680 openentry constant)
BASE_EDGE_BP = 20.0    # no-edge band
ENRICH_EDGE_BP = 50.0  # enrichment threshold

def load_seat():
    fs = [f for f in sorted(os.listdir(SEAT_DIR)) if f.endswith(".parquet")]
    frames = [pd.read_parquet(os.path.join(SEAT_DIR, f)) for f in fs]
    df = pd.concat(frames, ignore_index=True)
    df["code"] = df["SECURITY_CODE"].astype(str).str.zfill(6)
    df["day"] = df["TRADE_DATE"].astype(str).str.slice(0, 10)
    return df

def bars_map(codes_needed, events):
    """Load OHLC per code (name-addressed cols per r680 law), with day->index map."""
    per_code = {}
    for c in set(codes_needed):
        p = os.path.join(BARS_DIR, c + ".parquet")
        if not os.path.exists(p):
            continue
        b = pd.read_parquet(p)
        if not {"date", "open", "close"}.issubset(b.columns):
            continue
        b["_d"] = b["date"].astype(str).str.slice(0, 10)
        per_code[c] = {
            "d2i": {d: i for i, d in enumerate(b["_d"].tolist())},
            "open": b["open"].to_numpy(float),
            "close": b["close"].to_numpy(float),
        }
    return per_code

def fwd_legs(ev, per_code):
    """Per-row (code,day) forward legs: open(T+1), close(T+1), close(T+5), close(T)."""
    rows = []
    for c, day in zip(ev["code"].tolist(), ev["day"].tolist()):
        B = per_code.get(c)
        if B is None:
            continue
        idx = B["d2i"].get(day)
        if idx is None or idx + 5 >= len(B["close"]):
            continue
        t1 = idx + 1
        rows.append({"code": c, "day": day,
                     "closeT": B["close"][idx], "open1": B["open"][t1],
                     "close1": B["close"][t1], "close5": B["close"][idx + 5]})
    return pd.DataFrame(rows)

def face_stats(df, col, net=True):
    if len(df) == 0:
        return {"n": 0}
    v = df[col].to_numpy(float)
    v = v[np.isfinite(v)]
    out = {"n": int(len(v)), "mean_pct": float(np.mean(v) * 100),
           "median_pct": float(np.median(v) * 100), "win": float(np.mean(v > 0))}
    if net:
        out["mean_net_pct"] = float((np.mean(v) - 2 * COST_SIDE) * 100)
    return out

def main() -> int:
    seat = load_seat()
    meta = {"seat_rows": int(len(seat)),
            "windows_n": int(seat["day"].nunique()),
            "seats_n": int(seat["OPERATEDEPT_CODE"].nunique()),
            "code_day_n": int(seat.groupby(["code", "day"]).ngroups),
            "window_span": [str(seat["day"].min()), str(seat["day"].max())],
            "sampling_note": "36 windows ~10 trading days apart, 2007-01..2026-09 snapshot sample (cheap census, not full history)"}

    # seat aggregates
    agg = seat.groupby("OPERATEDEPT_CODE").agg(
        n=("code", "size"), net_sum=("NET", "sum"), buy_sum=("BUY", "sum")).reset_index()
    top_net = agg[(agg["net_sum"] > 0)].nlargest(50, "net_sum")["OPERATEDEPT_CODE"].tolist()
    top_freq = agg[(agg["net_sum"] > 0)].nlargest(50, "n")["OPERATEDEPT_CODE"].tolist()

    # events: seat rows with NET>0 and BUY>0, dedup to (code,day) per seat-set
    ev_seat = seat[(seat["NET"] > 0) & (seat["BUY"] > 0)]
    for name, sl in [("top_net", top_net), ("top_freq", top_freq)]:
        sub = ev_seat[ev_seat["OPERATEDEPT_CODE"].isin(sl)]
        evd = sub.groupby(["code", "day"], as_index=False).agg(
            seats=("OPERATEDEPT_CODE", "nunique"), net=("NET", "sum"))
        evd["set"] = name
        globals().setdefault("_EV", []).append(evd)

    ev_all = pd.concat(_EV, ignore_index=True)
    # baseline events: all board (code,day) universe of seat windows (any direction), dedup
    base_ev = seat.groupby(["code", "day"], as_index=False).size()[["code", "day"]].drop_duplicates()
    base_ev["set"] = "all_board"

    # forward legs via bars (only for involved codes)
    codes_needed = set(ev_all["code"]) | set(base_ev["code"])
    per_code = bars_map(codes_needed, None)
    legs_all = fwd_legs(base_ev, per_code)  # compute once for all (code,day), then join sets
    legs_all["key"] = legs_all["code"] + "|" + legs_all["day"]
    ev_all["key"] = ev_all["code"] + "|" + ev_all["day"]
    m = ev_all.merge(legs_all, on="key", how="inner")
    mb = legs_all  # baseline = all computed legs

    def enrich(df):
        df = df.copy()
        df["ret1_open"] = df["close1"] / df["open1"] - 1
        df["ret5_open"] = df["close5"] / df["open1"] - 1
        df["gap"] = df["open1"] / df["closeT"] - 1
        return df

    m = enrich(m)
    mb = enrich(mb)

    res = {"meta": meta,
           "cost_side_bp": COST_SIDE * 1e4 * 2,
           "seat_top_net_n": len(top_net), "seat_top_freq_n": len(top_freq)}

    base = {"ret1_open": face_stats(mb, "ret1_open"), "ret5_open": face_stats(mb, "ret5_open"),
            "gap": face_stats(mb, "gap")}
    res["baseline_all_board"] = base

    for name in ("top_net", "top_freq"):
        sub = m[m["set"] == name].drop_duplicates("key")
        f = {"ret1_open": face_stats(sub, "ret1_open"), "ret5_open": face_stats(sub, "ret5_open"),
             "gap": face_stats(sub, "gap"),
             "events_n": int(len(sub)),
             "seats_per_event_mean": float(sub["seats"].mean()) if len(sub) else 0}
        # edge vs baseline (net of cost)
        for col in ("ret1_open", "ret5_open"):
            if f[col].get("n", 0) > 0 and base[col].get("n", 0) > 0:
                edge_bp = (f[col]["mean_net_pct"] - base[col]["mean_net_pct"]) * 100
                f[col + "_edge_net_bp"] = round(edge_bp, 2)
                f[col + "_win_edge_pp"] = round((f[col]["win"] - base[col]["win"]) * 100, 2)
        res["face_" + name] = f

    # verdict (frozen rules)
    verd = []
    for name in ("top_net", "top_freq"):
        f = res["face_" + name]
        for col in ("ret1_open", "ret5_open"):
            e = f.get(col + "_edge_net_bp")
            w = f.get(col + "_win_edge_pp")
            if e is None:
                verd.append((name, col, "INSUFFICIENT"))
            elif e > ENRICH_EDGE_BP and w > 5:
                verd.append((name, col, "ENRICH"))
            elif e < BASE_EDGE_BP:
                verd.append((name, col, "CLOSE"))
            else:
                verd.append((name, col, "NEUTRAL"))
    res["verdict_cells"] = [list(v) for v in verd]
    overall = "CLOSE" if all(v[2] in ("CLOSE", "INSUFFICIENT", "NEUTRAL") for v in verd) and not any(v[2] == "ENRICH" for v in verd) else "ENRICH"
    res["overall_verdict"] = overall

    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        json.dump(res, f, ensure_ascii=False, indent=1, default=str)
    print("CENSUS_DONE overall=%s events_topnet=%d" % (overall, res["face_top_net"]["events_n"]))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
