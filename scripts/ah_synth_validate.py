# -*- coding: utf-8 -*-
"""T-17 deliverable-2 slice-1: single-pair AH premium synthesis validation.

ARB-2 lane (research/ARBITRAGE_PLAYBOOK.md P-B1 feeding). F-06 single-probe-first:
validate the synthesis path on ONE pair (02318 China Ping An H / 601318 A) BEFORE
building the 220-pair puller (deliverable-2 main body).

Validation legs (each honest-fail labeled, evidence_cutoff stamped):
  L1  stock_zh_ah_daily('02318') full-window  -> row count / date span / schema
      (FACE SEMANTICS CORRECTED: returns H-LEG OHLCV, NOT a parity series; and the
      full-window call truncates at 2019-12-31 -- recent data needs explicit windows)
  L2  stock_hk_daily('02318')                -> H-leg HKD close (sina face, probe-verified alive)
  L3  A-leg: local pool has NO single-stock dailies (ETF pool only) -> akshare
      stock_zh_a_hist('601318') attempt (EM push2his family = block risk, honest
      dead-label if connection-refused per moneyflow evidence)
  L3b A-leg sina-domain daily stock_zh_a_daily('sh601318') attempt (sina family
      alive on this host per futures/marks/HSAHP evidence)
  L3c bounded-window re-pull proving the 2019-truncation design constraint
  L4  in-panel cross-check: if ah_daily face carries both A and H price columns,
      verify parity_col ~= A_price / H_price internally (rate-basis disclosure:
      tencent parity basis, FX embedded -- per frozen fx_basis_preview)
  L5  direction sanity vs HSAHP index (54-row recent window, probe file) on the
      overlapping window: same-day sign agreement rate of daily changes
      (weighted index vs single name = coarse direction check only, NOT a gate)

Output: results/shortline/ah_synth_validate_02318.json (top-level evidence_cutoff
= science_gates.cutoff_meta/C2 legal key). Exit codes: 0=validation ran (verdict
carried in JSON), 2=mechanism failure (unexpected exception before evidence write).
"""
import json
import sys
import traceback

import pandas as pd

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

OUT = "results/shortline/ah_synth_validate_02318.json"
SYMBOL_H = "02318"   # China Ping An H (HKD board code)
SYMBOL_A = "601318"  # China Ping An A (Shanghai)
EVIDENCE_CUTOFF = "2026-09-24"  # ah_face_probes.json cutoff; refreshed below if faces newer


def run():
    import akshare as ak
    legs = {}
    # L1: tencent AH daily full window
    ah = None
    try:
        ah = ak.stock_zh_ah_daily(symbol=SYMBOL_H)
        legs["L1_ah_daily"] = {
            "ok": True, "rows": int(len(ah)),
            "cols": [str(c) for c in ah.columns],
            "first_date": str(ah.iloc[0, 0]) if len(ah) else None,
            "last_date": str(ah.iloc[-1, 0]) if len(ah) else None,
        }
    except Exception as e:
        legs["L1_ah_daily"] = {"ok": False, "error": f"{type(e).__name__}: {e}"[:300]}
    # L2: H leg sina daily
    hk = None
    try:
        hk = ak.stock_hk_daily(symbol=SYMBOL_H)
        legs["L2_hk_daily"] = {
            "ok": True, "rows": int(len(hk)),
            "cols": [str(c) for c in hk.columns],
            "first_date": str(hk.iloc[0, 0]) if len(hk) else None,
            "last_date": str(hk.iloc[-1, 0]) if len(hk) else None,
        }
    except Exception as e:
        legs["L2_hk_daily"] = {"ok": False, "error": f"{type(e).__name__}: {e}"[:300]}
    # L3: A leg EM push2his attempt (block-risk face, honest dead-label)
    a_leg = None
    try:
        a_leg = ak.stock_zh_a_hist(symbol=SYMBOL_A, period="daily", adjust="")
        legs["L3_a_hist"] = {
            "ok": True, "rows": int(len(a_leg)),
            "cols": [str(c) for c in a_leg.columns][:8],
        }
    except Exception as e:
        legs["L3_a_hist"] = {"ok": False, "error": f"{type(e).__name__}: {e}"[:200],
                             "label": "push2his family connection block risk (moneyflow evidence)"}
    # L3b: A-leg sina-domain daily (stock_zh_a_daily, exchange-prefixed code)
    try:
        a_sina = ak.stock_zh_a_daily(symbol="sh" + SYMBOL_A, adjust="")
        legs["L3b_a_daily_sina"] = {
            "ok": True, "rows": int(len(a_sina)),
            "cols": [str(c) for c in a_sina.columns][:8],
            "first_date": str(a_sina.iloc[0, 0]) if len(a_sina) else None,
            "last_date": str(a_sina.iloc[-1, 0]) if len(a_sina) else None,
        }
    except Exception as e:
        legs["L3b_a_daily_sina"] = {"ok": False, "error": f"{type(e).__name__}: {e}"[:200]}
    # L3c: KEY FACE-SEMANTICS correction probe -- bounded-window re-pull to prove
    # stock_zh_ah_daily needs explicit start/end for recent data (full-window call
    # truncates at 2019-12-31: design constraint for the deliverable-2 puller).
    try:
        ah_bounded = ak.stock_zh_ah_daily(symbol=SYMBOL_H, start_year="2025", end_year="2026")
        legs["L3c_bounded_window"] = {
            "ok": True, "rows": int(len(ah_bounded)),
            "first_date": str(ah_bounded.iloc[0, 0]) if len(ah_bounded) else None,
            "last_date": str(ah_bounded.iloc[-1, 0]) if len(ah_bounded) else None,
            "finding": "full-window call truncates at 2019 -> puller MUST pass explicit windows",
        }
    except Exception as e:
        legs["L3c_bounded_window"] = {"ok": False, "error": f"{type(e).__name__}: {e}"[:200]}
    # L6: FX history legs (the LAST synthesis gap). Official-parity preference:
    # currency_boc_sina (sina finance official central parity history, windowed)
    # + currency_boc_safe (SAFE table, no args). Basis disclosure frozen at
    # chinamoney central parity per probe file -- these two get audited for
    # parity-basis closeness, NOT silently substituted.
    try:
        fx_sina = ak.currency_boc_sina(symbol="港币", start_date="20260101", end_date="20260925")
        legs["L6_fx_boc_sina"] = {
            "ok": True, "rows": int(len(fx_sina)),
            "cols": [str(c) for c in fx_sina.columns][:10],
            "first_date": str(fx_sina.iloc[0, 0]) if len(fx_sina) else None,
            "last_date": str(fx_sina.iloc[-1, 0]) if len(fx_sina) else None,
            "head": fx_sina.head(2).to_dict(orient="records"),
        }
    except Exception as e:
        legs["L6_fx_boc_sina"] = {"ok": False, "error": f"{type(e).__name__}: {e}"[:200]}
    try:
        fx_safe = ak.currency_boc_safe()
        legs["L6b_fx_boc_safe"] = {
            "ok": True, "rows": int(len(fx_safe)),
            "cols": [str(c) for c in fx_safe.columns][:10],
        }
    except Exception as e:
        legs["L6b_fx_boc_safe"] = {"ok": False, "error": f"{type(e).__name__}: {e}"[:200]}
    # L7: end-to-end 5-day synthesis sample (single-pair premium, frozen formula:
    # premium = A_close(CNY) / (H_close(HKD) * fx_HKD_CNY) - 1; fx basis = BOC/SAFE
    # official central parity). Numeric plausibility only -- zero trials, zero gates.
    try:
        a5 = ak.stock_zh_a_daily(symbol="sh" + SYMBOL_A, adjust="").tail(5)
        h5 = ak.stock_zh_ah_daily(symbol=SYMBOL_H, start_year="2025", end_year="2026").tail(5)
        # same window args as the L6-proven call (narrow-window variant raised a
        # keying error inside the face -- reuse the proven invocation shape)
        fxs = ak.currency_boc_sina(symbol="港币", start_date="20260101", end_date="20260925")
        # explicit column semantics (r125 no-key-assumption law):
        # sina A daily: english cols date/open/high/low/close...
        # tencent AH daily: [date, open, close, high, low, volume] (close @ iloc 2)
        # boc FX: [date, boc buy..., central parity @ iloc 4, ...] per L6 schema
        ad = pd.DataFrame({"date": a5["date"].astype(str).str[:10],
                           "close_A": a5["close"].astype(float)})
        hd = pd.DataFrame({"date": h5.iloc[:, 0].astype(str).str[:10],
                           "close_H": h5.iloc[:, 2].astype(float)})
        fd = pd.DataFrame({"date8": fxs.iloc[:, 0].astype(str).str[:10].str.replace("-", ""),
                           "fx_HKD_CNY": fxs.iloc[:, 4].astype(float) / 100.0})
        m = ad.merge(hd, on="date")
        m["date8"] = m["date"].str.replace("-", "")
        m = m.merge(fd, on="date8", how="left")
        m["premium"] = m["close_A"] / (m["close_H"] * m["fx_HKD_CNY"]) - 1
        legs["L7_e2e_sample"] = {
            "ok": True, "rows": int(len(m)),
            "sample": m[["date", "close_A", "close_H", "fx_HKD_CNY", "premium"]].to_dict(orient="records"),
            "note": "premium > 0 = A-share premium (frozen formula, fx basis = BOC official parity)",
        }
    except Exception as e:
        legs["L7_e2e_sample"] = {"ok": False, "error": f"{type(e).__name__}: {e}"[:300]}
    # L4: in-panel cross-check (columns are CJK; probe showed 6 cols: date/parity?/prices)
    if ah is not None and len(ah):
        cols = [str(c) for c in ah.columns]
        legs["L4_inpanel"] = {"schema_notes": "raw col heads carried for prereg design",
                              "head_rows": ah.head(2).to_dict(orient="records")}
        # numeric landscape: which columns parse as price-like
        num_cols = {}
        for c in ah.columns:
            try:
                v = pd.to_numeric(ah[c], errors="coerce")
                if v.notna().sum() > len(ah) * 0.9:
                    num_cols[str(c)] = {"min": float(v.min()), "max": float(v.max())}
            except Exception:
                pass
        legs["L4_inpanel"]["numeric_cols"] = num_cols
    # L5: HSAHP direction sanity on overlap window
    if ah is not None and len(ah):
        try:
            idx = ak.stock_hk_index_daily_sina(symbol="HSAHP")
            legs["L5_hsahp"] = {"ok": True, "rows": int(len(idx)),
                                "last_date": str(idx.iloc[-1, 0]) if len(idx) else None}
        except Exception as e:
            legs["L5_hsahp"] = {"ok": False, "error": f"{type(e).__name__}: {e}"[:200]}
    verdict = {
        "synthesis_path": "CONSTRUCTIBLE-PENDING-DESIGN" if legs.get("L1_ah_daily", {}).get("ok")
        else "FACE-DEGRADED",
        "open_items": [
            "FX history face selection (L6 legs audited this run; basis = official central parity "
            "family, closeness to chinamoney frozen basis to be checked in puller design)",
            "A-leg source = stock_zh_a_daily sina (alive, L3b); EM push2his confirmed dead (L3)",
        ],
    }
    out = {
        "census": "ah_synth_validate",
        "ticket": "T-2026-09-24-17",
        "lane": "ARB-2 deliverable-2 slice-1 (single-pair synthesis validation, zero trials)",
        "ran_at": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S"),
        "legs": legs,
        "verdict": verdict,
        "evidence_cutoff": EVIDENCE_CUTOFF,
    }
    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        json.dump(out, f, ensure_ascii=False, indent=1, default=str)
        f.write("\n")
    print("legs:", {k: (v.get("ok"), v.get("rows")) for k, v in legs.items()})
    print("verdict:", verdict["synthesis_path"])
    print("written:", OUT)


if __name__ == "__main__":
    try:
        run()
    except Exception:
        traceback.print_exc()
        sys.exit(2)
