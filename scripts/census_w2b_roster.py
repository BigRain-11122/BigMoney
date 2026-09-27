# -*- coding: utf-8 -*-
"""T-86 s2 wave-2 W2-B roster derivation (deterministic doc face, sec.9.4).

Sec.9.4 append-confirm freeze precedes the W2-B runner build (R99:
freeze -> build -> run). Zero-invention law: every field is derived from
in-repo frozen artifacts, nothing hand-copied:

  A32 cross-face identity : results/census_fusion_s2/w2_roster.json
                            w2a.faces (R325 frozen, consumed read-only)
  D8 signs                : results/shortline/sina_construct_p1.json rows
                            h10_is_ic_mean (R338 judged artifact) --
                            ratio faces read the TIER construct directly
                            (same formula, judged); net faces declare the
                            same-tier directional prior (normalized-sibling
                            derivation, size-tilt disclosed in prereg
                            sec.9.4; NOT directly judged)
  D8 formulas             : net = raw sina panel rX_net column (SINA_MF_PREREG
                            sec.1 frozen schema); ratio = rX_net/turnover =
                            SINA_CONSTRUCT_P1 sec.3 TIER_rX literal (judged
                            convention)
  E-heat                  : census-infeasible today (3 daily snapshots +
                            97/5228 pilot rank_history files) -> OUT of
                            W2-B per sec.9.4 downscope (zero cells burned);
                            future path recorded, potential W2-C sub-wave

Enumeration is verified exactly with itertools over the 40-face union
(pairs 284 + triples 4920 = candidates 5204; controls 8x2=16; nulls 400
forced >=1 D face; ledger N 5620). Deterministic, zero-network, zero-engine;
ledger +0 (doc face). Output: results/census_fusion_s2/w2b_roster.json

Usage: python scripts/census_w2b_roster.py run
"""
import hashlib
import itertools
import json
import os
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

from science_gates import SEED_REGISTRY  # noqa: E402  (R250 same-commit reg)

W2_ROSTER = os.path.join(ROOT, "results", "census_fusion_s2", "w2_roster.json")
SINA_P1 = os.path.join(ROOT, "results", "shortline", "sina_construct_p1.json")
SINA_SPEC = os.path.join(ROOT, "research", "shortline", "SINA_MF_PREREG.md")
HEAT_SPEC = os.path.join(ROOT, "research", "shortline", "HEAT_ATTENTION_SPEC.md")
SINA_STATUS = os.path.join(ROOT, "results", "sina_mf_update_status.json")
OUT = os.path.join(ROOT, "results", "census_fusion_s2", "w2b_roster.json")

SEED_W2B = SEED_REGISTRY["census_fusion_s2_w2b"]     # 20282500 (this commit)
N_NULLS = 400          # 200 random pairs + 200 random triples (wave parity)
BENCH_FACES = ["rs_20_csi300", "rs_60_csi300"]

# predeclared face names (w2_roster.json w2b section) -> judged TIER construct
TIER_MAP = [
    ("sina_mf_eltra_large", "TIER_r0"),
    ("sina_mf_large", "TIER_r1"),
    ("sina_mf_mid", "TIER_r2"),
    ("sina_mf_small", "TIER_r3"),
]


def _sha12(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        h.update(fh.read())
    return h.hexdigest()[:12]


def build():
    with open(W2_ROSTER, encoding="utf-8") as fh:
        w2r = json.load(fh)
    with open(SINA_P1, encoding="utf-8") as fh:
        sp1 = json.load(fh)
    with open(SINA_STATUS, encoding="utf-8") as fh:
        sstat = json.load(fh)

    a_faces = [f["face"] for f in w2r["w2a"]["faces"]]
    assert len(a_faces) == 32, f"w2a faces {len(a_faces)} != 32"

    # D8 signs derived from the judged artifact (fail-closed, no hand-copy)
    tier_ic = {r["factor"]: r["h10_is_ic_mean"] for r in sp1["rows"]}
    d_faces = []
    for base, tier in TIER_MAP:
        ic = tier_ic.get(tier)
        assert isinstance(ic, (int, float)) and ic != 0, f"{tier} IS IC missing/zero"
        sign = 1 if ic > 0 else -1
        d_faces.append({
            "face": f"{base}_net", "row": "D", "sign": sign,
            "sign_anchor": (f"sina_construct_p1.json {tier} h10_is_ic_mean "
                            f"{ic:+.4f} (same-tier normalized-sibling derived "
                            "prior; raw face size-tilt disclosed sec.9.4)"),
            "ctor": (f"sina panel raw column (SINA_MF_PREREG sec.1 frozen "
                     f"schema); daily cross-sectional z-score"),
        })
        d_faces.append({
            "face": f"{base}_ratio", "row": "D", "sign": sign,
            "sign_anchor": (f"sina_construct_p1.json {tier} h10_is_ic_mean "
                            f"{ic:+.4f} (judged direct: same TIER_rX formula)"),
            "ctor": (f"rX_net/turnover = SINA_CONSTRUCT_P1 sec.3 {tier} "
                     "literal formula (judged-artifact convention)"),
        })
    assert len(d_faces) == 8

    # exact enumeration over the 40-face union (itertools, not formulas)
    union = a_faces + [f["face"] for f in d_faces]
    dset = {f["face"] for f in d_faces}
    assert len(union) == 40 and len(set(union)) == 40
    pairs = [c for c in itertools.combinations(union, 2) if dset & set(c)]
    triples = [c for c in itertools.combinations(union, 3) if dset & set(c)]
    n_pair, n_trip = len(pairs), len(triples)
    n_cand = n_pair + n_trip
    n_ctrl = len(d_faces) * len(BENCH_FACES)
    n_ledger = n_cand + n_ctrl + N_NULLS
    assert n_pair == 284 and n_trip == 4920 and n_cand == 5204, \
        f"enum mismatch: {n_pair}/{n_trip}/{n_cand}"
    assert n_ledger == 5620, f"ledger N mismatch: {n_ledger}"

    panel = sstat.get("panel") or {}
    doc = {
        "batch": "CENSUS_FUS_S2_W2B-ROSTER",
        "ticket": "T-2026-09-26-86-P1 s2 wave-2 W2-B (CEO O-20260926-2320)",
        "face": ("EXPLORATION roster freeze doc (sec.9.4 append-confirm; "
                 "deterministic derivation from judged/archived artifacts; "
                 "zero judgment claims; R99 freeze precedes W2-B runner "
                 "build/run)"),
        "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "rules_ref": ("research/CENSUS_FUSION_S2_PREREG.md sec.9.4 (this "
                      "freeze) + sec.9.3 wave-2 instantiation + "
                      "FACTOR_CENSUS_REGISTRY.md sec.s2 wave-2 rules"),
        "artifact_anchors": {
            "w2_roster.json": {"sha256_12": _sha12(W2_ROSTER),
                               "note": "A32 cross-face identity (R325 frozen)"},
            "sina_construct_p1.json": {"sha256_12": _sha12(SINA_P1),
                                       "note": "D8 sign evidence (R338 judged)"},
            "SINA_MF_PREREG.md": {"sha256_12": _sha12(SINA_SPEC)},
            "HEAT_ATTENTION_SPEC.md": {"sha256_12": _sha12(HEAT_SPEC)},
        },
        "gates": {
            "sina_mf_panel": {"state": "OPEN",
                              "complete": bool(panel.get("complete")),
                              "cutoff": panel.get("cutoff"),
                              "n_symbols": panel.get("n_symbols"),
                              "universe_n": panel.get("universe_n"),
                              "source": "results/sina_mf_update_status.json"},
            "e_heat": {"state": "CENSUS-INFEASIBLE -> OUT (sec.9.4 downscope)",
                       "evidence": ("popularity snapshots 3 (2026-09-23/24/25) + "
                                    "rank_history pilot 97/5228 members; "
                                    "HEAT_ATTENTION_SPEC sec.3.2 P-C no-IS law"),
                       "future_path": ("paper-forward accumulation continues; "
                                       "full-universe rank_history backfill "
                                       "amendment option -> potential W2-C")},
        },
        "w2b": {
            "lane": "bm-b (astock panel + A sidecars locality; D-face input "
                    "via bm-a small-artifact export + TRANSFER channel, sha "
                    "gate in-runner fail-closed)",
            "n_faces": 8,
            "faces": d_faces,
            "enumeration": {"pairs": n_pair, "triples": n_trip,
                            "candidates": n_cand, "controls_rs_pairs": n_ctrl,
                            "nulls": N_NULLS, "ledger_N": n_ledger},
            "nulls_design": ("200 random pairs + 200 random triples, each "
                              "forced >=1 D face (same-structure "
                              "same-coverage-window baseline; divergence from "
                              "W2-A unconditional draw disclosed sec.9.4); "
                              "random +/- sign assignment; same-mask "
                              "same-machine same-cost (RANDOM_LARGE_SAMPLE_LAW)"),
            "seeds": {"null_base": SEED_W2B,
                      "null_band": f"{SEED_W2B}..{SEED_W2B + N_NULLS - 1}"},
            "coverage_window_disclosure": (
                "sina panel = num=100 frozen collector ~250 rows/symbol "
                "(~2025-09..2026-09-24; sina_construct_p1 same window IS156+"
                "OOS81=237 signal days) -> D-combo stats run on the D-covered "
                "window (~1y, weekly REB ~47) vs W2-A full-window; deep-history "
                "re-pull (num=2500) = future amendment option (SINA_MF_PREREG "
                "sec.5-1)"),
            "honest_notes": [
                "sec.9.3 predeclare 9 faces / 6024 combos superseded by this "
                "sec.9.4 confirm (E-heat out, structural data availability, "
                "zero cells burned, non-result-driven)",
                "D-family standalone REJECT (R338 V1/V2) + OOS IC negative "
                "disclosed with the batch -- exploration face, no admission "
                "gate, T-23 intake consumers carry their own gates",
                "intra-D corr pre-evidence from judged census: TIER_r0|TIER_r1 "
                "0.4877, TIER_r0|MAIN 0.8636 (family_by_construction)",
            ],
        },
        "ledger_trials_added": 0,
        "note": ("doc face (roster freeze); W2-B runner build + bm-a sina "
                 "export artifact + pool entry = follow-up slices; batch N "
                 f"enters the ledger at run finalize (declared ledger_N="
                 f"{n_ledger})"),
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    s = json.dumps(doc, ensure_ascii=False, indent=1)
    json.loads(s)
    with open(OUT, "w", encoding="utf-8") as fh:
        fh.write(s)
    print(json.dumps({"ok": True, "out": OUT, "d_faces": len(d_faces),
                      "pairs": n_pair, "triples": n_trip,
                      "candidates": n_cand, "ledger_N": n_ledger,
                      "seed": SEED_W2B}, ensure_ascii=False))
    return 0


def main():
    if len(sys.argv) < 2 or sys.argv[1] != "run":
        print("usage: python scripts/census_w2b_roster.py run")
        return 2
    return build()


if __name__ == "__main__":
    sys.exit(main())
