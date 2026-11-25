# -*- coding: utf-8 -*-
"""Negative control for scripts/policy_trigger_audit.py (r2103, bm-c).

Every finding in that face must be able to *stop being a finding* when the
source it reads says something else.  A detector that always reports four
findings is a poster, not a check.  This harness copies each input to a temp
folder, poisons exactly one number, calls the real build() and asserts the
matching finding changed -- and that the other findings did not.

Run: python results/_r2103bmc_trigger_audit_negative.py
Exit 0 = all legs behave; 1 = the face is deaf to its own inputs.
"""
from __future__ import annotations

import io
import json
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import policy_trigger_audit as audit  # noqa: E402

LEGS = []


def ids(payload):
    return {f["id"] for f in payload.get("findings", [])}


def with_poison(files):
    """files: {global_name: transform(text)->text}. Returns build() payload."""
    tmp = tempfile.mkdtemp(prefix="pta_neg_", dir=os.path.join(ROOT, "results"))
    saved = {}
    try:
        for name, fn in files.items():
            src = getattr(audit, name)
            dst = os.path.join(tmp, os.path.basename(src))
            if src.endswith(".json"):
                data = json.load(io.open(src, "r", encoding="utf-8"))
                obj = fn(data)
                io.open(dst, "w", encoding="utf-8", newline="\n").write(
                    json.dumps(obj, ensure_ascii=False, indent=1))
            else:
                txt = io.open(src, "r", encoding="utf-8").read()
                io.open(dst, "w", encoding="utf-8", newline="\n").write(fn(txt))
            saved[name] = getattr(audit, name)
            setattr(audit, name, dst)
        return audit.build()
    finally:
        for name, path in saved.items():
            setattr(audit, name, path)
        shutil.rmtree(tmp, ignore_errors=True)


base = audit.build()
base_ids = ids(base)
base_vol_id = next(i for i in base_ids if i.startswith("VOL_TARGET_"))
LEGS.append(("baseline_reports_four", len(base_ids) == 4))

# 1. one vol number instead of three -> the vol finding must vanish
one_vol = with_poison({
    "DOC": lambda t: t.replace("组合波动目标 **9%**", "组合波动目标 **7%**")})
LEGS.append(("single_vol_silences_vol_finding",
             "VOL_TARGET_STATED_3_WAYS" not in ids(one_vol)
             and len(ids(one_vol)) == 3))
LEGS.append(("single_vol_keeps_the_rest", ids(one_vol) == base_ids - {
    base_vol_id}))

# 2. cap raised above the published targets -> notional finding must vanish
wide_cap = with_poison({
    "ENGINE": lambda t: t.replace("L2_NOTIONAL_CAP_X = 2.5", "L2_NOTIONAL_CAP_X = 5.0")})
LEGS.append(("wide_cap_silences_notional_finding",
             "NOTIONAL_CAP_NOT_APPLIED_TO_THE_SLEEVE" not in ids(wide_cap)))

# 3. ladder fed by the composite book -> mismeasure finding must vanish
book_fed = with_poison({
    "ENGINE": lambda t: t.replace(
        'paper_dd.get("worst_cumulative_carry_pct") or 0.0',
        'book_nav_drawdown() or 0.0')})
LEGS.append(("composite_feed_silences_drawdown_finding",
             "DRAWDOWN_LINE_MEASURED_ON_ONE_LEG" not in ids(book_fed)))

# 4. a quiet leg must price the placeholder lower, not identically
def quiet(data):
    for code in ("IC", "IM"):
        r = data["products"][code]["risk"]
        r["ann_vol_pct"] = 0.5      # 1/12 of the real vol
    return data

quiet_run = with_poison({"CARRY_RISK": quiet})
legs_quiet = {p["leg"]: p for p in quiet_run["carry_pause_pricing"]["legs"]}
LEGS.append(("quiet_leg_prices_a_smaller_trip_rate",
             all(legs_quiet[c]["trip_rate_at_line"] < 0.001 for c in ("IC", "IM"))))
# the line the document actually wrote (U+2212 minus) is the one being priced
LEGS.append(("written_line_is_priced_at_its_own_number",
             all(legs_quiet[c]["line_pp"] == -2.0 for c in ("IC", "IM"))))

# 5. moving the written line out to the recommended one must silence it.
#    The document writes the minus as U+2212, so a plain ASCII "-2pp" poison
#    would prove nothing (it would look like a missing line, not a moved one).
LOOSE_LINE = u"\u5355\u817f 60 \u65e5\u7d2f\u8ba1 carry < \u22124.5pp"
WRITTEN_LINE = u"\u5355\u817f 60 \u65e5\u7d2f\u8ba1 carry < \u22122pp"
filled = with_poison({"DOC": lambda t: t.replace(WRITTEN_LINE, LOOSE_LINE)})
LEGS.append(("looser_written_line_silences_finding",
             "CARRY_PAUSE_LINE_TOO_TIGHT" not in ids(filled)))

# 6. the arithmetic is checked by hand, not just against itself
LEGS.append(("ic_sigma_by_hand",
             abs(legs_quiet["IC"]["sigma_window_pp"] - round(0.5 * (60 / 252) ** 0.5, 3))
             < 1e-9))

ok = sum(1 for _, v in LEGS if v)
for name, v in LEGS:
    print("%-44s %s" % (name, "PASS" if v else "FAIL"))
print("%d/%d PASS" % (ok, len(LEGS)))
sys.exit(0 if ok == len(LEGS) else 1)
