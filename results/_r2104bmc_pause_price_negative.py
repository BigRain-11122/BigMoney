#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""negative / positive controls for idx_fut_carry_pause_price (r2104, bm-c).

A face that prints "the rule costs 1.03pp" is worth nothing unless the machinery could
have printed the opposite.  These are the controls that make the number mean something:

  C1  TRUE-NEGATIVE: on a synthetic leg whose carry is genuinely gone (a persistent
      -6pp/yr regime after a break), the pause must FIRE, and it must SAVE money.
      If the machinery cannot see a real broken leg, its "cost" reading is a constant.
  C2  IDENTITY: with the rule switched off (threshold -1e9) the filtered series must be
      byte-identical to the raw one, and cost must be exactly 0.
  C3  CEILING: always-paused cost must equal the raw annualised compound return.
  C4  RESUME CLAUSE: after a pause the leg must stay flat until the window clears 0, not
      the moment the window clears the threshold.
  C5  INDEPENDENT RECOMPUTE: the cost printed on the live face must be reproducible from
      the face's own two numbers (raw + filtered annualised), not from a helper alone.

Run: python results/_r2104bmc_pause_price_negative.py
"""
from __future__ import annotations

import io
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "scripts"))
sys.path.insert(0, ROOT)

import idx_fut_carry_pause_price as P   # noqa: E402

OUT = os.path.join(ROOT, "results", "_r2104bmc_pause_price_negative.json")


def main():
    rows = []

    def leg(name, cond, detail):
        rows.append({"control": name, "passed": bool(cond), "detail": detail})

    # C1 a genuinely broken leg: healthy for 300 bars, then carry turns to -0.05%/bar
    # (-3pp per 60 bars, so the rule's own ruler does call it broken)
    daily = [0.0004] * 300 + [-0.0005] * 300
    f, mask, eps = P.apply_pause(daily, 60, -2.0, 0.0)
    saved = P.ann_compound(f) - P.ann_compound(daily)
    leg("C1_true_negative",
        eps and saved > 0.5 and sum(1 for m in mask if m) > 100,
        "episodes=%d paused_bars=%d ann_gain_from_pausing=%+.2f pp"
        % (len(eps), sum(1 for m in mask if m), saved))

    # C2 identity when the rule is off
    f2, mask2, eps2 = P.apply_pause(daily, 60, -1e9, -1e9)
    leg("C2_identity",
        f2 == daily and not any(mask2) and not eps2 and abs(P.ann_compound(f2) - P.ann_compound(daily)) < 1e-12,
        "filtered == raw, no episodes, zero cost")

    # C3 ceiling: flat after the warm-up (the first `window` bars have no window yet and
    # are held by construction -- that is the honest ceiling, not a flat zero)
    f3, _, _ = P.apply_pause(daily, 60, 1e9, 1e9)
    leg("C3_ceiling",
        all(x == 0.0 for x in f3[60:]) and f3[:60] == daily[:60],
        "always-paused leaves the warm-up (%d bars) intact and is flat after; ann=%.4f%%"
        % (60, P.ann_compound(f3)))

    # C4 resume only after the window clears 0
    sh = [0.0002] * 100 + [-0.03] + [0.0002] * 10 + [0.004] * 40
    _, mask4, eps4 = P.apply_pause(sh, 20, -2.0, 0.0)
    if eps4:
        e = eps4[0]
        cum = P.rolling_cum(sh, 20)
        back = next((i for i in range(e["end"] + 1, len(sh)) if cum[i] >= 0.0), None)
        leg("C4_resume_clause",
            back is not None and e["end"] == back - 1,
            "paused %s..%s, window cleared 0 on bar %s (resume next bar)"
            % (e["start"], e["end"], back))
    else:
        leg("C4_resume_clause", False, "shock did not trigger at all")

    # C5 the live face's cost must be its own two numbers subtracted
    face_path = os.path.join(ROOT, "results", "idx_fut_carry_pause_price.json")
    if not os.path.exists(face_path):
        leg("C5_independent_recompute", False, "face missing")
    else:
        with io.open(face_path, encoding="utf-8") as fh:
            face = json.load(fh)
        bad = []
        for prod, p in face["products"].items():
            if p.get("status") != "ok":
                continue
            for key, b in p["rulings"].items():
                want = round(b["raw_ann_compound_pct"] - b["ann_compound_pct"], 4)
                if abs(want - b["cost_pp"]) > 0.002:
                    bad.append("%s %s %r != %r" % (prod, key, b["cost_pp"], want))
        leg("C5_independent_recompute", not bad,
            "checked %d product-legs on the live face%s"
            % (len([p for p in face["products"].values() if p.get("status") == "ok"]),
               "" if not bad else "; mismatches: " + "; ".join(bad[:4])))

    npass = sum(1 for r in rows if r["passed"])
    payload = {"schema": "pause-price-controls/v1", "controls": rows,
               "passed": npass, "total": len(rows),
               "verdict": "ALL_CONTROLS_PASS" if npass == len(rows) else "CONTROL_FAILED"}
    with io.open(OUT, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=1)
    for r in rows:
        print("%-26s %s  %s" % (r["control"], "PASS" if r["passed"] else "FAIL", r["detail"]))
    print("%d/%d %s" % (npass, len(rows), payload["verdict"]))
    return 0 if npass == len(rows) else 1


if __name__ == "__main__":
    sys.exit(main())
