# -*- coding: utf-8 -*-
"""T-86 s2 wave-2 WIDE-UNIVERSE roster derivation (deterministic doc face).

Precedes the wave-2 runner build (R99: freeze -> build -> run). Single-source
anchors (zero-invention law, research/FACTOR_CENSUS_REGISTRY.md sec.s2
wave-2 rules frozen R286):

  B4  zoo faces      : scripts/p1e_factors.py frozen r218 constructors,
                       sign prior '-' x4 (P1E_ZOO_BEHAVIOR_IC.md sec.5 frozen
                       prediction: four main prototype faces all-negative)
  C30 GTJA191/WQ101  : top-10 each by |h5_full_ir| from the archived stock
                       screening product research/shortline/
                       p1c_stock_ic_results.csv (P-1/P-2 line stock face,
                       artifact anchor; sign = sign of archived h5_full_ic)
  C   A158-truegap   : archived cells only 7 < 10 -> all 7 honest
                       (a158_truegap_ic_cells.csv, same sign rule)
  E2  LHB            : lhb_count_20 sign '-' (PA_LHB_IC.md IS IC -0.0642/
                       IR -0.84 project-strongest evidence; P-A literal
                       construction, Money02/data/lhb/lhb_detail.parquet)
  D8 + E-heat        : W2-B gated sub-wave (sina MF panel incomplete 2775/
                       5222 on bm-a; heat data bm-a-local) -> pre-declared
                       roster only, fires after data gates + sec.9.4 confirm

W2-A lane = bm-b (astock wide panel data locality, T-87 collector lane).
Deterministic, zero-network, zero-engine; ledger +0 (doc face, t33/aggregation
precedent). Output: results/census_fusion_s2/w2_roster.json

Usage: python scripts/census_w2_roster.py run
"""
import csv
import hashlib
import json
import math
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "results", "census_fusion_s2", "w2_roster.json")
T22 = os.path.join(ROOT, "research", "shortline")

P1C_CSV = os.path.join(T22, "p1c_stock_ic_results.csv")
A158_CSV = os.path.join(T22, "a158_truegap_ic_cells.csv")

# B-row zoo faces (registry B row, frozen r218 constructor anchors)
ZOO_FACES = [
    {"face": "zoo85_stv", "ctor": "scripts/p1e_factors.py build_zoo85_stv",
     "sign": -1, "sign_anchor": "P1E_ZOO_BEHAVIOR_IC.md sec.5 L68 all-negative"},
    {"face": "zoo85_terrified", "ctor": "scripts/p1e_factors.py build_zoo85_terrified",
     "sign": -1, "sign_anchor": "P1E_ZOO_BEHAVIOR_IC.md sec.5 L68 all-negative"},
    {"face": "zoo92_coin_team", "ctor": "scripts/p1e_factors.py build_zoo92_coin_team",
     "sign": -1, "sign_anchor": "P1E_ZOO_BEHAVIOR_IC.md sec.5 L68 all-negative"},
    {"face": "zoo93_arc", "ctor": "scripts/p1e_factors.py build_zoo93_arc_family",
     "sign": -1, "sign_anchor": "P1E_ZOO_BEHAVIOR_IC.md sec.5 L68 all-negative"},
]

# E-row LHB face (P-A literal line; heat face -> W2-B, bm-a-local data)
LHB_FACE = {
    "face": "lhb_count_20",
    "ctor": "scripts/pa_lhb_ic.py rank_rows (P-A literal; Money02/data/lhb/"
            "lhb_detail.parquet, dedup max-amount row, shift1)",
    "sign": -1,
    "sign_anchor": "PA_LHB_IC.md IS IC -0.0642 / IR -0.84 (h10 reversal)",
}

N_NULLS = 400          # 200 random pairs + 200 random triples (wave-1 parity)
SEED_W2 = 20281500     # census_fusion_s2_w2 null base (registered same commit;
                       # band 20281500..20281899 sits above cn_mkneutral_p1
                       # band top 20281300 = collision-free; rg scan zero hits)
SEED_W2_UNC = 20282000  # census_fusion_s2_w2_unc (derivation [seed, i] law,
                        # no band occupation, wave-1 census_fusion_s2_unc
                        # precedent; same-commit registration)


def _sha12(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        h.update(fh.read())
    return h.hexdigest()[:12]


def _f(x):
    try:
        v = float(x)
    except (TypeError, ValueError):
        return None
    return v if (v == v and abs(v) != math.inf) else None


def _top_by_abs_ir(rows, n, prefix=None, custom=None):
    ok = [r for r in rows if r.get("status") == "ok"
          and _f(r.get("h5_full_ir")) is not None
          and (custom(r) if custom else (r["factor"].startswith(prefix) if prefix else True))]
    ranked = sorted(ok, key=lambda r: -abs(_f(r["h5_full_ir"])))
    out = []
    for r in ranked[:n]:
        ic = _f(r.get("h5_full_ic"))
        out.append({
            "face": r["factor"],
            "arch_h5_full_ic": ic, "arch_h5_full_ir": _f(r["h5_full_ir"]),
            "sign": (1 if (ic or 0) >= 0 else -1),
            "sign_anchor": "sign(archived h5_full_ic) artifact rule",
            "ctor": "GTJA191/WQ101 expression family (p1c stock-face machinery)",
        })
    # stable deterministic order: by -|ir| then name
    out.sort(key=lambda d: (-abs(d["arch_h5_full_ir"]), d["face"]))
    return out


def build():
    with open(P1C_CSV, encoding="utf-8-sig") as fh:
        p1c = list(csv.DictReader(fh))
    with open(A158_CSV, encoding="utf-8-sig") as fh:
        a158 = list(csv.DictReader(fh))

    gtja = _top_by_abs_ir(p1c, 10, prefix="alpha191_")
    wq = _top_by_abs_ir(p1c, 10, custom=lambda r: r["factor"].startswith("wq101_alpha"))
    a158f = _top_by_abs_ir(a158, 10)          # all 7 archived cells (honest <10)

    w2a = ([dict(f, row="B") for f in ZOO_FACES]
           + [dict(f, row="C-gtja191") for f in gtja]
           + [dict(f, row="C-wq101") for f in wq]
           + [dict(f, row="C-a158") for f in a158f]
           + [dict(LHB_FACE, row="E-lhb")])
    n = len(w2a)
    n_pair = n * (n - 1) // 2
    n_trip = n * (n - 1) * (n - 2) // 6
    n_ctrl = 2 * n                            # x rs_20_csi300 + rs_60_csi300
    n_cand = n_pair + n_trip
    n_ledger = n_cand + n_ctrl + N_NULLS

    # W2-B pre-declared gated faces (roster only; run gate + sec.9.4 confirm)
    w2b = [
        {"face": "sina_mf_eltra_large_net", "row": "D", "sign": "gate-open declare",
         "anchor": "research/shortline/SINA_MF_PREREG.md (超大单净额)"},
        {"face": "sina_mf_large_net", "row": "D", "sign": "gate-open declare",
         "anchor": "SINA_MF_PREREG.md (大单净额)"},
        {"face": "sina_mf_mid_net", "row": "D", "sign": "gate-open declare",
         "anchor": "SINA_MF_PREREG.md (中单净额)"},
        {"face": "sina_mf_small_net", "row": "D", "sign": "gate-open declare",
         "anchor": "SINA_MF_PREREG.md (小单净额)"},
        {"face": "sina_mf_eltra_large_ratio", "row": "D", "sign": "gate-open declare",
         "anchor": "SINA_MF_PREREG.md (超大单占比)"},
        {"face": "sina_mf_large_ratio", "row": "D", "sign": "gate-open declare",
         "anchor": "SINA_MF_PREREG.md (大单占比)"},
        {"face": "sina_mf_mid_ratio", "row": "D", "sign": "gate-open declare",
         "anchor": "SINA_MF_PREREG.md (中单占比)"},
        {"face": "sina_mf_small_ratio", "row": "D", "sign": "gate-open declare",
         "anchor": "SINA_MF_PREREG.md (小单占比)"},
        {"face": "heat_attention", "row": "E", "sign": "gate-open declare",
         "anchor": "research/shortline/HEAT_ATTENTION_SPEC.md (人气榜面·bm-a-local data)"},
    ]
    nt = n + len(w2b)
    n_pair_t = nt * (nt - 1) // 2
    n_trip_t = nt * (nt - 1) * (nt - 2) // 6
    w2b_cross = (n_pair_t + n_trip_t) - n_cand

    doc = {
        "batch": "CENSUS_FUS_S2_W2-ROSTER",
        "ticket": "T-2026-09-26-86-P1 s2 wave-2 (CEO O-20260926-2320)",
        "face": ("EXPLORATION roster freeze doc (deterministic derivation from "
                 "archived artifacts; zero judgment claims; R99 freeze precedes "
                 "wave-2 runner build/run)"),
        "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "rules_ref": ("research/FACTOR_CENSUS_REGISTRY.md sec.s2 wave-2 rules "
                      "(frozen R286) + CENSUS_FUSION_S2_PREREG.md sec.2.2"),
        "artifact_anchors": {
            "p1c_stock_ic_results.csv": {"sha256_12": _sha12(P1C_CSV), "rows": len(p1c)},
            "a158_truegap_ic_cells.csv": {"sha256_12": _sha12(A158_CSV), "rows": len(a158)},
        },
        "universe": {
            "panel": "data/astock_daily/per/*.csv qfq (T-87 bm-b collector, "
                     "bm-b-local gitignored)",
            "panel_state": "complete=true, cutoff=2026-09-24, universe_n=5228, "
                           "per_files=5217 (results/astock_daily_update_status.json)",
            "mask": "data/fundamental/b_layer_mask.csv (B-layer filter law)",
            "evidence_cutoff": "2026-09-24",
        },
        "w2a": {
            "lane": "bm-b (panel data locality; pool entry lane_owner=bm-b)",
            "n_faces": n,
            "faces": w2a,
            "counts": {"B_zoo": len(ZOO_FACES), "C_gtja191": len(gtja),
                       "C_wq101": len(wq), "C_a158_truegap": len(a158f),
                       "E_lhb": 1},
            "enumeration": {"pairs": n_pair, "triples": n_trip, "candidates": n_cand,
                            "controls_rs_pairs": n_ctrl, "nulls": N_NULLS,
                            "ledger_N": n_ledger},
            "seeds": {"null_base": SEED_W2, "null_band": f"{SEED_W2}..{SEED_W2 + N_NULLS - 1}",
                      "unc": SEED_W2_UNC,
                      "unc_derive": "np.random.default_rng([census_fusion_s2_w2_unc, i])"},
            "honest_notes": [
                "A158-truegap archived cells = 7 < top-10 rule -> all 7 taken (honest undercount)",
                "GTJA191/WQ101 ranking anchored to the archived STOCK face (p1c csv) = "
                "wide-universe aligned; ETF-face csvs disclosed as lineage, not the rank key",
                "D6 not an admission gate (exploration face); zoo x LHB neighbor-corr "
                "pre-evidence r228 bm-b max|corr| 0.4829 < 0.7 disclosed",
            ],
        },
        "w2b": {
            "state": "GATED (roster pre-declared; runs only after gates open + "
                     "sec.9.4 append-confirm per R99)",
            "gates": ["sina MF panel complete (bm-a lane; 2775/5222 at freeze time)",
                      "heat data locality resolution (bm-a-local; TRANSFER channel "
                      "or small-artifact export decision)"],
            "n_faces": len(w2b),
            "faces": w2b,
            "cross_candidate_math": {"total_faces": nt, "total_candidates": n_pair_t + n_trip_t,
                                     "w2a_candidates": n_cand,
                                     "w2b_cross_and_internal": w2b_cross},
        },
        "ledger_trials_added": 0,
        "note": "doc face (roster freeze); wave-2 runner build + pool entry = "
                "follow-up slice; batch N enters the ledger at run finalize "
                f"(declared ledger_N={n_ledger} for W2-A)",
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    s = json.dumps(doc, ensure_ascii=False, indent=1)
    json.loads(s)
    with open(OUT, "w", encoding="utf-8") as fh:
        fh.write(s)
    print(json.dumps({"ok": True, "out": OUT, "w2a_faces": n,
                      "w2a_candidates": n_cand, "w2a_ledger_N": n_ledger,
                      "w2b_faces": len(w2b), "w2b_cross": w2b_cross},
                     ensure_ascii=False))
    return 0


def main():
    if len(sys.argv) < 2 or sys.argv[1] != "run":
        print("usage: python scripts/census_w2_roster.py run")
        return 2
    return build()


if __name__ == "__main__":
    sys.exit(main())
