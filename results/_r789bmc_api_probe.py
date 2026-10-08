# -*- coding: utf-8 -*-
"""r789 bm-c W17 runner-build API facts probe (hermetic, read-only).
Verifies seed registry keys, axis domain sizes, W16 same-face cell facts,
finalize-math signature, reform constants -- all consumed by the W17 runner."""
import sys, os, json, collections
_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_root, "scripts"))
sys.path.insert(0, _root)
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import science_gates as sg
import trial_labor_w1 as tl1
import trial_labor_w2 as tl2
import trial_labor_w16 as tl16

out = {}
out["seed_keys"] = {k: sg.SEED_REGISTRY[k] for k in sg.SEED_REGISTRY
                    if "w17" in k}
out["has_ceiling"] = hasattr(sg, "REFORM_CEILING_BASELINE")
out["ceiling"] = getattr(sg, "REFORM_CEILING_BASELINE", None)
out["freeze_integrity_rc"] = bool(sg.reform_weight_freeze_integrity())
axd = {"filter": len(tl1.AXIS_FILTERS), "exits": len(tl1.AXIS_EXITS),
       "sizing": len(tl1.AXIS_SIZING), "timing": len(tl1.AXIS_TIMING),
       "stop": len(tl2.AXIS_STOP), "gate": len(tl16.tl3.AXIS_GATE),
       "vol": len(tl16.tl4.AXIS_VOL), "yang": len(tl16.tl5.AXIS_YANG),
       "vconf": len(tl16.tl6.AXIS_VCONF), "streak": len(tl16.tl7.AXIS_STREAK),
       "tstate": len(tl16.tl8.AXIS_TSTATE), "amp": len(tl16.tl9.AXIS_AMP),
       "mom": len(tl16.AXIS_MOM), "std": len(tl16.AXIS_STD),
       "rsqr": len(tl16.AXIS_RSQR), "sumn": len(tl16.AXIS_SUMN),
       "resi": len(tl16.AXIS_RESI), "cnt": len(tl16.AXIS_CNT),
       "max": len(tl16.AXIS_MAX), "rank": len(tl16.AXIS_RANK)}
out["axis_domains"] = axd
cands = json.load(open(os.path.join(_root,
    "results", "trial_labor_w16", "w16_candidates.json"),
    encoding="utf-8"))["candidates"]
same_face = [c for c in cands if c["axis"][1] == "template_default"]
out["same_face_n"] = len(same_face)
out["same_face_family"] = dict(collections.Counter(
    c["family"] for c in same_face))
out["same_face_ids_sample"] = [c["candidate_id"] for c in same_face[:5]]
out["a_family_x"] = dict(collections.Counter(
    c["axis"][1] for c in cands if c["family"] == "A"))
import inspect
out["finalize_math_sig"] = str(inspect.signature(tl2._finalize_math))
out["descriptive_sig"] = str(inspect.signature(tl2._descriptive_face))
out["passive_rel_sig"] = str(inspect.signature(tl1.passive_rel))
out["windows"] = {k: v for k, v in tl1.WINDOWS.items()}
out["census_L"] = tl1.FROZEN_CENSUS["L"]
out["ledger_w16_row_sha16"] = None
led = os.path.join(_root, "results", "TRIAL_GRAMMAR_LEDGER.md")
if os.path.exists(led):
    for ln in open(led, encoding="utf-8"):
        if ln.startswith("| TRIAL_LABOR_W16 ") or ln.startswith("| TRIAL_LABOR_W14 "):
            out.setdefault("ledger_rows", []).append(ln[:120])
print(json.dumps(out, indent=1, ensure_ascii=False, default=str))
