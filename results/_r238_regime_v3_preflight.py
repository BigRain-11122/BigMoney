# r238 (bm-a): REGIME_GUARD v3 10-01 month-boundary activation preflight.
# READ-ONLY probe -- zero mutation of date gate / approval file / registered
# files (round-prompt law: do not manually alter date gate/approval/month boundary).
# Faces verified:
#   1. gate 1 approval file well-formed (calibration_pass + gm_approval)
#   2. live three-gate resolution accepts REAL files -> legal enforce context
#   3. pre-10-01 mask face on REAL v3 state series = zero behavior change
#   4. post-10-01 synthetic extension = response matrix auto-activates
#      (ffill step-function persistence + shift(1) decision causality)
import sys, json, io
sys.path.insert(0, ".")
import live.paper as P
import pandas as pd

out = {}

appr = json.load(open("results/regime_enforce_approved.json", encoding="utf-8-sig"))
out["gate1_approval"] = {
    "calibration_pass": bool(appr.get("calibration_pass")),
    "gm_approval": bool(appr.get("gm_approval")),
    "active_from_in_file": appr.get("active_from"),
}
ctx = P.regime_guard_context("enforce")
out["three_gate_resolution"] = {
    "mode": ctx.get("mode"), "approved": ctx.get("approved"),
    "active_from": ctx.get("active_from"),
}

st = P.v3_state_series()
out["v3_series"] = {
    "coverage": [str(st.index.min().date()), str(st.index.max().date())],
    "last_state": str(st.iloc[-1]),
}
panel_idx = pd.DatetimeIndex(sorted(set(st.index)))
m = P._enforce_mask(st, panel_idx)
out["pre_101_face"] = {
    "blocked_exec_days": m["blocked_exec_days"],
    "yellow_exec_days": m["yellow_exec_days"],
    "zero_behavior_change": m["blocked_exec_days"] == 0 and m["yellow_exec_days"] == 0,
}
future_dates = pd.date_range("2026-10-08", periods=5, freq="B")  # National Day post-holiday face
ext = panel_idx.append(future_dates)
m2 = P._enforce_mask(st, ext)
out["post_101_face"] = {
    "synthetic_days": 5, "from": "2026-10-08",
    "blocked_exec_days": m2["blocked_exec_days"],
    "yellow_exec_days": m2["yellow_exec_days"],
    "matrix_activates": m2["yellow_exec_days"] > 0 or m2["blocked_exec_days"] > 0,
}
out["verdict"] = "PASS" if (
    out["gate1_approval"]["calibration_pass"] and out["gate1_approval"]["gm_approval"]
    and out["three_gate_resolution"]["approved"]
    and out["pre_101_face"]["zero_behavior_change"]
    and out["post_101_face"]["matrix_activates"]
) else "FAIL"

with io.open("results/_r238_regime_v3_preflight.json", "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
print(json.dumps(out, ensure_ascii=False, indent=1))
