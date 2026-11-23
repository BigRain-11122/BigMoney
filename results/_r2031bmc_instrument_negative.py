"""Negative control for r2031 (astock_veto_hedge_instrument).

The face publishes four tokens.  A token is worth nothing if the machinery would print
it regardless of the data, so this control feeds the *same* loaders, costs and arithmetic
two books whose answers must be different from the published one:

  A. a book that IS the CSI 300 (the 510300 panel's own period returns)
     -> the winner must move to 510300, share removed must be ~1.00, and both rivals must
        fail to reach that risk.  If the face's picker were stuck on 512100 this fails.

  B. a book that is half CSI 300 and half CSI 500 by construction
     -> no single index can explain it, but the two-leg fit can, so SECOND_LEG_PAYS must
        fire.  If the face's second-leg test were stuck on "does not pay" this fails.

Nothing here touches the published face: it only asserts that the machinery disagrees
with itself when the data disagrees.

Usage:
    python results/_r2031bmc_instrument_negative.py
"""
from __future__ import annotations

import os
import sys

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import astock_veto_hedge_instrument as M  # noqa: E402

ok = fail = 0


def _ok(cond, msg):
    global ok, fail
    if cond:
        ok += 1
        print("PASS  %s" % msg)
    else:
        fail += 1
        print("FAIL  %s" % msg)


def main() -> int:
    book = M.load_book()
    hedges = {s: M.load_hedge(s, c) for s, _n, c in M.CANDIDATES}
    cal = hedges["512100"]["dates"]
    dates = book["dates"]
    ends, _spans = M.period_ends(dates, cal)
    h = {s: M.hedge_returns(dates, ends, hedges[s]["close"]) for s in hedges}

    def fit_on(synth_net):
        """Betas, shares and floors for one synthetic book on the real hedge panels."""
        out = {}
        for s in ("510300", "510500", "512100"):
            b, hh, _keep = M._pair({"net": synth_net, "dates": dates}, h[s])
            fit = M.ols(b, hh)
            var = M.variance_read(b, hh, fit["beta"]) if fit["beta"] is not None else {}
            out[s] = {"beta": fit["beta"], "r2": fit["r2"],
                      "share": var.get("share_removable"),
                      "arm": M.stats(M.arm_series(synth_net, h[s], 1.0, fit["beta"] or 0.0))}
        return out

    # ---------------------------------------------------------------- control A
    per_a = fit_on(list(h["510300"]))
    pick_a = M.pick_index({s: per_a[s]["share"] for s in per_a})
    _ok(pick_a["best"] == "510300",
        "A: a book that IS the CSI 300 picks 510300 (got %s)" % pick_a["best"])
    _ok(per_a["510300"]["share"] > 0.999,
        "A: the right index removes ~all the variance (%.4f)" % per_a["510300"]["share"])
    _ok(pick_a["verdict"] == "HEDGE_INSTRUMENT_MATTERS",
        "A: a 60pp+ spread is still called a real choice")

    target_a = per_a["510300"]["arm"]["annual_vol"]
    floors_a = {s: M.vol_floor(list(h["510300"]), h[s], per_a[s]["beta"] or 0.0) for s in per_a}
    reach_a = M.reach_verdict(target_a, floors_a, "510300",
                              per_a["510300"]["arm"]["annualized_compound"])
    _ok(reach_a["verdict"] == "NO_RIVAL_REACHES_THIS_RISK",
        "A: with the right index the rivals cannot reach its risk (%s)" % reach_a["verdict"])

    # ---------------------------------------------------------------- control B
    mixed = [0.5 * a + 0.5 * b for a, b in zip(h["510300"], h["510500"])]
    per_b = fit_on(mixed)
    pick_b = M.pick_index({s: per_b[s]["share"] for s in per_b})
    b1, b2 = [], []
    for i in range(len(dates)):
        vals = (mixed[i], h["510300"][i], h["510500"][i])
        if any(v is None or not np.isfinite(v) for v in vals):
            continue
        b1.append(float(vals[0]))
        b2.append((float(vals[1]), float(vals[2])))
    fit_two = M.ols_two(b1, [x[0] for x in b2], [x[1] for x in b2])
    resid = np.asarray(fit_two["resid"], dtype=np.float64)
    pair_vol = float(np.std(resid, ddof=1) * np.sqrt(M.PPY))
    single_vol = per_b[pick_b["best"]]["arm"]["annual_vol"]
    second = M.second_leg_verdict(single_vol, pair_vol)
    _ok(second["verdict"] == "SECOND_LEG_PAYS",
        "B: a book split across two indexes makes the second leg pay (%s, removed %.4f)"
        % (second["verdict"], second["removed_vol"] or float("nan")))
    _ok(pair_vol < single_vol / 2.0,
        "B: the two-leg fit leaves less than half the single-leg residual (%.4f vs %.4f)"
        % (pair_vol, single_vol))
    _ok(pick_b["best"] in ("510300", "510500"),
        "B: the single-leg winner moves off 512100 (got %s)" % pick_b["best"])

    # ---------------------------------------------------------------- published face
    face = M._read_json(M.OUT_JSON)
    _ok(face["reads"]["best_by_share"] == "512100",
        "the published face picks 512100 -- the opposite of control A's 510300")
    _ok(face["verdict_second_leg"] == "SECOND_LEG_DOES_NOT_PAY",
        "the published face says the second leg does not pay -- the opposite of control B")

    print("negative control %d/%d PASS" % (ok, ok + fail))
    return 0 if fail == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
