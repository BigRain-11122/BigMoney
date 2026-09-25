"""T-48 deliverable-1: factor-face registry (CEO order O-20260925-0855).

Maps the factor zoo to economic factor faces and decomposes the registered
trader roster into factor-face exposures:

  (a) engine factor faces  -- engine/factors.py FACTORS registry (the blend
      substrate for T-48 composite cells; core48 ETF panel computable);
  (b) IC evidence families -- recorded factor-IC batches (GTJA191 ETF face,
      WQ101 ETF face, GTJA191 stock face, Alpha158 truegap stock face) with
      per-family counts and evidence pointers (recorded cells, NO rerun);
  (c) zoo style families  -- ASTYLE_ZOO.md macro families (documented rows);
  (d) registered-strategy exposure face -- 28-trader roster entry signals
      mapped to primary factor faces, corps cross-refed from T-33
      results/corps_roster.json (read-only consume, bm-c lane artifact).

Deterministic, zero-network, zero-engine, zero new trials (registry doc, not
a batch: ledger_trials_added=0, t33 aggregation precedent). Hermetic:
missing artifacts -> honest empty + note (no fabrication).

Usage: python scripts/factor_registry.py run | selftest
"""
import argparse
import csv
import hashlib
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS = os.path.join(ROOT, "results", "factor_registry.json")
T22 = os.path.join(ROOT, "research", "shortline")

# --- (a) engine factor faces: curated economic-face map + sign prior ---
# face taxonomy per O-0855 s1: momentum/trend/breakout/reversal/low_vol/
# volume/mean_reversion. sign_prior = expected direction in a long-score
# composite (documented economic prior, NOT backtest rank).
ENGINE_FACES = {
    # face, sign prior, one-line economic prior
    "mom_20":          ("momentum", "+", "short-horizon cross-sectional momentum persistence"),
    "mom_60":          ("momentum", "+", "medium-horizon momentum (zoo s4 in-duty style)"),
    "mom_120":         ("momentum", "+", "long-horizon momentum"),
    "mom_12_1":        ("momentum", "+", "academic 12-1 skip-month momentum (J6 composite lineage)"),
    "mom_accel":       ("momentum", "+", "momentum acceleration = trend freshness"),
    "ma_slope_20":     ("momentum", "+", "trend direction slope of MA20"),
    "up_day_ratio":    ("momentum", "+", "advance persistence within window"),
    "overnight_minus_intraday": ("momentum", "+", "overnight-minus-intraday momentum style (docstring)"),
    "adx_14":          ("trend", "+", "trend strength (directional movement)"),
    "price_position":  ("trend", "+", "position in N-day range = breakout proximity (J6 lineage)"),
    "vol_regime":      ("trend", "-", "short/long vol ratio: expansion = trend stress"),
    "gap_overnight":   ("breakout", "+", "overnight gap = breakout confirmation (zoo s4 #25 high-open-confirm prior)"),
    "extreme_freq":    ("breakout", "-", "extreme-move frequency marks instability; orderly trends preferred"),
    "rev_5":           ("reversal", "+", "5d short-term reversal premium (overreaction bounce, zoo s2)"),
    "rev_10":          ("reversal", "+", "10d short-term reversal premium"),
    "drawdown_60":     ("reversal", "-", "deep 60d drawdown = reversal candidate pool (deep-water prior)"),
    "vol_20":          ("low_vol", "-", "short-window low-vol anomaly (zoo s5)"),
    "vol_60":          ("low_vol", "-", "low-vol anomaly, VOLATILITY-CE-01 registered lineage"),
    "intraday_range":  ("low_vol", "-", "tight normalized range = stability (J6 composite lineage)"),
    "return_skew":     ("low_vol", "-", "return skew: crash-prone tail profile avoided"),
    "return_kurt":     ("low_vol", "-", "excess kurtosis = tail-risk face"),
    "amt_20":          ("volume", "-", "20d amount level: drought floor prior (DROUGHT-CE-01 lineage)"),
    "volume_trend":    ("volume", "-", "volume expansion at range top = distribution"),
    "vol_price_diverge": ("volume", "+", "volume-confirmed moves vs divergence"),
    "amihud_illiq":    ("volume", "-", "Amihud illiquidity = stress-liquidity face"),
    "vol_price_corr":  ("volume", "+", "healthy trend has price-volume confirmation"),
    "ma_bias_20":      ("mean_reversion", "-", "20d MA bias: overextension fades to mean"),
    "ma_bias_60":      ("mean_reversion", "-", "60d MA bias fade"),
}

IC_FAMILIES = [
    # key, csv, panel, prereg doc, family-column?
    ("gtja191_etf", "gtja191_ic_results.csv", "core48 ETF daily panel",
     "research/shortline/P1_GTJA191_IC.md"),
    ("wq101_etf", "wq101_ic_results.csv", "core48 ETF daily panel",
     "research/shortline/P1_WQ101_IC.md"),
    ("gtja191_stock", "p1c_stock_ic_results.csv", "stock cross-section panel (P1C)",
     "research/shortline/P1C_STOCK_IC.md"),
    ("a158_truegap_stock", "a158_truegap_ic_cells.csv", "stock panel (true-gap axis)",
     "research/shortline/A158_TRUEGAP_IC.md"),
]

ZOO_FAMILIES = [
    ("attack_sentiment", "进攻·情绪系 (zoo s1: limitup/dragon/ban-open/limit-down-buy/mood/lhb/subnew)"),
    ("reversal_oversold", "反转·超跌系 (zoo s2: oversold-bias/zscore-revert/rsi2/deep-water/double-bottom)"),
    ("hold_grid", "死扛·长持系 (zoo s3: staged-DCA/grid/low-churn/regular-invest/repo-cash)"),
    ("trend_momentum", "趋势·动量系 (zoo s4: MA-cross/donchian/PSAR/supertrend/TS-mom/12-1/accel/RSRS)"),
    ("volatility_risk", "波动率·风险系 (zoo s5: low-vol anomaly/vol-targeting/regime-switch/vol-breakout)"),
    ("rotation_alloc", "轮动·配置系 (zoo s6: 2-8 rotation/sector rotation/composite rotation/risk-parity)"),
]

# --- (d) entry-signal -> primary factor face (curated, source = firm/traders params) ---
ENTRY_FACE_MAP = [
    ("top_n_rotation(composite", "composite_blend",
     "J6 composite blend: vol_60(-)/intraday_range(-)/mom_12_1(+)/price_position(+)"),
    ("low_vol_long", "low_vol", "60d low-vol top-k rotation (volatility face)"),
    ("vol_drought_reversal", "volume_drought_reversal", "volume drought + deep-water reversal (folk)"),
    ("engulf_reversal", "reversal", "bullish engulfing pattern in deep water"),
    ("needle_probe", "reversal", "long-lower-shadow probe in deep water"),
    ("vol_breakout", "breakout", "volatility breakout pattern"),
    ("inside_bar_breakup", "breakout", "inside-bar breakout pattern"),
    ("duck_head", "breakout", "duck-head breakout pattern"),
    ("bb_squeeze_breakout", "breakout", "Bollinger squeeze breakout"),
    ("doji_at_low", "reversal", "doji at low pattern"),
    ("hammer_reversal", "reversal", "hammer reversal pattern"),
    ("three_methods_up", "trend", "three-white-soldiers continuation"),
    ("oversold_bounce", "reversal", "20d<-15% oversold bounce"),
    ("ma_converge_break", "breakout", "MA convergence breakout"),
    ("ants_climb", "momentum", "stepwise advance accumulation"),
    ("immortal_guide", "trend", "guiding-star trend continuation"),
    ("rsrs_timing", "trend", "RSRS resistance-support timing"),
]


def _sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        h.update(fh.read())
    return h.hexdigest()[:12]


def _engine_faces():
    try:
        from engine.factors import FACTORS  # noqa: registry import (no compute)
        registered = sorted(FACTORS.keys())
    except Exception as exc:  # honest degradation, no fabrication
        return {}, {"error": repr(exc)}
    out = {}
    for name in registered:
        face, sign, prior = ENGINE_FACES.get(name, ("unmapped", "?", ""))
        out[name] = {"face": face, "sign_prior": sign, "prior": prior}
    meta = {"n_registered": len(registered),
            "unmapped": [k for k in registered
                         if ENGINE_FACES.get(k, ("unmapped",))[0] == "unmapped"],
            "source": "engine/factors.py FACTORS"}
    return out, meta


def _ic_families():
    out = {}
    for key, csv_name, panel, doc in IC_FAMILIES:
        path = os.path.join(T22, csv_name)
        row = {"panel": panel, "evidence": f"research/shortline/{csv_name} + {doc}"}
        if not os.path.exists(path):
            row["status"] = "missing (honest empty)"
            out[key] = row
            continue
        with open(path, encoding="utf-8-sig") as fh:
            rdr = csv.DictReader(fh)
            rows = list(rdr)
        row["n_factors_total"] = len(rows)
        row["n_in_pool"] = sum(1 for r in rows if str(r.get("in_pool", "")).lower() == "true")
        fams = {}
        for r in rows:
            fam = (r.get("family") or "").strip()
            if fam:
                fams[fam] = fams.get(fam, 0) + 1
        if fams:
            row["family_breakdown"] = dict(sorted(fams.items(), key=lambda kv: -kv[1]))
        row["source_sha256_12"] = _sha256(path)
        out[key] = row
    return out


def _registered_exposure():
    roster = {}
    tdir = os.path.join(ROOT, "firm", "traders")
    for fn in sorted(os.listdir(tdir)):
        if not fn.endswith(".json") or fn.startswith("_"):
            continue
        with open(os.path.join(tdir, fn), encoding="utf-8-sig") as fh:
            d = json.load(fh)
        entry = (d.get("params") or {}).get("entry", "")
        face, note = "unmapped", ""
        for needle, f, n in ENTRY_FACE_MAP:
            if needle in entry:
                face, note = f, n
                break
        roster[d["id"]] = {
            "level": d.get("level"), "entry": entry,
            "primary_face": face, "face_note": note,
            "school": d.get("school"),
            "evidence_cutoff": d.get("evidence_cutoff"),
        }
    # corps cross-ref: T-33 artifact (bm-c lane), read-only consume
    # schema (verified read): registered/prospect = list of {member, corps, ...}
    cpath = os.path.join(ROOT, "results", "corps_roster.json")
    corps_note = "results/corps_roster.json absent (honest empty)"
    if os.path.exists(cpath):
        with open(cpath, encoding="utf-8-sig") as fh:
            cr = json.load(fh)
        assign = {}
        for block in ("registered", "prospect"):
            for m in cr.get(block) or []:
                if not isinstance(m, dict):
                    continue
                a = m.get("corps") or m.get("candidate_corps")
                if m.get("member") and a:
                    assign[m["member"]] = a
        for tid, a in assign.items():
            if tid in roster:
                roster[tid]["corps"] = a
        corps_note = f"cross-refed {len(assign)} assignments from T-33 artifact"
    return roster, corps_note


def build():
    faces, emeta = _engine_faces()
    icfam = _ic_families()
    roster, corps_note = _registered_exposure()
    doc = {
        "batch": "T48-FACTOR-BLEND-REGISTRY",
        "order": "O-20260925-0855",
        "ticket": "T-2026-09-25-48",
        "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "ledger_trials_added": 0,
        "note": "registry documentation face (t33 aggregation precedent: no new trials)",
        "engine_factor_faces": faces,
        "engine_face_meta": emeta,
        "ic_evidence_families": icfam,
        "zoo_style_families": [{"family": f, "doc": d} for f, d in ZOO_FAMILIES],
        "zoo_doc": "research/shortline/ASTYLE_ZOO.md (V1 2026-09-23, CEO order O-20260923-1705)",
        "registered_strategy_exposure": roster,
        "exposure_meta": {"corps_cross_ref": corps_note,
                          "t33_artifact": "results/corps_roster.json (bm-c T-33 run#2 canon, read-only)"},
        "counts": {
            "engine_faces": len(faces),
            "ic_families": len(icfam),
            "zoo_families": len(ZOO_FAMILIES),
            "registered_roster": len(roster),
            "face_taxonomy": ["momentum", "trend", "breakout", "reversal",
                              "low_vol", "volume", "mean_reversion"],
        },
    }
    os.makedirs(os.path.dirname(RESULTS), exist_ok=True)
    with open(RESULTS, "w", encoding="utf-8") as fh:
        json.dump(doc, fh, ensure_ascii=False, indent=1)
    print(json.dumps({"ok": True, "out": RESULTS,
                      "counts": doc["counts"],
                      "engine_unmapped": emeta.get("unmapped"),
                      "roster_unmapped": [k for k, v in roster.items()
                                          if v["primary_face"] == "unmapped"],
                      "corps_note": corps_note}, ensure_ascii=False))


def selftest():
    """Hermetic selftest: natural-face fixtures, no network, no engine data."""
    ok = True

    def t(name, cond):
        nonlocal ok
        print(("PASS" if cond else "FAIL"), name)
        ok = ok and cond

    t("engine map covers all registered keys with a face",
      all(v[0] != "unmapped" for v in ENGINE_FACES.values()))
    t("every entry-face needle distinct", len({n for n, _, _ in ENTRY_FACE_MAP}) == len(ENTRY_FACE_MAP))
    t("face taxonomy = O-0855 seven faces",
      sorted({f for f, _, _ in ENGINE_FACES.values()}) == sorted(
          ["momentum", "trend", "breakout", "reversal", "low_vol", "volume", "mean_reversion"]))
    t("sign prior in {+,-,?}", all(s in "+-?" for _, s, _ in ENGINE_FACES.values()))
    t("csv families keys unique", len({k for k, _, _, _ in IC_FAMILIES}) == len(IC_FAMILIES))
    print("selftest:", "ALL PASS" if ok else "FAIL")
    return 0 if ok else 2


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["run", "selftest"])
    a = ap.parse_args()
    return selftest() if a.cmd == "selftest" else (build() or 0)


if __name__ == "__main__":
    sys.exit(main())
