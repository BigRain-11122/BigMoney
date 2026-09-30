"""RW-1 verification probe (r472 bm-a, ticket T-127, decision D-20260930-05).

Two legs:
  leg-1 synthetic: entry signal at day T fills at T+1 open (pre-existing),
      exit signal at day T must now fill at T+1 open with the T+1 open
      price -- the pre-fix engine filled exits at the SAME close (audit
      P0-1 look-ahead). Asserts exact fill date + exact fill price.
  leg-2 registered-member old-vs-new: recomputes the 6 registered
      traders' anchor evidence under the fixed engine and emits the
      old-vs-new diff table (RW-1 acceptance: honest overstatement
      disclosure). Read-only against trader JSONs unless --refreeze.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import pandas as pd


def leg1_synthetic() -> dict:
    import numpy as np
    from engine import run_backtest

    dates = pd.date_range("2026-01-05", periods=12, freq="B")
    # distinctive prices: open_k = 100 + k (fill dates identifiable),
    # close chosen so nothing else matters (explicit signals injected).
    opens = [100.0 + k for k in range(12)]
    closes = [100.5 + k for k in range(12)]
    df = pd.DataFrame({
        "open": opens, "high": [o + 1 for o in opens],
        "low": [o - 1 for o in opens], "close": closes,
    }, index=dates)
    entry = pd.DataFrame(False, index=dates, columns=["SYM"])
    exit_ = pd.DataFrame(False, index=dates, columns=["SYM"])
    entry.loc[dates[2], "SYM"] = True   # signal day T=dates[2]
    exit_.loc[dates[6], "SYM"] = True  # exit signal day T=dates[6]
    r = run_backtest({"SYM": df}, {}, entry_signal=entry, exit_signal=exit_)
    trades = r["trades"]
    assert len(trades) == 1, f"expected exactly 1 exit trade, got {len(trades)}: {trades}"
    t = trades[0]
    fill_date = pd.Timestamp(t["date"])
    want_date = dates[7]              # T+1 of the exit-signal day
    want_px = round(opens[7], 4)     # T+1 open, not the close of day 6
    ok_date = fill_date == want_date
    ok_px = abs(t["price"] - want_px) < 1e-9
    ok_not_close = abs(t["price"] - closes[6]) > 1e-9
    return {"ok": bool(ok_date and ok_px and ok_not_close),
            "fill_date": str(fill_date.date()), "fill_px": t["price"],
            "want_date": str(want_date.date()), "want_px": want_px,
            "old_close_px": closes[6],
            "asserts": {"fill_is_Tplus1_open": bool(ok_date and ok_px),
                        "not_signal_day_close": bool(ok_not_close)}}


def leg2_members(refreeze: bool) -> dict:
    from live import paper as live_paper
    from firm.hr import list_traders, load_trader, save_trader

    prices_full = live_paper.load_core()
    reg_ids = [t["id"] for t in list_traders()
               if t.get("level") in live_paper.PAPER_LEVELS]
    out = {"members": {}, "refrozen": refreeze, "n_registered": len(reg_ids)}
    for tid in reg_ids:
        t = load_trader(tid)
        a = live_paper.anchor_gate(t, prices_full)
        got = a.get("got")
        if got is None:
            out["members"][tid] = {"ok": False, "error": a.get("error")}
            continue
        want_old = t["backtest"]
        # frozen schema keys: sharpe / max_dd / annual / trades
        # (anchor 'got' face: sharpe / max_drawdown / annual_return / trades)
        new_seg = {}
        for seg in ("in_sample", "out_sample"):
            new_seg[seg] = {
                "sharpe": got[seg]["sharpe"],
                "max_dd": got[seg]["max_drawdown"],
                "annual": got[seg]["annual_return"],
                "trades": got[seg]["trades"],
            }
        row = {
            "ok_new_recompute": True,
            "old": {"in_sample": want_old["in_sample"],
                    "out_sample": want_old["out_sample"]},
            "new": new_seg,
            "delta": {},
        }
        for seg in ("in_sample", "out_sample"):
            for k in ("sharpe", "max_dd", "annual"):
                row["delta"][f"{seg}.{k}"] = round(
                    new_seg[seg][k] - want_old[seg][k], 4)
            row["delta"][f"{seg}.trades"] = (
                new_seg[seg]["trades"] - want_old[seg]["trades"])
        out["members"][tid] = row
        if refreeze:
            t["backtest"]["in_sample"] = new_seg["in_sample"]
            t["backtest"]["out_sample"] = new_seg["out_sample"]
            save_trader(t)
    return out


def main() -> int:
    refreeze = "--refreeze" in sys.argv
    l1 = leg1_synthetic()
    print("[leg-1 synthetic T+1-open exit]", json.dumps(l1, ensure_ascii=False))
    l2 = leg2_members(refreeze)
    print("[leg-2 members old-vs-new]", json.dumps(l2, ensure_ascii=False))
    artifact = ROOT / "results" / "_r472bma_rw1_probe.json"
    artifact.write_text(json.dumps(
        {"leg1": l1, "leg2": l2,
         "evidence_cutoff": "2026-09-22"}, ensure_ascii=False, indent=1),
        encoding="utf-8")
    if not l1["ok"]:
        print("LEG1 FAIL")
        return 2
    print("PROBE OK ->", artifact.name)
    return 0


if __name__ == "__main__":
    sys.exit(main())
