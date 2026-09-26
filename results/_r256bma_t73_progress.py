"""R256 bm-a: T-73 ticket progress_r256 append (four-face mirror writer).

Faces probed from HEAD blob: no BOM / LF-only / indent=1 /
ensure_ascii=False (r254/r255 laws). progress_* = per-round string keys.
"""
import io
import json
import subprocess

PATH = "fleet/tasks/T-2026-09-26-73-P1.json"
raw = subprocess.run(
    ["git", "show", "HEAD:" + PATH], capture_output=True).stdout
assert raw[:3] != b"\xef\xbb\xbf"
assert b"\r\n" not in raw
head_txt = raw.decode("utf-8")
lines = head_txt.split("\n")
assert len(lines[1]) - len(lines[1].lstrip()) == 1

j = json.loads(head_txt)
assert "progress_r256" not in j, "r256 already present"
j["progress_r256"] = (
    "R256 s3 slice-3 = CN-REGIME-POLICY-P1 prereg DRAFTED+FROZEN+PUSHED "
    "(commit 124b360c) + runner WRITTEN+SELFTESTED (18/18) + POOL "
    "SUBMITTED same round (supply-line duty answer to R255 "
    "pool_starvation flag: prereg->runner->pool compressed one round "
    "ahead of the R255-committed schedule). Design decision per "
    "s2-sliceB digest option-set: SCOPE-DOWN face (policy axis never an "
    "alpha slot; P4B={4,7,10,12} defensive risk-condition x0.5 only) -- "
    "interaction option rejected (expected-negative alpha burn = "
    "fabricated-busywork risk per O-1137), record-not-model rejected "
    "(CEO order s3 listed the model for full prereg->judgment; honest "
    "falsification batch = legitimate completion, two family negatives "
    "CN-REV-TILT/CN-DIV-LOWVOL-ROT precedent). Judged cells: "
    "v3_base/v3_policy/policy_only (3), nulls = 990 exhaustive "
    "C(12,4) month-set variants x2 families (zero RNG zero seeds), "
    "N=993 D1 bill. A-face = C2-vs-C1 policy-value 3-condition AND "
    "(full Sharpe + OOS Sharpe + maxDD), B-face = P4B 495-percentile "
    "one-sided p<=0.05, C-face = G1'v2/G2 admission (honest prior: "
    "0/3 pass, line~0.95). Reuse zero rebuild: regime axis = "
    "regime_deep_replay imported frozen layer, ladder = market_clock_"
    "call POSITION_LADDER T-74 L5 canon, costs = alloc_backtest "
    "side_cost_* single source, D6 = cn_rev_tilt_p1 loader. Probe "
    "facts frozen: results/cn_regime_policy_probe.json (510300 corpus "
    "3483 bars, v3 full-cover G1674/Y1238/R528/O43 268 flips, ADV20 "
    "min 300.66M CNY cap margin 3.8x). Exact resume point: pool entry "
    "CN-REGIME-POLICY-P1 ready 16:17:58 -- next = autofill launch -> "
    "landed marker -> r244-law deterministic harvest next round "
    "(gate re-derive + pool flip + prereg s7/s8 backfill + "
    "post_review row register per R246 law)"
)
with io.open(PATH, "w", encoding="utf-8", newline="\n") as fh:
    json.dump(j, fh, ensure_ascii=False, indent=1)
print("progress_r256 appended")
