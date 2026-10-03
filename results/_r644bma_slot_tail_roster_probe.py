# -*- coding: utf-8 -*-
"""r644 bm-a: G2-SLOT-TAIL-P1 roster + vendor smoke probe (facts artifact for
prereg freeze). Mirrors results/_r642bma_slot_stock_roster_probe.py (stock
family) for the merged-tail design: the six remaining non-mainline vendor
families (add_/better_/best_/extra_/original_/change_) in ONE stage-1 census
batch, per r643 next-round berth decision (meaning-gate: two consecutive
mainline family negatives old 0/41 + stock 0/14 died at the identical x2
translation layer; merged-tail asks each remaining family's IC-enrichment
question exactly once in one cheap batch, per-family verdicts derivable).

Zero network, zero judgment, deterministic. Legs:
 1. vendor engine import (ml-quant-trading pinned install a770825) + LEGACY_REGISTRY
    enumeration of the 6 tail prefixes
 2. roster cross-check: r639 probe families (ranks 3-8) vs census P2 NEW-FACE rows vs vendor registry
 3. per-face daily-panel derivability re-derive (r639 probe: 54/69 derivable)
 4. vendor anchors: repo HEAD, file sha256s
 5. core48 panel facts: 48 in-service members, rows, dates, columns, cutoff truncation, vwap derivability
 6. synthetic Panel smoke: all vendor tail faces run on torch CPU panel, shape/mask/finiteness
Output: results/_r644bma_slot_tail_roster_probe.json
"""
import hashlib
import json
import os
import re
import subprocess
import sys

import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VENDOR_SRC = r"C:\Users\sjs20\Desktop\FluxGroup\quant\toolstack\repos\ml-quant-trading\src"
VENDOR_REPO = r"C:\Users\sjs20\Desktop\FluxGroup\quant\toolstack\repos\ml-quant-trading"
ANCHOR_HEAD = "a770825f841504e41581f057b4d94160e6a50c2e"
CUTOFF = "2026-09-22"
TAIL_PREFIXES = ("add_", "better_", "best_", "extra_", "original_", "change_")

PANEL_INPUTS = {
    "open", "close", "high", "low", "volume", "vol", "vwap", "amount",
    "returns", "ret", "adv20", "cap",
}
OPS = {
    "rank", "corr", "ts_min", "ts_max", "ts_mean", "ts_sum", "ts_std",
    "ts_rank", "ts_corr", "delta", "delay", "ewma", "sign", "abs",
    "min", "max", "sum", "std", "mean", "log", "sqrt", "signedpower",
}


def _unknown_identifiers(formula: str):
    toks = re.findall(r"[A-Za-z_][A-Za-z_0-9]*", formula or "")
    unknown = []
    for t in toks:
        if t.lower() in PANEL_INPUTS or t in OPS or t.lower() in OPS:
            continue
        if re.fullmatch(r"\d+", t):
            continue
        if t not in unknown:
            unknown.append(t)
    return unknown


def main():
    out = {
        "artifact": "_r644bma_slot_tail_roster_probe",
        "audit": {"network": "zero", "deterministic": True, "judgment": "none (facts probe)"},
        "design": "merged-tail: 6 remaining non-mainline families, one stage-1 census batch",
        "legs": {},
    }
    fails = []

    # ---- leg 1: vendor import + registry ----
    sys.path.insert(0, VENDOR_SRC)
    import torch  # noqa: E402
    import mlquant.features._factors_add  # noqa: F401,E402  (decorator registration side-effect)
    import mlquant.features._factors_better  # noqa: F401,E402
    import mlquant.features._factors_best  # noqa: F401,E402
    import mlquant.features._factors_extra  # noqa: F401,E402
    import mlquant.features._factors_original  # noqa: F401,E402
    import mlquant.features._factors_change  # noqa: F401,E402
    from mlquant.features.legacy_factors import LEGACY_REGISTRY  # noqa: E402
    vendor_tail = sorted(k for k in LEGACY_REGISTRY if k.startswith(TAIL_PREFIXES))
    out["legs"]["vendor_registry"] = {
        "n_tail_faces": len(vendor_tail),
        "faces": vendor_tail,
    }
    if len(vendor_tail) != 126:
        fails.append(f"vendor tail faces {len(vendor_tail)} != 126 (install drift)")

    # ---- leg 2: roster cross-check ----
    census = json.load(open(os.path.join(ROOT, "results", "g2_overlap_census_p2.json"), encoding="utf-8"))
    tail_rows = {r["face"]: r for r in census["rows"] if r.get("face", "").startswith(TAIL_PREFIXES)}
    probe = json.load(open(os.path.join(ROOT, "results", "_r639bma_g2_slot_family_probe.json"), encoding="utf-8"))
    fams = [f for f in probe["families"] if f["family"] in
            ("add", "better", "best", "extra", "original", "change")]
    probe_faces = sorted(set().union(*[set(f["faces"]) for f in fams]))
    in_vendor = [f for f in probe_faces if f in vendor_tail]
    in_census_newface = [f for f in probe_faces if tail_rows.get(f, {}).get("verdict") == "NEW-FACE"]
    excluded = sorted(set(tail_rows) - set(probe_faces))
    excluded_status = {f: tail_rows[f].get("verdict") for f in excluded}
    fam_detail = {f["family"]: {"n": len(f["faces"]),
                                "in_vendor": len([x for x in f["faces"] if x in vendor_tail]),
                                "in_census_newface": len([x for x in f["faces"] if tail_rows.get(x, {}).get("verdict") == "NEW-FACE"])}
                  for f in fams}
    out["legs"]["roster_crosscheck"] = {
        "probe_tail_n": len(probe_faces),
        "probe_in_vendor": len(in_vendor),
        "probe_in_census_newface": len(in_census_newface),
        "excluded_from_families": excluded_status,
        "per_family": fam_detail,
    }
    if len(in_vendor) != 69:
        fails.append(f"probe tail vendor membership {len(in_vendor)} != 69")
    if len(in_census_newface) != 69:
        fails.append(f"probe tail NEW-FACE status {len(in_census_newface)} != 69")
    if set(probe_faces) - set(vendor_tail):
        fails.append("probe tail faces missing from vendor registry")
    if len(excluded) != 57:
        fails.append(f"tail faces excluded from family probe {len(excluded)} != 57 (56 UNVERIFIABLE + 1 DUP expected)")

    # ---- leg 2b: vendor function body cache (ground-truth adjudication base) ----
    import mlquant.features.legacy_factors as _lf  # noqa: E402
    _lf_path = os.path.dirname(_lf.__file__)
    vendor_body_cache = {}
    for f in probe_faces + ["old_047", "old_067"]:
        m = re.search(r'@register_legacy_factor\("' + re.escape(f) + r'"\).*?\n(?=@|\Z)',
                      open(os.path.join(_lf_path, "legacy_factors.py"), encoding="utf-8").read(), re.S)
        if m is None:
            for fname in os.listdir(_lf_path):
                if not fname.endswith(".py"):
                    continue
                m = re.search(r'@register_legacy_factor\("' + re.escape(f) + r'"\).*?\n(?=@|\Z)',
                              open(os.path.join(_lf_path, fname), encoding="utf-8").read(), re.S)
                if m is not None:
                    break
        if m is None:
            fails.append(f"vendor body not found for {f}")
            vendor_body_cache[f] = ""
        else:
            vendor_body_cache[f] = m.group(0)

    # ---- leg 3: per-face derivability (vendor ground-truth canon) ----
    # r639 token heuristic (r640/r642 roster probes) flagged 15 tail faces as
    # non-derivable on bare tokens (eps/close_loc/CV/cs_rank/log2/vwap_loc).
    # r644 vendor ground-truth adjudication (_r644bma_vendor_adjudication.py):
    # ALL 15 implementations access only panel.<open/high/low/close/volume/
    # vwap/amount/mask> -- the flagged tokens are epsilon constants (eps=1e-9,
    # old-family false-positive family: old_047/old_067), operator shorthands
    # (log2=log base2, cs_rank=cross-sectional rank), derived intermediates
    # (close_loc/vwap_loc/volume_5), EWMA kwargs (alpha=), time notation
    # (close[t]) and coefficient-of-variation (CV). The synthetic-panel smoke
    # (leg 6, only 8 panel fields present) is the fail-closed proof: any
    # non-panel data access would AttributeError. Roster rule therefore =
    # vendor implementation ground truth; r639 token counts kept as
    # disclosure (54) with the 15-face correction enumerated.
    PANEL_ATTRS = {"open", "close", "high", "low", "volume", "vol", "vwap",
                   "amount", "mask", "ret", "returns", "adv20", "cap"}
    deriv = {}
    for f in probe_faces:
        attrs = sorted(set(re.findall(r"panel\.([a-zA-Z_][a-zA-Z_0-9]*)",
                                      vendor_body_cache[f])))
        deriv[f] = {"panel_attrs": attrs,
                    "non_panel_attrs": [a for a in attrs if a not in PANEL_ATTRS]}
    non_derivable = sorted(f for f in deriv if deriv[f]["non_panel_attrs"])
    out["legs"]["derivability"] = {
        "rule": "vendor implementation ground truth (panel attr scan + synthetic smoke fail-closed)",
        "panel_derivable": sorted(set(probe_faces) - set(non_derivable)),
        "non_derivable": {f: deriv[f]["non_panel_attrs"] for f in non_derivable},
        "n_derivable": len(probe_faces) - len(non_derivable),
        "r639_token_rule_disclosure": {
            "n_derivable": 54,
            "fifteen_flagged_faces": sorted(
                "add_004 add_026 add_029 best_004 best_005 best_011 best_015 "
                "better_001 better_005 better_008 better_013 better_014 "
                "better_022 better_023 extra_001".split()),
            "adjudication": "all 15 panel-only in vendor source (r644 _r644bma_vendor_adjudication.py); tokens = eps-epsilon/log2-op/cs_rank-op/derived-intermediates/EWMA-kwarg/time-notation",
        },
    }
    if (len(probe_faces) - len(non_derivable)) != 69:
        fails.append(f"vendor-truth derivable count {len(probe_faces) - len(non_derivable)} != 69 (all NEW-FACE tail faces must be panel-only)")

    # ---- leg 4: vendor anchors ----
    head = subprocess.run(["git", "-C", VENDOR_REPO, "rev-parse", "HEAD"],
                          capture_output=True, text=True).stdout.strip()
    def _sha(p):
        return hashlib.sha256(open(p, "rb").read()).hexdigest()
    anchors = {"vendor_head": head, "head_matches_install_anchor": head == ANCHOR_HEAD}
    for name in ("legacy_factors.py", "tensor_factors.py"):
        p = os.path.join(VENDOR_SRC, "mlquant", "features", name)
        anchors[f"sha256_{name}"] = _sha(p)
    for name in ("_factors_add.py", "_factors_better.py", "_factors_best.py",
                 "_factors_extra.py", "_factors_original.py", "_factors_change.py"):
        p = os.path.join(VENDOR_SRC, "mlquant", "features", name)
        if os.path.exists(p):
            anchors[f"sha256_{name}"] = _sha(p)
        else:
            fails.append(f"vendor module missing: {name}")
    out["legs"]["vendor_anchors"] = anchors
    if not anchors["head_matches_install_anchor"]:
        fails.append("vendor HEAD drifted from pinned install anchor a770825")

    # ---- leg 5: core48 panel facts ----
    sys.path.insert(0, ROOT)
    from knowledge.panel_gate import INSERVICE_WHITELIST, INSERVICE_SHA16  # noqa: E402
    daily_dir = os.path.join(ROOT, "data", "daily")
    panel = {}
    for code in sorted(INSERVICE_WHITELIST):
        p = os.path.join(daily_dir, f"{code}.csv")
        if not os.path.exists(p):
            fails.append(f"core48 member {code} csv missing")
            continue
        df = pd.read_csv(p, parse_dates=["date"])
        df = df[df["date"] <= pd.Timestamp(CUTOFF)]
        if df["date"].duplicated().any():
            fails.append(f"{code} duplicate dates")
        panel[code] = df
    union_dates = sorted(set().union(*[set(d["date"]) for d in panel.values()])) if panel else []
    common_start = max(d["date"].min() for d in panel.values())
    min_rows = min(len(d) for d in panel.values())
    bad_cols = [c for c, d in panel.items()
                if not {"open", "high", "low", "close", "volume", "amount"} <= set(d.columns)]
    vwap_ok_frac = {}
    for c, d in panel.items():
        sub = d[d["date"] >= common_start]
        ok = ((sub["amount"] > 0) & (sub["volume"] > 0)).mean()
        vwap_ok_frac[c] = round(float(ok), 6)
    worst_vwap = min(vwap_ok_frac.values())
    out["legs"]["core48_panel"] = {
        "n_members": len(panel),
        "inservice_sha16": INSERVICE_SHA16,
        "union_trading_days": len(union_dates),
        "common_window_start": str(common_start.date()),
        "union_last": str(max(union_dates).date()) if union_dates else None,
        "min_rows_per_member": int(min_rows),
        "bad_columns_members": bad_cols,
        "vwap_ok_fraction_worst": worst_vwap,
        "cutoff": CUTOFF,
    }
    if len(panel) != 48:
        fails.append(f"core48 members loaded {len(panel)} != 48")
    if bad_cols:
        fails.append(f"core48 column gaps: {bad_cols[:5]}")
    if worst_vwap < 0.99:
        fails.append(f"vwap derivation worst fraction {worst_vwap} < 0.99")

    # ---- leg 6: synthetic panel smoke (torch CPU) ----
    torch.manual_seed(0)
    T, N = 300, 20
    rng = np.random.default_rng(7)
    o = rng.lognormal(size=(T, N)).astype(np.float32)
    fields = {
        "open": o, "high": o * 1.02, "low": o * 0.98,
        "close": o * (1 + rng.normal(0, 0.01, (T, N)).astype(np.float32)),
        "volume": (rng.random((T, N)) * 1e6 + 1).astype(np.float32),
    }
    fields["vwap"] = (fields["close"] * (1 + rng.normal(0, 0.002, (T, N)).astype(np.float32)))
    fields["amount"] = fields["vwap"] * fields["volume"]
    mask = (rng.random((T, N)) > 0.1)
    mask[:60] = False
    from mlquant.data.panel import Panel  # noqa: E402
    tt = {k: torch.from_numpy(v) for k, v in fields.items()}
    p = Panel(dates=np.arange(T), stocks=[f"S{i}" for i in range(N)],
              open=tt["open"], high=tt["high"], low=tt["low"], close=tt["close"],
              volume=tt["volume"], vwap=tt["vwap"], mask=torch.from_numpy(mask),
              amount=tt["amount"])
    smoke = {}
    for f in vendor_tail:
        try:
            val, m = LEGACY_REGISTRY[f](p)
            ok_shape = tuple(val.shape) == (T, N) and tuple(m.shape) == (T, N)
            ok_mask = m.dtype == torch.bool
            finite = torch.isfinite(val[mask]).float().mean().item() if m.any() else 0.0
            smoke[f] = {"rc": 0 if (ok_shape and ok_mask) else 1, "finite_frac": round(finite, 4)}
        except Exception as e:  # noqa: BLE001
            smoke[f] = {"rc": 2, "err": type(e).__name__}
    smoke_fail = [f for f, v in smoke.items() if v["rc"] != 0]
    probe_fail = [f for f in probe_faces if smoke.get(f, {}).get("rc") != 0]
    out["legs"]["synthetic_smoke"] = {
        "n_faces": len(vendor_tail),
        "n_fail": len(smoke_fail),
        "fail_faces": smoke_fail,
        "probe_family_fail": probe_fail,
        "device": "cpu",
    }
    if probe_fail:
        fails.append(f"probe-family smoke failures: {probe_fail[:8]}")

    # ---- leg 7: old-family roster-correction faces (old_047/old_067) ----
    # r640 old-family census downgraded these 2 faces to "fundamental lane" on
    # the r639 token rule flagging 'eps'. Vendor ground truth: doc_formula
    # '+ eps' == numeric epsilon (clamp_min(1e-9)), implementations are
    # panel-only (old_047: high/low/close; old_067: high/volume/vwap + cs_rank
    # operator). This is a FIRST measurement (faces were never burned), not a
    # re-burn of the answered old family (0/41 verdict stands on its measured
    # set). Carried in this merged-tail batch as roster-correction leg so the
    # census-P2 126 NEW-FACE berth reaches full coverage (41+2 + 14 + 69 = 126).
    old_corr = {}
    for f in ("old_047", "old_067"):
        attrs = sorted(set(re.findall(r"panel\.([a-zA-Z_][a-zA-Z_0-9]*)",
                                      vendor_body_cache[f])))
        non_panel = [a for a in attrs if a not in PANEL_ATTRS]
        try:
            val, m2 = LEGACY_REGISTRY[f](p)
            ok_shape = tuple(val.shape) == (T, N) and tuple(m2.shape) == (T, N)
            smoke_rc = 0 if (ok_shape and m2.dtype == torch.bool) else 1
        except Exception as e:  # noqa: BLE001
            smoke_rc = 2
            ok_shape = False
        old_corr[f] = {"panel_attrs": attrs, "non_panel_attrs": non_panel,
                       "synthetic_smoke_rc": smoke_rc}
        if non_panel or smoke_rc != 0:
            fails.append(f"old-correction face {f} not panel-only or smoke fail: {old_corr[f]}")
    out["legs"]["old_family_roster_correction"] = {
        "faces": old_corr,
        "basis": "r639 token rule false-positive family: 'eps' = numeric epsilon constant (1e-9), same-shape as r644 tail adjudication; first measurement, old 0/41 verdict untouched",
    }

    # ---- verdict ----
    out["verdict"] = "PASS" if not fails else "FAIL"
    out["fails"] = fails
    roster = {
        "burn_faces": sorted(set(probe_faces) - set(non_derivable)) + ["old_047", "old_067"],
        "downgraded_fundamental_lane": non_derivable,
        "n_burn": len(probe_faces) - len(non_derivable) + 2,
        "n_old_roster_correction": 2,
        "families": {f["family"]: sorted(set(f["faces"]) - set(non_derivable)) for f in fams},
        "old_roster_correction": ["old_047", "old_067"],
    }
    out["roster_freeze"] = roster
    dst = os.path.join(ROOT, "results", "_r644bma_slot_tail_roster_probe.json")
    with open(dst, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1)
    roster_sha = hashlib.sha256(json.dumps(roster, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
    print(f"selftest: {'PASS' if not fails else 'FAIL'} fails={fails}")
    print(f"roster: burn={roster['n_burn']} downgraded={len(non_derivable)} roster_freeze_sha256={roster_sha[:16]}")
    print(f"artifact: {dst}")
    return 0 if not fails else 1


if __name__ == "__main__":
    sys.exit(main())
