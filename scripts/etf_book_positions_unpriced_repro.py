"""r1483 (T29): what the positions face says when the execution bar has no closes.

The queue row (state/queue/tech.md T29) was written from a live incident: the ledger recorded a
2026-11-09 execution row while the price panel stopped at 2026-11-06, the replay marked the lots
on the older close, and the printed identity gap (-194.20 CNY / 20 bars) read as an engine error
and turned a smoke leg red. The panel has since caught up, so the condition cannot be reproduced
by simply running the tool -- this script reproduces it by handing `assess` the SAME products
with the panel truncated at the last bar that existed at the time, and records what the face now
says. It writes evidence only; the ledger is passed a copy and never stamped.
"""
import copy
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import etf_book_positions as P

OUT = os.path.join("results", "_r1483bmc_t29_unpriced_bar.json")
TRUNCATE_AT = "2026-11-06"


def main():
    real_loader = P.load_panel_and_rates

    def truncated_loader(holdings, **kw):
        closes, rates, missing = real_loader(holdings, **kw)
        cut = {}
        for sym, series in closes.items():
            cut[sym] = {d: v for d, v in series.items() if str(d) <= TRUNCATE_AT}
        return cut, {d: v for d, v in (rates or {}).items() if str(d) <= TRUNCATE_AT}, missing

    ticket = P._read_json(P.stack_face.latest_ticket_path())
    stack = P._read_json(P.STACK_FACE)
    ledger = copy.deepcopy(P.load_ledger())

    P.load_panel_and_rates = truncated_loader
    try:
        face = P.assess(ticket, stack, ledger, None)   # stamp=None -> writes nothing
    finally:
        P.load_panel_and_rates = real_loader

    st = face.get("settlement") or {}
    rp = face.get("replay") or {}
    acc = face.get("accrual") or {}
    ev = {
        "artifact": "r1483bmc_t29_unpriced_bar_repro",
        "question": ("does the positions face still print an identity verdict for an execution bar "
                     "the price panel cannot price?"),
        "setup": {"execution_bar": st.get("bar"), "panel_truncated_at": TRUNCATE_AT,
                  "ledger_rows": [r.get("bar") for r in ledger.get("rows") or []]},
        "settlement": st,
        "accrual_status": acc.get("status"),
        "accrual_valued_upto_bar": acc.get("valued_upto_bar"),
        "replay_identity_status": rp.get("identity_status"),
        "replay_identity_holds": rp.get("identity_holds"),
        "replay_identity_delta_cny": rp.get("identity_delta_cny"),
        "replay_missing_closes": rp.get("base_bar_missing_closes"),
        "replay_last_priced_day": rp.get("base_bar_last_priced_day"),
        "verdict": ("the face refuses to publish an identity for an unprintable bar: the bar is "
                    "named UNPRICED, the valuation stops at the last fully priced day, and the "
                    "CNY gap is printed as the fill-to-old-close distance, not as an engine error"
                    if (st.get("priced") is False and rp.get("identity_holds") is None
                        and acc.get("status") in ("NO_PRICED_BAR", "ACCRUED",
                                                  "NO_NEW_BAR"))
                    else "STILL PRINTS AN IDENTITY FOR AN UNPRICED BAR"),
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(ev, fh, ensure_ascii=False, indent=2)
        fh.write("\n")
    print(json.dumps(ev, ensure_ascii=False, indent=2))
    return 0 if ev["verdict"].startswith("the face refuses") else 1


if __name__ == "__main__":
    sys.exit(main())