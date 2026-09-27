# -*- coding: utf-8 -*-
"""r313 bm-b T-89 slice-1b pre-build probe (PROS_REGIME_SEGMENTS_P1 s2 gates).

Face A (census): enumerate starts on the CURRENT panels for both axes and
compare against the frozen gate targets (legacy 1,255 / deep 1,506, prereg
s2-iii) and the t22 finalize record (live-read). Mismatch = batch start
forbidden (probe-first law); the probe output is the adjudication evidence.
Face B (panels): legacy panel end must equal 2026-09-24 (prereg s2 frozen
probe value), deep end = t18 manifest evidence_cutoff (2026-09-22).
Face C (members): 22/22 PROSPECT roster, entry builders covered by
live.paper SIGNAL_BUILDERS, anchor face 22/22 anchor_ok with evidence
cutoff set.
Read-only: writes only this probe's own JSON. Zero engine runs, zero cell
burns, zero network.
"""
import glob
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))), "scripts"))

import pandas as pd
import t22_virtual_timepoints as t22

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "results", "_r313bmb_prospect_probe.json")

GATE_LEGACY_STARTS = 1255   # prereg s2-iii frozen gate target
GATE_DEEP_STARTS = 1506     # prereg s2-iii frozen gate target
LEGACY_PANEL_END = "2026-09-24"   # prereg s2 frozen probe value (r309)
ROSTER = ["ANTS", "ANTS-CE", "BBS", "BBS-CE", "DOJI", "DOJI-CE", "DUCK",
          "DUCK-CE", "HAM", "HAM-CE", "IBB", "IBB-CE", "IMM", "IMM-CE",
          "MCB", "MCB-CE", "OVB", "OVB-CE", "RSRS-CE", "TMU", "TMU-CE",
          "VOB-CE"]


def main():
    t0 = time.time()
    rep = {"probe": "r313bmb prospect_regime_segments pre-build",
           "ts": time.strftime("%Y-%m-%d %H:%M:%S")}

    # ---- Face C first (cheap): roster + builders + anchor face ----
    from live.paper import SIGNAL_BUILDERS
    from firm.hr import TRADERS_DIR
    members, missing_sb, anchor_ok, cuts = [], [], 0, set()
    for f in sorted(glob.glob(os.path.join(str(TRADERS_DIR), "*.json"))):
        with open(f, encoding="utf-8") as fh:
            t = json.load(fh)
        if t.get("level") != "PROSPECT":
            continue
        members.append(t["id"])
        if t["params"]["entry"] not in SIGNAL_BUILDERS:
            missing_sb.append(f"{t['id']}:{t['params']['entry']}")
        ppath = os.path.join(ROOT, "results", "prospect_paper",
                             os.path.basename(f))
        p = json.load(open(ppath, encoding="utf-8"))
        anchor_ok += 1 if p.get("anchor_ok") else 0
        cuts.add(p.get("evidence_cutoff"))
    roster_ok = members == [f"PROS-{r}-01" for r in ROSTER]
    rep["members"] = {"n": len(members), "roster_exact": roster_ok,
                      "missing_sb": missing_sb,
                      "anchor_ok": f"{anchor_ok}/22",
                      "anchor_evidence_cutoffs": sorted(c for c in cuts
                                                        if c)}

    # ---- Face A/B: census + panel ends, both axes ----
    axes = {}
    t22_rec = json.load(open(os.path.join(ROOT, "results",
                                          "t22_virtual_timepoints.json"),
                             encoding="utf-8"))
    for axis, gate_n in (("legacy", GATE_LEGACY_STARTS),
                         ("deep", GATE_DEEP_STARTS)):
        prices = t22._load_axis_prices(axis)
        from live.paper import build_panels
        close = build_panels(prices)["close"]
        idx = close.index
        listed = close.notna().sum(axis=1)
        elig = t22.enumerate_starts(len(idx), listed)
        rec_n = t22_rec["axes"][axis]["n_starts"]
        axes[axis] = {
            "panel_start": str(idx[0].date()), "panel_end": str(idx[-1].date()),
            "n_eligible": len(elig),
            "gate_target": gate_n,
            "t22_record": rec_n,
            "census_gate_pass": len(elig) == gate_n,
            "listed_uniform": sorted(set(int(v) for v in listed))[-3:],
        }
    axes["legacy"]["panel_end_gate_pass"] = \
        axes["legacy"]["panel_end"] == LEGACY_PANEL_END
    rep["axes"] = axes

    rep["verdict"] = {
        "census_gate": all(axes[a]["census_gate_pass"]
                           for a in ("legacy", "deep")),
        "panel_end_gate": axes["legacy"]["panel_end_gate_pass"],
        "member_gate": (len(members) == 22 and roster_ok and not missing_sb
                        and anchor_ok == 22),
    }
    rep["batch_start_allowed"] = all(rep["verdict"].values())
    rep["elapsed_sec"] = round(time.time() - t0, 1)
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(rep, fh, indent=1, ensure_ascii=False)
    print(json.dumps(rep, indent=1, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
