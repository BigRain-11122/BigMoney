"""r483 bm-c: MASS_TRIAL_W3 attrition row append (prereg sec.7 deliverable).
r678 law: verify json roundtrip identity FIRST; fail -> abort to line
surgery (never blind load-dump rewrite of a shared face)."""
import datetime
import json
import sys

PATH = "results/gate_attrition.json"
NOW = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

raw = open(PATH, "rb").read()
text = raw.decode("utf-8")
d = json.loads(text)

# roundtrip identity probe (interior CRLF conversion included)
found = None
for indent in (1, 2, None):
    cand = json.dumps(d, ensure_ascii=False, indent=indent)
    variants = [cand, cand.replace("\n", "\r\n"),
                cand.replace("\n", "\r\n") + "\r\n", cand + "\n"]
    for v in variants:
        if v.encode("utf-8") == raw:
            found = (indent, v)
            break
    if found:
        break
if found is None:
    print("ABORT: no roundtrip identity -- line surgery required")
    sys.exit(2)
indent, template = found
print("roundtrip identity: indent=%s exact" % (indent,))
assert not any(r.get("batch") == "MASS_TRIAL_W3" for r in d["entries"]), \
    "W3 row already present"

row = {
    "batch": "MASS_TRIAL_W3",
    "ts": NOW,
    "kind": "measurement",
    "cells_ledger_delta": 4814,
    "ledger_total_after": 646799,
    "gates": {
        "screen_pass": {
            "n_candidates": 4814, "n_survivors": 785,
            "line": "beat_rate_6m>=0.60 AND trades>=30 AND dd>=-0.35"},
        "null_face": {
            "p50": 0.45, "p95": 0.5333, "n": 20,
            "note": ("null p95 0.5333 < 0.60 line, margin thin (0.067); "
                     "third wave same thin margin as w1 0.533/w2 0.5333 "
                     "disclosed")},
        "dedup_face": {
            "param_dupes": 417, "signal_dupes": 734, "rejections": 9,
            "dead_signal": 227, "cross_wave_param_dupes": 916,
            "cross_wave_signal_dupes": 358,
            "cross_wave_note": (
                "1274 cross-wave collapses vs prereg band 150-600 "
                "(center ~300): enum/discrete collision scaling with dedup "
                "base 5811 (rate 21.9% vs w2 28.6% base-growth-consistent); "
                ">600 -> mechanism review disclosed at generate r480 + "
                "prereg sec.8 this batch; finalize-time keep-first id "
                "dedup 1227 rows elapsed_s-only-diff per r482 law "
                "(evidence results/_r483bmc_ckpt_dedup.json)")},
        "control_face": {
            "n_defaults": 75, "n_pass": 5, "n_signal_error": 2,
            "passed": ["volatility.low_vol_long",
                       "patterns.island_reversal",
                       "patterns.morning_star", "folk.ants_climb",
                       "patterns.vol_drought_reversal"],
            "note": ("same 5/75 pass set as w2 (identical list); "
                     "2 errors = month-required-arg defaults rows "
                     "(w1/w2 same)")}
    },
    "refs": {
        "prereg": "research/MASS_TRIAL_W3_PREREG.md (FROZEN r480 c2141d6c1)",
        "summary": ("results/mass_trial/w3_screen_summary.json "
                    "(complete=true, ledger 646799)"),
        "checkpoint": ("results/mass_trial/w3_screen_checkpoint.jsonl "
                       "(4909 unique rows post r482-law dedup)"),
        "dedup_evidence": "results/_r483bmc_ckpt_dedup.json",
        "generate": "results/mass_trial/w3_generate_summary.json"},
    "note": ("T-158 wave-3 stage-1 screen finalize r483 bm-c: survival "
             "16.31% (w1 17.0% w2 16.67%); R-bear 36.3% vs none 8.6% = "
             "4.22x (band 2-4x, ~4x stable third wave, marginally above "
             "band disclosed); family direction HIT 3rd consecutive wave "
             "(seasonal 28.1% event 23.1% patterns 20.0% vs trend 6.7% "
             "momentum 7.3%); pool double-flip same-window per r668 "
             "(SHARD-3 flip-authority bm-c, burn bm-a, verified "
             "4814/4814 zero-dup)"),
    "eliminated": 4029,
}
d["entries"].append(row)
new_text = json.dumps(d, ensure_ascii=False, indent=indent)
if "\r\n" in template:
    new_text = new_text.replace("\n", "\r\n")
if template.endswith("\r\n"):
    new_text += "\r\n"
elif template.endswith("\n"):
    new_text += "\n"
json.loads(new_text)  # reparse gate
with open(PATH, "wb") as fh:
    fh.write(new_text.encode("utf-8"))
d2 = json.loads(open(PATH, "rb").read().decode("utf-8"))
assert any(r.get("batch") == "MASS_TRIAL_W3" for r in d2["entries"])
print("APPEND_OK entries=%d ts=%s" % (len(d2["entries"]), NOW))
