# -*- coding: utf-8 -*-
"""r417 bm-b: face counts + A/B splits + stop-face survival probes for sec.7 reconciliation (read-only)."""
import json
import io
import os
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
R = r"E:\Fluxgroup\FluxGroup\quant\bigmoney\results"


def load(p):
    return json.load(io.open(os.path.join(R, p), encoding="utf-8"))


for n in (1, 2, 3, 4, 5):
    s = load(f"trial_labor_w{n}/w{n}_screen.json")
    surv = s.get("survivors", [])
    a = sum(1 for x in surv if f"-A-" in x)
    b = sum(1 for x in surv if f"-B-" in x)
    nd = s["n_distinct"]
    print(f"W{n}: survivors A={a} B={b} (total {len(surv)}); rate_by_distinct={len(surv)/nd:.4f}")
    for k in ("stop_face_counts", "gate_face_counts", "vol_face_counts", "yang_face_counts"):
        if k in s:
            print(f"    {k}: {json.dumps(s[k], ensure_ascii=False)[:200]}")
    # segmented survival faces (W3+: gate/vol/yang)
    for k in ("gate_segmented_survival", "vol_segmented_survival", "yang_segmented_survival"):
        if k in s:
            print(f"    {k}: {json.dumps(s[k], ensure_ascii=False)[:340]}")
    for k in ("gate_vol_interaction_survival", "gate_vol_yang_interaction_survival"):
        if k in s:
            print(f"    {k}: {json.dumps(s[k], ensure_ascii=False)[:340]}")
    # grammar sha
    print(f"    grammar_sha256: {str(s.get('grammar_sha256'))[:70]}")
    g = load(f"trial_labor_w{n}/w{n}_grammar.json")
    ax = g.get("axis_combos") or g.get("n_axis_combos")
    print(f"    grammar axis_combos: {ax}")
