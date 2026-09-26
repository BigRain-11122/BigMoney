"""r242 T-78 s4: EXIT-OVERLAY-P1 winner wiring (bm-b).

Frozen prereg research/EXIT_OVERLAY_P1.md 10/8-4: WIN configs ->
member registration update + paper wiring (code face landed this round:
dd_control kwarg at live/paper.py 4 call sites + t28 sleeve worker) +
anchor expectations re-derived SAME round (prereg sanctions the number
change) + x2 seed re-derive + status_history three-state notation.

Wiring resolution (multiple WINs per member): wire the MAXIMAL winning
cell (nested cell family tp_ladder/trail/dd < full). Every wired config
is a frozen-3 cell that passed the frozen-4 dual-face non-hurt gate:
  COMPOSITE-CE-01 -> ov_tp_ladder (only WIN)
  COMPOSITE-CE-02 -> ov_full      (superset of its tp_ladder/dd_control WINs)
  ENGULF-CE-01    -> ov_full      (superset of its trail_peak WIN)
Cell configs are read from the judged batch artifact (zero re-typing).
Self-check before wiring: old-config CostPatch(2) face must reproduce
the registered cost_x2 sharpe (face-definition parity, |d|<0.002).
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for p in (ROOT, os.path.join(ROOT, "scripts")):
    if p not in sys.path:
        sys.path.insert(0, p)

import pandas as pd
from live import paper as lp
from firm.hr import load_trader, save_trader
from science_gates import CostPatch

WIRE = {
    "COMPOSITE-CE-01": "ov_tp_ladder",
    "COMPOSITE-CE-02": "ov_full",
    "ENGULF-CE-01": "ov_full",
}
TODAY = "2026-09-26"


def x2_faces(t: dict, prices_full: dict) -> dict:
    """cost_x2 registration face: CostPatch(2) run at evidence_cutoff
(ce_transfer L168 caliber: full-window sharpe + oos sharpe)."""
    cutoff = lp.evidence_cutoff(t, prices_full)
    ps = pd.Timestamp(cutoff)
    prices = {s: df[df.index <= ps] for s, df in prices_full.items()}
    P = lp.build_panels(prices)
    entry = lp.SIGNAL_BUILDERS[t["params"]["entry"]](P)
    params = {k: v for k, v in t["params"].items() if k != "entry"}
    with CostPatch(2), lp.ExitPatch(t.get("exit_overrides")):
        res = lp.run_backtest(prices, params, entry_signal=entry,
                              exit_signal=(entry <= 0),
                              dd_control=t.get("dd_control"))
    idx = P["close"].index
    eq = pd.Series(res["equity_curve"], index=idx[:len(res["equity_curve"])])
    return {"full": lp.seg_metrics(eq), "oos": lp.seg_metrics(eq, lp.OOS_START)}


def wiring_note(cname: str, ov_bits: list, d_full, d_oos) -> str:
    return (
        "T-78 s4 EXIT-OVERLAY-P1 winner wiring: cell " + cname
        + " (" + "; ".join(ov_bits) + "). WIN per frozen dual-face "
        "non-hurt gate; batch evidence results/exit_overlay_p1.json "
        "pairs/stress_x2 (d_full=" + str(d_full)
        + ", d_oos=" + str(d_oos) + "). Anchor expectations re-derived "
        "same round per prereg s4; three-state: legislation=commit / "
        "effect=anchor re-derive PASS / review=post_review pending. "
        "Rejected cells not wired (lessons research/EXIT_OVERLAY_P1.md "
        "8).")


def main() -> int:
    with open(os.path.join(ROOT, "results", "exit_overlay_p1.json"),
              encoding="utf-8-sig") as fh:
        batch = json.load(fh)
    cells = batch["cells"]

    prices_full = lp.load_core()
    vi_bar = lp.load_vi_bar()
    assert vi_bar is not None, "vi_bar unavailable -- x2 seed face blinded"

    # -- self-check: face-definition parity on OLD configs -------------
    for tid in WIRE:
        t = load_trader(tid)
        reg_x2 = (t.get("backtest") or {}).get("cost_x2") or {}
        if reg_x2.get("sharpe") is None:
            print("SELFCHK " + tid + ": no registered cost_x2.sharpe -- skip")
            continue
        got_x2 = x2_faces(t, prices_full)["full"]["sharpe"]
        d = abs(got_x2 - reg_x2["sharpe"])
        print("SELFCHK " + tid + ": old-config x2 full=" + str(got_x2)
              + " registered=" + str(reg_x2["sharpe"]) + " |d|=" + str(d))
        assert d < 0.002, tid + ": x2 face parity FAIL -- abort wiring"

    # -- wire ----------------------------------------------------------
    report = []
    for tid, cname in WIRE.items():
        t = load_trader(tid)
        cell = cells[cname]
        cell_rec = batch["pairs"][tid]["cells"][cname]
        old_bt = json.loads(json.dumps(t["backtest"]))

        t["params"].update(cell["params"])
        t["exit_overrides"].update(cell["patch"])
        if cell.get("engine_kw", {}).get("dd_control"):
            t["dd_control"] = dict(cell["engine_kw"]["dd_control"])

        anchor = lp.anchor_gate(t, prices_full)
        assert "got" in anchor, tid + ": anchor re-derive error " + str(anchor)
        got = anchor["got"]

        t["backtest"]["in_sample"] = {
            "sharpe": got["in_sample"]["sharpe"],
            "max_dd": got["in_sample"]["max_drawdown"],
            "annual": got["in_sample"]["annual_return"],
            "trades": got["in_sample"]["trades"]}
        t["backtest"]["out_sample"] = {
            "sharpe": got["out_sample"]["sharpe"],
            "max_dd": got["out_sample"]["max_drawdown"],
            "annual": got["out_sample"]["annual_return"],
            "trades": got["out_sample"]["trades"]}

        x2 = x2_faces(t, prices_full)
        x2_sharpe = x2["full"]["sharpe"]
        c2 = t["backtest"]["cost_x2"]
        c2["sharpe"] = x2_sharpe
        if "oos_sharpe" in c2:
            c2["oos_sharpe"] = x2["oos"]["sharpe"]
        c2["survive"] = bool(x2_sharpe > vi_bar)
        c2["note"] = (c2.get("note", "").split("; re-derived")[0]
                      + "; re-derived " + TODAY + " with T-78 overlay "
                        "(prereg s4 same-round expectation update)")

        margin = round(x2_sharpe - vi_bar, 4)
        survive = bool(margin > 0)
        probation = bool(margin < lp.X2_PROBATION_MARGIN or not survive)
        t["paper"]["x2_watch"] = {
            "status": "probation" if probation else "ok",
            "probation": probation, "margin": margin, "survive": survive,
            "source": "registration_x2_seed", "as_of": TODAY}

        ov_bits = []
        if cell["params"]:
            ov_bits.append("params+=" + ",".join(sorted(cell["params"])))
        if cell["patch"]:
            ov_bits.append("exit_overrides+=" + ",".join(sorted(cell["patch"])))
        if cell.get("engine_kw", {}).get("dd_control"):
            ov_bits.append("dd_control=on")
        t["status_history"].append({
            "date": TODAY, "from": "INTERN", "to": "INTERN",
            "note": wiring_note(cname, ov_bits, cell_rec["d_full"],
                                cell_rec["d_oos"])})
        save_trader(t)

        report.append(tid + " <- " + cname + ": IS "
                      + str(old_bt["in_sample"]["sharpe"]) + "->"
                      + str(got["in_sample"]["sharpe"]) + " | OOS "
                      + str(old_bt["out_sample"]["sharpe"]) + "->"
                      + str(got["out_sample"]["sharpe"]) + " | x2 "
                      + str(x2_sharpe) + " (margin " + str(margin)
                      + (", probation)" if probation else ", ok)"))

    # -- verification pass: reload + anchor gate must PASS ------------
    for tid in WIRE:
        t = load_trader(tid)
        a = lp.anchor_gate(t, prices_full)
        line = "VERIFY " + tid + ": anchor_ok=" + str(a["ok"])
        if a["ok"]:
            line += (" IS=" + str(a["got"]["in_sample"]["sharpe"])
                     + " OOS=" + str(a["got"]["out_sample"]["sharpe"]))
        print(line)
        assert a["ok"], tid + ": anchor gate FAIL after wiring"

    print("---")
    for r in report:
        print(r)
    return 0


if __name__ == "__main__":
    sys.exit(main())
