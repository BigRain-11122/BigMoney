# -*- coding: utf-8 -*-
"""r639 bm-a: G2 mine supply-line SLOT s0 family-selection probe.

Purpose: advance the queue-c continuation (G2_OVERLAP_CENSUS_P2 sec.8 next-slice
recommendation: per-family SLOT preregistration, priority suggestion
"old_/stock_ mainline families top-N first") by grouping the 126 NEW-FACE
berth candidates by family and emitting the selection facts the next prereg
drafting round needs.

Law anchors:
- O-20260930-1901 (a) ①: mine faces MUST go per-family preregistered burns;
  batch-all-judge burns FORBIDDEN. This probe selects nothing for burning --
  it is measurement/advisory only; prereg freeze is a separate round face.
- Deterministic, zero-network, read-only inputs (census artifacts only).
- Probe != prereg: no criteria, no thresholds, no seeds touched here.

Self-verification: `selftest` subcommand = structural asserts + double-run
byte-identity of the output artifact.
"""
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "results" / "g2_overlap_census_p2.json"
OUT = ROOT / "results" / "_r639bma_g2_slot_family_probe.json"

# frozen sec.8 next-slice priority suggestion (verbatim semantic anchor)
PRIORITY_MAINLINE = ["old", "stock"]

# operators/inputs recognized as daily-panel derivable (P2 disclosure:
# "+126 OHLCV+amount/vwap computable faces" -- census's own classification,
# re-verified structurally here, never widened)
PANEL_INPUTS = {
    "open", "close", "high", "low", "volume", "vol", "vwap", "amount",
    "ret", "ret_1", "price", "p", "c", "o", "h", "l", "v",
}

# known expression operators (call heads): ts_* prefix family + bare ops.
# anything else that is a bare identifier = a data field the daily panel
# cannot supply (e.g. eps/indneutralize = fundamental/industry face).
OPERATOR_HEADS = {
    "rank", "corr", "sign", "std", "mean", "sum", "delay", "min", "max",
    "abs", "delta", "log", "del", "ewma", "pow", "sqrt", "if", "and", "or",
    "not",
}


def _load():
    with open(SRC, encoding="utf-8") as f:
        return json.load(f)


def _panel_derivable(formula: str):
    """Structural check: every bare identifier is a known panel input or an
    operator/number. Bare identifiers outside the set -> not derivable from
    the daily panel alone (honest downgrade, e.g. needs fundamental data)."""
    if not formula:
        return False, ["<empty>"]
    s = re.sub(r"[()^*/+\-\s,]", " ", formula)
    toks = [t for t in s.split() if t and not re.fullmatch(r"-?\d+(\.\d+)?", t)]
    unknown = []
    for t in toks:
        if re.fullmatch(r"[A-Za-z_][A-Za-z_0-9]*", t) and t.lower() not in PANEL_INPUTS:
            # ts_* rolling-window operators and known call heads are operators,
            # not data fields
            if not (t.lower().startswith("ts_") or t.lower() in OPERATOR_HEADS):
                unknown.append(t)
    return (len(unknown) == 0), unknown


def probe():
    p2 = _load()
    rows = [r for r in p2["rows"] if r.get("verdict") == "NEW-FACE"]
    families = {}
    for r in rows:
        fam = r.get("subfamily") or "<none>"
        d = families.setdefault(fam, {"family": fam, "n_faces": 0,
                                      "panel_derivable": 0, "non_derivable": 0,
                                      "non_derivable_faces": [], "faces": []})
        d["n_faces"] += 1
        ok, unknown = _panel_derivable(r.get("doc_formula") or "")
        if ok:
            d["panel_derivable"] += 1
        else:
            d["non_derivable"] += 1
            d["non_derivable_faces"].append({"face": r["face"], "unknown": unknown[:4]})
        d["faces"].append(r["face"])
    fam_list = sorted(families.values(), key=lambda d: (-d["n_faces"], d["family"]))
    # priority per frozen suggestion: mainline families first, then by size
    def prio(d):
        main = d["family"] in PRIORITY_MAINLINE
        return (0 if main else 1, -d["n_faces"], d["family"])
    ranked = sorted(fam_list, key=prio)
    first = ranked[0]
    samples = [r for r in rows if (r.get("subfamily") == first["family"])][:3]
    out = {
        "artifact": "_r639bma_g2_slot_family_probe",
        "round": "r639 bm-a",
        "law_refs": [
            "research/G2_OVERLAP_CENSUS_P2.md sec.8 next-slice (per-family SLOT prereg)",
            "O-20260930-1901 (a)-(1): census-first, per-family burns, batch-all forbidden",
        ],
        "evidence_cutoff": p2.get("evidence_cutoff"),
        "cutoff_meta": (p2.get("science_gates") or {}).get("cutoff_meta"),
        "inputs": {"src": "results/g2_overlap_census_p2.json", "new_face_n": len(rows)},
        "families": [
            {"family": d["family"], "n_faces": d["n_faces"],
             "panel_derivable": d["panel_derivable"],
             "non_derivable": d["non_derivable"],
             "faces": d["faces"]}
            for d in fam_list
        ],
        "priority_table": [
            {"rank": i + 1, "family": d["family"], "n_faces": d["n_faces"],
             "mainline": d["family"] in PRIORITY_MAINLINE}
            for i, d in enumerate(ranked)
        ],
        "first_family_recommendation": {
            "family": first["family"],
            "n_faces": first["n_faces"],
            "panel_derivable": first["panel_derivable"],
            "sample_formulas": [
                {"face": s["face"], "doc_formula": s.get("doc_formula")} for s in samples
            ],
            "status": "advisory-only: selection facts for next-round prereg draft",
        },
        "next_round_s1_checklist": [
            "draft from research/PREREG_TEMPLATE.md with alpha mechanism section (D6 four-choice) -- volume-price divergence/momentum family reading from old_* formula patterns",
            "D6 same-family corr gate: enumerate registered same-mechanism families via science_gates registered face before freeze",
            "exit-axis explicit gate (TRIAL_LABOR_LAW sec.4 three-choice) mandatory",
            "judged criteria from science_gates.g1_prime_v2/g2_registration_v2 shared library -- no hand-copied thresholds",
            "meaningfulness three-verifications: falsifiable hypothesis + named consumer face + negative-verdict disposal plan",
            "seeds registration in SEED_REGISTRY at freeze commit (three-step law)",
            "consumer face: candidate-supply pool berth -> trial-labor wave grammar family (per RETAIL_QUANT_TRACK budget attribution)",
        ],
        "audit": {
            "deterministic": True,
            "network": "zero",
            "burn_authorization": "NONE -- probe is measurement/advisory; prereg freeze is a separate round face per O-1901",
        },
    }
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1, sort_keys=True)
    print("probe ok ->", OUT.name)
    print("families:", len(fam_list), "first:", first["family"], first["n_faces"])
    return 0


def selftest():
    p2 = _load()
    nf = [r for r in p2["rows"] if r.get("verdict") == "NEW-FACE"]
    assert len(nf) == 126, "NEW-FACE n mismatch vs frozen census: %d" % len(nf)
    probe()
    first = json.loads(OUT.read_text(encoding="utf-8"))
    fam_sum = sum(d["n_faces"] for d in first["families"])
    assert fam_sum == 126, "family sum mismatch: %d" % fam_sum
    old = [d for d in first["families"] if d["family"] == "old"]
    stock = [d for d in first["families"] if d["family"] == "stock"]
    assert old and old[0]["n_faces"] == 43, "old family count drift"
    assert stock and stock[0]["n_faces"] == 14, "stock family count drift"
    assert first["priority_table"][0]["family"] in PRIORITY_MAINLINE
    h1 = hashlib.sha256(OUT.read_bytes()).hexdigest()
    probe()
    h2 = hashlib.sha256(OUT.read_bytes()).hexdigest()
    assert h1 == h2, "double-run byte identity FAIL"
    # encoding law: file must round-trip as utf-8 (no GBK pollution)
    OUT.read_text(encoding="utf-8")
    print("selftest PASS (126/sum/old=43/stock=14/double-run byte-identical)")
    return 0


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "probe"
    sys.exit({"probe": probe, "selftest": selftest}[cmd]())
