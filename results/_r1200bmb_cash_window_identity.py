"""E128 receipt: does the cash identity residual grow with the window?

The E40 cashdrag face is burned on one start (2020-01-01), so it can publish a
residual but cannot answer whether that residual is a stable valuation gap or
something that grows. This receipt burns the same leg on a second start and
writes both windows' per-book identity rows to one small file, so the answer is
re-derivable instead of living in prose.

Zero network, zero write outside results/e40_cashleg_drag/, no gate, no verdict.
"""
import io
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import e39_panel_census as E  # noqa: E402

STARTS = ("2020-01-01", "2023-01-01")


def main():
    face = E.run_cashdrag(None, starts=STARTS)
    rows = {}
    for start, win in face["windows"].items():
        rows[start] = {
            "bars": win["bars"],
            "cash_window_note": win["cash_window_note"],
            "books": {
                name: {
                    "first_trading_rebalance_index": r["first_trading_rebalance_index"],
                    "bars_beyond_burn_in": r["bars_beyond_burn_in"],
                    "window_is_burn_in_driven": r["window_is_burn_in_driven"],
                    "cash_bar_share_pct": r["cash_bar_share_pct"],
                    "mean_annual_cash_rate_pct": r["mean_annual_cash_rate_pct"],
                    "expected_linear_bp": r["expected_linear_bp"],
                    "measured_attribution_bp": r["measured_attribution_bp"],
                    "residual_bp": r["residual_bp"],
                    "ratio_measured_over_expected": r["ratio_measured_over_expected"],
                    "within_tolerance": r["within_tolerance"],
                }
                for name, r in win["cash_window_by_book"].items()
            },
        }
    out = {
        "study": "e128_cash_window_identity",
        "evidence_cutoff": face["evidence_cutoff"],
        "starts": list(STARTS),
        "windows": rows,
        "questions": {
            "is_the_ladder_wide_gap_a_window_effect":
                {s: rows[s]["cash_window_note"]["same_window_for_both_books"] for s in rows},
            "does_the_residual_grow_with_the_window":
                {s: {n: rows[s]["books"][n]["residual_bp"] for n in rows[s]["books"]}
                 for s in rows},
        },
        "honest": [
            "the identity is rate x share in bp; the engine compounds the accrual on the "
            "equity curve, so the measured attribution is not required to equal it",
            "a residual that scales with the cash share is a property of compounding on a "
            "different base return, not evidence of a second cash channel",
            "descriptive census only: no gate, no verdict, no prereg, no trial count",
        ],
    }
    outdir = os.path.join(ROOT, "results", "e40_cashleg_drag")
    os.makedirs(outdir, exist_ok=True)
    p = os.path.join(outdir, "IDENTITY-%s.json" % face["evidence_cutoff"].replace("-", ""))
    with io.open(p, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(json.dumps(out, ensure_ascii=False, indent=1, sort_keys=True) + "\n")
    print(json.dumps({"file": os.path.relpath(p, ROOT),
                      "questions": out["questions"]}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())